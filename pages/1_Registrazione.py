import streamlit as st
import pandas as pd
import datetime
import secrets
import string
from lib.google_sheet import get_sheet_by_name
from lib.style import apply_custom_style

# ✅ Configura pagina
st.set_page_config(page_title="Bionic 4.0 - Registrazione", layout="wide")

# ✅ Verifica login
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Accesso negato. Torna alla pagina principale.")
    st.stop()

# ✅ Applica stile grafico
apply_custom_style()

# ✅ Genera un ID univoco da usare come "nome" del partecipante
def genera_id_univoco(lunghezza=16):
    caratteri = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caratteri) for _ in range(lunghezza))

# ✅ Se non già presente, genera e controlla che sia unico nel foglio
if "id_partecipante" not in st.session_state:
    try:
        foglio_partecipanti = get_sheet_by_name("Dati_Partecipante", "Partecipanti")
        esistenti = [r[3] for r in foglio_partecipanti.get_all_values()[1:]]  # colonna Nome (indice 3)

        nuovo_id = genera_id_univoco()
        while nuovo_id in esistenti:
            nuovo_id = genera_id_univoco()

        st.session_state["id_partecipante"] = nuovo_id
    except Exception as e:
        st.error("❌ Errore durante la generazione dell'ID partecipante.")
        st.text(f"Dettaglio: {e}")
        st.stop()

# ✅ Titolo
st.markdown('<div class="header">🏠 Benvenuto nella dashboard di Bionic 4.0</div>', unsafe_allow_html=True)
st.markdown("### 📝 Inserisci le tue informazioni per partecipare al workshop:")

# ✅ Mostra l’ID partecipante all’utente
st.info(f"🔑 Il tuo codice identificativo è: `{st.session_state['id_partecipante']}`\nSalvalo per eventuali riferimenti futuri.")

# ✅ Carica le tavole rotonda attive da Google Sheet
try:
    foglio_attivo = get_sheet_by_name("Dati_Partecipante", "Tavola Rotonda Attiva")
    dati_attivi = pd.DataFrame(foglio_attivo.get_all_records())

    # ✅ Filtra le righe non vuote nella colonna "Tavola Rotonda Attiva"
    opzioni_tavola = dati_attivi["Tavola Rotonda Attiva"].dropna().unique().tolist()

    if not opzioni_tavola:
        st.warning("⚠️ Nessuna tavola rotonda attiva trovata.")
        opzioni_tavola = ["(nessuna disponibile)"]
except Exception as e:
    st.error("❌ Errore nel caricamento delle tavole rotonda attive.")
    st.text(f"Dettaglio: {e}")
    opzioni_tavola = ["(errore di connessione)"]

# ✅ FORM
with st.form("user_info_form"):
    tavola_rotonda = st.selectbox("🔘 Tavola rotonda", opzioni_tavola)
    eta = st.number_input("🎂 Età", min_value=16, max_value=100, step=1)
    professione = st.text_input("💼 Professione")
    ruolo = st.selectbox("🎭 Qual è il tuo ruolo in questo progetto?", [
        "Cittadino interessato", "Tecnico/Esperto", "Rappresentante istituzionale", "Studente", "Altro"
    ])
    formazione = st.text_input("🎓 Formazione o background (facoltativo)", placeholder="Esempio: Architettura, Economia, Informatica...")

    ambito = st.selectbox("🌱 Qual è il tuo principale ambito di interesse?", [
        "Urbanistica", "Tecnologia e digitale", "Transizione ecologica",
        "Inclusione sociale", "Economia e lavoro", "Cultura e creatività"
    ])
    esperienza = st.radio("🧭 Hai già partecipato ad altri progetti partecipativi?", ["Sì", "No"])
    coinvolgimento = st.slider("📍 Quanto ti senti coinvolto/a nella vita del tuo territorio?", 0, 10, 5)
    conoscenza = st.slider("📚 Quanto conosci il tema di questa tavola rotonda?", 0, 10, 5)
    motivazione = st.text_area("🗣️ Cosa ti ha spinto a partecipare a questo tavolo di lavoro?", placeholder="Scrivi liberamente...")
    obiettivo = st.text_area("🎯 Cosa ti piacerebbe ottenere da questo incontro?", placeholder="Ad esempio: conoscere persone, contribuire a un'idea, essere aggiornato...")
    visione = st.radio("🔍 Ti senti più orientato a...", ["Valori tradizionali", "Innovazione", "Equilibrio tra i due"])
    valori = st.multiselect("❤️ Quali di questi valori senti più vicini?", [
        "Innovazione", "Collaborazione", "Responsabilità", "Tradizione", "Trasparenza", "Inclusione"
    ])
    canale = st.selectbox("📡 Come preferisci essere aggiornato su iniziative pubbliche?", [
        "Email", "Social", "Eventi pubblici", "Siti ufficiali", "Bacheche locali"
    ])

    submitted = st.form_submit_button("Invia")

# ✅ Salvataggio dati
if submitted:
    if not all([professione, ruolo, ambito, motivazione, obiettivo, valori]):
        st.error("⚠️ Compila tutti i campi obbligatori prima di continuare.")
    else:
        dati_utente = {
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Utente": st.session_state.get("username", "anonimo"),
            "Tavola rotonda": tavola_rotonda,
            "Nome": st.session_state["id_partecipante"],  # usa ID generato
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

        try:
            sheet = get_sheet_by_name("Dati_Partecipante", "Partecipanti")
            sheet.append_row(list(dati_utente.values()))
            st.session_state["tavola_rotonda"] = tavola_rotonda
            st.success("✅ Dati salvati con successo!")
            st.switch_page("pages/2_Persona_Model.py")
        except Exception as e:
            st.error("❌ Errore durante il salvataggio dei dati.")
            st.text(f"Dettaglio: {e}")



