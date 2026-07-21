#!/usr/bin/env python3
"""Focused isolated-browser regression coverage for the mobile drawer.

Uses a temporary synthetic DATA_DIR, the installed Google Chrome channel, and
blocked non-localhost browser requests. No production credentials or data are
required.
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

                page.goto(base_url, wait_until="networkidle")
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

    print("Mobile drawer browser test passed: focus, ARIA, scrim, scroll, navigation, breakpoint, network, and cleanup contracts are intact.")


if __name__ == "__main__":
    main()
