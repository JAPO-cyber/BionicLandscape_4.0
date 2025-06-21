import os
import unicodedata
import logging
import streamlit as st
from lib.style import apply_custom_style
from lib.navigation import render_sidebar_navigation, PAGES_ACCESS
from lib.get_secret import get_secret

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
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("role", None)
st.session_state.setdefault("quartiere", None)

# ─── Navigazione laterale ──────────────────────────────────────────────────
render_sidebar_navigation()

# ─── Header: Titolo e Descrizione ──────────────────────────────────────────
st.markdown(f"# {PAGE_TITLE}")
st.write(PAGE_DESCRIPTION)
st.markdown("---")

# ─── Sezione di Accesso ────────────────────────────────────────────────────
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



