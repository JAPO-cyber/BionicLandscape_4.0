import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import gmean
from sklearn.cluster import KMeans
import random

st.title("4. Output Tavolo Rotondo")
st.markdown("""
In questa pagina analizziamo l'importanza percepita del verde urbano da parte dei partecipanti, 
combinando le loro valutazioni e clusterizzando le opinioni in base ai profili del **modello persona**.
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

# Se hai già il model persona generato:
if "persona_model" in st.session_state:
    profili_df = st.session_state["persona_model"]
else:
    # Simulazione di 30 profili esempio (puoi sostituire con il tuo dataset reale)
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
            valore = random.choice(scala_valori)
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

# Calcolo dei pesi aggregati
eigvals, eigvecs = np.linalg.eig(combined_matrix)
max_idx = np.argmax(eigvals.real)
weights = eigvecs[:, max_idx].real
weights = weights / weights.sum()
weights_df = pd.DataFrame({
    "Elemento": elementi_verde,
    "Peso Aggregato": weights
}).sort_values("Peso Aggregato", ascending=False)

st.subheader("📌 Pesi Aggregati AHP")
st.dataframe(weights_df)

# -------------------------------
# 5. CLUSTERING PER PROFILI
# -------------------------------
st.subheader("📈 Analisi Cluster sulle Percezioni")

# Calcolo dei vettori pesi individuali
feature_vectors = []
for matrix in matrici:
    eigvals, eigvecs = np.linalg.eig(matrix)
    max_idx = np.argmax(eigvals.real)
    w = eigvecs[:, max_idx].real
    w = w / w.sum()
    feature_vectors.append(w)
feature_vectors = np.array(feature_vectors)

# Aggiunta al dataframe dei profili
cluster_df = profili_df.copy()
cluster_df[elementi_verde] = feature_vectors

k = st.slider("Numero di cluster", 2, 6, 3)
kmeans = KMeans(n_clusters=k, random_state=42)
cluster_labels = kmeans.fit_predict(feature_vectors)
cluster_df["Cluster"] = cluster_labels

st.dataframe(cluster_df)

# Media per cluster
media_cluster = cluster_df.groupby("Cluster")[elementi_verde].mean()
st.subheader("📊 Media dei Pesi per Cluster")
st.dataframe(media_cluster)

# -------------------------------
# 6. ESPORTAZIONE
# -------------------------------
import io
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
