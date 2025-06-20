import streamlit as st
import pandas as pd
import datetime
import secrets
import string
from lib.google_sheet import get_sheet_by_name
from lib.style import apply_custom_style, get_secret
from lib.sql_questions import fetch_questions_for_quartiere, ensure_questions_table
from lib.save_to_sheet import save_to_sheet
from lib.save_to_sql import save_to_sql
from lib.navigation import render_sidebar_navigation

# ─── Configura pagina ─────────────────────────────────────────────────────
st.set_page_config(page_title="Registrazione", layout="wide")

# ─── Verifica login ───────────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    st.error("❌ Accesso negato. Torna alla pagina principale.")
    st.stop()

# ─── Applica stile grafico ─────────────────────────────────────────────────
apply_custom_style()

# ─── Eredita quartiere e metodo segreti dal main ──────────────────────────
quartiere = st.session_state.get("quartiere", "")
secret_method = st.session_state.get("secret_method", "Streamlit Secrets")

# ─── Genera un ID univoco ───────────────────────────────────────────────────
def genera_id_univoco(lunghezza=16):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(lunghezza))

if "id_partecipante" not in st.session_state:
    try:
        sheet = get_sheet_by_name("Dati_Partecipante", "Partecipanti")
        existing = [r[3] for r in sheet.get_all_values()[1:]]
        new_id = genera_id_univoco()
        while new_id in existing:
            new_id = genera_id_univoco()
        st.session_state["id_partecipante"] = new_id
    except Exception as e:
        st.error("❌ Errore nella generazione dell'ID partecipante.")
        st.text(f"Dettaglio: {e}")
        st.stop()

# ─── Titolo e informazioni ─────────────────────────────────────────────────
st.markdown('<div class="header">🏠 Pagina di Registrazione</div>', unsafe_allow_html=True)
st.markdown(f"### ID: `{st.session_state['id_partecipante']}` | Quartiere: **{quartiere}**")
st.markdown("---")

# ─── Prepara opzioni tavola in modalità Streamlit Secrets ────────────────
if secret_method == "Streamlit Secrets":
    try:
        sheet_attive = get_sheet_by_name("Dati_Partecipante", "Tavola Rotonda Attiva")
        df_attive = pd.DataFrame(sheet_attive.get_all_records())
        opzioni = df_attive["Tavola Rotonda Attiva"].dropna().unique().tolist()
        if not opzioni:
            opzioni = ["(nessuna disponibile)"]
    except Exception:
        opzioni = ["(errore connessione)"]

# ─── Carica domande dinamiche (solo SQL) ────────────────────────────────────
questions = []
if secret_method != "Streamlit Secrets":
    ensure_questions_table()
    questions = fetch_questions_for_quartiere(quartiere)

# ─── FORM DATI UTENTE ───────────────────────────────────────────────────────
with st.form("user_info_form"):
    answers = {}

    if secret_method == "Streamlit Secrets":
        answers["Tavola rotonda"] = st.selectbox("🔘 Tavola rotonda", opzioni, key="tavola_static")
        answers["Età"] = st.number_input("🎂 Età", min_value=16, max_value=100, step=1, key="eta_static")
        answers["Professione"] = st.text_input("💼 Professione", key="prof_static")
        answers["Ruolo"] = st.selectbox(
            "🎭 Ruolo", 
            ["Cittadino", "Tecnico comunale", "Rappresentante associazione", "Educatore ambientale"],
            key="ruolo_static"
        )
        answers["Motivazione"] = st.text_area("🗣️ Motivazione", placeholder="Perché partecipi?", key="motivazione_static")
        answers["Obiettivo"] = st.text_area("🎯 Obiettivo", placeholder="Cosa vuoi ottenere?", key="obiettivo_static")
        valori = st.multiselect(
            "❤️ Valori",
            ["Innovazione", "Collaborazione", "Responsabilità", "Inclusione", "Sostenibilità"],
            key="valori_static"
        )
        answers["Valori"] = ", ".join(valori)
    else:
        for idx, q in enumerate(questions):
            key = f"q_{idx}"
            if q["type"] == "select":
                answers[q["question"]] = st.selectbox(q["question"], q["values"], key=key)
            elif q["type"] == "radio":
                answers[q["question"]] = st.radio(q["question"], q["values"], key=key)
            elif q["type"] == "multiselect":
                answers[q["question"]] = st.multiselect(q["question"], q["values"], key=key)
            elif q["type"] == "slider":
                vals = [int(v) for v in q["values"] if v.isdigit()]
                if vals:
                    answers[q["question"]] = st.slider(
                        q["question"], min(vals), max(vals), (min(vals) + max(vals)) // 2, key=key
                    )
            else:
                answers[q["question"]] = st.text_input(q["question"], key=key)

    submitted = st.form_submit_button("Invia")

# ─── Salvataggio dati ───────────────────────────────────────────────────────
if submitted:
    if not answers:
        st.error("⚠️ Nessuna risposta inserita.")
    else:
        dati = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id": st.session_state["id_partecipante"],
            "quartiere": quartiere,
            "answers": answers
        }
        if secret_method == "Streamlit Secrets":
            save_to_sheet({**dati, **{k: v for k, v in answers.items()}}, sheet_name="Partecipanti")
        else:
            save_to_sql(dati, table_name="Risposte")
        # Naviga alla pagina successiva
        st.query_params = {"page": "2_Persona_Model"}
        st.rerun()

# ─── Sidebar di navigazione ─────────────────────────────────────────────────
render_sidebar_navigation()
