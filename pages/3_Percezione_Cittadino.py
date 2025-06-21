import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
from lib.style import apply_custom_style
from lib.google_sheet import get_sheet_by_name
from lib.navigation import render_sidebar_navigation

# ✅ Configura e applica lo stile
st.set_page_config(page_title="🌿 Percezione Verde Urbano", layout="wide")
apply_custom_style()

# ✅ Verifica login
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("❌ Accesso negato. Torna alla pagina principale.")
    st.stop()

render_sidebar_navigation()

# ✅ Verifica esistenza della chiave univoca
if "id_partecipante" not in st.session_state:
    st.error("❌ Identificativo partecipante mancante. Torna alla pagina di registrazione.")
    st.stop()

# ✅ Titolo e istruzioni
st.title("Valutazione della Percezione del Verde Urbano")

st.markdown("""
Confronta tra loro i seguenti elementi del verde urbano in base alla tua percezione personale. 
Seleziona quale consideri più importante e di quanto. I dati verranno usati per costruire una matrice di pesi individuale.
""")

# Lista degli elementi significativi del verde urbano
elementi_verde = [
    "Accessibilità del verde",
    "Biodiversità",
    "Manutenzione e pulizia",
    "Funzione sociale (es. luoghi di incontro)",
    "Funzione ambientale (es. ombra, qualità aria)"
]

st.subheader("Confronti AHP tra gli elementi del verde urbano")

n = len(elementi_verde)
comparison_matrix = np.ones((n, n))

# ✅ Form con confronti AHP
with st.form("form_ahp_verde"):
    responses = {}
    st.write("Per ciascuna coppia, scegli il rapporto di importanza percepito.")
    for i in range(n):
        for j in range(i+1, n):
            el_i = elementi_verde[i]
            el_j = elementi_verde[j]
            with st.expander(f"Confronta: {el_i} vs {el_j}", expanded=False):
                option = st.radio(
                    "Quanto è più importante uno rispetto all'altro?",
                    (
                        "Sono equamente importanti",
                        f"{el_i} è poco più importante di {el_j}",
                        f"{el_i} è abbastanza più importante di {el_j}",
                        f"{el_i} è decisamente più importante di {el_j}",
                        f"{el_i} è assolutamente più importante di {el_j}",
                        f"{el_j} è poco più importante di {el_i}",
                        f"{el_j} è abbastanza più importante di {el_i}",
                        f"{el_j} è decisamente più importante di {el_i}",
                        f"{el_j} è assolutamente più importante di {el_i}"
                    ),
                    index=0,
                    key=f"{i}_{j}"
                )
                responses[f"{i}_{j}"] = option

    submitted = st.form_submit_button("Calcola Matrice Pesi")

# ✅ Calcolo della matrice AHP e salvataggio
if submitted:
    scale_map = {
        "poco più importante": 3,
        "abbastanza più importante": 5,
        "decisamente più importante": 7,
        "assolutamente più importante": 9
    }

    for i in range(n):
        for j in range(i+1, n):
            option = responses[f"{i}_{j}"]
            if "equamente" in option:
                val = 1
            elif elementi_verde[i] in option:
                val = next((v for k, v in scale_map.items() if k in option), 1)
            elif elementi_verde[j] in option:
                val = 1 / next((v for k, v in scale_map.items() if k in option), 1)
            else:
                val = 1
            comparison_matrix[i, j] = val
            comparison_matrix[j, i] = 1 / val

    matrix_df = pd.DataFrame(comparison_matrix, index=elementi_verde, columns=elementi_verde)

    eigvals, eigvecs = np.linalg.eig(comparison_matrix)
    max_index = np.argmax(eigvals.real)
    weights = eigvecs[:, max_index].real
    weights /= weights.sum()

    weights_df = pd.DataFrame({
        "Elemento": elementi_verde,
        "Peso Relativo": weights
    })

    st.subheader("📌 Pesi Relativi Calcolati")
    st.dataframe(weights_df)

    # ✅ Salvataggio su Google Sheet
    sheet = get_sheet_by_name("Dati_Partecipante", "Pesi Parametri")
    if sheet:
        row = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ID Partecipante": st.session_state["id_partecipante"],
            "Tavola rotonda": st.session_state.get("tavola_rotonda", "non specificata")
        }
        for elemento, peso in zip(elementi_verde, weights):
            row[elemento] = round(peso, 4)
        sheet.append_row(list(row.values()))
        st.success("✅ Valutazione salvata nel foglio 'Pesi Parametri'!")
    else:
        st.error("❌ Errore nel salvataggio su Google Sheet.")

    # ✅ Salva in sessione anche per la prossima pagina
    st.session_state["matrice_utente"] = matrix_df
    st.session_state["pesi_utente"] = weights_df

