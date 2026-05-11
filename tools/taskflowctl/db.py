from __future__ import annotations

import os
import re
import subprocess

from env import load_runtime_env
from paths import IS_LINUX
from process import command_ok, printable, which


IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _identifier(value: str) -> str:
    if not IDENTIFIER_RE.match(value):
        raise ValueError(f"Unsafe PostgreSQL identifier: {value}")
    return value


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def db_init(*, system: bool = False) -> int:
    env_values = load_runtime_env(system=system)
    user = _identifier(env_values.get("POSTGRES_USER", "taskflow"))
    password = env_values.get("POSTGRES_PASSWORD", "taskflow")
    database = _identifier(env_values.get("POSTGRES_DB", "taskflow"))

    sql = f"""
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = {_literal(user)}) THEN
      CREATE ROLE {user} LOGIN PASSWORD {_literal(password)};
   END IF;
END
$$;

SELECT 'CREATE DATABASE {database} OWNER {user}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = {_literal(database)})\\gexec
"""

    if IS_LINUX and which("sudo"):
        cmd = ["sudo", "-u", "postgres", "psql", "-v", "ON_ERROR_STOP=1"]
        env = os.environ.copy()
    else:
        cmd = [
            "psql",
            "-U",
            env_values.get("POSTGRES_ADMIN_USER", "postgres"),
            "-h",
            env_values.get("POSTGRES_HOST", "localhost"),
            "-p",
            env_values.get("POSTGRES_PORT", "5432"),
            "-v",
            "ON_ERROR_STOP=1",
        ]
        env = os.environ.copy()
        env.setdefault("PGPASSWORD", env_values.get("POSTGRES_ADMIN_PASSWORD", ""))

    print("+", printable(cmd), flush=True)
    subprocess.run(cmd, input=sql, text=True, check=True, env=env)
    return 0


def check_db(*, system: bool = False) -> bool:
    env_values = load_runtime_env(system=system)
    database_url = env_values.get("DATABASE_URL")
    if not database_url or not which("psql"):
        return False
    return command_ok(["psql", database_url, "-c", "SELECT 1;"])
