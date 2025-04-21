import streamlit as st

# Funzione per salvataggio su Google Sheets (pronta da usare)
def salva_su_google_sheet(dati_dict):
    import pandas as pd
    from streamlit_gsheets import GSheetsConnection

    conn = st.connection("gsheets", type=GSheetsConnection)
    sheet_df = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit")
    nuovo_df = pd.concat([sheet_df, pd.DataFrame([dati_dict])], ignore_index=True)
    conn.update(nuovo_df)


if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Accesso negato. Torna alla pagina principale.")
    st.stop()

st.title("🏠 Benvenuto nella dashboard di Bionic 4.0")
st.markdown("### 📝 Inserisci le tue informazioni per partecipare al workshop:")

with st.form("user_info_form"):

    tavola_rotonda = st.selectbox(
        "🔘 Tavola rotonda",
        [
            "Digitale e città",
            "Transizione ecologica",
            "Spazi pubblici e comunità",
            "Futuro del lavoro",
            "Cultura e creatività",
        ]
    )
    
    nome = st.text_input("👤 Nome")
    eta = st.number_input("🎂 Età", min_value=16, max_value=100, step=1)
    professione = st.text_input("💼 Professione")
    ruolo = st.selectbox(
        "🎭 Qual è il tuo ruolo in questo progetto?",
        ["Cittadino interessato", "Tecnico/Esperto", "Rappresentante istituzionale", "Studente", "Altro"]
    )
    formazione = st.text_input("🎓 Formazione o background (facoltativo)", placeholder="Esempio: Architettura, Economia, Informatica...")

    ambito = st.selectbox(
        "🌱 Qual è il tuo principale ambito di interesse?",
        ["Urbanistica", "Tecnologia e digitale", "Transizione ecologica", 
         "Inclusione sociale", "Economia e lavoro", "Cultura e creatività"]
    )

    esperienza = st.radio(
        "🧭 Hai già partecipato ad altri progetti partecipativi?",
        ["Sì", "No"]
    )

    coinvolgimento = st.slider(
        "📍 Quanto ti senti coinvolto/a nella vita del tuo territorio?",
        0, 10, 5
    )

    conoscenza = st.slider(
        "📚 Quanto conosci il tema di questa tavola rotonda?",
        0, 10, 5
    )

    motivazione = st.text_area(
        "🗣️ Cosa ti ha spinto a partecipare a questo tavolo di lavoro?",
        placeholder="Scrivi liberamente..."
    )

    obiettivo = st.text_area(
        "🎯 Cosa ti piacerebbe ottenere da questo incontro?",
        placeholder="Ad esempio: conoscere persone, contribuire a un'idea, essere aggiornato..."
    )

    visione = st.radio(
        "🔍 Ti senti più orientato a...",
        ["Valori tradizionali", "Innovazione", "Equilibrio tra i due"]
    )

    valori = st.multiselect(
        "❤️ Quali di questi valori senti più vicini?",
        ["Innovazione", "Collaborazione", "Responsabilità", "Tradizione", "Trasparenza", "Inclusione"]
    )

    canale = st.selectbox(
        "📡 Come preferisci essere aggiornato su iniziative pubbliche?",
        ["Email", "Social", "Eventi pubblici", "Siti ufficiali", "Bacheche locali"]
    )

    submitted = st.form_submit_button("Invia")

if submitted:
    dati_utente = {
        "Tavola rotonda": tavola_rotonda,
        "Nome": nome,
        "Età": eta,
        "Professione": professione,
        "Formazione": formazione,
        "Ruolo": ruolo,
        "Ambito": ambito,
        "Esperienza": esperienza,
        "Coinvolgimento": coinvolgimento,
        "Conoscenza tema": conoscenza,
        "Motivazione": motivazione,
        "Obiettivo": obiettivo,
        "Visione": visione,
        "Valori": ", ".join(valori),
        "Canale preferito": canale
    }

    # 🔐 Salvataggio su Google Sheet - attiva quando sei pronto
    # salva_su_google_sheet(dati_utente)

    st.success("✅ Grazie per aver inviato le tue informazioni!")

    st.markdown("### 📊 Dati raccolti:")
    for chiave, valore in dati_utente.items():
        st.write(f"**{chiave}**: {valore}")

