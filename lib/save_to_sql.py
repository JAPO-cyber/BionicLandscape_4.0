import streamlit as st
import sqlalchemy
from sqlalchemy import text

# Questo modulo centralizza tutte le interazioni con Google Cloud SQL

def save_to_sql(dati: dict, table_name: str = "Risposte"):
    """
    Salva i dati su Google Cloud SQL in formato long.

    Parameters
    ----------
    dati : dict
        Deve contenere chiavi:
            - 'timestamp': str
            - 'id': str
            - 'quartiere': str
            - 'answers': dict question->response
    table_name : str
        Tabella in cui salvare le risposte.
    """
    try:
        db_url = st.secrets.get("SQL_CONNECTION_URL", "")
        engine = sqlalchemy.create_engine(db_url)
        # Crea la tabella se non esiste
        create_sql = text(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                timestamp  VARCHAR(20),
                id         VARCHAR(50),
                quartiere  VARCHAR(100),
                question   TEXT,
                response   TEXT
            )
        """
        )
        insert_sql = text(f"""
            INSERT INTO {table_name} (timestamp, id, quartiere, question, response)
            VALUES (:timestamp, :id, :quartiere, :question, :response)
        """
        )
        ts = dati.get("timestamp")
        answers = dati.get("answers", {})
        with engine.begin() as conn:
            conn.execute(create_sql)
            for question, response in answers.items():
                resp = ", ".join(map(str, response)) if isinstance(response, list) else str(response)
                conn.execute(insert_sql, {
                    "timestamp": ts,
                    "id": dati.get("id"),
                    "quartiere": dati.get("quartiere"),
                    "question": question,
                    "response": resp
                })
        st.success("✅ Risposte salvate su Cloud SQL!")
    except Exception as e:
        st.error("❌ Errore nel salvataggio su Cloud SQL.")
        st.text(f"Dettaglio: {e}")
