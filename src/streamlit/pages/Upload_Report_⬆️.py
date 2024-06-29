from time import sleep

import streamlit as st
from src.streamlit.pages.helpers.helpers import menu, menu_metrics
from src.ingestion.report import Report
import os

st.set_page_config(page_title="Upload Annual Report", page_icon=":page_with_curl:")

menu()

if "processed" not in st.session_state:
    st.session_state.processed = []

uploaded_files = st.file_uploader(
    label="Upload annual report in JSON format. It should be in the form <company_name>_<year>.json",
    type="json",
    accept_multiple_files=True,
)

# check if file has the right naming convention <company_name>_<year>.json
if uploaded_files:
    for file_path in uploaded_files:
        if not file_path.name.endswith(".json"):
            st.error("File must be in JSON format")
            st.stop()
        if len(file_path.name.split("_")) != 2:
            st.error("File name must be in the form <company_name>_<year>.json")
            st.stop()

if len(uploaded_files) > 0:
    with st.spinner("Uploading and Extracting Metrics"):
        for file in uploaded_files:
            # create file in temp directory
            temp_file_path = f"temp/{file.name}"
            if not os.path.exists("temp"):
                os.makedirs("temp")
            with open(temp_file_path, "wb") as f:
                f.write(file.getvalue())
            report = Report.from_json(temp_file_path)
            report.get_kpis()
            os.remove(temp_file_path)
            st.session_state.processed.append(report)
            menu_metrics()
