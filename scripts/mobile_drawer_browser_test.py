#!/usr/bin/env python3
"""Focused isolated-browser regression coverage for the shared app shell.

Uses a temporary synthetic DATA_DIR, the installed Google Chrome channel, and
blocked non-localhost browser requests. No production credentials or data are
required. Covers the mobile drawer plus theme, HTMX configuration and swaps,
AI modal listeners, CSRF wiring, service-worker registration, and configured-
auth/no-password shell loading. Transaction and supporting modal fragments,
categorization/upload controls, Cash Flow/Long-Term Planning, Short-Term
Planning, and Weekly/Waterfall interactions run only against temporary
synthetic databases. Subscription and BFM-only payroll interactions use the
same local-only fixture and cleanup boundary. Standalone offline/error and
`/k/` execution proof uses synthetic status routes and the same denied-network,
temporary-data, and exact-cleanup boundary.
"""

from __future__ import annotations

import os
import sys
import tempfile
import threading
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from werkzeug.serving import WSGIRequestHandler, make_server


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PLAID_INITIALIZER_URL = (
    "https://cdn.plaid.com/link/v2/stable/link-initialize.js"
)
PLAID_STUB_SOURCE = """
window.__plaidStub = {mode: "exit", opens: 0};
window.Plaid = {
    create: function (options) {
        if (window.__plaidStub.mode === "throw") {
            throw new Error("synthetic initializer failure");
        }
        window.__plaidStub.options = options;
        return {
            open: function () {
                window.__plaidStub.opens += 1;
                if (window.__plaidStub.mode === "exit") {
                    options.onExit();
                    return;
                }
                options.onSuccess("synthetic-4aq-public-token", {
                    institution: {
                        name: "Synthetic 4AQ Institution",
                        institution_id: "ins_synthetic_4aq"
                    }
                });
            }
        };
    }
};
"""


class _QuietRequestHandler(WSGIRequestHandler):
    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        pass


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _drawer_state(page) -> dict:
    return page.evaluate(
        """() => {
            const sidebar = document.getElementById('sidebar-nav');
            const scrim = document.getElementById('sidebar-scrim');
            const button = document.getElementById('hamburger-btn');
            return {
                expanded: button.getAttribute('aria-expanded'),
                label: button.getAttribute('aria-label'),
                controls: button.getAttribute('aria-controls'),
                open: sidebar.classList.contains('open'),
                sidebarHidden: sidebar.getAttribute('aria-hidden'),
                sidebarInert: sidebar.hasAttribute('inert'),
                scrimHidden: scrim.hidden,
                scrimVisible: scrim.classList.contains('visible'),
                bodyLocked: document.body.classList.contains('mobile-drawer-open'),
                bodyOverflow: getComputedStyle(document.body).overflow,
                activeId: document.activeElement && document.activeElement.id,
                activeText: document.activeElement && document.activeElement.textContent.trim(),
                activeInsideSidebar: sidebar.contains(document.activeElement),
            };
        }"""
    )


def _assert_closed_mobile(page, label: str) -> None:
    state = _drawer_state(page)
    _check(state["expanded"] == "false", f"{label}: hamburger must be collapsed")
    _check(state["label"] == "Open navigation", f"{label}: open label must be restored")
    _check(state["controls"] == "sidebar-nav", f"{label}: drawer control relationship must remain")
    _check(not state["open"], f"{label}: drawer class must be closed")
    _check(state["sidebarHidden"] == "true", f"{label}: closed drawer must be hidden from assistive navigation")
    _check(state["sidebarInert"], f"{label}: closed drawer must be inert")
    _check(state["scrimHidden"], f"{label}: closed scrim must be hidden")
    _check(not state["scrimVisible"], f"{label}: closed scrim must not be visible")
    _check(not state["bodyLocked"], f"{label}: closed drawer must release body lock")
    _check(state["bodyOverflow"] != "hidden", f"{label}: closed drawer must restore body overflow")


def _assert_open_mobile(page, label: str) -> None:
    state = _drawer_state(page)
    _check(state["expanded"] == "true", f"{label}: hamburger must be expanded")
    _check(state["label"] == "Close navigation", f"{label}: close label must be exposed")
    _check(state["open"], f"{label}: drawer class must be open")
    _check(state["sidebarHidden"] is None, f"{label}: open drawer must be exposed to assistive navigation")
    _check(not state["sidebarInert"], f"{label}: open drawer must not be inert")
    _check(not state["scrimHidden"] and state["scrimVisible"], f"{label}: scrim must be visible")
    _check(state["bodyLocked"] and state["bodyOverflow"] == "hidden", f"{label}: body scroll must be locked")
    _check(state["activeInsideSidebar"], f"{label}: focus must move into the drawer")
    _check(state["activeText"] == "Dashboard", f"{label}: first primary navigation link must receive focus")


def _assert_shared_shell(page, label: str) -> None:
    state = page.evaluate(
        """async () => {
            const config = window.htmx && window.htmx.config;
            const indicator = document.createElement('div');
            indicator.className = 'htmx-indicator';
            document.body.appendChild(indicator);
            const hiddenOpacity = getComputedStyle(indicator).opacity;
            indicator.classList.add('htmx-request');
            await new Promise((resolve) => setTimeout(resolve, 400));
            const requestOpacity = getComputedStyle(indicator).opacity;
            indicator.remove();
            return {
                themeAsset: Boolean(document.querySelector('script[src*="theme-init.js"]')),
                shellAsset: Boolean(document.querySelector('script[src*="app-shell.js"]')),
                includeIndicatorStyles: config && config.includeIndicatorStyles,
                allowEval: config && config.allowEval,
                allowScriptTags: config && config.allowScriptTags,
                injectedIndicatorStyle: Array.from(document.head.querySelectorAll('style')).some(
                    (style) => style.textContent.includes('.htmx-indicator')
                ),
                hiddenOpacity,
                requestOpacity,
                shellFunctions: [
                    window.toggleTheme,
                    window.toggleSidebar,
                    window.aiChatOpen,
                    window.aiChatClose,
                ].every((value) => typeof value === 'function'),
            };
        }"""
    )
    _check(state["themeAsset"] and state["shellAsset"], f"{label}: local shell assets must load")
    _check(state["includeIndicatorStyles"] is False, f"{label}: HTMX must not inject indicator CSS")
    _check(state["allowEval"] is False, f"{label}: HTMX eval must be disabled")
    _check(state["allowScriptTags"] is False, f"{label}: HTMX swapped scripts must be disabled")
    _check(not state["injectedIndicatorStyle"], f"{label}: HTMX indicator style tag must be absent")
    _check(state["hiddenOpacity"] == "0" and state["requestOpacity"] == "1", f"{label}: local indicator CSS must preserve behavior")
    _check(state["shellFunctions"], f"{label}: compatibility globals must remain available")


def _seed_dashboard_data(entity_key: str) -> None:
    from core.db import get_connection

    today = date.today().isoformat()
    imported_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for index in range(25):
        amount_cents = -(1000 + index * 25)
        rows.append(
            (
                f"4ag-{entity_key}-expense-{index:02d}",
                today,
                f"SYNTHETIC 4AG EXPENSE {index:02d}",
                f"Synthetic Merchant {index:02d}",
                f"Synthetic Merchant {index:02d}",
                amount_cents / 100,
                amount_cents,
                "Synthetic Checking",
                "Office Supplies",
                "General" if index % 2 == 0 else "Equipment",
                1.0,
                "synthetic-4ag.csv",
                imported_at,
            )
        )
    rows.append(
        (
            f"4ag-{entity_key}-income",
            today,
            "SYNTHETIC 4AG INCOME",
            "Synthetic Income",
            "Synthetic Income",
            1000.0,
            100000,
            "Synthetic Checking",
            "Income",
            "General",
            1.0,
            "synthetic-4ag.csv",
            imported_at,
        )
    )
    conn = get_connection(entity_key)
    conn.executemany(
        "INSERT INTO transactions "
        "(transaction_id, date, description_raw, merchant_raw, merchant_canonical, "
        "amount, amount_cents, account, category, subcategory, confidence, "
        "source_filename, imported_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.execute(
        "UPDATE transactions SET description_raw=?, merchant_raw=?, merchant_canonical=?, "
        "category=NULL, subcategory=NULL, confidence=0.1 WHERE transaction_id=?",
        (
            "PAYPAL * SYNTHETIC ALIAS TX",
            "PAYPAL * SYNTHETIC ALIAS TX",
            "PAYPAL * SYNTHETIC ALIAS TX",
            f"4ag-{entity_key}-expense-23",
        ),
    )
    conn.execute(
        "UPDATE transactions SET category='Legacy Category', "
        "subcategory='Legacy Subcategory', confidence=1.0 WHERE transaction_id=?",
        (f"4ag-{entity_key}-expense-24",),
    )
    conn.execute(
        "INSERT INTO categories (name, created_at) VALUES ('Legacy Category', ?)",
        (imported_at,),
    )
    conn.execute(
        "INSERT INTO subcategories (category_name, name, created_at) "
        "VALUES ('Legacy Category', 'Legacy Subcategory', ?)",
        (imported_at,),
    )
    conn.execute(
        "INSERT INTO merchant_aliases "
        "(pattern_type, pattern, merchant_canonical, default_category, active, created_at) "
        "VALUES ('contains', 'SYNTHETIC DELETE ALIAS', 'Synthetic Delete Alias', "
        "'Office Supplies', 1, ?)",
        (imported_at,),
    )
    checklist_cursor = conn.execute(
        "INSERT INTO import_checklist "
        "(label, filename_pattern, profile_name, url, notes, sort_order, created_at, entity) "
        "VALUES (?, ?, 'Amex Credit Card', NULL, ?, 0, ?, ?)",
        (
            "Synthetic Browser Source",
            "synthetic-browser",
            "Local-only 4AK browser fixture",
            imported_at,
            entity_key,
        ),
    )
    conn.execute(
        "INSERT INTO import_checklist_status "
        "(checklist_item_id, month, completed, completed_at, source_filename) "
        "VALUES (?, ?, 1, ?, 'synthetic-browser.csv')",
        (checklist_cursor.lastrowid, today[:7], imported_at),
    )
    auto_split_txn_id = f"4ag-{entity_key}-expense-00"
    order_cursor = conn.execute(
        "INSERT INTO amazon_orders "
        "(order_id, order_date, product_summary, order_total, order_total_cents, "
        "matched_transaction_id, imported_at) VALUES (?, ?, ?, 10.00, 1000, ?, ?)",
        (
            f"4ah-{entity_key}-auto-split-order",
            today,
            "Synthetic browser split fixtures",
            auto_split_txn_id,
            imported_at,
        ),
    )
    conn.executemany(
        "INSERT INTO order_line_items "
        "(amazon_order_id, product_name, quantity, unit_price_cents, item_total_cents, "
        "category, subcategory, created_at) VALUES (?, ?, 1, ?, ?, ?, 'General', ?)",
        (
            (order_cursor.lastrowid, "Synthetic office item", 400, 400, "Office Supplies", imported_at),
            (order_cursor.lastrowid, "Synthetic food item", 600, 600, "Food", imported_at),
        ),
    )
    conn.commit()
    conn.close()


def _seed_cashflow_planning_data(entity_key: str) -> None:
    from core.db import get_connection

    display_name = {
        "personal": "Personal",
        "company": "BFM",
        "luxelegacy": "LL",
    }[entity_key]
    updated_at = datetime.now(timezone.utc).isoformat()
    conn = get_connection(entity_key)
    conn.execute(
        "INSERT INTO account_balances "
        "(account_name, balance_cents, balance_source, low_threshold_cents, "
        "updated_at, created_at, account_type, credit_limit_cents, "
        "payment_due_day, payment_amount_cents, sort_order, payment_due_date, apr_bps) "
        "VALUES (?, ?, 'manual', 50000, ?, ?, 'bank', 0, NULL, 0, 0, NULL, NULL)",
        (
            f"4AL {display_name} Checking",
            425000,
            updated_at,
            updated_at,
        ),
    )
    conn.execute(
        "INSERT INTO account_balances "
        "(account_name, balance_cents, balance_source, low_threshold_cents, "
        "updated_at, created_at, account_type, credit_limit_cents, "
        "payment_due_day, payment_amount_cents, sort_order, payment_due_date, apr_bps) "
        "VALUES (?, ?, 'manual', 50000, ?, ?, 'credit_card', ?, 17, ?, 1, ?, ?)",
        (
            f"4AL {display_name} Credit",
            123400,
            updated_at,
            updated_at,
            900000,
            27500,
            "2026-08-17",
            1999,
        ),
    )
    conn.execute(
        "INSERT INTO planning_items "
        "(item_type, name, current_value_cents, annual_rate_bps, "
        "monthly_contrib_cents, monthly_payment_cents, source, "
        "cashflow_account_name, sort_order, created_at, updated_at) "
        "VALUES ('asset', ?, 15000000, 500, 50000, 0, 'cashflow', ?, 0, ?, ?)",
        (
            f"4AL {display_name} Asset",
            f"4AL {display_name} Checking",
            updated_at,
            updated_at,
        ),
    )
    conn.execute(
        "INSERT INTO planning_items "
        "(item_type, name, current_value_cents, annual_rate_bps, "
        "monthly_contrib_cents, monthly_payment_cents, source, "
        "cashflow_account_name, sort_order, created_at, updated_at) "
        "VALUES ('liability', ?, 4200000, 650, 0, 45000, 'manual', NULL, 0, ?, ?)",
        (
            f"4AL {display_name} Liability",
            updated_at,
            updated_at,
        ),
    )
    conn.commit()
    conn.close()


def _seed_short_term_planning_data(entity_key: str) -> None:
    if entity_key == "luxelegacy":
        return

    from core.db import get_connection

    display_name = {
        "personal": "Personal",
        "company": "BFM",
    }[entity_key]
    month = date.today().strftime("%Y-%m")
    timestamp = datetime.now(timezone.utc).isoformat()
    linked_account = f"4AL {display_name} Credit"
    transaction_id = f"synthetic-4am-{entity_key}-food"
    conn = get_connection(entity_key)
    conn.execute(
        "INSERT INTO short_term_goals "
        "(name, goal_type, target_amount_cents, target_date, strategy, "
        "monthly_amount_cents, linked_accounts, status, notes, ai_plan) "
        "VALUES (?, 'debt_payoff', 0, ?, 'avalanche', 25000, ?, 'active', "
        "'Synthetic 4AM goal', 'Pay the highest APR first.')",
        (
            f"4AM {display_name} Goal",
            f"{date.today().year + 1}-12-31",
            f'["{linked_account}"]',
        ),
    )
    conn.execute(
        "INSERT INTO action_items "
        "(title, status, due_date, notes, sort_order, is_recurring) "
        "VALUES (?, 'pending', NULL, 'Synthetic 4AM action', 0, 0)",
        (f"4AM {display_name} Action",),
    )
    conn.execute(
        "INSERT INTO budget_items "
        "(category, monthly_budget_cents, budget_section) "
        "VALUES ('Food', 50000, 'focus') "
        "ON CONFLICT(category) DO UPDATE SET "
        "monthly_budget_cents=excluded.monthly_budget_cents, "
        "budget_section=excluded.budget_section"
    )
    conn.execute(
        "INSERT INTO budget_subcategories "
        "(category, subcategory, monthly_budget_cents) "
        "VALUES ('Food', 'General', 30000) "
        "ON CONFLICT(category, subcategory) DO UPDATE SET "
        "monthly_budget_cents=excluded.monthly_budget_cents"
    )
    conn.execute(
        "INSERT INTO transactions "
        "(transaction_id, date, description_raw, merchant_canonical, amount, "
        "amount_cents, account, category, subcategory, source_filename, imported_at) "
        "VALUES (?, ?, ?, ?, -12.34, -1234, '4AM Synthetic', 'Food', 'General', "
        "'synthetic-4am', ?)",
        (
            transaction_id,
            f"{month}-15",
            f"4AM {display_name} Food",
            f"4AM {display_name} Food",
            timestamp,
        ),
    )
    conn.commit()
    conn.close()


def _seed_subscription_data(entity_key: str) -> None:
    from core.db import get_connection

    display_name = {
        "personal": "Personal",
        "company": "BFM",
        "luxelegacy": "LL",
    }[entity_key]
    today = date.today()
    imported_at = datetime.now(timezone.utc).isoformat()
    watchlist_merchant = f"4AO {display_name} Watchlist"
    suggestion_merchant = f"4AO {display_name} Suggestion"
    conn = get_connection(entity_key)
    watchlist_cursor = conn.execute(
        "INSERT INTO subscription_watchlist "
        "(merchant, amount_cents, frequency, status, notes, cancellation_tips) "
        "VALUES (?, 1299, 'monthly', 'watching', ?, NULL)",
        (watchlist_merchant, f"Synthetic 4AO {display_name} notes"),
    )
    subscription_id = watchlist_cursor.lastrowid
    conn.execute(
        "INSERT INTO subscription_account_info "
        "(subscription_id, field_type, field_value, sort_order) "
        "VALUES (?, 'Email', ?, 0)",
        (subscription_id, f"synthetic-{entity_key}@example.invalid"),
    )
    conn.execute(
        "INSERT INTO subscription_notes_log "
        "(subscription_id, action, detail) VALUES (?, 'created', 'Synthetic 4AO fixture')",
        (subscription_id,),
    )
    conn.execute(
        "INSERT INTO subscription_dismissals (merchant_canonical) VALUES (?)",
        (f"4AO {display_name} Dismissed",),
    )

    for merchant, prefix, amount_cents in (
        (watchlist_merchant, "watchlist", -1299),
        (suggestion_merchant, "suggestion", -2499),
    ):
        for index, days_ago in enumerate((60, 30, 0)):
            transaction_date = (today - timedelta(days=days_ago)).isoformat()
            conn.execute(
                "INSERT INTO transactions "
                "(transaction_id, date, description_raw, merchant_raw, "
                "merchant_canonical, amount, amount_cents, account, category, "
                "subcategory, confidence, source_filename, imported_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Office Supplies', 'General', "
                "1.0, 'synthetic-4ao.csv', ?)",
                (
                    f"4ao-{entity_key}-{prefix}-{index}",
                    transaction_date,
                    merchant,
                    merchant,
                    merchant,
                    amount_cents / 100,
                    amount_cents,
                    f"4AO {display_name} Card",
                    imported_at,
                ),
            )
    conn.commit()
    conn.close()


def _seed_payroll_data(entity_key: str) -> None:
    if entity_key != "company":
        return

    from core.db import get_connection

    conn = get_connection(entity_key)
    employee = conn.execute(
        "INSERT INTO employees "
        "(name, role, pay_type, pay_rate_cents, hire_date, status, notes) "
        "VALUES ('4AP BFM Provider', 'Providers', 'salary', 12000000, "
        "'2024-01-15', 'active', 'Synthetic 4AP detail notes')"
    )
    employee_id = employee.lastrowid
    conn.execute(
        "INSERT INTO employee_pay_changes "
        "(employee_id, effective_date, old_rate_cents, new_rate_cents, notes) "
        "VALUES (?, '2026-01-01', 11000000, 12000000, 'Synthetic 4AP raise')",
        (employee_id,),
    )
    conn.executemany(
        "INSERT INTO payroll_entries "
        "(employee_id, paycheck_date, amount_cents, source_filename) "
        "VALUES (?, ?, ?, 'synthetic-4ap.xlsx')",
        (
            (employee_id, "2026-06-15", 500000),
            (employee_id, "2026-07-01", 600000),
        ),
    )
    conn.commit()
    conn.close()


def _seed_plaid_entry_data(entity_key: str) -> None:
    from core.db import get_connection

    created_at = datetime.now(timezone.utc).isoformat()
    conn = get_connection(entity_key)
    conn.execute(
        "INSERT INTO plaid_items "
        "(item_id, access_token, institution_name, institution_id, is_vendor, created_at) "
        "VALUES (?, 'synthetic-4aq-token', ?, 'ins_4aq_vendor', 1, ?)",
        (
            f"4aq-{entity_key}-vendor-existing",
            f"4AQ {entity_key.title()} Vendor",
            created_at,
        ),
    )
    conn.execute(
        "INSERT INTO plaid_items "
        "(item_id, access_token, institution_name, institution_id, is_vendor, created_at) "
        "VALUES (?, 'synthetic-4aq-token', ?, 'ins_4aq_bank', 0, ?)",
        (
            f"4aq-{entity_key}-bank-existing",
            f"4AQ {entity_key.title()} Bank",
            created_at,
        ),
    )
    conn.execute(
        "INSERT INTO plaid_accounts "
        "(item_id, account_id, name, display_name, mask, type, subtype, enabled) "
        "VALUES (?, ?, ?, '', '4242', 'depository', 'checking', 1)",
        (
            f"4aq-{entity_key}-bank-existing",
            f"4aq-{entity_key}-account-existing",
            f"4AQ {entity_key.title()} Checking",
        ),
    )
    conn.execute(
        "INSERT INTO vendor_transactions "
        "(plaid_item_id, plaid_transaction_id, plaid_account_id, date, amount, "
        "amount_cents, name, merchant_name, recipient, vendor_type, imported_at) "
        "VALUES (?, ?, ?, '2026-07-01', 12.34, 1234, "
        "'Synthetic 4AQ payment', 'Synthetic 4AQ payment', "
        "'Synthetic 4AQ recipient', 'venmo', ?)",
        (
            f"4aq-{entity_key}-vendor-existing",
            f"4aq-{entity_key}-vendor-transaction",
            f"4aq-{entity_key}-vendor-account",
            created_at,
        ),
    )
    conn.commit()
    conn.close()


