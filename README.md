# Despeses de casa 🏠

App Streamlit (Eloi/Ariana) per gestionar ingressos i despeses de la llar.
Funciona en local amb SQLite i al mòbil via Streamlit Cloud + Supabase.

## Instal·lar i executar (local)

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Obre `http://localhost:8501`. En local, si no hi ha password configurat, entra directe.

## Ús

1. **Afegir**: introdueix cada ingrés/despesa amb data, categoria i qui l'ha pagat.
2. **Inici**: dashboard amb totals, taxa d'estalvi i gràfics per categoria.
3. **Resum**: filtra per mes i descarrega `resum_mensual_YYYY-MM.xlsx`.

La base de dades és `data/despeses.db` (SQLite) en local i Postgres (Supabase) al Cloud. L'Excel és només l'informe generat.

## Accés mòbil fora de casa (Streamlit Cloud + Supabase, gratis)

1. **Supabase**: crea projecte a supabase.com → Database → copia la `SUPABASE_DB_URL`
   (`postgresql://postgres:CLAU@db.xxxxx.supabase.co:5432/postgres`).
2. **Secrets local**: copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml`
   (mai al git) i omple `APP_PASSWORD` + `SUPABASE_DB_URL`.
3. **Pujar dades**: `python scripts/migrate_sqlite_to_supabase.py` amb `SUPABASE_DB_URL` definit.
4. **GitHub**: `git push` d'aquest repo.
5. **Cloud**: share.streamlit.io → New app → repo `Projecte-Gastos` → `app.py` → Deploy.
6. **Secrets Cloud**: App → Settings → Secrets, enganxa el mateix contingut del `secrets.toml`.
7. **Mòbil**: obre la URL, fes login amb el password i afegeix-la a pantalla d'inici.

## Tests

```powershell
pip install -r requirements.txt
python -m pytest -v
```
