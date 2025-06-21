import streamlit as st

# ─── Mappatura pagine accesso globale ──────────────────────────────────────
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}

# Label e icona per ogni pagina (personalizzabili)
PAGE_METADATA = {
    '1_Registrazione':     {'label': 'Registrazione',      'icon': '🏠'},
    '2_Amministrazione':    {'label': 'Amministrazione',   'icon': '🛠️'},
    '3_Admin':             {'label': 'Admin',              'icon': '⚙️'},
}


def render_sidebar_navigation():
    """
    Renderizza la sidebar di navigazione sulla base del ruolo utente.
    Usa i parametri di query 'page' per tenere traccia della pagina attiva.
    """
    role = st.session_state.get('role')
    if not role:
        return  # Non mostrare sidebar se non loggato

    # Intestazione e info utente
    st.sidebar.markdown(f"### 📂 Sezioni disponibili")
    st.sidebar.markdown(f"**Ruolo:** {role}")
    quartiere = st.session_state.get('quartiere')
    if quartiere:
        st.sidebar.markdown(f"**Quartiere:** {quartiere}")
    st.sidebar.markdown("---")

    # Lista delle pagine per il ruolo
    pages = PAGES_ACCESS.get(role, [])
    if not pages:
        st.sidebar.info("Nessuna sezione disponibile.")
        return

    # Pagina corrente da query params
    params = st.experimental_get_query_params()
    current_page = params.get('page', [pages[0]])[0]

    # Render bottoni per ogni pagina
    for page in pages:
        meta = PAGE_METADATA.get(page, {})
        label = meta.get('label', page)
        icon = meta.get('icon', '')
        is_selected = (page == current_page)
        btn_label = f"{icon} {label}" if icon else label
        # Evidenzia la pagina selezionata con il param 'selected'
        if st.sidebar.button(btn_label, key=page, disabled=is_selected):
            # Imposta nuovo param e ricarica
            st.experimental_set_query_params(page=page)
            st.experimental_rerun()

    # Logout (opzionale)
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        # resetta lo state utile e torna alla home
        for k in ['logged_in','role','quartiere']:
            st.session_state.pop(k, None)
        st.experimental_set_query_params()
        st.experimental_rerun()