def _assert_dashboard_report_fragments(page, base_url: str, label: str) -> None:
    page.goto(base_url, wait_until="networkidle")
    page.wait_for_selector('#kpi-detail[data-fragment-initialized="true"]')
    page.wait_for_selector('#ie-line-chart[data-fragment-initialized="true"] svg')

    initial = page.evaluate(
        """() => ({
            asset: Boolean(document.querySelector('script[src*="dashboard-fragments.js"]')),
            chartCount: document.querySelectorAll('#ie-line-chart svg').length,
            detailCategories: Boolean(document.getElementById('detail-categories')),
            detailInsights: Boolean(document.getElementById('detail-insights')),
            ieInsights: Boolean(document.getElementById('ie-insights')),
            styleAttributes: document.querySelectorAll('[style]').length,
            boundedBars: document.querySelectorAll(
                '.u-width-pct[class*="u-pct-"], .u-height-pct[class*="u-pct-"]'
            ).length,
            sidebarClass: document.getElementById('sidebar-nav').className,
            sidebarAccent: getComputedStyle(
                document.getElementById('sidebar-nav')
            ).getPropertyValue('--sb-accent').trim(),
            allowEval: window.htmx.config.allowEval,
            allowScriptTags: window.htmx.config.allowScriptTags,
        })"""
    )
    _check(initial["asset"], f"{label}: dashboard fragment controller must load")
    _check(initial["chartCount"] == 1, f"{label}: static controller must render one income/expense chart")
    _check(
        initial["detailCategories"] and initial["detailInsights"] and initial["ieInsights"],
        f"{label}: KPI dependent fragment targets must remain available",
    )
    _check(
        initial["allowEval"] is False and initial["allowScriptTags"] is False,
        f"{label}: final global HTMX execution switches must be disabled",
    )
    _check(
        initial["styleAttributes"] == 0
        and initial["boundedBars"] > 0
        and "sidebar--personal" in initial["sidebarClass"]
        and initial["sidebarAccent"] == "#003eb6",
        f"{label}: dashboard shell and fragments must use local bounded classes with no style attributes",
    )

    hover_column = page.locator("#ie-line-chart .ie-hover-col").first
    hover_column.hover()
    tooltip_state = page.evaluate(
        """() => {
            const guide = document.querySelector('#ie-line-chart [data-ie-guide]');
            const tip = document.querySelector('#ie-line-chart [data-ie-tip]');
            return {
                guideVisible: guide.classList.contains('ie-guide--visible'),
                tipVisible: !tip.hidden,
                tipPercentClass: Array.from(tip.classList).some(
                    (className) => /^u-pct-\\d+$/.test(className)
                ),
                tipInlineStyle: tip.hasAttribute('style'),
                tipTop: getComputedStyle(tip).top,
            };
        }"""
    )
    _check(
        tooltip_state
        == {
            "guideVisible": True,
            "tipVisible": True,
            "tipPercentClass": True,
            "tipInlineStyle": False,
            "tipTop": "16px",
        },
        f"{label}: chart tooltip must preserve positioned guide behavior through local state classes",
    )
    page.mouse.move(0, 0)

    detail_category = page.locator(
        '#detail-categories [data-fragment-action="toggle-category"]'
    ).first
    page.wait_for_selector('#detail-categories [data-fragment-action="toggle-category"]')
    detail_subcategories = detail_category.locator("xpath=following-sibling::*[1]")
    _check(detail_subcategories.is_hidden(), f"{label}: detail subcategories must start collapsed")
    detail_category.click()
    _check(detail_subcategories.is_visible(), f"{label}: delegated category control must expand")
    detail_category.click()
    _check(detail_subcategories.is_hidden(), f"{label}: delegated category control must collapse")
    detail_category.click()
    subcategory_row = detail_subcategories.locator(
        '[data-fragment-action="open-subcategory-popup"]'
    ).first
    with page.expect_response(
        lambda response: "/dashboard/subcategory-txns" in response.url
    ) as response_info:
        subcategory_row.click()
    _check(response_info.value.status == 200, f"{label}: subcategory popup request must return 200")
    page.wait_for_selector(
        '#dcat-popup-body [data-transaction-fragment-action="close-subcategory-popup"]'
    )
    subcategory_popup = page.locator("#dcat-popup-scrim")
    _check(subcategory_popup.is_visible(), f"{label}: subcategory popup must open")
    page.locator(
        '#dcat-popup-body [data-transaction-fragment-action="close-subcategory-popup"]'
    ).click()
    _check(subcategory_popup.is_hidden(), f"{label}: delegated subcategory popup control must close")
    _check(
        page.locator("#dcat-popup-body").inner_html() == "",
        f"{label}: subcategory popup close must clear the swapped fragment",
    )

    page.wait_for_selector('#detail-insights [data-fragment-action="open-insight-modal"]')
    with page.expect_response(
        lambda response: "/dashboard/insight-detail" in response.url
    ) as response_info:
        page.locator(
            '#detail-insights [data-fragment-action="open-insight-modal"]'
        ).first.click()
    _check(response_info.value.status == 200, f"{label}: insight detail request must return 200")
    detail_modal = page.locator("#detail-iu-modal-scrim")
    _check(detail_modal.is_visible(), f"{label}: delegated insight control must open the modal")
    page.locator(
        '#detail-iu-modal-scrim [data-fragment-action="close-insight-modal"]'
    ).click()
    _check(detail_modal.is_hidden(), f"{label}: delegated insight control must close the modal")

    with page.expect_response(
        lambda response: "/dashboard/ai-analysis" in response.url
    ) as response_info:
        page.locator("#detail-ai-analysis-section .iu-ai-btn").click()
    _check(response_info.value.status == 200, f"{label}: AI analysis fragment request must return 200")
    page.wait_for_selector("#detail-ai-analysis-section .iu-ai-label")
    ai_toggle_state = page.evaluate(
        """() => {
            const host = document.createElement('div');
            host.id = 'synthetic-ai-fragment';
            host.innerHTML = '<div class="iu-row iu-ai-row iu-ai-row--expandable" '
                + 'data-fragment-action="toggle-ai"><span class="iu-chevron">›</span></div>'
                + '<div class="iu-ai-detail" hidden>Synthetic detail</div>';
            document.body.appendChild(host);
            const row = host.firstElementChild;
            const detail = row.nextElementSibling;
            row.click();
            const expanded = !detail.hidden;
            row.click();
            const collapsed = detail.hidden;
            host.remove();
            return { expanded, collapsed };
        }"""
    )
    _check(
        ai_toggle_state == {"expanded": True, "collapsed": True},
        f"{label}: delegated AI analysis rows must expand and collapse",
    )

    page.locator('[data-dashboard-page-action="set-view"][data-view="compare"]').click()
    page.wait_for_selector('#kpi-left[data-fragment-initialized="true"]')
    page.wait_for_selector('#kpi-right[data-fragment-initialized="true"]')
    page.wait_for_selector('#categories-compare [data-fragment-action="toggle-category"]')
    compare_category = page.locator(
        '#categories-compare [data-fragment-action="toggle-category"]'
    ).first
    compare_subcategories = compare_category.locator("xpath=following-sibling::*[1]")
    _check(compare_subcategories.is_hidden(), f"{label}: compare subcategories must start collapsed")
    compare_category.click()
    _check(compare_subcategories.is_visible(), f"{label}: compare category must expand")
    compare_category.click()
    _check(compare_subcategories.is_hidden(), f"{label}: compare category must collapse")
    page.locator('[data-dashboard-page-action="set-view"][data-view="details"]').click()

    for swap_number in (1, 2):
        with page.expect_response(
            lambda response: "/dashboard/partial" in response.url
        ) as response_info:
            page.evaluate(
                """() => window.htmx.ajax('GET', '/dashboard/partial', {
                    target: '#dashboard-body', swap: 'innerHTML'
                })"""
            )
        _check(
            response_info.value.status == 200,
            f"{label} dashboard swap {swap_number}: partial must return 200",
        )
        page.wait_for_selector('#kpi-detail[data-fragment-initialized="true"]')
        page.wait_for_selector('#ie-line-chart[data-fragment-initialized="true"] svg')
        fragment_state = page.evaluate(
            """() => {
                const root = document.getElementById('dashboard-body');
                const elements = [root, ...root.querySelectorAll('*')];
                return {
                    charts: root.querySelectorAll('#ie-line-chart svg').length,
                    scriptElements: root.querySelectorAll('script').length,
                    styleAttributes: root.querySelectorAll('[style]').length,
                    nativeHandlers: elements.reduce((count, element) => count +
                        Array.from(element.attributes || []).filter(
                            (attribute) => /^on[a-z]/i.test(attribute.name)
                        ).length, 0),
                };
            }"""
        )
        _check(
            fragment_state
            == {
                "charts": 1,
                "scriptElements": 0,
                "styleAttributes": 0,
                "nativeHandlers": 0,
            },
            f"{label} dashboard swap {swap_number}: migrated fragments must reinitialize without inline execution or style attributes",
        )

    page.goto(f"{base_url}/reports/", wait_until="networkidle")
    _assert_shared_shell(page, f"{label} reports shell")
    _check(
        page.locator("[style]").count() == 0,
        f"{label}: reports shell must render with no style attributes",
    )
    export_menu = page.locator(".rpt-export-menu")
    _check(export_menu.is_hidden(), f"{label}: report export menu must start closed")
    page.locator('[data-dashboard-page-action="toggle-export"]').click()
    _check(export_menu.is_visible(), f"{label}: delegated report export control must open the menu")
    page.keyboard.press("Escape")
    _check(export_menu.is_hidden(), f"{label}: Escape must close the report export menu")
    page.locator("#report_type").select_option("merchants")
    _check(
        page.locator('.rpt-desc[data-report="merchants"]').is_visible()
        and page.locator(".rpt-export-qbo").is_hidden(),
        f"{label}: delegated report-type change must update description and QBO visibility",
    )
    with page.expect_response(lambda response: "/reports/view" in response.url) as response_info:
        page.get_by_role("button", name="View", exact=True).click()
    _check(response_info.value.status == 200, f"{label} merchant report swap must return 200")
    page.wait_for_selector('#rpt-results [data-fragment-action="show-more-report-rows"]')
    more_rows = page.locator("#rpt-more-merchants")
    _check(more_rows.is_hidden(), f"{label}: extra merchant rows must start hidden")
    page.locator('[data-fragment-action="show-more-report-rows"]').click()
    _check(more_rows.is_visible(), f"{label}: delegated report control must reveal extra merchant rows")

    page.locator("#report_type").select_option("tax_summary")
    with page.expect_response(lambda response: "/reports/view" in response.url) as response_info:
        page.get_by_role("button", name="View", exact=True).click()
    _check(response_info.value.status == 200, f"{label} tax report swap must return 200")
    page.wait_for_selector('#rpt-results [data-fragment-action="toggle-report-group"]')
    group_button = page.locator('[data-fragment-action="toggle-report-group"]').first
    target_id = group_button.get_attribute("data-target")
    group_rows = page.locator(f"#{target_id}")
    _check(group_rows.is_visible(), f"{label}: tax group rows must start expanded")
    group_button.click()
    _check(group_rows.is_hidden(), f"{label}: delegated report control must collapse tax group rows")
    group_button.click()
    _check(group_rows.is_visible(), f"{label}: delegated report control must re-expand tax group rows")

    report_state = page.evaluate(
        """() => {
            const root = document.getElementById('rpt-results');
            const elements = [root, ...root.querySelectorAll('*')];
            return {
                executableScripts: root.querySelectorAll(
                    'script:not([type="application/json"]):not([src])'
                ).length,
                styleAttributes: root.querySelectorAll('[style]').length,
                nativeHandlers: elements.reduce((count, element) => count +
                    Array.from(element.attributes || []).filter(
                        (attribute) => /^on[a-z]/i.test(attribute.name)
                    ).length, 0),
            };
        }"""
    )
    _check(
        report_state
        == {
            "executableScripts": 0,
            "styleAttributes": 0,
            "nativeHandlers": 0,
        },
        f"{label}: repeated report swaps must contain no inline execution or style attributes",
    )


def _assert_transaction_modal_fragments(page, base_url: str, label: str) -> None:
    page.goto(f"{base_url}/transactions/?start=2025-01-01", wait_until="networkidle")
    _assert_shared_shell(page, f"{label} transactions shell")
    page.locator("#category_id").select_option(index=1)
    page.wait_for_function("document.querySelectorAll('#subcategory option').length > 1")
    _check(
        page.locator("#subcategory option").count() > 1,
        f"{label}: delegated transaction category filter must populate subcategories",
    )
    page.locator("#category_id").select_option("")
    initial = page.evaluate(
        """() => ({
            asset: Boolean(document.querySelector('script[src*="transaction-fragments.js"]')),
            rows: document.querySelectorAll('#txn-results tr.txn-clickable').length,
            styleAttributes: document.querySelectorAll('#main-content [style]').length,
            allowEval: window.htmx.config.allowEval,
            allowScriptTags: window.htmx.config.allowScriptTags,
        })"""
    )
    _check(initial["asset"], f"{label}: transaction fragment controller must load")
    _check(initial["rows"] > 0, f"{label}: synthetic transaction rows must render")
    _check(
        initial["styleAttributes"] == 0,
        f"{label}: transaction page must render without style attributes",
    )
    _check(
        initial["allowEval"] is False and initial["allowScriptTags"] is False,
        f"{label}: final global HTMX execution switches must be disabled",
    )

    filter_button = page.locator("#txn-filter-form button[type='submit']")
    for swap_number in (1, 2):
        with page.expect_response(
            lambda response: "/transactions/partial" in response.url
        ) as response_info:
            filter_button.click()
        _check(
            response_info.value.status == 200,
            f"{label} transaction swap {swap_number}: partial must return 200",
        )
        page.wait_for_selector("#txn-results tr.txn-clickable")
        fragment_state = page.evaluate(
            """() => {
                const root = document.getElementById('txn-results');
                const elements = [root, ...root.querySelectorAll('*')];
                return {
                    targets: document.querySelectorAll('#txn-results').length,
                    scriptElements: root.querySelectorAll('script').length,
                    nativeHandlers: elements.reduce((count, element) => count +
                        Array.from(element.attributes || []).filter(
                            (attribute) => /^on[a-z]/i.test(attribute.name)
                        ).length, 0),
                    hxOn: elements.reduce((count, element) => count +
                        Array.from(element.attributes || []).filter(
                            (attribute) => attribute.name.startsWith('hx-on')
                        ).length, 0),
                    styleAttributes: root.querySelectorAll('[style]').length,
                };
            }"""
        )
        _check(
            fragment_state == {
                "targets": 1,
                "scriptElements": 0,
                "nativeHandlers": 0,
                "hxOn": 0,
                "styleAttributes": 0,
            },
            f"{label} transaction swap {swap_number}: result fragment must remain execution-free",
        )

    with page.expect_response(
        lambda response: "/transactions/partial" in response.url
    ) as response_info:
        page.locator(
            '#txn-results [data-transaction-fragment-action="sort"][data-sort-column="amount"]'
        ).click()
    _check(response_info.value.status == 200, f"{label}: delegated transaction sort must return 200")
    _check(
        page.locator("#sort-field").input_value() == "amount",
        f"{label}: delegated transaction sort must update the filter state",
    )

    page.evaluate(
        """() => {
            navigator.clipboard.writeText = (text) => {
                window.__transactionFragmentClipboard = text;
                return Promise.resolve();
            };
        }"""
    )
    copy_button = page.locator(
        '#txn-results [data-transaction-fragment-action="copy-list"]'
    )
    copy_button.click()
    page.wait_for_function(
        "document.querySelector('[data-transaction-fragment-action=\"copy-list\"]').textContent.trim() === 'Copied!'"
    )
    _check(
        bool(page.evaluate("window.__transactionFragmentClipboard")),
        f"{label}: delegated copy control must produce a visible transaction list",
    )

    first_row = page.locator('#txn-results tr[id^="txn-4ag-personal-expense-00"]').first
    first_row.click()
    page.wait_for_selector("#txn-modal .txn-modal-backdrop")
    page.locator(
        '#txn-modal [data-transaction-fragment-action="close-transaction-modal"]'
    ).click()
    _check(page.locator("#txn-modal").inner_html() == "", f"{label}: modal close button must clear the fragment")

    first_row.click()
    page.wait_for_selector("#txn-modal .txn-modal-backdrop")
    page.locator("#txn-modal .txn-modal-backdrop").click(position={"x": 4, "y": 4})
    _check(page.locator("#txn-modal").inner_html() == "", f"{label}: backdrop click must close the modal")

    first_row.click()
    page.wait_for_selector("#txn-modal .txn-modal-form")
    _check(
        page.locator("#txn-modal [style]").count() == 0,
        f"{label}: transaction edit fragment must contain no style attributes",
    )
    with page.expect_response(
        lambda response: "/transactions/suggest/" in response.url
    ) as response_info:
        page.locator(
            '#txn-modal [data-transaction-fragment-action="suggest-category"]'
        ).click()
    _check(response_info.value.status == 200, f"{label}: synthetic AI suggestion must return 200")
    page.wait_for_function(
        "!document.querySelector('[data-transaction-fragment-action=\"suggest-category\"]').disabled"
    )
    _check(
        page.locator("#txn-modal .txn-ai-reason").text_content()
        == "Synthetic local-only browser suggestion",
        f"{label}: delegated suggestion control must render the synthetic reason",
    )
    subcategory_select = page.locator('#txn-modal select[name="subcategory"]')
    subcategory_select.select_option("__new__")
    subcategory_input = page.locator("#txn-modal .txn-subcat-add")
    _check(subcategory_input.is_visible(), f"{label}: delegated subcategory change must expose the input")
    subcategory_input.fill("Synthetic Browser Subcategory")
    subcategory_input.press("Enter")
    _check(
        subcategory_select.input_value() == "Synthetic Browser Subcategory"
        and subcategory_input.is_hidden(),
        f"{label}: delegated Enter handler must add and select the new subcategory",
    )
    page.locator('#txn-modal input[name="notes"]').fill("synthetic fragment browser verification")
    with page.expect_response(
        lambda response: "/transactions/update/" in response.url
    ) as response_info:
        page.locator('#txn-modal button[type="submit"]').click()
    _check(response_info.value.status == 200, f"{label}: transaction edit save must return 200")
    page.wait_for_function("document.getElementById('txn-modal').innerHTML === ''")

    page.evaluate(
        """() => window.htmx.ajax(
            'GET', '/transactions/edit-row/4ag-personal-expense-00',
            {target: '#txn-modal', swap: 'innerHTML'}
        )"""
    )
    page.wait_for_selector("#txn-modal .txn-modal-form")
    page.wait_for_timeout(100)
    with page.expect_response(
        lambda response: "/transactions/create-rule/" in response.url
    ) as response_info:
        page.locator('#txn-modal button[hx-post*="/transactions/create-rule/"]').click()
    _check(response_info.value.status == 200, f"{label}: delegated rule action must return 200")
    page.wait_for_function("document.getElementById('txn-modal').innerHTML === ''")

    page.evaluate(
        """() => window.htmx.ajax(
            'GET', '/transactions/edit-row/4ag-personal-expense-00',
            {target: '#txn-modal', swap: 'innerHTML'}
        )"""
    )
    page.wait_for_selector("#txn-modal .txn-modal-form")
    page.wait_for_timeout(100)
    with page.expect_response(
        lambda response: response.url.endswith("/transactions/splits/4ag-personal-expense-00")
    ) as response_info:
        page.locator(
            '#txn-modal button[hx-get="/transactions/splits/4ag-personal-expense-00"]'
        ).click()
    _check(response_info.value.status == 200, f"{label}: split editor request must return 200")
    page.wait_for_selector(
        '#txn-modal [data-transaction-fragment-controller="split-editor"]'
        '[data-transaction-fragment-initialized="true"]'
    )
    split_root = page.locator('#txn-modal [data-transaction-fragment-controller="split-editor"]')
    _check(split_root.locator("script").count() == 0, f"{label}: split editor must contain no script elements")
    _check(
        split_root.locator("[style]").count() == 0,
        f"{label}: split editor must contain no style attributes",
    )
    _check(
        page.locator("#txn-modal template[data-json]").count() == 2,
        f"{label}: split editor must retain both non-script JSON carriers",
    )
    initial_line_count = split_root.locator(".split-line").count()
    _check(initial_line_count == 2, f"{label}: unsplit transaction must start with two split lines")
    with page.expect_response(
        lambda response: "/splits/" in response.url and response.url.endswith("/auto")
    ) as response_info:
        split_root.locator('[data-transaction-fragment-action="split-auto"]').click()
    _check(response_info.value.status == 200, f"{label}: delegated auto-split must return 200")
    page.wait_for_selector(
        '#txn-modal [data-transaction-fragment-controller="split-editor"]'
        '[data-transaction-fragment-initialized="true"] '
        '[data-transaction-fragment-action="split-delete-all"]'
    )
    page.once("dialog", lambda dialog: dialog.accept())
    with page.expect_response(
        lambda response: "/splits/" in response.url and response.url.endswith("/delete")
    ) as response_info:
        page.locator(
            '#txn-modal [data-transaction-fragment-action="split-delete-all"]'
        ).click()
    _check(response_info.value.status == 200, f"{label}: auto-split cleanup must return 200")
    page.wait_for_function("document.getElementById('txn-modal').innerHTML === ''")

    page.evaluate(
        """() => window.htmx.ajax(
            'GET', '/transactions/edit-row/4ag-personal-expense-00',
            {target: '#txn-modal', swap: 'innerHTML'}
        )"""
    )
    page.wait_for_selector("#txn-modal .txn-modal-form")
    page.wait_for_timeout(100)
    with page.expect_response(
        lambda response: response.url.endswith("/transactions/splits/4ag-personal-expense-00")
    ) as response_info:
        page.locator(
            '#txn-modal button[hx-get="/transactions/splits/4ag-personal-expense-00"]'
        ).click()
    _check(response_info.value.status == 200, f"{label}: manual split editor request must return 200")
    page.wait_for_selector(
        '#txn-modal [data-transaction-fragment-controller="split-editor"]'
        '[data-transaction-fragment-initialized="true"]'
    )
    split_root = page.locator('#txn-modal [data-transaction-fragment-controller="split-editor"]')
    split_root.locator('[data-transaction-fragment-action="split-add-line"]').click()
    _check(split_root.locator(".split-line").count() == 3, f"{label}: delegated split add must append a line")
    _check(
        split_root.locator("[style]").count() == 0,
        f"{label}: generated split lines must remain style-attribute free",
    )
    split_root.locator('[data-transaction-fragment-action="split-remove-line"]').last.click()
    _check(split_root.locator(".split-line").count() == 2, f"{label}: delegated split remove must remove a line")
    parent_cents = int(split_root.get_attribute("data-parent-cents"))
    first_cents = int(parent_cents / 2)
    second_cents = parent_cents - first_cents
    amount_inputs = split_root.locator(".split-amount")
    amount_inputs.nth(0).fill(str(first_cents))
    amount_inputs.nth(1).fill(str(second_cents))
    expected_total = f"{'\u2212' if parent_cents < 0 else ''}${abs(parent_cents) / 100:,.2f}"
    _check(
        split_root.locator("#split-total-display").text_content() == expected_total,
        f"{label}: split running total must track delegated amount input",
    )
    _check(
        "txn-split-total--balanced"
        in split_root.locator("#split-total-bar").get_attribute("class").split(),
        f"{label}: balanced split total must use the maintained state class",
    )
    with page.expect_response(
        lambda response: "/splits/" in response.url and response.url.endswith("/save")
    ) as response_info:
        split_root.locator('[data-transaction-fragment-action="split-save"]').click()
    _check(response_info.value.status == 200, f"{label}: split save must return 200")
    page.wait_for_function("document.getElementById('txn-modal').innerHTML === ''")
    page.wait_for_selector("#txn-results tr.txn-clickable")
    page.evaluate(
        """() => window.htmx.ajax(
            'GET', '/transactions/splits/4ag-personal-expense-00',
            {target: '#txn-modal', swap: 'innerHTML'}
        )"""
    )
    page.wait_for_selector(
        '#txn-modal [data-transaction-fragment-action="split-delete-all"]'
    )
    page.once("dialog", lambda dialog: dialog.accept())
    with page.expect_response(
        lambda response: "/splits/" in response.url and response.url.endswith("/delete")
    ) as response_info:
        page.locator(
            '#txn-modal [data-transaction-fragment-action="split-delete-all"]'
        ).click()
    _check(response_info.value.status == 200, f"{label}: manual split cleanup must return 200")
    page.wait_for_function("document.getElementById('txn-modal').innerHTML === ''")

    page.goto(f"{base_url}/todo/", wait_until="networkidle")
    _assert_shared_shell(page, f"{label} todo shell")
    with page.expect_response(
        lambda response: "/todo/queue/large-txns" in response.url
    ) as response_info:
        page.locator('[hx-get="/todo/queue/large-txns"]').click()
    _check(response_info.value.status == 200, f"{label}: todo queue fragment must return 200")
    page.wait_for_selector(
        '#tq-modal-body [data-transaction-fragment-action="close-todo-queue"]'
    )
    todo_modal = page.locator("#tq-modal-scrim")
    _check(todo_modal.is_visible(), f"{label}: todo queue modal must open")
    page.locator(
        '#tq-modal-body [data-transaction-fragment-action="close-todo-queue"]'
    ).click()
    _check(todo_modal.is_hidden(), f"{label}: delegated todo queue control must close")
    _check(
        page.locator("#tq-modal-body").inner_html() == "",
        f"{label}: todo queue close must clear the swapped fragment",
    )
    queue_control = page.locator('[hx-get="/todo/queue/large-txns"]')
    queue_control.focus()
    with page.expect_response(
        lambda response: "/todo/queue/large-txns" in response.url
    ) as response_info:
        page.keyboard.press("Enter")
    _check(response_info.value.status == 200, f"{label}: keyboard todo queue request must return 200")
    page.wait_for_selector('#tq-modal-body [data-transaction-fragment-action="close-todo-queue"]')
    _check(todo_modal.is_visible(), f"{label}: delegated keyboard activation must open the todo modal")
    page.keyboard.press("Escape")
    _check(todo_modal.is_hidden(), f"{label}: Escape must close the todo queue modal")
    page.goto(f"{base_url}/transactions/?start=2025-01-01", wait_until="networkidle")
    page.wait_for_selector("#txn-results tr.txn-clickable")


