"""Payroll — employee roster, Phoenix import, role-based spending."""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import date, datetime

from flask import Blueprint, g, redirect, render_template, request, url_for, jsonify
from markupsafe import escape

from core.db import get_connection
from core.payroll_parser import (
    PHOENIX_JOB_CODE_MAP,
    get_unique_employees_from_entries,
    match_to_employees,
    parse_phoenix_per_payroll_costs,
    suggest_role,
)

bp = Blueprint("payroll", __name__, url_prefix="/payroll")

_TEMP_DIR = os.path.join(tempfile.gettempdir(), "expense-tracker-uploads")
os.makedirs(_TEMP_DIR, exist_ok=True)

# ── Role colors for badges ───────────────────────────────────────────────────

ROLE_COLORS: dict[str, str] = {
    "Providers": "#ff453a",
    "Nurses": "#bf5af2",
    "Scribes": "#ff9f0a",
    "Front Office": "#30d158",
    "Office Manager": "#0a84ff",
    "HR": "#5e5ce6",
    "Owner": "#98989d",
}

ROLE_ORDER = ["Providers", "Nurses", "Scribes", "Front Office", "Office Manager", "HR", "Owner"]


def _save_temp(key: str, data: dict) -> None:
    path = os.path.join(_TEMP_DIR, f"{key}.json")
    with open(path, "w") as f:
        json.dump(data, f)


