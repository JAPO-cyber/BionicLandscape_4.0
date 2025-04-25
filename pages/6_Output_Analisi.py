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

# Fix comma decimals in specified columns
def fix_decimal_commas(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        df[c] = (
            df[c].astype(str)
                 .str.replace(",", ".", regex=False)
                 .pipe(pd.to_numeric, errors="coerce")
        )
    return df

st.set_page_config(page_title="6. Analisi e risultati", layout="wide")
apply_custom_style()
st.title("6. Analisi e visualizzazione dei risultati")

# ------------------------------------------------------------------
# 1️⃣ Load and clean
# ------------------------------------------------------------------
dfs = load_data()
df_val = dfs["df_valutazioni"]
df_pesi = dfs["df_pesi"]
df_info = dfs["df_info"]
df_val_green = dfs["df_valutazioni_green"]
df_pesi_green = dfs["df_pesi_green"]

for df in (df_val, df_pesi, df_info, df_val_green, df_pesi_green):
    df.rename(columns=lambda c: str(c).strip(), inplace=True)

# Rename long fields
rename_map = {
    "Funzione sociale (es. luoghi di incontro)": "Funzione sociale",
    "Funzione ambientale (es. ombra, qualità aria)": "Funzione ambientale",
}
df_val.rename(columns=rename_map, inplace=True)
df_pesi.rename(columns=rename_map, inplace=True)

# ------------------------------------------------------------------
# 2️⃣ Correct decimal commas in weights
# ------------------------------------------------------------------
df_pesi = fix_decimal_commas(df_pesi, CRITERI_STD)
# Converte percentuali (0-100) in frazioni (0-1)
df_pesi[CRITERI_STD] = df_pesi[CRITERI_STD] / 100

# green criteria
meta_cols = {"Timestamp", "Utente", "Index", "Persona"}
criteri_green = [c for c in df_pesi_green.columns if c not in meta_cols]
df_pesi_green = fix_decimal_commas(df_pesi_green, criteri_green)
# Converte percentuali (0-100) in frazioni (0-1)
df_pesi_green[criteri_green] = df_pesi_green[criteri_green] / 100
meta_cols = {"Timestamp", "Utente", "Index", "Persona"}
criteri_green = [c for c in df_pesi_green.columns if c not in meta_cols]
df_pesi_green = fix_decimal_commas(df_pesi_green, criteri_green)

# ------------------------------------------------------------------
# 3️⃣ Sidebar filters
# ------------------------------------------------------------------
st.sidebar.header("Filtri")
page_sel = st.sidebar.radio("Vista:", [
    "📍 Mappa Punteggi", "📊 Classifica Parchi",
    "📈 Analisi Aggregata", "🔀 Combina Green & Citizen",
    "📉 Correlazione Criteri", "📋 Tabella Completa"
])
tav_sel = st.sidebar.selectbox(
    "Tavola rotonda:", ["Tutte"] + df_val["Tavola rotonda"].dropna().unique().tolist()
)
quart_sel = st.sidebar.selectbox(
    "Quartiere:", ["Tutti"] + df_info["Quartiere"].dropna().unique().tolist()
)
# filter
if tav_sel != "Tutte":
    mask = df_val["Tavola rotonda"] == tav_sel
    df_val = df_val[mask]
    df_pesi = df_pesi[mask]

# ------------------------------------------------------------------
# 4️⃣ Compute Standard scores
# ------------------------------------------------------------------
media_std = df_val.groupby("Parco")[CRITERI_STD].mean()
std_std   = df_val.groupby("Parco")[CRITERI_STD].std()
pesi_std  = df_pesi[CRITERI_STD].mean()
media_std["punteggio_std"] = media_std.mul(pesi_std).sum(axis=1)
map_df_std = (
    media_std.reset_index()
    .merge(df_info, left_on="Parco", right_on="Nome del Parco", how="inner")
)
map_df_std = to_numeric_df(map_df_std, ["Latitudine", "Longitudine"])
if quart_sel != "Tutti":
    map_df_std = map_df_std[map_df_std["Quartiere"]==quart_sel]

# ------------------------------------------------------------------
# 5️⃣ Compute Green scores
# ------------------------------------------------------------------
# Intersezione criteri green presenti nelle valutazioni
criteri_green_eff = [c for c in criteri_green if c in df_val_green.columns]

# Media dei voti per parco sui criteri effettivi
media_green = df_val_green.groupby("Parco")[criteri_green_eff].mean()
# Pesi solo per criteri effettivi
pesi_green = df_pesi_green[criteri_green_eff].mean()

# Merge con info e calcolo punteggio verde
map_df_green = (
    df_info.merge(media_green, left_on="Nome del Parco", right_index=True, how="inner")
)
map_df_green["punteggio_green"] = (
    map_df_green[criteri_green_eff].mul(pesi_green, axis=1).sum(axis=1)
)
map_df_green = to_numeric_df(map_df_green, ["Latitudine", "Longitudine"])
if quart_sel != "Tutti":
    map_df_green = map_df_green[map_df_green["Quartiere"]==quart_sel]

# ------------------------------------------------------------------
if page_sel == "📍 Mappa Punteggi":
    st.subheader("Mappa Citizen")
    df = map_df_std.assign(
        color = map_df_std['punteggio_std'].apply(
            lambda p: [max(0,255-int(p*50)), min(255,int(p*50)),0,160]
        ),
        radius = map_df_std['punteggio_std'] * 50
    )
    st.pydeck_chart(
        pdk.Deck(
            map_style='mapbox://styles/mapbox/outdoors-v11',
            initial_view_state=pdk.ViewState(latitude=45.6983, longitude=9.6773, zoom=13),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer", df,
                    get_position="[Longitudine, Latitudine]",
                    get_fill_color="color", get_radius="radius",
                    pickable=True
                )
            ],
            tooltip={"text":"{Nome del Parco}\nCitizen: {punteggio_std:.2f}"}
        ), key='map_citizen'
    )