def _assert_transaction_matching_styles(page, base_url: str, label: str) -> None:
    entity_names = ("Personal", "BFM", "LL")
    viewport_cases = (
        (390, 844, "phone"),
        (768, 900, "exact-768"),
        (1280, 900, "desktop"),
    )

    for entity_name in entity_names:
        page.context.add_cookies(
            [{"name": "entity", "value": entity_name, "url": base_url}]
        )
        for width, height, viewport_label in viewport_cases:
            page.set_viewport_size({"width": width, "height": height})
            page.goto(
                f"{base_url}/transactions/?start=2025-01-01",
                wait_until="networkidle",
            )
            responsive_state = page.evaluate(
                """() => {
                    const dateGroup = document.querySelector(".txn-filter-date");
                    const filter = document.querySelector(".txn-filter-bar");
                    return {
                        styleAttributes: document.querySelectorAll(
                            "#main-content [style]"
                        ).length,
                        dateWidth: dateGroup.getBoundingClientRect().width,
                        filterWidth: filter.getBoundingClientRect().width,
                        pageOverflow:
                            document.documentElement.scrollWidth
                            > window.innerWidth + 1,
                    };
                }"""
            )
            _check(
                responsive_state["styleAttributes"] == 0,
                f"{label}: {entity_name} {viewport_label} transactions must contain no style attributes",
            )
            _check(
                not responsive_state["pageOverflow"],
                f"{label}: {entity_name} {viewport_label} transactions must not overflow the page",
            )
            if viewport_label == "phone":
                _check(
                    responsive_state["dateWidth"]
                    >= responsive_state["filterWidth"] - 40,
                    f"{label}: {entity_name} phone filters must stack at full width",
                )
            elif viewport_label == "exact-768":
                _check(
                    responsive_state["filterWidth"] * 0.4
                    <= responsive_state["dateWidth"]
                    <= responsive_state["filterWidth"] * 0.6,
                    f"{label}: {entity_name} exact-768 filters must preserve the two-column layout",
                )
            else:
                _check(
                    125 <= responsive_state["dateWidth"] <= 135,
                    f"{label}: {entity_name} desktop date filters must preserve their fixed width",
                )

    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.set_viewport_size({"width": 390, "height": 844})

    page.goto(f"{base_url}/__synthetic-4at/match-card", wait_until="networkidle")
    match_state = page.evaluate(
        """() => ({
            styleAttributes: document.querySelectorAll("#main-content [style]").length,
            boundedProgress: Boolean(document.querySelector(
                ".progress-fill.u-width-pct.u-pct-50"
            )),
            warningMetrics: document.querySelectorAll(
                ".match-metric--warning"
            ).length,
            pageOverflow:
                document.documentElement.scrollWidth > window.innerWidth + 1,
        })"""
    )
    _check(
        match_state
        == {
            "styleAttributes": 0,
            "boundedProgress": True,
            "warningMetrics": 2,
            "pageOverflow": False,
        },
        f"{label}: synthetic matching card must preserve bounded progress warning state and phone layout without style attributes",
    )

    page.goto(f"{base_url}/__synthetic-4at/vendor-card", wait_until="networkidle")
    vendor_state = page.evaluate(
        """() => ({
            styleAttributes: document.querySelectorAll("#main-content [style]").length,
            boundedProgress: Boolean(document.querySelector(
                ".progress-fill.u-width-pct.u-pct-60"
            )),
            formClass: Boolean(document.querySelector(
                "form.vendor-card-form"
            )),
            pageOverflow:
                document.documentElement.scrollWidth > window.innerWidth + 1,
        })"""
    )
    _check(
        vendor_state
        == {
            "styleAttributes": 0,
            "boundedProgress": True,
            "formClass": True,
            "pageOverflow": False,
        },
        f"{label}: synthetic vendor card must preserve bounded progress form layout and phone width without style attributes",
    )

    page.goto(f"{base_url}/transactions/?start=2025-01-01", wait_until="networkidle")


def _assert_categorization_upload_pages(page, base_url: str, label: str) -> None:
    entity_names = ("Personal", "BFM", "LL")
    viewport_cases = (
        (390, 844, "phone"),
        (768, 900, "exact-768"),
        (1280, 900, "desktop"),
    )

    for entity_name in entity_names:
        page.context.add_cookies(
            [{"name": "entity", "value": entity_name, "url": base_url}]
        )
        for width, height, viewport_label in viewport_cases:
            page.set_viewport_size({"width": width, "height": height})

            page.goto(
                f"{base_url}/__synthetic-4au/categorize-pagination",
                wait_until="networkidle",
            )
            categorization_style_state = page.evaluate(
                """() => ({
                    styleAttributes: document.querySelectorAll(
                        "#main-content [style]"
                    ).length,
                    styleBlocks: document.querySelectorAll(
                        "#main-content style"
                    ).length,
                    compactControl: Boolean(document.querySelector(
                        ".cat-compact-control"
                    )),
                    lowConfidence: Boolean(document.querySelector(
                        ".cat-low-confidence"
                    )),
                    pageButtons: document.querySelectorAll(
                        ".cat-page-button"
                    ).length,
                    pageOverflow:
                        document.documentElement.scrollWidth
                        > window.innerWidth + 1,
                })"""
            )
            _check(
                categorization_style_state
                == {
                    "styleAttributes": 0,
                    "styleBlocks": 0,
                    "compactControl": True,
                    "lowConfidence": True,
                    "pageButtons": 3,
                    "pageOverflow": False,
                },
                f"{label}: {entity_name} {viewport_label} categorization must preserve compact confidence pagination layout without inline styles or page overflow",
            )

            page.goto(
                f"{base_url}/categorize/orphans",
                wait_until="networkidle",
            )
            orphan_style_state = page.evaluate(
                """() => {
                    const row = document.querySelector(".cat-orphan-row");
                    return {
                        styleAttributes: document.querySelectorAll(
                            "#main-content [style]"
                        ).length,
                        panel: Boolean(document.querySelector(
                            ".cat-orphan-panel"
                        )),
                        fields: document.querySelectorAll(
                            ".cat-orphan-field"
                        ).length,
                        rowDirection: getComputedStyle(row).flexDirection,
                        pageOverflow:
                            document.documentElement.scrollWidth
                            > window.innerWidth + 1,
                    };
                }"""
            )
            expected_orphan_direction = (
                "row" if viewport_label == "desktop" else "column"
            )
            _check(
                orphan_style_state["styleAttributes"] == 0
                and orphan_style_state["panel"]
                and orphan_style_state["fields"] == 2
                and orphan_style_state["rowDirection"]
                == expected_orphan_direction
                and not orphan_style_state["pageOverflow"],
                f"{label}: {entity_name} {viewport_label} orphan reassignment must preserve responsive semantic layout without style attributes",
            )

            page.goto(f"{base_url}/upload/", wait_until="networkidle")
            upload_style_state = page.evaluate(
                """() => {
                    const progress = document.querySelector(
                        ".progress-fill.u-width-pct"
                    );
                    return {
                        styleAttributes: document.querySelectorAll(
                            "#main-content [style]"
                        ).length,
                        boundedProgress:
                            Boolean(progress)
                            && Array.from(progress.classList).some(
                                (name) => name.startsWith("u-pct-")
                            ),
                        monthField: Boolean(document.querySelector(
                            ".upload-month-field"
                        )),
                        pageOverflow:
                            document.documentElement.scrollWidth
                            > window.innerWidth + 1,
                    };
                }"""
            )
            _check(
                upload_style_state
                == {
                    "styleAttributes": 0,
                    "boundedProgress": True,
                    "monthField": True,
                    "pageOverflow": False,
                },
                f"{label}: {entity_name} {viewport_label} upload checklist must preserve bounded progress and responsive layout without style attributes",
            )

            page.goto(
                f"{base_url}/__synthetic-4au/upload-dialog",
                wait_until="networkidle",
            )
            preview_style_state = page.evaluate(
                """() => ({
                    styleAttributes: document.querySelectorAll(
                        "#main-content [style]"
                    ).length,
                    metrics: document.querySelectorAll(
                        ".import-preview-metric"
                    ).length,
                    credit: Boolean(document.querySelector(
                        ".import-preview-value--credit"
                    )),
                    debit: Boolean(document.querySelector(
                        ".import-preview-value--debit"
                    )),
                    rename: Boolean(document.querySelector(
                        ".import-preview-rename"
                    )),
                    pageOverflow:
                        document.documentElement.scrollWidth
                        > window.innerWidth + 1,
                })"""
            )
            _check(
                preview_style_state
                == {
                    "styleAttributes": 0,
                    "metrics": 4,
                    "credit": True,
                    "debit": True,
                    "rename": True,
                    "pageOverflow": False,
                },
                f"{label}: {entity_name} {viewport_label} upload preview must preserve metric and rename layout without style attributes or page overflow",
            )

    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.set_viewport_size({"width": 390, "height": 844})

    page.goto(f"{base_url}/categorize/", wait_until="networkidle")
    page.wait_for_function(
        "document.querySelector('[data-categorization-controller]')?.dataset.initialized === 'true'"
    )
    page.wait_for_selector('[data-categorization-change="category"]')
    category_select = page.locator('[data-categorization-change="category"]').first
    subcategory_select = page.locator('select[name^="subcat_"]').first
    initial = page.evaluate(
        """() => ({
            asset: Boolean(document.querySelector('script[src*="categorization-upload.js"]')),
            inlineHandlers: document.querySelectorAll(
                '#main-content [onclick], #main-content [onchange], #main-content [onsubmit], #main-content [onkeydown]'
            ).length,
            allowEval: window.htmx.config.allowEval,
            allowScriptTags: window.htmx.config.allowScriptTags,
        })"""
    )
    _check(initial["asset"], f"{label}: categorization/upload controller must load")
    _check(initial["inlineHandlers"] == 0, f"{label}: included page must expose no native inline handlers")
    _check(
        initial["allowEval"] is False and initial["allowScriptTags"] is False,
        f"{label}: HTMX execution switches must remain disabled",
    )

    alias_control = page.locator(
        '[data-categorization-action="prefill-alias"]'
        '[data-description="PAYPAL * SYNTHETIC ALIAS TX"]'
    )
    _check(alias_control.count() == 1, f"{label}: synthetic alias prefill control must render")
    _check(
        alias_control.is_hidden(),
        f"{label}: alias control must start hidden until its transaction row is hovered",
    )
    alias_control.locator("xpath=ancestor::tr").hover()
    _check(
        alias_control.is_visible(),
        f"{label}: maintained hover CSS must reveal the alias control",
    )
    alias_control.evaluate("element => element.click()")
    alias_state = page.evaluate(
        """() => ({
            pattern: document.getElementById('alias-pattern').value,
            canonical: document.getElementById('alias-canonical').value,
            open: document.getElementById('alias-details').open,
        })"""
    )
    _check(
        alias_state == {
            "pattern": "SYNTHETIC ALIAS",
            "canonical": "SYNTHETIC ALIAS",
            "open": True,
        },
        f"{label}: delegated alias prefill must preserve prefix stripping and details expansion",
    )

    category_select.select_option("Food")
    page.wait_for_function(
        "Array.from(document.querySelector('select[name^=\"subcat_\"]')?.options || [])"
        ".some((option) => option.value === 'Coffee')"
    )
    _check(
        "Coffee" in subcategory_select.locator("option").all_text_contents(),
        f"{label}: delegated category change must populate maintained subcategories",
    )

    page.goto(f"{base_url}/categorize/?tab=settings", wait_until="networkidle")
    alias_dialogs: list[str] = []

    def dismiss_alias_dialog(dialog) -> None:
        alias_dialogs.append(dialog.message)
        dialog.dismiss()

    page.once("dialog", dismiss_alias_dialog)
    page.locator('form[action*="/categorize/delete-alias/"] [data-confirm-message]').first.click()
    _check(alias_dialogs == ["Delete this alias?"], f"{label}: alias delete confirmation must be delegated")

    page.goto(f"{base_url}/categorize/orphans", wait_until="networkidle")
    orphan_category = page.locator('[data-categorization-change="orphan-category"]').first
    _check(orphan_category.count() == 1, f"{label}: synthetic orphan reassignment control must render")
    with page.expect_response(
        lambda response: "/categorize/subcategories" in response.url
    ) as response_info:
        orphan_category.select_option("Food")
    _check(response_info.value.status == 200, f"{label}: orphan subcategory request must return 200")
    _check(
        "Coffee" in page.locator(".orphan-sub").first.locator("option").all_text_contents(),
        f"{label}: delegated orphan category change must populate subcategories",
    )

    page.goto(f"{base_url}/upload/", wait_until="networkidle")
    mark_incomplete = page.get_by_role("button", name="Mark incomplete", exact=True)
    _check(mark_incomplete.count() == 1, f"{label}: status-only action must use the explicit label")
    status_dialogs: list[str] = []

    def dismiss_status_dialog(dialog) -> None:
        status_dialogs.append(dialog.message)
        dialog.dismiss()

    page.once("dialog", dismiss_status_dialog)
    mark_incomplete.click()
    _check(
        status_dialogs == [
            "Mark this source incomplete? Imported transactions will remain in the ledger."
        ],
        f"{label}: status-only confirmation must say imported transactions remain",
    )

    month_select = page.locator('[data-upload-change="month"]')
    second_month = month_select.locator("option").nth(1).get_attribute("value")
    with page.expect_navigation(wait_until="networkidle"):
        month_select.select_option(index=1)
    _check(
        page.url.endswith("?month=" + second_month),
        f"{label}: delegated upload month navigation must preserve the selected month",
    )

    page.goto(f"{base_url}/upload/?tab=settings", wait_until="networkidle")
    source_dialogs: list[str] = []
    profile_dialogs: list[str] = []

    def dismiss_source_dialog(dialog) -> None:
        source_dialogs.append(dialog.message)
        dialog.dismiss()

    def dismiss_profile_dialog(dialog) -> None:
        profile_dialogs.append(dialog.message)
        dialog.dismiss()

    page.once("dialog", dismiss_source_dialog)
    page.locator('form[action*="/upload/delete-source/"] [data-confirm-message]').first.click()
    page.once("dialog", dismiss_profile_dialog)
    page.locator('form[action*="/upload/delete-profile/"] [data-confirm-message]').first.click()
    _check(source_dialogs == ["Delete this source?"], f"{label}: source delete confirmation must be delegated")
    _check(profile_dialogs == ["Delete this profile?"], f"{label}: profile delete confirmation must be delegated")


