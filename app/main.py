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
dashboard   = st.Page("pages/0_Dashboard.py", title="Dashboard", default=True)
upload      = st.Page("pages/1_Upload.py", title="Upload")
vendors     = st.Page("pages/2_Vendors.py", title="Vendors")
cat_vendors = st.Page("pages/3_Categorize_Vendors.py", title="Categorize Vendors")
match       = st.Page("pages/4_Match.py", title="Match")
categorize  = st.Page("pages/5_Categorize.py", title="Categorize")
reports     = st.Page("pages/6_Reports.py", title="Reports")

# Hide the auto-generated nav so we can build sidebar ourselves
pg = st.navigation(
    [dashboard, upload, vendors, cat_vendors, match, categorize, reports],
    position="hidden",
)

# Build sidebar: entity toggle first, then page links
entity_selector()

with st.sidebar:
    st.page_link(dashboard, label="Dashboard")
    st.page_link(reports, label="Reports")
    st.markdown("---")

    _STEPS = [
        (upload, "ONE", "Upload from Bank/CC"),
        (vendors, "TWO", "Upload from Vendors"),
        (cat_vendors, "THREE", "Categorize Vendors"),
        (match, "FOUR", "Match"),
        (categorize, "FIVE", "Categorize Remaining"),
    ]
    for _page, _num, _label in _STEPS:
        st.markdown(
            f'<div style="font-family:SF Mono,Fira Code,monospace;font-size:0.7rem;'
            f'font-weight:700;letter-spacing:0.05em;opacity:0.5;'
            f'margin-bottom:-0.5rem">{_num}</div>',
            unsafe_allow_html=True,
        )
        st.page_link(_page, label=_label)

pg.run()
