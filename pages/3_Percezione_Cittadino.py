import streamlit as st
import pandas as pd
import numpy as np
import io

st.title("3. Valutazione della Percezione del Verde Urbano")
st.markdown("""
Confronta tra loro i seguenti elementi del verde urbano in base alla tua percezione personale. 
Seleziona quale consideri più importante e di quanto. I dati verranno usati per costruire una **matrice AHP individuale**.
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

    submitted = st.form_submit_button("Calcola Matrice AHP")

if submitted:
    # Mappatura valori AHP (scala di Saaty)
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
                for k, v in scale_map.items():
                    if k in option:
                        val = v
                        break
            elif elementi_verde[j] in option:
                for k, v in scale_map.items():
                    if k in option:
                        val = 1 / v
                        break
            else:
                val = 1
            comparison_matrix[i, j] = val
            comparison_matrix[j, i] = 1 / val

    matrix_df = pd.DataFrame(comparison_matrix, index=elementi_verde, columns=elementi_verde)
    st.subheader("📊 Matrice AHP Personale")
    st.dataframe(matrix_df)

    # Calcolo autovalore principale e vettore dei pesi normalizzati
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

    # Esportazione dei risultati
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        matrix_df.to_excel(writer, sheet_name="Matrice AHP")
        weights_df.to_excel(writer, sheet_name="Pesi Relativi", index=False)
    excel_data = output.getvalue()

    st.download_button(
        "📥 Scarica la tua valutazione AHP (Excel)",
        data=excel_data,
        file_name="valutazione_verde_ahp.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Salva nel session state per la pagina successiva
    st.session_state["matrice_utente"] = matrix_df
    st.session_state["pesi_utente"] = weights_df
