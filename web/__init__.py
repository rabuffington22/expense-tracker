"""Flask app factory for The Ledger."""
from __future__ import annotations

import os
import secrets
import sys
import time
import tempfile
from pathlib import Path

# Load .env from project root if present (works for both gunicorn and dev server)
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# Ensure project root is on sys.path
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from flask import Flask, request, g, redirect, url_for, send_from_directory, render_template, session, abort, flash
from markupsafe import Markup

from core.db import init_db, get_connection
from core.categories import load_categories


# ── Entity helpers ────────────────────────────────────────────────────────────

# Default entity map (production). Override via ENTITIES env var for demo:
#   ENTITIES="Personal:personal,Business:company"
_DEFAULT_ENTITY_MAP = {"Personal": "personal", "BFM": "company", "LL": "luxelegacy"}
_env_entities = os.environ.get("ENTITIES")
if _env_entities:
    _ENTITY_MAP = {}
    for _pair in _env_entities.split(","):
        _display, _, _key = _pair.strip().partition(":")
        _ENTITY_MAP[_display.strip()] = _key.strip()
else:
    _ENTITY_MAP = _DEFAULT_ENTITY_MAP

_ENTITY_COLORS = {
    "Personal": "#003eb6",
    "BFM": "#003eb6",
    "LL": "#003eb6",
    "Business": "#003eb6",
}
_ENTITY_LABELS = {
    "Personal": {"income": "Income",  "spend": "Spending", "net": "Net",    "type": "personal"},
    "BFM":      {"income": "Revenue", "spend": "Expenses", "net": "Profit", "type": "business"},
    "LL":       {"income": "Revenue", "spend": "Expenses", "net": "Profit", "type": "business"},
    "Business": {"income": "Revenue", "spend": "Expenses", "net": "Profit", "type": "business"},
}
_DEFAULT_LABELS = {"income": "Revenue", "spend": "Expenses", "net": "Profit", "type": "business"}


def get_entity():
    """Read entity from cookie, return (display_name, db_key)."""
    _default = next(iter(_ENTITY_MAP))
    choice = request.cookies.get("entity", _default)
    if choice not in _ENTITY_MAP:
        choice = _default
    return choice, _ENTITY_MAP[choice]


def get_accent():
    """Return accent color for the current entity."""
    choice = request.cookies.get("entity", "Personal")
    return _ENTITY_COLORS.get(choice, "#0a84ff")


def get_categories(entity_key):
    """Return sorted list of category names."""
    conn = get_connection(entity_key)
    try:
        rows = conn.execute("SELECT name FROM categories ORDER BY name").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


def get_subcategories(entity_key, category):
    """Return subcategory names for a given category. General first, Unknown last."""
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT name FROM subcategories WHERE category_name = ? ORDER BY name",
            (category,),
        ).fetchall()
        subs = [r[0] for r in rows]
        if "General" not in subs:
            subs.insert(0, "General")
        if "Unknown" not in subs:
            subs.append("Unknown")
        # Move General to top, Unknown to bottom
        ordered = []
        if "General" in subs:
            ordered.append("General")
        ordered.extend(s for s in subs if s not in ("General", "Unknown"))
        if "Unknown" in subs:
            ordered.append("Unknown")
        return ordered
    except Exception:
        return ["General", "Unknown"]
    finally:
        conn.close()


# ── Temp file cleanup ────────────────────────────────────────────────────────

_TEMP_DIR = os.path.join(tempfile.gettempdir(), "expense-tracker-uploads")
_CLEANUP_INTERVAL = 3600  # seconds between cleanup runs
_TEMP_MAX_AGE = 4 * 3600  # delete temp files older than 4 hours
_last_cleanup = 0.0


def _cleanup_temp_files():
    """Remove temp files older than _TEMP_MAX_AGE. Called periodically."""
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < _CLEANUP_INTERVAL:
        return
    _last_cleanup = now
    if not os.path.isdir(_TEMP_DIR):
        return
    cutoff = now - _TEMP_MAX_AGE
    removed = 0
    for name in os.listdir(_TEMP_DIR):
        path = os.path.join(_TEMP_DIR, name)
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)
                removed += 1
        except OSError:
            pass
    if removed:
        import logging
        logging.getLogger(__name__).info(f"Cleaned up {removed} expired temp file(s)")


# ── Sync categories from categories.md ───────────────────────────────────────

_synced_entities: set[str] = set()

