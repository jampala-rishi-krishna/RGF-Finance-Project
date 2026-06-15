import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
except ImportError:
    pass

def _secret(key: str, default: str = "") -> str:
    """Read from st.secrets (Streamlit Cloud) then fall back to os.getenv (local)."""
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

SUPABASE_URL         = _secret("SUPABASE_URL")
SUPABASE_KEY         = _secret("SUPABASE_KEY")
SERPAPI_KEY          = _secret("SERPAPI_KEY")
ADMIN_PASSWORD       = _secret("ADMIN_PASSWORD")
MANAGER_PASSWORD     = _secret("MANAGER_PASSWORD")
ADMIN_EMAIL_PASSWORD = _secret("ADMIN_EMAIL_PASSWORD")
RISHI_EMAIL_PASSWORD = _secret("RISHI_EMAIL_PASSWORD")
