"""Dashboard route — quick stats and import status."""

from datetime import datetime

from flask import Blueprint, render_template, g

from core.db import get_connection
from core.amazon import get_order_counts

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    conn = get_connection(g.entity_key)
    try:
        # ── Core metrics ──────────────────────────────────────────────────────
        total_txn_count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]

        uncat_count = conn.execute(
            "SELECT COUNT(*) FROM transactions "
            "WHERE category IS NULL OR category = '' OR confidence < 0.6"
        ).fetchone()[0]

        categorized_count = total_txn_count - uncat_count
        cat_pct = int(categorized_count / total_txn_count * 100) if total_txn_count else 0

        # Current month spend (expenses only — negative amounts or positive debits)
        now = datetime.now()
        cur_month = f"{now.year:04d}-{now.month:02d}"
        month_spend_row = conn.execute(
            "SELECT COALESCE(SUM(ABS(amount)), 0) FROM transactions "
            "WHERE strftime('%%Y-%%m', date) = ? AND amount < 0",
            (cur_month,),
        ).fetchone()
        month_spend = month_spend_row[0] if month_spend_row else 0
        # Some profiles negate amounts — also check positive amounts
        if month_spend == 0:
            month_spend_row = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM transactions "
                "WHERE strftime('%%Y-%%m', date) = ? AND amount > 0",
                (cur_month,),
            ).fetchone()
            month_spend = month_spend_row[0] if month_spend_row else 0

        latest_raw = conn.execute("SELECT MAX(date) FROM transactions").fetchone()[0]
        if latest_raw:
            latest_date = datetime.strptime(latest_raw, "%Y-%m-%d").strftime("%b %-d, %Y")
        else:
            latest_date = "\u2014"

        # ── Vendor matching status ────────────────────────────────────────────
        total_orders, unmatched_orders = get_order_counts(g.entity_key)

        # ── Import progress — last 3 months ───────────────────────────────────
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

        # ── Top categories this month ─────────────────────────────────────────
        top_cats_rows = conn.execute(
            "SELECT category, COALESCE(SUM(ABS(amount)), 0) as total "
            "FROM transactions "
            "WHERE strftime('%%Y-%%m', date) = ? "
            "  AND category IS NOT NULL AND category != '' "
            "GROUP BY category ORDER BY total DESC LIMIT 5",
            (cur_month,),
        ).fetchall()
        top_cats = [{"name": r[0], "total": r[1]} for r in top_cats_rows]
    finally:
        conn.close()

    return render_template(
        "dashboard.html",
        total_txn_count=total_txn_count,
        uncat_count=uncat_count,
        categorized_count=categorized_count,
        cat_pct=cat_pct,
        month_spend=month_spend,
        cur_month_label=now.strftime("%b %Y"),
        latest_date=latest_date,
        total_orders=total_orders,
        unmatched_orders=unmatched_orders,
        month_progress=month_progress,
        has_sources=bool(all_sources),
        top_cats=top_cats,
    )
