import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from scipy.stats import f_oneway
from lib.google_sheet import get_sheet_by_name
from lib.style import apply_custom_style

st.set_page_config(page_title="🔍 AHP Tavolo Rotondo", layout="wide")
apply_custom_style()

st.title("4. Matrice AHP del Tavolo Rotondo")

# ✅ Carica i dati da Google Sheets
sheet_weights = get_sheet_by_name("Dati_Partecipante", "Pesi Parametri")
sheet_profiles = get_sheet_by_name("Dati_Partecipante", "Partecipanti")

if not sheet_weights or not sheet_profiles:
    st.error("❌ Impossibile caricare i dati dal Google Sheet.")
    st.stop()

# ✅ Importa i dati
df_weights = pd.DataFrame(sheet_weights.get_all_records())
df_profiles = pd.DataFrame(sheet_profiles.get_all_records())

# ✅ Merge sui nomi (Utente)
df_merged = pd.merge(df_weights, df_profiles, how="inner", left_on="Utente", right_on="Nome")

# ✅ Colonne AHP e meta
elementi_verde = [
    "Accessibilità del verde",
    "Biodiversità",
    "Manutenzione e pulizia",
    "Funzione sociale (es. luoghi di incontro)",
    "Funzione ambientale (es. ombra, qualità aria)"
]

tavola_column = [col for col in df_merged.columns if "Tavola rotonda" in col][0]

# ✅ Menu a sinistra per selezionare analisi
analisi = st.sidebar.radio("📌 Seleziona Analisi", [
    "Dataset Combinato",
    "Statistica Tavole",
    "ANOVA Tavole",
    "Cluster AHP",
    "Media per Cluster",
    "Distribuzione Cluster"
])

if analisi == "Dataset Combinato":
    st.markdown("### 🔍 Dataset Combinato")
    st.dataframe(df_merged)

elif analisi == "Statistica Tavole":
    st.subheader("📊 Confronto tra Tavole rotonde")
    mean_by_round = df_merged.groupby(tavola_column)[elementi_verde].mean()
    st.dataframe(mean_by_round)
    fig1 = px.bar(mean_by_round.T, barmode="group", title="Pesi AHP medi per Tavola rotonda")
    st.plotly_chart(fig1, use_container_width=True)

elif analisi == "ANOVA Tavole":
    st.subheader("📐 Test ANOVA tra Tavole rotonde")
    for elemento in elementi_verde:
        gruppi = [group[elemento].values for name, group in df_merged.groupby(tavola_column)]
        stat, p = f_oneway(*gruppi)
        st.write(f"🔸 {elemento}: p-value = {p:.4f} ({'⚠️ Differenze significative' if p < 0.05 else 'Nessuna differenza significativa'})")

elif analisi == "Cluster AHP":
    st.subheader("🔎 Cluster sui profili AHP")
    X = df_merged[elementi_verde].values
    k = st.slider("Scegli il numero di cluster:", 2, 6, 3)
    kmeans = KMeans(n_clusters=k, random_state=42).fit(X)
    df_merged["Cluster"] = kmeans.labels_
    valid_df = df_merged.dropna(subset=[elementi_verde[0], elementi_verde[1], "Cluster"])

    if valid_df.empty:
        st.warning("⚠️ Non ci sono abbastanza dati validi per generare il grafico dei cluster.")
    else:
        fig2 = px.scatter(
            valid_df,
            x=elementi_verde[0],
            y=elementi_verde[1],
            color="Cluster",
            hover_data=["Utente_x", tavola_column, "Età", "Ruolo", "Ambito"]
        )
        st.plotly_chart(fig2, use_container_width=True)

elif analisi == "Media per Cluster":
    st.subheader("📌 Media pesi AHP per Cluster")
    if "Cluster" not in df_merged.columns:
        st.warning("⚠️ Esegui prima il clustering nella sezione 'Cluster AHP'.")
    else:
        media_cluster = df_merged.groupby("Cluster")[elementi_verde].mean()
        st.dataframe(media_cluster)
        fig3 = px.bar(media_cluster.T, barmode="group", title="Distribuzione Pesi AHP per Cluster")
        st.plotly_chart(fig3, use_container_width=True)

elif analisi == "Distribuzione Cluster":
    st.subheader("📊 Cluster per Tavola rotonda")
    if "Cluster" not in df_merged.columns:
        st.warning("⚠️ Esegui prima il clustering nella sezione 'Cluster AHP'.")
    else:
        cross_tab = pd.crosstab(df_merged[tavola_column], df_merged["Cluster"])
        st.dataframe(cross_tab)
        fig4 = px.bar(cross_tab, barmode="group", title="Distribuzione dei Cluster per Tavola rotonda")
        st.plotly_chart(fig4, use_container_width=True)

# ✅ Salva in sessione se utile
st.session_state["df_merged"] = df_merged


