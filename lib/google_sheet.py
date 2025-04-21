import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    service_account_info = json.loads(st.secrets["gcp_service_account"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    return gspread.authorize(credentials)

def get_sheet_by_name(sheet_name):
    client = get_gspread_client()
    try:
        spreadsheet = client.open(sheet_name)
        return spreadsheet.sheet1  # o usa `.worksheet("NomeFoglio")` se necessario
    except Exception as e:
        st.error(f"Errore nel caricamento dello Sheet: {e}")
        return None
