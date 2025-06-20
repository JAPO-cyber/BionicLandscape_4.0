import os
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

# ─── Configurazione e Logging ──────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO")
)
logger = logging.getLogger(__name__)

# ─── Funzione per recuperare segreti da Secret Manager (solo per credenziali) ─
def get_secret(secret_key: str) -> str:
    if hasattr(st, 'secrets') and secret_key in st.secrets:
        return st.secrets[secret_key]
    from google.cloud import secretmanager
    project_id = os.getenv("GCP_PROJECT")
    secret_id = os.getenv(f"GCP_SECRET_ID_{secret_key}") or secret_key
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

# ─── Configurazione Streamlit ────────────────────────────────────────────
st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)
apply_custom_style()
logger.info("Pagina iniziale: %s", PAGE_TITLE)

# ─── Stato Sessione ───────────────────────────────────────────────────────
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("role", None)

# ─── Dizionari di Accesso e Credenziali ───────────────────────────────────
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}

CRED = {
    role: (get_secret(f"{role.upper()}_USER"), get_secret(f"{role.upper()}_PASS"))
    for role in PAGES_ACCESS
}

# ─── Descrizione Pagina (sempre visibile) ─────────────────────────────────
st.markdown(f"# {PAGE_TITLE}")
st.write(PAGE_DESCRIPTION)
st.markdown("---")

# ─── Sezione Accesso o Navigazione ────────────────────────────────────────
if not st.session_state.logged_in:
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
            logger.info("%s autenticato come %s", username, auth_role)
            st.experimental_set_query_params(page=PAGES_ACCESS[auth_role][0])
            st.experimental_rerun()
        else:
            st.error("Credenziali non valide")
else:
    with st.sidebar:
        st.markdown(f"**Ruolo:** {st.session_state.role}")
        st.markdown("### Sezioni disponibili")
        for p in PAGES_ACCESS[st.session_state.role]:
            if st.button(p, key=f"nav_{p}"):
                st.experimental_set_query_params(page=p)
                st.experimental_rerun()
        if st.button("Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.experimental_rerun()
