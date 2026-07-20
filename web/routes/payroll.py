"""Payroll — employee roster, Phoenix import, role-based spending."""

from __future__ import annotations

import json
import os
import re
import tempfile
import time
import uuid
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Blueprint, flash, g, jsonify, redirect, render_template, request, url_for
from markupsafe import escape

from core.db import get_connection
from core.payroll_parser import (
    PHOENIX_JOB_CODE_MAP,
    PayrollWorkbookError,
    get_unique_employees_from_entries,
    parse_phoenix_per_payroll_costs,
    suggest_role,
)

bp = Blueprint("payroll", __name__, url_prefix="/payroll")

_TEMP_DIR = os.path.join(tempfile.gettempdir(), "expense-tracker-uploads")
_TEMP_MAX_AGE_SECONDS = 4 * 3600
os.makedirs(_TEMP_DIR, exist_ok=True)


@bp.before_request
def _require_bfm_entity():
    """Keep every payroll read and mutation inside the BFM entity."""
    if g.entity_key != "company":
        return redirect(url_for("dashboard.index"))

# ── Role colors for badges ───────────────────────────────────────────────────

ROLE_COLORS: dict[str, str] = {
    "Providers": "#ef4444",
    "Nurses": "#8b5cf6",
    "Scribes": "#f59e0b",
    "Front Office": "#22c55e",
    "Office Manager": "#3b82f6",
    "HR": "#6366f1",
    "Owner": "#94a3b8",
}

ROLE_ORDER = ["Providers", "Nurses", "Scribes", "Front Office", "Office Manager", "HR", "Owner"]
PAY_TYPES = {"hourly", "salary"}
EMPLOYEE_STATUSES = {"active", "inactive", "terminated"}
MAX_PAY_RATE_CENTS = 99_999_999_999


class EmployeeValidationError(ValueError):
    """A controlled employee-roster validation failure."""


def _normalize_employee_name(value: str | None) -> str:
    return (value or "").strip()


def _employee_name_key(value: str | None) -> str:
    return _normalize_employee_name(value).casefold()


def _parse_pay_rate_cents(value: str | None) -> int:
    raw_value = (value or "").strip().replace(",", "").replace("$", "")
    if not raw_value:
        return 0
    try:
        amount = Decimal(raw_value)
    except (InvalidOperation, ValueError):
        raise EmployeeValidationError("Enter a valid pay rate.") from None
    if not amount.is_finite() or amount < 0:
        raise EmployeeValidationError("Pay rate must be a finite non-negative amount.")
    if amount > Decimal(MAX_PAY_RATE_CENTS) / 100:
        raise EmployeeValidationError("Pay rate exceeds the supported maximum.")
    try:
        cents = (amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        raise EmployeeValidationError("Pay rate exceeds the supported maximum.") from None
    return int(cents)


def _validate_hire_date(value: str | None) -> str | None:
    hire_date = (value or "").strip()
    if not hire_date:
        return None
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", hire_date):
        raise EmployeeValidationError("Enter a valid hire date.")
    try:
        date.fromisoformat(hire_date)
    except ValueError:
        raise EmployeeValidationError("Enter a valid hire date.") from None
    return hire_date


def _validate_employee_fields(
    *,
    name: str | None,
    role: str | None,
    pay_type: str | None,
    pay_rate: str | None,
    hire_date: str | None = None,
    status: str | None = "active",
    phoenix_job_code: str | None = None,
) -> dict:
    """Normalize and validate one employee row before any mutation."""
    normalized_name = _normalize_employee_name(name)
    normalized_role = (role or "").strip()
    normalized_pay_type = (pay_type or "").strip()
    normalized_status = (status or "").strip()
    if not normalized_name:
        raise EmployeeValidationError("Employee name is required.")
    if normalized_role not in ROLE_ORDER:
        raise EmployeeValidationError("Select a valid employee role.")
    if normalized_pay_type not in PAY_TYPES:
        raise EmployeeValidationError("Select a valid pay type.")
    if normalized_status not in EMPLOYEE_STATUSES:
        raise EmployeeValidationError("Select a valid employee status.")
    return {
        "name": normalized_name,
        "role": normalized_role,
        "pay_type": normalized_pay_type,
        "pay_rate_cents": _parse_pay_rate_cents(pay_rate),
        "hire_date": _validate_hire_date(hire_date),
        "status": normalized_status,
        "phoenix_job_code": (phoenix_job_code or "").strip() or None,
    }


def _reject_employee_input(exc: EmployeeValidationError):
    flash(str(exc), "danger")
    return redirect(url_for("payroll.index"))


def _sanitize_temp_key(key: str) -> str:
    """Strip path separators to prevent directory traversal."""
    return os.path.basename(key).replace("..", "")


def _temp_path(key: str) -> str | None:
    """Return the exact payroll payload path for a valid opaque key."""
    safe_key = _sanitize_temp_key(key)
    if not safe_key or safe_key != key:
        return None
    return os.path.join(_TEMP_DIR, f"{safe_key}.json")


def _save_temp(key: str, data: dict) -> None:
    path = _temp_path(key)
    if path is None:
        raise ValueError("Invalid temporary payroll key")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)


