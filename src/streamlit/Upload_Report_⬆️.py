from time import sleep

import streamlit as st

st.set_page_config(page_title="Upload Annual Report", page_icon=":page_with_curl:")

if "processed" not in st.session_state:
    st.session_state.processed = []

file_paths = st.file_uploader(
    label="Upload annual report in JSON format. It should be in the form <company_name>_<year>.json",
    type="json",
    accept_multiple_files=True,
)

if len(file_paths) > 0:
    with st.spinner("Uploading and Extracting Metrics"):
        sleep(3)
        for file_path in file_paths:
            st.write(f"Uploading {file_path.name}...")
            st.session_state.processed.append(file_path.name)
