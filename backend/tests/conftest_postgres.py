"""Helpers for optional PostgreSQL-backed integration tests."""

from __future__ import annotations

from app.config import settings


def postgres_tcp_available() -> bool:
    """Return True if Postgres accepts a TCP connection with current settings."""
    try:
        import psycopg2

        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname=settings.POSTGRES_DB,
            connect_timeout=2,
        )
        conn.close()
        return True
    except Exception:
        return False