def _assert_cashflow_planning_pages(page, base_url: str, label: str) -> None:
    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(f"{base_url}/cashflow/", wait_until="networkidle")
    page.wait_for_function(
        "document.querySelector('[data-cashflow-controller]')?.dataset.initialized === 'true'"
    )
    cashflow_state = page.evaluate(
        """() => ({
            asset: Boolean(document.querySelector('script[src*="cashflow.js"]')),
            inlineHandlers: document.querySelectorAll(
                '#main-content [onclick], #main-content [onchange], #main-content [onfocus], '
                + '#main-content [oninput], #main-content [onblur], #main-content [onsubmit], '
                + '#main-content [onkeydown]'
            ).length,
            personal: Boolean(document.querySelector('[data-acct-name="4AL Personal Checking"]')),
            company: Boolean(document.querySelector('[data-acct-name="4AL BFM Checking"]')),
            styleAttrs: document.querySelectorAll("#main-content [style]").length,
        })"""
    )
    _check(cashflow_state["asset"], f"{label}: Cash Flow controller must load")
    _check(
        cashflow_state["inlineHandlers"] == 0,
        f"{label}: Cash Flow must expose no native inline handlers",
    )
    _check(
        cashflow_state["personal"] and cashflow_state["company"],
        f"{label}: Cash Flow must preserve Personal/BFM shared visibility",
    )
    _check(
        cashflow_state["styleAttrs"] == 0,
        f"{label}: Cash Flow must render without style attributes",
    )

    credit_card = page.locator(
        '.cf-box--card[data-cashflow-action="flip-open"]'
    ).first
    credit_card.evaluate("element => element.click()")
    page.wait_for_timeout(300)
    page.wait_for_function("!document.getElementById('cf-modal-scrim').hidden")
    card_modal = page.evaluate(
        """() => ({
            title: document.getElementById('cf-modal-title').textContent,
            action: document.getElementById('cf-modal-form').action,
            cardClass: document.querySelector('.cfm').classList.contains('cfm--card'),
            cardFieldsVisible: !document.getElementById('cf-modal-card-group').hidden,
            dueDisplay: document.getElementById('cf-modal-due-display').value,
            dueHidden: document.getElementById('cf-modal-due-day-hidden').value,
            payment: document.getElementById('cf-modal-payment').value,
            balanceSize: document.getElementById('cf-modal-balance').size,
            dueSize: document.getElementById('cf-modal-due-display').size,
            animationFrames: document.querySelector('.cfm').getAnimations()
                .flatMap((animation) => animation.effect.getKeyframes()),
            styleAttrs: document.querySelectorAll("#main-content [style]").length,
        })"""
    )
    _check(
        card_modal["title"] == "4AL Personal Credit"
        and card_modal["action"].endswith("/cashflow/accounts/update-card/2")
        and card_modal["cardClass"]
        and card_modal["cardFieldsVisible"]
        and card_modal["dueDisplay"] == "Aug 17"
        and card_modal["dueHidden"] == "17"
        and card_modal["payment"] == "275"
        and card_modal["balanceSize"] >= 2
        and card_modal["dueSize"] >= 2
        and card_modal["styleAttrs"] == 0
        and len(card_modal["animationFrames"]) >= 2
        and "translate3d(" in card_modal["animationFrames"][0]["transform"]
        and "scale(0.05)" in card_modal["animationFrames"][0]["transform"],
        f"{label}: delegated credit-card modal must preserve populated card fields",
    )
    due_display = page.locator("#cf-modal-due-display")
    due_display.fill("31")
    _check(
        page.locator("#cf-modal-due-day-hidden").input_value() == "31"
        and due_display.get_attribute("style") is None
        and int(due_display.get_attribute("size")) >= 3,
        f"{label}: delegated due-day parsing must preserve valid days",
    )
    due_display.fill("32")
    _check(
        page.locator("#cf-modal-due-day-hidden").input_value() == "",
        f"{label}: delegated due-day parsing must reject invalid days",
    )
    due_display.fill("17")
    page.keyboard.press("Escape")
    page.wait_for_timeout(350)
    _check(
        page.locator("#cf-modal-scrim").is_hidden(),
        f"{label}: Escape must close the Cash Flow modal",
    )

    bank_card = page.locator(
        '.cf-grid--banks [data-cashflow-action="flip-open"]'
    ).first
    bank_card.evaluate("element => element.click()")
    page.wait_for_timeout(300)
    bank_modal = page.evaluate(
        """() => ({
            title: document.getElementById('cf-modal-title').textContent,
            action: document.getElementById('cf-modal-form').action,
            bankClass: document.querySelector('.cfm').classList.contains('cfm--bank'),
            cardFieldsHidden: document.getElementById('cf-modal-card-group').hidden,
        })"""
    )
    _check(
        bank_modal["title"] == "4AL Personal Checking"
        and "/cashflow/accounts/update/" in bank_modal["action"]
        and bank_modal["bankClass"]
        and bank_modal["cardFieldsHidden"],
        f"{label}: delegated bank modal must preserve account-specific behavior",
    )
    page.locator('[data-cashflow-action="close-modal"]').click()
    page.wait_for_timeout(350)

    page.locator(
        '[data-app-shell-action="open-ai-chat"][data-ai-page="cashflow"]'
    ).click()
    _check(
        page.locator("#ai-chat-scrim").is_visible()
        and page.locator("#ai-chat-page").input_value() == "cashflow",
        f"{label}: Cash Flow AI entry must use the maintained app-shell action",
    )
    page.locator("[data-ai-chat-close]").click()

    page.goto(f"{base_url}/planning/", wait_until="networkidle")
    page.wait_for_function(
        "document.querySelector('[data-planning-controller]')?.dataset.initialized === 'true'"
    )
    planning_state = page.evaluate(
        """() => ({
            asset: Boolean(document.querySelector('script[src*="planning.js"]')),
            inlineHandlers: document.querySelectorAll(
                '#main-content [onclick], #main-content [onchange], #main-content [onfocus], '
                + '#main-content [oninput], #main-content [onblur], #main-content [onsubmit], '
                + '#main-content [onkeydown]'
            ).length,
            personal: Boolean(document.querySelector('#pl-card-1')),
            company: Array.from(document.querySelectorAll('.pl-cross .pl-box-name')).some(
                (element) => element.textContent.includes('4AL BFM')
            ),
            staticCards: document.querySelectorAll(".pl-cross .pl-box--static").length,
            styleAttrs: document.querySelectorAll("#main-content [style]").length,
        })"""
    )
    _check(planning_state["asset"], f"{label}: Planning controller must load")
    _check(
        planning_state["inlineHandlers"] == 0,
        f"{label}: Long-Term Planning must expose no native inline handlers",
    )
    _check(
        planning_state["personal"] and planning_state["company"],
        f"{label}: Long-Term Planning must preserve Personal/BFM shared visibility",
    )
    _check(
        planning_state["staticCards"] >= 1
        and planning_state["styleAttrs"] == 0,
        f"{label}: Long-Term Planning must use static cross-entity cards without style attributes",
    )

    primary_card = page.locator(
        '.pl-entity-section:not(.pl-cross) [data-planning-action="flip-open"]'
    ).first
    primary_card.evaluate("element => element.click()")
    page.wait_for_timeout(300)
    visible_edit = page.locator(".pl-modal-form:not([hidden])")
    _check(
        visible_edit.count() == 1
        and visible_edit.locator(".pl-box-projections").count() == 1
        and page.evaluate(
            """() => {
                const frames = document.querySelector(".pl-modal-popup")
                    .getAnimations()
                    .flatMap((animation) => animation.effect.getKeyframes());
                return frames.length >= 2
                    && frames[0].transform.includes("translate3d(")
                    && frames[0].transform.includes("scale(0.05)");
            }"""
        ),
        f"{label}: delegated item-card opening must preserve projections and one visible edit form",
    )
    source_select = visible_edit.locator('[data-planning-change="source"]')
    source_select.select_option("manual")
    _check(
        not visible_edit.locator('input[name="current_value"]').is_disabled()
        and visible_edit.locator(".pl-g-cfaccount").is_hidden()
        and visible_edit.locator('input[name="current_value"]').evaluate(
            "element => getComputedStyle(element).opacity"
        )
        == "1",
        f"{label}: manual source selection must enable the maintained value input",
    )
    source_select.select_option("cashflow")
    _check(
        visible_edit.locator('input[name="current_value"]').is_disabled()
        and visible_edit.locator(".pl-g-cfaccount").is_visible()
        and visible_edit.locator('input[name="current_value"]').evaluate(
            "element => getComputedStyle(element).opacity"
        )
        == "0.5"
        and visible_edit.locator('input[name="current_value"]').get_attribute("style")
        is None,
        f"{label}: Cash Flow source selection must expose the linked-account control",
    )
    page.keyboard.press("Escape")
    page.wait_for_timeout(350)
    _check(
        page.locator("#pl-modal-scrim").is_hidden(),
        f"{label}: Escape must close the Long-Term Planning modal",
    )

    add_asset = page.locator(
        '[data-planning-action="open-add"][data-item-type="asset"]'
    ).first
    add_asset.click()
    add_form = page.locator("#pl-add-form-personal-asset")
    _check(add_form.is_visible(), f"{label}: delegated add-asset control must open")
    add_form.locator('input[name="name"]').fill("4AL Browser Added Asset")
    add_form.locator('input[name="current_value"]').fill("1,234")
    add_form.locator('input[name="annual_rate"]').fill("5.5")
    add_form.locator('[data-planning-change="source"]').select_option("manual")
    with page.expect_navigation(wait_until="networkidle"):
        add_form.locator('button[type="submit"]').click()
    added_card = page.locator(".pl-box", has_text="4AL Browser Added Asset")
    _check(added_card.count() == 1, f"{label}: add form must create the synthetic asset")

    added_card.evaluate("element => element.click()")
    page.wait_for_timeout(300)
    edit_form = page.locator(".pl-modal-form:not([hidden])")
    edit_form.locator('input[name="name"]').fill("4AL Browser Updated Asset")
    edit_form.locator('input[name="current_value"]').fill("2,345")
    with page.expect_navigation(wait_until="networkidle"):
        edit_form.locator('button[type="submit"]').click()
    updated_card = page.locator(".pl-box", has_text="4AL Browser Updated Asset")
    _check(updated_card.count() == 1, f"{label}: edit form must update the synthetic asset")

    updated_card.evaluate("element => element.click()")
    page.wait_for_timeout(300)
    delete_dialogs: list[str] = []

    def dismiss_delete(dialog) -> None:
        delete_dialogs.append(dialog.message)
        dialog.dismiss()

    page.once("dialog", dismiss_delete)
    page.locator(".pl-modal-form:not([hidden]) [data-planning-action='delete-item']").click()
    _check(
        delete_dialogs == ["Delete this item?"]
        and page.locator(".pl-box", has_text="4AL Browser Updated Asset").count() == 1,
        f"{label}: delegated delete confirmation must preserve the item when dismissed",
    )
    page.once("dialog", lambda dialog: dialog.accept())
    with page.expect_navigation(wait_until="networkidle"):
        page.locator(".pl-modal-form:not([hidden]) [data-planning-action='delete-item']").click()
    _check(
        page.locator(".pl-box", has_text="4AL Browser Updated Asset").count() == 0,
        f"{label}: accepted delete confirmation must remove only the synthetic item",
    )

    page.locator('[data-planning-action="edit-age"]').click()
    birth_date = page.locator("#pl-birth-date")
    _check(birth_date.is_visible(), f"{label}: birthday editor must become visible")
    with page.expect_navigation(wait_until="networkidle"):
        birth_date.evaluate(
            """element => {
                element.value = '1980-01-01';
                element.dispatchEvent(new Event('change', {bubbles: true}));
            }"""
        )
    _check(
        page.locator("#pl-birth-date").input_value() == "1980-01-01",
        f"{label}: delegated birthday save must persist through the maintained settings route",
    )

    page.locator(
        '[data-app-shell-action="open-ai-chat"][data-ai-page="planning"]'
    ).click()
    _check(
        page.locator("#ai-chat-scrim").is_visible()
        and page.locator("#ai-chat-page").input_value() == "planning",
        f"{label}: Planning AI entry must use the maintained app-shell action",
    )
    page.locator("[data-ai-chat-close]").click()


def _assert_short_term_planning_page(page, base_url: str, label: str) -> None:
    current_month = date.today().strftime("%Y-%m")
    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(
        f"{base_url}/planning/short-term/?month={current_month}",
        wait_until="networkidle",
    )
    page.wait_for_function(
        "document.querySelector('[data-short-term-planning-controller]')"
        "?.dataset.initialized === 'true'"
    )
    initial = page.evaluate(
        """() => ({
            asset: Boolean(document.querySelector('script[src*="short-term-planning.js"]')),
            inertTemplate: document.getElementById('stp-goals-data')?.tagName === 'TEMPLATE',
            inlineHandlers: document.querySelectorAll(
                '#main-content [onclick], #main-content [onchange], #main-content [onfocus], '
                + '#main-content [oninput], #main-content [onblur], #main-content [onsubmit], '
                + '#main-content [onkeydown]'
            ).length,
            goal: Boolean(document.querySelector(
                '.stp-goal-card[data-stp-action="flip-open"][data-goal-id]'
            )),
            action: Array.from(document.querySelectorAll('.stp-action-title')).some(
                (element) => element.textContent.includes('4AM Personal Action')
            ),
            boundedProgress: document.querySelectorAll(
                ".stp-progress-fill.u-width-pct[class*='u-pct-'], "
                + ".stp-budget-fill.u-width-pct[class*='u-pct-']"
            ).length,
            styleAttrs: document.querySelectorAll("#main-content [style]").length,
            allowEval: window.htmx.config.allowEval,
            allowScriptTags: window.htmx.config.allowScriptTags,
        })"""
    )
    _check(
        initial["asset"] and initial["inertTemplate"],
        f"{label}: Short-Term Planning controller and inert goal data must load",
    )
    _check(
        initial["inlineHandlers"] == 0,
        f"{label}: Short-Term Planning must expose no native inline handlers",
    )
    _check(
        initial["goal"] and initial["action"],
        f"{label}: synthetic Personal goal and action must remain visible",
    )
    _check(
        initial["boundedProgress"] >= 1 and initial["styleAttrs"] == 0,
        f"{label}: Short-Term Planning must use bounded progress classes without style attributes",
    )
    _check(
        initial["allowEval"] is False and initial["allowScriptTags"] is False,
        f"{label}: disabled HTMX execution switches must remain intact",
    )

    goal_card = page.locator(
        '.stp-goal-card[data-stp-action="flip-open"]',
        has_text="4AM Personal Goal",
    )
    goal_card.evaluate("element => element.click()")
    page.wait_for_timeout(300)
    _check(
        page.locator("#stp-goal-scrim").is_visible()
        and page.locator("#stp-popup-name").text_content() == "4AM Personal Goal"
        and page.locator("#stp-popup-strategy").text_content() == "Avalanche"
        and page.locator("#stp-popup-plan-btn").text_content() == "Update Plan"
        and page.evaluate(
            """() => {
                const frames = document.getElementById("stp-goal-popup")
                    .getAnimations()
                    .flatMap((animation) => animation.effect.getKeyframes());
                return frames.length >= 2
                    && frames[0].transform.includes("translate3d(")
                    && frames[0].transform.includes("scale(0.05)");
            }"""
        ),
        f"{label}: delegated goal-card opening must populate the maintained popup",
    )
    page.keyboard.press("Escape")
    page.wait_for_timeout(350)
    _check(
        page.locator("#stp-goal-scrim").is_hidden(),
        f"{label}: Escape must close the goal popup",
    )

    goal_card.evaluate("element => element.click()")
    page.wait_for_timeout(300)
    page.locator('[data-stp-action="edit-current-goal"]').click()
    edit_dialog = page.locator("#stp-edit-modal")
    _check(
        edit_dialog.is_visible()
        and edit_dialog.locator("#stp-edit-name").input_value()
        == "4AM Personal Goal"
        and edit_dialog.locator("#stp-edit-form").get_attribute("action").endswith(
            "/planning/short-term/goals/1/update"
        ),
        f"{label}: delegated edit action must populate the goal-specific form",
    )
    edit_dialog.locator('[data-stp-action="close-dialog"]').first.click()
    page.wait_for_timeout(350)

    goal_card.evaluate("element => element.click()")
    page.wait_for_timeout(300)
    page.locator('[data-stp-action="lock-current-goal"]').click()
    lock_dialog = page.locator("#stp-lock-modal")
    _check(
        lock_dialog.is_visible()
        and lock_dialog.locator("#stp-lock-strategy-group").is_visible()
        and lock_dialog.locator("#stp-lock-narrative").input_value()
        == "Pay the highest APR first.",
        f"{label}: delegated plan action must preserve debt strategy and narrative",
    )
    lock_dialog.locator('[data-stp-action="close-dialog"]').first.click()
    page.wait_for_timeout(350)

    goal_card.evaluate("element => element.click()")
    page.wait_for_timeout(300)
    review_button = page.locator('[data-stp-action="review-current-goal"]')
    _check(review_button.is_visible(), f"{label}: monthly review action must remain visible")
    review_button.click()
    review_dialog = page.locator("#stp-review-1")
    _check(
        review_dialog.is_visible(),
        f"{label}: delegated monthly review action must open its goal dialog",
    )
    review_dialog.locator('[data-stp-action="close-dialog"]').click()
    page.wait_for_timeout(350)

    page.locator('[data-stp-action="open-dialog"][data-dialog-id="stp-add-modal"]').click()
    add_dialog = page.locator("#stp-add-modal")
    add_dialog.get_by_text("Savings", exact=True).click()
    _check(
        add_dialog.locator("#stp-debt-fields").is_hidden()
        and add_dialog.locator("#stp-savings-fields").is_visible()
        and add_dialog.locator("#stp-spending-fields").is_hidden(),
        f"{label}: delegated goal-type change must preserve conditional fields",
    )
    add_dialog.locator('[data-stp-action="close-dialog"]').first.click()

    category_toggle = page.locator(
        '[data-stp-action="toggle-subcategories"][data-category="Food"]'
    ).first
    category_toggle.click()
    page.wait_for_selector('tr.stp-subcat-row[data-parent="Food"]')
    subcategory_control = page.locator(
        'tr.stp-subcat-row[data-parent="Food"] '
        '[data-stp-action="show-transactions"][data-subcategory="General"]'
    ).first
    _check(
        subcategory_control.count() == 1,
        f"{label}: fetched subcategory markup must expose delegated drill-down controls",
    )
    subcategory_control.click()
    transaction_dialog = page.locator("#stp-txn-modal")
    page.wait_for_selector(
        '#stp-txn-modal-body [data-stp-action="edit-transaction"]'
    )
    dynamic_handler_count = page.locator(
        "#stp-txn-modal-body [onclick], #stp-txn-modal-body [onchange], "
        "#stp-txn-modal-body [oninput], #stp-txn-modal-body [onsubmit]"
    ).count()
    _check(
        transaction_dialog.is_visible()
        and dynamic_handler_count == 0
        and transaction_dialog.get_attribute("style") is None
        and page.locator("#stp-txn-modal-body").get_attribute("style") is None
        and transaction_dialog.evaluate(
            "element => getComputedStyle(element).maxWidth"
        )
        == "560px"
        and page.locator("#stp-txn-modal-body").evaluate(
            "element => getComputedStyle(element).overflowY"
        )
        == "auto",
        f"{label}: fetched transaction markup must remain visible and handler-free",
    )

    transaction_row = page.locator(
        '#stp-txn-modal-body [data-transaction-id="synthetic-4am-personal-food"]'
    )
    transaction_row.click()
    page.wait_for_selector(
        '#stp-txn-modal-body tr.stp-drill-edit-row '
        '[data-stp-change="transaction-category"]'
    )
    edit_row = page.locator(
        '#stp-txn-modal-body tr[data-transaction-id="synthetic-4am-personal-food"]'
    )
    edit_row.locator('[data-stp-change="transaction-category"]').select_option("Food")
    edit_row.locator('[data-stp-field="transaction-subcategory"]').select_option(
        "General"
    )
    edit_row.locator('[data-stp-action="save-transaction"]').click()
    page.wait_for_selector(
        '#stp-txn-modal-body [data-transaction-id="synthetic-4am-personal-food"]'
        '[data-stp-action="edit-transaction"]'
    )
    restored_row = page.locator(
        '#stp-txn-modal-body [data-transaction-id="synthetic-4am-personal-food"]'
    )
    restored_row.click()
    page.wait_for_selector(
        '#stp-txn-modal-body tr.stp-drill-edit-row '
        '[data-stp-action="cancel-transaction"]'
    )
    page.locator(
        '#stp-txn-modal-body [data-stp-action="cancel-transaction"]'
    ).click()
    _check(
        page.locator(
            '#stp-txn-modal-body [data-transaction-id="synthetic-4am-personal-food"]'
            '[data-stp-action="edit-transaction"]'
        ).count()
        == 1,
        f"{label}: delegated transaction cancel must restore the response row",
    )
    with page.expect_navigation(wait_until="networkidle"):
        transaction_dialog.locator('[data-stp-action="close-dialog"]').click()

    page.locator(
        '[data-app-shell-action="open-ai-chat"][data-ai-page="short-term-planning"]'
    ).first.click()
    _check(
        page.locator("#ai-chat-scrim").is_visible()
        and page.locator("#ai-chat-page").input_value() == "short-term-planning",
        f"{label}: Short-Term Planning AI entry must use the maintained app-shell action",
    )
    page.locator("[data-ai-chat-close]").click()

    page.context.add_cookies(
        [{"name": "entity", "value": "BFM", "url": base_url}]
    )
    page.goto(
        f"{base_url}/planning/short-term/?month={current_month}",
        wait_until="networkidle",
    )
    _check(
        page.locator(".stp-goal-card", has_text="4AM BFM Goal").count() == 1,
        f"{label}: BFM Short-Term Planning must remain available and isolated",
    )

    page.context.add_cookies(
        [{"name": "entity", "value": "LL", "url": base_url}]
    )
    page.goto(
        f"{base_url}/planning/short-term/?month={current_month}",
        wait_until="networkidle",
    )
    _check(
        page.url.rstrip("/") == base_url
        and page.locator(".stp-goal-card").count() == 0,
        f"{label}: Luxe Legacy must remain denied before Short-Term Planning execution",
    )
    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(base_url, wait_until="networkidle")


