import streamlit as st
from utils.auth import check_login
from lib.style import apply_custom_style

st.set_page_config(page_title="Bionic 4.0", layout="wide")

# ✅ Applica stile grafico centralizzato
apply_custom_style()

# 📌 Stato sessione
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# 🔐 Login
if not st.session_state.logged_in:
    st.markdown("## 🔐 Login")
    username = st.text_input("Username").strip()
    password = st.text_input("Password", type="password").strip()

    if st.button("Login"):
        success, role = check_login(username, password)
        if success:
            st.session_state.logged_in = True
            st.session_state.role = role

            # 🔁 Reindirizza in base al ruolo
            if role.lower() == "bionic":
                st.switch_page("pages/2_Persona_Model.py")
            else:
                st.switch_page("pages/1_Registrazione.py")
        else:
            st.error("❌ Credenziali non valide")

# 🔓 Logout + Ruolo nella sidebar
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown(f"👤 **Ruolo attuale:** {st.session_state.role}")
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()


