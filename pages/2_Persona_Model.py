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
    df_completo = pd.DataFrame(data)

    tavola_rotonda = st.session_state.get("tavola_rotonda", None)
    if tavola_rotonda:
        df = df_completo[df_completo["Tavola rotonda"] == tavola_rotonda]
        st.info(f"📌 Analisi basata sulla tavola rotonda selezionata: **{tavola_rotonda}**")
    else:
        st.warning("⚠️ Nessuna tavola rotonda selezionata nella fase precedente.")
        tavole_uniche = df_completo["Tavola rotonda"].unique().tolist()
        scelta_manuale = st.selectbox("🔘 Seleziona manualmente la tavola rotonda da analizzare:", tavole_uniche)
        df = df_completo[df_completo["Tavola rotonda"] == scelta_manuale]
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
    tab1, tab2 = st.tabs(["🎯 Tavola selezionata", "📊 Confronto tra tavole"])
    with tab1:
        st.subheader("📊 Distribuzione dell'età dei partecipanti")
        fig_eta = px.histogram(df, x="Età", nbins=10, title="Distribuzione dell'età",
                               labels={"Età": "Età (anni)"}, color_discrete_sequence=["#2ca02c"], text_auto=True)
        fig_eta.update_layout(xaxis_title="Fasce d'età", yaxis_title="Numero di partecipanti", bargap=0.05)
        st.plotly_chart(fig_eta, use_container_width=True)
        st.markdown("#### 📈 Statistiche descrittive - Età")
        st.dataframe(df['Età'].describe().to_frame(), use_container_width=True)
    
        st.subheader("📈 Livello di coinvolgimento")
        coinvolgimento_counts = df["Coinvolgimento"].value_counts().sort_index().reset_index()
        coinvolgimento_counts.columns = ["Coinvolgimento", "Partecipanti"]
        fig_coinv = px.bar(coinvolgimento_counts, x="Coinvolgimento", y="Partecipanti",
                           title="Coinvolgimento dichiarato",
                           labels={"Coinvolgimento": "Livello (1–10)", "Partecipanti": "N. partecipanti"},
                           text_auto=True, color_discrete_sequence=["#1f77b4"])
        fig_coinv.update_layout(xaxis=dict(tickmode="linear"), yaxis_title="Numero di partecipanti")
        st.plotly_chart(fig_coinv, use_container_width=True)
        st.markdown("#### 📈 Statistiche descrittive - Coinvolgimento")
        st.dataframe(df['Coinvolgimento'].describe().to_frame(), use_container_width=True)

    # --- TAB 2: Confronto tra tavole rotonde ---
    with tab2:
        st.subheader("📊 Età media per tavola rotonda")
        eta_media = df_completo.groupby("Tavola rotonda")["Età"].mean().reset_index()
        fig_eta_confronto = px.bar(eta_media, x="Tavola rotonda", y="Età", title="Età media per tavola rotonda",
                                   labels={"Età": "Età media"}, text_auto=True, color_discrete_sequence=["#2ca02c"])
        st.plotly_chart(fig_eta_confronto, use_container_width=True)
    
        st.subheader("📈 Coinvolgimento medio per tavola rotonda")
        coinv_media = df_completo.groupby("Tavola rotonda")["Coinvolgimento"].mean().reset_index()
        fig_coinv_confronto = px.bar(coinv_media, x="Tavola rotonda", y="Coinvolgimento",
                                     title="Coinvolgimento medio per tavola rotonda",
                                     labels={"Coinvolgimento": "Coinvolgimento medio"},
                                     text_auto=True, color_discrete_sequence=["#1f77b4"])
        st.plotly_chart(fig_coinv_confronto, use_container_width=True)
    
        # 🔍 Violin plot e Boxplot
        st.subheader("🎻 Distribuzioni dettagliate per tavola rotonda")
        fig_violin = px.violin(df_completo, y="Età", x="Tavola rotonda", box=True, points="all",
                               color="Tavola rotonda", title="Distribuzione dell'età per tavola rotonda")
        st.plotly_chart(fig_violin, use_container_width=True)
    
        fig_box = px.box(df_completo, y="Coinvolgimento", x="Tavola rotonda", points="all",
                         color="Tavola rotonda", title="Distribuzione del coinvolgimento per tavola rotonda")
        st.plotly_chart(fig_box, use_container_width=True)

         # ===  === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === ===
        # === Analisi statistica ===
        st.subheader("📊 Test ANOVA – Differenze tra tavole")
        
        from scipy.stats import f_oneway, kruskal, shapiro
        import scikit_posthocs as sp
        
        # Gruppi per variabili
        gruppi_coinv = [g["Coinvolgimento"].dropna().values for _, g in df_completo.groupby("Tavola rotonda") if len(g["Coinvolgimento"].dropna()) > 1]
        gruppi_eta = [g["Età"].dropna().values for _, g in df_completo.groupby("Tavola rotonda") if len(g["Età"].dropna()) > 1]
        
        # ANOVA
        anova_coinv = f_oneway(*gruppi_coinv)
        anova_eta = f_oneway(*gruppi_eta)
        
        # Verifica normalità
        def check_normality(col):
            return all(shapiro(g[col].dropna())[1] > 0.05 for _, g in df_completo.groupby("Tavola rotonda") if len(g[col].dropna()) >= 3)
        
        normal_eta = check_normality("Età")
        normal_coinv = check_normality("Coinvolgimento")
        
        # Kruskal-Wallis se necessario
        kruskal_eta = kruskal(*gruppi_eta) if not normal_eta else None
        kruskal_coinv = kruskal(*gruppi_coinv) if not normal_coinv else None
        
        # Tabella dei risultati
        df_anova = pd.DataFrame({
            "Variabile": ["Età", "Coinvolgimento"],
            "F-value (ANOVA)": [anova_eta.statistic, anova_coinv.statistic],
            "p-value (ANOVA)": [anova_eta.pvalue, anova_coinv.pvalue],
            "Distribuzione normale?": ["✅" if normal_eta else "❌", "✅" if normal_coinv else "❌"],
            "Test alternativo": ["Kruskal-Wallis" if not normal_eta else "-", "Kruskal-Wallis" if not normal_coinv else "-"],
            "H-value (Kruskal)": [kruskal_eta.statistic if kruskal_eta else None,
                                  kruskal_coinv.statistic if kruskal_coinv else None],
            "p-value (Kruskal)": [kruskal_eta.pvalue if kruskal_eta else None,
                                  kruskal_coinv.pvalue if kruskal_coinv else None]
        })
        st.dataframe(df_anova, use_container_width=True)
        
        # Tabella semafori
        anova_eta_sig = "✅" if anova_eta.pvalue < 0.05 else "❌"
        anova_coinv_sig = "✅" if anova_coinv.pvalue < 0.05 else "❌"
        kruskal_eta_sig = "✅" if kruskal_eta and kruskal_eta.pvalue < 0.05 else "❌"
        kruskal_coinv_sig = "✅" if kruskal_coinv and kruskal_coinv.pvalue < 0.05 else "❌"
        
        st.markdown(f"""
        ---
        ### 📊 Interpretazione del test ANOVA e Kruskal-Wallis
        
        Il **test ANOVA** serve a verificare se esistono differenze tra le medie delle tavole rotonde. Se i gruppi non sono normalmente distribuiti, viene applicato in automatico il **test di Kruskal-Wallis** (non parametrico).
        
        | Variabile         | ANOVA Significativa (p < 0.05) | Dati Normali? | Kruskal-Wallis Significativo (p < 0.05) |
        |-------------------|-------------------------------|----------------|-----------------------------------------|
        | **Età**            | {anova_eta_sig}               | {"✅" if normal_eta else "❌"}         | {kruskal_eta_sig}                        |
        | **Coinvolgimento** | {anova_coinv_sig}             | {"✅" if normal_coinv else "❌"}       | {kruskal_coinv_sig}                      |
        
        ✅ = risultato significativo o condizione soddisfatta  
        ❌ = risultato non significativo o condizione non soddisfatta
        
        📌 Se almeno un test (ANOVA o Kruskal) è significativo, l'analisi continua con un **test post-hoc** per confrontare i gruppi a coppie e capire *quali tavole rotonde differiscono* tra loro.
        """)
        
        # === POST-HOC ===
        st.subheader("🔎 Analisi post-hoc")
        
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        
        if normal_eta and anova_eta.pvalue < 0.05:
            st.markdown("**Post-hoc Tukey HSD – Età**")
            tukey_eta = pairwise_tukeyhsd(df_completo["Età"], df_completo["Tavola rotonda"])
            st.dataframe(pd.DataFrame(tukey_eta.summary().data[1:], columns=tukey_eta.summary().data[0]), use_container_width=True)
        
        if not normal_eta and kruskal_eta and kruskal_eta.pvalue < 0.05:
            st.markdown("**Post-hoc Dunn – Età**")
            dunn_eta = sp.posthoc_dunn(df_completo, val_col='Età', group_col='Tavola rotonda', p_adjust='bonferroni')
            st.dataframe(dunn_eta, use_container_width=True)
        
        if normal_coinv and anova_coinv.pvalue < 0.05:
            st.markdown("**Post-hoc Tukey HSD – Coinvolgimento**")
            tukey_coinv = pairwise_tukeyhsd(df_completo["Coinvolgimento"], df_completo["Tavola rotonda"])
            st.dataframe(pd.DataFrame(tukey_coinv.summary().data[1:], columns=tukey_coinv.summary().data[0]), use_container_width=True)
        
        if not normal_coinv and kruskal_coinv and kruskal_coinv.pvalue < 0.05:
            st.markdown("**Post-hoc Dunn – Coinvolgimento**")
            dunn_coinv = sp.posthoc_dunn(df_completo, val_col='Coinvolgimento', group_col='Tavola rotonda', p_adjust='bonferroni')
            st.dataframe(dunn_coinv, use_container_width=True)
        
        # === TEST DI NORMALITÀ ===
        st.subheader("🧪 Test di normalità (Shapiro-Wilk)")
        def normality_test_by_group(df, column):
            results = []
            for name, group in df.groupby("Tavola rotonda"):
                vals = group[column].dropna()
                if len(vals) >= 3:
                    stat, p = shapiro(vals)
                    results.append({
                        "Tavola rotonda": name,
                        "Variabile": column,
                        "Shapiro-Wilk W": stat,
                        "p-value": p,
                        "Normale (α=0.05)": "✅" if p > 0.05 else "❌"
                    })
            return pd.DataFrame(results)
        
        st.markdown("#### Età")
        st.dataframe(normality_test_by_group(df_completo, "Età"), use_container_width=True)
        
        st.markdown("#### Coinvolgimento")
        st.dataframe(normality_test_by_group(df_completo, "Coinvolgimento"), use_container_width=True)
                

         # ===  === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === === ===

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
