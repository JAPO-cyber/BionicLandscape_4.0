import streamlit as st
from lib.google_sheet import get_sheet_by_name

# Questo modulo centralizza tutte le interazioni con Google Sheet

def save_to_sheet(dati: dict, sheet_name: str = "Partecipanti"):
    """
    Salva i dati su Google Sheet.

    Parameters
    ----------
    dati : dict
        Dizionario di valori da appendere come nuova riga.
    sheet_name : str
        Nome del foglio all'interno del file 'Dati_Partecipante'.
    """
    try:
        sheet = get_sheet_by_name("Dati_Partecipante", sheet_name)
        sheet.append_row(list(dati.values()))
        st.success("✅ Dati salvati su Google Sheet!")
    except Exception as e:
        st.error("❌ Errore nel salvataggio su Google Sheet.")
        st.text(f"Dettaglio: {e}")
