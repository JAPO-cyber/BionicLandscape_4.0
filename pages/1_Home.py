import streamlit as st

# ✅ Blocca accesso se non loggato
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Accesso negato. Torna alla pagina principale.")
    st.stop()

# ✅ Contenuto della pagina
st.title("🏠 Benvenuto nella dashboard di Bionic 4.0")
st.markdown("### 📝 Inserisci le tue informazioni per partecipare al workshop:")
