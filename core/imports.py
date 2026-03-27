"""CSV and PDF ingestion, normalization, deduplication, and commit."""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

from core.db import get_connection, get_data_dir


# ── Transaction ID ────────────────────────────────────────────────────────────

def compute_transaction_id(date: str, amount: float, description_raw: str) -> str:
    """Stable 24-char SHA-256 hash of (date, amount, description_raw)."""
    key = f"{date}|{amount:.6f}|{description_raw.strip().lower()}"
    return hashlib.sha256(key.encode()).hexdigest()[:24]


# ── CSV helpers ───────────────────────────────────────────────────────────────

def _try_read_csv(path) -> Optional[pd.DataFrame]:
    """Attempt a normal pd.read_csv; return None on parse errors."""
    try:
        df = pd.read_csv(path, dtype=str, skip_blank_lines=True)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception:
        return None


def _read_raw_lines(path) -> list[str]:
    """Read all lines from a path or file-like object."""
    if hasattr(path, "read"):
        if hasattr(path, "seek"):
            path.seek(0)
        data = path.read()
        if isinstance(data, bytes):
            data = data.decode("utf-8", errors="replace")
        return data.splitlines(keepends=True)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


# ── CSV parsing ───────────────────────────────────────────────────────────────

def parse_csv(
    path: str | Path,
    profile: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Parse a CSV file into a raw DataFrame with canonical column names.

    If *profile* is provided, rename columns per the stored mapping.
    Falls back to heuristic auto-detection for any still-missing columns.
    Raises ValueError if required columns (date, description_raw, amount)
    cannot be resolved.
    """
    # Some bank CSVs (e.g. BofA checking) have a summary header section
    # with fewer columns than the data, causing a parse error.  We try a
    # normal read first; if that fails or produces no recognisable date
    # column, scan for the real header row and re-read from there.
    import io as _io

    df = _try_read_csv(path)

    if df is None or ("Date" not in df.columns and "date" not in [c.lower() for c in df.columns]):
        raw_lines = _read_raw_lines(path)
        header_idx = None
        for i, line in enumerate(raw_lines):
            if "Date" in line and "Description" in line:
                header_idx = i
                break
        if header_idx is not None:
            csv_text = "".join(raw_lines[header_idx:])
            df = pd.read_csv(_io.StringIO(csv_text), dtype=str, skip_blank_lines=True)
            df.columns = [c.strip() for c in df.columns]
        elif df is None:
            raise ValueError("Could not parse CSV — mixed column counts and no recognisable header found.")

    if profile:
        rename: dict[str, str] = {}
        for canonical, src in [
            ("date",            profile.get("date_col")),
            ("description_raw", profile.get("description_col")),
            ("amount",          profile.get("amount_col")),
            ("merchant_raw",    profile.get("merchant_col")),
            ("account",         profile.get("account_col")),
            ("currency",        profile.get("currency_col")),
        ]:
            if src and src in df.columns:
                rename[src] = canonical
        df = df.rename(columns=rename)

    df = _auto_detect_columns(df)

    # Fallback: if no description column but merchant exists, use merchant as description
    if "description_raw" not in df.columns and "merchant_raw" in df.columns:
        df["description_raw"] = df["merchant_raw"]

    # Merge split Debit/Credit columns into a single "amount" column
    df = _merge_debit_credit(df)

    missing = {"date", "description_raw", "amount"} - set(df.columns)
    if missing:
        raise ValueError(
            f"Could not resolve required columns {missing}. "
            f"Available: {list(df.columns)}"
        )
    return df


def _auto_detect_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Heuristically map common column-name variants to canonical names."""
    mapping: dict[str, str] = {}
    for col in df.columns:
        lc = col.lower().strip()
        if lc in {"date", "transaction date", "trans date", "posted date",
                  "posting date", "trans. date"}:
            mapping.setdefault("date", col)
        elif lc in {"description", "memo", "narrative", "transaction description",
                    "details", "payee", "merchant name", "name"}:
            mapping.setdefault("description_raw", col)
        elif lc in {"amount", "transaction amount", "value", "amt"}:
            mapping.setdefault("amount", col)
        elif lc in {"merchant", "vendor"}:
            mapping.setdefault("merchant_raw", col)
        elif lc in {"account", "account name", "account number", "account #"}:
            mapping.setdefault("account", col)
        elif lc in {"currency", "currency code", "ccy"}:
            mapping.setdefault("currency", col)

    return df.rename(columns={v: k for k, v in mapping.items()})


def _merge_debit_credit(df: pd.DataFrame) -> pd.DataFrame:
    """
    If the CSV has separate Debit/Credit columns but no Amount column,
    merge them: debits become negative, credits become positive.
    """
    if "amount" in df.columns:
        return df

    # Find debit and credit columns
    debit_col = credit_col = None
    for col in df.columns:
        lc = col.lower().strip()
        if lc in {"debit", "debit amount", "debits", "withdrawal"}:
            debit_col = col
        elif lc in {"credit", "credit amount", "credits", "deposit"}:
            credit_col = col

    if not debit_col and not credit_col:
        return df

    def _to_float(val):
        if not isinstance(val, str) or not val.strip():
            return 0.0
        cleaned = re.sub(r"[^\d.\-]", "", val.strip())
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    if debit_col and credit_col:
        debits  = df[debit_col].apply(_to_float).abs()
        credits = df[credit_col].apply(_to_float).abs()
        df["amount"] = credits - debits
    elif debit_col:
        df["amount"] = -df[debit_col].apply(_to_float).abs()
    else:
        df["amount"] = df[credit_col].apply(_to_float).abs()

    # Convert back to string so _parse_amount handles it downstream
    df["amount"] = df["amount"].apply(lambda x: str(x))
    return df


# ── PDF parsing ───────────────────────────────────────────────────────────────

# Pattern A: full date — MM/DD/YY(YY) description amount
# Optional asterisk after date handles Amex posting-date notation (e.g. "01/06/26*")
_DATE_LINE_RE = re.compile(
    r"^(\d{2}/\d{2}/\d{2,4})\*?\s+(.+?)\s+(-?\$?[\d,]+\.\d{2})\s*$"
)
# Pattern B: short numeric date — MM/DD [MM/DD] description amount
# Handles BofA CC ("01/21 01/22 PAYMENT ...") and Citi CC ("01/14 01/15 KROGER ...")
# Note: no end-of-line anchor — credit card PDFs often have sidebar text after the amount
_SHORT_DATE_LINE_RE = re.compile(
    r"^(\d{2}/\d{2})\s+(?:\d{2}/\d{2}\s+)?(.+?)\s+(-?\$?[\d,]+\.\d{2})(?:\s|$)"
)
# Pattern C: named-month date — Mon DD Mon DD description amount
# Handles Barclay CC ("Nov 04 Nov 05 Payment Received ...")
_MONTH_DATE_LINE_RE = re.compile(
    r"^([A-Z][a-z]{2}\s+\d{2})\s+[A-Z][a-z]{2}\s+\d{2}\s+(.+?)\s+(-?\$?[\d,]+\.\d{2})(?:\s|$)"
)
# Check line: check# MM-DD $amount
_CHECK_LINE_RE = re.compile(
    r"^(\d{4,6})\s+(\d{2}-\d{2})\s+(-?\$?[\d,]+\.\d{2})\s*$"
)

# Month name → number mapping for named-month dates
_MONTH_NUMS = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}

