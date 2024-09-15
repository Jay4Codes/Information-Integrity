import streamlit as st
import google_auth_oauthlib.flow

def google_auth():
    st.markdown("""
        <style>
        .google-login {
            background-color: #4285F4;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .google-login img {
            width: 20px;
            margin-right: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <a href="/login" class="google-login">
            <img src="/static/google_logo.png" alt="Google Logo"/> Continue with Google
        </a>
    """, unsafe_allow_html=True)
