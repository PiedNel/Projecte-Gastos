"""Punt d'entrada principal de Despeses de casa."""
import streamlit as st

from src.auth import require_login

st.set_page_config(page_title="Despeses de casa", page_icon="🏠", layout="wide")
require_login()

pg = st.navigation(
    [
        st.Page("src/views/inici.py", title="Inici", icon="🏠"),
        st.Page("pages/2_Afegir.py", title="Afegir", icon="➕"),
        st.Page("pages/3_Resum.py", title="Resum", icon="📊"),
        st.Page("pages/4_Gestionar.py", title="Gestionar", icon="🛠️"),
    ]
)
pg.run()
