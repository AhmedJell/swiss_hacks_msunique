import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from src.streamlit.pages.helpers.helpers import menu
from src.ingestion.report import Report
from datetime import datetime

st.set_page_config(
    page_title="Metrics",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

def get_additional_data(ticker: str):
    FMP_API_KEY="GhbGMbjG4ZtktR7ayXypbMZkKzHgQ910"
    #!/usr/bin/env python
    try:
        # For Python 3.0 and later
        from urllib.request import urlopen
    except ImportError:
        # Fall back to Python 2's urllib2
        from urllib2 import urlopen

    import certifi
    import json

    def get_jsonparsed_data(url):
        response = urlopen(url, cafile=certifi.where())
        data = response.read().decode("utf-8")
        return json.loads(data)

    url = (f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?period=annual&apikey={FMP_API_KEY}")
    st.write(get_jsonparsed_data(url))


def run_report(report: Report, container):
    container.title(f"Metrics Dashboard of **{report.company_name}** in {report.year}")

    col1, col2 = container.columns(2)

    col1.header("Quick Company Overview")
    col1.write(
        """
        ABB, headquartered in Zurich, Switzerland, was founded in 1988 through the merger of ASEA (1883) and BBC (1891). It operates globally with a presence in over 100 countries, primarily across Europe, the Americas, Asia, the Middle East, and Africa. ABB specializes in electrification, motion, process automation, and robotics & discrete automation sectors. The company’s strategy focuses on leveraging its technological leadership to drive sustainability and resource efficiency. ABB is listed on the SIX Swiss Exchange and Nasdaq Stockholm.
        """
    )

    col2.header("Highlights of the year")
    col2.write(
        """
        In 2023, ABB invested $170 million in the US and $280 million in Sweden to expand capacity, unveiled the ABB Dynafin™ for ships, delisted from the NYSE, updated its Code of Conduct, and completed the $505 million sale of its Power Conversion division.
        """
    )

    container.dataframe(report.kpis)

    container.header("Key metrics")
    col_m1, col_m2, col_m3, col_m4, col_m5 = container.columns(5)
    col_mt1, col_mt2, col_mt3, col_mt4, col_mt5 = container.columns(5)

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

    container.write("The company shows strong financial performance with a total revenue of $32.2m (up 9.5%) and a net income of $3.7m (up 51.3%). Total assets are $40.2m (up 5.7%) and total equity is $13.4m (up 3.6%).")

    col_c1, col_c2 = container.columns(spec=[0.4, 0.6])
    col_c1.header("Stock ticker from past 12 months")
    ticker = yf.Ticker("UBSG")
    hist = ticker.history(period="1y")

    get_additional_data("UBS")

    # Transforming the data
    formatted_data = []
    for item in ticker.news:
        formatted_item = {
            'Title': item['title'],
            'Publisher': item['publisher'],
            'Type': item['type'],
            'Date': datetime.fromtimestamp(item['providerPublishTime']).strftime('%d/%m/%Y'),
            'Link': item['link']
        }
        formatted_data.append(formatted_item)

    # Creating DataFrame
    df = pd.DataFrame(formatted_data)

    # Streamlit display
    container.title('News Articles')
    container.dataframe(df,
        column_config={
            "Link": st.column_config.LinkColumn(
                "Links",
                help="The top trending Streamlit apps",
                validate="^https://[a-z]+\.streamlit\.app$",
                max_chars=100,
                display_text="https://(.*?)\.streamlit\.app"
            )},
        hide_index=True,
    )

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

if "processed" in st.session_state:
    reports = st.session_state.processed
    number_of_reports = len(reports)
else:
    number_of_reports = 0

if number_of_reports == 0:
    st.error("Please upload at least one report.")
elif number_of_reports == 1:
    run_report(reports[0], st)
elif number_of_reports == 2:
    tab_1, tab_2 = st.tabs([f"{report.company_name} {report.year}" for report in reports])
    tab_1 = run_report(reports[0], tab_1)
    tab_2 = run_report(reports[1], tab_2)
elif number_of_reports == 3:
    tab_1, tab_2, tab_3 = st.tabs([f"{report.company_name} {report.year}" for report in reports])
elif number_of_reports == 4:
    tab_1, tab_2, tab_3, tab_4 = st.tabs([f"{report.company_name} {report.year}" for report in reports])
else:
    st.error("You can only compare up to 4 reports at a time.")

    
