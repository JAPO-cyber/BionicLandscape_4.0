import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime
from lib.style import apply_custom_style
from lib.google_sheet import get_sheet_by_name

# ✅ Configura pagina e stile
st.set_page_config(page_title="5. Valutazione dei parchi", layout="wide")
apply_custom_style()

# ✅ Verifica login e ID partecipante
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Accesso negato. Torna alla pagina principale.")
    st.stop()

if "id_partecipante" not in st.session_state:
    st.error("❌ Identificativo partecipante mancante. Torna alla registrazione.")
    st.stop()

# ✅ Titolo e descrizione
st.title("5. Valutazione dei parchi di Bergamo")
st.markdown("""
In questa pagina ti chiediamo di valutare alcuni parchi urbani del quartiere di Bergamo, in base ai criteri emersi dall'analisi AHP del tavolo rotondo.
Ogni parco è rappresentato sulla mappa qui sotto. Seleziona un parco per visualizzarne le informazioni e fornire una valutazione.
""")

# ✅ Criteri AHP
criteri = [
    "Accessibilità del verde",
    "Biodiversità",
    "Manutenzione e pulizia",
    "Funzione sociale",
    "Funzione ambientale"
]

# ✅ Carica i parchi da Google Sheet
try:
    sheet_parchi = get_sheet_by_name("Dati_Partecipante", "Informazioni Parchi")
    df_parchi = pd.DataFrame(sheet_parchi.get_all_records())
except Exception as e:
    st.error("❌ Errore nel caricamento dei dati dei parchi.")
    st.stop()

# ✅ Mappa dei parchi
st.subheader("🗺️ Mappa dei parchi")
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=df_parchi["Latitudine"].mean(),
        longitude=df_parchi["Longitudine"].mean(),
        zoom=13
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=df_parchi,
            get_position='[Longitudine, Latitudine]',
            get_fill_color='[0, 128, 0, 160]',
            get_radius=100,
        )
    ]
))

# ✅ Inizializza stato sessione
if "valutazioni_parchi" not in st.session_state:
    st.session_state["valutazioni_parchi"] = {}

# ✅ Conteggio parchi votati
parchi_nomi = df_parchi["Nome del Parco"].tolist()
n_votati = len(st.session_state["valutazioni_parchi"])
n_totale = len(parchi_nomi)
st.markdown(f"### Parchi valutati: {n_votati} su {n_totale}")

# ✅ Selezione parco da valutare
parchi_non_valutati = [p for p in parchi_nomi if p not in st.session_state["valutazioni_parchi"]]
parchi_valutati = list(st.session_state["valutazioni_parchi"].keys())
scelte = parchi_non_valutati + parchi_valutati

if scelte:
    st.subheader("📝 Valuta o modifica un parco")
    parco_selezionato = st.selectbox("Seleziona un parco da valutare o modificare:", scelte)
    parco_info = df_parchi[df_parchi["Nome del Parco"] == parco_selezionato].iloc[0]

    st.markdown(f"**{parco_info['Nome del Parco']} - {parco_info['Quartiere']}**")
    st.markdown(f"_{parco_info['Descrizione']}_")
    st.image(parco_info["Link immagine"], use_container_width=True)

    valutazioni = st.session_state["valutazioni_parchi"].get(parco_selezionato, {})

    st.markdown("### Inserisci una valutazione da 1 (bassa) a 5 (alta) per ciascun criterio:")
    nuove_valutazioni = {}
    for criterio in criteri:
        valore_default = valutazioni.get(criterio, 3)
        nuove_valutazioni[criterio] = st.slider(f"{criterio}", 1, 5, valore_default)

    feedback = valutazioni.get("Feedback", "")
    nuove_valutazioni["Feedback"] = st.text_area("Lascia un commento su questo parco (opzionale):", value=feedback)

    if st.button("💾 Salva o aggiorna valutazione per questo parco"):
        st.session_state["valutazioni_parchi"][parco_selezionato] = nuove_valutazioni
        st.success(f"✅ Valutazione salvata o aggiornata per {parco_selezionato}!")

else:
    st.success("Hai completato la valutazione di tutti i parchi. Grazie per il tuo contributo!")

# ✅ Mostra riepilogo e consente invio
if st.session_state["valutazioni_parchi"]:
    st.subheader("📊 Riepilogo delle valutazioni inserite")
    st.write(pd.DataFrame(st.session_state["valutazioni_parchi"]).T)

    if st.button("📤 Invia tutte le valutazioni"):
        try:
            sheet_valutazioni = get_sheet_by_name("Dati_Partecipante", "Valutazione Parchi")
            for parco, dati in st.session_state["valutazioni_parchi"].items():
                row = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ID Partecipante": st.session_state["id_partecipante"],
                    "Tavola rotonda": st.session_state.get("tavola_rotonda", "non specificata"),
                    "Parco": parco,
                }
                for criterio in criteri:
                    row[criterio] = dati.get(criterio, "")
                row["Feedback"] = dati.get("Feedback", "")
                sheet_valutazioni.append_row(list(row.values()))
            st.success("✅ Tutte le valutazioni sono state salvate su Google Sheet!")
        except Exception as e:
            st.error("❌ Errore durante il salvataggio delle valutazioni.")
            st.text(f"Dettaglio: {e}")


