"""Càlcul de resums i ratios."""
from __future__ import annotations

import pandas as pd


def filtrar_mes(df: pd.DataFrame, any_mes: str) -> pd.DataFrame:
    """any_mes format 'YYYY-MM'."""
    if df.empty:
        return df
    return df[df["data"].dt.strftime("%Y-%m") == any_mes].copy()


def calcular_resum(df: pd.DataFrame) -> dict:
    """Retorna totals i ratios del període filtrat."""
    if df.empty:
        return {
            "ingressos": 0.0,
            "despeses": 0.0,
            "estalvi": 0.0,
            "taxa_estalvi": 0.0,
            "per_categoria": pd.DataFrame(),
            "per_persona": pd.DataFrame(),
        }
    ingressos = float(df.loc[df["tipus"] == "ingrés", "import"].sum())
    despeses = float(df.loc[df["tipus"] == "despesa", "import"].sum())
    estalvi = ingressos - despeses
    taxa = (estalvi / ingressos * 100) if ingressos > 0 else 0.0

    despeses_df = df[df["tipus"] == "despesa"]
    if not despeses_df.empty:
        per_cat = (
            despeses_df.groupby("categoria")["import"]
            .sum()
            .reset_index()
            .rename(columns={"import": "total"})
        )
        per_cat["pes_pct"] = (per_cat["total"] / despeses * 100).round(1) if despeses else 0.0
        per_cat = per_cat.sort_values("total", ascending=False)
    else:
        per_cat = pd.DataFrame(columns=["categoria", "total", "pes_pct"])

    per_persona = (
        df.groupby(["qui", "tipus"])["import"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    return {
        "ingressos": round(ingressos, 2),
        "despeses": round(despeses, 2),
        "estalvi": round(estalvi, 2),
        "taxa_estalvi": round(taxa, 1),
        "per_categoria": per_cat,
        "per_persona": per_persona,
    }


def comparativa_mes_anterior(df: pd.DataFrame, any_mes: str) -> dict:
    """% variació de despesa vs mes anterior."""
    if df.empty:
        return {"variacio_pct": 0.0}
    actual = filtrar_mes(df, any_mes)
    try:
        prev_periode = (pd.Period(any_mes, freq="M") - 1).strftime("%Y-%m")
    except Exception:
        return {"variacio_pct": 0.0}
    anterior = filtrar_mes(df, prev_periode)
    desp_actual = float(actual.loc[actual["tipus"] == "despesa", "import"].sum())
    desp_ant = float(anterior.loc[anterior["tipus"] == "despesa", "import"].sum())
    if desp_ant == 0:
        return {"variacio_pct": 0.0}
    return {"variacio_pct": round((desp_actual - desp_ant) / desp_ant * 100, 1)}
