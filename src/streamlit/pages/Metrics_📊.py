from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from src.ingestion.report import Report
from src.llm_agents.rag.agent import RAGAgent
from src.streamlit.pages.helpers.helpers import menu

st.set_page_config(
    page_title="Reports",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

def capitalize(s):
    return ' '.join(word.capitalize() for word in s.split())

def metric_data(df, metric):
    df_tmp = df.query(f"question.str.contains('{metric}')")

    if len(df_tmp) == 0:
        return None
    
    value = df_tmp.value.values[0]
    base = df_tmp.base.values[0]
    unit = df_tmp.unit.values[0]

    if base == "Million":
        base = "m"
    elif base == "Billion":
        base = "b"
    elif base == "Trillion":
        base = "t"

    if unit == "USD":
        unit = "$"
    elif unit == "EUR":
        unit = "€"

    formatted_value = "{:,}".format(int(value)).replace(",", "'")

    if base == "m":
        value = value * 1e6
    elif base == "b":
        value = value * 1e9


    return f"{unit}{formatted_value}{base}", value, base, unit
    

def get_additional_data(ticker: str):
    FMP_API_KEY="GhbGMbjG4ZtktR7ayXypbMZkKzHgQ910"
    #!/usr/bin/env python
    try:
        # For Python 3.0 and later
        from urllib.request import urlopen
    except ImportError:
        # Fall back to Python 2's urllib2
        from urllib2 import urlopen

    import json

    import certifi

    def get_jsonparsed_data(url):
        response = urlopen(url, cafile=certifi.where())
        data = response.read().decode("utf-8")
        return json.loads(data)

    url = (f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?period=annual&apikey={FMP_API_KEY}")
    st.write(get_jsonparsed_data(url))


def run_report(report: Report, container):
    container.title(f"Metrics Dashboard of **{report.company_name}** in {report.year}")
    agent = RAGAgent(report)
    df_report = report.kpis
    for _, row in df_report.iterrows():
        try:
            row["value"] = float(row["value"])
        except Exception as e:
            print(e)

    container.header("Key metrics")

    metrics = {}
    for metric in ["total revenue", "gross profit", "net income", "total assets", "total equity"]:
        res = metric_data(df_report, metric)
        if res is None:
            continue
        metrics[metric] = res

    col_metrics = container.columns(len(metrics))
    for i, (metric, value) in enumerate(metrics.items()):
        col_metrics[i].metric(capitalize(metric), value[0])

    computations = {}
    try:
        roe = round((metrics["net income"][1] / metrics["total equity"][1])*100, 1)
        computations["ROE"] = f"{roe}%"
    except Exception as e:
        computations["ROE"] = "NA"

    try:
        roe = round((metrics["net income"][1] / metrics["total assets"][1])*100, 1)
        computations["ROA"] = f"{roe}%"
    except Exception as e:
        computations["ROA"] = "NA"
    
    col_comp = container.columns(len(computations))
    for i, (metric, value) in enumerate(computations.items()):
        col_comp[i].metric(metric, value)
  

    # bar chart to show revenue by region and plot value on bar
    df_regions = df_report.query("question.str.contains('total revenue in')")
    if len(df_regions)>0:
        st.header("Revenue by region")
        _, col_region, _ = container.columns(spec=[0.2, 0.6, 0.2])

        df_regions["Region"] = df_regions.question.str.replace("What is the company's total revenue in ", "")
        df_regions.Region = df_regions.Region.str.replace("?", "")
        
        fig = px.pie(df_regions, values="value", names=df_regions.Region)\
            .update_traces(textposition="inside", texttemplate="$%{value: 0.2s}m <br> %{percent}", hole=0.4)\
            .update_layout(font_size=24, width=800, height=600, legend_title_font_size=30, legend_font_size=24)

        col_region.plotly_chart(fig)


    st.header("Sources of the KPIs")
    _, col_sources, _ = container.columns(spec=[0.2, 0.6, 0.2])
    df_sources = report.kpis.drop(
        columns=["found", "description", "acronym", "question"]
    ).rename(columns={"full_name": "KPI", "source": "Page", "value": "Value", "base": "Base", "unit": "Unit"})

    df_sources.set_index("Page", inplace=True)

    if "formula" in df_sources.columns:
        df_sources.drop(columns=["formula"], inplace=True)

    col_sources.dataframe(df_sources, use_container_width=True)

    col1, col2 = container.columns(2)

    col1.header("Quick Company Overview")
    quick_overview = agent.complete(
        "Give a company overview in a short paragraph"
    )
    col1.write(
       quick_overview
    )

    col2.header("Highlights of the year")
    highlight_of_the_year = agent.complete(
        "In a short paragraph, summarize the highlights of the year of the company."
    )
    col2.write(
        highlight_of_the_year
    )

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

    
