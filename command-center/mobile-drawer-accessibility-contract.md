# Mobile Drawer Accessibility Contract

## Scope

Work block 4AD resolves Task 1P.3 and only the responsive-navigation slice of `P3-3J-C01`. It does not change desktop navigation, authentication, cookies, CSP, service-worker behavior, production dependencies, live systems, or publication state.

## Mobile State

The maintained drawer breakpoint is `max-width: 768px`.

- Closed: the hamburger reports `aria-expanded="false"`, labels its action as `Open navigation`, and controls `sidebar-nav`; the sidebar is `aria-hidden` and `inert`; the scrim is hidden; body scrolling is available.
- Open: the sidebar is exposed and interactive, the hamburger reports `aria-expanded="true"` and `Close navigation`, the scrim is visible, and body overflow is locked.
- Opening focuses the first primary navigation link. Tab and Shift+Tab wrap across the drawer's usable controls while it is open.
- Escape, the scrim, or the hamburger closes the drawer and restores focus to the hamburger.
- Route links and entity-submit controls close without restoring stale focus immediately before navigation.
- Crossing to desktop clears transient drawer and scrim state, releases body scroll, and exposes the persistent desktop sidebar without leaving it inert. Returning to mobile starts closed.

## Maintained Verification

`scripts/mobile_drawer_browser_test.py` uses Playwright with the installed Google Chrome channel. It starts a temporary localhost Flask server with synthetic Personal, BFM, and Luxe Legacy databases; overrides credential-bearing integration variables with empty or fake values; blocks every non-localhost browser request; uses disposable browser state; and removes its temporary `DATA_DIR` exactly.

The script verifies phone width, the exact `768px` mobile boundary, the `769px` desktop transition, closed Tab exclusion, open focus placement and containment, ARIA and inert state, Escape, scrim, scroll lock, route navigation, entity submission, console health, network denial, and cleanup. The regular synthetic smoke suite remains the whole-application regression gate.

Browser test dependencies live in `requirements-dev.txt`; production continues to install only `requirements.txt`.
