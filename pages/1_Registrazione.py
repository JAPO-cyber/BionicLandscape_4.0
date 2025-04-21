import streamlit as st
import base64
from lib.google_sheet import get_gspread_client
from datetime import datetime

# ✅ Blocca accesso se non loggato
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Accesso negato. Torna alla pagina principale.")
    st.stop()

# ✅ Configurazione base
st.set_page_config(page_title="Bionic 4.0 - Registrazione", layout="wide")

# ✅ Stile globale
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://raw.githubusercontent.com/JAPO-cyber/BionicLandscape_4.0/main/assets/bg.jpg");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-position: center;
    }

    .form-container {
        background-color: rgba(255, 255, 255, 0.94);
        padding: 2rem;
        border-radius: 15px;
        max-width: 900px;
        margin: 2rem auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    .stButton button {
        width: 100%;
        padding: 1rem;
        font-size: 1.1rem;
        border-radius: 10px;
        margin-top: 1rem;
    }

    .block-container {
        padding: 0rem 0.5rem 2rem 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ Contenitore visivo del form
st.markdown('<div class="form-container">', unsafe_allow_html=True)

st.title("🏠 Registrazione al workshop Bionic 4.0")
st.markdown("### 📝 Inserisci le tue informazioni per partecipare:")

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

st.markdown('</div>', unsafe_allow_html=True)

# ✅ Dopo l'invio
if submitted:
    try:
        client = get_gspread_client()
        sheet = client.open("Dati_Partecipanti").worksheet("Partecipanti")

        dati_utente = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Utente": st.session_state.get("utente", "Anonimo"),
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

        riga = list(dati_utente.values())
        sheet.append_row(riga)

        st.success("✅ Grazie per aver inviato le tue informazioni!")
        st.markdown("### 📊 Dati raccolti:")
        for chiave, valore in dati_utente.items():
            st.write(f"**{chiave}**: {valore}")

        st.markdown("---")
        st.page_link("pages/2_Persona_Model.py", label="➡️ Vai a Persona Model", icon="👤")

    except Exception as e:
        st.warning("⚠️ Errore durante il salvataggio.")
        st.text(f"Dettaglio: {e}")


