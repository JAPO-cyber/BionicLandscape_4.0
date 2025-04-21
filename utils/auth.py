# utils/auth.py

def check_login(username, password):
    users = {
        "admin": ("bionic", "bionic"),
        "cittadino": ("responsabile", "responsabile")
    }

    if username in users:
        stored_password, role = users[username]
        if stored_password == password:
            return True, role
    return False, None
