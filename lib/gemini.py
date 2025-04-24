import os
import streamlit as st

def get_gemini_api_key():
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    elif "GEMINI_API_KEY" in os.environ:
        return os.environ["GEMINI_API_KEY"]
    else:
        st.error("❌ Chiave API Gemini non trovata.")
        st.stop()
