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

# Define pages
dashboard  = st.Page("pages/0_Dashboard.py", title="Dashboard", default=True)
upload     = st.Page("pages/1_Upload.py", title="Upload")
categorize = st.Page("pages/2_Categorize.py", title="Categorize")
match      = st.Page("pages/3_Match.py", title="Match")
reports    = st.Page("pages/4_Reports.py", title="Reports")

# Hide the auto-generated nav so we can build sidebar ourselves
pg = st.navigation([dashboard, upload, categorize, match, reports], position="hidden")

# Build sidebar: entity toggle first, then page links
entity_selector()

with st.sidebar:
    st.page_link(dashboard, label="Dashboard")
    st.page_link(upload, label="Upload")
    st.page_link(categorize, label="Categorize")
    st.page_link(match, label="Match")
    st.page_link(reports, label="Reports")

pg.run()
