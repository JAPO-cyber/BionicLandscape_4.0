import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go

from lib.style import apply_custom_style
from lib.google_sheet import get_sheet_by_name

st.set_page_config(page_title="6. Analisi e risultati", layout="wide")
apply_custom_style()

st.title("6. Analisi e visualizzazione dei risultati")

# ------------------------------------------------------------------
# 1️⃣  CARICAMENTO DATI ------------------------------------------------
# ------------------------------------------------------------------
try:
    df_valutazioni = pd.DataFrame(
        get_sheet_by_name("Dati_Partecipante", "Valutazione Parchi").get_all_records()
    )
    df_pesi = pd.DataFrame(
        get_sheet_by_name("Dati_Partecipante", "Pesi Parametri").get_all_records()
    )
    df_info = pd.DataFrame(
        get_sheet_by_name("Dati_Partecipante", "Informazioni Parchi").get_all_records()
    )

    # Fogli “verde” (AHP criteri di sostenibilità)
    df_valutazioni_green = pd.DataFrame(
        get_sheet_by_name("Dati_Partecipante", "Valutazione Parchi Verde").get_all_records()
    )
    df_pesi_green = pd.DataFrame(
        get_sheet_by_name("Dati_Partecipante", "Pesi Parametri Verde").get_all_records()
    )

except Exception as e:
    st.error(f"❌ Errore nel caricamento dei dati: {e}")
    st.stop()

# ------------------------------------------------------------------
# 2️⃣  PULIZIA NOMI COLONNA -------------------------------------------
# ------------------------------------------------------------------
for _df in (df_valutazioni, df_pesi, df_info, df_valutazioni_green, df_pesi_green):
    _df.rename(columns=lambda c: str(c).strip(), inplace=True)

# ------------------------------------------------------------------
# 3️⃣  COSTRUZIONE CRITERI VERDE + PESI FISSI --------------------------
# ------------------------------------------------------------------
META_COLS = {"Timestamp", "Utente", "Index", "Persona"}
criteri_green = [c for c in df_pesi_green.columns if c not in META_COLS]

# Serie con il peso medio di ogni criterio (uguale per tutti i parchi)
pesi_green = (
    df_pesi_green[criteri_green]
    .apply(pd.to_numeric, errors="coerce")
    .mean()
)

# ------------------------------------------------------------------
# 4️⃣  MEDIA VOTI PER PARCO (SEZIONE VERDE) ---------------------------
# ------------------------------------------------------------------
media_val_green = (
    df_valutazioni_green
    .groupby("Parco")[criteri_green]
    .mean()
)
criteri_eff_green = list(set(pesi_green.index) & set(media_val_green.columns))

# ------------------------------------------------------------------
# 5️⃣  MERGE INFO PARCO + SCORE VERDE -------------------------------
# ------------------------------------------------------------------
map_df_green = df_info.merge(
    media_val_green,
    left_on="Nome del Parco",
    right_index=True,
    how="inner",
)
map_df_green["punteggio_green"] = (
    map_df_green[criteri_eff_green]
    .mul(pesi_green[criteri_eff_green], axis=1)
    .sum(axis=1)
)

# ------------------------------------------------------------------
# 6️⃣  SEZIONE CRITERI STANDARD --------------------------------------
# ------------------------------------------------------------------
CAMPI_RINOMINA = {
    "Funzione sociale (es. luoghi di incontro)": "Funzione sociale",
    "Funzione ambientale (es. ombra, qualità aria)": "Funzione ambientale",
}

df_pesi.rename(columns=CAMPI_RINOMINA, inplace=True)
df_valutazioni.rename(columns=CAMPI_RINOMINA, inplace=True)

CRITERI_STD = [
    "Accessibilità del verde",
    "Biodiversità",
    "Manutenzione e pulizia",
    "Funzione sociale",
    "Funzione ambientale",
]

# ------------------------------------------------------------------
# 7️⃣  FILTRI DALLA SIDEBAR -----------------------------------------
# ------------------------------------------------------------------
with st.sidebar:
    st.header("📊 Analisi")
    page_sel = st.radio(
        "Seleziona vista:",
        [
            "📍 Mappa Punteggi",
            "📊 Classifica Parchi",
            "📈 Analisi Aggregata",
            "🔀 Combina Green & Citizen",
        ],
    )

    tavole = df_valutazioni["Tavola rotonda"].dropna().unique().tolist()
    tavola_sel = st.selectbox("🎯 Filtra per Tavola rotonda:", ["Tutte"] + tavole)

    quartieri = df_info["Quartiere"].dropna().unique().tolist()
    quartiere_sel = st.selectbox("🏘️ Filtra per quartiere:", ["Tutti"] + quartieri)

