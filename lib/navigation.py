import streamlit as st

# ─── Mappatura pagine accesso globale ──────────────────────────────────────
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}


def render_sidebar_navigation():
    """
    Renderizza la sidebar con navigazione diretta.
    """
    role = st.session_state.get('role', '—')
    quartiere = st.session_state.get('quartiere', '—')

    with st.sidebar:
        st.markdown(f"**Ruolo:** {role}")
        st.markdown(f"**Quartiere:** {quartiere}")
        st.markdown("### Sezioni disponibili")

        for page in PAGES_ACCESS.get(role, []):
            if st.button(page, key=f"nav_{page}"):
                # Passa al modulo corrispondente nella cartella page
                st.switch_page(f"page/{page}.py")

        if st.button("Logout", key="logout_btn"):
            st.session_state.clear()
            st.rerun()
