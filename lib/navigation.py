import streamlit as st

# ─── Mappatura pagine accesso globale ──────────────────────────────────────
PAGES_ACCESS = {
    'utente': ['1_Registrazione'],
    'amministrazione': ['2_Amministrazione'],
    'ADMIN': ['1_Registrazione', '2_Amministrazione', '3_Admin'],
}

def render_sidebar_navigation():
    """
    Renderizza in sidebar:
      - Ruolo e quartiere correnti
      - Pulsanti verdi per navigare tra le pagine di PAGES_ACCESS[role]
      - Logout
    """
    role = st.session_state.get('role', '—')
    quartiere = st.session_state.get('quartiere', '—')

    with st.sidebar:
        st.markdown(f"**Ruolo:** {role}")
        st.markdown(f"**Quartiere:** {quartiere}")
        st.markdown("### Sezioni disponibili")

        for page in PAGES_ACCESS.get(role, []):
            if st.button(page, key=f"nav_{page}"):
                st.query_params = {"page": page}
                st.rerun()

        if st.button("Logout", key="logout_btn"):
            st.session_state.clear()
            st.rerun()
