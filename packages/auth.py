import bcrypt
import streamlit as st
from packages.database import get_user, add_user

def hash_password(password):
    """Hashe un mot de passe avec bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Vérifie un mot de passe."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login_user(username, password):
    """Authentifie un utilisateur."""
    user = get_user(username)
    if user:
        # user = (id, username, password_hash, role)
        if check_password(password, user[2]):
            st.session_state.user = {
                "id": user[0],
                "username": user[1],
                "role": user[3]
            }
            return True
    return False

def register_user(username, password, role):
    """Enregistre un nouvel utilisateur."""
    hashed = hash_password(password)
    return add_user(username, hashed, role)

def logout_user():
    """Déconnecte l'utilisateur."""
    if "user" in st.session_state:
        del st.session_state.user
    st.rerun()
