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

from app.shared import entity_selector, get_accent

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

# Build sidebar: title, entity toggle, then page links
with st.sidebar:
    _title_color = get_accent()
    st.markdown(
        f'<p style="color:{_title_color};font-weight:700;font-size:1.6rem;'
        f'margin:-0.5rem 0 0.4rem 0;letter-spacing:0.04em;">'
        f'EXPENSE TRACKER</p>',
        unsafe_allow_html=True,
    )

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
    _accent = get_accent()
    for _page, _num, _label in _STEPS:
        c_num, c_link = st.columns([1, 3])
        c_num.markdown(
            f'<span style="color:{_accent};font-weight:600;font-size:1.1rem">{_num}</span>',
            unsafe_allow_html=True,
        )
        c_link.page_link(_page, label=_label)

pg.run()
