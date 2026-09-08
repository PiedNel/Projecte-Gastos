"""Tests de login i detecció de backend."""
import os

from src.auth import check_password


def test_sense_password_acces_lliure(monkeypatch):
    monkeypatch.delenv("APP_PASSWORD", raising=False)
    assert check_password("qualsevol") is True


def test_amb_password(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD", "secret123")
    assert check_password("secret123") is True
    assert check_password("dolent") is False


def test_sqlite_per_defecte_i_amb_tmp(tmp_path, monkeypatch):
    from src import db

    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    assert db._use_pg() is False
    # db_path temporal mai usa Postgres encara que hi hagi env
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://x")
    assert db._use_pg(tmp_path / "altra.db") is False
