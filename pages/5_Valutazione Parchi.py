import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide")
st.title("5. Valutazione dei parchi di Bergamo")

st.markdown("""
In questa pagina ti chiediamo di valutare alcuni parchi urbani del quartiere di Bergamo, in base ai criteri emersi dall'analisi AHP del tavolo rotondo.
Ogni parco è rappresentato sulla mappa qui sotto. Seleziona un parco per visualizzarne le informazioni e fornire una valutazione.
""")

# Criteri AHP definiti nella fase precedente
criteri = [
    "Accessibilità del verde",
    "Biodiversità",
    "Manutenzione e pulizia",
    "Funzione sociale",
    "Funzione ambientale"
]

# Lista di parchi con geolocalizzazione, descrizione e immagini
parchi = [
    {"nome": "Parco Suardi", "lat": 45.7035, "lon": 9.6783,
     "descrizione": "Situato vicino al centro, offre ampi spazi verdi, giochi per bambini e monumenti storici.",
     "img": "https://upload.wikimedia.org/wikipedia/commons/2/26/Parco_Suardi_Bergamo_2.jpg"},
    {"nome": "Parco della Trucca", "lat": 45.6847, "lon": 9.6240,
     "descrizione": "Parco molto ampio con laghetti, pista ciclabile e ampi spazi per picnic.",
     "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Bergamo_-_Parco_della_Trucca.jpg/1280px-Bergamo_-_Parco_della_Trucca.jpg"},
    {"nome": "Parco Goisis", "lat": 45.7151, "lon": 9.6821,
     "descrizione": "Area verde con attrezzature sportive, giochi e ampi spazi per attività motorie.",
     "img": "https://upload.wikimedia.org/wikipedia/commons/3/32/Parco_Goisis_Bergamo.jpg"},
    {"nome": "Parco Locatelli", "lat": 45.7080, "lon": 9.6695,
     "descrizione": "Piccolo parco di quartiere ben curato e frequentato da famiglie.",
     "img": "https://upload.wikimedia.org/wikipedia/commons/8/81/Parco_Locatelli_Bergamo.jpg"}
]

# Mappa dei parchi
st.subheader("\U0001F5FA Mappa dei parchi")
parchi_df = pd.DataFrame(parchi)
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=45.70,
        longitude=9.67,
        zoom=12,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=parchi_df,
            get_position='[lon, lat]',
            get_fill_color='[0, 128, 0, 160]',
            get_radius=100,
        )
    ]
))

# Session state inizializzazione
if "valutazioni_parchi" not in st.session_state:
    st.session_state["valutazioni_parchi"] = {}

# Calcolo del numero di parchi votati
n_votati = len(st.session_state["valutazioni_parchi"])
n_totale = len(parchi)
st.markdown(f"### Parchi valutati: {n_votati} su {n_totale}")

# Lista parchi ancora da votare
parchi_non_votati = [p['nome'] for p in parchi if p['nome'] not in st.session_state["valutazioni_parchi"]]

if parchi_non_votati:
    st.subheader("\U0001F4DD Valuta ciascun parco")
    parco_selezionato = st.selectbox("Seleziona un parco da valutare:", parchi_non_votati)
    parco_dati = next(p for p in parchi if p['nome'] == parco_selezionato)

    st.markdown(f"**{parco_dati['nome']}**")
    st.markdown(f"_{parco_dati['descrizione']}_")
    st.image(parco_dati["img"], use_container_width=True)

    valutazioni = {}
    st.markdown("### Inserisci una valutazione da 1 (bassa) a 5 (alta) per ciascun criterio:")
    for criterio in criteri:
        valutazioni[criterio] = st.slider(f"{criterio}", 1, 5, 3)

    if st.button("Salva valutazione per questo parco"):
        st.session_state["valutazioni_parchi"][parco_selezionato] = valutazioni
        st.success(f"Valutazione salvata per {parco_selezionato}!")
else:
    st.success("Hai completato la valutazione di tutti i parchi. Grazie per il tuo contributo!")

# Mostra tutte le valutazioni inserite
if st.session_state["valutazioni_parchi"]:
    st.subheader("\U0001F4C8 Riepilogo delle valutazioni inserite")
    st.write(pd.DataFrame(st.session_state["valutazioni_parchi"]).T)

