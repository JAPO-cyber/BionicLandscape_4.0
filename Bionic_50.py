import os
import unicodedata
import logging
import streamlit as st
from lib.style import apply_custom_style

# ─── Costanti Pagina ──────────────────────────────────────────────────────
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

# Metodo di recupero segreti: "Streamlit Secrets" o "Google Secret Manager"
SECRET_METHOD = "Streamlit Secrets"

# Definizione delle pagine accessibili per ruolo
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}

# Funzione per recuperare segreti
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

# Configurazione Streamlit e stile
st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)
apply_custom_style()

# Logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO")
)
logger = logging.getLogger(__name__)
logger.info(f"Avvio pagina: {PAGE_TITLE}")

# Inizializza session state
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("role", None)
st.session_state.setdefault("quartiere", None)

# Header comune
st.markdown(f"# {PAGE_TITLE}")
st.write(PAGE_DESCRIPTION)
st.markdown("---")

# Sezione login
if not st.session_state.logged_in:
    st.markdown("## 🔐 Accesso Quartieri")
    with st.form(key="login_form"):
        username = st.text_input("Username")
        selected_quartiere = st.selectbox("Seleziona Quartiere", QUARTIERI)
        password = st.text_input("Password Quartiere o ADMIN", type="password")
        submitted = st.form_submit_button("Accedi")
        if submitted:
            # Controllo ADMIN
            if username == get_secret("ADMIN_USER") and password == get_secret("ADMIN_PASS"):
                st.session_state.logged_in = True
                st.session_state.role = "ADMIN"
                st.session_state.quartiere = "Tutti"
                logger.info("ADMIN autenticato")
                st.experimental_set_query_params(page=PAGES_ACCESS['ADMIN'][0])
                st.experimental_rerun()
            # Controllo amministrazione
            if username == get_secret("AMMIN_USER") and password == get_secret("AMMIN_PASS"):
                st.session_state.logged_in = True
                st.session_state.role = "amministrazione"
                st.session_state.quartiere = "Tutti"
                logger.info("Amministrazione autenticato")
                st.experimental_set_query_params(page=PAGES_ACCESS['amministrazione'][0])
                st.experimental_rerun()
            # Controllo utente quartiere
            raw = unicodedata.normalize('NFD', selected_quartiere)
            safe = raw.encode('ascii', 'ignore').decode('utf-8').upper().replace(' ', '_')
            secret_key = f"PW_{safe}"
            if password == get_secret(secret_key) and password != "":
                st.session_state.logged_in = True
                st.session_state.role = "utente"
                st.session_state.quartiere = selected_quartiere
                logger.info(f"Utente quartiere {selected_quartiere} autenticato")
                st.experimental_set_query_params(page=PAGES_ACCESS['utente'][0])
                st.experimental_rerun()
            st.error("❌ Credenziali o password quartiere non valide")

# Sidebar navigazione dopo login
else:
    with st.sidebar:
        st.markdown(f"**Ruolo:** {st.session_state.role}")
        st.markdown(f"**Quartiere:** {st.session_state.quartiere}")
        st.markdown("### Sezioni disponibili")
        for page in PAGES_ACCESS[st.session_state.role]:
            if st.button(page):
                st.experimental_set_query_params(page=page)
                st.experimental_rerun()
        if st.button("Logout"):
            st.session_state.clear()
            st.experimental_rerun()