def _load_temp(key: str) -> dict | None:
    path = os.path.join(_TEMP_DIR, f"{key}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    os.remove(path)
    return data


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_employees(conn) -> list[dict]:
    """Get all employees, active first, sorted by role order then name."""
    rows = conn.execute(
        "SELECT * FROM employees ORDER BY "
        "CASE status WHEN 'active' THEN 0 WHEN 'inactive' THEN 1 ELSE 2 END, "
        "name"
    ).fetchall()
    employees = []
    for r in rows:
        emp = dict(r)
        # Get last pay change
        last_change = conn.execute(
            "SELECT * FROM employee_pay_changes "
            "WHERE employee_id = ? ORDER BY effective_date DESC LIMIT 1",
            (r["id"],),
        ).fetchone()
        if last_change:
            emp["last_raise_date"] = last_change["effective_date"]
            try:
                d = datetime.strptime(last_change["effective_date"], "%Y-%m-%d")
                emp["days_since_raise"] = (datetime.now() - d).days
            except (ValueError, TypeError):
                emp["days_since_raise"] = None
        else:
            emp["last_raise_date"] = None
            emp["days_since_raise"] = None
        employees.append(emp)
    return employees


def _get_pay_changes(conn, emp_id: int) -> list[dict]:
    """Get pay change history for an employee, newest first."""
    rows = conn.execute(
        "SELECT * FROM employee_pay_changes "
        "WHERE employee_id = ? ORDER BY effective_date DESC",
        (emp_id,),
    ).fetchall()
    changes = []
    for r in rows:
        c = dict(r)
        if c["old_rate_cents"] and c["old_rate_cents"] > 0:
            c["pct_change"] = round(
                (c["new_rate_cents"] - c["old_rate_cents"]) / c["old_rate_cents"] * 100, 1
            )
        else:
            c["pct_change"] = None
        changes.append(c)
    return changes


def _get_recent_paychecks(conn, emp_id: int, limit: int = 10) -> list[dict]:
    """Get recent payroll entries for an employee."""
    rows = conn.execute(
        "SELECT * FROM payroll_entries "
        "WHERE employee_id = ? ORDER BY paycheck_date DESC LIMIT ?",
        (emp_id, limit),
    ).fetchall()
    return [dict(r) for r in rows]


def _log_pay_change(conn, emp_id: int, old_cents: int, new_cents: int,
                    eff_date: str, notes: str = "") -> None:
    """Record a pay rate change."""
    conn.execute(
        "INSERT INTO employee_pay_changes "
        "(employee_id, effective_date, old_rate_cents, new_rate_cents, notes) "
        "VALUES (?, ?, ?, ?, ?)",
        (emp_id, eff_date, old_cents, new_cents, notes),
    )


def _get_compensation_analysis(conn) -> dict:
    """Compute per-role average pay rates for comparison."""
    rows = conn.execute(
        "SELECT role, pay_type, pay_rate_cents FROM employees WHERE status = 'active'"
    ).fetchall()
    role_rates: dict[str, list[int]] = {}
    for r in rows:
        role = r["role"]
        if role not in role_rates:
            role_rates[role] = []
        role_rates[role].append(r["pay_rate_cents"])
    # Compute averages
    role_avgs: dict[str, int] = {}
    for role, rates in role_rates.items():
        role_avgs[role] = round(sum(rates) / len(rates)) if rates else 0
    return role_avgs


def _get_role_spending(conn, paycheck_date: str) -> list[dict]:
    """Aggregate payroll_entries by employee role for a single pay period.

    Returns list of dicts: {role, total_cents, employees: [{name, total_cents}]}
    """
    rows = conn.execute(
        "SELECT e.role, e.name, SUM(pe.amount_cents) as total_cents "
        "FROM payroll_entries pe "
        "JOIN employees e ON pe.employee_id = e.id "
        "WHERE pe.paycheck_date = ? "
        "GROUP BY e.role, e.name "
        "ORDER BY e.role, total_cents DESC",
        (paycheck_date,),
    ).fetchall()

    role_data: dict[str, dict] = {}
    for r in rows:
        role = r["role"]
        if role not in role_data:
            role_data[role] = {"role": role, "total_cents": 0, "employees": []}
        role_data[role]["total_cents"] += r["total_cents"]
        role_data[role]["employees"].append({
            "name": r["name"],
            "total_cents": r["total_cents"],
        })

    # Sort by role order
    result = []
    for role in ROLE_ORDER:
        if role in role_data:
            result.append(role_data[role])
    # Add any roles not in the predefined order
    for role, data in role_data.items():
        if role not in ROLE_ORDER:
            result.append(data)

    return result


def _get_available_pay_periods(conn) -> list[str]:
    """Get distinct paycheck dates from payroll_entries."""
    rows = conn.execute(
        "SELECT DISTINCT paycheck_date FROM payroll_entries "
        "ORDER BY paycheck_date"
    ).fetchall()
    return [r["paycheck_date"] for r in rows]


# ── Routes ───────────────────────────────────────────────────────────────────

@bp.route("/")
def index():
    """Main payroll page: roster + spending + import."""
    conn = get_connection(g.entity_key)
    try:
        employees = _get_employees(conn)
        role_avgs = _get_compensation_analysis(conn)

        # Spending data — biweekly pay periods
        available_periods = _get_available_pay_periods(conn)
        default_period = available_periods[-1] if available_periods else date.today().strftime("%Y-%m-%d")
        spending_period = request.args.get("spending_period", default_period)
        role_spending = _get_role_spending(conn, spending_period)

        # Grand total for spending bars
        grand_total = sum(rs["total_cents"] for rs in role_spending)

        return render_template(
            "payroll.html",
            employees=employees,
            role_avgs=role_avgs,
            role_spending=role_spending,
            grand_total=grand_total,
            role_colors=ROLE_COLORS,
            role_order=ROLE_ORDER,
            available_periods=available_periods,
            spending_period=spending_period,
        )
    finally:
        conn.close()


@bp.route("/employees/create", methods=["POST"])
def create_employee():
    """Add a new employee."""
    name = request.form.get("name", "").strip()
    role = request.form.get("role", "").strip()
    pay_type = request.form.get("pay_type", "hourly")
    pay_rate = request.form.get("pay_rate", "0").replace(",", "").replace("$", "")
    hire_date = request.form.get("hire_date", "")
    phoenix_job_code = request.form.get("phoenix_job_code", "").strip()
    notes = request.form.get("notes", "").strip()

    if not name or not role:
        return redirect(url_for("payroll.index"))

    try:
        pay_rate_cents = int(round(float(pay_rate) * 100))
    except (ValueError, TypeError):
        pay_rate_cents = 0

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO employees (name, role, phoenix_job_code, pay_type, "
            "pay_rate_cents, hire_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, role, phoenix_job_code or None, pay_type,
             pay_rate_cents, hire_date or None, notes or None),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("payroll.index"))


@bp.route("/employees/update/<int:emp_id>", methods=["POST"])
def update_employee(emp_id: int):
    """Update an employee, auto-logging rate changes."""
    conn = get_connection(g.entity_key)
    try:
        old = conn.execute(
            "SELECT * FROM employees WHERE id = ?", (emp_id,)
        ).fetchone()
        if not old:
            return redirect(url_for("payroll.index"))

        name = request.form.get("name", old["name"]).strip()
        role = request.form.get("role", old["role"]).strip()
        pay_type = request.form.get("pay_type", old["pay_type"])
        pay_rate = request.form.get("pay_rate", "0").replace(",", "").replace("$", "")
        hire_date = request.form.get("hire_date", old["hire_date"] or "")
        status = request.form.get("status", old["status"])
        phoenix_job_code = request.form.get("phoenix_job_code", old["phoenix_job_code"] or "").strip()
        notes = request.form.get("notes", old["notes"] or "").strip()

        try:
            new_rate_cents = int(round(float(pay_rate) * 100))
        except (ValueError, TypeError):
            new_rate_cents = old["pay_rate_cents"]

        # Log rate change if pay rate changed
        if new_rate_cents != old["pay_rate_cents"] and old["pay_rate_cents"] > 0:
            eff_date = date.today().strftime("%Y-%m-%d")
            _log_pay_change(conn, emp_id, old["pay_rate_cents"], new_rate_cents, eff_date)

        conn.execute(
            "UPDATE employees SET name=?, role=?, phoenix_job_code=?, pay_type=?, "
            "pay_rate_cents=?, hire_date=?, status=?, notes=?, "
            "updated_at=datetime('now') WHERE id=?",
            (name, role, phoenix_job_code or None, pay_type,
             new_rate_cents, hire_date or None, status, notes or None, emp_id),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("payroll.index"))