# Section headers that indicate sign of transactions
_CREDIT_SECTIONS = {"DEPOSITS/OTHER CREDITS", "DEPOSITS", "CREDITS",
                    "OTHER CREDITS", "ADDITIONS",
                    # Credit card charge sections — amounts already have correct sign
                    # in the text; sign=1 prevents double-negation from a prior
                    # "PAYMENTS" section.
                    "FEES CHARGED", "INTEREST CHARGED",
                    # Amex uses "New Charges" for the purchase/charges section.
                    "NEW CHARGES"}
_DEBIT_SECTIONS = {"OTHER DEBITS", "DEBITS", "CHECKS", "CHECKS/OTHER DEBITS",
                   "WITHDRAWALS", "PAYMENTS", "SUBTRACTIONS"}
_STOP_SECTIONS = {"DAILY ENDING BALANCE", "DAILY BALANCE", "TOTAL OVERDRAFT",
                  "EARNINGS SUMMARY", "STATEMENT SUMMARY", "TOTAL FOR THIS PERIOD",
                  "ACCOUNT SUMMARY", "SHOP WITH POINTS"}


def parse_pdf(path: str | Path) -> tuple[pd.DataFrame, list[str]]:
    """
    Best-effort transaction extraction from a PDF bank statement.

    Tries table extraction first; falls back to text-based line parsing
    (which handles statements like Prosperity that use plain text layout).
    Returns (DataFrame, error_list).  DataFrame may be empty if nothing
    could be extracted or pdfplumber is not installed.
    """
    try:
        import pdfplumber  # noqa: PLC0415  (optional dep)
    except ImportError:
        return pd.DataFrame(), ["pdfplumber not installed; run: pip install pdfplumber"]

    errors: list[str] = []

    try:
        # Accept both file paths and file-like objects (e.g. Streamlit UploadedFile)
        if hasattr(path, "read"):
            if hasattr(path, "seek"):
                path.seek(0)
            pdf = pdfplumber.open(path)
        else:
            pdf = pdfplumber.open(str(path))
    except Exception as exc:
        return pd.DataFrame(), [f"Failed to open PDF: {exc}"]

    # ── Strategy 1: table extraction ──────────────────────────────────────
    chunks: list[pd.DataFrame] = []
    try:
        for page_num, page in enumerate(pdf.pages, 1):
            for tbl in page.extract_tables() or []:
                try:
                    chunk = _table_to_df(tbl)
                    if chunk is not None and not chunk.empty:
                        chunks.append(chunk)
                except Exception as exc:
                    errors.append(f"Page {page_num} table: {exc}")
    except Exception as exc:
        errors.append(f"Table extraction failed: {exc}")

    if chunks:
        df = pd.concat(chunks, ignore_index=True)
        df = _auto_detect_columns(df)
        # Only trust table extraction if it produced recognisable columns
        # AND the data actually contains parseable dates/amounts (not NaN/junk).
        has_date = "date" in df.columns or any(
            c.lower().strip() in {"date", "transaction date", "posted date"}
            for c in df.columns
        )
        if has_date and len(df) >= 2 and _table_data_looks_valid(df):
            pdf.close()
            return df, errors

    # ── Strategy 2: text-based line parsing ───────────────────────────────
    try:
        df, text_errors = _parse_pdf_text(pdf)
        errors.extend(text_errors)
    except Exception as exc:
        errors.append(f"Text extraction failed: {exc}")
        df = pd.DataFrame()
    finally:
        pdf.close()

    if df.empty:
        errors.append("No transactions could be extracted from PDF")

    return df, errors


