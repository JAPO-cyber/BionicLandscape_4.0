import streamlit as st
import sqlalchemy
from sqlalchemy import text
from lib.style import get_secret

# Questo modulo si attiva solo se SECRET_METHOD è "Google Secret Manager"
# Serve a creare la tabella delle domande e a recuperarle dinamicamente.

def _get_engine():
    secret_method = st.session_state.get("secret_method", "Streamlit Secrets")
    if secret_method != "Google Secret Manager":
        return None
    # Recupera URL di connessione da segreti
    db_url = get_secret("SQL_CONNECTION_URL")
    engine = sqlalchemy.create_engine(db_url)
    return engine


def ensure_questions_table():
    """
    Crea la tabella 'Questions' se non esiste.
    Struttura:
      - quartiere:    VARCHAR(100)
      - question:     TEXT
      - question_type VARCHAR(50)   # e.g. 'select', 'radio', 'text', 'multiselect', 'slider'
      - question_value TEXT         # valori possibili, separati da virgola
    """
    engine = _get_engine()
    if engine is None:
        return
    create_sql = text(
        """
        CREATE TABLE IF NOT EXISTS Questions (
            quartiere       VARCHAR(100),
            question        TEXT,
            question_type   VARCHAR(50),
            question_value  TEXT
        )
        """
    )
    with engine.begin() as conn:
        conn.execute(create_sql)


def fetch_questions_for_quartiere(quartiere: str):
    """
    Restituisce lista di domande per il quartiere dato.
    Ogni elemento è un dict con chiavi: question, type, values (lista).
    """
    engine = _get_engine()
    if engine is None:
        return []
    ensure_questions_table()
    query = text(
        "SELECT question, question_type, question_value"
        " FROM Questions"
        " WHERE quartiere = :quartiere"
    )
    with engine.connect() as conn:
        rows = conn.execute(query, {"quartiere": quartiere}).fetchall()
    questions = []
    for q, qtype, qvals in rows:
        values = [v.strip() for v in qvals.split(',')] if qvals else []
        questions.append({
            "question": q,
            "type": qtype,
            "values": values
        })
    return questions
