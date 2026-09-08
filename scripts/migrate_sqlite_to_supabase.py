"""Puja els moviments de data/despeses.db (SQLite) a Supabase (Postgres).

Ús:
    $env:SUPABASE_DB_URL="postgresql://..."
    python scripts/migrate_sqlite_to_supabase.py
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db import DB_PATH  # noqa: E402


def main() -> None:
    dsn = os.environ.get("SUPABASE_DB_URL", "").strip()
    if not dsn:
        raise SystemExit("Cal definir SUPABASE_DB_URL.")
    import psycopg2
    import psycopg2.errors

    if not DB_PATH.exists():
        raise SystemExit(f"No existeix {DB_PATH}.")

    con_lite = sqlite3.connect(DB_PATH)
    con_lite.row_factory = sqlite3.Row
    files = con_lite.execute("SELECT * FROM moviments ORDER BY id").fetchall()
    print(f"Files locals: {len(files)}")

    conn = psycopg2.connect(dsn)
    with conn:
        with conn.cursor() as cur:
            cur.execute(
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
    pujats = duplicats = 0
    with psycopg2.connect(dsn) as conn:
        for f in files:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO moviments
                           (data, tipus, import, categoria, subcategoria, qui, descripcio, metode, creat)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (f["data"], f["tipus"], f["import"], f["categoria"],
                         f["subcategoria"], f["qui"], f["descripcio"], f["metode"], f["creat"]),
                    )
                conn.commit()
                pujats += 1
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                duplicats += 1
    print(f"Pujats: {pujats} · Duplicats omesos: {duplicats}")


if __name__ == "__main__":
    main()