def _infer_pdf_year(pdf) -> str:
    """Scan first two pages for the statement year from date-like contexts."""
    for page in pdf.pages[:2]:
        text = page.extract_text() or ""
        # 1. "Month DD, YYYY" or "Month DD - Month DD, YYYY"
        m = re.search(
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
            r"\s+\d{1,2},?\s+(20\d{2})", text
        )
        if m:
            return m.group(1)
        # 2. MM/DD/YYYY (4-digit year in a date)
        m = re.search(r"\d{2}/\d{2}/(20\d{2})", text)
        if m:
            return m.group(1)
        # 3. MM/DD/YY (2-digit year in a date)
        m = re.search(r"\d{2}/\d{2}/(\d{2})\b", text)
        if m:
            return str(2000 + int(m.group(1)))
    return str(datetime.now().year)


def _infer_closing_month(pdf) -> Optional[int]:
    """
    Try to find the statement closing month for year-rollback logic.

    Statements that span two calendar years (e.g. Dec 2025 – Jan 2026)
    need to assign earlier months to the previous year.  Returns the
    closing month (1-12) or None if it can't be determined.
    """
    for page in pdf.pages[:3]:
        text = page.extract_text() or ""
        # "Closing Date" with optional opening-closing range:
        #   Chase:  "Opening/Closing Date 12/21/25 - 01/20/26"
        #   Amex:   "Closing Date01/22/26"
        # If there's a hyphen-separated second date, use that (it's the closing).
        m = re.search(
            r"[Cc]losing\s+[Dd]ate\D*?"
            r"(\d{2}/\d{2}/\d{2,4})"
            r"(?:\s*-\s*(\d{2}/\d{2}/\d{2,4}))?",
            text,
        )
        if m:
            date_str = m.group(2) or m.group(1)
            return int(date_str.split("/")[0])
        # "Statement Date: MM/DD/YY" or "Statement Date MM/DD/YY"
        m = re.search(r"Statement\s+Date:?\s*(\d{2})/\d{2}/\d{2,4}", text)
        if m:
            return int(m.group(1))
        # Barclay: "Statement Balance as of MM/DD/YY"
        m = re.search(r"[Ss]tatement.*?as\s+of\s*(\d{2})/\d{2}/\d{2,4}", text)
        if m:
            return int(m.group(1))
        # "through MM/DD/YY" (Citi)
        m = re.search(r"through\s+(\d{2})/\d{2}/\d{2,4}", text)
        if m:
            return int(m.group(1))
    return None


