"""Despeses de casa — Inici (dashboard)."""
import streamlit as st
import plotly.express as px

from src.db import get_moviments
from src.ratios import calcular_resum, comparativa_mes_anterior, filtrar_mes

st.set_page_config(page_title="Despeses de casa", page_icon="🏠", layout="wide")
st.title("🏠 Despeses de casa")

df = get_moviments()
if df.empty:
    st.info("Encara no hi ha moviments. Ves a la pàgina **Afegir** per introduir el primer.")
    st.stop()

mesos = sorted(df["data"].dt.strftime("%Y-%m").unique(), reverse=True)
col1, col2, col3 = st.columns(3)
with col1:
    mes = st.selectbox("Mes", mesos, index=0)
with col2:
    usuaris = ["Tots"] + sorted(df["qui"].dropna().unique().tolist())
    qui = st.selectbox("Persona", usuaris, index=0)
with col3:
    cats = ["Totes"] + sorted(df["categoria"].dropna().unique().tolist())
    cat = st.selectbox("Categoria", cats, index=0)

dff = filtrar_mes(df, mes)
if qui != "Tots":
    dff = dff[dff["qui"] == qui]
if cat != "Totes":
    dff = dff[dff["categoria"] == cat]

resum = calcular_resum(dff)
comp = comparativa_mes_anterior(df, mes)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Ingressos", f"{resum['ingressos']:.2f} €")
m2.metric("Despeses", f"{resum['despeses']:.2f} €", f"{comp['variacio_pct']:+.1f}% vs mes anterior")
m3.metric("Estalvi net", f"{resum['estalvi']:.2f} €")
m4.metric("Taxa d'estalvi", f"{resum['taxa_estalvi']:.1f}%")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Despesa per categoria")
    if not resum["per_categoria"].empty:
        fig = px.pie(resum["per_categoria"], names="categoria", values="total")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(resum["per_categoria"], use_container_width=True, hide_index=True)
    else:
        st.write("Sense despeses aquest període.")
with c2:
    st.subheader("Per persona")
    st.dataframe(resum["per_persona"], use_container_width=True, hide_index=True)

st.subheader("Evolució mensual (12 mesos)")
mensual = (
    df.assign(mes=df["data"].dt.strftime("%Y-%m"))
    .groupby(["mes", "tipus"])["import"]
    .sum()
    .unstack(fill_value=0)
    .reset_index()
    .sort_values("mes")
    .tail(12)
)
st.bar_chart(mensual.set_index("mes"))

st.subheader("Últims moviments")
st.dataframe(dff.head(50), use_container_width=True, hide_index=True)
