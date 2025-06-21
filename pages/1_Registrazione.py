# pages/1_Registrazione.py

import streamlit as st
import pandas as pd
import datetime
import secrets
import string
import sqlalchemy
from sqlalchemy import text

from lib.google_sheet import get_sheet_by_name
from lib.style import apply_custom_style
from lib.get_secret import get_secret
from lib.sql_questions import fetch_questions_for_quartiere, ensure_questions_table
from lib.navigation import render_sidebar_navigation


# ─── Configura pagina ─────────────────────────────────────────────────────
st.set_page_config(page_title="Registrazione", layout="wide")

# ─── Verifica login ───────────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    st.error("❌ Accesso negato. Torna alla pagina principale.")
    st.stop()


# ─── Applica stile grafico ─────────────────────────────────────────────────
apply_custom_style()

render_sidebar_navigation()

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

# ─── Carica domande dinamiche (solo SQL) ────────────────────────────────────
questions = []
if secret_method != "Streamlit Secrets":
    ensure_questions_table()
    questions = fetch_questions_for_quartiere(quartiere)

# ─── FORM DATI UTENTE ───────────────────────────────────────────────────────
with st.form("user_info_form"):
    answers = {}

    if secret_method == "Streamlit Secrets":
        # campi statici
        answers["Tavola rotonda"] = st.selectbox("🔘 Tavola rotonda", opzioni, key="tavola_static")
        answers["Età"]            = st.number_input("🎂 Età", min_value=16, max_value=100, step=1, key="eta_static")
        answers["Professione"]    = st.text_input("💼 Professione", key="prof_static")
        answers["Ruolo"]          = st.selectbox(
            "🎭 Ruolo",
            ["Cittadino", "Tecnico comunale", "Rappresentante associazione", "Educatore ambientale"],
            key="ruolo_static"
        )
        answers["Motivazione"]    = st.text_area("🗣️ Motivazione", placeholder="Perché partecipi?", key="motivazione_static")
        answers["Obiettivo"]      = st.text_area("🎯 Obiettivo", placeholder="Cosa vuoi ottenere?", key="obiettivo_static")
        valori = st.multiselect(
            "❤️ Valori",
            ["Innovazione", "Collaborazione", "Responsabilità", "Inclusione", "Sostenibilità"],
            key="valori_static"
        )
        answers["Valori"] = ", ".join(valori)

    else:
        # campi dinamici da SQL
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
        # Prepara record base
        dati = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id": st.session_state["id_partecipante"],
            "quartiere": quartiere
        }
        # Unisci risposte
        for k, v in answers.items():
            dati[k] = v

        try:
            if secret_method == "Streamlit Secrets":
                # salva su Google Sheet
                sheet = get_sheet_by_name("Dati_Partecipante", "Partecipanti")
                sheet.append_row(list(dati.values()))
                st.success("✅ Dati salvati su Google Sheet!")
            else:
                # salva su Cloud SQL in formato long
                db_url = get_secret("SQL_CONNECTION_URL")
                engine = sqlalchemy.create_engine(db_url)

                create_sql = text("""
                    CREATE TABLE IF NOT EXISTS Risposte (
                        timestamp  VARCHAR(20),
                        id         VARCHAR(50),
                        quartiere  VARCHAR(100),
                        question   TEXT,
                        response   TEXT
                    )
                """)
                insert_sql = text("""
                    INSERT INTO Risposte (timestamp, id, quartiere, question, response)
                    VALUES (:timestamp, :id, :quartiere, :question, :response)
                """)

                ts = dati["timestamp"]
                with engine.begin() as conn:
                    conn.execute(create_sql)
                    for question, response in answers.items():
                        resp = ", ".join(map(str, response)) if isinstance(response, list) else str(response)
                        conn.execute(insert_sql, {
                            "timestamp": ts,
                            "id": dati["id"],
                            "quartiere": quartiere,
                            "question": question,
                            "response": resp
                        })
                st.success("✅ Risposte salvate su Cloud SQL!")
            # vai avanti
            st.experimental_set_query_params(page="2_Persona_Model")
            st.experimental_rerun()

        except Exception as e:
            st.error("❌ Errore salvataggio dati.")
            st.text(f"Dettaglio: {e}")

