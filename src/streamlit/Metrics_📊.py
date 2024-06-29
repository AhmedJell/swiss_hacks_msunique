import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html
from src.streamlit.helpers.helpers import menu

st.set_page_config(
    page_title="Metrics",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

with st.sidebar:
    company_name = st.multiselect(
        options=["Company A", "Company B", "Company C"], label="Select Company"
    )
    years = st.multiselect(options=[2023, 2022, 2021], label="Select Year(s)")

    kpis = st.multiselect(label="Select KPI(s)", options=["Revenue", "Profit", "Employees"])
    
if "Revenue" in kpis:
    company = "ABB"
    st.title(f"Metrics Dashboard of **{company}**")

    col1, col2 = st.columns(2)

    col1.header("Quick Company Overview")
    col1.markdown(
        """
        ABB, headquartered in Zurich, Switzerland, was founded in 1988 through the merger of ASEA (1883) and BBC (1891). It operates globally with a presence in over 100 countries, primarily across Europe, the Americas, Asia, the Middle East, and Africa. ABB specializes in electrification, motion, process automation, and robotics & discrete automation sectors. The company’s strategy focuses on leveraging its technological leadership to drive sustainability and resource efficiency. ABB is listed on the SIX Swiss Exchange and Nasdaq Stockholm.
        """
    )

    col2.header("Highlights of the year")
    col2.markdown(
        """
        In 2023, ABB invested \$170 million in the US and \$280 million in Sweden to expand capacity, unveiled the ABB Dynafin™ for ships, delisted from the NYSE, updated its Code of Conduct, and completed the $505 million sale of its Power Conversion division.
        """
    )

    st.header("Key metrics")
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    col_mt1, col_mt2, col_mt3, col_mt4, col_mt5 = st.columns(5)

    col_m1.metric("Total Revenue", "$32.2m", "9.5%")
    col_m2.metric("Gross Profits", "$11.m", "15.0%")
    col_m3.metric("Net Income", "$3.7m", "51.3%")
    col_m4.metric("Total Assets", "$40.2m", "5.7%")
    col_m5.metric("Total equity", "$13.4m", "3.6%")

    col_mt1.metric("ROE", "$32.2m", "9.5%")
    col_mt2.metric("ROA", "$11.m", "15.0%")
    if "If financial instution":

        col_mt3.metric("EBITDA", "$5'603m", "43.5%")
        col_mt4.metric("EBIT", "$4,871m", "46.0%")

    st.markdown("The company shows strong financial performance with a total revenue of $32.2m (up 9.5%) and a net income of $3.7m (up 51.3%). Total assets are $40.2m (up 5.7%) and total equity is $13.4m (up 3.6%).")

    col_c1, col_c2 = st.columns(spec=[0.4, 0.6])
    col_c1.header("Stock ticker from past 12 months")
    ticker = yf.Ticker("ABBN.SW")
    hist = ticker.history(period="1y")

    col_c1.line_chart(hist["Close"])

    col_c2.header("Revenue by region")
    revenue_by_region = {
        "revenues_by_geography": [
            {
                "Region": "Europe",
                "revenues": 11568,
                "growth": "12%",
                "comparable_growth": "14%"
            },
            {
                "Region": "The Americas",
                "revenues": 11090,
                "growth": "16%",
                "comparable_growth": "18%"
            },
            {
                "Region": "Asia, Middle East, and Africa",
                "revenues": 9577,
                "growth": "0%",
                "comparable_growth": "8%"
            }
        ],
        "total_group_revenues": 32235,
        "overall_growth": "9%",
        "overall_comparable_growth": "14%"
    }

    # bar chart to show revenue by region and plot value on bar
    df = pd.DataFrame(revenue_by_region["revenues_by_geography"]).set_index("Region")
    fig = px.pie(df, values="revenues", names=df.index, title="Revenue by region").update_traces(textposition="inside", texttemplate="$%{value: 0.2s}m <br> %{percent}", hole=0.4)
    col_c2.plotly_chart(fig)
