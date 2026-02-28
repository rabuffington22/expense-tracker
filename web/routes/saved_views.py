"""Saved Views — bookmark dashboard / transactions filter configurations."""

from datetime import datetime, timezone

from flask import Blueprint, request, g, jsonify

from core.db import get_connection

bp = Blueprint("saved_views", __name__, url_prefix="/saved-views")

_VALID_PAGES = ("dashboard", "transactions")
_MAX_NAME_LEN = 100


def _fetch_views(conn, page):
    """Return all saved views for a page, ordered by name."""
    return conn.execute(
        "SELECT id, name FROM saved_views WHERE page = ? ORDER BY name",
        (page,),
    ).fetchall()


def _views_json(rows):
    """Convert DB rows to a JSON-serialisable list of {id, name} dicts."""
    return [{"id": r["id"], "name": r["name"]} for r in rows]


@bp.route("/list")
def list_views():
    page = request.args.get("page", "")
    if page not in _VALID_PAGES:
        return jsonify({"error": "bad page"}), 400
    conn = get_connection(g.entity_key)
    try:
        rows = _fetch_views(conn, page)
    finally:
        conn.close()
    return jsonify(_views_json(rows))


@bp.route("/create", methods=["POST"])
def create_view():
    name = request.form.get("name", "").strip()
    page = request.form.get("page", "")
    query_string = request.form.get("query_string", "")

    if not name or page not in _VALID_PAGES:
        return jsonify({"error": "bad request"}), 400
    if len(name) > _MAX_NAME_LEN:
        name = name[:_MAX_NAME_LEN]

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO saved_views (name, page, query_string, created_at) "
            "VALUES (?, ?, ?, ?)",
            (name, page, query_string,
             datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        rows = _fetch_views(conn, page)
    finally:
        conn.close()
    return jsonify(_views_json(rows))


@bp.route("/delete", methods=["POST"])
def delete_view():
    view_id = request.form.get("id", "")
    page = request.form.get("page", "")
    if not view_id or page not in _VALID_PAGES:
        return jsonify({"error": "bad request"}), 400
    conn = get_connection(g.entity_key)
    try:
        # Verify the view exists in the current entity's DB before deleting
        row = conn.execute(
            "SELECT id FROM saved_views WHERE id = ?", (int(view_id),)
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        conn.execute("DELETE FROM saved_views WHERE id = ?", (int(view_id),))
        conn.commit()
        rows = _fetch_views(conn, page)
    finally:
        conn.close()
    return jsonify(_views_json(rows))


@bp.route("/rename", methods=["POST"])
def rename_view():
    view_id = request.form.get("id", "")
    new_name = request.form.get("name", "").strip()
    page = request.form.get("page", "")

    if not view_id or page not in _VALID_PAGES:
        return jsonify({"error": "bad request"}), 400
    if not new_name:
        return jsonify({"error": "name is required"}), 400
    if len(new_name) > _MAX_NAME_LEN:
        new_name = new_name[:_MAX_NAME_LEN]

    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT id, name FROM saved_views WHERE id = ?", (int(view_id),)
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        if row["name"] == new_name:
            return jsonify({"error": "name unchanged"}), 400
        conn.execute(
            "UPDATE saved_views SET name = ? WHERE id = ?",
            (new_name, int(view_id)),
        )
        conn.commit()
    finally:
        conn.close()
    return jsonify({"id": int(view_id), "name": new_name, "page": page})


@bp.route("/get")
def get_view():
    view_id = request.args.get("id", "")
    if not view_id:
        return jsonify({"error": "missing id"}), 400
    conn = get_connection(g.entity_key)
    try:
        row = conn.execute(
            "SELECT page, query_string FROM saved_views WHERE id = ?",
            (int(view_id),),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify({"page": row["page"], "query_string": row["query_string"]})
