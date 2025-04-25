import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go

from lib.style import apply_custom_style
from lib.google_sheet import get_sheet_by_name

# ------------------------------------------------------------------
# Utility & Config
# ------------------------------------------------------------------
@st.cache_data
def to_numeric_df(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
    return df

@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    sheets = {
        "df_valutazioni": "Valutazione Parchi",
        "df_pesi": "Pesi Parametri",
        "df_info": "Informazioni Parchi",
        "df_valutazioni_green": "Valutazione Parchi Verde",
        "df_pesi_green": "Pesi Parametri Verde",
    }
    dfs: dict[str, pd.DataFrame] = {}
    for key, name in sheets.items():
        dfs[key] = pd.DataFrame(
            get_sheet_by_name("Dati_Partecipante", name).get_all_records()
        )
    return dfs

st.set_page_config(page_title="6. Analisi e risultati", layout="wide")
apply_custom_style()
st.title("6. Analisi e visualizzazione dei risultati")

# ------------------------------------------------------------------
# 1️⃣  Load and Clean Data
# ------------------------------------------------------------------
dfs = load_data()
df_val            = dfs['df_valutazioni']
df_pesi           = dfs['df_pesi']
df_info           = dfs['df_info']
df_val_green      = dfs['df_valutazioni_green']
df_pesi_green     = dfs['df_pesi_green']

for df in (df_val, df_pesi, df_info, df_val_green, df_pesi_green):
    df.rename(columns=lambda c: str(c).strip(), inplace=True)

# Rinomina campi estesi
df_val.rename(columns={
    "Funzione sociale (es. luoghi di incontro)": "Funzione sociale",
    "Funzione ambientale (es. ombra, qualità aria)": "Funzione ambientale"
}, inplace=True)

df_pesi.rename(columns={
    "Funzione sociale (es. luoghi di incontro)": "Funzione sociale",
    "Funzione ambientale (es. ombra, qualità aria)": "Funzione ambientale"
}, inplace=True)

# ------------------------------------------------------------------
# 2️⃣  Sidebar Filters & Page Selection
# ------------------------------------------------------------------
st.sidebar.header("📊 Filtri")
page_sel = st.sidebar.radio("Seleziona vista:", [
    "📍 Mappa Punteggi",
    "📊 Classifica Parchi",
    "📈 Analisi Aggregata",
    "🔀 Combina Green & Citizen",
    "📉 Correlazione Criteri",
    "📋 Tabella Completa"
])
tavole = df_val.get("Tavola rotonda", pd.Series()).dropna().unique().tolist()
tav_sel = st.sidebar.selectbox("Tavola rotonda:", ["Tutte"] + tavole)
quartieri = df_info.get("Quartiere", pd.Series()).dropna().unique().tolist()
quart_sel = st.sidebar.selectbox("Quartiere:", ["Tutti"] + quartieri)

# Filtra df_val e df_pesi per tavola
if tav_sel != "Tutte":
    mask = df_val["Tavola rotonda"] == tav_sel
    df_val_f = df_val[mask]
    df_pesi_f = df_pesi[mask]
else:
    df_val_f = df_val.copy()
    df_pesi_f = df_pesi.copy()

# ------------------------------------------------------------------
# 3️⃣  Compute Standard Scores
# ------------------------------------------------------------------
CRITERI_STD = [
    "Accessibilità del verde", "Biodiversità",
    "Manutenzione e pulizia", "Funzione sociale", "Funzione ambientale"
]
media_std = df_val_f.groupby("Parco")[CRITERI_STD].mean()
std_std   = df_val_f.groupby("Parco")[CRITERI_STD].std()
pesi_std  = df_pesi_f[CRITERI_STD].mean()

# Calcola punteggio standard
media_std['punteggio_std'] = media_std.mul(pesi_std).sum(axis=1)
map_df_std = pd.merge(
    media_std.reset_index(), df_info,
    left_on="Parco", right_on="Nome del Parco", how="inner"
)
map_df_std = to_numeric_df(map_df_std, ["Latitudine", "Longitudine"])

# ------------------------------------------------------------------
# 4️⃣  Compute Green Scores
# ------------------------------------------------------------------
META_COLS = {"Timestamp", "Utente", "Index", "Persona"}
# Tutti i criteri definiti nei pesi
criteri_green_all = [c for c in df_pesi_green.columns if c not in META_COLS]
# Filtriamo solo quelli presenti anche nel foglio di valutazione verde
criteri_green = [c for c in criteri_green_all if c in df_val_green.columns]

# Calcoliamo i pesi usando solo i criteri effettivi
df_pesi_green_numeric = df_pesi_green[criteri_green].apply(pd.to_numeric, errors='coerce')
pesi_green = df_pesi_green_numeric.mean()

# Media dei voti per parco sui criteri effettivi
media_green = df_val_green.groupby("Parco")[criteri_green].mean()

# Merge con info e calcolo punteggio verde
map_df_green = pd.merge(
    df_info, media_green,
    left_on="Nome del Parco", right_index=True, how="inner"
)
# Ponderazione solo sui criteri effettivi
df_weights = pesi_green[criteri_green]
map_df_green['punteggio_green'] = map_df_green[criteri_green].mul(df_weights, axis=1).sum(axis=1)
# Assicuriamo lat/long numerici
map_df_green = to_numeric_df(map_df_green, ["Latitudine", "Longitudine"])

# ------------------------------------------------------------------
# ------------------------------------------------------------------
# 5️⃣  Merge for Combined Analysis
# ------------------------------------------------------------------
# Uniamo standard + green per l'analisi combinata
df_combi = map_df_std.merge(
    map_df_green[['Nome del Parco','punteggio_green'] + criteri_green],
    on='Nome del Parco', how='inner'
)
map_df_combi = df_combi.copy()

# Applica filtro quartiere anche alla combinata
if quart_sel != 'Tutti':
    map_df_combi = map_df_combi[map_df_combi['Quartiere']==quart_sel]

# ------------------------------------------------------------------
# 📍 Mappa Punteggi
elif page_sel == "📍 Mappa Punteggi":
    st.subheader("Mappa dei parchi (Citizen)")
    df = map_df_std.assign(
        color = map_df_std['punteggio_std'].apply(lambda p: [max(0,255-int(p*50)), min(255,int(p*50)), 0, 160]),
        radius = map_df_std['punteggio_std'] * 100
    )
    view = pdk.ViewState(latitude=45.6983, longitude=9.6773, zoom=13)
    st.pydeck_chart(
        pdk.Deck(
            map_style='mapbox://styles/mapbox/outdoors-v11',
            initial_view_state=view,
            layers=[
                pdk.Layer('ScatterplotLayer', data=df,
                          get_position='[Longitudine, Latitudine]',
                          get_fill_color='color',
                          get_radius='radius', pickable=True)
            ],
            tooltip={'text': '{Nome del Parco}\nCitizen: {punteggio_std:.2f}'}
        ), key='map_citizen'
    )

# 📊 Classifica Parchi
elif page_sel == "📊 Classifica Parchi":
    st.subheader("Classifica dei parchi per Citizen Score")
    st.dataframe(
        map_df_std[['Nome del Parco','Quartiere','punteggio_std']]
        .sort_values(by='punteggio_std', ascending=False).round(2),
        key='table_citizen'
    )

# 📈 Analisi Aggregata
elif page_sel == "📈 Analisi Aggregata":
    st.subheader("Statistiche & Radar (Citizen)")
    media_vals = df_val_f[CRITERI_STD].mean()
    fig_bar = px.bar(x=CRITERI_STD, y=media_vals, labels={'x':'Criterio','y':'Media'})
    st.plotly_chart(fig_bar, use_container_width=True, key='bar_agg')
    radar = go.Figure(go.Scatterpolar(
        r=media_vals.tolist()+[media_vals.iloc[0]],
        theta=CRITERI_STD+[CRITERI_STD[0]], fill='toself'))
    radar.update_layout(polar=dict(radialaxis=dict(range=[0,5])), showlegend=False)
    st.plotly_chart(radar, use_container_width=True, key='radar_agg')

# 🔀 Combina Green & Citizen
elif page_sel == "🔀 Combina Green & Citizen":
    st.subheader("Combinazione Green vs Citizen")
    # Definisci mid-point per quadranti
    x_mid = map_df_combi['punteggio_green'].mean()
    y_mid = map_df_combi['punteggio_std'].mean()

    def label_quadrant(row):
        x, y = row['punteggio_green'], row['punteggio_std']
        if x>=x_mid and y>=y_mid: return 'Top Right'
        if x< x_mid and y>=y_mid: return 'Top Left'
        if x< x_mid and y< y_mid: return 'Bottom Left'
        return 'Bottom Right'

    map_df_combi['quadrante'] = map_df_combi.apply(label_quadrant, axis=1)
    # Scatter
    fig_sc = px.scatter(
        map_df_combi, x='punteggio_green', y='punteggio_std',
        size='Manutenzione', color='quadrante', hover_name='Nome del Parco',
        labels={'punteggio_green':'Score Green','punteggio_std':'Citizen Score'}
    )
    fig_sc.add_vline(x=x_mid, line_dash='dash')
    fig_sc.add_hline(y=y_mid, line_dash='dash')
    st.plotly_chart(fig_sc, use_container_width=True, height=600, key='scatter_combi')

    # Mappa combinata
    st.subheader("Mappa Combinata")
    map_df_combi['color_cit'] = map_df_combi['punteggio_std'].apply(
        lambda p: [max(0,255-int(p*50)), min(255,int(p*50)), 0, 160]
    )
    map_df_combi['radius_green'] = map_df_combi['punteggio_green'] * 100
    st.pydeck_chart(
        pdk.Deck(
            map_style='mapbox://styles/mapbox/outdoors-v11',
            initial_view_state=pdk.ViewState(latitude=45.6983, longitude=9.6773, zoom=13),
            layers=[
                pdk.Layer('ScatterplotLayer', data=map_df_combi,
                          get_position='[Longitudine, Latitudine]',
                          get_fill_color='color_cit',
                          get_radius='radius_green', pickable=True)
            ],
            tooltip={'text':'{Nome del Parco}\nGreen: {punteggio_green:.2f}\nCitizen: {punteggio_std:.2f}\nQuadrante: {quadrante}'}
        ), key='map_combi'
    )

# 📉 Correlazione Criteri
elif page_sel == "📉 Correlazione Criteri":
    st.subheader("Correlazione Criteri Citizen")
    corr_std = df_val_f[CRITERI_STD].corr()
    fig1 = px.imshow(corr_std, text_auto=True, aspect='equal',
                     color_continuous_scale='RdBu', zmin=-1, zmax=1)
    st.plotly_chart(fig1, use_container_width=True)
    st.subheader("Correlazione Criteri Verde")
    corr_g = df_val_green[criteri_green].corr()
    fig2 = px.imshow(corr_g, text_auto=True, aspect='equal',
                     color_continuous_scale='RdBu', zmin=-1, zmax=1)
    st.plotly_chart(fig2, use_container_width=True)

# 📋 Tabella Completa
elif page_sel == "📋 Tabella Completa":
    st.subheader("Dati Grezzi")
    st.markdown("**Valutazioni Citizen**")
    st.dataframe(df_val_f)
    st.markdown("**Valutazioni Verde**")
    st.dataframe(df_val_green)
    st.markdown("**Pesi Citizen**")
    st.dataframe(df_pesi_f)
    st.markdown("**Pesi Verde**")
    st.dataframe(df_pesi_green)


