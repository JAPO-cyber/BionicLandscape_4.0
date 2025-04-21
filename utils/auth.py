import streamlit as st

# Esempio semplice con un utente hardcoded (per test locali)
def check_login(username, password):
    return username == "admin" and password == "bionic"
