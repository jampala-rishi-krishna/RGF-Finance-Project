import streamlit as st
import hashlib
from config import (ADMIN_PASSWORD, MANAGER_PASSWORD,
                    ADMIN_EMAIL_PASSWORD, RISHI_EMAIL_PASSWORD)

def _h(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

USERS = {
    "admin":                    _h(ADMIN_PASSWORD),
    "manager":                  _h(MANAGER_PASSWORD),
    "admin@rareglobalfood.com": _h(ADMIN_EMAIL_PASSWORD),
    "rishi@rareglobalfood.com": _h(RISHI_EMAIL_PASSWORD),
}

def check_login(username: str, password: str) -> bool:
    if not username or not password:
        return False
    stored = USERS.get(username.strip().lower())
    return stored == _h(password)

def logout():
    for key in ["authenticated", "username"]:
        st.session_state.pop(key, None)
