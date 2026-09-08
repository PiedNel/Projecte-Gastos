"""Pàgina per corregir o eliminar moviments erronis."""
from datetime import date

import streamlit as st

from src.db import (
    CATEGORIES_DESPESA,
    CATEGORIES_INGRES,
    METODES,
    USUARIS,
    delete_moviment,
    get_moviments,
    update_moviment,
)

st.set_page_config(page_title="Gestionar moviments", page_icon="🛠️")
st.title("🛠️ Gestionar moviments")

df = get_moviments()
if df.empty:
    st.info("No hi ha moviments per gestionar.")
    st.stop()

st.dataframe(df, use_container_width=True, hide_index=True)

opcions = {
    f"#{int(r['id'])} · {r['data'].strftime('%Y-%m-%d')} · {r['tipus']} · "
    f"{float(r['import']):.2f} € · {r['categoria']} · {r['qui']}": int(r["id"])
    for _, r in df.iterrows()
}
seleccio = st.selectbox("Tria el moviment a corregir", list(opcions.keys()))
mov_id = opcions[seleccio]
fila = df[df["id"] == mov_id].iloc[0]

st.divider()
st.subheader(f"Editar moviment #{mov_id}")

tipus_edit = st.radio(
    "Tipus", ["despesa", "ingrés"], horizontal=True,
    index=["despesa", "ingrés"].index(fila["tipus"]),
    key="edit_tipus",
)
cats_edit = CATEGORIES_DESPESA if tipus_edit == "despesa" else CATEGORIES_INGRES
idx_cat = cats_edit.index(fila["categoria"]) if fila["categoria"] in cats_edit else 0

with st.form("form_editar"):
    data_edit = st.date_input("Data", value=fila["data"].date())
    import_edit = st.number_input("Import (€)", min_value=0.01, value=float(fila["import"]),
                                  step=1.0, format="%.2f")
    categoria_edit = st.selectbox("Categoria", cats_edit, index=idx_cat)
    subcat_edit = st.text_input("Subcategoria", value=str(fila["subcategoria"] or ""))
    idx_qui = USUARIS.index(fila["qui"]) if fila["qui"] in USUARIS else 0
    qui_edit = st.selectbox("Qui", USUARIS, index=idx_qui)
    desc_edit = st.text_input("Descripció", value=str(fila["descripcio"] or ""))
    idx_met = METODES.index(fila["metode"]) if fila["metode"] in METODES else 0
    metode_edit = st.selectbox("Mètode de pagament", METODES, index=idx_met)
    desa = st.form_submit_button("💾 Desar canvis", use_container_width=True)

if desa:
    try:
        update_moviment(
            mov_id,
            data_mov=data_edit,
            tipus=tipus_edit,
            import_mov=float(import_edit),
            categoria=categoria_edit,
            qui=qui_edit,
            subcategoria=subcat_edit.strip(),
            descripcio=desc_edit.strip(),
            metode=metode_edit,
        )
        st.success(f"Moviment #{mov_id} actualitzat. Recarrega la pàgina per veure'l.")
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))

st.divider()
st.subheader("Zona perillosa")
confirma = st.checkbox(f"Confirmo que vull eliminar el moviment #{mov_id}")
if st.button("🗑️ Eliminar definitivament", disabled=not confirma, use_container_width=True):
    try:
        delete_moviment(mov_id)
        st.success(f"Moviment #{mov_id} eliminat.")
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))

if not confirma:
    st.caption("Marca la casella de confirmació per activar l'eliminació.")
