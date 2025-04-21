import streamlit as st
import base64
from utils.auth import check_login

st.set_page_config(page_title="Bionic 4.0", layout="wide")

# 🌟 Ottimizzazione mobile: pulsanti grandi e layout full width
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
            st.experimental_rerun()
        else:
            st.error("❌ Credenziali non valide")

# ✅ Navigazione per ruolo
if st.session_state.logged_in:
    ruolo = st.session_state.role
    st.success(f"✅ Login effettuato come **{ruolo}**")

    st.markdown("### 📱 Seleziona una sezione:")

    def mobile_link(path, label):
        st.markdown(
            f"""
            <a href="/{path}" target="_self">
                <button style="width: 100%; padding: 1rem; font-size: 1.1rem; margin-bottom: 0.5rem;">{label}</button>
            </a>
            """,
            unsafe_allow_html=True
        )

    if ruolo == "bionic":
        mobile_link("pages/1_Home", "🏠 Home")
        mobile_link("pages/2_Persona Model", "👤 Persona Model")
        mobile_link("pages/3_Percezione Cittadino", "🧠 Percezione Cittadino")
        mobile_link("pages/4_Output Tavolo Rotondo", "🗣️ Output Tavolo Rotondo")
        mobile_link("pages/5_Valutazione Parchi", "🏞️ Valutazione Parchi")
        mobile_link("pages/6_Output Analisi", "📊 Analisi Finale")
        mobile_link("pages/7_Generazione Report", "📝 Generazione Report")

    elif ruolo == "responsabile":
        mobile_link("pages/1_Home", "🏠 Home")
        mobile_link("pages/3_Percezione Cittadino", "🧠 Percezione Cittadino")
        mobile_link("pages/5_Valutazione Parchi", "🏞️ Valutazione Parchi")

    # 🔓 Logout
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.experimental_rerun()


