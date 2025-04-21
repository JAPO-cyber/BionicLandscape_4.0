import streamlit as st

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Accesso negato. Torna alla pagina principale.")
    st.stop()

st.title("🏠 Benvenuto nella dashboard di Bionic 4.0")