@bp.route("/employees/delete/<int:emp_id>", methods=["POST"])
def delete_employee(emp_id: int):
    """Delete an employee (CASCADE deletes pay changes + payroll entries)."""
    conn = get_connection(g.entity_key)
    try:
        conn.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("payroll.index"))


@bp.route("/employees/detail/<int:emp_id>")
def employee_detail(emp_id: int):
    """Return JSON with employee detail for the modal."""
    conn = get_connection(g.entity_key)
    try:
        emp = conn.execute(
            "SELECT * FROM employees WHERE id = ?", (emp_id,)
        ).fetchone()
        if not emp:
            return jsonify({"error": "Employee not found"}), 404

        emp_dict = dict(emp)
        emp_dict["pay_changes"] = _get_pay_changes(conn, emp_id)
        emp_dict["recent_paychecks"] = _get_recent_paychecks(conn, emp_id)

        # Peer comparison
        role_avgs = _get_compensation_analysis(conn)
        emp_dict["peer_avg_cents"] = role_avgs.get(emp["role"], 0)

        # Days since last raise
        last_change = conn.execute(
            "SELECT effective_date FROM employee_pay_changes "
            "WHERE employee_id = ? ORDER BY effective_date DESC LIMIT 1",
            (emp_id,),
        ).fetchone()
        if last_change:
            try:
                d = datetime.strptime(last_change["effective_date"], "%Y-%m-%d")
                emp_dict["days_since_raise"] = (datetime.now() - d).days
            except (ValueError, TypeError):
                emp_dict["days_since_raise"] = None
        else:
            emp_dict["days_since_raise"] = None

        return jsonify(emp_dict)
    finally:
        conn.close()


@bp.route("/import/parse", methods=["POST"])
def import_parse():
    """Upload + parse Phoenix report, return preview page."""
    f = request.files.get("payroll_file")
    if not f or not f.filename:
        return redirect(url_for("payroll.index"))

    entries, warnings = parse_phoenix_per_payroll_costs(f)

    if not entries:
        return render_template(
            "payroll.html",
            employees=_get_employees_safe(),
            role_avgs={},
            role_spending=[],
            grand_total=0,
            role_colors=ROLE_COLORS,
            role_order=ROLE_ORDER,
            available_months=[],
            spending_month=date.today().strftime("%Y-%m"),
            import_warnings=warnings,
            import_error="No payroll entries found in the uploaded file.",
        )

    conn = get_connection(g.entity_key)
    try:
        matched, unmatched = match_to_employees(conn, entries)
        unique_employees = get_unique_employees_from_entries(entries)

        # Save parsed data to temp for the save step
        temp_key = f"payroll_import_{uuid.uuid4().hex[:12]}"
        _save_temp(temp_key, {
            "entries": entries,
            "filename": f.filename,
        })

        employees = _get_employees(conn)
        role_avgs = _get_compensation_analysis(conn)
        available_months = _get_available_months(conn)
        spending_month = date.today().strftime("%Y-%m")
        role_spending = _get_role_spending(conn, spending_month, spending_month)
        grand_total = sum(rs["total_cents"] for rs in role_spending)

        return render_template(
            "payroll.html",
            employees=employees,
            role_avgs=role_avgs,
            role_spending=role_spending,
            grand_total=grand_total,
            role_colors=ROLE_COLORS,
            role_order=ROLE_ORDER,
            available_months=available_months,
            spending_month=spending_month,
            import_preview=True,
            import_temp_key=temp_key,
            import_matched=matched,
            import_unmatched=unmatched,
            import_unique_employees=unique_employees,
            import_warnings=warnings,
            import_filename=f.filename,
            import_total_entries=len(entries),
        )
    finally:
        conn.close()


