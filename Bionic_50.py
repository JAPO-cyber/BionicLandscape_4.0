import streamlit as st
import base64
from utils.auth import check_login  # Assicurati che esista il file utils/auth.py

st.set_page_config(page_title="Bionic 4.0", layout="wide")

# Funzione per impostare lo sfondo
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
set_background("assets/bg.jpg")  # Assicurati che il file esista

# Stato di login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Form di login
if not st.session_state.logged_in:
    st.markdown("## 🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Credenziali non valide")
else:
    st.switch_page("pages/1_Home.py")  # Reindirizza alla pagina Home se già loggato
