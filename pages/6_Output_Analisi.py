

# ✅ Filtri base
df_valutazioni_f = df_valutazioni.copy()
if tavola_sel != "Tutte":
    df_valutazioni_f = df_valutazioni[df_valutazioni["Tavola rotonda"] == tavola_sel]
    df_pesi = df_pesi[df_pesi["Tavola rotonda"] == tavola_sel]

# ✅ Calcolo media e punteggi con analisi della variabilità
media_val = df_valutazioni_f.groupby("Parco")[criteri].mean()
std_val = df_valutazioni_f.groupby("Parco")[criteri].std()

st.markdown("### 📊 Analisi statistica preliminare")
st.markdown("Nella tabella seguente sono riportati i voti medi e la deviazione standard per ciascun criterio, parco per parco. Questo permette di individuare parchi con giudizi instabili o potenzialmente influenzati da outlier.")

st.dataframe(
    pd.concat(
        [media_val.add_suffix(" (Media)"), std_val.add_suffix(" (Dev. Std)")],
        axis=1
    ).round(2)
)

soglia_std = 1.2
mask_outlier = std_val.max(axis=1) > soglia_std

if mask_outlier.any():
    st.warning(f"⚠️ {mask_outlier.sum()} parchi esclusi per alta variabilità nei voti (Dev. Std > {soglia_std})")
    media_val = media_val[~mask_outlier]
else:
    st.success("✅ Tutti i parchi rientrano nei limiti accettabili di variabilità")

pesi_dict = df_pesi[criteri].mean().to_dict()

def calcola_punteggio(riga):
    return sum(riga[c] * pesi_dict.get(c, 0) for c in criteri)

media_val = media_val.reset_index()
media_val["punteggio"] = media_val.apply(calcola_punteggio, axis=1)

map_df = pd.merge(media_val, df_info, left_on="Parco", right_on="Nome del Parco", how="inner")

if media_val.empty:
    st.error("❌ Nessun parco con valutazioni disponibili dopo il filtraggio.")
    st.stop()

if map_df.empty:
    st.error("❌ Nessun match trovato tra parchi valutati e anagrafica parchi.")
    st.stop()

map_df["Latitudine"] = pd.to_numeric(map_df["Latitudine"], errors="coerce")
map_df["Longitudine"] = pd.to_numeric(map_df["Longitudine"], errors="coerce")
map_df = map_df.dropna(subset=["Latitudine", "Longitudine"])

if quartiere_sel != "Tutti":
    map_df = map_df[map_df["Quartiere"] == quartiere_sel]

# ✅ Applichiamo un round per evitare errori di precisione
map_df["punteggio"] = map_df["punteggio"].round(2)



def punteggio_to_rgb(p):
    if p <= 2:
        r = 255
        g = int(255 * (p - 1))
    elif p <= 4:
        r = int(255 * (1 - (p - 2) / 2))
        g = 255
    else:
        r = 0
        g = 255
    return [r, g, 0, 160]

map_df["color"] = map_df["punteggio"].apply(punteggio_to_rgb)

