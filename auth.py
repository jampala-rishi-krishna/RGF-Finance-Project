import streamlit as st
import hashlib

def _h(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

USERS = {
    "admin@rareglobalfood.com": _h("admin@123"),
}

def check_login(username: str, password: str) -> bool:
    if not username or not password:
        return False
    stored = USERS.get(username.strip().lower())
    return stored == _h(password)

def logout():
    for key in ["authenticated", "username"]:
        st.session_state.pop(key, None)
