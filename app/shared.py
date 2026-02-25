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
        page_icon="$",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def entity_selector() -> tuple[str, str]:
    """
    Render entity toggle in the sidebar, above the page navigation.

    Returns (display_name, db_key) where:
      - display_name is "Personal" or "BFM"
      - db_key is "personal" or "company" (for DB operations)
    """
    with st.sidebar:
        choice = st.radio(
            "Entity",
            list(_ENTITY_MAP.keys()),
            horizontal=True,
            key="entity",
            label_visibility="collapsed",
        )
        st.markdown("---")

    db_key = _ENTITY_MAP[choice]
    accent = _ENTITY_COLORS[choice]["accent"]

    init_db(db_key)

    # ── Inject entity-aware theme CSS ─────────────────────────────────────────
    st.markdown(f"""
    <style>
    /* ── Entity toggle styling (sidebar) ─────────────────────────────────── */

    /* Hide the default radio dot */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div > label > div:first-child {{
        display: none !important;
    }}
    /* Space between the two options */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div {{
        gap: 0.5rem !important;
    }}
    /* Base style for both options */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div > label {{
        padding: 0.35rem 1.2rem !important;
        border: 1.5px solid #444 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: #666 !important;
        background: transparent !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }}
    /* Active option — colored text + colored border, no fill */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div > label[data-checked="true"],
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div > label:has(input:checked) {{
        border-color: {accent} !important;
        color: {accent} !important;
    }}

    /* Rename "Main" to "Dashboard" in sidebar nav */
    [data-testid="stSidebarNav"] li:first-child a span {{
        font-size: 0 !important;
    }}
    [data-testid="stSidebarNav"] li:first-child a span::after {{
        content: "Dashboard";
        font-size: 14px;
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
