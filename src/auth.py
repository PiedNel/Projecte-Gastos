"""Login simple compartit (Eloi/Ariana) via Secrets."""
from __future__ import annotations

import hmac
import os


def _expected_password() -> str:
    try:
        import streamlit as st

        pwd = str(st.secrets.get("APP_PASSWORD", "") or "").strip()
        if pwd:
            return pwd
    except Exception:
        pass
    return os.environ.get("APP_PASSWORD", "").strip()


def check_password(candidat: str) -> bool:
    esperat = _expected_password()
    if not esperat:
        return True  # sense password configurat (local) -> accés lliure
    return hmac.compare_digest(candidat.strip(), esperat)


def require_login() -> None:
    """Bloqueja la pàgina fins que s'introdueix el password (si n'hi ha)."""
    import streamlit as st

    if not _expected_password():
        return
    if st.session_state.get("auth_ok"):
        return
    st.title("🔒 Despeses de casa")
    st.text_input("Password", type="password", key="auth_pwd")
    if st.button("Entrar", use_container_width=True):
        if check_password(st.session_state.get("auth_pwd", "")):
            st.session_state["auth_ok"] = True
            st.rerun()
        else:
            st.error("Password incorrecte.")
    st.stop()
