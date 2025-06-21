import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from kmodes.kprototypes import KPrototypes
from lib.google_sheet import get_sheet_by_name
from lib.style import apply_custom_style
from lib.navigation import render_sidebar_navigation
import re
import json

# ✅ Import SDK Gemini
from google import genai

# 🛠️ Impostazioni iniziali
st.set_page_config(page_title="Cluster e Analisi Partecipanti", layout="wide")
apply_custom_style()

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Accesso negato. Torna alla pagina principale.")
    st.stop()

render_sidebar_navigation()

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

Utilizza esclusivamente le **categorie standard** del diagramma di Ishikawa, ovvero:
- Metodi
- Mezzi
- Materiali
- Persone
- Ambiente
- Misurazioni

Per ciascuna categoria, identifica da 3 a 6 cause ricorrenti emerse nei commenti.

⚠️ Rispondi solo con un oggetto JSON valido, senza testo descrittivo né blocchi markdown.

Formato atteso finale:
{{
  "pareto": [...],
  "ishikawa": {{
    "Metodi": [...],
    "Mezzi": [...],
    "Materiali": [...],
    "Persone": [...],
    "Ambiente": [...],
    "Misurazioni": [...]
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

            # --- PARETO ---
            pareto_df = pd.DataFrame(result["pareto"])
            pareto_df = pareto_df.sort_values(by="frequenza", ascending=False).reset_index(drop=True)
            pareto_df["% cumulata"] = pareto_df["frequenza"].cumsum() / pareto_df["frequenza"].sum() * 100

            fig = go.Figure()
            fig.add_trace(go.Bar(x=pareto_df["tema"], y=pareto_df["frequenza"], name="Frequenza"))
            fig.add_trace(go.Scatter(x=pareto_df["tema"], y=pareto_df["% cumulata"],
                                     name="% Cumulata", yaxis="y2", mode="lines+markers"))

            fig.add_shape(
                type="line",
                x0=-0.5, x1=len(pareto_df) - 0.5,
                y0=80, y1=80,
                yref="y2",
                line=dict(color="red", dash="dash"),
                name="80%"
            )

            fig.update_layout(
                title="📈 Diagramma di Pareto – Richieste principali",
                xaxis=dict(title="Temi"),
                yaxis=dict(title="Frequenza"),
                yaxis2=dict(title="% Cumulata", overlaying="y", side="right", range=[0, 100]),
                legend=dict(x=0.8, y=1.2),
                bargap=0.2
            )
            st.plotly_chart(fig)

            # --- ISHIKAWA ---
            st.markdown("### 🧩 Categorizzazione secondo il Diagramma di Ishikawa")
            for categoria in ["Metodi", "Mezzi", "Materiali", "Persone", "Ambiente", "Misurazioni"]:
                cause = result["ishikawa"].get(categoria, [])
                if cause:
                    st.markdown(f"**{categoria}**")
                    st.write(", ".join(cause))

        except json.JSONDecodeError as e:
            st.error("❌ Il formato restituito da Gemini non è un JSON valido.")
            st.code(cleaned_text)
            st.exception(e)
