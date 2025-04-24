import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from scipy import stats
import re
from lib.google_sheet import get_sheet_by_name
from lib.style import apply_custom_style

# ✅ Configura la pagina (deve essere il primo comando Streamlit)
st.set_page_config(page_title="📊 Personas Model Analysis", layout="wide")

# ✅ Applica stile grafico centralizzato
apply_custom_style()

st.title("📊 Analisi partecipanti - Personas Model")

# 🔗 Pulsante per andare alla schermata successiva
st.markdown("---")
st.page_link("pages/3_Percezione_Cittadino.py", label="➡️ Vai a Percezione Cittadino", icon="🧠")
st.markdown("---")

# ✅ Carica dati reali dal Google Sheet
sheet = get_sheet_by_name("Dati_Partecipante", "Partecipanti")

if sheet:
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # ✅ Filtra per tavola rotonda selezionata o consenti scelta
    tavola_rotonda = st.session_state.get("tavola_rotonda", None)
    if tavola_rotonda:
        df = df[df["Tavola rotonda"] == tavola_rotonda]
        st.info(f"📌 Analisi basata sulla tavola rotonda selezionata: **{tavola_rotonda}**")
    else:
        st.warning("⚠️ Nessuna tavola rotonda selezionata nella fase precedente.")
        tavole_uniche = df["Tavola rotonda"].unique().tolist()
        scelta_manuale = st.selectbox("🔘 Seleziona manualmente la tavola rotonda da analizzare:", tavole_uniche)
        df = df[df["Tavola rotonda"] == scelta_manuale]
        st.info(f"📌 Analisi basata sulla tavola rotonda selezionata: **{scelta_manuale}**")
else:
    st.error("❌ Errore nel caricamento dei dati da Google Sheets.")
    st.stop()

# Opzioni menu sidebar
menu = [
    "Dataset", "Età e Coinvolgimento", "Conoscenza tema", "Visione e Valori",
    "Ambiti di Interesse", "Esperienza Precedente", "Canali Preferiti", "Ruoli",
    "Formazione", "Correlazioni", "Boxplot", "K-Means Clustering",
    "Pareto Valori", "Clusterizzazione semplificata", "Esporta CSV",
    "Heatmap Ruolo vs Coinvolgimento", "Gap Coinvolgimento-Conoscenza",
    "Radar PersonaModel", "Ambito vs Visione", "Statistica descrittiva",
    "Test ANOVA e Normalità", "PCA 2D", "Silhouette Score"
]
scelta = st.sidebar.radio("📌 Seleziona Analisi", menu)

# [segue codice delle analisi, invariato rispetto alla versione precedente...]


# Esegui la sezione corrispondente
if scelta == "Dataset":
    st.dataframe(df)

elif scelta == "Età e Coinvolgimento":
    # 📊 Distribuzione Età
    st.subheader("📊 Distribuzione dell'età dei partecipanti")
    fig_eta = px.histogram(
        df,
        x="Età",
        nbins=10,
        title="Distribuzione dell'età dei partecipanti",
        labels={"Età": "Età (anni)"},
        color_discrete_sequence=["#2ca02c"],
        text_auto=True
    )
    fig_eta.update_layout(
        xaxis_title="Fasce d'età",
        yaxis_title="Numero di partecipanti",
        bargap=0.05
    )
    st.plotly_chart(fig_eta, use_container_width=True)
    
    # 📈 Coinvolgimento
    st.subheader("📈 Livello di coinvolgimento dichiarato")
    coinvolgimento_counts = df["Coinvolgimento"].value_counts().sort_index().reset_index()
    coinvolgimento_counts.columns = ["Coinvolgimento", "Partecipanti"]
    
    fig_coinvolgimento = px.bar(
        coinvolgimento_counts,
        x="Coinvolgimento",
        y="Partecipanti",
        title="Distribuzione del livello di coinvolgimento",
        labels={"Coinvolgimento": "Livello di coinvolgimento (1-10)", "Partecipanti": "Numero di partecipanti"},
        text_auto=True,
        color_discrete_sequence=["#1f77b4"]
    )
    fig_coinvolgimento.update_layout(
        xaxis=dict(tickmode="linear"),
        yaxis_title="Numero di partecipanti"
    )
    st.plotly_chart(fig_coinvolgimento, use_container_width=True)


    

elif scelta == "Conoscenza tema":
    fig = px.box(df, y="Conoscenza tema", points="all", title="Boxplot Conoscenza tema")
    st.plotly_chart(fig, use_container_width=True)

elif scelta == "Visione e Valori":
    st.bar_chart(df["Visione"].value_counts())
    valori_series = df["Valori"].str.split(", ").explode()
    st.subheader("Valori più rappresentati")
    st.bar_chart(valori_series.value_counts())

elif scelta == "Ambiti di Interesse":
    fig = px.pie(df, names="Ambito", title="Ambiti di interesse")
    st.plotly_chart(fig, use_container_width=True)

elif scelta == "Esperienza Precedente":
    st.bar_chart(df["Esperienza"].value_counts())

elif scelta == "Canali Preferiti":
    st.bar_chart(df["Canale preferito"].value_counts())

elif scelta == "Ruoli":
    st.bar_chart(df["Ruolo"].value_counts())

elif scelta == "Formazione":
    st.bar_chart(df["Formazione"].value_counts())

elif scelta == "Correlazioni":
    corr = df[["Età", "Coinvolgimento", "Conoscenza tema"]].corr()
    st.dataframe(corr.style.background_gradient(cmap='RdBu_r', axis=None))