# Orphaned categories/subcategories: removed from categories.md but still
# referenced by transactions.  Keyed by entity_key.
_category_orphans: dict[str, list[dict]] = {}


def get_category_orphans(entity_key: str) -> list[dict]:
    """Return list of orphaned categories for the given entity."""
    return _category_orphans.get(entity_key, [])


def clear_category_orphan(entity_key: str, old_category: str, old_subcategory: str | None = None) -> None:
    """Remove a resolved orphan from the in-memory list."""
    orphans = _category_orphans.get(entity_key, [])
    _category_orphans[entity_key] = [
        o for o in orphans
        if not (o["old_category"] == old_category and o.get("old_subcategory") == old_subcategory)
    ]


def sync_categories_from_file(entity_key: str) -> None:
    """Ensure DB categories/subcategories match categories.md.

    Runs once per entity per process lifetime. Adds missing entries and
    collects orphans (categories removed from file but still referenced by
    transactions) for the user to reassign via /categorize/orphans.
    """
    if entity_key in _synced_entities:
        return
    _synced_entities.add(entity_key)

    file_cats = load_categories(entity_key)
    if not file_cats:
        return

    orphans: list[dict] = []

    conn = get_connection(entity_key)
    try:
        # Current DB state
        db_cats = {r[0] for r in conn.execute("SELECT name FROM categories").fetchall()}
        db_subs: dict[str, set[str]] = {}
        for row in conn.execute("SELECT category_name, name FROM subcategories").fetchall():
            db_subs.setdefault(row[0], set()).add(row[1])

        file_cat_names = set(file_cats.keys())

        # INSERT categories in file but not in DB
        for cat in file_cat_names - db_cats:
            conn.execute(
                "INSERT OR IGNORE INTO categories (name, created_at) VALUES (?, datetime('now'))",
                (cat,),
            )

        # INSERT subcategories in file but not in DB
        for cat, subs in file_cats.items():
            existing = db_subs.get(cat, set())
            for sub in subs:
                if sub not in existing:
                    conn.execute(
                        "INSERT OR IGNORE INTO subcategories (category_name, name, created_at) "
                        "VALUES (?, ?, datetime('now'))",
                        (cat, sub),
                    )

        # Handle categories in DB but not in file
        for cat in sorted(db_cats - file_cat_names):
            count = conn.execute(
                "SELECT COUNT(*) FROM transactions WHERE category = ?", (cat,)
            ).fetchone()[0]
            if count > 0:
                orphans.append({
                    "old_category": cat,
                    "old_subcategory": None,
                    "count": count,
                })
            else:
                # Safe to delete — no transactions reference it
                conn.execute("DELETE FROM subcategories WHERE category_name = ?", (cat,))
                conn.execute("DELETE FROM categories WHERE name = ?", (cat,))

        # Handle subcategories in DB but not in file
        for cat, subs in file_cats.items():
            file_subs = set(subs)
            existing = db_subs.get(cat, set())
            for sub in sorted(existing - file_subs):
                count = conn.execute(
                    "SELECT COUNT(*) FROM transactions WHERE category = ? AND subcategory = ?",
                    (cat, sub),
                ).fetchone()[0]
                if count > 0:
                    orphans.append({
                        "old_category": cat,
                        "old_subcategory": sub,
                        "count": count,
                    })
                else:
                    conn.execute(
                        "DELETE FROM subcategories WHERE category_name = ? AND name = ?",
                        (cat, sub),
                    )

        conn.commit()
    finally:
        conn.close()

    if orphans:
        _category_orphans[entity_key] = orphans


# ── App factory ──────────────────────────────────────────────────────────────

