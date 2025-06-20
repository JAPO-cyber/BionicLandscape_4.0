import streamlit as st
from streamlit_option_menu import option_menu
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

# ✅ Menu orizzontale in alto
selected = option_menu(
    menu_title=None,
    options=["🔐 Login", "ℹ️ Info", "📄 Credits"],
    icons=["box-arrow-in-right", "info-circle", "file-earmark-text"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#f0f2f6"},
        "icon": {"color": "#2c3e50", "font-size": "18px"},
        "nav-link": {"font-size": "18px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#2980b9", "color": "white"},
    }
)

# 🔐 LOGIN PAGE
if selected == "🔐 Login":
    if not st.session_state.logged_in:
        st.subheader("🔐 Login")
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
    else:
        st.success(f"✅ Accesso effettuato come: `{st.session_state.role}`")

        with st.sidebar:
            st.markdown(f"👤 **Ruolo attuale:** `{st.session_state.role}`")
            if st.button("🔓 Logout"):
                st.session_state.logged_in = False
                st.session_state.role = None
                st.rerun()

# 📄 ALTRE PAGINE STATICHE (placeholder)
elif selected == "ℹ️ Info":
    st.title("ℹ️ Informazioni sull'app Bionic 4.0")
    st.write("Questa applicazione è stata sviluppata per il progetto Bionic Landscape.")

elif selected == "📄 Credits":
    st.title("📄 Credits")
    st.write("Progetto a cura di ... (da completare)")


