"""Flask app factory for Ledger AI."""

import os
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

import base64
from flask import Flask, request, g, redirect, url_for, Response

from core.db import init_db, get_connection


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


# ── App factory ──────────────────────────────────────────────────────────────

def create_app():
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent / "static"),
    )
    app.secret_key = os.environ.get("FLASK_SECRET", "expense-tracker-dev-key")
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # 64MB upload limit

    # ── Before-request: HTTP Basic Auth ─────────────────────────────────────
    _AUTH_USER = os.environ.get("APP_USERNAME", "")
    _AUTH_PASS = os.environ.get("APP_PASSWORD", "")

    @app.before_request
    def _basic_auth():
        if request.path.startswith("/k"):
            return  # Public page — no auth required
        if not _AUTH_USER or not _AUTH_PASS:
            return  # Auth not configured — skip (local dev)
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Basic "):
            try:
                decoded = base64.b64decode(auth[6:]).decode("utf-8")
                username, _, password = decoded.partition(":")
                if username == _AUTH_USER and password == _AUTH_PASS:
                    return  # Authenticated
            except Exception:
                pass
        return Response(
            "Unauthorized",
            401,
            {"WWW-Authenticate": 'Basic realm="Ledger AI"'},
        )

    # ── Before-request: init DB, set entity context ──────────────────────────
    @app.before_request
    def _setup_entity():
        if request.path.startswith("/k"):
            return  # Kristine's page manages its own DB connections
        g.entity_display, g.entity_key = get_entity()
        g.accent = get_accent()
        init_db(g.entity_key)
        _cleanup_temp_files()

    # ── Template context ─────────────────────────────────────────────────────
    @app.context_processor
    def _inject_globals():
        if request.path.startswith("/k"):
            return {}  # Kristine's page doesn't use entity context
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

    # ── Register blueprints ──────────────────────────────────────────────────
    from web.routes.dashboard import bp as dashboard_bp
    from web.routes.upload import bp as upload_bp
    from web.routes.vendors import bp as vendors_bp
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
    from web.routes.kristine import bp as kristine_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(vendors_bp)
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
    app.register_blueprint(kristine_bp)

    return app
