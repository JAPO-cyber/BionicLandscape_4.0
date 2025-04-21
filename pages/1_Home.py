import streamlit as st

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Accesso negato. Torna alla pagina principale.")
    st.stop()

st.title("🏠 Benvenuto nella dashboard di Bionic 4.0")
st.markdown("### 📝 Inserisci le tue informazioni per partecipare al workshop:")

with st.form("user_info_form"):

    # 1. Tavola rotonda
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
    
    # 2. Identità e ruolo
    nome = st.text_input("👤 Nome")
    eta = st.number_input("🎂 Età", min_value=16, max_value=100, step=1)
    professione = st.text_input("💼 Professione")
    
    ruolo = st.selectbox(
        "🎭 Qual è il tuo ruolo in questo progetto?",
        ["Cittadino interessato", "Tecnico/Esperto", "Rappresentante istituzionale", "Studente", "Altro"]
    )
    
    formazione = st.text_input("🎓 Formazione o background (facoltativo)", placeholder="Esempio: Architettura, Economia, Informatica...")

    # 3. Ambito e motivazioni
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

# Risultato
if submitted:
    st.success("✅ Grazie per aver inviato le tue informazioni!")

    st.markdown("### 📊 Dati raccolti:")
    st.write(f"🧩 **Tavola rotonda**: {tavola_rotonda}")
    st.write(f"👤 **Nome**: {nome}")
    st.write(f"🎂 **Età**: {eta}")
    st.write(f"💼 **Professione**: {professione}")
    st.write(f"🎓 **Formazione**: {formazione}")
    st.write(f"🎭 **Ruolo**: {ruolo}")
    st.write(f"🌱 **Ambito di interesse**: {ambito}")
    st.write(f"🧭 **Esperienza pregressa**: {esperienza}")
    st.write(f"📍 **Coinvolgimento nel territorio**: {coinvolgimento}/10")
    st.write(f"📚 **Conoscenza del tema**: {conoscenza}/10")
    st.write(f"🗣️ **Motivazione**: {motivazione}")
    st.write(f"🎯 **Obiettivo personale**: {obiettivo}")
    st.write(f"🔍 **Visione**: {visione}")
    st.write(f"❤️ **Valori**: {', '.join(valori)}")
    st.write(f"📡 **Canale preferito**: {canale}")
