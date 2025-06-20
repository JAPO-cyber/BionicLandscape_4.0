import os
import logging
from dotenv import load_dotenv
import streamlit as st
from lib.style import apply_custom_style

# ─── Cloud-Ready Configurations ──────────────────────────────────────────
if os.getenv("GAE_ENV", "local") == "local":
    load_dotenv()

# Logging setup
logging.basicConfig(
    format="%((asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO")
)
logger = logging.getLogger(__name__)

# Secret retrieval
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
        logger.error("Error retrieving secret %s: %s", secret_key, e)
        raise

# Streamlit page config
PAGE_TITLE = os.getenv("PAGE_TITLE") or get_secret("PAGE_TITLE")
PAGE_LAYOUT = os.getenv("PAGE_LAYOUT", "wide")
PAGE_DESCRIPTION = os.getenv("PAGE_DESCRIPTION") or get_secret("PAGE_DESCRIPTION")
st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)
apply_custom_style()
logger.info("Applied custom style for %s", PAGE_TITLE)

# Session state init
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("role", None)

# Role-based pages
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}
# Credentials
CRED = {
    role: (get_secret(f"{role.upper()}_USER"), get_secret(f"{role.upper()}_PASS"))
    for role in PAGES_ACCESS
}

# Login page: left description, right login
if not st.session_state.logged_in:
    cols = st.columns([1, 1], gap="large")
    with cols[0]:
        st.markdown("# Benvenuto in LOTUS App")
        st.write(PAGE_DESCRIPTION)
    with cols[1]:
        st.markdown("## 🔐 Accesso")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Accedi", key="login_btn"):
            auth_role = None
            for role, creds in CRED.items():
                if username == creds[0] and password == creds[1]:
                    auth_role = role
                    break
            if auth_role:
                st.session_state.logged_in = True
                st.session_state.role = auth_role
                logger.info("%s logged in as %s", username, auth_role)
                st.experimental_set_query_params(page=PAGES_ACCESS[auth_role][0])
                st.experimental_rerun()
            else:
                st.error("Credenziali non valide")
else:
    # Sidebar navigation for logged in users
    with st.sidebar:
        st.markdown(f"**Ruolo:** {st.session_state.role}")
        st.markdown("### Sezioni disponibili")
        for p in PAGES_ACCESS[st.session_state.role]:
            if st.button(p):
                st.experimental_set_query_params(page=p)
                st.experimental_rerun()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.experimental_rerun()

