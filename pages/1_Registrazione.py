import os
import unicodedata
import logging
import streamlit as st
from lib.style import apply_custom_style

# ─── Mappatura pagine accesso globale ──────────────────────────────────────
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}

# ─── Costanti Pagine (statiche) ───────────────────────────────────────────
PAGE_TITLE = "LOTUS App"
PAGE_LAYOUT = "wide"
PAGE_DESCRIPTION = (
    "LOTUS App è la piattaforma di digital transformation che ti aiuta a semplificare i processi, "
    "analizzare i dati e ottenere report in tempo reale, il tutto in un'unica interfaccia intuitiva."
)

QUARTIERI = [
    "Città Alta", "Città Bassa", "Valtesse", "Malpensata",
    "Longuelo", "Borgo Santa Caterina", "Redona", "Celadina"
]

SECRET_METHOD = "Streamlit Secrets"

# ─── Recupero segreti ───────────────────────────────────────
def get_secret(key: str) -> str:
    try:
        if SECRET_METHOD == "Streamlit Secrets":
            return st.secrets.get(key, "")
        from google.cloud import secretmanager
        project_id = os.getenv("GCP_PROJECT", "")
        secret_id = os.getenv(f"GCP_SECRET_ID_{key}", key)
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logging.error(f"Errore recupero segreto '{key}': {e}")
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
logger.info(f"Avvio pagina: {PAGE_TITLE}")

# ─── Inizializzazione session state ────────────────────────────────────────
for key in ["logged_in", "role", "quartiere"]:
    st.session_state.setdefault(key, None)

# ─── Navigazione multipage ────────────────────────────────────────
params = st.experimental_get_query_params()
if "page" in params:
    st.switch_page(params["page"][0])

# ─── Header ──────────────────────────────────────────────────────────
st.markdown(f"# {PAGE_TITLE}")
st.write(PAGE_DESCRIPTION)
st.markdown("---")

# ─── Gestione Login ────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("## 🔐 Accesso Quartieri")
    with st.form("login_form"):
        username = st.text_input("Username")
        selected_quartiere = st.selectbox("Seleziona Quartiere", QUARTIERI)
        password = st.text_input("Password Quartiere o ADMIN", type="password")
        submit = st.form_submit_button("Accedi")

    if submit:
        valid_login = False
        for role, creds in [("ADMIN", ("ADMIN_USER", "ADMIN_PASS")),
                            ("amministrazione", ("AMMIN_USER", "AMMIN_PASS"))]:
            if username == get_secret(creds[0]) and password == get_secret(creds[1]):
                st.session_state.update({"logged_in": True, "role": role, "quartiere": None})
                st.rerun()

        if not valid_login:
            safe_quartiere = unicodedata.normalize('NFD', selected_quartiere)
            safe_quartiere = safe_quartiere.encode('ascii', 'ignore').decode().upper().replace(' ', '_')
            quartiere_key = f"PW_{safe_quartiere}"
            if password and password == get_secret(quartiere_key):
                st.session_state.update({
                    "logged_in": True,
                    "role": "utente",
                    "quartiere": selected_quartiere
                })
                st.rerun()
            else:
                st.error("❌ Credenziali non valide")
else:
    # ─── Navigazione con pulsanti ────────────────────────────
    st.markdown("## 📌 Naviga nelle sezioni")
    for page in PAGES_ACCESS.get(st.session_state.role, []):
        page_file = f"pages/{page}.py"
        if st.button(page, key=f"page_{page}"):
            st.switch_page(page_file)

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

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
        st.image(author["image"], width=100) if os.path.exists(author["image"]) else st.write("[Immagine non disponibile]")
    with col2:
        st.markdown(f"**{author['name']}**  \n{author['desc']}")
