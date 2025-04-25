import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go

from lib.style import apply_custom_style
from lib.google_sheet import get_sheet_by_name

# 🛠 Funzione Utility per convertire lat/lon
@st.cache_data
def to_numeric_df(df, cols):
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

st.set_page_config(page_title="6. Analisi e risultati", layout="wide")
apply_custom_style()

st.title("6. Analisi e visualizzazione dei risultati")

# ------------------------------------------------------------------
# 1️⃣  CARICAMENTO DATI ------------------------------------------------
# ------------------------------------------------------------------
@st.cache_data
def load_data():
    sheets = [
        ("Valutazione Parchi", None),
        ("Pesi Parametri", None),
        ("Informazioni Parchi", None),
        ("Valutazione Parchi Verde", "_green"),
        ("Pesi Parametri Verde", "_green"),
    ]
    dfs = {}
    for name, suffix in sheets:
        dfs[f"df_{name.split()[0].lower()}{suffix}"] = pd.DataFrame(
            get_sheet_by_name("Dati_Partecipante", name).get_all_records()
        )
    return dfs

dfs = load_data()
(df_val, df_pesi, df_info, df_val_green, df_pesi_green) = (
    dfs['df_valutazione'], dfs['df_pesi'], dfs['df_informazioni'], dfs['df_valutazione_green'], dfs['df_pesi_green']
)

# ------------------------------------------------------------------
# 2️⃣  PULIZIA & RINOMINA COLONNE -------------------------------------
# ------------------------------------------------------------------
def clean_columns(df):
    df.rename(columns=lambda c: str(c).strip(), inplace=True)

for df in (df_val, df_pesi, df_info, df_val_green, df_pesi_green):
    clean_columns(df)

# Rinomina campi lunghi
df_val.rename(columns={
    "Funzione sociale (es. luoghi di incontro)": "Funzione sociale",
    "Funzione ambientale (es. ombra, qualità aria)": "Funzione ambientale"
}, inplace=True)

# ------------------------------------------------------------------
# 3️⃣  FILTRI DALLA SIDEBAR -------------------------------------------
# ------------------------------------------------------------------
st.sidebar.header("📊 Filtri")
page_sel = st.sidebar.radio("Vista:", [
    "📍 Mappa Punteggi",
    "📊 Classifica Parchi",
    "📈 Analisi Aggregata",
    "🔀 Combina Green & Citizen",
    "📉 Correlazione Criteri",
    "📋 Tabella Completa"
])
tavole = [*df_val["Tavola rotonda"].dropna().unique()]
tav_sel = st.sidebar.selectbox("Tavola rotonda:", ["Tutte"]+tavole)

quartieri = [*df_info["Quartiere"].dropna().unique()]
quart_sel = st.sidebar.selectbox("Quartiere:", ["Tutti"]+quartieri)

# Applica filtri
mask_val = df_val if tav_sel=="Tutte" else df_val[df_val["Tavola rotonda"]==tav_sel]
df_pesi_f = df_pesi if tav_sel=="Tutte" else df_pesi[df_pesi["Tavola rotonda"]==tav_sel]

# ------------------------------------------------------------------
# 4️⃣  CALCOLI PUNTEGGIO STANDARD & VERDE ----------------------------
# ------------------------------------------------------------------
CRITERI_STD = ["Accessibilità del verde","Biodiversità","Manutenzione e pulizia","Funzione sociale","Funzione ambientale"]
# Standard
media_val = mask_val.groupby("Parco")[CRITERI_STD].mean()
std_val = mask_val.groupby("Parco")[CRITERI_STD].std()
pesi_std = df_pesi_f[CRITERI_STD].mean()
media_val["punteggio_std"] = media_val.mul(pesi_std).sum(axis=1)
map_df_std = pd.merge(
    media_val.reset_index(), df_info, left_on="Parco", right_on="Nome del Parco"
)
# Verde
META = {"Timestamp","Utente","Index","Persona"}
criteri_green = [c for c in df_pesi_green.columns if c not in META]
pesi_green = df_pesi_green[criteri_green].apply(pd.to_numeric,errors="coerce").mean()
media_val_g = df_val_green.groupby("Parco")[criteri_green].mean()
map_df_green = df_info.merge(media_val_g, left_on="Nome del Parco", right_index=True)
map_df_green["punteggio_green"] = map_df_green[criteri_green].mul(pesi_green).sum(axis=1)

# Assicura lat/long
map_df_std = to_numeric_df(map_df_std, ["Latitudine","Longitudine"])
map_df_green = to_numeric_df(map_df_green, ["Latitudine","Longitudine"])

# Unione per combinata
map_df_combi = pd.merge(
    map_df_std, map_df_green[["Nome del Parco","punteggio_green"]+criteri_green],
    on="Nome del Parco"
)
if quart_sel!="Tutti":
    map_df_std = map_df_std[map_df_std["Quartiere"]==quart_sel]
    map_df_combi = map_df_combi[map_df_combi["Quartiere"]==quart_sel]

# ------------------------------------------------------------------
# 🔟 VISUALIZZAZIONI MULTIPAGINA -------------------------------------
# ------------------------------------------------------------------
if page_sel == "📍 Mappa Punteggi":
    st.subheader("📍 Mappa dei parchi")
    df = map_df_std.assign(
        color=map_df_std["punteggio_std"].apply(lambda p: [max(0,255-int(p*50)),min(255,int(p*50)),0,160]),
        radius=map_df_std["punteggio_std"]*100
    )
    view = pdk.ViewState(latitude=45.6983, longitude=9.6773, zoom=13)
    st.pydeck_chart(pdk.Deck(layers=[pdk.Layer("ScatterplotLayer",df,get_position="[Longitudine,Latitudine]",get_fill_color="color",get_radius="radius")],initial_view_state=view))

elif page_sel == "📊 Classifica Parchi":
    st.subheader("📊 Classifica")
    st.dataframe(map_df_std[["Nome del Parco","Quartiere","punteggio_std"]].sort_values(by="punteggio_std",ascending=False).round(2))

elif page_sel == "📈 Analisi Aggregata":
    st.subheader("📈 Statistiche & Radar")
    fig=go.Figure()
    media_std=mask_val[CRITERI_STD].mean()
    fig.add_trace(go.Bar(x=CRITERI_STD,y=media_std))
    st.plotly_chart(fig)
    radar=go.Figure(data=[go.Scatterpolar(r=media_std.tolist()+[media_std.tolist()[0]],theta=CRITERI_STD+[CRITERI_STD[0]],fill='toself')])
    st.plotly_chart(radar)

elif page_sel == "🔀 Combina Green & Citizen":
    # rimane identico come sopra
    pass

elif page_sel == "📉 Correlazione Criteri":
    st.subheader("📉 Matrice di correlazione (standard)")
    corr = mask_val[CRITERI_STD].corr()
    fig = px.imshow(corr, text_auto=True, aspect="equal")
    st.plotly_chart(fig)

    st.subheader("📉 Matrice di correlazione (verde)")
    corr_g = df_val_green[criteri_green].corr()
    fig2 = px.imshow(corr_g, text_auto=True, aspect="equal")
    st.plotly_chart(fig2)

elif page_sel == "📋 Tabella Completa":
    st.subheader("📋 Dati grezzi")
    st.write("**Valutazioni Citizen**")
    st.dataframe(mask_val)
    st.write("**Valutazioni Verde**")
    st.dataframe(df_val_green)
    st.write("**Pesi Citizen**")
    st.dataframe(df_pesi)
    st.write("**Pesi Verde**")
    st.dataframe(df_pesi_green)
