import streamlit as st

st.set_page_config(
    page_title="Metrics",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    company_name = st.multiselect(
        options=["Company A", "Company B", "Company C"], label="Select Company"
    )
    years = st.multiselect(options=[2019, 2020, 2021], label="Select Year(s)")

    kpis = st.multiselect(label="Select KPI(s)", options=["Revenue", "Profit", "Employees"])
    