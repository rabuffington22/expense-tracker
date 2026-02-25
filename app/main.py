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
        (upload, "ONE", "Upload from Bank/CC", "/upload"),
        (vendors, "TWO", "Upload from Vendors", "/vendors"),
        (cat_vendors, "THREE", "Categorize Vendors", "/categorize_vendors"),
        (match, "FOUR", "Match", "/match"),
        (categorize, "FIVE", "Categorize Remaining", "/categorize"),
    ]
    _SP = "\u00a0" * 6
    _links_html = ""
    for _page, _num, _label, _url in _STEPS:
        _links_html += (
            f'<a href="{_url}" target="_self" style="display:block;padding:6px 8px;'
            f'margin:2px 0;border-radius:6px;text-decoration:none;'
            f'color:rgba(250,250,250,0.9);font-size:0.875rem">'
            f'<span style="color:#98989d;font-weight:600">{_num}</span>'
            f'{_SP}{_label}</a>'
        )
    st.markdown(_links_html, unsafe_allow_html=True)

pg.run()
