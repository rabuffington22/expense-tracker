#!/usr/bin/env python3
"""Focused isolated-browser regression coverage for the shared app shell.

Uses a temporary synthetic DATA_DIR, the installed Google Chrome channel, and
blocked non-localhost browser requests. No production credentials or data are
required. Covers the mobile drawer plus theme, HTMX configuration and swaps,
AI modal listeners, CSRF wiring, service-worker registration, and configured-
auth/no-password shell loading.
"""

from __future__ import annotations

import os
import sys
import tempfile
import threading
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
    _check(state["allowEval"] is True, f"{label}: HTMX eval must remain temporarily enabled")
    _check(state["allowScriptTags"] is True, f"{label}: HTMX swapped scripts must remain temporarily enabled")
    _check(not state["injectedIndicatorStyle"], f"{label}: HTMX indicator style tag must be absent")
    _check(state["hiddenOpacity"] == "0" and state["requestOpacity"] == "1", f"{label}: local indicator CSS must preserve behavior")
    _check(state["shellFunctions"], f"{label}: compatibility globals must remain available")


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
            from web import create_app

            for entity_key in ("personal", "company", "luxelegacy"):
                init_db(entity_key)

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
                page.evaluate("window.toggleTheme()")
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
                page.evaluate("window.toggleTheme()")

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

                page.evaluate("window.aiChatOpen('dashboard')")
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

                page.goto(f"{base_url}/transactions/?start=2025-01-01", wait_until="networkidle")
                _assert_shared_shell(page, "transactions shell")
                filter_button = page.locator("#txn-filter-form button[type='submit']")
                for swap_number in (1, 2):
                    with page.expect_response(
                        lambda response: "/transactions/partial" in response.url
                    ) as response_info:
                        filter_button.click()
                    _check(
                        response_info.value.status == 200,
                        f"HTMX swap {swap_number}: transaction partial must return 200",
                    )
                    page.wait_for_timeout(50)
                    _check(
                        page.locator("#txn-results").count() == 1,
                        f"HTMX swap {swap_number}: transaction results target must remain",
                    )
                    _assert_shared_shell(page, f"HTMX swap {swap_number}")

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
                _assert_closed_mobile(page, "configured-auth phone state")
                page.locator("#hamburger-btn").click()
                _assert_open_mobile(page, "configured-auth drawer open")
                page.keyboard.press("Escape")
                page.wait_for_timeout(350)
                _assert_closed_mobile(page, "configured-auth drawer close")
                page.evaluate("window.toggleTheme()")
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
        os.environ.clear()
        os.environ.update(original_environment)

    print("Shared shell browser test passed: auth modes, local assets, theme, HTMX, AI, CSRF, service worker, drawer, swaps, errors, network, and cleanup contracts are intact.")


if __name__ == "__main__":
    main()