def _assert_planning_style_responsive(page, base_url: str, label: str) -> None:
    current_month = date.today().strftime("%Y-%m")
    route_contracts = (
        ("/cashflow/", "[data-cashflow-controller]"),
        ("/planning/", "[data-planning-controller]"),
        (
            f"/planning/short-term/?month={current_month}",
            "[data-short-term-planning-controller]",
        ),
    )
    viewports = (
        ("phone", 390, 844),
        ("exact-768", 768, 900),
        ("desktop", 1280, 900),
    )

    for entity_name in ("Personal", "BFM"):
        page.context.add_cookies(
            [{"name": "entity", "value": entity_name, "url": base_url}]
        )
        for viewport_name, width, height in viewports:
            page.set_viewport_size({"width": width, "height": height})
            for route, controller_selector in route_contracts:
                page.goto(f"{base_url}{route}", wait_until="networkidle")
                page.wait_for_function(
                    "(selector) => document.querySelector(selector)?.dataset.initialized === 'true'",
                    arg=controller_selector,
                )
                responsive_state = page.evaluate(
                    """() => ({
                        styleAttrs: document.querySelectorAll(
                            "#main-content [style]"
                        ).length,
                        bodyOverflow: document.documentElement.scrollWidth
                            > document.documentElement.clientWidth + 1,
                        mainVisible: Boolean(
                            document.getElementById("main-content")
                                ?.getClientRects().length
                        ),
                    })"""
                )
                _check(
                    responsive_state["styleAttrs"] == 0
                    and not responsive_state["bodyOverflow"]
                    and responsive_state["mainVisible"],
                    f"{label}: {entity_name} {route} must preserve a style-attribute-free non-overflowing {viewport_name} layout",
                )

    page.set_viewport_size({"width": 390, "height": 844})
    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(base_url, wait_until="networkidle")


def _assert_weekly_waterfall_pages(page, base_url: str, label: str) -> None:
    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(f"{base_url}/weekly/", wait_until="networkidle")
    weekly_ai = page.locator(
        '[data-app-shell-action="open-ai-chat"][data-ai-page="weekly"]'
    )
    _check(
        weekly_ai.count() == 1,
        f"{label}: Weekly must expose the maintained app-shell AI action",
    )
    weekly_ai.click()
    _check(
        page.locator("#ai-chat-scrim").is_visible()
        and page.locator("#ai-chat-page").input_value() == "weekly",
        f"{label}: Weekly AI entry must preserve its page context",
    )
    page.locator("[data-ai-chat-close]").click()

    page.goto(f"{base_url}/waterfall/", wait_until="networkidle")
    _check(
        page.locator("[data-waterfall-controller]").count() == 1
        and page.locator('script[src*="waterfall.js"]').count() == 1,
        f"{label}: Waterfall must load one page-owned controller",
    )
    waterfall_ai = page.locator(
        '[data-app-shell-action="open-ai-chat"][data-ai-page="waterfall"]'
    )
    waterfall_ai.click()
    _check(
        page.locator("#ai-chat-scrim").is_visible()
        and page.locator("#ai-chat-page").input_value() == "waterfall",
        f"{label}: Waterfall AI entry must preserve its page context",
    )
    page.locator("[data-ai-chat-close]").click()

    actual_view = page.locator("#wf-view-actual")
    target_view = page.locator("#wf-view-target")
    _check(
        actual_view.is_visible() and target_view.is_hidden(),
        f"{label}: Waterfall must start on the actual view without target params",
    )
    actual_bar = actual_view.locator(".wf-wf-bar-anim").first
    actual_bar_state = actual_bar.evaluate(
        """element => ({
            noStyle: !element.hasAttribute("style"),
            geometry: element.getAnimations().some((animation) => {
                const frames = animation.effect.getKeyframes();
                return frames.some(
                    (frame) => frame.left === `${element.dataset.barLeft}%`
                        && frame.width === `${element.dataset.barWidth}%`
                );
            }),
            entrance: element.getAnimations().some((animation) => {
                const frames = animation.effect.getKeyframes();
                return animation.effect.getTiming().duration === 500
                    && frames.some(
                        (frame) => typeof frame.clipPath === "string"
                            && frame.clipPath.includes("100%")
                    );
            }),
        })"""
    )
    _check(
        actual_bar.count() == 1
        and actual_bar_state
        == {"noStyle": True, "geometry": True, "entrance": True},
        f"{label}: actual-view bars must preserve exact geometry and entrance motion without style attributes",
    )

    page.locator(
        '[data-waterfall-action="toggle-breakdown"][data-section="details"]'
    ).click()
    _check(
        page.locator("#wf-detail-details").is_visible()
        and page.locator("#wf-chevron-details").evaluate(
            "element => element.classList.contains('wf-chevron--open')"
        ),
        f"{label}: delegated breakdown control must open details",
    )
    page.locator(
        '[data-waterfall-action="toggle-breakdown"][data-section="fixed"]'
    ).click()
    _check(
        page.locator("#wf-detail-fixed").evaluate("element => !element.hidden"),
        f"{label}: nested breakdown controls must remain interactive",
    )

    tooltip_row = actual_view.locator(".wf-wf-row[data-tip]").first
    tooltip_row.click(position={"x": 24, "y": 20})
    tooltip_state = page.locator("#wf-tip").evaluate(
        """element => {
            const rect = element.getBoundingClientRect();
            return {
                noStyle: !element.hasAttribute("style"),
                positioned: element.getAnimations().some((animation) =>
                    animation.effect.getKeyframes().some(
                        (frame) => typeof frame.left === "string"
                            && typeof frame.top === "string"
                    )
                ),
                insideViewport: rect.left >= 7
                    && rect.top >= 7
                    && rect.right <= window.innerWidth - 7
                    && rect.bottom <= window.innerHeight - 7,
            };
        }"""
    )
    _check(
        page.locator("#wf-tip").is_visible()
        and page.locator("#wf-tip .wf-tip-row").count() >= 1
        and tooltip_state
        == {"noStyle": True, "positioned": True, "insideViewport": True},
        f"{label}: delegated Waterfall row click must show a bounded measured tooltip without style attributes",
    )
    tooltip_row.click(position={"x": 24, "y": 20})
    _check(
        page.locator("#wf-tip").is_hidden(),
        f"{label}: clicking the active Waterfall row must toggle its tooltip off",
    )
    tooltip_row.click(position={"x": 24, "y": 20})
    page.locator(".page-title-row h1").click()
    _check(
        page.locator("#wf-tip").is_hidden(),
        f"{label}: outside click must close the Waterfall tooltip",
    )

    page.locator(
        '[data-waterfall-action="switch-view"][data-view="target"]'
    ).click()
    _check(
        actual_view.is_hidden()
        and target_view.is_visible()
        and page.locator("#wf-seg-target").evaluate(
            "element => element.classList.contains('wf-seg-btn--active')"
        ),
        f"{label}: delegated target-view switching must preserve active state",
    )
    target_bar = target_view.locator(".wf-wf-bar-anim").first
    target_bar_state = target_bar.evaluate(
        """element => ({
            noStyle: !element.hasAttribute("style"),
            geometry: element.getAnimations().some((animation) => {
                const frames = animation.effect.getKeyframes();
                return frames.some(
                    (frame) => frame.left === `${element.dataset.barLeft}%`
                        && frame.width === `${element.dataset.barWidth}%`
                );
            }),
            delay: element.getAnimations().some((animation) =>
                animation.effect.getTiming().duration === 500
                    && animation.effect.getTiming().delay
                        === Number.parseInt(element.dataset.delay || "0", 10) * 150
            ),
        })"""
    )
    _check(
        target_bar.count() == 1
        and target_bar_state
        == {"noStyle": True, "geometry": True, "delay": True},
        f"{label}: newly visible target bars must preserve geometry and staggered motion without style attributes",
    )

    takehome_mode = page.locator(
        '[data-waterfall-action="set-mode"][data-mode="takehome"]'
    )
    takehome_mode.click()
    target_input = page.locator("#wf-input-value")
    _check(
        takehome_mode.evaluate(
            "element => element.classList.contains('wf-seg-btn--active')"
        )
        and target_input.input_value() == ""
        and target_input.evaluate("element => document.activeElement === element"),
        f"{label}: delegated mode switching must clear and focus the target input",
    )
    target_input.fill("12,345")
    with page.expect_navigation(wait_until="networkidle"):
        target_input.press("Enter")
    _check(
        "take_home=12345" in page.url
        and "mode=takehome" in page.url
        and page.locator("#wf-view-target").is_visible(),
        f"{label}: target Enter handling must preserve take-home URL semantics",
    )

    tax_input = page.locator("#wf-tax-rate")
    tax_input.fill("23.5")
    with page.expect_navigation(wait_until="networkidle"):
        tax_input.press("Enter")
    _check(
        "tax_rate=23.5" in page.url
        and page.locator("#wf-view-target").is_visible(),
        f"{label}: tax Enter handling must preserve normalized-route URL semantics",
    )

    page.context.add_cookies(
        [{"name": "entity", "value": "BFM", "url": base_url}]
    )
    page.goto(f"{base_url}/waterfall/", wait_until="networkidle")
    _check(
        page.locator("[data-waterfall-controller]").count() == 1,
        f"{label}: BFM Waterfall must remain available",
    )

    page.context.add_cookies(
        [{"name": "entity", "value": "LL", "url": base_url}]
    )
    page.goto(f"{base_url}/weekly/", wait_until="networkidle")
    _check(
        page.url.rstrip("/") == base_url
        and page.locator("[data-ai-page='weekly']").count() == 0,
        f"{label}: Luxe Legacy must remain denied before Weekly execution",
    )
    page.goto(f"{base_url}/waterfall/", wait_until="networkidle")
    _check(
        page.url.rstrip("/") == base_url
        and page.locator("[data-waterfall-controller]").count() == 0,
        f"{label}: Luxe Legacy must remain denied before Waterfall execution",
    )

    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(base_url, wait_until="networkidle")


def _assert_weekly_waterfall_style_responsive(
    page, base_url: str, label: str
) -> None:
    route_contracts = (
        ("/weekly/", False),
        ("/waterfall/", True),
    )
    viewports = (
        ("phone", 390, 844),
        ("exact-768", 768, 900),
        ("desktop", 1280, 900),
    )

    for entity_name in ("Personal", "BFM"):
        page.context.add_cookies(
            [{"name": "entity", "value": entity_name, "url": base_url}]
        )
        for viewport_name, width, height in viewports:
            page.set_viewport_size({"width": width, "height": height})
            for route, is_waterfall in route_contracts:
                page.goto(f"{base_url}{route}", wait_until="networkidle")
                if is_waterfall:
                    page.wait_for_function(
                        "document.querySelector('[data-waterfall-controller]')"
                        "?.dataset.initialized === 'true'"
                    )
                responsive_state = page.evaluate(
                    """(isWaterfall) => {
                        const geometryBars = Array.from(
                            document.querySelectorAll(
                                "#wf-view-actual .wf-wf-bar"
                                + "[data-bar-left][data-bar-width]"
                            )
                        );
                        return {
                            styleAttrs: document.querySelectorAll(
                                "#main-content [style]"
                            ).length,
                            bodyOverflow: document.documentElement.scrollWidth
                                > document.documentElement.clientWidth + 1,
                            mainVisible: Boolean(
                                document.getElementById("main-content")
                                    ?.getClientRects().length
                            ),
                            boundedBars: document.querySelectorAll(
                                ".wk-cc-bar.u-width-pct[class*='u-pct-'], "
                                + ".wk-cc-progress.u-width-pct[class*='u-pct-'], "
                                + ".wk-cat-bar.u-width-pct[class*='u-pct-'], "
                                + ".chart-fill.u-height-pct[class*='u-pct-']"
                            ).length,
                            geometryBars: geometryBars.length,
                            geometryReady: !isWaterfall || (
                                geometryBars.length > 0
                                && geometryBars.every(
                                    (bar) => {
                                        const trackRect = bar.parentElement
                                            .getBoundingClientRect();
                                        const barRect = bar.getBoundingClientRect();
                                        const expectedLeft = trackRect.width
                                            * Number.parseFloat(
                                                bar.dataset.barLeft
                                            ) / 100;
                                        const expectedWidth = trackRect.width
                                            * Number.parseFloat(
                                                bar.dataset.barWidth
                                            ) / 100;
                                        return !bar.hasAttribute("style")
                                            && Math.abs(
                                                barRect.left
                                                    - trackRect.left
                                                    - expectedLeft
                                            ) <= 1.5
                                            && Math.abs(
                                                barRect.width - expectedWidth
                                            ) <= 1.5;
                                    }
                                )
                            ),
                        };
                    }""",
                    is_waterfall,
                )
                _check(
                    responsive_state["styleAttrs"] == 0
                    and not responsive_state["bodyOverflow"]
                    and responsive_state["mainVisible"]
                    and responsive_state["boundedBars"] > 0
                    and responsive_state["geometryReady"],
                    f"{label}: {entity_name} {route} must preserve bounded bars exact geometry and a style-attribute-free non-overflowing {viewport_name} layout; state={responsive_state}",
                )

    page.context.add_cookies(
        [{"name": "entity", "value": "LL", "url": base_url}]
    )
    for viewport_name, width, height in viewports:
        page.set_viewport_size({"width": width, "height": height})
        for route, _is_waterfall in route_contracts:
            page.goto(f"{base_url}{route}", wait_until="networkidle")
            _check(
                page.url.rstrip("/") == base_url
                and page.locator("[data-waterfall-controller]").count() == 0
                and page.locator("[data-ai-page='weekly']").count() == 0,
                f"{label}: Luxe Legacy {route} must remain denied at {viewport_name}",
            )

    page.set_viewport_size({"width": 390, "height": 844})
    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(base_url, wait_until="networkidle")


def _assert_subscription_page(page, base_url: str, label: str) -> None:
    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(f"{base_url}/subscriptions/", wait_until="networkidle")
    _check(
        page.locator("[data-subscriptions-controller]").count() == 1
        and page.locator('script[src*="subscriptions.js"]').count() == 1,
        f"{label}: subscriptions must load one page-owned controller",
    )

    subscriptions_ai = page.locator(
        '[data-app-shell-action="open-ai-chat"][data-ai-page="subscriptions"]'
    )
    _check(
        subscriptions_ai.count() == 1,
        f"{label}: subscriptions must expose the maintained app-shell AI action",
    )
    subscriptions_ai.click()
    _check(
        page.locator("#ai-chat-scrim").is_visible()
        and page.locator("#ai-chat-page").input_value() == "subscriptions",
        f"{label}: subscriptions AI entry must preserve its page context",
    )
    page.locator("[data-ai-chat-close]").click()

    suggestion_row = page.locator(
        '[data-subscriptions-row][data-subscriptions-action="open-suggestion"]'
    )
    _check(
        suggestion_row.count() == 1,
        f"{label}: synthetic recurring history must render one suggestion",
    )
    suggestion_row.focus()
    suggestion_row.press("Enter")
    _check(
        page.locator("#sub-detail-scrim").is_visible()
        and "4AO Personal Suggestion"
        in page.locator("#sub-detail-title").inner_text()
        and page.locator("#sub-detail-footer form").count() == 2,
        f"{label}: suggestion Enter must open details with both server forms",
    )
    page.locator('[data-subscriptions-action="close-detail"]').click()
    _check(
        page.locator("#sub-detail-scrim").is_hidden(),
        f"{label}: delegated close button must hide suggestion details",
    )
    suggestion_row.focus()
    suggestion_row.press("Space")
    _check(
        page.locator("#sub-detail-scrim").is_visible(),
        f"{label}: suggestion Space must open details",
    )
    page.locator("#sub-detail-scrim").click(position={"x": 2, "y": 2})
    _check(
        page.locator("#sub-detail-scrim").is_hidden(),
        f"{label}: scrim click must close suggestion details",
    )

    add_trigger = page.locator('[data-subscriptions-action="show-add"]')
    add_trigger.click()
    add_name = page.locator('#sub-add-panel input[name="merchant"]')
    _check(
        page.locator("#sub-add-panel").is_visible()
        and add_name.evaluate("element => document.activeElement === element"),
        f"{label}: delegated add control must reveal and focus the form",
    )
    add_name.fill("Synthetic unsaved 4AO")
    page.locator('[data-subscriptions-action="hide-add"]').click()
    _check(
        page.locator("#sub-add-panel").is_hidden()
        and add_name.input_value() == "",
        f"{label}: delegated add cancellation must hide and reset the form",
    )

    dismissed_list = page.locator("#sub-dismissed-list")
    dismissed_trigger = page.locator(
        '[data-subscriptions-action="toggle-dismissed"]'
    )
    _check(
        dismissed_trigger.get_attribute("aria-expanded") == "false",
        f"{label}: dismissed disclosure must begin semantically collapsed",
    )
    dismissed_trigger.click()
    _check(
        dismissed_list.is_visible()
        and "4AO Personal Dismissed" in dismissed_list.inner_text()
        and dismissed_trigger.get_attribute("aria-expanded") == "true"
        and page.locator("#sub-dismissed-chevron").get_attribute("style") is None,
        f"{label}: delegated dismissed control must reveal entity-local rows",
    )
    dismissed_trigger.click()
    _check(
        dismissed_list.is_hidden()
        and dismissed_trigger.get_attribute("aria-expanded") == "false",
        f"{label}: delegated dismissed control must close the list",
    )

    watchlist_row = page.locator(
        '[data-subscriptions-row][data-subscriptions-action="open-watchlist"]'
    )
    _check(
        watchlist_row.count() == 1,
        f"{label}: Personal must render one synthetic watchlist item",
    )
    watchlist_row.click()
    page.wait_for_function(
        "() => document.getElementById('sub-detail-title').textContent.includes('4AO Personal Watchlist')"
    )
    _check(
        page.locator("#sub-detail-scrim").is_visible()
        and "3" in page.locator("#sub-detail-count").inner_text()
        and "4AO Personal Card" in page.locator("#sub-detail-payment").inner_text()
        and page.locator("#sub-detail-charges .sub-detail-charge").count() == 3
        and page.locator("#sub-detail-timeline .sub-detail-timeline-entry").count() >= 1
        and page.locator("#sub-detail-acctinfo-fields .sub-acctinfo-field").count() == 1,
        f"{label}: watchlist detail must render charges payment timeline and account info",
    )

    account_value = page.locator("#sub-acctinfo-value")
    account_value.fill("synthetic-added@example.invalid")
    account_value.press("Enter")
    page.wait_for_function(
        "() => document.querySelectorAll('#sub-detail-acctinfo-fields .sub-acctinfo-field').length === 2"
    )
    account_rows = page.locator(
        "#sub-detail-acctinfo-fields .sub-acctinfo-field"
    )
    _check(
        account_rows.count() == 2
        and "synthetic-added@example.invalid" in account_rows.last.inner_text(),
        f"{label}: account-info Enter must add a synthetic field",
    )
    account_rows.last.locator(
        '[data-subscriptions-action="delete-account-info"]'
    ).click()
    page.wait_for_function(
        "() => document.querySelectorAll('#sub-detail-acctinfo-fields .sub-acctinfo-field').length === 1"
    )

    tips_button = page.locator('[data-subscriptions-action="fetch-tips"]')
    if tips_button.is_visible():
        tips_button.click()
        page.wait_for_function(
            "() => document.getElementById('sub-detail-tips').textContent.includes('Synthetic 4AO cancellation tips')"
        )
    _check(
        "Synthetic 4AO cancellation tips"
        in page.locator("#sub-detail-tips").inner_text()
        and
        page.locator("#sub-tips-fetch-btn").is_hidden(),
        f"{label}: deterministic local tips must persist and hide the fetch control",
    )

    page.evaluate(
        """() => {
            window.__copiedSubscriptionText = '';
            Object.defineProperty(navigator, 'clipboard', {
                configurable: true,
                value: {
                    writeText: async (text) => {
                        window.__copiedSubscriptionText = text;
                    },
                },
            });
        }"""
    )
    page.locator('[data-subscriptions-action="copy-share"]').click()
    page.wait_for_function(
        "() => window.__copiedSubscriptionText.includes('4AO PERSONAL WATCHLIST')"
    )
    _check(
        "synthetic-personal@example.invalid"
        in page.evaluate("window.__copiedSubscriptionText"),
        f"{label}: clipboard action must use the entity-local synthetic share text",
    )
    page.evaluate(
        """() => {
            window.__subscriptionFallback = null;
            navigator.clipboard.writeText = async () => {
                throw new Error("synthetic clipboard rejection");
            };
            document.execCommand = (command) => {
                const proxy = document.querySelector(".u-clipboard-proxy");
                window.__subscriptionFallback = {
                    command,
                    proxyPresent: Boolean(proxy),
                    inlineStyle: proxy?.hasAttribute("style") ?? true,
                    position: proxy ? getComputedStyle(proxy).position : "",
                    opacity: proxy ? getComputedStyle(proxy).opacity : "",
                };
                return true;
            };
        }"""
    )
    page.locator('[data-subscriptions-action="copy-share"]').click()
    page.wait_for_function("() => window.__subscriptionFallback !== null")
    clipboard_fallback = page.evaluate("window.__subscriptionFallback")
    _check(
        clipboard_fallback
        == {
            "command": "copy",
            "proxyPresent": True,
            "inlineStyle": False,
            "position": "fixed",
            "opacity": "0",
        }
        and page.locator(".u-clipboard-proxy").count() == 0,
        f"{label}: clipboard rejection must use and remove the style-attribute-free maintained proxy; state={clipboard_fallback}",
    )

    page.once("dialog", lambda dialog: dialog.dismiss())
    page.locator('[data-subscriptions-action="remove-watchlist"]').click()
    _check(
        page.locator("#sub-detail-scrim").is_visible(),
        f"{label}: dismissed removal confirmation must preserve the current detail",
    )
    page.keyboard.press("Escape")
    _check(
        page.locator("#sub-detail-scrim").is_hidden(),
        f"{label}: Escape must close watchlist details",
    )

    for entity_name, expected_merchant, excluded_merchant in (
        ("BFM", "4AO BFM Watchlist", "4AO Personal Watchlist"),
        ("LL", "4AO LL Watchlist", "4AO BFM Watchlist"),
    ):
        page.context.add_cookies(
            [{"name": "entity", "value": entity_name, "url": base_url}]
        )
        page.goto(f"{base_url}/subscriptions/", wait_until="networkidle")
        page_text = page.locator(".sub-page").inner_text()
        _check(
            expected_merchant in page_text and excluded_merchant not in page_text,
            f"{label}: {entity_name} subscriptions must remain entity-local",
        )

    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(base_url, wait_until="networkidle")


