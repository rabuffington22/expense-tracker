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
    df = pd.read_csv(path, dtype=str, skip_blank_lines=True)
    df.columns = [c.strip() for c in df.columns]

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

def parse_pdf(path: str | Path) -> tuple[pd.DataFrame, list[str]]:
    """
    Best-effort transaction extraction from a PDF bank statement.

    Returns (DataFrame, error_list).  DataFrame may be empty if no tables
    are found or pdfplumber is not installed.
    """
    try:
        import pdfplumber  # noqa: PLC0415  (optional dep)
    except ImportError:
        return pd.DataFrame(), ["pdfplumber not installed; run: pip install pdfplumber"]

    errors: list[str] = []
    chunks: list[pd.DataFrame] = []

    try:
        with pdfplumber.open(str(path)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                for tbl in page.extract_tables() or []:
                    try:
                        chunk = _table_to_df(tbl)
                        if chunk is not None and not chunk.empty:
                            chunks.append(chunk)
                    except Exception as exc:
                        errors.append(f"Page {page_num}: {exc}")
    except Exception as exc:
        return pd.DataFrame(), [f"Failed to open PDF: {exc}"]

    if not chunks:
        return pd.DataFrame(), errors + ["No extractable tables found in PDF"]

    df = pd.concat(chunks, ignore_index=True)
    df = _auto_detect_columns(df)
    return df, errors


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
        "merchant_canonical", "amount", "currency", "account",
        "category", "confidence", "notes", "source_filename", "imported_at",
    ]
    for c in cols:
        if c not in new_df.columns:
            new_df[c] = None

    sql = (
        f"INSERT OR IGNORE INTO transactions ({','.join(cols)}) "
        f"VALUES ({','.join(['?']*len(cols))})"
    )
    conn = get_connection(entity)
    try:
        conn.executemany(sql, new_df[cols].values.tolist())
        conn.commit()
    finally:
        conn.close()
    return len(new_df), skipped


def save_upload(file_bytes: bytes, filename: str) -> Path:
    """Persist an uploaded file to DATA_DIR/uploads/ and return the path."""
    dest = get_data_dir() / "uploads" / filename
    dest.write_bytes(file_bytes)
    return dest
