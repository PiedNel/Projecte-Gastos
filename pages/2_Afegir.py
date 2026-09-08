"""Pàgina per afegir ingressos i despeses."""
from datetime import date

import streamlit as st

from src.auth import require_login
from src.db import (
    CATEGORIES_DESPESA,
    CATEGORIES_INGRES,
    METODES,
    USUARIS,
    add_moviment,
)

st.set_page_config(page_title="Afegir moviment", page_icon="➕")
require_login()
st.title("➕ Afegir moviment")

# El tipus va FORA del formulari perquè el desplegable de categoria
# s'actualitzi a l'instant en canviar entre despesa/ingrés.
tipus = st.radio("Tipus", ["despesa", "ingrés"], horizontal=True)
cats = CATEGORIES_DESPESA if tipus == "despesa" else CATEGORIES_INGRES

with st.form("form_moviment", clear_on_submit=True):
    data_mov = st.date_input("Data", value=date.today(), max_value=date.today())
    import_mov = st.number_input("Import (€)", min_value=0.01, step=1.0, format="%.2f")
    categoria = st.selectbox("Categoria", cats)
    subcategoria = st.text_input("Subcategoria (opcional)")
    qui = st.selectbox("Qui", USUARIS)
    descripcio = st.text_input("Descripció")
    metode = st.selectbox("Mètode de pagament", METODES)
    enviat = st.form_submit_button("Desar", use_container_width=True)

if enviat:
    try:
        nou_id = add_moviment(
            data_mov=data_mov,
            tipus=tipus,
            import_mov=float(import_mov),
            categoria=categoria,
            qui=qui,
            subcategoria=subcategoria.strip(),
            descripcio=descripcio.strip(),
            metode=metode,
        )
        st.success(f"Moviment #{nou_id} desat correctament.")
    except ValueError as exc:
        st.error(str(exc))
