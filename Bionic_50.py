import streamlit as st
import base64
from utils.auth import check_login
from streamlit_extras.switch_page_button import switch_page, get_pages

st.set_page_config(page_title="Bionic 4.0", layout="wide")

# 🌟 Mobile-friendly style
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
            st.rerun()  # forza ricaricamento
        else:
            st.error("❌ Credenziali non valide")

# ✅ Dopo login: menu mobile-friendly
if st.session_state.logged_in:
    ruolo = st.session_state.role
    st.success(f"✅ Login effettuato come **{ruolo}**")

    st.markdown("### 📱 Seleziona una sezione:")

    # ✅ Funzione di navigazione con key univoche
    def mobile_link(page_name, label):
        if st.button(label, key=f"go_{page_name}"):
            switch_page(page_name)

    # 🔎 Debug (opzionale): stampa le pagine disponibili
    # st.write("DEBUG - Pagine disponibili:", get_pages("pages"))

    if ruolo == "bionic":
        mobile_link("1_Home", "🏠 Home")
        mobile_link("2_Persona_Model", "👤 Persona Model")
        mobile_link("3_Percezione_Cittadino", "🧠 Percezione Cittadino")
        mobile_link("4_Output_Tavolo_Rotondo", "🗣️ Output Tavolo Rotondo")
        mobile_link("5_Valutazione_Parchi", "🏞️ Valutazione Parchi")
        mobile_link("6_Output_Analisi", "📊 Analisi Finale")
        mobile_link("7_Generazione_Report", "📝 Generazione Report")

    elif ruolo == "responsabile":
        mobile_link("1_Home", "🏠 Home")
        mobile_link("3_Percezione_Cittadino", "🧠 Percezione Cittadino")
        mobile_link("5_Valutazione_Parchi", "🏞️ Valutazione Parchi")

    # 🔓 Logout
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()


