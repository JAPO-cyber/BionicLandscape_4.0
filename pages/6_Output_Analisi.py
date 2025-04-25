import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go

from lib.style import apply_custom_style
from lib.google_sheet import get_sheet_by_name

# -------------------- Utility & Config --------------------
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
    return {k: pd.DataFrame(get_sheet_by_name("Dati_Partecipante", v).get_all_records()) for k, v in sheets.items()}

def fix_decimal_commas(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        df[c] = df[c].astype(str).str.replace(",", ".", regex=False)
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# -------------------- App Initialization --------------------
st.set_page_config(page_title="6. Analisi e risultati", layout="wide")
apply_custom_style()
st.title("6. Analisi e visualizzazione dei risultati")

# -------------------- Load & Clean --------------------
dfs = load_data()
df_val, df_pesi, df_info = dfs['df_valutazioni'], dfs['df_pesi'], dfs['df_info']
df_val_green, df_pesi_green = dfs['df_valutazioni_green'], dfs['df_pesi_green']
for df in (df_val, df_pesi, df_info, df_val_green, df_pesi_green): df.rename(columns=lambda c: str(c).strip(), inplace=True)
rename_map = {"Funzione sociale (es. luoghi di incontro)": "Funzione sociale", "Funzione ambientale (es. ombra, qualità aria)": "Funzione ambientale"}
df_val.rename(columns=rename_map, inplace=True); df_pesi.rename(columns=rename_map, inplace=True)

# -------------------- Normalize Weights --------------------
CRITERI_STD = ["Accessibilità del verde","Biodiversità","Manutenzione e pulizia","Funzione sociale","Funzione ambientale"]
fix_decimal_commas(df_pesi, CRITERI_STD); df_pesi[CRITERI_STD] /= 100
meta_cols = {"Timestamp","Utente","Index","Persona"}
criteri_green = [c for c in df_pesi_green.columns if c not in meta_cols]
fix_decimal_commas(df_pesi_green, criteri_green); df_pesi_green[criteri_green] /= 100

# -------------------- Sidebar Filters --------------------
st.sidebar.header("Filtri")
page_sel = st.sidebar.radio("Vista:", ["📍 Mappa Punteggi","📊 Classifica Parchi","📈 Analisi Aggregata","🔀 Combina Green & Citizen","📉 Correlazione Criteri","📋 Tabella Completa"] )
tav_sel = st.sidebar.selectbox("Tavola rotonda:", ["Tutte"] + df_val["Tavola rotonda"].dropna().unique().tolist())
quart_sel = st.sidebar.selectbox("Quartiere:", ["Tutti"] + df_info["Quartiere"].dropna().unique().tolist())
if tav_sel != "Tutte": mask = df_val["Tavola rotonda"]==tav_sel; df_val, df_pesi = df_val[mask], df_pesi[mask]

# -------------------- Compute Citizen Score --------------------
media_std = df_val.groupby("Parco")[CRITERI_STD].mean(); pesi_std = df_pesi[CRITERI_STD].mean()
media_std["punteggio_std"] = media_std.mul(pesi_std).sum(axis=1)
map_df_std = media_std.reset_index().merge(df_info, left_on="Parco", right_on="Nome del Parco").pipe(to_numeric_df, ["Latitudine","Longitudine"])
if quart_sel != "Tutti": map_df_std = map_df_std[map_df_std["Quartiere"]==quart_sel]

# -------------------- Compute Green Score --------------------
criteri_green_eff = [c for c in criteri_green if c in df_val_green.columns]
media_green = df_val_green.groupby("Parco")[criteri_green_eff].mean(); pesi_green = df_pesi_green[criteri_green_eff].mean()
map_df_green = df_info.merge(media_green, left_on="Nome del Parco", right_index=True)
map_df_green["punteggio_green"] = map_df_green[criteri_green_eff].mul(pesi_green,axis=1).sum(axis=1)
map_df_green = to_numeric_df(map_df_green, ["Latitudine","Longitudine"])
if quart_sel != "Tutti": map_df_green = map_df_green[map_df_green["Quartiere"]==quart_sel]

# -------------------- Merge Combined --------------------
map_df_combi = map_df_std.merge(map_df_green[["Nome del Parco","punteggio_green"]+criteri_green_eff], on="Nome del Parco")
if quart_sel != "Tutti": map_df_combi = map_df_combi[map_df_combi["Quartiere"]==quart_sel]

# -------------------- Render Views --------------------
# Mappa Citizen
if page_sel=="📍 Mappa Punteggi":
    st.subheader("Mappa Citizen")
    df_map = map_df_std.assign(color=map_df_std['punteggio_std'].apply(lambda p:[max(0,255-int(p*50)),min(255,int(p*50)),0,160]), radius=map_df_std['punteggio_std']*50)
    st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/outdoors-v11', initial_view_state=pdk.ViewState(45.6983,9.6773,13), layers=[pdk.Layer('ScatterplotLayer', data=df_map, get_position='[Longitudine, Latitudine]', get_fill_color='color', get_radius='radius', pickable=True)], tooltip={'text':'{Nome del Parco}
Citizen: {punteggio_std:.2f}'}), key='map_citizen')

# Classifica
elif page_sel=="📊 Classifica Parchi":
    st.subheader("Classifica Citizen")
    st.dataframe(map_df_std[['Nome del Parco','Quartiere','punteggio_std']].sort_values('punteggio_std',ascending=False).round(2), key='table_citizen')

# Analisi Aggregata
elif page_sel=="📈 Analisi Aggregata":
    st.subheader("Analisi Aggregata Citizen")
    avg = df_val[CRITERI_STD].mean()
    st.plotly_chart(px.bar(x=CRITERI_STD,y=avg,labels={'x':'Criterio','y':'Media'}), use_container_width=True, key='bar_agg')
    radar = go.Figure(go.Scatterpolar(r=list(avg)+[avg.iloc[0]], theta=list(CRITERI_STD)+[CRITERI_STD[0]], fill='toself'))
    radar.update_layout(polar=dict(radialaxis=dict(range=[0,5])), showlegend=False)
    st.plotly_chart(radar, use_container_width=True, key='radar_agg')

# Combina
elif page_sel=="🔀 Combina Green & Citizen":
    st.subheader("Combinazione Green vs Citizen")
    x_mid,y_mid=2.5,2.5
    # Nuovi nomi quadranti
    quadrant_names={
        'Top Right':'Priorità condivisa',
        'Top Left':'Valore Sociale',
        'Bottom Left':'Rischio Strategico',
        'Bottom Right':'Tensione ecologica'
    }
    map_df_combi['quadrante']=map_df_combi.apply(
        lambda r: quadrant_names['Top Right']     if r['punteggio_green']>=x_mid and r['punteggio_std']>=y_mid else
                  quadrant_names['Top Left']      if r['punteggio_green']< x_mid and r['punteggio_std']>=y_mid else
                  quadrant_names['Bottom Left']   if r['punteggio_green']< x_mid and r['punteggio_std']< y_mid else
                  quadrant_names['Bottom Right'], axis=1)
    fig=px.scatter(
        map_df_combi, x='punteggio_green', y='punteggio_std',
        size='Manutenzione', color='quadrante', hover_name='Nome del Parco',
        labels={'punteggio_green':'Score Green','punteggio_std':'Citizen Score'},
        category_orders={'quadrante': list(quadrant_names.values())}
    )
    fig.update_xaxes(range=[0,5]); fig.update_yaxes(range=[0,5])
    fig.add_vline(x=x_mid, line_dash='dash', line_color='gray'); fig.add_hline(y=y_mid, line_dash='dash', line_color='gray')
    st.plotly_chart(fig, use_container_width=True, height=600, key='scatter_combi')
    st.subheader("Mappa Combinata")
    dfc=map_df_combi.assign(
        color_cit=map_df_combi['punteggio_std'].apply(lambda p:[max(0,255-int(p*50)),min(255,int(p*50)),0,160]),
        radius_green=map_df_combi['punteggio_green']*50
    )
    # Tooltip corretto con escape 

    tooltip_text = '{Nome del Parco}
Green: {punteggio_green:.2f}
Citizen: {punteggio_std:.2f}
Quadrante: {quadrante}'
    st.pydeck_chart(
        pdk.Deck(
            map_style='mapbox://styles/mapbox/outdoors-v11',
            initial_view_state=pdk.ViewState(45.6983,9.6773,13),
            layers=[pdk.Layer(
                'ScatterplotLayer', data=dfc,
                get_position='[Longitudine, Latitudine]',
                get_fill_color='color_cit', get_radius='radius_green', pickable=True
            )],
            tooltip={'text': tooltip_text}
        ), key='map_combi'
    )
elif page_sel=="🔀 Combina Green & Citizen":
    st.subheader("Combinazione Green vs Citizen")
    x_mid,y_mid=2.5,2.5; quadrant_names={'Top Right':'Leader Sostenibili','Top Left':'Verdi Puristi','Bottom Left':'Critici Ecologici','Bottom Right':'Cittadini Fedeli'}
    map_df_combi['quadrante']=map_df_combi.apply(lambda r: quadrant_names['Top Right'] if r['punteggio_green']>=x_mid and r['punteggio_std']>=y_mid else quadrant_names['Top Left'] if r['punteggio_green']<x_mid and r['punteggio_std']>=y_mid else quadrant_names['Bottom Left'] if r['punteggio_green']<x_mid and r['punteggio_std']<y_mid else quadrant_names['Bottom Right'], axis=1)
    fig=px.scatter(map_df_combi, x='punteggio_green',y='punteggio_std', size='Manutenzione', color='quadrante', hover_name='Nome del Parco', labels={'punteggio_green':'Score Green','punteggio_std':'Citizen Score'}, category_orders={'quadrante':list(quadrant_names.values())})
    fig.update_xaxes(range=[0,5]); fig.update_yaxes(range=[0,5])
    fig.add_vline(x=x_mid,line_dash='dash',line_color='gray'); fig.add_hline(y=y_mid,line_dash='dash',line_color='gray')
    st.plotly_chart(fig,use_container_width=True, height=600, key='scatter_combi')
    st.subheader("Mappa Combinata")
    dfc=map_df_combi.assign(color_cit=map_df_combi['punteggio_std'].apply(lambda p:[max(0,255-int(p*50)),min(255,int(p*50)),0,160]), radius_green=map_df_combi['punteggio_green']*50)
    st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/outdoors-v11', initial_view_state=pdk.ViewState(45.6983,9.6773,13), layers=[pdk.Layer('ScatterplotLayer',data=dfc,get_position='[Longitudine, Latitudine]',get_fill_color='color_cit',get_radius='radius_green',pickable=True)], tooltip={'text':'{Nome del Parco}
Green: {punteggio_green:.2f}
Citizen: {punteggio_std:.2f}
Quadrante: {quadrante}'}), key='map_combi')

# Correlazione
elif page_sel=="📉 Correlazione Criteri":
    st.subheader("Correlazione Standard & Verde")
    c1=df_val[CRITERI_STD].corr(); st.plotly_chart(px.imshow(c1,text_auto=True,aspect='equal',color_continuous_scale='RdBu',zmin=-1,zmax=1), key='corr1')
    c2=df_val_green[criteri_green_eff].corr(); st.plotly_chart(px.imshow(c2,text_auto=True,aspect='equal',color_continuous_scale='RdBu',zmin=-1,zmax=1), key='corr2')

# Tabella Completa
elif page_sel=="📋 Tabella Completa":
    st.subheader("Dati Grezzi")
    st.write("**Valutazioni Citizen**"); st.dataframe(df_val, key='raw_val')
    st.write("**Valutazioni Verde**"); st.dataframe(df_val_green, key='raw_valg')
    st.write("**Pesi Citizen (0-1)**"); st.dataframe(df_pesi[CRITERI_STD].round(2), key='raw_pesi')
    st.write("**Pesi Verde (0-1)**"); st.dataframe(df_pesi_green[criteri_green_eff].round(2), key='raw_pesig')