# Applica filtro tavola
if tavola_sel != "Tutte":
    mask = df_valutazioni["Tavola rotonda"] == tavola_sel
    df_val_f = df_valutazioni[mask]
    df_pesi_f = df_pesi[df_pesi["Tavola rotonda"] == tavola_sel]
else:
    df_val_f = df_valutazioni.copy()
    df_pesi_f = df_pesi.copy()

# ------------------------------------------------------------------
# 8️⃣  OUTLIER & PUNTEGGIO STANDARD ---------------------------------
# ------------------------------------------------------------------
media_val = df_val_f.groupby("Parco")[CRITERI_STD].mean()
std_val = df_val_f.groupby("Parco")[CRITERI_STD].std()

SOGLIA_STD = 1.2
mask_outlier = std_val.max(axis=1) > SOGLIA_STD
if mask_outlier.any():
    media_val = media_val[~mask_outlier]

pesi_std = df_pesi_f[CRITERI_STD].mean()
media_val = media_val.reset_index()
media_val["punteggio_std"] = (
    media_val[CRITERI_STD]
    .mul(pesi_std, axis=1)
    .sum(axis=1)
)

map_df_std = pd.merge(
    media_val,
    df_info,
    left_on="Parco",
    right_on="Nome del Parco",
    how="inner",
)

# ------------------------------------------------------------------
# 9️⃣  PREPARA DATI PER COMBINAZIONE -------------------------------
# ------------------------------------------------------------------
# Assicura lat/lon numerici e filtra quartieri
for df in (map_df_std, map_df_green):
    df["Latitudine"] = pd.to_numeric(df["Latitudine"], errors="coerce")
    df["Longitudine"] = pd.to_numeric(df["Longitudine"], errors="coerce")

# Unisci citizen + green
map_df_combi = pd.merge(
    map_df_std,
    map_df_green[["Nome del Parco", "punteggio_green"] + criteri_eff_green],
    on="Nome del Parco",
    how="inner",
)
map_df_combi.dropna(subset=["Latitudine", "Longitudine"], inplace=True)
if quartiere_sel != "Tutti":
    map_df_combi = map_df_combi[map_df_combi["Quartiere"] == quartiere_sel]

# ------------------------------------------------------------------
# 🔟  VISUALIZZAZIONI ----------------------------------------------
# ------------------------------------------------------------------
if page_sel == "📍 Mappa Punteggi":
    st.subheader("📍 Mappa dei parchi con punteggio finale")
    df = map_df_std.rename(columns={"punteggio_std": "punteggio"})
    if df.empty:
        st.warning("⚠️ Nessun parco soddisfa i filtri selezionati.")
    else:
        view_state = pdk.ViewState(latitude=45.6983, longitude=9.6773, zoom=13)
        df["color"] = df["punteggio"].apply(lambda p: [
            255 if p <= 2 else int(255*(1-(p-2)/2)) if p<=4 else 0,
            int(255*(p-1)) if p<=2 else 255,
            0, 160
        ])
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/outdoors-v11',
            initial_view_state=view_state,
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df,
                    get_position="[Longitudine, Latitudine]",
                    get_fill_color="color",
                    get_radius=150,
                    pickable=True,
                )
            ],
            tooltip={"text": "{Nome del Parco}\nPunteggio: {punteggio:.2f}"}
        ))

elif page_sel == "📊 Classifica Parchi":
    st.subheader("📊 Classifica dei parchi per punteggio")
    st.dataframe(
        map_df_std[["Nome del Parco", "Quartiere", "punteggio_std"]]
        .rename(columns={"punteggio_std": "punteggio"})
        .sort_values(by="punteggio", ascending=False)
    )

elif page_sel == "📈 Analisi Aggregata":
    st.subheader("📈 Analisi media & radar")
    media_criteri = df_valutazioni_green[criteri_green].mean().round(2)
    pesi_criteri = pesi_green.round(2)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Valori medi (verde):**")
        st.dataframe(media_criteri.rename("Media").to_frame())
    with col2:
        st.markdown("**Pesi AHP (verde):**")
        st.dataframe(pesi_criteri.rename("Peso").to_frame())
    radar_val = go.Figure()
    radar_val.add_trace(
        go.Scatterpolar(r=media_criteri.tolist(), theta=criteri_green, fill="toself")
    )
    radar_val.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
    st.plotly_chart(radar_val, use_container_width=True)
    radar_pesi = go.Figure()
    radar_pesi.add_trace(
        go.Scatterpolar(r=pesi_criteri.tolist(), theta=criteri_green, fill="toself")
    )
    radar_pesi.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False)
    st.plotly_chart(radar_pesi, use_container_width=True)

