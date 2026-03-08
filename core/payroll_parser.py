"""Phoenix / Greenpage CyberPayroll report parser.

Parses the "Per Payroll Costs" Excel export which contains one row per employee
with columns for each paycheck date.  Amounts = Gross + ER Tax + Benefits
(total employer cost).

Format:
  Row 0: Title ("BUFFINGTON FAMILY MEDICINE PLLC PAYROLL ...")
  Row 1: Blank
  Row 2: Header — "YYYY Paycheck Dates" | date cols | "Total"
  Rows 3–N: Name | Job Code | Location | amounts... | Total
  TOTAL row: aggregate
  (May repeat for multiple years with blank rows between sections)
"""

from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import IO, Union

import pandas as pd


# ── Phoenix job code → role mapping ──────────────────────────────────────────

PHOENIX_JOB_CODE_MAP: dict[str, str] = {
    "700 PA": "Providers",
    "600 Nurse /MA": "Nurses",
    "200 Scribe": "Scribes",
    "400 Front Office": "Front Office",
    "100 Billing": "Front Office",
    "900 Owner": "Owner",
    "Human Resources": "Office Manager",
}


def _parse_date(val) -> str | None:
    """Parse a Phoenix date value (M/D/YYYY or datetime) to YYYY-MM-DD."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d")
    s = str(val).strip()
    if not s:
        return None
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _is_amount(val) -> bool:
    """Check if a value is a numeric amount (not NaN, not None)."""
    if val is None:
        return False
    if isinstance(val, (int, float)):
        return not math.isnan(val) and val != 0
    return False


def parse_phoenix_per_payroll_costs(
    file_or_path: Union[str, Path, IO],
) -> tuple[list[dict], list[str]]:
    """Parse a Phoenix 'Per Payroll Costs' Excel report.

    Returns:
        (entries, warnings) where entries is a flat list of dicts:
            {name, phoenix_job_code, paycheck_date, amount}
        and warnings is a list of human-readable warning strings.
    """
    df = pd.read_excel(file_or_path, header=None)
    entries: list[dict] = []
    warnings: list[str] = []

    nrows, ncols = df.shape

    # Find year-section headers by looking for "Paycheck Dates" in any cell
    header_rows: list[int] = []
    for i in range(nrows):
        for j in range(ncols):
            cell = df.iloc[i, j]
            if isinstance(cell, str) and "Paycheck Dates" in cell:
                header_rows.append(i)
                break

    if not header_rows:
        warnings.append("Could not find any 'Paycheck Dates' header row.")
        return entries, warnings

    for hi, hrow in enumerate(header_rows):
        # Parse date columns from the header row
        # Column 0 = "YYYY Paycheck Dates", columns 1-2 might be Job Code / Location
        # or the dates might start at column 3 if name/jobcode/location are in 0-2
        # Detect by scanning for date-like values

        # First, figure out where the data columns start
        # Try to parse dates from each column in the header row
        date_cols: list[tuple[int, str]] = []
        for j in range(ncols):
            d = _parse_date(df.iloc[hrow, j])
            if d:
                date_cols.append((j, d))

        if not date_cols:
            warnings.append(f"No date columns found in header row {hrow}.")
            continue

        # Data starts on the row after the header
        data_start = hrow + 1
        # Data ends at next header, "TOTAL" row, or end of dataframe
        data_end = header_rows[hi + 1] if hi + 1 < len(header_rows) else nrows

        for i in range(data_start, data_end):
            name_val = df.iloc[i, 0]
            if name_val is None or (isinstance(name_val, float) and math.isnan(name_val)):
                continue
            name = str(name_val).strip()
            if not name or name.upper().startswith("TOTAL"):
                continue

            # Column 1 = Job Code, Column 2 = Location
            job_code_val = df.iloc[i, 1]
            job_code = str(job_code_val).strip() if job_code_val is not None and not (isinstance(job_code_val, float) and math.isnan(job_code_val)) else ""

            for col_idx, paycheck_date in date_cols:
                val = df.iloc[i, col_idx]
                if _is_amount(val):
                    entries.append({
                        "name": name,
                        "phoenix_job_code": job_code,
                        "paycheck_date": paycheck_date,
                        "amount": round(float(val), 2),
                    })

    if not entries:
        warnings.append("No payroll entries found in the file.")

    # Deduplicate (same name + date)
    seen = set()
    deduped = []
    for e in entries:
        key = (e["name"], e["paycheck_date"])
        if key not in seen:
            seen.add(key)
            deduped.append(e)
        else:
            warnings.append(
                f"Duplicate entry skipped: {e['name']} on {e['paycheck_date']}"
            )
    entries = deduped

    return entries, warnings


def match_to_employees(
    conn, entries: list[dict]
) -> tuple[list[dict], list[dict]]:
    """Match parsed entries to employees in the database.

    Returns:
        (matched, unmatched) where each entry gets an 'employee_id' field if matched.
    """
    rows = conn.execute(
        "SELECT id, name, phoenix_job_code, role FROM employees"
    ).fetchall()

    # Build lookup indexes
    name_map: dict[str, dict] = {}  # lowercase name -> employee row
    for r in rows:
        name_map[r["name"].lower().strip()] = dict(r)

    matched: list[dict] = []
    unmatched: list[dict] = []

    for entry in entries:
        e_name = entry["name"].lower().strip()
        emp = name_map.get(e_name)
        if emp:
            entry["employee_id"] = emp["id"]
            entry["employee_name"] = emp["name"]
            entry["role"] = emp["role"]
            matched.append(entry)
        else:
            unmatched.append(entry)

    return matched, unmatched


def suggest_role(phoenix_job_code: str) -> str:
    """Suggest a role based on Phoenix job code."""
    code = phoenix_job_code.strip()
    return PHOENIX_JOB_CODE_MAP.get(code, "")


def get_unique_employees_from_entries(entries: list[dict]) -> list[dict]:
    """Extract unique employee names + job codes from parsed entries.

    Returns list of dicts: {name, phoenix_job_code, suggested_role, entry_count, total_amount}
    """
    emp_data: dict[str, dict] = {}
    for e in entries:
        name = e["name"]
        if name not in emp_data:
            emp_data[name] = {
                "name": name,
                "phoenix_job_code": e["phoenix_job_code"],
                "suggested_role": suggest_role(e["phoenix_job_code"]),
                "entry_count": 0,
                "total_amount": 0.0,
            }
        emp_data[name]["entry_count"] += 1
        emp_data[name]["total_amount"] += e["amount"]

    return sorted(emp_data.values(), key=lambda x: x["name"])
