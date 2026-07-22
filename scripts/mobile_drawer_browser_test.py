#!/usr/bin/env python3
"""Focused isolated-browser regression coverage for the shared app shell.

Uses a temporary synthetic DATA_DIR, the installed Google Chrome channel, and
blocked non-localhost browser requests. No production credentials or data are
required. Covers the mobile drawer plus theme, HTMX configuration and swaps,
AI modal listeners, CSRF wiring, service-worker registration, and configured-
auth/no-password shell loading. Transaction and supporting modal fragment
controls run only against the temporary synthetic databases.
"""

from __future__ import annotations

import os
import sys
import tempfile
import threading
from datetime import date, datetime, timezone
from pathlib import Path

from werkzeug.serving import WSGIRequestHandler, make_server


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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
            await new Promise((resolve) => setTimeout(resolve, 250));
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
                    nativeHandlers: elements.reduce((count, element) => count +
                        Array.from(element.attributes || []).filter(
                            (attribute) => /^on[a-z]/i.test(attribute.name)
                        ).length, 0),
                };
            }"""
        )
        _check(
            fragment_state == {"charts": 1, "scriptElements": 0, "nativeHandlers": 0},
            f"{label} dashboard swap {swap_number}: migrated fragments must reinitialize without script elements or inline execution",
        )

    page.goto(f"{base_url}/reports/", wait_until="networkidle")
    _assert_shared_shell(page, f"{label} reports shell")
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
                nativeHandlers: elements.reduce((count, element) => count +
                    Array.from(element.attributes || []).filter(
                        (attribute) => /^on[a-z]/i.test(attribute.name)
                    ).length, 0),
            };
        }"""
    )
    _check(
        report_state == {"executableScripts": 0, "nativeHandlers": 0},
        f"{label}: repeated report swaps must contain no inline execution",
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
            allowEval: window.htmx.config.allowEval,
            allowScriptTags: window.htmx.config.allowScriptTags,
        })"""
    )
    _check(initial["asset"], f"{label}: transaction fragment controller must load")
    _check(initial["rows"] > 0, f"{label}: synthetic transaction rows must render")
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
                };
            }"""
        )
        _check(
            fragment_state == {
                "targets": 1,
                "scriptElements": 0,
                "nativeHandlers": 0,
                "hxOn": 0,
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

    try:
        with tempfile.TemporaryDirectory(prefix="expense_drawer_browser_") as temp_root:
            temp_root_path = Path(temp_root)
            os.environ.update(
                {
                    "DATA_DIR": temp_root,
                    "FLASK_SECRET": "synthetic-mobile-drawer-secret",
                    "APP_PASSWORD_HASH": "",
                    "PLAID_CLIENT_ID": "",
                    "PLAID_SECRET": "",
                    "SYNC_SECRET": "",
                    "OPENROUTER_API_KEY": "",
                    "LUXURY_SUPABASE_URL": "",
                    "LUXURY_SUPABASE_SERVICE_KEY": "",
                    "FLASK_DEBUG": "0",
                }
            )

            from core.db import init_db
            from core import ai_client as ai_client_module
            from web import create_app

            original_category_suggestion = ai_client_module.generate_category_suggestion
            ai_client_module.generate_category_suggestion = lambda **_kwargs: {
                "category": "Office Supplies",
                "subcategory": "General",
                "reason": "Synthetic local-only browser suggestion",
            }

            for entity_key in ("personal", "company", "luxelegacy"):
                init_db(entity_key)
                _seed_dashboard_data(entity_key)

            app = create_app()
            app.config.update(TESTING=True)
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
                    if url.startswith(base_url) or url.startswith("data:"):
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
                        overflow: document.body.style.overflow,
                    })"""
                )
                _check(
                    ai_open == {
                        "hidden": False,
                        "page": "dashboard",
                        "clearValues": '{"page":"dashboard"}',
                        "focused": True,
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
                        "document.getElementById('ai-chat-scrim').hidden && document.body.style.overflow === ''"
                    ),
                    "AI close control must hide the modal and release body scrolling",
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

                page.locator("body").press("/")
                _check(
                    page.evaluate("document.activeElement === document.getElementById('q')"),
                    "migrated keyboard shortcut must focus transaction search after repeated swaps",
                )

                hamburger.click()
                _assert_open_mobile(page, "entity open")
                with page.expect_navigation(wait_until="networkidle"):
                    page.get_by_role("button", name="BFM", exact=True).click()
                _assert_closed_mobile(page, "entity navigation")

                page.set_viewport_size({"width": 768, "height": 844})
                page.wait_for_timeout(50)
                _assert_closed_mobile(page, "exact mobile breakpoint")
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

                page.set_viewport_size({"width": 390, "height": 844})
                page.wait_for_timeout(50)
                _assert_closed_mobile(page, "return to phone")

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
            auth_app.config.update(TESTING=True)
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
                    if url.startswith(base_url) or url.startswith("data:"):
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
        os.environ.clear()
        os.environ.update(original_environment)

    print("Shared shell browser test passed: auth modes, local assets, theme, HTMX, dashboard/report and transaction/modal fragments, split save/delete, AI, CSRF, service worker, drawer, swaps, errors, network, and cleanup contracts are intact.")


if __name__ == "__main__":
    main()