def _delete_temp(key: str) -> bool:
    """Delete exactly one payroll payload, returning whether it existed."""
    path = _temp_path(key)
    if path is None:
        return False
    try:
        os.remove(path)
        return True
    except FileNotFoundError:
        return False


def _load_temp(key: str) -> dict | None:
    """Consume one fresh, structurally valid payroll payload."""
    path = _temp_path(key)
    if path is None:
        return None
    try:
        if os.path.getmtime(path) < time.time() - _TEMP_MAX_AGE_SECONDS:
            _delete_temp(key)
            return None
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        _delete_temp(key)
        return None

    _delete_temp(key)
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("entries"), list)
        or not isinstance(data.get("filename", ""), str)
    ):
        return None
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


def _render_import_error(warnings: list[str], message: str):
    """Render a controlled payroll import outcome without retaining payloads."""
    return render_template(
        "payroll.html",
        employees=_get_employees_safe(),
        role_avgs={},
        role_spending=[],
        grand_total=0,
        role_colors=ROLE_COLORS,
        role_order=ROLE_ORDER,
        available_periods=[],
        spending_period=date.today().strftime("%Y-%m-%d"),
        import_warnings=warnings,
        import_error=message,
    )


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
    try:
        employee = _validate_employee_fields(
            name=request.form.get("name", ""),
            role=request.form.get("role", ""),
            pay_type=request.form.get("pay_type", "hourly"),
            pay_rate=request.form.get("pay_rate", ""),
            hire_date=request.form.get("hire_date", ""),
            status="active",
            phoenix_job_code=request.form.get("phoenix_job_code", ""),
        )
    except EmployeeValidationError as exc:
        return _reject_employee_input(exc)
    notes = request.form.get("notes", "").strip()

    conn = get_connection(g.entity_key)
    try:
        conn.execute(
            "INSERT INTO employees (name, role, phoenix_job_code, pay_type, "
            "pay_rate_cents, hire_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (employee["name"], employee["role"], employee["phoenix_job_code"],
             employee["pay_type"], employee["pay_rate_cents"],
             employee["hire_date"], notes or None),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
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

        try:
            employee = _validate_employee_fields(
                name=request.form.get("name", old["name"]),
                role=request.form.get("role", old["role"]),
                pay_type=request.form.get("pay_type", old["pay_type"]),
                pay_rate=request.form.get(
                    "pay_rate", str(Decimal(old["pay_rate_cents"]) / 100)
                ),
                hire_date=request.form.get("hire_date", old["hire_date"] or ""),
                status=request.form.get("status", old["status"]),
                phoenix_job_code=request.form.get(
                    "phoenix_job_code", old["phoenix_job_code"] or ""
                ),
            )
        except EmployeeValidationError as exc:
            return _reject_employee_input(exc)
        notes = request.form.get("notes", old["notes"] or "").strip()

        # Log rate change if pay rate changed
        if (employee["pay_rate_cents"] != old["pay_rate_cents"]
                and old["pay_rate_cents"] > 0):
            eff_date = date.today().strftime("%Y-%m-%d")
            _log_pay_change(
                conn, emp_id, old["pay_rate_cents"],
                employee["pay_rate_cents"], eff_date
            )

        conn.execute(
            "UPDATE employees SET name=?, role=?, phoenix_job_code=?, pay_type=?, "
            "pay_rate_cents=?, hire_date=?, status=?, notes=?, "
            "updated_at=datetime('now') WHERE id=?",
            (employee["name"], employee["role"], employee["phoenix_job_code"],
             employee["pay_type"], employee["pay_rate_cents"],
             employee["hire_date"], employee["status"], notes or None, emp_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
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

    if not f.filename.lower().endswith(".xlsx"):
        return _render_import_error(
            ["Unsupported payroll file type."],
            "Upload a Phoenix payroll workbook in .xlsx format.",
        )

    try:
        entries, warnings = parse_phoenix_per_payroll_costs(f)
    except PayrollWorkbookError:
        return _render_import_error(
            ["The uploaded workbook could not be read."],
            "Upload a valid Phoenix payroll workbook and try again.",
        )

    if not entries:
        return _render_import_error(
            warnings,
            "No payroll entries found in the uploaded file.",
        )

    conn = get_connection(g.entity_key)
    try:
        unique_employees = get_unique_employees_from_entries(entries)
        employees = _get_employees(conn)
        employees_by_name: dict[str, list[dict]] = {}
        for employee in employees:
            employees_by_name.setdefault(
                _employee_name_key(employee["name"]), []
            ).append(employee)
        for employee in unique_employees:
            exact_matches = employees_by_name.get(
                _employee_name_key(employee["name"]), []
            )
            employee["exact_matches"] = exact_matches
            employee["matched_employee"] = (
                exact_matches[0] if len(exact_matches) == 1 else None
            )

        # Save parsed data to temp for the save step
        temp_key = f"payroll_import_{uuid.uuid4().hex[:12]}"
        _save_temp(temp_key, {
            "entries": entries,
            "filename": f.filename,
        })

        role_avgs = _get_compensation_analysis(conn)
        available_periods = _get_available_pay_periods(conn)
        spending_period = available_periods[-1] if available_periods else date.today().strftime("%Y-%m-%d")
        role_spending = _get_role_spending(conn, spending_period)
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
            import_preview=True,
            import_temp_key=temp_key,
            import_unique_employees=unique_employees,
            import_warnings=warnings,
            import_filename=f.filename,
            import_total_entries=len(entries),
        )
    finally:
        conn.close()


@bp.route("/import/cancel", methods=["POST"])
def import_cancel():
    """End one abandoned payroll preview and discard only its payload."""
    _delete_temp(request.form.get("temp_key", ""))
    return redirect(url_for("payroll.index"))


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
        employee_rows = [
            dict(r) for r in conn.execute("SELECT * FROM employees").fetchall()
        ]
        existing_employee_ids = {employee["id"] for employee in employee_rows}
        existing_employees: dict[str, list[dict]] = {}
        for employee in employee_rows:
            existing_employees.setdefault(
                _employee_name_key(employee["name"]), []
            ).append(employee)
        entries_by_name = {
            _employee_name_key(entry.get("name")): entry
            for entry in entries
            if _employee_name_key(entry.get("name"))
        }

        # Validate the full roster-assignment batch before the first write.
        assignments: dict[str, int] = {}  # lowercase name -> employee_id
        pending_new_employees: list[tuple[str, dict]] = []
        seen_assignment_names: set[str] = set()
        for key, val in request.form.items():
            if key.startswith("assign_"):
                emp_name = key[7:]  # Remove "assign_" prefix
                normalized_name = _employee_name_key(emp_name)
                if normalized_name not in entries_by_name:
                    raise EmployeeValidationError(
                        "Select a valid payroll employee assignment."
                    )
                if normalized_name in seen_assignment_names:
                    raise EmployeeValidationError(
                        "Select each payroll employee only once."
                    )
                seen_assignment_names.add(normalized_name)
                if val == "new":
                    exact_matches = existing_employees.get(normalized_name, [])
                    if len(exact_matches) == 1:
                        assignments[normalized_name] = exact_matches[0]["id"]
                        continue
                    if exact_matches:
                        # Never create another employee when the submitted name
                        # is already ambiguous. The preview requires an explicit
                        # existing employee choice in this case.
                        continue
                    # Create new employee
                    role = request.form.get(f"new_role_{emp_name}", "")
                    if not role:
                        continue
                    # Find Phoenix job code from entries
                    job_code = entries_by_name[normalized_name].get(
                        "phoenix_job_code", ""
                    )
                    employee = _validate_employee_fields(
                        name=emp_name,
                        role=role,
                        pay_type="hourly",
                        pay_rate="0",
                        status="active",
                        phoenix_job_code=job_code,
                    )
                    pending_new_employees.append((normalized_name, employee))
                elif val:
                    try:
                        employee_id = int(val)
                    except (ValueError, TypeError):
                        raise EmployeeValidationError(
                            "Select a valid existing employee."
                        ) from None
                    if employee_id not in existing_employee_ids:
                        raise EmployeeValidationError(
                            "Select a valid existing employee."
                        )
                    assignments[normalized_name] = employee_id

        for normalized_name, employee in pending_new_employees:
            cur = conn.execute(
                "INSERT INTO employees (name, role, phoenix_job_code, pay_type, "
                "pay_rate_cents, hire_date, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (employee["name"], employee["role"], employee["phoenix_job_code"],
                 employee["pay_type"], employee["pay_rate_cents"],
                 employee["hire_date"], employee["status"]),
            )
            assignments[normalized_name] = cur.lastrowid
            new_employee = {
                "id": cur.lastrowid,
                "name": employee["name"],
            }
            existing_employee_ids.add(cur.lastrowid)
            existing_employees[normalized_name] = [new_employee]

        # Match entries to employees and insert
        inserted = 0
        skipped = 0
        for entry in entries:
            e_name = _employee_name_key(entry["name"])
            emp_id = assignments.get(e_name)

            # Try existing employees if not in assignments
            if emp_id is None:
                exact_matches = existing_employees.get(e_name, [])
                if len(exact_matches) == 1:
                    emp_id = exact_matches[0]["id"]

            if emp_id is None:
                skipped += 1
                continue

            amount_cents = int(round(entry["amount"] * 100))
            conn.execute(
                "INSERT OR IGNORE INTO payroll_entries "
                "(employee_id, paycheck_date, amount_cents, source_filename) "
                "VALUES (?, ?, ?, ?)",
                (emp_id, entry["paycheck_date"], amount_cents, filename),
            )
            inserted += 1

        conn.commit()
    except EmployeeValidationError as exc:
        conn.rollback()
        return _reject_employee_input(exc)
    except Exception:
        conn.rollback()
        raise
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