@bp.route("/import/save", methods=["POST"])
def import_save():
    """Save parsed payroll entries to the database."""
    temp_key = request.form.get("temp_key", "")
    data = _load_temp(temp_key)
    if not data:
        return redirect(url_for("payroll.index"))

    entries = data["entries"]
    filename = data.get("filename", "")

    conn = get_connection(g.entity_key)
    try:
        # Process new employee assignments from the form
        # Form fields: assign_{employee_name} = existing employee_id or "new"
        # For new employees: new_role_{employee_name} = role
        existing_employees = {
            r["name"].lower().strip(): dict(r)
            for r in conn.execute("SELECT * FROM employees").fetchall()
        }

        # Collect assignments from form
        assignments: dict[str, int] = {}  # lowercase name -> employee_id
        for key, val in request.form.items():
            if key.startswith("assign_"):
                emp_name = key[7:]  # Remove "assign_" prefix
                if val == "new":
                    # Create new employee
                    role = request.form.get(f"new_role_{emp_name}", "")
                    if not role:
                        continue
                    # Find Phoenix job code from entries
                    job_code = ""
                    for e in entries:
                        if e["name"] == emp_name:
                            job_code = e.get("phoenix_job_code", "")
                            break
                    cur = conn.execute(
                        "INSERT INTO employees (name, role, phoenix_job_code, pay_type, "
                        "pay_rate_cents) VALUES (?, ?, ?, 'hourly', 0)",
                        (emp_name, role, job_code or None),
                    )
                    assignments[emp_name.lower().strip()] = cur.lastrowid
                elif val:
                    try:
                        assignments[emp_name.lower().strip()] = int(val)
                    except (ValueError, TypeError):
                        pass

        # Match entries to employees and insert
        inserted = 0
        skipped = 0
        for entry in entries:
            e_name = entry["name"].lower().strip()
            emp_id = assignments.get(e_name)

            # Try existing employees if not in assignments
            if emp_id is None:
                emp = existing_employees.get(e_name)
                if emp:
                    emp_id = emp["id"]

            if emp_id is None:
                skipped += 1
                continue

            amount_cents = int(round(entry["amount"] * 100))
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO payroll_entries "
                    "(employee_id, paycheck_date, amount_cents, source_filename) "
                    "VALUES (?, ?, ?, ?)",
                    (emp_id, entry["paycheck_date"], amount_cents, filename),
                )
                inserted += 1
            except Exception:
                skipped += 1

        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("payroll.index"))


@bp.route("/spending")
def spending_partial():
    """HTMX partial: role spending for selected pay period."""
    spending_period = request.args.get("spending_period", date.today().strftime("%Y-%m-%d"))

    conn = get_connection(g.entity_key)
    try:
        role_spending = _get_role_spending(conn, spending_period)
        grand_total = sum(rs["total_cents"] for rs in role_spending)

        lines = []
        if not role_spending:
            lines.append(
                '<div class="pr-spending-empty">No payroll data for this pay period</div>'
            )
        else:
            for rs in role_spending:
                pct = round(rs["total_cents"] / grand_total * 100) if grand_total else 0
                color = ROLE_COLORS.get(rs["role"], "#98989d")
                role_esc = escape(rs["role"])
                lines.append(
                    f'<div class="pr-spending-role">'
                    f'<div class="pr-spending-role-header">'
                    f'<span class="pr-role-badge" style="background:{color}">{role_esc}</span>'
                    f'<span class="pr-spending-amount">${rs["total_cents"] / 100:,.0f}</span>'
                    f'<span class="pr-spending-pct">{pct}%</span>'
                    f'</div>'
                    f'<div class="pr-spending-bar-track">'
                    f'<div class="pr-spending-bar-fill" style="width:{pct}%;background:{color}"></div>'
                    f'</div>'
                )
                # Per-employee breakdown
                for emp in rs["employees"]:
                    emp_pct = round(emp["total_cents"] / grand_total * 100) if grand_total else 0
                    emp_esc = escape(emp["name"])
                    lines.append(
                        f'<div class="pr-spending-employee">'
                        f'<span class="pr-spending-emp-name">{emp_esc}</span>'
                        f'<span class="pr-spending-emp-amount">${emp["total_cents"] / 100:,.0f}</span>'
                        f'</div>'
                    )
                lines.append('</div>')

            # Grand total
            lines.append(
                f'<div class="pr-spending-total">'
                f'<span>Total</span>'
                f'<span>${grand_total / 100:,.0f}</span>'
                f'</div>'
            )

        return "\n".join(lines)
    finally:
        conn.close()


def _get_employees_safe() -> list[dict]:
    """Get employees without crashing if table doesn't exist yet."""
    try:
        conn = get_connection(g.entity_key)
        try:
            return _get_employees(conn)
        finally:
            conn.close()
    except Exception:
        return []