def _normalise_pdf_date(date_str: str) -> str:
    """Convert MM/DD/YY to MM/DD/YYYY if needed."""
    parts = date_str.split("/")
    if len(parts) == 3 and len(parts[2]) == 2:
        year = int(parts[2])
        parts[2] = str(2000 + year if year < 100 else year)
    return "/".join(parts)


def _month_name_to_date(month_day: str, year: str) -> str:
    """Convert 'Nov 04' to 'MM/DD/YYYY'."""
    parts = month_day.split()
    month_num = _MONTH_NUMS.get(parts[0].lower(), "01")
    return f"{month_num}/{parts[1]}/{year}"


def _year_for_short_date(date_short: str, stmt_year: str, closing_month: Optional[int]) -> str:
    """
    Determine the correct year for a short MM/DD date.

    Statements that span two calendar years (e.g. Dec – Jan) need December
    transactions assigned to the previous year.  If the transaction month is
    later than the statement closing month, it belongs to the prior year.
    """
    txn_month = int(date_short.split("/")[0])
    if closing_month is not None and txn_month > closing_month:
        return str(int(stmt_year) - 1)
    return stmt_year


def _parse_pdf_amount(amt_str: str, section_sign: int) -> float:
    """
    Parse an amount string from a PDF line, applying section sign correctly.

    If the amount already has a negative sign in the text (e.g. BofA debits),
    we keep that sign.  If it's positive and the section is debit, we negate it
    (e.g. Prosperity debits shown as positive under a "DEBITS" header).
    """
    cleaned = amt_str.replace(",", "").replace("$", "")
    amount = float(cleaned)
    # Only apply section sign if the text amount is positive — avoids double-negating
    if section_sign == -1 and amount > 0:
        amount = -amount
    return amount