def create_app():
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent / "static"),
    )
    _secret = os.environ.get("FLASK_SECRET")
    if not _secret:
        raise RuntimeError(
            "FLASK_SECRET environment variable is required. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    app.secret_key = _secret

    # Validate that hardcoded category references match categories.md
    from core.categories import validate_references
    import logging
    for warning in validate_references():
        logging.getLogger(__name__).warning(warning)
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # 64MB upload limit

    # ── Auth: client-side password gate (see base.html) ─────────────────────
    # HTTP Basic Auth removed — it breaks PWA installs and service workers.
    # Auth is now handled by a client-side SHA-256 hash check in base.html
    # with localStorage persistence (shared across apps on same domain).

    # ── Security headers ─────────────────────────────────────────────────
    @app.after_request
    def _security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if request.is_secure:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    # ── CSRF protection ──────────────────────────────────────────────────
    _CSRF_SAFE_METHODS = frozenset(("GET", "HEAD", "OPTIONS"))
    _CSRF_EXEMPT_PATHS = ("/sw.js", "/offline", "/auth/verify")

    def _get_csrf_token():
        """Return the CSRF token for the current session, creating one if needed."""
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_hex(32)
        return session["_csrf_token"]

    @app.before_request
    def _csrf_protect():
        if app.config.get("TESTING"):
            return
        if request.method in _CSRF_SAFE_METHODS:
            return
        if request.path in _CSRF_EXEMPT_PATHS:
            return
        token = (
            request.form.get("_csrf_token")
            or request.headers.get("X-CSRF-Token")
        )
        if not token or token != session.get("_csrf_token"):
            abort(403)

    app.jinja_env.globals["csrf_token"] = _get_csrf_token

    # ── Server-side auth ─────────────────────────────────────────────────
    _AUTH_HASH = os.environ.get("APP_PASSWORD_HASH", "").lower().strip()
    _AUTH_EXEMPT = frozenset(("/sw.js", "/offline", "/health", "/auth/verify"))

    @app.route("/auth/verify", methods=["POST"])
    def _auth_verify():
        """Verify password hash from client-side auth overlay."""
        from flask import jsonify as _jsonify
        submitted = (request.get_json(silent=True) or {}).get("hash", "")
        if not _AUTH_HASH:
            # No password configured (demo mode) — auto-authenticate
            session["authenticated"] = True
            return _jsonify({"ok": True})
        if submitted.lower().strip() == _AUTH_HASH:
            session["authenticated"] = True
            return _jsonify({"ok": True})
        return _jsonify({"ok": False, "error": "Invalid password"}), 401

    @app.before_request
    def _check_auth():
        if not _AUTH_HASH:
            return  # No password configured (demo mode) — skip auth
        if request.path in _AUTH_EXEMPT:
            return
        if request.path.startswith("/k/") or request.path == "/k":
            return  # Kristine's page — public
        if request.path.startswith("/static/"):
            return  # Static assets — always accessible
        if session.get("authenticated"):
            return
        # For HTMX/fetch requests, return 401 so the client can show the overlay
        if request.headers.get("HX-Request") or request.is_json:
            abort(401)
        # For full page requests, the client-side overlay handles the UI —
        # but we still return the page so the overlay JS can run
        return

    # ── Before-request: init DB, set entity context ──────────────────────────
    @app.before_request
    def _setup_entity():
        if request.path.startswith("/k/") or request.path == "/k" or request.path in ("/sw.js", "/offline", "/health"):
            return  # Kristine's page, SW, offline, health — manage own context
        g.entity_display, g.entity_key = get_entity()
        g.accent = get_accent()
        init_db(g.entity_key)
        sync_categories_from_file(g.entity_key)

        # Flash orphan warning once per session per entity
        orphans = get_category_orphans(g.entity_key)
        orphan_key = f"orphan_warning_{g.entity_key}"
        if orphans and not session.get(orphan_key):
            n = len(orphans)
            word = "category" if n == 1 else "categories"
            link = '<a href="/categorize/orphans">Reassign them</a>'
            flash(
                Markup(f"{n} {word} removed from categories.md still have transactions. {link}."),
                "warning",
            )
            session[orphan_key] = True

        _cleanup_temp_files()

    # ── Template context ─────────────────────────────────────────────────────
    @app.context_processor
    def _inject_globals():
        if request.path.startswith("/k/") or request.path == "/k" or request.path in ("/sw.js", "/offline", "/health"):
            return {}  # These pages don't use entity context
        labels = _ENTITY_LABELS.get(g.entity_display, _DEFAULT_LABELS)
        return {
            "entity_display": g.entity_display,
            "entity_key": g.entity_key,
            "accent": g.accent,
            "entities": list(_ENTITY_MAP.keys()),
            "entity_type": labels["type"],
            "entity_labels": labels,
        }

    # ── Entity toggle route ──────────────────────────────────────────────────
    @app.route("/set-entity", methods=["POST"])
    def set_entity():
        choice = request.form.get("entity", "Personal")
        redirect_to = request.form.get("redirect", "/")
        # Prevent open redirect — only allow relative paths
        if not redirect_to.startswith("/") or redirect_to.startswith("//"):
            redirect_to = "/"
        resp = redirect(redirect_to)
        resp.set_cookie("entity", choice, max_age=365 * 24 * 3600, samesite="Lax")
        return resp

    # ── Jinja globals ────────────────────────────────────────────────────────
    from web.routes.reports import fmt_date, fmt_month_short, fmt_month_full

    def fmt_cents(cents):
        """Format integer cents as dollar string. -8943 → '−$89.43'"""
        if cents is None:
            return "$0.00"
        cents = int(cents)
        sign = "\u2212" if cents < 0 else ""
        return f"{sign}${abs(cents) / 100:,.2f}"

    def fmt_dollars(cents):
        """Format integer cents as whole-dollar string. -8943 → '−$89'"""
        if cents is None:
            return "$0"
        cents = int(cents)
        rounded = round(cents / 100)
        sign = "\u2212" if rounded < 0 else ""
        return f"{sign}${abs(rounded):,.0f}"

    def fmt_due_date(date_str):
        """Format YYYY-MM-DD as 'Apr 15' or 'Apr 15, 2025' if not current year."""
        try:
            from datetime import datetime
            d = datetime.strptime(date_str, "%Y-%m-%d")
            if d.year == datetime.now().year:
                return d.strftime("%b %-d")
            return d.strftime("%b %-d, %Y")
        except (ValueError, TypeError):
            return date_str or ""

    app.jinja_env.globals["fmt_date"] = fmt_date
    app.jinja_env.globals["fmt_month_short"] = fmt_month_short
    app.jinja_env.globals["fmt_month_full"] = fmt_month_full
    app.jinja_env.globals["fmt_cents"] = fmt_cents
    app.jinja_env.globals["fmt_dollars"] = fmt_dollars
    app.jinja_env.globals["fmt_due_date"] = fmt_due_date
    app.jinja_env.globals["cache_bust"] = str(int(time.time()))
    app.jinja_env.globals["get_subcategories"] = get_subcategories

    # ── Register blueprints ──────────────────────────────────────────────────
    from web.routes.dashboard import bp as dashboard_bp
    from web.routes.upload import bp as upload_bp
    from web.routes.data_sources import bp as data_sources_bp
    from web.routes.categorize_vendors import bp as cat_vendors_bp
    from web.routes.match import bp as match_bp
    from web.routes.categorize import bp as categorize_bp
    from web.routes.reports import bp as reports_bp
    from web.routes.plaid import bp as plaid_bp
    from web.routes.transactions import bp as transactions_bp
    from web.routes.saved_views import bp as saved_views_bp
    from web.routes.todo import bp as todo_bp
    from web.routes.cashflow import bp as cashflow_bp
    from web.routes.planning import bp as planning_bp
    from web.routes.short_term_planning import bp as short_term_planning_bp
    from web.routes.subscriptions import bp as subscriptions_bp
    from web.routes.ai import bp as ai_bp
    from web.routes.payroll import bp as payroll_bp
    from web.routes.weekly import bp as weekly_bp
    from web.routes.waterfall import bp as waterfall_bp
    from web.routes.kristine import bp as kristine_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(data_sources_bp)
    app.register_blueprint(cat_vendors_bp)
    app.register_blueprint(match_bp)
    app.register_blueprint(categorize_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(plaid_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(saved_views_bp)
    app.register_blueprint(todo_bp)
    app.register_blueprint(cashflow_bp)
    app.register_blueprint(planning_bp)
    app.register_blueprint(short_term_planning_bp)
    app.register_blueprint(subscriptions_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(payroll_bp)
    app.register_blueprint(weekly_bp)
    app.register_blueprint(waterfall_bp)
    app.register_blueprint(kristine_bp)

    # ── Service worker (must be served from root for max scope) ─────────────
    @app.route("/sw.js")
    def service_worker():
        return send_from_directory(
            app.static_folder, "sw.js",
            mimetype="application/javascript",
            max_age=0,  # Always check for SW updates
        )

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    # ── Offline fallback page ─────────────────────────────────────────────────
    @app.route("/offline")
    def offline():
        return render_template("offline.html")

    # ── Error handlers ────────────────────────────────────────────────────
    @app.errorhandler(403)
    def _forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def _not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def _server_error(e):
        return render_template("errors/500.html"), 500

    # ── Legacy redirect: /vendors → /data-sources ──────────────────────────
    @app.route("/vendors")
    @app.route("/vendors/")
    def _legacy_vendors_redirect():
        return redirect(url_for("data_sources.index"), code=301)

    return app
