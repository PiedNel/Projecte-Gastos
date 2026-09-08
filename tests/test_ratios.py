"""Test bàsic de càlcul de ratios."""
import pandas as pd

from src.ratios import calcular_resum


def test_resum_basic():
    df = pd.DataFrame(
        [
            {"tipus": "ingrés", "import": 3000.0, "categoria": "Nòmina", "qui": "Jo",
             "data": pd.Timestamp("2026-09-01")},
            {"tipus": "despesa", "import": 1000.0, "categoria": "Habitatge", "qui": "Jo",
             "data": pd.Timestamp("2026-09-02")},
            {"tipus": "despesa", "import": 500.0, "categoria": "Alimentació", "qui": "Parella",
             "data": pd.Timestamp("2026-09-03")},
        ]
    )
    r = calcular_resum(df)
    assert r["ingressos"] == 3000.0
    assert r["despeses"] == 1500.0
    assert r["estalvi"] == 1500.0
    assert r["taxa_estalvi"] == 50.0
