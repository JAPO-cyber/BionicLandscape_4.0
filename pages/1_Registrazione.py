import streamlit as st
import pandas as pd
import datetime
import secrets
import string
from lib.google_sheet import get_sheet_by_name
from lib.style import apply_custom_style

# ─── Configura pagina ─────────────────────────────────────────────────────
st.set_page_config(page_title="Registrazione", layout="wide")

# ─── Verifica login ───────────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    st.error("❌ Accesso negato. Torna alla pagina principale.")
    st.stop()

# ─── Applica stile grafico ─────────────────────────────────────────────────
apply_custom_style()

# ─── Eredito quartiere e metodo segreti dal main ───────────────────────────
quartiere = st.session_state.get("quartiere", "")
secret_method = st.session_state.get("secret_method", "Streamlit Secrets")

# ─── Genera un ID univoco da usare come "nome" del partecipante ─────────────
def genera_id_univoco(lunghezza=16):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(lunghezza))

if "id_partecipante" not in st.session_state:
    try:
        foglio = get_sheet_by_name("Dati_Partecipante", "Partecipanti")
        existing = [r[3] for r in foglio.get_all_values()[1:]]  # colonna Nome (indice 3)
        new_id = genera_id_univoco()
        while new_id in existing:
            new_id = genera_id_univoco()
        st.session_state["id_partecipante"] = new_id
    except Exception as e:
        st.error("❌ Errore nella generazione dell'ID partecipante.")
        st.text(f"Dettaglio: {e}")
        st.stop()

# ─── Titolo e istruzioni ────────────────────────────────────────────────────
st.markdown('<div class="header">🏠 Benvenuto nella pagina di registrazione</div>', unsafe_allow_html=True)
st.markdown("### 📝 Inserisci le tue informazioni per partecipare al workshop:")
st.info(f"🔑 Il tuo codice identificativo è: `{st.session_state['id_partecipante']}`. Quartiere: {quartiere}")

# ─── Carica tavole rotonda attive ───────────────────────────────────────────
try:
    sheet_attive = get_sheet_by_name("Dati_Partecipante", "Tavola Rotonda Attiva")
    df_attive = pd.DataFrame(sheet_attive.get_all_records())
    opzioni = df_attive["Tavola Rotonda Attiva"].dropna().unique().tolist()
    if not opzioni:
        st.warning("⚠️ Nessuna tavola rotonda attiva trovata.")
        opzioni = ["(nessuna disponibile)"]
except Exception as e:
    st.error("❌ Errore nel caricamento delle tavole rotonda.")
    st.text(f"Dettaglio: {e}")
    opzioni = ["(errore di connessione)"]

# ─── FORM DATI UTENTE ───────────────────────────────────────────────────────
with st.form("user_info_form"):
    tavola = st.selectbox("🔘 Tavola rotonda", opzioni)
    eta = st.number_input("🎂 Età", min_value=16, max_value=100, step=1)
    professione = st.text_input("💼 Professione")
    ruolo = st.selectbox("🎭 Il tuo ruolo in questo progetto", [
        "Cittadino", "Tecnico comunale", "Rappresentante associazione", "Educatore ambientale"
    ])
    formazione = st.text_input(
        "🎓 Formazione o background (facoltativo)",
        placeholder="Esempio: Architettura, Economia, Informatica..."
    )
    ambito = st.selectbox("🌱 Ambito di interesse", [
        "Ambientale", "Culturale", "Sociale", "Educativo", "Urbanistico"
    ])
    esperienza = st.radio("🧭 Hai già partecipato ad altri progetti partecipativi?", ["Sì", "No"])
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
        placeholder="Ad esempio: conoscere persone, contribuire a un'idea..."
    )
    visione = st.radio("🔍 Ti senti più orientato a...", [
        "Città verde", "Comunità coesa", "Parchi per tutti", "Tecnologia al servizio del verde"
    ])
    valori = st.multiselect("❤️ Quali valori senti vicini?", [
        "Innovazione", "Collaborazione", "Responsabilità",
        "Tradizione", "Trasparenza", "Inclusione", "Sostenibilità"
    ])
    canale = st.selectbox("📡 Come preferisci essere aggiornato?", [
        "Email", "Social", "Eventi pubblici", "Sito web",
        "Bacheche locali", "Volantino", "Scuola", "Passaparola"
    ])
    submitted = st.form_submit_button("Invia")

# ─── Gestione submit ────────────────────────────────────────────────────────
if submitted:
    if not all([professione, ruolo, ambito, motivazione, obiettivo, valori]):
        st.error("⚠️ Compila tutti i campi obbligatori prima di continuare.")
    else:
        dati = {
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Utente": st.session_state.get("username", "anonimo"),
            "Quartiere": quartiere,
            "Tavola rotonda": tavola,
            "Nome": st.session_state["id_partecipante"],
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
            "Canale preferito": canale,
            "SecretMethod": secret_method
        }
        try:
            sheet = get_sheet_by_name("Dati_Partecipante", "Partecipanti")
            sheet.append_row(list(dati.values()))
            st.session_state["tavola_rotonda"] = tavola
            st.success("✅ Dati salvati con successo!")
            st.query_params = {"page": "2_Persona_Model"}
            st.rerun()
        except Exception as e:
            st.error("❌ Errore durante il salvataggio dei dati.")
            st.text(f"Dettaglio: {e}")



