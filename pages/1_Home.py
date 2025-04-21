import streamlit as st
import base64

# ✅ Funzione per convertire l'immagine in base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ✅ Imposta l'immagine di sfondo con overlay
def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        position: relative;
    }}
    .overlay {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.6);
        z-index: 0;
    }}
    .main-content {{
        position: relative;
        z-index: 1;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# ✅ Imposta l'immagine di sfondo
set_background('assets/bg.jpg')  # Assicurati che il percorso sia corretto

# ✅ Inizio del contenuto principale
st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ✅ Contenuto della pagina
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

# ✅ Dopo l'invio
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

    # salva_su_google_sheet(dati_utente)  # Attiva quando pronto

    st.success("✅ Grazie per aver inviato le tue informazioni!")

    st.markdown("### 📊 Dati raccolti:")
    for chiave, valore in dati_utente.items():
        st.write(f"**{chiave}**: {valore}")

    st.markdown("---")
    st.page_link("pages/2_Persona_Model.py", label="➡️ Vai a Persona Model", icon="👤")

# ✅ Fine del contenuto principale
st.markdown('</div>', unsafe_allow_html=True)


