from time import sleep

import streamlit as st
from src.streamlit.helpers.helpers import menu

st.set_page_config(page_title="Upload Annual Report", page_icon=":page_with_curl:")

menu()

if "processed" not in st.session_state:
    st.session_state.processed = []

file_paths = st.file_uploader(
    label="Upload annual report in JSON format. It should be in the form <company_name>_<year>.json",
    type="json",
    accept_multiple_files=True,
)

# check if file has the right naming convention
if file_paths:
    for file_path in file_paths:
        if not file_path.name.endswith(".json"):
            st.error("Please upload a file with the .json extension")
            st.stop()

if len(file_paths) > 0:
    with st.spinner("Uploading and Extracting Metrics"):
        sleep(3)
        for file_path in file_paths:
            st.write(f"Uploading {file_path.name}...")
            st.session_state.processed.append(file_path.name)
