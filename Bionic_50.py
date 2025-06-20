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

# ─── Modalità di recupero segreti (impostare manualmente in codice) ────────
# Opzioni: "Streamlit Secrets" o "Google Secret Manager"
SECRET_METHOD = "Streamlit Secrets"

# ─── Configurazione Streamlit ────────────────────────────────────────────
st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)
apply_custom_style()

# ─── Configurazione e Logging ──────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO")
)
logger = logging.getLogger(__name__)
logger.info("Pagina iniziale caricata: %s", PAGE_TITLE)

# ─── Funzione per recuperare segreti ───────────────────────────────────────
def get_secret(secret_key: str) -> str:
    if SECRET_METHOD == "Streamlit Secrets":
        if hasattr(st, 'secrets') and secret_key in st.secrets:
            return st.secrets[secret_key]
        else:
            raise KeyError(f"Segreto '{secret_key}' non trovato in Streamlit Secrets")
    # Google Secret Manager
    from google.cloud import secretmanager
    project_id = os.getenv("GCP_PROJECT")
    secret_id = os.getenv(f"GCP_SECRET_ID_{secret_key}") or secret_key
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

# ─── Stato Sessione ───────────────────────────────────────────────────────
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("role", None)

# ─── Mappatura pagine e credenziali ───────────────────────────────────────
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}

CRED = {}
for role in PAGES_ACCESS:
    user_key = f"{role.upper()}_USER"
    pass_key = f"{role.upper()}_PASS"
    CRED[role] = (get_secret(user_key), get_secret(pass_key))

# ─── Header: Titolo e Descrizione (sempre visibili) ────────────────────────
st.markdown(f"# {PAGE_TITLE}")
st.write(PAGE_DESCRIPTION)
st.markdown("---")

# ─── Sezione di Accesso (se non autenticato) ──────────────────────────────
if not st.session_state.logged_in:
    st.markdown("## 🔐 Accesso")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Accedi", key="login_btn"):
        auth_role = None
        for role, (u, p) in CRED.items():
            if username == u and password == p:
                auth_role = role
                break
        if auth_role:
            st.session_state.logged_in = True
            st.session_state.role = auth_role
            logger.info("%s autenticato come %s", username, auth_role)
            first_page = PAGES_ACCESS[auth_role][0]
            st.experimental_set_query_params(page=first_page)
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

