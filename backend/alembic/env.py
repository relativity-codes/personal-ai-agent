from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection

from app.config import settings
from app.db.models.base import Base

import app.db.models  # noqa: F401 — register models on Base.metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    # Use psycopg3 driver for CockroachDB migrations (works with CockroachDB and SQLAlchemy)
    url = settings.DATABASE_URL
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "+psycopg")
        # Use psycopg2 driver for CockroachDB migrations (recommended by CockroachDB)
        if "+asyncpg" in url:
            url = url.replace("+asyncpg", "+psycopg2")
        elif "+psycopg" in url:
            url = url.replace("+psycopg", "+psycopg2")
        return url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    # --- CockroachDB version string workaround ---
    import sqlalchemy.dialects.postgresql.psycopg2 as pg_psycopg2
    import re
    def cockroach_version_workaround(self, connection):
        version = connection.exec_driver_sql("select version()", ()).scalar()
        match = re.search(r"v(\d+)(?:\.(\d+))?(?:\.(\d+))?", version)
        if match:
            return tuple(int(x) if x is not None else 0 for x in match.groups())
        return (0, 0, 0)
    pg_psycopg2.PGDialect_psycopg2._get_server_version_info = cockroach_version_workaround
        # --- end workaround ---

    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
