"""Shared helpers imported by every Streamlit page."""

import sys
from pathlib import Path

# Ensure project root is on sys.path regardless of cwd
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from core.db import init_db, get_connection


def page_config(title: str = "Expense Tracker") -> None:
    """Call once at the top of each page (before any other st.* call)."""
    st.set_page_config(
        page_title=title,
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def entity_selector() -> str:
    """
    Render a sidebar entity selector and return the chosen entity string.

    Also ensures the DB is initialized for the selected entity.
    """
    with st.sidebar:
        st.selectbox(
            "Entity",
            ["Personal", "Company"],
            key="entity",
            help="Switch between Personal and Company ledger",
        )

    entity: str = st.session_state.get("entity", "Personal")
    init_db(entity.lower())
    return entity


def get_categories(entity: str) -> list[str]:
    """Return sorted list of category names for the given entity."""
    conn = get_connection(entity.lower())
    try:
        rows = conn.execute("SELECT name FROM categories ORDER BY name").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()
