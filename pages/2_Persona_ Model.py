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

# Caricamento dati simulati
np.random.seed(42)
n = 25
ruoli = ["Cittadino interessato", "Tecnico/Esperto", "Rappresentante istituzionale", "Studente", "Altro"]
ambiti = ["Urbanistica", "Tecnologia e digitale", "Transizione ecologica",
          "Inclusione sociale", "Economia e lavoro", "Cultura e creatività"]
valori_possibili = ["Innovazione", "Collaborazione", "Responsabilità", "Tradizione", "Trasparenza", "Inclusione"]
visioni = ["Valori tradizionali", "Innovazione", "Equilibrio tra i due"]
canali = ["Email", "Social", "Eventi pubblici", "Siti ufficiali", "Bacheche locali"]
esperienza_partecipativa = ["Sì", "No"]

def sample_valori():
    return ", ".join(np.random.choice(valori_possibili, size=np.random.randint(1, 4), replace=False))

df = pd.DataFrame({
    "Tavola rotonda": np.random.choice(["Digitale e città", "Transizione ecologica", "Spazi pubblici e comunità",
                                        "Futuro del lavoro", "Cultura e creatività"], size=n),
    "Nome": [f"Partecipante {i+1}" for i in range(n)],
    "Età": np.random.randint(18, 70, size=n),
    "Professione": np.random.choice(["Ingegnere", "Studente", "Architetto", "Docente", "Impiegato", "Freelance"], size=n),
    "Formazione": np.random.choice(["Informatica", "Architettura", "Scienze Politiche", "Economia", "Lettere", "Nessuna"], size=n),
    "Ruolo": np.random.choice(ruoli, size=n),
    "Ambito": np.random.choice(ambiti, size=n),
    "Esperienza": np.random.choice(esperienza_partecipativa, size=n),
    "Coinvolgimento": np.random.randint(0, 11, size=n),
    "Conoscenza tema": np.random.randint(0, 11, size=n),
    "Motivazione": ["Partecipo per contribuire al futuro della mia città."] * n,
    "Obiettivo": ["Voglio condividere idee e ascoltare altri punti di vista."] * n,
    "Visione": np.random.choice(visioni, size=n),
    "Valori": [sample_valori() for _ in range(n)],
    "Canale preferito": np.random.choice(canali, size=n)
})

st.set_page_config(page_title="📊 Personas Model Analysis", layout="wide")
st.title("📊 Analisi partecipanti - Personas Model")

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
scelta = st.sidebar.selectbox("🔍 Seleziona l'analisi da visualizzare", menu)

# Esegui la sezione corrispondente
if scelta == "Dataset":
    st.dataframe(df)

elif scelta == "Età e Coinvolgimento":
    fig = px.histogram(df, x="Età", nbins=10, title="Distribuzione età")
    st.plotly_chart(fig, use_container_width=True)
    st.bar_chart(df.groupby("Coinvolgimento").size(), use_container_width=True)

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
