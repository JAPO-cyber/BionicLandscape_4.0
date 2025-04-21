import streamlit as st
from utils.auth import check_login
from lib.style import set_background, set_custom_style

st.set_page_config(page_title="Bionic 4.0", layout="wide")

# 💄 Applica lo stile
set_custom_style()

# 🖼️ Imposta lo sfondo
set_background("assets/bg.jpg")

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
            st.switch_page("pages/1_Registrazione.py")
        else:
            st.error("❌ Credenziali non valide")

# 🔓 Logout
if st.session_state.logged_in:
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()


