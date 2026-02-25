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
    "Personal": {"accent": "#30d158"},
    "BFM":      {"accent": "#0a84ff"},
}


def entity_selector() -> tuple[str, str]:
    """
    Render entity toggle in the sidebar and inject theme CSS.

    Called once in the app router (main.py) BEFORE st.navigation()
    so the toggle appears above the page links.

    Returns (display_name, db_key).
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
    /* ── Reduce sidebar top padding ──────────────────────────────────────── */
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 0.4rem !important;
    }}

    /* ── Apple-style segmented control ───────────────────────────────────── */

    /* Outer capsule — force horizontal row, full sidebar width */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div {{
        display: flex !important;
        flex-direction: row !important;
        background: #1c1c1e !important;
        border-radius: 8px !important;
        padding: 2px !important;
        gap: 0 !important;
        width: 100% !important;
    }}
    /* Kill the radio dot — remove from flow entirely */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div > label > div:first-child {{
        position: absolute !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        opacity: 0 !important;
    }}
    /* Each segment — equal width, no border */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div > label {{
        flex: 1 !important;
        text-align: center !important;
        padding: 0.4rem 1rem !important;
        margin: 0 !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        color: rgba(255,255,255,0.85) !important;
        background: transparent !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
    }}
    /* Center the text inside — override any inner element alignment */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div > label * {{
        text-align: center !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }}
    /* Active segment — filled background */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div > label:nth-of-type({1 if choice == "Personal" else 2}) {{
        background: #38383a !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    return choice, db_key


def get_entity() -> tuple[str, str]:
    """
    Read the current entity from session state (no rendering).

    Called by individual page files. Returns (display_name, db_key).
    """
    choice = st.session_state.get("entity", "Personal")
    db_key = _ENTITY_MAP.get(choice, "personal")
    init_db(db_key)
    return choice, db_key


def get_accent() -> str:
    """Return the accent color hex for the current entity."""
    choice = st.session_state.get("entity", "Personal")
    return _ENTITY_COLORS.get(choice, {}).get("accent", "#30d158")


def entity_display(db_key: str) -> str:
    """Convert a DB key ('personal' or 'company') to its display name."""
    _REVERSE = {v: k for k, v in _ENTITY_MAP.items()}
    return _REVERSE.get(db_key, db_key.title())


@st.cache_data(ttl=120)
def get_categories(entity: str) -> list[str]:
    """Return sorted list of category names for the given entity (cached 2 min)."""
    conn = get_connection(entity.lower())
    try:
        rows = conn.execute("SELECT name FROM categories ORDER BY name").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


@st.cache_data(ttl=120)
def get_subcategories(entity: str, category: str) -> list[str]:
    """Return subcategory names for a given category (cached 2 min). Always includes 'Unknown'."""
    conn = get_connection(entity.lower())
    try:
        rows = conn.execute(
            "SELECT name FROM subcategories WHERE category_name = ? ORDER BY name",
            (category,),
        ).fetchall()
        subs = [r[0] for r in rows]
        if "Unknown" not in subs:
            subs.append("Unknown")
        return subs
    except Exception:
        return ["Unknown"]
    finally:
        conn.close()
