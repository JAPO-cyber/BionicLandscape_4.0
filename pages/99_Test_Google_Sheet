import streamlit as st
from lib.google_sheet import get_sheet_by_name

st.title("🔌 Test Connessione Google Sheet")

# Nome del file Google Sheet condiviso
sheet_name = "Dati_Partecipanti"

# Connessione
sheet = get_sheet_by_name(sheet_name)

# Verifica della connessione
if sheet:
    st.success(f"✅ Connessione riuscita al foglio: '{sheet_name}'")
    
    # Mostra le intestazioni e i primi dati
    records = sheet.get_all_records()
    
    if records:
        st.write("📋 Dati trovati nel foglio:")
        st.dataframe(records)
    else:
        st.info("📂 Nessun dato ancora nel foglio.")
else:
    st.error("❌ Connessione fallita. Controlla il nome del file o i permessi.")
