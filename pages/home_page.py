import streamlit as st

def home_page():
    st.title("Sentiment Analysis App")
    
    with st.expander("About the App"):
        st.write("""
        This app provides comprehensive sentiment analysis using advanced techniques.
        You can upload documents, analyze sentiments, visualize results, and download reports.
        Features include word clouds, detailed sentiment reports, and more!
        Navigate through the sidebar to explore.
        """)
        
    st.write("Navigate to the Generate Report or Word Cloud pages to get started!")
