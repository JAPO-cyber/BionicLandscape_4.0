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

# ─── Modalità di recupero segreti (impostare manualmente in codice) ────────
# Opzioni: "Streamlit Secrets" o "Google Secret Manager"
SECRET_METHOD = "Streamlit Secrets"

# ─── Mappatura pagine e credenziali ───────────────────────────────────────
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}

# ─── Funzione per recuperare segreti ───────────────────────────────────────
def get_secret(secret_key: str) -> str:
    try:
        if SECRET_METHOD == "Streamlit Secrets":
            return st.secrets.get(secret_key, "")
        from google.cloud import secretmanager
        project_id = os.getenv("GCP_PROJECT", "")
        secret_id = os.getenv(f"GCP_SECRET_ID_{secret_key}") or secret_key
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logging.error(f"Errore recupero segreto {secret_key}: {e}")
        return ""

# ─── Configurazione Streamlit e stile ─────────────────────────────────────
st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)
apply_custom_style()

# ─── Logging setup ─────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO")
)
logger = logging.getLogger(__name__)
logger.info(f"Pagina iniziale caricata: {PAGE_TITLE}")

# ─── Stato sessione ────────────────────────────────────────────────────────
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("role", None)

# ─── Header: Titolo e Descrizione (sempre visibili) ────────────────────────
st.markdown(f"# {PAGE_TITLE}")
st.write(PAGE_DESCRIPTION)
st.markdown("---")

# ─── Sezione di Accesso (se non autenticato) ──────────────────────────────
if not st.session_state.logged_in:
    st.markdown("## 🔐 Accesso")
    with st.form(key='login_form'):
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        submit = st.form_submit_button("Accedi")
        if submit:
            # 1) Controllo ADMIN
            admin_user = get_secret("ADMIN_USER")
            admin_pass = get_secret("ADMIN_PASS")
            if username == admin_user and password == admin_pass:
                st.session_state.logged_in = True
                st.session_state.role = "ADMIN"
                logger.info(f"{username} autenticato come ADMIN")
                st.experimental_set_query_params(page=PAGES_ACCESS["ADMIN"][0])
                st.experimental_rerun()

            # 2) Controllo utente standard
            user_creds = get_secret("UTENTE_USER"), get_secret("UTENTE_PASS")
            admin_creds = get_secret("AMMIN_USER"), get_secret("AMMIN_PASS")
            if (username, password) == user_creds:
                st.session_state.logged_in = True
                st.session_state.role = 'utente'
                logger.info(f"{username} autenticato come utente")
                st.experimental_set_query_params(page=PAGES_ACCESS['utente'][0])
                st.experimental_rerun()
            elif (username, password) == admin_creds:
                st.session_state.logged_in = True
                st.session_state.role = 'amministrazione'
                logger.info(f"{username} autenticato come amministrazione")
                st.experimental_set_query_params(page=PAGES_ACCESS['amministrazione'][0])
                st.experimental_rerun()
            else:
                st.error("❌ Credenziali non valide")

# ─── Sidebar di navigazione (se autenticato) ───────────────────────────────
else:
    with st.sidebar:
        st.markdown(f"**Ruolo corrente:** {st.session_state.role}")
        st.markdown("### Sezioni disponibili")
        for page in PAGES_ACCESS[st.session_state.role]:
            if st.button(f"🔗 {page}", key=f"nav_{page}"):
                st.experimental_set_query_params(page=page)
                st.experimental_rerun()
        if st.button("🔓 Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.experimental_rerun()


