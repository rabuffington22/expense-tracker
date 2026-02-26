"""Flask app factory for Expense Tracker."""

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

from flask import Flask, request, g, redirect, url_for

from core.db import init_db, get_connection


# ── Entity helpers ────────────────────────────────────────────────────────────

_ENTITY_MAP = {"Personal": "personal", "BFM": "company"}
_ENTITY_COLORS = {
    "Personal": "#30d158",
    "BFM": "#0a84ff",
}


def get_entity():
    """Read entity from cookie, return (display_name, db_key)."""
    choice = request.cookies.get("entity", "Personal")
    if choice not in _ENTITY_MAP:
        choice = "Personal"
    return choice, _ENTITY_MAP[choice]


def get_accent():
    """Return accent color for the current entity."""
    choice = request.cookies.get("entity", "Personal")
    return _ENTITY_COLORS.get(choice, "#30d158")


def get_categories(entity_key):
    """Return sorted list of category names."""
    conn = get_connection(entity_key)
    try:
        rows = conn.execute("SELECT name FROM categories ORDER BY name").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


def get_subcategories(entity_key, category):
    """Return subcategory names for a given category. Always includes 'Unknown'."""
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT name FROM subcategories WHERE category_name = ? ORDER BY name",
            (category,),
        ).fetchall()
        subs = [r[0] for r in rows]
        if "Unknown" not in subs:
            subs.append("Unknown")
        return subs
    except Exception:
        return ["Unknown"]
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

    # ── Before-request: init DB, set entity context ──────────────────────────
    @app.before_request
    def _setup_entity():
        g.entity_display, g.entity_key = get_entity()
        g.accent = get_accent()
        init_db(g.entity_key)
        _cleanup_temp_files()

    # ── Template context ─────────────────────────────────────────────────────
    @app.context_processor
    def _inject_globals():
        return {
            "entity_display": g.entity_display,
            "entity_key": g.entity_key,
            "accent": g.accent,
            "entities": list(_ENTITY_MAP.keys()),
        }

    # ── Entity toggle route ──────────────────────────────────────────────────
    @app.route("/set-entity", methods=["POST"])
    def set_entity():
        choice = request.form.get("entity", "Personal")
        redirect_to = request.form.get("redirect", "/")
        resp = redirect(redirect_to)
        resp.set_cookie("entity", choice, max_age=365 * 24 * 3600, samesite="Lax")
        return resp

    # ── Register blueprints ──────────────────────────────────────────────────
    from web.routes.dashboard import bp as dashboard_bp
    from web.routes.upload import bp as upload_bp
    from web.routes.vendors import bp as vendors_bp
    from web.routes.categorize_vendors import bp as cat_vendors_bp
    from web.routes.match import bp as match_bp
    from web.routes.categorize import bp as categorize_bp
    from web.routes.reports import bp as reports_bp
    from web.routes.plaid import bp as plaid_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(cat_vendors_bp)
    app.register_blueprint(match_bp)
    app.register_blueprint(categorize_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(plaid_bp)

    return app