def _assert_payroll_page(page, base_url: str, label: str) -> None:
    from web.routes import payroll as payroll_routes

    page.context.add_cookies(
        [{"name": "entity", "value": "BFM", "url": base_url}]
    )
    page.goto(f"{base_url}/payroll/", wait_until="networkidle")
    page.wait_for_function(
        "document.querySelector('[data-payroll-controller]')"
        "?.dataset.initialized === 'true'"
    )
    _check(
        page.locator("[data-payroll-controller]").count() == 1
        and page.locator('script[src*="payroll.js"]').count() == 1
        and page.locator("#pr-role-classes-data").evaluate(
            "element => element.tagName === 'TEMPLATE'"
        )
        and page.locator("#main-content [style]").count() == 0
        and page.locator(
            "#main-content [onclick], #main-content [onchange], "
            "#main-content [onkeydown], #main-content [hx-on]"
        ).count() == 0,
        f"{label}: BFM payroll must load one handler-free page-owned controller",
    )

    page.locator('[data-payroll-action="show-add"]').click()
    add_name = page.locator('#pr-add-form input[name="name"]')
    _check(
        page.locator("#pr-add-form").is_visible()
        and add_name.evaluate("element => document.activeElement === element"),
        f"{label}: delegated add control must reveal and focus the form",
    )
    add_name.fill("Synthetic unsaved 4AP")
    page.locator('[data-payroll-action="hide-add"]').click()
    _check(
        page.locator("#pr-add-form").is_hidden(),
        f"{label}: delegated add cancellation must hide the form",
    )

    roster_row = page.locator('[data-payroll-action="open-detail"]')
    _check(
        roster_row.count() == 1
        and "4AP BFM Provider" in roster_row.inner_text(),
        f"{label}: BFM payroll must render the synthetic roster row",
    )
    roster_row.focus()
    roster_row.press("Enter")
    page.wait_for_function(
        "() => document.getElementById('pr-detail-name').textContent.includes('4AP BFM Provider')"
    )
    _check(
        page.locator("#pr-detail-scrim").is_visible()
        and "pr-role--providers"
        in page.locator("#pr-detail-role-badge").get_attribute("class")
        and page.locator("#pr-detail-role-badge").get_attribute("style") is None
        and page.locator("#pr-detail-timeline .pr-timeline-item").count() == 1
        and page.locator("#pr-detail-paychecks .pr-paycheck-item").count() == 2
        and page.locator("#pr-edit-form").get_attribute("action").endswith(
            "/payroll/employees/update/1"
        )
        and page.locator("#pr-delete-form").get_attribute("action").endswith(
            "/payroll/employees/delete/1"
        ),
        f"{label}: Enter detail must populate history paychecks and valid edit/delete forms",
    )

    page.once("dialog", lambda dialog: dialog.dismiss())
    page.locator("#pr-delete-btn").click()
    _check(
        page.locator("#pr-detail-scrim").is_visible()
        and page.locator('[data-payroll-action="open-detail"]').count() == 1,
        f"{label}: dismissed deletion confirmation must preserve the employee",
    )
    page.locator(
        '#pr-detail-scrim [data-payroll-action="close-detail"]'
    ).first.click()
    _check(
        page.locator("#pr-detail-scrim").is_hidden(),
        f"{label}: delegated close button must hide payroll detail",
    )

    roster_row.focus()
    roster_row.press("Space")
    page.wait_for_function(
        "() => !document.getElementById('pr-detail-scrim').hidden"
    )
    page.locator("#pr-detail-scrim").click(position={"x": 2, "y": 2})
    _check(
        page.locator("#pr-detail-scrim").is_hidden(),
        f"{label}: scrim click must close payroll detail",
    )
    roster_row.click()
    page.wait_for_function(
        "() => !document.getElementById('pr-detail-scrim').hidden"
    )
    page.keyboard.press("Escape")
    _check(
        page.locator("#pr-detail-scrim").is_hidden(),
        f"{label}: Escape must close payroll detail",
    )

    spending = page.locator("#pr-spending-period")
    spending.select_option("2026-06-15")
    page.wait_for_function(
        "() => document.getElementById('pr-spending-body').textContent.includes('$5,000')"
    )
    _check(
        "4AP BFM Provider" in page.locator("#pr-spending-body").inner_text()
        and page.locator("#pr-spending-body [style]").count() == 0
        and page.locator(
            "#pr-spending-body .pr-spending-bar-fill.u-width-pct[class*='u-pct-']"
        ).count()
        >= 1
        and page.locator(
            "#pr-spending-body .pr-role-badge[class*='pr-role--']"
        ).count()
        >= 1,
        f"{label}: delegated spending-period change must refresh synthetic BFM totals",
    )

    upload = page.locator('input[name="payroll_file"]')
    upload.set_input_files(
        {
            "name": "synthetic-4ap.xlsx",
            "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "buffer": b"synthetic local-only workbook",
        }
    )
    with page.expect_navigation(wait_until="networkidle"):
        page.get_by_role("button", name="Upload & Preview", exact=True).click()
    assignment = page.locator(".pr-select--assign")
    new_role = page.locator(".pr-select--role")
    _check(
        assignment.count() == 1
        and new_role.is_visible()
        and new_role.get_attribute("style") is None
        and "4AP Preview Employee" in page.locator(".pr-import-table").inner_text(),
        f"{label}: synthetic import preview must expose the new-role control",
    )
    assignment.select_option("1")
    _check(
        new_role.is_hidden() and new_role.get_attribute("style") is None,
        f"{label}: selecting an existing employee must hide the new-role control",
    )
    assignment.select_option("new")
    _check(
        new_role.is_visible() and new_role.get_attribute("style") is None,
        f"{label}: selecting new must reveal the new-role control",
    )
    temp_key = page.locator('input[name="temp_key"]').input_value()
    temp_path = Path(payroll_routes._TEMP_DIR) / f"{temp_key}.json"
    _check(temp_path.exists(), f"{label}: preview must create its exact temporary payload")
    with page.expect_navigation(wait_until="networkidle"):
        page.get_by_role("button", name="Cancel", exact=True).last.click()
    _check(
        not temp_path.exists(),
        f"{label}: preview cancellation must remove its exact temporary payload",
    )

    for entity_name in ("Personal", "LL"):
        page.context.add_cookies(
            [{"name": "entity", "value": entity_name, "url": base_url}]
        )
        page.goto(f"{base_url}/payroll/", wait_until="networkidle")
        _check(
            page.url.rstrip("/") == base_url
            and page.locator("[data-payroll-controller]").count() == 0,
            f"{label}: {entity_name} must remain denied before payroll execution",
        )

    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(base_url, wait_until="networkidle")


def _assert_subscriptions_payroll_style_responsive(
    page, base_url: str, label: str
) -> None:
    viewports = (
        ("phone", 390, 844),
        ("exact-768", 768, 900),
        ("desktop", 1280, 900),
    )

    for entity_name in ("Personal", "BFM", "LL"):
        page.context.add_cookies(
            [{"name": "entity", "value": entity_name, "url": base_url}]
        )
        for viewport_name, width, height in viewports:
            page.set_viewport_size({"width": width, "height": height})
            page.goto(f"{base_url}/subscriptions/", wait_until="networkidle")
            subscription_state = page.evaluate(
                """() => ({
                    controller: document.querySelectorAll(
                        "[data-subscriptions-controller]"
                    ).length,
                    styleAttrs: document.querySelectorAll(
                        "#main-content [style]"
                    ).length,
                    bodyOverflow: document.documentElement.scrollWidth
                        > document.documentElement.clientWidth + 1,
                    pageVisible: Boolean(
                        document.querySelector(".sub-page")?.getClientRects().length
                    ),
                    triggerExpanded: document.getElementById(
                        "sub-dismissed-trigger"
                    )?.getAttribute("aria-expanded") ?? null,
                })"""
            )
            _check(
                subscription_state["controller"] == 1
                and subscription_state["styleAttrs"] == 0
                and not subscription_state["bodyOverflow"]
                and subscription_state["pageVisible"]
                and (
                    entity_name != "Personal"
                    or subscription_state["triggerExpanded"] == "false"
                ),
                f"{label}: {entity_name} Subscriptions must remain style-attribute-free and non-overflowing at {viewport_name}; state={subscription_state}",
            )
            if entity_name == "Personal":
                disclosure = page.locator(
                    '[data-subscriptions-action="toggle-dismissed"]'
                )
                disclosure.click()
                disclosure_state = page.evaluate(
                    """() => {
                        const trigger = document.getElementById(
                            "sub-dismissed-trigger"
                        );
                        const chevron = document.getElementById(
                            "sub-dismissed-chevron"
                        );
                        return {
                            expanded: trigger.getAttribute("aria-expanded"),
                            listVisible: !document.getElementById(
                                "sub-dismissed-list"
                            ).hidden,
                            inlineStyle: chevron.hasAttribute("style"),
                            transform: getComputedStyle(chevron).transform,
                        };
                    }"""
                )
                _check(
                    disclosure_state["expanded"] == "true"
                    and disclosure_state["listVisible"]
                    and not disclosure_state["inlineStyle"]
                    and disclosure_state["transform"] != "none",
                    f"{label}: Personal dismissed disclosure must use semantic state and maintained rotation at {viewport_name}; state={disclosure_state}",
                )
                disclosure.click()

    page.context.add_cookies(
        [{"name": "entity", "value": "BFM", "url": base_url}]
    )
    for viewport_name, width, height in viewports:
        page.set_viewport_size({"width": width, "height": height})
        page.goto(f"{base_url}/payroll/", wait_until="networkidle")
        page.wait_for_function(
            "document.querySelector('[data-payroll-controller]')"
            "?.dataset.initialized === 'true'"
        )
        payroll_state = page.evaluate(
            """() => {
                const badges = Array.from(
                    document.querySelectorAll(".pr-role-badge")
                );
                const bars = Array.from(
                    document.querySelectorAll(".pr-spending-bar-fill")
                );
                return {
                    controller: document.querySelectorAll(
                        "[data-payroll-controller]"
                    ).length,
                    styleAttrs: document.querySelectorAll(
                        "#main-content [style]"
                    ).length,
                    bodyOverflow: document.documentElement.scrollWidth
                        > document.documentElement.clientWidth + 1,
                    badges: badges.length,
                    finiteRoleClasses: badges.every(
                        (badge) => Array.from(badge.classList).some(
                            (name) => name.startsWith("pr-role--")
                        )
                    ),
                    boundedBars: bars.length,
                    boundedBarClasses: bars.every(
                        (bar) => bar.classList.contains("u-width-pct")
                            && Array.from(bar.classList).some(
                                (name) => name.startsWith("u-pct-")
                            )
                            && !bar.hasAttribute("style")
                    ),
                };
            }"""
        )
        _check(
            payroll_state["controller"] == 1
            and payroll_state["styleAttrs"] == 0
            and not payroll_state["bodyOverflow"]
            and payroll_state["badges"] > 0
            and payroll_state["finiteRoleClasses"]
            and payroll_state["boundedBars"] > 0
            and payroll_state["boundedBarClasses"],
            f"{label}: BFM Payroll must preserve finite role classes bounded bars and a style-attribute-free non-overflowing {viewport_name} layout; state={payroll_state}",
        )

    for entity_name in ("Personal", "LL"):
        page.context.add_cookies(
            [{"name": "entity", "value": entity_name, "url": base_url}]
        )
        for viewport_name, width, height in viewports:
            page.set_viewport_size({"width": width, "height": height})
            page.goto(f"{base_url}/payroll/", wait_until="networkidle")
            _check(
                page.url.rstrip("/") == base_url
                and page.locator("[data-payroll-controller]").count() == 0,
                f"{label}: {entity_name} Payroll must remain denied before controller execution at {viewport_name}",
            )

    page.set_viewport_size({"width": 390, "height": 844})
    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(base_url, wait_until="networkidle")