elif page_sel == "📊 Classifica Parchi":
    st.subheader("Classifica Citizen")
    st.dataframe(
        map_df_std[['Nome del Parco','Quartiere','punteggio_std']]
        .sort_values('punteggio_std',ascending=False).round(2), key='table_citizen'
    )

elif page_sel == "📈 Analisi Aggregata":
    st.subheader("Analisi Aggregata Citizen")
    avg = df_val[CRITERI_STD].mean()
    fig = px.bar(x=CRITERI_STD,y=avg, labels={'x':'Criterio','y':'Media'})
    st.plotly_chart(fig, use_container_width=True, key='bar_agg')
    radar = go.Figure(go.Scatterpolar(
        r=list(avg)+[avg.iloc[0]], theta=list(CRITERI_STD)+[CRITERI_STD[0]], fill='toself'
    ))
    radar.update_layout(polar=dict(radialaxis=dict(range=[0,5])), showlegend=False)
    st.plotly_chart(radar, use_container_width=True, key='radar_agg')

elif page_sel == "🔀 Combina Green & Citizen":
    st.subheader("Combinazione Green vs Citizen")
    x_mid = map_df_combi['punteggio_green'].mean()
    y_mid = map_df_combi['punteggio_std'].mean()
    def lbl(r):
        x,y=r['punteggio_green'],r['punteggio_std']
        if x>=x_mid and y>=y_mid: return 'Top Right'
        if x< x_mid and y>=y_mid: return 'Top Left'
        if x< x_mid and y< y_mid: return 'Bottom Left'
        return 'Bottom Right'
    map_df_combi['quadrante']=map_df_combi.apply(lbl,axis=1)
    fig2=px.scatter(
        map_df_combi,x='punteggio_green',y='punteggio_std',size='Manutenzione',
        color='quadrante',hover_name='Nome del Parco',
        labels={'punteggio_green':'Score Green','punteggio_std':'Citizen'}
    )
    fig2.add_vline(x=x_mid,line_dash='dash')
    fig2.add_hline(y=y_mid,line_dash='dash')
    st.plotly_chart(fig2,use_container_width=True,key='scatter_combi',height=600)
    st.subheader("Mappa Combinata")
    dfm=map_df_combi.assign(
        color_cit=map_df_combi['punteggio_std'].apply(
            lambda p:[max(0,255-int(p*50)),min(255,int(p*50)),0,160]
        ),radius_green=map_df_combi['punteggio_green']*50
    )
    st.pydeck_chart(
        pdk.Deck(
            map_style='mapbox://styles/mapbox/outdoors-v11',
            initial_view_state=pdk.ViewState(latitude=45.6983,longitude=9.6773,zoom=13),
            layers=[pdk.Layer('ScatterplotLayer',data=dfm,
                             get_position='[Longitudine, Latitudine]',
                             get_fill_color='color_cit',
                             get_radius='radius_green',pickable=True)
                   ],
            tooltip={"text":"{Nome del Parco}\nGreen: {punteggio_green:.2f}\nCitizen: {punteggio_std:.2f}\nQuadrante: {quadrante}"}
        ),key='map_combi'
    )

elif page_sel == "📉 Correlazione Criteri":
    st.subheader("Correlazione Standard & Verde")
    c1=df_val[CRITERI_STD].corr()
    st.plotly_chart(px.imshow(c1,text_auto=True,aspect='equal',color_continuous_scale='RdBu',zmin=-1,zmax=1),key='corr1')
    c2=df_val_green[criteri_green].corr()
    st.plotly_chart(px.imshow(c2,text_auto=True,aspect='equal',color_continuous_scale='RdBu',zmin=-1,zmax=1),key='corr2')

elif page_sel == "📋 Tabella Completa":
    st.subheader("Dati Grezzi")
    st.write("**Valutazioni Citizen**")
    st.dataframe(df_val,key='raw_val')
    st.write("**Valutazioni Verde**")
    st.dataframe(df_val_green,key='raw_valg')
    st.write("**Pesi Citizen**")
    st.dataframe(df_pesi,key='raw_pesi')
    st.write("**Pesi Verde**")
    st.dataframe(df_pesi_green,key='raw_pesig')


