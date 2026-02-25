"""Shared helpers imported by every Streamlit page."""

import sys
from pathlib import Path

# Ensure project root is on sys.path regardless of cwd
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from core.db import init_db, get_connection


# ── Entity mapping ────────────────────────────────────────────────────────────
# Display name → database key
_ENTITY_MAP = {"Personal": "personal", "BFM": "company"}
_ENTITY_COLORS = {
    "Personal": {"accent": "#30d158", "accent_hover": "#2ab84d", "glow": "rgba(48,209,88,0.25)"},
    "BFM":      {"accent": "#0a84ff", "accent_hover": "#0974de", "glow": "rgba(10,132,255,0.25)"},
}


def page_config(title: str = "Expense Tracker") -> None:
    """Call once at the top of each page (before any other st.* call)."""
    st.set_page_config(
        page_title=title,
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def entity_selector() -> tuple[str, str]:
    """
    Render a prominent entity toggle at the top-left of the page.

    Returns (display_name, db_key) where:
      - display_name is "Personal" or "BFM"
      - db_key is "personal" or "company" (for DB operations)
    """
    col_toggle, _ = st.columns([2, 5])
    with col_toggle:
        choice = st.radio(
            "Entity",
            list(_ENTITY_MAP.keys()),
            horizontal=True,
            key="entity",
            label_visibility="collapsed",
        )

    db_key = _ENTITY_MAP[choice]
    theme = _ENTITY_COLORS[choice]
    accent = theme["accent"]
    accent_hover = theme["accent_hover"]
    glow = theme["glow"]

    init_db(db_key)

    # ── Inject entity-aware theme CSS ─────────────────────────────────────────
    st.markdown(f"""
    <style>
    /* ── Entity theme: {choice} ──────────────────────────────────────────── */

    /* Colored accent bar at top of app */
    [data-testid="stHeader"] {{
        border-top: 4px solid {accent};
    }}

    /* Style the entity radio as a prominent segmented control */
    div[data-testid="stRadio"] > div {{
        gap: 0 !important;
    }}
    div[data-testid="stRadio"] > div > label {{
        padding: 0.45rem 1.4rem !important;
        border: 2px solid {accent} !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
        background: transparent !important;
    }}
    div[data-testid="stRadio"] > div > label:first-child {{
        border-radius: 8px 0 0 8px !important;
        border-right: 1px solid {accent} !important;
    }}
    div[data-testid="stRadio"] > div > label:last-child {{
        border-radius: 0 8px 8px 0 !important;
        border-left: 1px solid {accent} !important;
    }}
    /* Active / selected option */
    div[data-testid="stRadio"] > div > label[data-checked="true"],
    div[data-testid="stRadio"] > div > label:has(input:checked) {{
        background: {accent} !important;
        color: white !important;
        box-shadow: 0 0 12px {glow} !important;
    }}
    /* Hide the default radio dot */
    div[data-testid="stRadio"] > div > label > div:first-child {{
        display: none !important;
    }}

    /* ── Primary buttons ─────────────────────────────────────────────────── */
    button[kind="primary"],
    [data-testid="baseButton-primary"] {{
        background-color: {accent} !important;
        border-color: {accent} !important;
    }}
    button[kind="primary"]:hover,
    [data-testid="baseButton-primary"]:hover {{
        background-color: {accent_hover} !important;
        border-color: {accent_hover} !important;
    }}

    /* ── Form submit buttons ─────────────────────────────────────────────── */
    button[kind="primaryFormSubmit"],
    [data-testid="baseButton-primaryFormSubmit"] {{
        background-color: {accent} !important;
        border-color: {accent} !important;
    }}
    button[kind="primaryFormSubmit"]:hover,
    [data-testid="baseButton-primaryFormSubmit"]:hover {{
        background-color: {accent_hover} !important;
        border-color: {accent_hover} !important;
    }}

    /* ── Tabs ─────────────────────────────────────────────────────────────── */
    button[data-baseweb="tab"][aria-selected="true"] {{
        border-bottom-color: {accent} !important;
        color: {accent} !important;
    }}

    /* ── Progress bars ────────────────────────────────────────────────────── */
    [data-testid="stProgress"] > div > div > div {{
        background-color: {accent} !important;
    }}

    /* ── Metric values ────────────────────────────────────────────────────── */
    [data-testid="stMetricValue"] {{
        color: {accent} !important;
    }}

    /* ── Checkboxes & toggles ─────────────────────────────────────────────── */
    input[type="checkbox"]:checked + label > span,
    [data-baseweb="checkbox"] input:checked ~ div {{
        background-color: {accent} !important;
        border-color: {accent} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    return choice, db_key


def entity_display(db_key: str) -> str:
    """Convert a DB key ('personal' or 'company') to its display name."""
    _REVERSE = {v: k for k, v in _ENTITY_MAP.items()}
    return _REVERSE.get(db_key, db_key.title())


def get_categories(entity: str) -> list[str]:
    """Return sorted list of category names for the given entity."""
    conn = get_connection(entity.lower())
    try:
        rows = conn.execute("SELECT name FROM categories ORDER BY name").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()
