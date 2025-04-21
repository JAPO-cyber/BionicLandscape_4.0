import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import gmean
from sklearn.cluster import KMeans
import plotly.express as px
import random
import io

st.title("4. Matrice AHP del Tavolo Rotondo")
st.markdown("""
In questa pagina analizziamo l'importanza percepita del verde urbano da parte dei partecipanti, 
combinando le loro matrici AHP e clusterizzando le opinioni in base ai profili del **modello persona**.
""")

# -------------------------------
# 1. ELEMENTI E SCALA AHP
# -------------------------------
elementi_verde = [
    "Accessibilità del verde",
    "Biodiversità",
    "Manutenzione e pulizia",
    "Funzione sociale",
    "Funzione ambientale"
]
n = len(elementi_verde)
scala_valori = [1, 3, 5, 7, 9]

# -------------------------------
# 2. CARICAMENTO O SIMULAZIONE PROFILI
# -------------------------------
st.subheader("🎭 Profili dei partecipanti")

if "persona_model" in st.session_state:
    profili_df = st.session_state["persona_model"]
else:
    zone = ["Centro", "Periferia", "Area Verde", "Area Mista"]
    ruoli = ["Studente", "Tecnico", "Cittadino", "Attivista", "Urbanista"]
    eta_range = list(range(18, 66))

    profili = []
    for i in range(30):
        profili.append({
            "ID": f"User_{i+1}",
            "Età": random.choice(eta_range),
            "Zona": random.choice(zone),
            "Ruolo": random.choice(ruoli)
        })
    profili_df = pd.DataFrame(profili)

st.dataframe(profili_df)

# -------------------------------
# 3. SIMULAZIONE MATRICI AHP
# -------------------------------
st.subheader("📊 Generazione Matrici AHP Simulate")
matrici = []

def genera_matrice_ahp_random():
    matrix = np.ones((n, n))
    for i in range(n):
        for j in range(i+1, n):
            valore = random.choice(scalavalori)
            matrix[i, j] = valore
            matrix[j, i] = 1 / valore
    return matrix

for _ in range(len(profili_df)):
    matrice = genera_matrice_ahp_random()
    matrici.append(matrice)

# -------------------------------
# 4. CALCOLO MATRICE AHP AGGREGATA
# -------------------------------
matrix_3d = np.array(matrici)
combined_matrix = gmean(matrix_3d, axis=0)
combined_df = pd.DataFrame(combined_matrix, index=elementi_verde, columns=elementi_verde)

st.subheader("🔗 Matrice AHP Aggregata")
st.dataframe(combined_df)

eigvals, eigvecs = np.linalg.eig(combined_matrix)
max_idx = np.argmax(eigvals.real)
weights = eigvecs[:, max_idx].real
weights /= weights.sum()
weights_df = pd.DataFrame({
    "Elemento": elementi_verde,
    "Peso Aggregato": weights
}).sort_values("Peso Aggregato", ascending=False)

st.subheader("📌 Pesi Aggregati AHP")
st.dataframe(weights_df)

# -------------------------------
# 5. CLUSTERING + COERENZA
# -------------------------------
st.subheader("📈 Analisi Cluster + Coerenza")

def calcola_cr(matrice):
    eigvals, _ = np.linalg.eig(matrice)
    lambda_max = np.max(eigvals.real)
    ci = (lambda_max - n) / (n - 1)
    ri_values = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32}
    ri = ri_values.get(n, 1.12)
    cr = ci / ri if ri != 0 else 0
    return round(ci, 4), round(cr, 4)

feature_vectors = []
ci_list = []
cr_list = []

for matrix in matrici:
    eigvals, eigvecs = np.linalg.eig(matrix)
    max_idx = np.argmax(eigvals.real)
    w = eigvecs[:, max_idx].real
    w = w / w.sum()
    feature_vectors.append(w)
    ci, cr = calcola_cr(matrix)
    ci_list.append(ci)
    cr_list.append(cr)

feature_vectors = np.array(feature_vectors)

cluster_df = profili_df.copy()
cluster_df[elementi_verde] = feature_vectors
cluster_df["CI"] = ci_list
cluster_df["CR"] = cr_list

k = st.slider("Numero di cluster", 2, 6, 3)
kmeans = KMeans(n_clusters=k, random_state=42)
cluster_labels = kmeans.fit_predict(feature_vectors)
cluster_df["Cluster"] = cluster_labels

st.dataframe(cluster_df)

media_cluster = cluster_df.groupby("Cluster")[elementi_verde].mean()
st.subheader("📊 Media dei Pesi per Cluster")
st.dataframe(media_cluster)

# -------------------------------
# 6. VISUALIZZAZIONI INTERATTIVE
# -------------------------------
st.subheader("📊 Grafico Interattivo - Pesi AHP")
st.markdown("""
Questo grafico a barre mostra l'importanza relativa percepita di ciascun elemento del verde urbano secondo la media aggregata dei partecipanti. 
Ogni barra rappresenta un elemento, e la sua altezza indica quanto è considerato prioritario rispetto agli altri.
""")
fig = px.bar(weights_df, x="Elemento", y="Peso Aggregato", title="Pesi AHP Aggregati", text_auto=True)
st.plotly_chart(fig, use_container_width=True)

st.subheader("🧪 Distribuzione Consistency Ratio (CR)")
st.markdown("""
L'istogramma mostra la distribuzione del Consistency Ratio (CR) tra i partecipanti. 
Il CR misura la coerenza nelle risposte AHP: valori inferiori a 0.10 indicano giudizi coerenti, mentre valori superiori suggeriscono possibili incoerenze nelle valutazioni.
""")
fig2 = px.histogram(cluster_df, x="CR", nbins=10, title="Distribuzione del Consistency Ratio (CR)")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("🎯 Cluster Interattivi")
st.markdown("""
Questo scatter plot interattivo visualizza i partecipanti raggruppati in cluster basati sulle loro percezioni del verde urbano. 
Ogni punto rappresenta un partecipante, colorato in base al cluster di appartenenza. 
Passando il cursore su un punto, puoi visualizzare dettagli come ID, ruolo, età, zona e CR.
""")
fig3 = px.scatter(cluster_df, x=elementi_verde[0], y=elementi_verde[1],
                  color="Cluster", hover_data=["ID", "Ruolo", "Età", "Zona", "CR"])
st.plotly_chart(fig3, use_container_width=True)

# -------------------------------
# 7. ESPORTAZIONE
# -------------------------------
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    profili_df.to_excel(writer, sheet_name="Profili", index=False)
    combined_df.to_excel(writer, sheet_name="Matrice_Aggregata")
    weights_df.to_excel(writer, sheet_name="Pesi_AHP", index=False)
    cluster_df.to_excel(writer, sheet_name="Cluster_Utenti", index=False)
    media_cluster.to_excel(writer, sheet_name="Cluster_Media")

st.download_button(
    label="📥 Scarica risultati AHP (Excel)",
    data=output.getvalue(),
    file_name="ahp_tavolo_rotondo_risultati.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

