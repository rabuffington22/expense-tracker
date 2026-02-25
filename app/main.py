"""
Expense Tracker — app router.

Run with:
    streamlit run app/main.py --server.address 127.0.0.1 --server.port 8501
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from app.shared import entity_selector

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="$",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Entity toggle — rendered BEFORE st.navigation() so it sits above page links
entity_selector()

# Page navigation
pg = st.navigation([
    st.Page("pages/0_Dashboard.py", title="Dashboard", default=True),
    st.Page("pages/1_Upload.py", title="Upload"),
    st.Page("pages/2_Categorize.py", title="Categorize"),
    st.Page("pages/3_Reports.py", title="Reports"),
])
pg.run()