elif page_sel == "🔀 Combina Green & Citizen":
    st.subheader("🔀 Combina score Green e Citizen")
    # Definizione dei limiti di quadrante (medie degli asse)
    x_mid = map_df_combi['punteggio_green'].mean()
    y_mid = map_df_combi['punteggio_std'].mean()

    # Assegna quadrante e colore
    def quadrant_label(p):
        x, y = p['punteggio_green'], p['punteggio_std']
        if x >= x_mid and y >= y_mid:
            return 'Top Right'
        elif x < x_mid and y >= y_mid:
            return 'Top Left'
        elif x < x_mid and y < y_mid:
            return 'Bottom Left'
        else:
            return 'Bottom Right'

    map_df_combi['quadrante'] = map_df_combi.apply(quadrant_label, axis=1)
    quadrant_colors = {
        'Top Right': 'green',
        'Top Left': 'blue',
        'Bottom Left': 'red',
        'Bottom Right': 'orange'
    }
    map_df_combi['col_quadr'] = map_df_combi['quadrante'].map(quadrant_colors)

    # Scatter plot XY con quadranti e nomi
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=map_df_combi['punteggio_green'],
        y=map_df_combi['punteggio_std'],
        mode='markers+text',
        marker=dict(
            size=map_df_combi['Manutenzione'],
            sizemode='area',
            sizeref=2.*max(map_df_combi['Manutenzione'])/(40.**2),
            sizemin=4,
            color=map_df_combi['col_quadr'],
        ),
        text=map_df_combi['Nome del Parco'],
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>Green: %{x:.2f}<br>Citizen: %{y:.2f}<br>Quadrante: %{marker.color}'
    ))
    # Aggiungo linee di separazione dei quadranti
    fig.add_shape(type='line', x0=x_mid, x1=x_mid, y0=map_df_combi['punteggio_std'].min(), y1=map_df_combi['punteggio_std'].max(), line=dict(dash='dash'))
    fig.add_shape(type='line', y0=y_mid, y1=y_mid, x0=map_df_combi['punteggio_green'].min(), x1=map_df_combi['punteggio_green'].max(), line=dict(dash='dash'))
    # Etichette quadranti
    fig.add_annotation(x=x_mid + (fig.layout.xaxis.range[1]-x_mid)/2, y=y_mid + (fig.layout.yaxis.range[1]-y_mid)/2,
                       text='Top Right', showarrow=False)
    fig.add_annotation(x=(fig.layout.xaxis.range[0]+x_mid)/2, y=y_mid + (fig.layout.yaxis.range[1]-y_mid)/2,
                       text='Top Left', showarrow=False)
    fig.add_annotation(x=(fig.layout.xaxis.range[0]+x_mid)/2, y=(fig.layout.yaxis.range[0]+y_mid)/2,
                       text='Bottom Left', showarrow=False)
    fig.add_annotation(x=x_mid + (fig.layout.xaxis.range[1]-x_mid)/2, y=(fig.layout.yaxis.range[0]+y_mid)/2,
                       text='Bottom Right', showarrow=False)

    fig.update_layout(
        xaxis_title='Score Green',
        yaxis_title='Punteggio Citizen',
        height=600,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # Mappa combinata
    st.subheader("📍 Mappa combinata")
    view_state = pdk.ViewState(latitude=45.6983, longitude=9.6773, zoom=13)
    map_df_combi['color_citizen'] = map_df_combi['punteggio_std'].apply(
        lambda p: [
            255 if p <= 2 else int(255*(1-(p-2)/2)) if p<=4 else 0,
            int(255*(p-1)) if p<=2 else 255,
            0, 160
        ]
    )
    map_df_combi['radius_green'] = map_df_combi['punteggio_green'] * 100
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/outdoors-v11',
        initial_view_state=view_state,
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_df_combi,
                get_position="[Longitudine, Latitudine]",
                get_fill_color="color_citizen",
                get_radius="radius_green",
                pickable=True,
            )
        ],
        tooltip={"text": "{Nome del Parco}
Green: {punteggio_green:.2f}
Citizen: {punteggio_std:.2f}
Quadrante: {quadrante}"}
    ))