elif scelta == "Boxplot":
    fig1 = px.box(df, y="Coinvolgimento", points="all")
    fig2 = px.box(df, y="Conoscenza tema", points="all")
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

elif scelta == "K-Means Clustering":
    features = df[["Età", "Coinvolgimento", "Conoscenza tema"]]
    scaled = StandardScaler().fit_transform(features)
    kmeans = KMeans(n_clusters=3, random_state=42).fit(scaled)
    df["Cluster"] = kmeans.labels_
    fig = px.scatter_3d(df, x="Età", y="Coinvolgimento", z="Conoscenza tema", color="Cluster", title="Cluster 3D")
    st.plotly_chart(fig, use_container_width=True)

elif scelta == "Pareto Valori":
    valori_series = df["Valori"].str.split(", ").explode()
    valori_count = valori_series.value_counts().reset_index()
    valori_count.columns = ["Valore", "Frequenza"]
    valori_count["Cumulata %"] = valori_count["Frequenza"].cumsum() / valori_count["Frequenza"].sum() * 100
    fig = px.bar(valori_count, x="Valore", y="Frequenza", title="Pareto Valori")
    st.plotly_chart(fig, use_container_width=True)

elif scelta == "Clusterizzazione semplificata":
    def assegna_persona(row):
        if row["Età"] < 30 and row["Coinvolgimento"] >= 7:
            return "🧑‍🎓 Giovane attivista"
        elif row["Ruolo"] == "Tecnico/Esperto" and row["Conoscenza tema"] >= 7:
            return "🧑‍🔬 Esperto tecnico"
        elif row["Esperienza"] == "No" and row["Coinvolgimento"] < 4:
            return "👤 Cittadino curioso"
        elif row["Ruolo"] == "Rappresentante istituzionale":
            return "🏛️ Rappresentante"
        else:
            return "🌍 Partecipante coinvolto"

    df["PersonaModel"] = df.apply(assegna_persona, axis=1)
    st.dataframe(df[["Nome", "PersonaModel"]])
    st.bar_chart(df["PersonaModel"].value_counts())

elif scelta == "Esporta CSV":
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 Scarica CSV", csv, "analisi_personas.csv", "text/csv")

elif scelta == "Heatmap Ruolo vs Coinvolgimento":
    pivot = df.pivot_table(index="Ruolo", values="Coinvolgimento", aggfunc="mean")
    st.dataframe(pivot.style.background_gradient(cmap="YlOrRd"))

elif scelta == "Gap Coinvolgimento-Conoscenza":
    df["Gap"] = df["Coinvolgimento"] - df["Conoscenza tema"]
    fig = px.histogram(df, x="Gap", nbins=10, title="Gap tra coinvolgimento e conoscenza")
    st.plotly_chart(fig, use_container_width=True)

elif scelta == "Radar PersonaModel":
    import plotly.graph_objects as go
    if "PersonaModel" not in df:
        st.warning("⚠️ Prima esegui la clusterizzazione semplificata.")
    else:
        radar_df = df.groupby("PersonaModel")[["Età", "Coinvolgimento", "Conoscenza tema"]].mean()
        categories = list(radar_df.columns)
        fig = go.Figure()
        for index, row in radar_df.iterrows():
            fig.add_trace(go.Scatterpolar(r=row.values, theta=categories, fill='toself', name=index))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

elif scelta == "Ambito vs Visione":
    cross = pd.crosstab(df["Ambito"], df["Visione"])
    st.dataframe(cross)
    fig = px.bar(cross, barmode="group", title="Ambiti e orientamento di visione")
    st.plotly_chart(fig, use_container_width=True)

elif scelta == "Statistica descrittiva":
    descrittive = df[["Età", "Coinvolgimento", "Conoscenza tema"]].describe()
    st.dataframe(descrittive.style.format("{:.2f}").background_gradient(cmap="Blues"))

elif scelta == "Test ANOVA e Normalità":
    for col in ["Età", "Coinvolgimento", "Conoscenza tema"]:
        stat, p = stats.shapiro(df[col])
        st.write(f"🔹 {col}: p-value = {p:.4f} ({'Distribuzione normale' if p > 0.05 else 'Non normale'})")
    st.markdown("---")
    gruppi = [df[df["Ruolo"] == ruolo]["Coinvolgimento"] for ruolo in df["Ruolo"].unique()]
    stat, p = stats.f_oneway(*gruppi)
    st.write(f"**ANOVA Coinvolgimento per Ruolo**: p-value = {p:.4f}")

elif scelta == "PCA 2D":
    pca_features = df[["Età", "Coinvolgimento", "Conoscenza tema"]]
    scaler = StandardScaler()
    scaled_pca = scaler.fit_transform(pca_features)
    pca = PCA(n_components=2)
    components = pca.fit_transform(scaled_pca)
    df_pca = pd.DataFrame(components, columns=["PC1", "PC2"])
    df_pca["Ruolo"] = df["Ruolo"]
    fig = px.scatter(df_pca, x="PC1", y="PC2", color="Ruolo", title="Proiezione PCA 2D per Ruolo")
    st.plotly_chart(fig, use_container_width=True)

elif scelta == "Silhouette Score":
    X = df[["Età", "Coinvolgimento", "Conoscenza tema"]]
    X_scaled = StandardScaler().fit_transform(X)
    scores = []
    k_range = range(2, 8)
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42)
        labels = km.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        scores.append(score)
    score_df = pd.DataFrame({"k": list(k_range), "Silhouette Score": scores})
    fig = px.line(score_df, x="k", y="Silhouette Score", markers=True, title="Silhouette Score per K")
    st.plotly_chart(fig, use_container_width=True)
