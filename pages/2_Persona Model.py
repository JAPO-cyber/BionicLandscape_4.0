import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
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

tabs = st.tabs([
    "1️⃣ Dataset", "2️⃣ Età e Coinvolgimento", "3️⃣ Conoscenza tema", "4️⃣ Visione e Valori",
    "5️⃣ Ambiti di Interesse", "6️⃣ Esperienza Precedente", "7️⃣ Canali Preferiti", "8️⃣ Ruoli",
    "9️⃣ Formazione", "🔟 Correlazioni", "🔢 Boxplot", "🧩 K-Means Clustering",
    "📈 Pareto Valori", "🎯 Clusterizzazione semplificata", "📥 Esporta CSV"
])

with tabs[0]:
    st.subheader("Dataset completo")
    st.dataframe(df)

with tabs[1]:
    fig = px.histogram(df, x="Età", nbins=10, title="Distribuzione età")
    st.plotly_chart(fig, use_container_width=True)
    st.bar_chart(df.groupby("Coinvolgimento").size(), use_container_width=True)

with tabs[2]:
    st.subheader("Distribuzione della conoscenza del tema")
    fig = px.box(df, y="Conoscenza tema", points="all", title="Boxplot Conoscenza tema")
    st.plotly_chart(fig, use_container_width=True)

with tabs[3]:
    st.subheader("Visione dichiarata")
    st.bar_chart(df["Visione"].value_counts())

    valori_series = df["Valori"].str.split(", ").explode()
    st.subheader("Valori più rappresentati")
    st.bar_chart(valori_series.value_counts())

with tabs[4]:
    st.subheader("Distribuzione degli ambiti di interesse")
    fig = px.pie(df, names="Ambito", title="Ambiti di interesse")
    st.plotly_chart(fig, use_container_width=True)

with tabs[5]:
    st.subheader("Esperienza partecipativa")
    st.bar_chart(df["Esperienza"].value_counts())

with tabs[6]:
    st.subheader("Canale preferito per ricevere informazioni")
    st.bar_chart(df["Canale preferito"].value_counts())

with tabs[7]:
    st.subheader("Distribuzione dei ruoli")
    st.bar_chart(df["Ruolo"].value_counts())

with tabs[8]:
    st.subheader("Formazione dichiarata")
    st.bar_chart(df["Formazione"].value_counts())

with tabs[9]:
    st.subheader("Matrice di correlazione")
    corr = df[["Età", "Coinvolgimento", "Conoscenza tema"]].corr()
    st.dataframe(corr.style.background_gradient(cmap='RdBu_r', axis=None))

with tabs[10]:
    st.subheader("Boxplot per Coinvolgimento e Conoscenza tema")
    fig1 = px.box(df, y="Coinvolgimento", points="all")
    fig2 = px.box(df, y="Conoscenza tema", points="all")
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

with tabs[11]:
    st.subheader("Clustering con K-Means (Età, Coinvolgimento, Conoscenza)")
    features = df[["Età", "Coinvolgimento", "Conoscenza tema"]]
    scaled = StandardScaler().fit_transform(features)
    kmeans = KMeans(n_clusters=3, random_state=42).fit(scaled)
    df["Cluster"] = kmeans.labels_
    fig = px.scatter_3d(df, x="Età", y="Coinvolgimento", z="Conoscenza tema", color="Cluster", title="Cluster 3D")
    st.plotly_chart(fig, use_container_width=True)

with tabs[12]:
    st.subheader("Diagramma di Pareto dei valori")
    valori_count = valori_series.value_counts().reset_index()
    valori_count.columns = ["Valore", "Frequenza"]
    valori_count["Cumulata %"] = valori_count["Frequenza"].cumsum() / valori_count["Frequenza"].sum() * 100
    fig = px.bar(valori_count, x="Valore", y="Frequenza", title="Pareto Valori")
    st.plotly_chart(fig, use_container_width=True)

with tabs[13]:
    st.subheader("Clusterizzazione semplificata (logica)")

    def remove_emoji(text):
        return re.sub(r'[^\w\s,.-]', '', text)

    def assegna_persona(row):
        if row["Età"] < 30 and row["Coinvolgimento"] >= 7:
            return "Giovane attivista"
        elif row["Ruolo"] == "Tecnico/Esperto" and row["Conoscenza tema"] >= 7:
            return "Esperto tecnico"
        elif row["Esperienza"] == "No" and row["Coinvolgimento"] < 4:
            return "Cittadino curioso"
        elif row["Ruolo"] == "Rappresentante istituzionale":
            return "Rappresentante"
        else:
            return "Partecipante coinvolto"

    df["PersonaModel"] = df.apply(assegna_persona, axis=1)
    df["PersonaModel"] = df["PersonaModel"].apply(remove_emoji)
    st.dataframe(df[["Nome", "PersonaModel"]])
    st.bar_chart(df["PersonaModel"].value_counts())

with tabs[14]:
    st.subheader("Scarica i dati in CSV")
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 Scarica CSV", csv, "analisi_personas.csv", "text/csv")
