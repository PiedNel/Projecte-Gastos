# Despeses de casa 🏠

App local (Python + Streamlit) per gestionar ingressos i despeses de la llar.

## Instal·lar i executar

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Obre `http://localhost:8501` al navegador (o al mòbil si estàs a la mateixa xarxa).

## Ús

1. **Afegir**: introdueix cada ingrés/despesa amb data, categoria i qui l'ha pagat.
2. **Inici**: dashboard amb totals, taxa d'estalvi i gràfics per categoria.
3. **Resum**: filtra per mes i descarrega `resum_mensual_YYYY-MM.xlsx`.

La base de dades és `data/despeses.db` (SQLite). L'Excel és només l'informe generat.

## Desplegament mòbil (parella)

Drive no executa apps web. Per usar-ho des del mòbil cal desplegar gratis a
Streamlit Community Cloud amb aquest mateix codi.
