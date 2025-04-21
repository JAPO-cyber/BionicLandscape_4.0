import streamlit as st

def check_login(username, password):
    # Dizionario utenti: username → (password, ruolo)
    users = {
        "admin": ("password1", "bionic"),
        "cittadino": ("password2", "responsabile")
    }

    if username in users and users[username][0] == password:
        return True, users[username][1]  # login OK, ritorna anche il ruolo
    else:
        return False, None

