import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk

st.set_page_config(layout="wide")
st.title("6. Analisi della valutazione dei parchi")

# Verifica che ci siano valutazioni salvate
if "valutazioni_parchi" not in st.session_state or not st.session_state["valutazioni_parchi"]:
    st.warning("Nessuna valutazione trovata. Torna alla pagina precedente per completare la valutazione dei parchi.")
    st.stop()

# Recupera i dati delle valutazioni
valutazioni_dict = st.session_state["valutazioni_parchi"]
parchi_valutati = list(valutazioni_dict.keys())
criteri = [c for c in list(valutazioni_dict[parchi_valutati[0]].keys()) if c != "feedback"]

# Costruzione DataFrame valutazioni
df_valutazioni = pd.DataFrame(
    {parco: {criterio: valori[criterio] for criterio in criteri} for parco, valori in valutazioni_dict.items()}
).T

# Calcolo statistiche
st.subheader("\U0001F4CA Statistiche delle valutazioni")
st.markdown("Media e variabilità delle valutazioni fornite per ciascun parco.")

media_df = df_valutazioni.mean(axis=1).rename("Media")
std_df = df_valutazioni.std(axis=1).rename("Deviazione Standard")
statistiche = pd.concat([media_df, std_df], axis=1)
st.dataframe(statistiche)

# Visualizzazione
fig = px.bar(statistiche, x=statistiche.index, y="Media", error_y="Deviazione Standard",
             title="Valutazione media dei parchi con deviazione standard")
st.plotly_chart(fig, use_container_width=True)

# Recupera i pesi AHP dell'utente se disponibili
if "ahp_weights" not in st.session_state:
    st.warning("Non sono stati trovati i pesi AHP individuali. Torna alla pagina della matrice AHP per completarli.")
    st.stop()

# Calcolo punteggio AHP aggregato
st.subheader("\U0001F4DD Valutazione Cittadino")

ahp_pesi = st.session_state["ahp_weights"]
vet_pesi = np.array([ahp_pesi[c] for c in criteri])
punteggi = df_valutazioni @ vet_pesi

df_finale = pd.DataFrame({
    "Punteggio Valutazione Cittadino": punteggi,
    "Media": media_df,
    "Deviazione Standard": std_df
})
st.dataframe(df_finale.sort_values("Punteggio Valutazione Cittadino", ascending=False))

# Commenti
st.subheader("\U0001F4AC Commenti lasciati dagli utenti")
for parco, valutazione in valutazioni_dict.items():
    commento = valutazione.get("feedback", "")
    if commento:
        st.markdown(f"**{parco}**: {commento}")

# Mappa con colori secondo punteggio
st.subheader("\U0001F5FA Mappa dei parchi colorata per punteggio")
parchi_coord = {
    "Parco Suardi": (45.7035, 9.6783),
    "Parco della Trucca": (45.6847, 9.6240),
    "Parco Goisis": (45.7151, 9.6821),
    "Parco Locatelli": (45.7080, 9.6695),
}

map_df = pd.DataFrame([
    {
        "nome": parco,
        "lat": parchi_coord[parco][0],
        "lon": parchi_coord[parco][1],
        "punteggio": punteggi[parco]
    } for parco in punteggi.index if parco in parchi_coord
])

# Funzione per assegnare colore RGB in base al punteggio
# 0 = rosso, 5 = giallo, >9 = verde

def punteggio_to_rgb(p):
    if p <= 5:
        r = 255
        g = int(255 * (p / 5))
    elif p <= 9:
        r = int(255 * (1 - (p - 5) / 4))
        g = 255
    else:
        r = 0
        g = 255
    return [r, g, 0, 160]

map_df["color"] = map_df["punteggio"].apply(punteggio_to_rgb)

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=45.6983,
        longitude=9.6773,
        zoom=13
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[lon, lat]",
            get_fill_color="color",
            get_radius=150,
            pickable=True
        )
    ],
    tooltip={"text": "{nome}\nPunteggio: {punteggio:.2f}"}
))
