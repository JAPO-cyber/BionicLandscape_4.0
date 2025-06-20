import os
import unicodedata
import logging
import streamlit as st
from lib.style import apply_custom_style

# ─── Costanti Pagine (statiche) ───────────────────────────────────────────
PAGE_TITLE = "LOTUS App"
PAGE_LAYOUT = "wide"
PAGE_DESCRIPTION = (
    "LOTUS App è la piattaforma di digital transformation che ti aiuta a semplificare i processi, "
    "analizzare i dati e ottenere report in tempo reale, il tutto in un'unica interfaccia intuitiva."
)
# Quartieri del comune di Bergamo
QUARTIERI = [
    "Città Alta",
    "Città Bassa",
    "Valtesse",
    "Malpensata",
    "Longuelo",
    "Borgo Santa Caterina",
    "Redona",
    "Celadina",
]

# ─── Modalità di recupero segreti ──────────────────────────────────────────
# Opzioni: "Streamlit Secrets" o "Google Secret Manager"
SECRET_METHOD = "Streamlit Secrets"

# ─── Pagine Accesso per ruolo ─────────────────────────────────────────────
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}

# ─── Funzione per recuperare segreti ───────────────────────────────────────
def get_secret(key: str) -> str:
    try:
        if SECRET_METHOD == "Streamlit Secrets":
            return st.secrets.get(key, "")
        from google.cloud import secretmanager
        project_id = os.getenv("GCP_PROJECT", "")
        secret_id = os.getenv(f"GCP_SECRET_ID_{key}") or key
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logging.error(f"Errore recupero segreto {key}: {e}")
        return ""

# ─── Configurazione Streamlit e applicazione stile ─────────────────────────
st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)
apply_custom_style()

# ─── Logging setup ─────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO")
)
logger = logging.getLogger(__name__)
logger.info(f"Avvio pagina: {PAGE_TITLE}")

# ─── Inizializzazione session state ────────────────────────────────────────
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("role", None)
st.session_state.setdefault("quartiere", None)

# ─── Header: Titolo e Descrizione (sempre visibili) ────────────────────────
st.markdown(f"# {PAGE_TITLE}")
st.write(PAGE_DESCRIPTION)
st.markdown("---")

# ─── Sezione di Accesso (se non autenticato) ──────────────────────────────
if not st.session_state.logged_in:
    st.markdown("## 🔐 Accesso Quartieri")
    with st.form(key="login_form"):
        username = st.text_input("Username", key="login_user")
        selected_quartiere = st.selectbox("Seleziona Quartiere", QUARTIERI, key="login_quartiere")
        password = st.text_input("Password Quartiere o ADMIN", type="password", key="login_pass")
        submit = st.form_submit_button("Accedi")
        if submit:
            # 1) ADMIN
            if username == get_secret("ADMIN_USER") and password == get_secret("ADMIN_PASS"):
                st.session_state.logged_in = True
                st.session_state.role = 'ADMIN'
                st.session_state.quartiere = None
                st.query_params = {"page": PAGES_ACCESS['ADMIN'][0]}
                st.rerun()
            # 2) amministrazione
            if username == get_secret("AMMIN_USER") and password == get_secret("AMMIN_PASS"):
                st.session_state.logged_in = True
                st.session_state.role = 'amministrazione'
                st.session_state.quartiere = None
                st.query_params = {"page": PAGES_ACCESS['amministrazione'][0]}
                st.rerun()
            # 3) utente quartiere
            raw = unicodedata.normalize('NFD', selected_quartiere)
            safe = raw.encode('ascii', 'ignore').decode('utf-8').upper().replace(' ', '_')
            pw_key = f"PW_{safe}"
            if password and password == get_secret(pw_key):
                st.session_state.logged_in = True
                st.session_state.role = 'utente'
                st.session_state.quartiere = selected_quartiere
                st.query_params = {"page": PAGES_ACCESS['utente'][0]}
                st.rerun()
            else:
                st.error("❌ Credenziali o password non valide")

# ─── Informazioni aggiuntive (Autori + Credits) ───────────────────────────
st.markdown("---")
st.markdown("## Autori e Credits")
authors = [
    {"name": "Alice Rossi", "image": "ASSETT/alice.png", "desc": "Data Scientist e UX Designer"},
    {"name": "Bruno Bianchi", "image": "ASSETT/bruno.png", "desc": "Esperto di Cloud e DevOps"},
    {"name": "Chiara Verdi", "image": "ASSETT/chiara.png", "desc": "Full Stack Developer e PM"},
]
for author in authors:
    col1, col2 = st.columns([1, 3], gap="medium")
    with col1:
        if os.path.exists(author["image"]):
            st.image(author["image"], width=100)
        else:
            st.write("[Immagine non disponibile]")
    with col2:
        st.markdown(f"**{author['name']}**  \n{author['desc']}")
st.markdown("**Credits:** App sviluppata da Alice, Bruno e Chiara in collaborazione con il team Lotus.")

# ─── Sidebar di navigazione (se autenticato) ───────────────────────────────
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown(f"**Ruolo:** {st.session_state.role}")
        quart = st.session_state.quartiere or '—'
        st.markdown(f"**Quartiere:** {quart}")
        st.markdown("### Sezioni disponibili")
        for page in PAGES_ACCESS[st.session_state.role]:
            if st.button(page, key=f"nav_{page}"):
                st.query_params = {"page": page}
                st.rerun()
        if st.button("Logout", key="logout_btn"):
            st.session_state.clear()
            st.rerun()



