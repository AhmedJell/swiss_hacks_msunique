import streamlit as st
from src.streamlit.pages.helpers.helpers import menu

st.set_page_config(
    page_title="Chatbot",
    page_icon=":robot:",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

st.components.v1.iframe("http://localhost:8000", height=700)