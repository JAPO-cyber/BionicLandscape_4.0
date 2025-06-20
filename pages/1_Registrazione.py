import streamlit as st
import pandas as pd
import datetime
import secrets
import string
from lib.google_sheet import get_sheet_by_name
from lib.style import apply_custom_style

# ─── Funzione per recuperare segreti (copiata localmente) ──────────────────
# Utilizza SECRET_METHOD ereditato dalla session state
SECRET_METHOD = st.session_state.get("secret_method", "Streamlit Secrets")
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
from lib.sql_questions import fetch_questions_for_quartiere, ensure_questions_table
from lib.save_to_sheet import save_to_sheet
from lib.save_to_sql import save_to_sql

# ─── Mappatura pagine accesso globale ──────────────────────────────────────
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}

# ─── Configura pagina ──────────────────────────────────────────────────────
st.set_page_config(page_title="Registrazione", layout="wide")

# ─── Verifica login ───────────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    st.error("❌ Accesso negato. Torna alla pagina principale.")
    st.stop()

# ─── Applica stile grafico ─────────────────────────────────────────────────
apply_custom_style()

# ─── Eredita quartiere e metodo segreti dal main ──────────────────────────
quartiere = st.session_state.get("quartiere", "")
secret_method = st.session_state.get("secret_method", "Streamlit Secrets")

# ─── Genera un ID univoco ───────────────────────────────────────────────────
def genera_id_univoco(lunghezza=16):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(lunghezza))

if "id_partecipante" not in st.session_state:
    try:
        sheet = get_sheet_by_name("Dati_Partecipante", "Partecipanti")
        existing = [r[3] for r in sheet.get_all_values()[1:]]
        new_id = genera_id_univoco()
        while new_id in existing:
            new_id = genera_id_univoco()
        st.session_state["id_partecipante"] = new_id
    except Exception as e:
        st.error("❌ Errore nella generazione dell'ID partecipante.")
        st.text(f"Dettaglio: {e}")
        st.stop()

# ─── Titolo e informazioni ─────────────────────────────────────────────────
st.markdown('<div class="header">🏠 Pagina di Registrazione</div>', unsafe_allow_html=True)
st.markdown(f"### ID: `{st.session_state['id_partecipante']}` | Quartiere: **{quartiere}**")
st.markdown("---")

# ─── Prepara opzioni tavola in modalità Streamlit Secrets ────────────────
if secret_method == "Streamlit Secrets":
    try:
        sheet_attive = get_sheet_by_name("Dati_Partecipante", "Tavola Rotonda Attiva")
        df_attive = pd.DataFrame(sheet_attive.get_all_records())
        opzioni = df_attive["Tavola Rotonda Attiva"].dropna().unique().tolist()
        if not opzioni:
            opzioni = ["(nessuna disponibile)"]
    except Exception:
        opzioni = ["(errore connessione)"]

# ─── Carica domande dinamiche (solo SQL) ────────────────────────────────────
questions = []
if secret_method != "Streamlit Secrets":
    ensure_questions_table()
    questions = fetch_questions_for_quartiere(quartiere)

# ─── Sezione di Accesso Quartieri ─────────────────────────────────────────
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
            st.experimental_set_query_params(page=PAGES_ACCESS['ADMIN'][0])
            st.experimental_rerun()
        # 2) Amministrazione
        elif username == get_secret("AMMIN_USER") and password == get_secret("AMMIN_PASS"):
            st.session_state.logged_in = True
            st.session_state.role = 'amministrazione'
            st.session_state.quartiere = None
            st.experimental_set_query_params(page=PAGES_ACCESS['amministrazione'][0])
            st.experimental_rerun()
        # 3) Utente quartiere
        else:
            raw = unicodedata.normalize('NFD', selected_quartiere)
            safe = raw.encode('ascii', 'ignore').decode('utf-8').upper().replace(' ', '_')
            pw_key = f"PW_{safe}"
            if password and password == get_secret(pw_key):
                st.session_state.logged_in = True
                st.session_state.role = 'utente'
                st.session_state.quartiere = selected_quartiere
                st.experimental_set_query_params(page=PAGES_ACCESS['utente'][0])
                st.experimental_rerun()
            else:
                st.error("❌ Credenziali o password non valide")

# ─── Navigazione sotto il login ───────────────────────────────────────────
if st.session_state.logged_in:
    st.markdown("---")
    st.markdown("### Sezioni disponibili")
    for page in PAGES_ACCESS[st.session_state.role]:
        if st.button(page, key=f"nav_{page}"):
            st.experimental_set_query_params(page=page)
            st.experimental_rerun()
    if st.button("Logout", key="logout_btn_bottom"):
        st.session_state.clear()
        st.experimental_rerun()

# ─── FORM DATI UTENTE ───────────────────────────────────────────────────────
# ... resto del form e salvataggio ...

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
