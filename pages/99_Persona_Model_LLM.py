import streamlit as st
import pandas as pd
import plotly.express as px
from kmodes.kprototypes import KPrototypes
from lib.google_sheet import get_sheet_by_name

# ✅ Import corretto per Gemini
from google import genai

st.set_page_config(page_title="Cluster Insight", layout="wide")
st.title("📊 Analisi dei Cluster dei Partecipanti")

# ✅ Carica i dati da Google Sheets
sheet_profiles = get_sheet_by_name("Dati_Partecipante", "Partecipanti")
df = sheet_profiles

if df is None:
    st.error("❌ Errore nel caricamento del foglio 'Partecipanti'. Controlla che esista e che il nome sia corretto.")
    st.stop()

# Selezione colonne rilevanti per il clustering
columns = [
    "Età", "Professione", "Formazione", "Ruolo", "Ambito", "Esperienza",
    "Coinvolgimento", "Conoscenza tema", "Motivazione", "Obiettivo", 
    "Visione", "Valori", "Canale preferito"
]
df = df[columns].dropna().reset_index(drop=True)

# Separazione numeriche e categoriche
df_encoded = df.copy()
categorical_cols = df_encoded.select_dtypes(include='object').columns.tolist()
numerical_cols = df_encoded.select_dtypes(exclude='object').columns.tolist()

for col in categorical_cols:
    df_encoded[col] = df_encoded[col].astype('category').cat.codes

# Clustering
kproto = KPrototypes(n_clusters=4, init='Huang', random_state=42)
categorical_idx = [df.columns.get_loc(col) for col in categorical_cols]
df['Cluster'] = kproto.fit_predict(df_encoded, categorical=categorical_idx)

# Visualizzazione 3D
fig = px.scatter_3d(df, x="Età", y="Coinvolgimento", z="Conoscenza tema", 
                    color=df['Cluster'].astype(str), symbol="Ruolo", title="Clusterizzazione 3D")
st.plotly_chart(fig)

# Descrizione AI con Gemini
if st.button("🧠 Genera insight con Gemini"):
    api_key = st.secrets["gemini"]["api_key"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    cluster_summary = df.groupby('Cluster').agg(lambda x: x.mode()[0] if x.dtype == 'object' else x.mean(numeric_only=True))

    prompt = f"""
    Stiamo analizzando dati raccolti da cittadini coinvolti in un progetto urbano.
    Sono stati suddivisi in 4 cluster sulla base di dati misti (età, ruolo, motivazione, ecc).
    Genera per ciascun cluster un profilo descrittivo con:
    - Nome simbolico del cluster
    - Breve descrizione (2-3 righe)
    - 2-3 azioni consigliate per coinvolgerli
    - Canale comunicativo preferito
    - Tipologia di spazio verde ideale

    Dati medi e modali per cluster:
    {cluster_summary.to_string()}
    """

    response = model.generate_content(prompt)
    st.markdown("### 💬 Insight generati con Gemini:")
    st.markdown(response.text)

