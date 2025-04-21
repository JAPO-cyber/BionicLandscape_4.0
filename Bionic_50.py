import streamlit as st
import base64
from utils.auth import check_login
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Bionic 4.0", layout="wide")

# 🌟 Stile mobile-friendly
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        padding: 1rem;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        border-radius: 10px;
    }
    .block-container {
        padding: 1rem 1rem 2rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# 🎨 Sfondo personalizzato
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
            switch_page("1_Home")  # Reindirizza direttamente alla pagina Home
        else:
            st.error("❌ Credenziali non valide")

# 🔓 Logout
if st.session_state.logged_in:
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()


