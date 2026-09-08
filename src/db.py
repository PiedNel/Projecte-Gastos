"""Model de dades per despeses-casa: SQLite local o Postgres (Supabase) al Cloud."""
from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "despeses.db"

CATEGORIES_DESPESA = [
    "Habitatge",
    "Subministraments",
    "Alimentació",
    "Transport",
    "Salut",
    "Oci",
    "Nens",
    "Estalvi/Inversió",
    "Altres",
]
CATEGORIES_INGRES = ["Nòmina", "Parking", "Lloguers", "Repasos", "Altres"]
METODES = ["Compte corrent", "Targeta", "Efectiu", "Bizum", "Altres"]
USUARIS = ["Eloi", "Ariana"]


def _pg_dsn() -> str | None:
    """DSN de Postgres si està configurat (Secrets Cloud o variable d'entorn)."""
    dsn = os.environ.get("SUPABASE_DB_URL", "").strip()
    if dsn:
        return dsn
    try:
        import streamlit as st

        dsn = str(st.secrets.get("SUPABASE_DB_URL", "")).strip()
        return dsn or None
    except Exception:
        return None


def _use_pg(db_path: Path = DB_PATH) -> bool:
    # Els tests passen db_path temporal -> forcem SQLite encara que hi hagi env.
    if str(db_path) != str(DB_PATH):
        return False
    return bool(_pg_dsn())


def _init_pg(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS moviments (
            id SERIAL PRIMARY KEY,
            data TEXT NOT NULL,
            tipus TEXT NOT NULL CHECK (tipus IN ('ingrés','despesa')),
            import REAL NOT NULL CHECK (import > 0),
            categoria TEXT NOT NULL,
            subcategoria TEXT DEFAULT '',
            qui TEXT NOT NULL,
            descripcio TEXT DEFAULT '',
            metode TEXT DEFAULT '',
            creat TEXT NOT NULL,
            UNIQUE (data, tipus, import, categoria, qui, descripcio)
        )
        """
    )
    conn.commit()


def _get_pg_conn():
    import psycopg2

    return psycopg2.connect(_pg_dsn())


def get_conn(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    if _use_pg(db_path):
        with _get_pg_conn() as conn:
            _init_pg(conn)
        return
    with get_conn(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS moviments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                tipus TEXT NOT NULL CHECK (tipus IN ('ingrés','despesa')),
                import REAL NOT NULL CHECK (import > 0),
                categoria TEXT NOT NULL,
                subcategoria TEXT DEFAULT '',
                qui TEXT NOT NULL,
                descripcio TEXT DEFAULT '',
                metode TEXT DEFAULT '',
                creat TEXT NOT NULL,
                UNIQUE (data, tipus, import, categoria, qui, descripcio)
            )
            """
        )
        conn.commit()


def validar_moviment(data_mov: date, tipus: str, import_mov: float) -> None:
    if import_mov <= 0:
        raise ValueError("L'import ha de ser > 0.")
    if tipus not in ("ingrés", "despesa"):
        raise ValueError("Tipus invàlid.")
    if data_mov > date.today() + timedelta(days=7):
        raise ValueError("La data no pot ser més de 7 dies en el futur.")


def add_moviment(
    data_mov: date,
    tipus: str,
    import_mov: float,
    categoria: str,
    qui: str,
    subcategoria: str = "",
    descripcio: str = "",
    metode: str = "",
    db_path: Path = DB_PATH,
) -> int:
    validar_moviment(data_mov, tipus, import_mov)
    if isinstance(data_mov, (datetime, date)):
        data_str = data_mov.isoformat()
    else:
        data_str = str(data_mov)
    if _use_pg(db_path):
        import psycopg2.errors

        with _get_pg_conn() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO moviments
                           (data, tipus, import, categoria, subcategoria, qui, descripcio, metode, creat)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                        (data_str, tipus, float(import_mov), categoria, subcategoria,
                         qui, descripcio, metode,
                         datetime.now().isoformat(timespec="seconds")),
                    )
                    new_id = int(cur.fetchone()[0])
                conn.commit()
                return new_id
            except psycopg2.errors.UniqueViolation as exc:
                conn.rollback()
                raise ValueError("Moviment duplicat (mateixa data, tipus, import, categoria, persona i descripció).") from exc
    with get_conn(db_path) as conn:
        try:
            cur = conn.execute(
                """INSERT INTO moviments
                   (data, tipus, import, categoria, subcategoria, qui, descripcio, metode, creat)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    data_str,
                    tipus,
                    float(import_mov),
                    categoria,
                    subcategoria,
                    qui,
                    descripcio,
                    metode,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)
        except sqlite3.IntegrityError as exc:
            raise ValueError("Moviment duplicat (mateixa data, tipus, import, categoria, persona i descripció).") from exc


def get_moviments(db_path: Path = DB_PATH) -> pd.DataFrame:
    init_db(db_path)
    if _use_pg(db_path):
        with _get_pg_conn() as conn:
            df = pd.read_sql_query("SELECT * FROM moviments ORDER BY data DESC, id DESC", conn)
        if not df.empty:
            df["data"] = pd.to_datetime(df["data"])
        return df
    with get_conn(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM moviments ORDER BY data DESC, id DESC", conn)
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
    return df


def delete_moviment(mov_id: int, db_path: Path = DB_PATH) -> None:
    if _use_pg(db_path):
        with _get_pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM moviments WHERE id = %s", (mov_id,))
                n = cur.rowcount
            conn.commit()
            if n == 0:
                raise ValueError(f"No existeix cap moviment amb id {mov_id}.")
        return
    with get_conn(db_path) as conn:
        cur = conn.execute("DELETE FROM moviments WHERE id = ?", (mov_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"No existeix cap moviment amb id {mov_id}.")


def update_moviment(
    mov_id: int,
    data_mov: date,
    tipus: str,
    import_mov: float,
    categoria: str,
    qui: str,
    subcategoria: str = "",
    descripcio: str = "",
    metode: str = "",
    db_path: Path = DB_PATH,
) -> None:
    validar_moviment(data_mov, tipus, import_mov)
    data_str = data_mov.isoformat() if isinstance(data_mov, (datetime, date)) else str(data_mov)
    if _use_pg(db_path):
        import psycopg2.errors

        with _get_pg_conn() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """UPDATE moviments SET data=%s, tipus=%s, import=%s, categoria=%s,
                           subcategoria=%s, qui=%s, descripcio=%s, metode=%s WHERE id=%s""",
                        (data_str, tipus, float(import_mov), categoria, subcategoria,
                         qui, descripcio, metode, mov_id),
                    )
                    n = cur.rowcount
                conn.commit()
            except psycopg2.errors.UniqueViolation as exc:
                conn.rollback()
                raise ValueError("La modificació crea un duplicat d'un altre moviment.") from exc
            if n == 0:
                raise ValueError(f"No existeix cap moviment amb id {mov_id}.")
        return
    with get_conn(db_path) as conn:
        try:
            cur = conn.execute(
                """UPDATE moviments SET data=?, tipus=?, import=?, categoria=?,
                   subcategoria=?, qui=?, descripcio=?, metode=? WHERE id=?""",
                (data_str, tipus, float(import_mov), categoria, subcategoria,
                 qui, descripcio, metode, mov_id),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("La modificació crea un duplicat d'un altre moviment.") from exc
        if cur.rowcount == 0:
            raise ValueError(f"No existeix cap moviment amb id {mov_id}.")
