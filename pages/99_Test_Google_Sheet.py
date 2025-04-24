import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Test Gemini API", layout="centered")
st.title("🔍 Test Connessione Gemini API")

api_key = st.secrets["gemini"]["api_key"]
genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content("Scrivi una frase motivazionale sul cambiamento urbano.")
    st.success("✅ Risposta ricevuta da Gemini:")
    st.markdown(response.text)
except Exception as e:
    st.error("❌ Errore: " + str(e))
