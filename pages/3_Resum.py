"""Pàgina de resum mensual + descàrrega Excel."""
import streamlit as st

from src.auth import require_login
from src.db import get_moviments
from src.excel_export import generar_excel
from src.ratios import calcular_resum, filtrar_mes

st.set_page_config(page_title="Resum mensual", page_icon="📊")
require_login()
st.title("📊 Resum mensual i Excel")

df = get_moviments()
if df.empty:
    st.info("No hi ha dades per generar el resum.")
    st.stop()

mesos = sorted(df["data"].dt.strftime("%Y-%m").unique(), reverse=True)
mes = st.selectbox("Mes", mesos, index=0)
dff = filtrar_mes(df, mes)
resum = calcular_resum(dff)

st.write(f"**Ingressos:** {resum['ingressos']:.2f} € · **Despeses:** {resum['despeses']:.2f} € · "
         f"**Estalvi:** {resum['estalvi']:.2f} € · **Taxa:** {resum['taxa_estalvi']:.1f}%")
st.dataframe(dff, use_container_width=True, hide_index=True)

buf = generar_excel(dff, resum, mes)
st.download_button(
    "⬇️ Descarrega Excel del mes",
    data=buf,
    file_name=f"resum_mensual_{mes}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
