import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Test Gemini API", layout="centered")
st.title("🔍 Test Connessione Gemini API")

# ✅ Carica la chiave in modo sicuro
try:
    if "gemini" in st.secrets and "api_key" in st.secrets["gemini"]:
        api_key = st.secrets["gemini"]["api_key"]
    elif "GEMINI_API_KEY" in os.environ:
        api_key = os.environ["GEMINI_API_KEY"]
    else:
        st.error("❌ Nessuna chiave API trovata. Inseriscila in st.secrets o come variabile d'ambiente.")
        st.stop()

    # ✅ Configura Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    # Test prompt
    prompt = "Scrivi una frase motivazionale sul cambiamento urbano."
    with st.spinner("Interrogando Gemini..."):
        response = model.generate_content(prompt)

    st.success("✅ Connessione riuscita e risposta ottenuta!")
    st.markdown("**Risposta generata:**")
    st.markdown(response.text)

except Exception as e:
    st.error("❌ Errore durante la connessione con Gemini API:")
    st.exception(e)
