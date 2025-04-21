# lib/style.py
import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        .stApp {
            background-image: url("https://raw.githubusercontent.com/JAPO-cyber/BionicLandscape_4.0/main/assets/bg.jpg");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
        }
        .stButton button {
            width: 100%;
            padding: 1rem;
            font-size: 1.1rem;
            border-radius: 10px;
            margin-top: 1rem;
        }
        .block-container {
            padding: 2rem 1rem 4rem 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
