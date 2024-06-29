import streamlit as st

def menu():
    st.sidebar.page_link(
        "pages/Chatbot.py", label="Chatbot", icon="🤖"
    )
    st.sidebar.page_link(
        "pages/Upload_Report_⬆️.py", label="Upload Report", icon="⬆️"
    )
    if "processed" in st.session_state and len(st.session_state.processed) > 0:
        st.sidebar.page_link(
            "pages/Metrics_📊.py", label="Metrics", icon="📊"
        )

def menu_metrics():
    st.sidebar.page_link(
        "pages/Metrics_📊.py", label="Metrics", icon="📊"
    )