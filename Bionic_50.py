import streamlit as st
import base64
from utils.auth import check_login  # check_login restituisce (success, role)

st.set_page_config(page_title="Bionic 4.0", layout="wide")

# 🌄 Funzione per impostare lo sfondo
def set_background(image_path):
    with open(image_path, "rb") as img_file:
        bg_image = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bg_image}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Imposta lo sfondo
set_background("assets/bg.jpg")

# 🔁 Stato sessione
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# 🔐 Form login
if not st.session_state.logged_in:
    st.markdown("## 🔐 Login")
    username = st.text_input("Username").strip()
    password = st.text_input("Password", type="password").strip()

    if st.button("Login"):
        success, role = check_login(username, password)
        if success:
            st.session_state.logged_in = True
            st.session_state.role = role
        else:
            st.error("❌ Credenziali non valide")

# ✅ Dopo login
if st.session_state.logged_in:
    ruolo = st.session_state.role
    st.success(f"✅ Login effettuato come **{ruolo}**")

    # Pagina sempre disponibile
    st.page_link("pages/1_Home.py", label="🏠 Home")

    # Accesso differenziato
    if ruolo == "bionic":
        st.page_link("pages/2_Stakeholder.py", label="📊 Stakeholder")
        st.page_link("pages/4_Matrice AHP.py", label="📐 Matrice AHP")
    elif ruolo == "responsabile":
        st.page_link("pages/3_Valutazione Verde.py", label="🌳 Valutazione Verde")
        st.page_link("pages/5_Valutazione Parchi.py", label="🗺️ Valutazione Parchi")

