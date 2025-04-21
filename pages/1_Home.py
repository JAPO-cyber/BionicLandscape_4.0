import streamlit as st
import base64

# ✅ Configurazione pagina
st.set_page_config(page_title="Bionic 4.0 - Home", layout="wide")

# ✅ Blocco accesso se non loggato
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Accesso negato. Torna alla pagina principale.")
    st.switch_page("Bionic_50.py")

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

# ✅ Contenuto della pagina
st.title("🏠 Benvenuto nella dashboard di Bionic 4.0")
st.markdown("### 📝 Inserisci le tue informazioni per partecipare al workshop:")

with st.form("user_info_form"):
    tavola_rotonda = st.selectbox(
        "🔘 Tavola rotonda",
        [
            "Digitale e città",
            "Transizione ecologica",
            "Spazi pubblici e comunità",
            "Futuro del lavoro",
            "Cultura e creatività",
        ]
    )
    nome = st.text_input("👤 Nome")
    eta = st.number_input("🎂 Età", min_value=16, max_value=100, step=1)
    professione = st.text_input("💼 Professione")
    ruolo = st.selectbox(
        "🎭 Qual è il tuo ruolo in questo progetto?",
        ["Cittadino interessato", "Tecnico/Esperto", "Rappresentante istituzionale", "Studente", "Altro"]
    )
    formazione = st.text_input("🎓 Formazione o background (facoltativo)", placeholder="Esempio: Architettura, Economia, Informatica...")

    ambito = st.selectbox(
        "🌱 Qual è il tuo principale ambito di interesse?",
        ["Urbanistica", "Tecnologia e digitale", "Transizione ecologica", 
         "Inclusione sociale", "Economia e lavoro", "Cultura e creatività"]
    )

    esperienza = st.radio(
        "🧭 Hai già partecipato ad altri progetti partecipativi?",
        ["Sì", "No"]
    )

    coinvolgimento = st.slider(
        "📍 Quanto ti senti coinvolto/a nella vita del tuo territorio?",
        0, 10, 5
    )

    conoscenza = st.slider(
        "📚 Quanto conosci il tema di questa tavola rotonda?",
        0, 10, 5
    )

    motivazione = st.text_area(
        "🗣️ Cosa ti ha spinto a partecipare a questo tavolo di lavoro?",
        placeholder="Scrivi liberamente..."
    )

    obiettivo = st.text_area(
        "🎯 Cosa ti piacerebbe ottenere da questo incontro?",
        placeholder="Ad esempio: conoscere persone, contribuire a un'idea, essere aggiornato..."
    )

    visione = st.radio(
        "🔍 Ti senti più orientato a...",
        ["Valori tradizionali", "Innovazione", "Equilibrio tra i due"]
    )

    valori = st.multiselect(
        "❤️ Quali di questi valori senti più vicini?",
        ["Innovazione", "Collaborazione", "Responsabilità", "Tradizione", "Trasparenza", "Inclusione"]
    )

    canale = st.selectbox(
        "📡 Come preferisci essere aggiornato su iniziative pubbliche?",
        ["Email", "Social", "Eventi pubblici", "Siti ufficiali", "Bacheche locali"]
    )

    submitted = st.form_submit_button("Invia")

# ✅ Dopo l'invio
if submitted:
    dati_utente = {
        "Tavola rotonda": tavola_rotonda,
        "Nome": nome,
        "Età": eta,
        "Professione": professione,
        "Formazione": formazione,
        "Ruolo": ruolo,
        "Ambito": ambito,
        "Esperienza": esperienza,
        "Coinvolgimento": coinvolgimento,
        "Conoscenza tema": conoscenza,
        "Motivazione": motivazione,
        "Obiettivo": obiettivo,
        "Visione": visione,
        "Valori": ", ".join(valori),
        "Canale preferito": canale
    }

    # salva_su_google_sheet(dati_utente)  # Attiva quando pronto

    st.success("✅ Grazie per aver inviato le tue informazioni!")

    st.markdown("### 📊 Dati raccolti:")
    for chiave, valore in dati_utente.items():
        st.write(f"**{chiave}**: {valore}")

    # ✅ Link alla prossima pagina
    st.markdown("---")
    st.page_link("pages/2_Persona_Model.py", label="➡️ Vai a Persona Model", icon="👤")

# 🔓 Logout
st.markdown("---")
if st.button("🔓 Logout"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.switch_page("Bionic_50.py")

