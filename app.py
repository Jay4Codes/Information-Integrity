import streamlit as st
from streamlit_option_menu import option_menu


def main():

    st.set_page_config(
        page_title="SimPPL", layout="wide", initial_sidebar_state="auto", page_icon="📄"
    )

    st.image("icon.png")
    st.title("SimPPL")
    st.subheader("Welcome to SimPPL")
    with st.expander("About this app", expanded=False):
        st.write(   
            "Intelligent"
        )

    with st.sidebar:
        st.image("icon.png")
        st.title("SimPPL")
        selected_page = option_menu(
            None,
            ["Home"],
            icons=["house"],
            menu_icon="cast",
            default_index=0,
        )

    if selected_page == "Home":
        st.markdown("##### Home")
        
        
if __name__ == "__main__":
    main()