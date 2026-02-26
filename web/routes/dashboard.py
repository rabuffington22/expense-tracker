"""Dashboard route — quick stats and import status."""

from datetime import datetime

from flask import Blueprint, render_template, g

from core.db import get_connection

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    conn = get_connection(g.entity_key)
    try:
        uncat_count = conn.execute(
            "SELECT COUNT(*) FROM transactions "
            "WHERE category IS NULL OR category = '' OR confidence < 0.6"
        ).fetchone()[0]

        latest_raw = conn.execute("SELECT MAX(date) FROM transactions").fetchone()[0]
        if latest_raw:
            latest_date = datetime.strptime(latest_raw, "%Y-%m-%d").strftime("%b %-d, %Y")
        else:
            latest_date = "\u2014"

        # Import progress — last 3 months
        now = datetime.now()
        y, m = now.year, now.month
        months = []
        for _ in range(3):
            months.append(f"{y:04d}-{m:02d}")
            m -= 1
            if m == 0:
                m = 12
                y -= 1

        all_sources = conn.execute(
            "SELECT id FROM import_checklist WHERE entity=? ORDER BY sort_order, id",
            (g.entity_key,),
        ).fetchall()
        all_sources = [dict(r) for r in all_sources]

        month_progress = []
        if all_sources:
            item_ids = [s["id"] for s in all_sources]
            placeholders = ",".join("?" * len(item_ids))
            total = len(all_sources)
            for mo in months:
                status_rows = conn.execute(
                    f"SELECT checklist_item_id, completed FROM import_checklist_status "
                    f"WHERE month=? AND checklist_item_id IN ({placeholders})",
                    [mo] + item_ids,
                ).fetchall()
                done = sum(1 for r in status_rows if bool(r["completed"]))
                label = datetime.strptime(mo, "%Y-%m").strftime("%b %Y")
                month_progress.append({"label": label, "done": done, "total": total})
    finally:
        conn.close()

    return render_template(
        "dashboard.html",
        uncat_count=uncat_count,
        latest_date=latest_date,
        month_progress=month_progress,
        has_sources=bool(all_sources),
    )
