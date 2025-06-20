import os
import logging
from dotenv import load_dotenv
import streamlit as st
from lib.style import apply_custom_style

# ─── Cloud-Ready Configurations ──────────────────────────────────────────
if os.getenv("GAE_ENV", "local") == "local":
    load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO")
)
logger = logging.getLogger(__name__)

# Funzione per recuperare segreti da Streamlit Cloud o Google Secret Manager
def get_secret(secret_key: str) -> str:
    if hasattr(st, 'secrets') and secret_key in st.secrets:
        return st.secrets[secret_key]
    try:
        from google.cloud import secretmanager
        project_id = os.getenv("GCP_PROJECT")
        secret_id = os.getenv(f"GCP_SECRET_ID_{secret_key}") or secret_key
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error("Impossibile recuperare il segreto %s: %s", secret_key, e)
        raise

# ─── Streamlit Config ────────────────────────────────────────────────────
PAGE_TITLE = os.getenv("PAGE_TITLE") or get_secret("PAGE_TITLE")
PAGE_LAYOUT = os.getenv("PAGE_LAYOUT", "wide")
PAGE_DESCRIPTION = os.getenv("PAGE_DESCRIPTION") or get_secret("PAGE_DESCRIPTION")

st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)
apply_custom_style()
logger.info("Stile applicato: %s", PAGE_TITLE)

# ─── Initialize Session State ─────────────────────────────────────────────
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("role", None)

# ─── Mappatura ruoli e accesso pagine ─────────────────────────────────────
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}

# ─── Preload Credentials ──────────────────────────────────────────────────
CRED = {
    'utente': (get_secret("UTENTE_USER"), get_secret("UTENTE_PASS")),
    'amministrazione': (get_secret("AMMIN_USER"), get_secret("AMMIN_PASS")),
    'ADMIN': (get_secret("ADMIN_USER"), get_secret("ADMIN_PASS")),
}

# ─── Sezione Login con descrizione responsive ─────────────────────────────
if not st.session_state.logged_in:
    # due colonne: sinistra descrizione, destra app title
    left_col, right_col = st.columns([1, 1], gap="large")
    with left_col:
        st.markdown("## 📄 Descrizione")
        st.markdown(PAGE_DESCRIPTION)
    with right_col:
        st.markdown("## LOTUS APP incredibile")
else:
    with st.sidebar:
        st.markdown(f"👤 **Ruolo attuale:** {st.session_state.role}")
        pages = PAGES_ACCESS.get(st.session_state.role, [])
        st.markdown("**Pagine disponibili:**")
        for p in pages:
            if st.button(f"🔗 Vai a {p}"):
                st.experimental_set_query_params(page=p)
                st.experimental_rerun()
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            logger.info("Utente disconnesso")
            st.experimental_rerun()



