import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Test Gemini API")
st.title("🔍 Test connessione Gemini API")

# Caricamento della chiave da Streamlit secrets
api_key = st.secrets["gemini"]["api_key"]

# Configurazione del modello
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    prompt = "Scrivi una frase motivazionale sul cambiamento urbano."
    response = model.generate_content(prompt)

    st.success("✅ Connessione riuscita!")
    st.markdown(f"**Risposta generata:**\n\n{response.text}")

except Exception as e:
    st.error("❌ Errore nella connessione con Gemini API")
    st.exception(e)
