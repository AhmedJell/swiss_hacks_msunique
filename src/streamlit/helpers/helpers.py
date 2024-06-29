import streamlit as st

def menu():
    st.sidebar.page_link(
        "pages/Chatbot.py", label="Chatbot", icon="🤖"
    )
    st.sidebar.page_link(
        "pages/Upload_Report_⬆️.py", label="Upload Report", icon="⬆️"
    )
    if "processed" in st.session_state:
        st.sidebar.page_link(
            "Metrics_📊.py", label="Metrics", icon="📊"
        )