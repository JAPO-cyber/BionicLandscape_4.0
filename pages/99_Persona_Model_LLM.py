import streamlit as st
import pandas as pd
import plotly.express as px
from kmodes.kprototypes import KPrototypes
from lib.google_sheet import get_sheet_by_name
import re
import json

# ✅ Import SDK Gemini
from google import genai

# 🛠️ Impostazioni iniziali
st.set_page_config(page_title="Cluster e Analisi Partecipanti", layout="wide")

# 🔄 Tabs per separare analisi
tab1, tab2 = st.tabs(["📊 Cluster Insight", "📌 Pareto & Ishikawa"])

# ✅ Carica i dati da Google Sheets
sheet_profiles = get_sheet_by_name("Dati_Partecipante", "Partecipanti")
data = sheet_profiles.get_all_records()
df = pd.DataFrame(data)

if df is None or df.empty:
    st.error("❌ Errore nel caricamento del foglio 'Partecipanti'. Controlla che esista e che il nome sia corretto.")
    st.stop()

# 🎯 Colonne utilizzate nel clustering
columns = [
    "Età", "Professione", "Formazione", "Ruolo", "Ambito", "Esperienza",
    "Coinvolgimento", "Conoscenza tema", "Motivazione", "Obiettivo", 
    "Visione", "Valori", "Canale preferito"
]
df = df[columns].dropna().reset_index(drop=True)

# 🎛️ Separazione numeriche e categoriche
df_encoded = df.copy()
categorical_cols = df_encoded.select_dtypes(include='object').columns.tolist()
numerical_cols = df_encoded.select_dtypes(exclude='object').columns.tolist()

for col in categorical_cols:
    df_encoded[col] = df_encoded[col].astype('category').cat.codes

# 🧠 Clustering KPrototypes
kproto = KPrototypes(n_clusters=4, init='Huang', random_state=42)
categorical_idx = [df.columns.get_loc(col) for col in categorical_cols]
df['Cluster'] = kproto.fit_predict(df_encoded, categorical=categorical_idx)

# ========== 📊 TAB 1: CLUSTER INSIGHT ==========
with tab1:
    st.title("📊 Analisi dei Cluster dei Partecipanti")

    fig = px.scatter_3d(
        df, x="Età", y="Coinvolgimento", z="Conoscenza tema",
        color=df['Cluster'].astype(str), symbol="Ruolo",
        title="Clusterizzazione 3D"
    )
    st.plotly_chart(fig)

    if st.button("🧠 Genera insight con Gemini", key="cluster_insight"):
        api_key = st.secrets["gemini"]["api_key"]
        client = genai.Client(api_key=api_key)

        cluster_summary = df.groupby('Cluster').agg(lambda x: x.mode()[0] if x.dtype == 'object' else x.mean(numeric_only=True))

        prompt = f"""
        Sei un'amministrazione comunale che vuole valorizzare il verde urbano attraverso l'ascolto strutturato dei cittadini.
        I partecipanti sono stati suddivisi in 4 cluster tramite un'analisi di dati misti (età, ruolo, motivazione, ecc).
        Per ogni cluster genera:

        - Un nome simbolico (es. "I pragmatici", "I visionari")
        - Una descrizione sintetica (2-3 righe)
        - 2-3 azioni concrete per coinvolgerli nei progetti di rigenerazione urbana
        - Il canale di comunicazione più efficace
        - La tipologia di spazio verde ideale per quel cluster

        Ecco i dati medi/modali per ciascun cluster:
        {cluster_summary.to_string()}
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        st.markdown("### 💬 Profili generati con Gemini:")
        st.markdown(response.text)

# ========== 📌 TAB 2: PARETO & ISHIKAWA ==========
with tab2:
    st.title("📌 Analisi delle Motivazioni e Obiettivi")

    motivazioni = df["Motivazione"].dropna().tolist()
    obiettivi = df["Obiettivo"].dropna().tolist()

    prompt = f"""
Sei un facilitatore esperto che collabora con l'Amministrazione Comunale di Bergamo per migliorare il verde urbano attraverso l'ascolto strutturato dei cittadini.

Abbiamo raccolto due elenchi di risposte aperte da un questionario:
- Motivazioni: {motivazioni}
- Obiettivi: {obiettivi}

### FASE 1 – ANALISI PARETO
Unifica e analizza questi due elenchi per identificare le richieste o temi più frequenti. Raggruppali per categoria logica (es. "più alberi", "maggior coinvolgimento", "migliore manutenzione", "spazi per bambini") e calcola quante volte ogni tema appare.
Restituisci i risultati in questo formato JSON:
"pareto": [
  {{ "tema": "più alberi", "frequenza": 18 }},
  ...
]

### FASE 2 – DIAGRAMMA DI ISHIKAWA
Costruisci un diagramma di Ishikawa (Causa-Effetto) partendo dalla domanda centrale:
**"Perché i cittadini non si sentono pienamente coinvolti nella progettazione e gestione del verde urbano?"**

Raggruppa le cause in massimo 6 categorie (es. Metodi, Persone, Strumenti, Ambiente, Comunicazione, Processi), ciascuna con una lista di 3–6 cause ricorrenti emerse nei commenti.

⚠️ Rispondi solo con un oggetto JSON valido, senza testo descrittivo né blocchi markdown.

Formato atteso finale:
{{
  "pareto": [...],
  "ishikawa": {{
    "Categoria1": [...],
    ...
  }}
}}
"""

    if st.button("📊 Analizza motivazioni con Gemini", key="analisi_pareto_ishikawa"):
        api_key = st.secrets["gemini"]["api_key"]
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        raw_text = response.text
        cleaned_text = re.sub(r"```json|```", "", raw_text).strip()

        try:
            result = json.loads(cleaned_text)

            # 🔹 Grafico Pareto
            pareto_df = pd.DataFrame(result["pareto"])
            fig_pareto = px.bar(
                pareto_df, x="tema", y="frequenza",
                title="🔢 Analisi Pareto – Richieste principali dei cittadini",
                labels={"tema": "Tema", "frequenza": "Frequenza"}
            )
            st.plotly_chart(fig_pareto)

            # 🔹 Tabella Ishikawa
            st.markdown("### 🧩 Categorizzazione secondo il Diagramma di Ishikawa")
            for categoria, cause in result["ishikawa"].items():
                st.markdown(f"**{categoria}**")
                st.write(", ".join(cause))

        except json.JSONDecodeError as e:
            st.error("❌ Il formato restituito da Gemini non è un JSON valido.")
            st.code(cleaned_text)
            st.exception(e)