def _assert_plaid_entry_pages(page, base_url: str, label: str) -> None:
    from core.db import get_connection
    from web.routes import data_sources as data_sources_routes

    safe_label = "".join(character for character in label if character.isalnum())
    fixture_conn = get_connection("personal")
    try:
        empty_vendor_items = fixture_conn.execute(
            "SELECT pi.item_id FROM plaid_items pi "
            "LEFT JOIN vendor_transactions vt ON vt.plaid_item_id = pi.item_id "
            "WHERE pi.is_vendor = 1 GROUP BY pi.item_id HAVING COUNT(vt.id) = 0"
        ).fetchall()
        for index, row in enumerate(empty_vendor_items):
            fixture_conn.execute(
                "INSERT INTO vendor_transactions "
                "(plaid_item_id, plaid_transaction_id, plaid_account_id, date, "
                "amount, amount_cents, name, merchant_name, recipient, vendor_type, "
                "imported_at) VALUES (?, ?, ?, '2026-07-01', 12.34, 1234, "
                "'Synthetic 4AQ payment', 'Synthetic 4AQ payment', "
                "'Synthetic 4AQ recipient', 'venmo', ?)",
                (
                    row["item_id"],
                    f"4aq-browser-vendor-stat-{index}-{safe_label}",
                    f"4aq-browser-vendor-account-{index}",
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        fixture_conn.commit()
    finally:
        fixture_conn.close()

    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(f"{base_url}/data-sources/", wait_until="networkidle")
    page.wait_for_function(
        "document.querySelector('[data-data-sources-controller]')"
        "?.dataset.initialized === 'true'"
    )
    _check(
        page.locator('script[src*="data-sources.js"]').count() == 1
        and page.locator(
            f'script[src="{PLAID_INITIALIZER_URL}"]'
        ).count() == 1
        and page.locator(
            "#main-content [onclick], #main-content [onchange], "
            "#main-content [onsubmit], #main-content [hx-on]"
        ).count() == 0,
        f"{label}: Data Sources must load one handler-free local controller and exact Plaid initializer",
    )

    vendor_select = page.locator("#vendorSelect")
    vendor_select.select_option("Henry Schein")
    _check(
        page.locator("#fileLabel").text_content()
        == "Henry Schein Items Purchased XLSX",
        f"{label}: delegated vendor selection must update the file label",
    )
    vendor_select.select_option("Amazon")

    amazon_csv = (
        "Order ID,Order Date,Product Name,Item Total,Quantity\n"
        f"4AQ-{safe_label}-1,2026-07-01,Synthetic first item,10.00,1\n"
        f"4AQ-{safe_label}-2,2026-07-02,Synthetic middle item,20.00,1\n"
        f"4AQ-{safe_label}-3,2026-07-03,Synthetic final item,30.00,1\n"
    ).encode()
    page.locator('input[name="file"]').set_input_files(
        {
            "name": f"synthetic-{safe_label}-amazon.csv",
            "mimeType": "text/csv",
            "buffer": amazon_csv,
        }
    )
    with page.expect_navigation(wait_until="networkidle"):
        page.get_by_role("button", name="Upload & Parse", exact=True).click()
    page.wait_for_function(
        "document.querySelector('[data-data-sources-controller]')"
        "?.dataset.initialized === 'true'"
    )
    temp_key = page.locator('input[name="temp_key"]').input_value()
    temp_path = Path(data_sources_routes._TEMP_DIR) / f"{temp_key}.json"
    _check(
        temp_path.exists()
        and page.locator("#ds-order-dates-data").evaluate(
            "element => element.tagName === 'TEMPLATE'"
        ),
        f"{label}: Data Sources preview must use one exact temporary payload and non-script date carrier",
    )
    page.locator("#filterFrom").evaluate(
        """element => {
            element.value = "2026-07-02";
            element.dispatchEvent(new Event("change", {bubbles: true}));
        }"""
    )
    page.locator("#filterTo").evaluate(
        """element => {
            element.value = "2026-07-02";
            element.dispatchEvent(new Event("change", {bubbles: true}));
        }"""
    )
    _check(
        page.locator("#saveBtn").text_content() == "Save 1 orders",
        f"{label}: delegated date filtering must update the preview save count",
    )

    vendor_dialogs: list[str] = []

    def dismiss_vendor_disconnect(dialog) -> None:
        vendor_dialogs.append(dialog.message)
        dialog.dismiss()

    page.once("dialog", dismiss_vendor_disconnect)
    page.locator(
        'form[action*="/data-sources/disconnect-vendor/"] button'
    ).first.click()
    _check(
        vendor_dialogs
        == [
            "Disconnect 4AQ Personal Vendor? "
            "This will remove all synced vendor transactions."
        ],
        f"{label}: Data Sources disconnect confirmation must remain delegated and exact",
    )
    with page.expect_navigation(wait_until="networkidle"):
        page.locator("#saveBtn").click()
    _check(
        not temp_path.exists(),
        f"{label}: saving the preview must consume its exact temporary payload",
    )

    page.wait_for_function(
        "document.querySelector('[data-data-sources-controller]')"
        "?.dataset.initialized === 'true'"
    )
    page.evaluate("window.__plaidStub.mode = 'exit'")
    page.locator("#ds-connect-btn").click()
    page.wait_for_function(
        "() => !document.getElementById('ds-connect-btn').disabled "
        "&& document.getElementById('ds-connect-btn').textContent "
        "=== 'Connect Payment Account'"
    )
    data_source_errors: list[str] = []

    def dismiss_data_source_error(dialog) -> None:
        data_source_errors.append(dialog.message)
        dialog.dismiss()

    page.evaluate("window.__plaidStub.mode = 'throw'")
    page.once("dialog", dismiss_data_source_error)
    page.locator("#ds-connect-btn").click()
    page.wait_for_function(
        "() => !document.getElementById('ds-connect-btn').disabled"
    )
    _check(
        data_source_errors
        == [
            "Failed to start Plaid Link: "
            "Error: synthetic initializer failure"
        ],
        f"{label}: Data Sources initializer failures must alert and reset the button",
    )

    page.evaluate("window.__plaidStub.mode = 'success'")
    with page.expect_navigation(wait_until="networkidle"):
        page.locator("#ds-connect-btn").click()
    _check(
        "Synthetic 4AQ Institution" in page.locator("#main-content").inner_text(),
        f"{label}: mocked vendor Link success must preserve form exchange and reload",
    )

    page.goto(f"{base_url}/plaid/", wait_until="networkidle")
    page.wait_for_function(
        "document.querySelector('[data-plaid-controller]')"
        "?.dataset.initialized === 'true'"
    )
    _check(
        page.locator('script[src*="/static/plaid.js"]').count() == 1
        and page.locator(
            f'script[src="{PLAID_INITIALIZER_URL}"]'
        ).count() == 1
        and page.locator(
            "#main-content [onclick], #main-content [onchange], "
            "#main-content [onsubmit], #main-content [hx-on]"
        ).count() == 0
        and page.locator('[data-plaid-action="connect"]').count() >= 1,
        f"{label}: Connected Accounts must load one handler-free controller exact initializer and delegated Link controls",
    )

    plaid_dialogs: list[str] = []

    def dismiss_plaid_disconnect(dialog) -> None:
        plaid_dialogs.append(dialog.message)
        dialog.dismiss()

    page.once("dialog", dismiss_plaid_disconnect)
    page.locator(
        'form[action$="/plaid/disconnect/4aq-personal-bank-existing"] button'
    ).click()
    _check(
        plaid_dialogs
        == [
            "Disconnect 4AQ Personal Bank? "
            "Imported transactions will be kept."
        ],
        f"{label}: Connected Accounts disconnect confirmation must remain delegated and exact",
    )

    page.evaluate("window.__plaidStub.mode = 'exit'")
    page.locator("#connect-btn").click()
    page.wait_for_function(
        "() => !document.getElementById('connect-btn').disabled "
        "&& document.getElementById('connect-btn').textContent.trim() "
        "=== 'Connect a Bank'"
    )
    plaid_errors: list[str] = []

    def dismiss_plaid_error(dialog) -> None:
        plaid_errors.append(dialog.message)
        dialog.dismiss()

    page.evaluate("window.__plaidStub.mode = 'throw'")
    page.once("dialog", dismiss_plaid_error)
    page.locator("#connect-btn").click()
    page.wait_for_function("() => !document.getElementById('connect-btn').disabled")
    _check(
        plaid_errors
        == [
            "Failed to start Plaid Link: synthetic initializer failure"
        ],
        f"{label}: Connected Accounts initializer failures must alert and reset the button",
    )

    page.evaluate("window.__plaidStub.mode = 'success'")
    with page.expect_navigation(wait_until="networkidle"):
        page.locator("#connect-btn").click()
    _check(
        "Synthetic 4AQ Institution" in page.locator("#main-content").inner_text()
        and "Synthetic 4AQ Checking" in page.locator("#main-content").inner_text(),
        f"{label}: mocked bank Link success must preserve JSON exchange account creation and reload",
    )

    for entity_name in ("BFM", "LL"):
        page.context.add_cookies(
            [{"name": "entity", "value": entity_name, "url": base_url}]
        )
        page.goto(f"{base_url}/plaid/", wait_until="networkidle")
        _check(
            "Synthetic 4AQ Institution"
            not in page.locator("#main-content").inner_text(),
            f"{label}: mocked Personal Link results must not leak into {entity_name}",
        )

    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(base_url, wait_until="networkidle")


def _assert_plaid_entry_style_responsive(
    page, base_url: str, label: str
) -> None:
    from core.db import get_connection

    viewports = (
        ("phone", 390, 844),
        ("exact-768", 768, 900),
        ("desktop", 1280, 900),
    )

    entity_pairs = (
        ("Personal", "personal"),
        ("BFM", "company"),
        ("LL", "luxelegacy"),
    )
    safe_label = "".join(character for character in label if character.isalnum())
    for _entity_name, entity_key in entity_pairs:
        fixture_conn = get_connection(entity_key)
        try:
            empty_vendor_items = fixture_conn.execute(
                "SELECT pi.item_id FROM plaid_items pi "
                "LEFT JOIN vendor_transactions vt ON vt.plaid_item_id = pi.item_id "
                "WHERE pi.is_vendor = 1 GROUP BY pi.item_id HAVING COUNT(vt.id) = 0"
            ).fetchall()
            for index, row in enumerate(empty_vendor_items):
                fixture_conn.execute(
                    "INSERT INTO vendor_transactions "
                    "(plaid_item_id, plaid_transaction_id, plaid_account_id, date, "
                    "amount, amount_cents, name, merchant_name, recipient, vendor_type, "
                    "imported_at) VALUES (?, ?, ?, '2026-07-01', 12.34, 1234, "
                    "'Synthetic 4AY style payment', 'Synthetic 4AY style payment', "
                    "'Synthetic 4AY style recipient', 'venmo', ?)",
                    (
                        row["item_id"],
                        f"4ay-browser-style-{entity_key}-{index}-{safe_label}",
                        f"4ay-browser-style-account-{entity_key}-{index}",
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
            fixture_conn.commit()
        finally:
            fixture_conn.close()

    for entity_name, _entity_key in entity_pairs:
        page.context.add_cookies(
            [{"name": "entity", "value": entity_name, "url": base_url}]
        )
        for viewport_name, width, height in viewports:
            page.set_viewport_size({"width": width, "height": height})
            page.goto(f"{base_url}/data-sources/", wait_until="networkidle")
            data_sources_state = page.evaluate(
                """() => {
                    const vendorRow = document.querySelector(".ds-vendor-row");
                    const vendorActions = document.querySelector(
                        ".ds-vendor-actions"
                    );
                    const inlineForms = Array.from(
                        document.querySelectorAll(".ds-inline-form")
                    );
                    return {
                        controller: document.querySelectorAll(
                            "[data-data-sources-controller]"
                        ).length,
                        styleAttrs: document.querySelectorAll(
                            "#main-content [style]"
                        ).length,
                        bodyOverflow: document.documentElement.scrollWidth
                            > document.documentElement.clientWidth + 1,
                        vendorRows: document.querySelectorAll(
                            ".ds-vendor-row"
                        ).length,
                        vendorDisplay: vendorRow
                            ? getComputedStyle(vendorRow).display
                            : null,
                        vendorActionsDisplay: vendorActions
                            ? getComputedStyle(vendorActions).display
                            : null,
                        inlineForms: inlineForms.length,
                    };
                }"""
            )
            _check(
                data_sources_state["controller"] == 1
                and data_sources_state["styleAttrs"] == 0
                and not data_sources_state["bodyOverflow"]
                and data_sources_state["vendorRows"] > 0
                and data_sources_state["vendorDisplay"] == "flex"
                and data_sources_state["vendorActionsDisplay"] == "flex"
                and data_sources_state["inlineForms"] >= 2,
                f"{label}: {entity_name} Data Sources must preserve semantic vendor layout and remain style-attribute-free and non-overflowing at {viewport_name}; state={data_sources_state}",
            )

            page.goto(f"{base_url}/plaid/", wait_until="networkidle")
            page.wait_for_function(
                "document.querySelector('[data-plaid-controller]')"
                "?.dataset.initialized === 'true'"
            )
            plaid_state = page.evaluate(
                """() => {
                    const toolbar = document.querySelector(".plaid-toolbar");
                    const accountTable = document.querySelector(
                        ".plaid-accounts-table"
                    );
                    const renameForm = document.querySelector(
                        ".plaid-rename-form"
                    );
                    return {
                        controller: document.querySelectorAll(
                            "[data-plaid-controller]"
                        ).length,
                        styleAttrs: document.querySelectorAll(
                            "#main-content [style]"
                        ).length,
                        bodyOverflow: document.documentElement.scrollWidth
                            > document.documentElement.clientWidth + 1,
                        toolbarDisplay: toolbar
                            ? getComputedStyle(toolbar).display
                            : null,
                        tableLayout: accountTable
                            ? getComputedStyle(accountTable).tableLayout
                            : null,
                        renameDisplay: renameForm
                            ? getComputedStyle(renameForm).display
                            : null,
                        initializerCount: document.querySelectorAll(
                            'script[src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"]'
                        ).length,
                    };
                }"""
            )
            _check(
                plaid_state["controller"] == 1
                and plaid_state["styleAttrs"] == 0
                and not plaid_state["bodyOverflow"]
                and plaid_state["toolbarDisplay"] == "flex"
                and plaid_state["tableLayout"] == "fixed"
                and plaid_state["renameDisplay"] == "flex"
                and plaid_state["initializerCount"] == 1,
                f"{label}: {entity_name} Connected Accounts must preserve toolbar table rename and initializer layout while remaining style-attribute-free and non-overflowing at {viewport_name}; state={plaid_state}",
            )

    page.set_viewport_size({"width": 390, "height": 844})
    page.context.add_cookies(
        [{"name": "entity", "value": "Personal", "url": base_url}]
    )
    page.goto(base_url, wait_until="networkidle")


def _register_standalone_test_routes(app) -> None:
    from flask import abort, render_template, render_template_string

    def synthetic_forbidden():
        abort(403)

    def synthetic_not_found():
        abort(404)

    def synthetic_server_error():
        raise RuntimeError("SYNTHETIC_4AR_EXCEPTION_MARKER")

    def synthetic_match_card():
        synthetic_match = {
            "txn_amount": -120.00,
            "order_total": 100.00,
            "txn_date": "2026-07-23",
            "txn_description": "Synthetic browser style match",
            "order_date": "2026-07-15",
            "product_summary": "Synthetic browser order",
            "suggested_category": "Office Supplies",
            "suggested_subcategory": "General",
            "date_gap": 8,
        }
        return render_template_string(
            '{% extends "base.html" %}'
            '{% block content %}{{ synthetic_body|safe }}{% endblock %}',
            synthetic_body=render_template(
                "components/match_card.html",
                review=[synthetic_match, synthetic_match],
                review_idx=1,
                current_match=synthetic_match,
                no_match=[],
                source="orders",
            ),
        )

    def synthetic_vendor_card():
        return render_template_string(
            '{% extends "base.html" %}'
            '{% block content %}{{ synthetic_body|safe }}{% endblock %}',
            synthetic_body=render_template(
                "components/vendor_card.html",
                order={
                    "id": 1,
                    "product_summary": "Synthetic browser vendor card",
                    "order_date": "2026-07-23",
                    "order_total": 42.00,
                },
                total=2,
                initial=5,
                completed=3,
                progress_pct=60,
                categories=["Office Supplies"],
                subcategories=["General"],
                inferred_cat="Office Supplies",
                inferred_sub="General",
            ),
        )

    def synthetic_categorization_pagination():
        return render_template(
            "categorize.html",
            tab="review",
            txns=[
                {
                    "transaction_id": "synthetic-4au-pagination",
                    "date": "2026-07-23",
                    "description_raw": "SYNTHETIC 4AU LOW CONFIDENCE",
                    "amount": -42.00,
                    "category": "Food",
                    "subcategory": "Coffee",
                    "confidence": 0.2,
                    "notes": "",
                }
            ],
            txn_count=51,
            categories=["Food", "Uncategorized"],
            cats=["Food"],
            aliases=[],
            has_suggestions=True,
            page=2,
            total_pages=3,
            page_size=50,
        )

    def synthetic_upload_dialog():
        return render_template(
            "upload_dialog.html",
            item={"id": 1, "label": "Synthetic 4AU import"},
            month="2026-07",
            show_preview=True,
            good_count=1,
            total_txns=2,
            format_month=lambda value: "July 2026",
            previews=[
                {
                    "name": "synthetic-4au.csv",
                    "error": None,
                    "count": 2,
                    "min_date": "2026-07-01",
                    "max_date": "2026-07-02",
                    "credits": 10.00,
                    "debits": 4.00,
                    "net": 6.00,
                    "suggested_name": "Synthetic 4AU",
                }
            ],
        )

    app.add_url_rule(
        "/__synthetic-4ar/403",
        "synthetic_4ar_403",
        synthetic_forbidden,
    )
    app.add_url_rule(
        "/__synthetic-4ar/404",
        "synthetic_4ar_404",
        synthetic_not_found,
    )
    app.add_url_rule(
        "/__synthetic-4ar/500",
        "synthetic_4ar_500",
        synthetic_server_error,
    )
    app.add_url_rule(
        "/__synthetic-4at/match-card",
        "synthetic_4at_match_card",
        synthetic_match_card,
    )
    app.add_url_rule(
        "/__synthetic-4at/vendor-card",
        "synthetic_4at_vendor_card",
        synthetic_vendor_card,
    )
    app.add_url_rule(
        "/__synthetic-4au/categorize-pagination",
        "synthetic_4au_categorize_pagination",
        synthetic_categorization_pagination,
    )
    app.add_url_rule(
        "/__synthetic-4au/upload-dialog",
        "synthetic_4au_upload_dialog",
        synthetic_upload_dialog,
    )
    app.add_url_rule(
        "/favicon.ico",
        "synthetic_4ar_favicon",
        lambda: ("", 204),
    )


def _assert_standalone_documents(
    page,
    base_url: str,
    label: str,
    console_errors: list[str],
) -> None:
    console_error_start = len(console_errors)
    page.goto(base_url, wait_until="networkidle")
    page.evaluate("localStorage.setItem('theme', 'light')")

    offline_response = page.goto(f"{base_url}/offline", wait_until="networkidle")
    _check(
        offline_response is not None and offline_response.status == 200,
        f"{label}: offline document must retain HTTP 200",
    )
    offline_state = page.evaluate(
        """() => ({
            theme: document.documentElement.getAttribute("data-theme"),
            color: document.querySelector('meta[name="theme-color"]').content,
            stylesheetCount: document.querySelectorAll(
                'link[rel="stylesheet"][href$="/static/style.css"]'
            ).length,
            styleBlockCount: document.querySelectorAll("style").length,
            styleAttributeCount: document.querySelectorAll("[style]").length,
            assetCount: document.querySelectorAll(
                'script[src*="standalone-documents.js"]'
            ).length,
            inlineCount: Array.from(document.scripts).filter(
                (script) => !script.src
            ).length,
            retryAction: document.querySelector(".offline-btn").dataset.standaloneAction,
            bodyDisplay: getComputedStyle(document.body).display,
            wrapMaxWidth: getComputedStyle(
                document.querySelector(".offline-wrap")
            ).maxWidth,
        })"""
    )
    _check(
        offline_state
        == {
            "theme": "light",
            "color": "#F7F9FC",
            "stylesheetCount": 1,
            "styleBlockCount": 0,
            "styleAttributeCount": 0,
            "assetCount": 1,
            "inlineCount": 0,
            "retryAction": "retry",
            "bodyDisplay": "flex",
            "wrapMaxWidth": "360px",
        },
        f"{label}: offline document must preserve local CSS layout early theme and delegated retry without inline styles",
    )
    with page.expect_navigation(wait_until="networkidle"):
        page.get_by_role("button", name="Retry", exact=True).click()
    _check(
        page.url == f"{base_url}/offline",
        f"{label}: offline retry must reload the same data-free document",
    )

    for status in (403, 404, 500):
        response = page.goto(
            f"{base_url}/__synthetic-4ar/{status}",
            wait_until="networkidle",
        )
        _check(
            response is not None and response.status == status,
            f"{label}: synthetic {status} document must retain its exact status",
        )
        error_state = page.evaluate(
            """() => ({
                theme: document.documentElement.getAttribute("data-theme"),
                color: document.querySelector('meta[name="theme-color"]').content,
                stylesheetCount: document.querySelectorAll(
                    'link[rel="stylesheet"][href$="/static/style.css"]'
                ).length,
                styleBlockCount: document.querySelectorAll("style").length,
                styleAttributeCount: document.querySelectorAll("[style]").length,
                assetCount: document.querySelectorAll(
                    'script[src*="standalone-documents.js"]'
                ).length,
                inlineCount: Array.from(document.scripts).filter(
                    (script) => !script.src
                ).length,
                body: document.body.innerText,
                bodyDisplay: getComputedStyle(document.body).display,
                wrapMaxWidth: getComputedStyle(
                    document.querySelector(".error-wrap")
                ).maxWidth,
            })"""
        )
        _check(
            error_state["theme"] == "light"
            and error_state["color"] == "#F7F9FC"
            and error_state["stylesheetCount"] == 1
            and error_state["styleBlockCount"] == 0
            and error_state["styleAttributeCount"] == 0
            and error_state["assetCount"] == 1
            and error_state["inlineCount"] == 0,
            f"{label}: {status} document must use local CSS and the early-theme controller without inline styles",
        )
        _check(
            error_state["bodyDisplay"] == "flex"
            and error_state["wrapMaxWidth"] == "360px",
            f"{label}: {status} document must preserve centered responsive layout",
        )
        _check(
            "SYNTHETIC_4AR_EXCEPTION_MARKER" not in error_state["body"],
            f"{label}: {status} document must not leak exception detail",
        )

    focused_response = page.goto(f"{base_url}/k/", wait_until="networkidle")
    _check(
        focused_response is not None and focused_response.status == 200,
        f"{label}: authenticated or no-password /k/ document must render",
    )
    focused_state = page.evaluate(
        """() => ({
            assetCount: document.querySelectorAll('script[src*="kristine.js"]').length,
            inlineCount: Array.from(document.scripts).filter(
                (script) => !script.src
            ).length,
            stylesheetCount: document.querySelectorAll(
                'link[rel="stylesheet"][href*="/static/style.css"]'
            ).length,
            styleBlockCount: document.querySelectorAll("style").length,
            styleAttributeCount: document.querySelectorAll("[style]").length,
            boundedFillCount: document.querySelectorAll(
                '.kd-fill.u-width-pct[class*="u-pct-"]'
            ).length,
            bfmLeak: document.body.innerText.includes("4AL BFM Checking"),
            focusVisible: document.body.innerText.includes("FOCUS SPENDING")
                && document.body.innerText.includes("Food"),
        })"""
    )
    _check(
        focused_state["assetCount"] == 1
        and focused_state["inlineCount"] == 0
        and focused_state["stylesheetCount"] == 1
        and focused_state["styleBlockCount"] == 0
        and focused_state["styleAttributeCount"] == 0
        and focused_state["boundedFillCount"] >= 2
        and not focused_state["bfmLeak"]
        and focused_state["focusVisible"],
        f"{label}: /k/ must use local CSS and bounded bars while preserving Personal plus LL without BFM",
    )

    toggles = page.locator('[data-kristine-action="toggle-category"]')
    _check(
        toggles.count() > 0,
        f"{label}: synthetic /k/ fixture must expose a delegated drill-down control",
    )
    toggle = toggles.first
    drill = toggle.locator(".kd-drill")
    _check(
        drill.count() == 1 and drill.evaluate("element => element.hidden"),
        f"{label}: /k/ drill-down must start closed",
    )
    toggle.click()
    _check(
        not drill.evaluate("element => element.hidden")
        and toggle.evaluate(
            "element => element.classList.contains('kd-cat-row--open')"
        ),
        f"{label}: delegated /k/ click must open the drill-down",
    )
    toggle.click()
    _check(
        drill.evaluate("element => element.hidden"),
        f"{label}: delegated /k/ click must close the drill-down",
    )

    for viewport_width in (768, 1200, 390):
        page.set_viewport_size({"width": viewport_width, "height": 844})
        responsive_state = page.evaluate(
            """() => ({
                styleBlockCount: document.querySelectorAll("style").length,
                styleAttributeCount: document.querySelectorAll("[style]").length,
                wrapWidth: document.querySelector(".kd-wrap").getBoundingClientRect().width,
                viewportWidth: document.documentElement.clientWidth,
                bodyOverflow: document.documentElement.scrollWidth
                    > document.documentElement.clientWidth,
            })"""
        )
        _check(
            responsive_state["styleBlockCount"] == 0
            and responsive_state["styleAttributeCount"] == 0
            and responsive_state["wrapWidth"] <= 480
            and not responsive_state["bodyOverflow"],
            f"{label}: /k/ must preserve zero-inline responsive layout at {viewport_width}px",
        )

    page.evaluate("localStorage.setItem('theme', 'dark')")
    page.goto(base_url, wait_until="networkidle")
    expected_status_errors = sorted(
        [
            "Failed to load resource: the server responded with a status of 403 (FORBIDDEN)",
            "Failed to load resource: the server responded with a status of 404 (NOT FOUND)",
            "Failed to load resource: the server responded with a status of 500 (INTERNAL SERVER ERROR)",
        ]
    )
    observed_status_errors = sorted(console_errors[console_error_start:])
    _check(
        observed_status_errors == expected_status_errors,
        f"{label}: only exact synthetic error-status console entries are expected",
    )
    del console_errors[console_error_start:]


def main() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Playwright is required. Install local test dependencies with "
            "`.venv/bin/pip install -r requirements-dev.txt`."
        ) from exc

    original_environment = os.environ.copy()
    temp_root_path: Path | None = None
    server = None
    server_thread = None
    blocked_urls: list[str] = []
    console_errors: list[str] = []
    page_errors: list[str] = []
    ai_client_module = None
    original_category_suggestion = None
    original_cancellation_tips = None
    payroll_routes_module = None
    original_payroll_parser = None
    plaid_client_module = None
    original_create_link_token = None
    original_exchange_public_token = None
    original_get_accounts = None
    crypto_module = None
    original_encrypt_token = None
    kristine_routes_module = None
    original_start_background_sync = None

    try:
        with tempfile.TemporaryDirectory(prefix="expense_drawer_browser_") as temp_root:
            temp_root_path = Path(temp_root)
            os.environ.update(
                {
                    "DATA_DIR": temp_root,
                    "FLASK_SECRET": "synthetic-mobile-drawer-secret",
                    "APP_PASSWORD_HASH": "",
                    "PLAID_CLIENT_ID": "synthetic-4aq-client",
                    "PLAID_SECRET": "synthetic-4aq-secret",
                    "SYNC_SECRET": "",
                    "OPENROUTER_API_KEY": "",
                    "LUXURY_SUPABASE_URL": "",
                    "LUXURY_SUPABASE_SERVICE_KEY": "",
                    "FLASK_DEBUG": "0",
                }
            )

            from core.db import init_db
            from core import ai_client as ai_client_module
            from core import crypto as crypto_module
            from core import plaid_client as plaid_client_module
            from web import create_app
            from web.routes import kristine as kristine_routes_module
            from web.routes import payroll as payroll_routes_module

            original_category_suggestion = ai_client_module.generate_category_suggestion
            original_cancellation_tips = ai_client_module.generate_cancellation_tips
            original_payroll_parser = payroll_routes_module.parse_phoenix_per_payroll_costs
            original_create_link_token = plaid_client_module.create_link_token
            original_exchange_public_token = (
                plaid_client_module.exchange_public_token
            )
            original_get_accounts = plaid_client_module.get_accounts
            original_encrypt_token = crypto_module.encrypt_token
            original_start_background_sync = (
                kristine_routes_module._start_background_sync
            )
            ai_client_module.generate_category_suggestion = lambda **_kwargs: {
                "category": "Office Supplies",
                "subcategory": "General",
                "reason": "Synthetic local-only browser suggestion",
            }
            ai_client_module.generate_cancellation_tips = (
                lambda _merchant: "Synthetic 4AO cancellation tips. Use the local account portal."
            )
            payroll_routes_module.parse_phoenix_per_payroll_costs = (
                lambda _file: (
                    [
                        {
                            "name": "4AP Preview Employee",
                            "phoenix_job_code": "SYNTHETIC",
                            "paycheck_date": "2026-07-15",
                            "amount": 1234.56,
                        }
                    ],
                    [],
                )
            )
            plaid_exchange_counter = {"value": 0}

            def synthetic_exchange_public_token(_public_token):
                plaid_exchange_counter["value"] += 1
                return {
                    "access_token": (
                        f"synthetic-4aq-access-"
                        f"{plaid_exchange_counter['value']}"
                    ),
                    "item_id": (
                        f"4aq-browser-item-"
                        f"{plaid_exchange_counter['value']}"
                    ),
                }

            plaid_client_module.create_link_token = (
                lambda user_id: f"synthetic-4aq-link-{user_id}"
            )
            plaid_client_module.exchange_public_token = (
                synthetic_exchange_public_token
            )
            plaid_client_module.get_accounts = lambda _access_token: [
                {
                    "account_id": (
                        f"4aq-browser-account-"
                        f"{plaid_exchange_counter['value']}"
                    ),
                    "name": "Synthetic 4AQ Checking",
                    "mask": "4242",
                    "type": "depository",
                    "subtype": "checking",
                    "balance_current": 1234.56,
                    "balance_available": 1200.00,
                    "balance_limit": None,
                }
            ]
            crypto_module.encrypt_token = (
                lambda token: f"synthetic-encrypted-{token}"
            )
            kristine_routes_module._start_background_sync = lambda: False

            for entity_key in ("personal", "company", "luxelegacy"):
                init_db(entity_key)
                _seed_dashboard_data(entity_key)
                _seed_cashflow_planning_data(entity_key)
                _seed_short_term_planning_data(entity_key)
                _seed_subscription_data(entity_key)
                _seed_payroll_data(entity_key)
                _seed_plaid_entry_data(entity_key)

            app = create_app()
            app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)
            app.logger.disabled = True
            _register_standalone_test_routes(app)
            server = make_server(
                "127.0.0.1", 0, app, request_handler=_QuietRequestHandler
            )
            port = server.server_port
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            base_url = f"http://127.0.0.1:{port}"

            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="chrome", headless=True)
                context = browser.new_context(viewport={"width": 390, "height": 844})
                page = context.new_page()

                def route_request(route) -> None:
                    url = route.request.url
                    if url == PLAID_INITIALIZER_URL:
                        route.fulfill(
                            status=200,
                            content_type="application/javascript",
                            body=PLAID_STUB_SOURCE,
                        )
                    elif url.startswith(base_url) or url.startswith("data:"):
                        route.continue_()
                    else:
                        blocked_urls.append(url)
                        route.abort()

                page.route("**/*", route_request)
                page.on(
                    "console",
                    lambda message: console_errors.append(message.text)
                    if message.type == "error"
                    else None,
                )
                page.on("pageerror", lambda error: page_errors.append(str(error)))

                page.goto(base_url, wait_until="networkidle")
                _assert_shared_shell(page, "no-password shell")

                theme_state = page.evaluate(
                    """() => ({
                        theme: document.documentElement.getAttribute('data-theme'),
                        stored: localStorage.getItem('theme'),
                        color: document.querySelector('meta[name="theme-color"]').content,
                        icon: document.querySelector('.theme-toggle-icon').textContent,
                    })"""
                )
                _check(
                    theme_state["theme"] == "dark"
                    and theme_state["color"] == "#000000"
                    and theme_state["icon"] == "☾",
                    "initial theme must reconcile before interaction",
                )
                page.locator('[data-app-shell-action="toggle-theme"]').evaluate("element => element.click()")
                light_state = page.evaluate(
                    """() => ({
                        theme: document.documentElement.getAttribute('data-theme'),
                        stored: localStorage.getItem('theme'),
                        color: document.querySelector('meta[name="theme-color"]').content,
                        icon: document.querySelector('.theme-toggle-icon').textContent,
                    })"""
                )
                _check(
                    light_state == {
                        "theme": "light",
                        "stored": "light",
                        "color": "#F7F9FC",
                        "icon": "☀️",
                    },
                    "theme toggle must reconcile HTML, storage, mobile color, and label",
                )
                page.reload(wait_until="networkidle")
                _assert_shared_shell(page, "persisted no-password shell")
                _check(
                    page.evaluate("document.documentElement.getAttribute('data-theme')") == "light",
                    "early local theme asset must restore the saved theme before app-shell initialization",
                )
                page.locator('[data-app-shell-action="toggle-theme"]').evaluate("element => element.click()")

                csrf_state = page.evaluate(
                    """() => {
                        const token = document.querySelector('meta[name="csrf-token"]').content;
                        const existing = Array.from(document.querySelectorAll('form[method="post"]'));
                        const existingOk = existing.every(
                            (form) => form.querySelector('input[name="_csrf_token"]')?.value === token
                        );
                        const dynamic = document.createElement('form');
                        dynamic.method = 'post';
                        dynamic.id = 'synthetic-dynamic-post';
                        document.body.appendChild(dynamic);
                        dynamic.dispatchEvent(new CustomEvent('htmx:afterSettle', {
                            bubbles: true,
                            detail: {},
                        }));
                        const dynamicToken = dynamic.querySelector('input[name="_csrf_token"]')?.value;
                        const headers = {};
                        dynamic.dispatchEvent(new CustomEvent('htmx:configRequest', {
                            bubbles: true,
                            detail: { headers },
                        }));
                        dynamic.remove();
                        return {
                            existingOk,
                            dynamicOk: dynamicToken === token,
                            headerOk: headers['X-CSRF-Token'] === token,
                        };
                    }"""
                )
                _check(
                    csrf_state == {"existingOk": True, "dynamicOk": True, "headerOk": True},
                    "CSRF inputs and HTMX headers must remain wired for initial and swapped forms",
                )

                page.locator('[data-app-shell-action="open-ai-chat"][data-ai-page="dashboard"]').click()
                ai_open = page.evaluate(
                    """() => ({
                        hidden: document.getElementById('ai-chat-scrim').hidden,
                        page: document.getElementById('ai-chat-page').value,
                        clearValues: document.getElementById('ai-chat-clear-btn').getAttribute('hx-vals'),
                        focused: document.activeElement === document.getElementById('ai-chat-input'),
                        bodyClass: document.body.classList.contains('body-scroll-locked'),
                        inlineStyle: document.body.hasAttribute('style'),
                        overflow: getComputedStyle(document.body).overflow,
                    })"""
                )
                _check(
                    ai_open == {
                        "hidden": False,
                        "page": "dashboard",
                        "clearValues": '{"page":"dashboard"}',
                        "focused": True,
                        "bodyClass": True,
                        "inlineStyle": False,
                        "overflow": "hidden",
                    },
                    "AI modal open behavior must survive handler migration",
                )
                ai_events = page.evaluate(
                    """() => {
                        const form = document.getElementById('ai-chat-form');
                        const thinking = document.getElementById('ai-chat-thinking');
                        form.dispatchEvent(new CustomEvent('htmx:beforeRequest', {
                            bubbles: true,
                            detail: {},
                        }));
                        const beforeVisible = !thinking.hidden;
                        document.getElementById('ai-chat-input').value = 'synthetic';
                        form.dispatchEvent(new CustomEvent('htmx:afterRequest', {
                            bubbles: true,
                            detail: { successful: true },
                        }));
                        return {
                            beforeVisible,
                            afterHidden: thinking.hidden,
                            restoredPage: document.getElementById('ai-chat-page').value,
                            inputCleared: document.getElementById('ai-chat-input').value === '',
                        };
                    }"""
                )
                _check(
                    ai_events == {
                        "beforeVisible": True,
                        "afterHidden": True,
                        "restoredPage": "dashboard",
                        "inputCleared": True,
                    },
                    "AI HTMX lifecycle listeners must preserve thinking and reset behavior",
                )
                page.locator("[data-ai-chat-close]").click()
                _check(
                    page.evaluate(
                        """document.getElementById('ai-chat-scrim').hidden
                        && !document.body.classList.contains('body-scroll-locked')
                        && !document.body.hasAttribute('style')
                        && getComputedStyle(document.body).overflow !== 'hidden'"""
                    ),
                    "AI close control must hide the modal and release body scrolling without runtime styles",
                )

                worker_url = page.evaluate(
                    """async () => {
                        const registration = await navigator.serviceWorker.ready;
                        return registration.active && registration.active.scriptURL;
                    }"""
                )
                _check(worker_url.endswith("/sw.js"), "shared shell must register the same-origin service worker")

                _assert_closed_mobile(page, "initial phone state")

                hamburger = page.locator("#hamburger-btn")
                hamburger.focus()
                page.keyboard.press("Tab")
                _check(
                    not page.evaluate("document.getElementById('sidebar-nav').contains(document.activeElement)"),
                    "closed drawer controls must stay out of the Tab order",
                )
                hamburger.focus()
                hamburger.press("Enter")
                _assert_open_mobile(page, "keyboard open")

                focusable_selector = (
                    "#sidebar-nav a[href], #sidebar-nav button:not([disabled]), "
                    "#sidebar-nav input:not([disabled]), #sidebar-nav select:not([disabled]), "
                    "#sidebar-nav textarea:not([disabled]), "
                    "#sidebar-nav [tabindex]:not([tabindex='-1'])"
                )
                focusable = page.locator(focusable_selector)
                _check(focusable.count() >= 2, "focus trap requires at least two drawer controls")
                focusable.last.focus()
                page.keyboard.press("Tab")
                _check(
                    page.evaluate("document.getElementById('sidebar-nav').contains(document.activeElement)"),
                    "forward Tab must remain inside the open drawer",
                )
                focusable.first.focus()
                page.keyboard.press("Shift+Tab")
                _check(
                    page.evaluate("document.getElementById('sidebar-nav').contains(document.activeElement)"),
                    "reverse Tab must remain inside the open drawer",
                )

                page.keyboard.press("Escape")
                page.wait_for_timeout(350)
                _assert_closed_mobile(page, "Escape close")
                _check(
                    page.evaluate("document.activeElement === document.getElementById('hamburger-btn')"),
                    "Escape close must restore focus to the hamburger",
                )

                hamburger.click()
                _assert_open_mobile(page, "pointer open")
                page.locator("#sidebar-scrim").click(position={"x": 380, "y": 100})
                page.wait_for_timeout(350)
                _assert_closed_mobile(page, "scrim close")
                _check(
                    page.evaluate("document.activeElement === document.getElementById('hamburger-btn')"),
                    "scrim close must restore focus to the hamburger",
                )

                hamburger.click()
                _assert_open_mobile(page, "route open")
                with page.expect_navigation(wait_until="networkidle"):
                    page.locator("#sidebar-nav .sb-nav a[href='/']").click()
                _assert_closed_mobile(page, "route navigation")

                _assert_dashboard_report_fragments(
                    page, base_url, "no-password fragment execution"
                )

                _assert_transaction_modal_fragments(
                    page, base_url, "no-password fragment execution"
                )
                _assert_transaction_matching_styles(
                    page, base_url, "no-password transaction/matching styles"
                )

                page.locator("body").press("/")
                _check(
                    page.evaluate("document.activeElement === document.getElementById('q')"),
                    "migrated keyboard shortcut must focus transaction search after repeated swaps",
                )

                _assert_categorization_upload_pages(
                    page, base_url, "no-password categorization/upload execution"
                )
                _assert_cashflow_planning_pages(
                    page, base_url, "no-password Cash Flow/Planning execution"
                )
                _assert_short_term_planning_page(
                    page, base_url, "no-password Short-Term Planning execution"
                )
                _assert_planning_style_responsive(
                    page, base_url, "no-password planning style compatibility"
                )
                _assert_weekly_waterfall_pages(
                    page, base_url, "no-password Weekly/Waterfall execution"
                )
                _assert_weekly_waterfall_style_responsive(
                    page,
                    base_url,
                    "no-password Weekly/Waterfall style compatibility",
                )
                _assert_subscription_page(
                    page, base_url, "no-password subscription execution"
                )
                _assert_payroll_page(
                    page, base_url, "no-password payroll execution"
                )
                _assert_subscriptions_payroll_style_responsive(
                    page,
                    base_url,
                    "no-password Subscriptions/Payroll style compatibility",
                )
                _assert_plaid_entry_style_responsive(
                    page,
                    base_url,
                    "no-password Plaid entry style compatibility",
                )
                _assert_plaid_entry_pages(
                    page, base_url, "no-password Plaid entry execution"
                )
                _assert_standalone_documents(
                    page,
                    base_url,
                    "no-password standalone execution",
                    console_errors,
                )

                hamburger.click()
                _assert_open_mobile(page, "entity open")
                with page.expect_navigation(wait_until="networkidle"):
                    page.get_by_role("button", name="BFM", exact=True).click()
                _assert_closed_mobile(page, "entity navigation")

                page.set_viewport_size({"width": 768, "height": 844})
                page.wait_for_timeout(50)
                _assert_closed_mobile(page, "exact mobile breakpoint")
                _check(
                    page.locator("[style]").count() == 0
                    and "sidebar--company"
                    in page.locator("#sidebar-nav").get_attribute("class"),
                    "BFM exact-768 shell must preserve entity styling without style attributes",
                )
                hamburger.click()
                _assert_open_mobile(page, "exact mobile breakpoint open")
                page.set_viewport_size({"width": 769, "height": 844})
                page.wait_for_timeout(50)
                desktop_state = _drawer_state(page)
                _check(not desktop_state["open"], "desktop transition must clear transient open class")
                _check(desktop_state["sidebarHidden"] is None, "desktop sidebar must remain exposed")
                _check(not desktop_state["sidebarInert"], "desktop sidebar must not remain inert")
                _check(desktop_state["scrimHidden"], "desktop transition must hide the scrim")
                _check(not desktop_state["bodyLocked"], "desktop transition must release body lock")
                _check(
                    page.locator("[style]").count() == 0,
                    "BFM desktop shell must remain free of style attributes",
                )

                page.set_viewport_size({"width": 390, "height": 844})
                page.wait_for_timeout(50)
                _assert_closed_mobile(page, "return to phone")

                context.add_cookies(
                    [{"name": "entity", "value": "LL", "url": base_url}]
                )
                page.goto(base_url, wait_until="networkidle")
                page.wait_for_selector('#ie-line-chart[data-fragment-initialized="true"] svg')
                _check(
                    page.locator("[style]").count() == 0
                    and "sidebar--luxelegacy"
                    in page.locator("#sidebar-nav").get_attribute("class"),
                    "Luxe Legacy phone shell must preserve entity styling without style attributes",
                )

                _check(not blocked_urls, f"browser attempted external requests: {blocked_urls}")
                _check(not console_errors, f"browser console errors: {console_errors}")
                _check(not page_errors, f"browser page errors: {page_errors}")

                context.close()
                browser.close()

            server.shutdown()
            server_thread.join(timeout=5)
            server.server_close()
            server = None
            server_thread = None

            from werkzeug.security import generate_password_hash

            auth_password = "synthetic-shared-shell-password"
            os.environ["APP_PASSWORD_HASH"] = generate_password_hash(auth_password)
            auth_app = create_app()
            auth_app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)
            auth_app.logger.disabled = True
            _register_standalone_test_routes(auth_app)
            server = make_server(
                "127.0.0.1", 0, auth_app, request_handler=_QuietRequestHandler
            )
            port = server.server_port
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            base_url = f"http://127.0.0.1:{port}"
            auth_blocked_urls: list[str] = []
            auth_console_errors: list[str] = []
            auth_page_errors: list[str] = []

            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="chrome", headless=True)
                context = browser.new_context(viewport={"width": 390, "height": 844})
                page = context.new_page()

                def route_auth_request(route) -> None:
                    url = route.request.url
                    if url == PLAID_INITIALIZER_URL:
                        route.fulfill(
                            status=200,
                            content_type="application/javascript",
                            body=PLAID_STUB_SOURCE,
                        )
                    elif url.startswith(base_url) or url.startswith("data:"):
                        route.continue_()
                    else:
                        auth_blocked_urls.append(url)
                        route.abort()

                page.route("**/*", route_auth_request)
                page.on(
                    "console",
                    lambda message: auth_console_errors.append(message.text)
                    if message.type == "error"
                    else None,
                )
                page.on("pageerror", lambda error: auth_page_errors.append(str(error)))

                page.goto(base_url, wait_until="networkidle")
                _check(
                    "/auth/login" in page.url,
                    "configured-auth shell must redirect to the standalone login first",
                )
                login_style_state = page.evaluate(
                    """() => ({
                        stylesheetCount: document.querySelectorAll(
                            'link[rel="stylesheet"][href$="/static/style.css"]'
                        ).length,
                        styleBlockCount: document.querySelectorAll("style").length,
                        styleAttributeCount: document.querySelectorAll("[style]").length,
                        bodyDisplay: getComputedStyle(document.body).display,
                        cardWidth: document.querySelector(
                            ".standalone-login-card"
                        ).getBoundingClientRect().width,
                        cardMaxWidth: getComputedStyle(
                            document.querySelector(".standalone-login-card")
                        ).maxWidth,
                    })"""
                )
                _check(
                    login_style_state["stylesheetCount"] == 1
                    and login_style_state["styleBlockCount"] == 0
                    and login_style_state["styleAttributeCount"] == 0
                    and login_style_state["bodyDisplay"] == "grid"
                    and login_style_state["cardWidth"] <= 360
                    and login_style_state["cardMaxWidth"] == "360px",
                    "configured-auth login must preserve its local CSS card layout without inline styles",
                )
                page.locator("#password").fill(auth_password)
                with page.expect_navigation(wait_until="networkidle"):
                    page.get_by_role("button", name="Sign in", exact=True).click()

                _check(page.url.rstrip("/") == base_url, "configured-auth login must return to the app shell")
                _assert_shared_shell(page, "configured-auth shell")
                _assert_dashboard_report_fragments(
                    page, base_url, "configured-auth fragment execution"
                )
                _assert_transaction_modal_fragments(
                    page, base_url, "configured-auth fragment execution"
                )
                _assert_transaction_matching_styles(
                    page, base_url, "configured-auth transaction/matching styles"
                )
                _assert_categorization_upload_pages(
                    page, base_url, "configured-auth categorization/upload execution"
                )
                _assert_cashflow_planning_pages(
                    page, base_url, "configured-auth Cash Flow/Planning execution"
                )
                _assert_short_term_planning_page(
                    page, base_url, "configured-auth Short-Term Planning execution"
                )
                _assert_planning_style_responsive(
                    page, base_url, "configured-auth planning style compatibility"
                )
                _assert_weekly_waterfall_pages(
                    page, base_url, "configured-auth Weekly/Waterfall execution"
                )
                _assert_weekly_waterfall_style_responsive(
                    page,
                    base_url,
                    "configured-auth Weekly/Waterfall style compatibility",
                )
                _assert_subscription_page(
                    page, base_url, "configured-auth subscription execution"
                )
                _assert_payroll_page(
                    page, base_url, "configured-auth payroll execution"
                )
                _assert_subscriptions_payroll_style_responsive(
                    page,
                    base_url,
                    "configured-auth Subscriptions/Payroll style compatibility",
                )
                _assert_plaid_entry_style_responsive(
                    page,
                    base_url,
                    "configured-auth Plaid entry style compatibility",
                )
                _assert_plaid_entry_pages(
                    page, base_url, "configured-auth Plaid entry execution"
                )
                _assert_standalone_documents(
                    page,
                    base_url,
                    "configured-auth standalone execution",
                    auth_console_errors,
                )
                _assert_closed_mobile(page, "configured-auth phone state")
                page.locator("#hamburger-btn").click()
                _assert_open_mobile(page, "configured-auth drawer open")
                page.keyboard.press("Escape")
                page.wait_for_timeout(350)
                _assert_closed_mobile(page, "configured-auth drawer close")
                page.locator('[data-app-shell-action="toggle-theme"]').evaluate("element => element.click()")
                _check(
                    page.evaluate("document.documentElement.getAttribute('data-theme')") == "light",
                    "configured-auth shell must retain migrated theme behavior",
                )
                _check(
                    not auth_blocked_urls,
                    f"configured-auth browser attempted external requests: {auth_blocked_urls}",
                )
                _check(
                    not auth_console_errors,
                    f"configured-auth browser console errors: {auth_console_errors}",
                )
                _check(
                    not auth_page_errors,
                    f"configured-auth browser page errors: {auth_page_errors}",
                )

                context.close()
                browser.close()

            server.shutdown()
            server_thread.join(timeout=5)
            server.server_close()
            server = None
            server_thread = None

        _check(temp_root_path is not None and not temp_root_path.exists(), "temporary DATA_DIR cleanup must be exact")
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        if server_thread is not None:
            server_thread.join(timeout=5)
        if ai_client_module is not None and original_category_suggestion is not None:
            ai_client_module.generate_category_suggestion = original_category_suggestion
        if ai_client_module is not None and original_cancellation_tips is not None:
            ai_client_module.generate_cancellation_tips = original_cancellation_tips
        if payroll_routes_module is not None and original_payroll_parser is not None:
            payroll_routes_module.parse_phoenix_per_payroll_costs = original_payroll_parser
        if plaid_client_module is not None and original_create_link_token is not None:
            plaid_client_module.create_link_token = original_create_link_token
        if plaid_client_module is not None and original_exchange_public_token is not None:
            plaid_client_module.exchange_public_token = original_exchange_public_token
        if plaid_client_module is not None and original_get_accounts is not None:
            plaid_client_module.get_accounts = original_get_accounts
        if crypto_module is not None and original_encrypt_token is not None:
            crypto_module.encrypt_token = original_encrypt_token
        if (
            kristine_routes_module is not None
            and original_start_background_sync is not None
        ):
            kristine_routes_module._start_background_sync = (
                original_start_background_sync
            )
        os.environ.clear()
        os.environ.update(original_environment)

    print("Shared shell browser test passed: auth modes, local assets, theme, HTMX, dashboard/report and transaction/modal fragments, categorization/upload, Cash Flow/Long-Term Planning, Short-Term Planning, Weekly/Waterfall, subscription, BFM-only payroll, mocked Plaid entry, and standalone login/offline/error/k execution and style workflows, status-only wording, split and planning CRUD, AI, CSRF, service worker, drawer, swaps, errors, network, and cleanup contracts are intact.")


if __name__ == "__main__":
    main()