def _parse_pdf_text(pdf) -> tuple[pd.DataFrame, list[str]]:
    """
    Extract transactions from PDF text by finding dated lines with
    dollar amounts, using section headers to determine sign (credit/debit).

    Handles multiple date formats:
      - Full dates: MM/DD/YYYY or MM/DD/YY  (checking/savings statements)
      - Short numeric: MM/DD [MM/DD]        (BofA CC, Citi CC, Chase)
      - Named month:  Mon DD Mon DD         (Barclay CC)
    """
    errors: list[str] = []
    rows: list[dict] = []

    # Current section sign: 1 for credits, -1 for debits, 0 for unknown
    sign = 0
    stmt_year = _infer_pdf_year(pdf)
    current_year = stmt_year

    # For statements spanning two calendar years (e.g. Dec 2025 – Jan 2026),
    # short dates like "12/27" need the previous year, not stmt_year.
    closing_month = _infer_closing_month(pdf)

    # Stop sections (DAILY ENDING BALANCE, SHOP WITH POINTS, etc.) disable
    # transaction parsing until a credit/debit section header re-enables it.
    parsing_active = True

    for page in pdf.pages:
        text = page.extract_text() or ""
        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue

            # ── 1. Try transaction match FIRST ────────────────────────────
            # This prevents descriptions containing words like "PAYMENTS"
            # from being misidentified as section headers.
            # Only match transactions when parsing is active (not in a
            # stop section like "SHOP WITH POINTS ACTIVITY").

            if parsing_active:
                # Pattern A: full date — MM/DD/YY(YY)
                m = _DATE_LINE_RE.match(stripped)
                if m:
                    date_str, desc, amt_str = m.group(1), m.group(2), m.group(3)
                    desc_lower = desc.lower()
                    if "beginning balance" in desc_lower or "ending balance" in desc_lower:
                        continue
                    date_str = _normalise_pdf_date(date_str)
                    amount = _parse_pdf_amount(amt_str, sign)
                    rows.append({
                        "date": date_str,
                        "description_raw": desc.strip(),
                        "amount": str(amount),
                    })
                    current_year = date_str.split("/")[-1]
                    continue

                # Pattern B: short numeric — MM/DD [MM/DD] (credit card statements)
                m = _SHORT_DATE_LINE_RE.match(stripped)
                if m:
                    date_short, desc, amt_str = m.group(1), m.group(2), m.group(3)
                    year = _year_for_short_date(date_short, stmt_year, closing_month)
                    date_str = f"{date_short}/{year}"
                    amount = _parse_pdf_amount(amt_str, sign)
                    rows.append({
                        "date": date_str,
                        "description_raw": desc.strip(),
                        "amount": str(amount),
                    })
                    continue

                # Pattern C: named month — Mon DD Mon DD (Barclay)
                m = _MONTH_DATE_LINE_RE.match(stripped)
                if m:
                    month_day, desc, amt_str = m.group(1), m.group(2), m.group(3)
                    year = _year_for_short_date(
                        f"{_MONTH_NUMS.get(month_day.split()[0].lower(), '01')}/01",
                        stmt_year, closing_month,
                    )
                    date_str = _month_name_to_date(month_day, year)
                    amount = _parse_pdf_amount(amt_str, sign)
                    rows.append({
                        "date": date_str,
                        "description_raw": desc.strip(),
                        "amount": str(amount),
                    })
                    continue

                # Check line: checknum MM-DD
                m = _CHECK_LINE_RE.match(stripped)
                if m:
                    check_num, date_short, amt_str = m.group(1), m.group(2), m.group(3)
                    amount = -abs(_parse_pdf_amount(amt_str, sign))  # checks always debits
                    month, day = date_short.split("-")
                    date_str = f"{month}/{day}/{current_year}"
                    rows.append({
                        "date": date_str,
                        "description_raw": f"Check #{check_num}",
                        "amount": str(amount),
                    })
                    continue

            # ── 2. Check section headers (only short, non-transaction lines)
            # Long boilerplate (deposit agreements, disclosures) can contain
            # words like "deposits" and "withdrawals" — ignore those.
            if len(stripped) <= 70:
                upper = stripped.upper()
                if any(s in upper for s in _STOP_SECTIONS):
                    sign = 0
                    parsing_active = False
                    continue
                if any(s in upper for s in _CREDIT_SECTIONS):
                    sign = 1
                    parsing_active = True
                    continue
                if any(s in upper for s in _DEBIT_SECTIONS):
                    sign = -1
                    parsing_active = True
                    continue

    if not rows:
        return pd.DataFrame(), errors + ["No transaction lines found in PDF text"]

    df = pd.DataFrame(rows)
    return df, errors


def _table_data_looks_valid(df: pd.DataFrame) -> bool:
    """
    Sanity-check table-extracted data: at least 30% of rows should have a
    parseable date AND a parseable numeric amount.  This catches junk tables
    (payment coupons, comparison charts) that happen to have columns named
    "date" or "amount" but contain NaN / empty / non-date text.
    """
    date_col = "date" if "date" in df.columns else None
    amt_col = "amount" if "amount" in df.columns else None
    if not date_col:
        return False

    _date_like = re.compile(r"\d{1,2}[/\-]\d{1,2}([/\-]\d{2,4})?")
    good = 0
    for _, row in df.iterrows():
        d = str(row.get(date_col, "")).strip()
        if not d or d.lower() == "nan":
            continue
        if not _date_like.search(d):
            continue
        # If we have an amount column, check that too
        if amt_col:
            a = str(row.get(amt_col, "")).strip()
            if not a or a.lower() == "nan":
                continue
            cleaned = re.sub(r"[^\d.\-]", "", a)
            try:
                float(cleaned)
            except ValueError:
                continue
        good += 1

    return good >= max(2, len(df) * 0.3)


def _table_to_df(table: list[list]) -> Optional[pd.DataFrame]:
    if len(table) < 2:
        return None
    headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(table[0])]
    rows = [
        [str(c).strip() if c else "" for c in row]
        for row in table[1:]
        if any(c for c in row)
    ]
    return pd.DataFrame(rows, columns=headers) if rows else None


# ── Normalization ─────────────────────────────────────────────────────────────

