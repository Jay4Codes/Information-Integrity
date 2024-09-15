import streamlit as st
from pages.home_page import home_page
from pages.generate_report_page import generate_report_page
from pages.contact_us_page import contact_us_page
from utils.auth_helpers import google_auth
from pages.wordcloud_page import wordcloud_page

st.set_page_config(page_title="SimPPL", layout="wide", initial_sidebar_state="auto", page_icon="📄")

st.sidebar.image("static/icon.png")
page = st.sidebar.selectbox("Go to", ["Home", "Word Cloud", "Generate Report", "Contact Us"])

google_auth()

if page == "Home":
    home_page()
elif page == "Word Cloud":
    wordcloud_page()
elif page == "Generate Report":
    generate_report_page()
elif page == "Contact Us":
    contact_us_page()
