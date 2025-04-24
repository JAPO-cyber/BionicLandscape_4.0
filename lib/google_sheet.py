import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Lettura delle credenziali: Streamlit Cloud o Cloud Run
    if "gcp_service_account" in st.secrets:
        service_account_info = st.secrets["gcp_service_account"]
    elif "GCP_CREDENTIALS_JSON" in os.environ:
        service_account_info = json.loads(os.environ["GCP_CREDENTIALS_JSON"])
    else:
        st.error("❌ Credenziali Google non trovate.")
        st.stop()

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    return gspread.authorize(credentials)


def get_sheet_by_name(sheet_name, worksheet_name="Sheet1"):
    client = get_gspread_client()
    try:
        spreadsheet = client.open(sheet_name)
        return spreadsheet.worksheet(worksheet_name)
    except Exception as e:
        st.error(f"❌ Errore nel caricamento del foglio '{worksheet_name}': {e}")
        return None