def normalize_transactions(
    df: pd.DataFrame,
    source_filename: str = "",
    profile: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Convert a raw parsed DataFrame into the canonical transaction schema.

    Returns a clean DataFrame ready for deduplication and DB insertion.
    Rows with unparseable dates or amounts are silently dropped.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    date_fmt = profile.get("date_format") if profile else None
    amount_negate = bool(profile.get("amount_negate")) if profile else False

    out = pd.DataFrame()
    out["date"]            = df["date"].apply(lambda v: _parse_date(v, date_fmt))
    out["description_raw"] = df["description_raw"].fillna("").str.strip()
    out["amount"]          = df["amount"].apply(_parse_amount)

    if amount_negate:
        out["amount"] = -out["amount"]

    n = len(df)
    out["merchant_raw"]       = df.get("merchant_raw",  pd.Series([""] * n, dtype=str)).fillna("").str.strip()
    out["merchant_canonical"] = ""
    out["currency"]           = df.get("currency",      pd.Series(["USD"] * n, dtype=str)).fillna("USD").str.strip()
    out["account"]            = df.get("account",       pd.Series([""] * n, dtype=str)).fillna("").str.strip()
    out["category"]           = ""
    out["confidence"]         = None
    out["notes"]              = ""
    out["source_filename"]    = source_filename
    out["imported_at"]        = now_iso

    out["transaction_id"] = out.apply(
        lambda r: compute_transaction_id(r["date"] or "", r["amount"] or 0.0, r["description_raw"]),
        axis=1,
    )

    # Drop rows where core fields couldn't be parsed
    out = out.dropna(subset=["date", "amount"])
    out = out[out["amount"].apply(lambda x: isinstance(x, (int, float)))]
    return out.reset_index(drop=True)


def _parse_date(value: str, fmt: Optional[str] = None) -> Optional[str]:
    """Return ISO-8601 date string (YYYY-MM-DD) or None."""
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    candidates = [fmt] if fmt else [
        "%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y",
        "%b %d, %Y", "%B %d, %Y", "%d-%b-%Y", "%Y%m%d",
        "%m-%d-%Y", "%d %b %Y", "%d %B %Y",
    ]
    for f in candidates:
        try:
            return datetime.strptime(value, f).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _parse_amount(value) -> Optional[float]:
    """Parse a messy amount string (currency symbols, parens) to float."""
    if not isinstance(value, str):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    value = value.strip()
    # Parentheses indicate negative: (47.32) → -47.32
    negative = value.startswith("(") and value.endswith(")")
    cleaned = re.sub(r"[^\d.\-]", "", value.replace("(", "-").replace(")", ""))
    try:
        result = float(cleaned)
        return -abs(result) if negative and result > 0 else result
    except ValueError:
        return None


# ── Deduplication & commit ────────────────────────────────────────────────────

def deduplicate(df: pd.DataFrame, entity: str) -> tuple[pd.DataFrame, int]:
    """
    Remove rows whose transaction_id already exists in the DB.

    Returns (new_rows_df, skipped_count).
    """
    if df.empty:
        return df, 0

    conn = get_connection(entity)
    try:
        existing = {r[0] for r in conn.execute("SELECT transaction_id FROM transactions").fetchall()}
    finally:
        conn.close()

    mask = ~df["transaction_id"].isin(existing)
    mask &= ~df["transaction_id"].duplicated(keep="first")
    new_df = df[mask].copy()
    return new_df, len(df) - len(new_df)


def commit_transactions(df: pd.DataFrame, entity: str) -> tuple[int, int]:
    """
    Deduplicate and insert transactions.  Returns (inserted, skipped).
    """
    new_df, skipped = deduplicate(df, entity)
    if new_df.empty:
        return 0, skipped

    cols = [
        "transaction_id", "date", "description_raw", "merchant_raw",
        "merchant_canonical", "amount", "amount_cents", "currency", "account",
        "category", "confidence", "notes", "source_filename", "imported_at",
    ]
    for c in cols:
        if c not in new_df.columns:
            new_df[c] = None

    # Populate amount_cents from amount (integer cents, no floating-point math downstream)
    new_df["amount_cents"] = new_df["amount"].apply(
        lambda a: round(a * 100) if a is not None else None
    )

    sql = (
        f"INSERT OR IGNORE INTO transactions ({','.join(cols)}) "
        f"VALUES ({','.join(['?']*len(cols))})"
    )
    conn = get_connection(entity)
    try:
        conn.executemany(sql, new_df[cols].values.tolist())
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return len(new_df), skipped


def save_upload(file_bytes: bytes, filename: str) -> Path:
    """Persist an uploaded file to DATA_DIR/uploads/ and return the path."""
    dest = get_data_dir() / "uploads" / filename
    dest.write_bytes(file_bytes)
    return dest
