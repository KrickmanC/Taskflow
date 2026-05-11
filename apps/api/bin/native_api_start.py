#!/usr/bin/env python3
import hashlib
import os
import platform
import shlex
import socket
import subprocess
import sys
import uuid
from pathlib import Path


def load_env_file(path: str | Path | None) -> None:
    if not path:
        return

    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        try:
            token = shlex.split(line, comments=True, posix=True)[0]
        except (IndexError, ValueError):
            continue

        key, value = token.split("=", 1)
        os.environ.setdefault(key, value)


def load_native_env() -> None:
    candidates = [
        os.environ.get("TASKFLOW_ENV_FILE"),
        Path.cwd() / ".env",
        Path.cwd() / ".env.native",
    ]
    for candidate in candidates:
        load_env_file(candidate)


def machine_signature() -> str:
    raw = "|".join(
        [
            socket.gethostname(),
            platform.platform(),
            platform.machine(),
            platform.processor(),
            str(uuid.getnode()),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.check_call(cmd)


def manage(*args: str) -> None:
    run([sys.executable, "manage.py", *args])


def main() -> None:
    load_native_env()
    os.environ.setdefault("MACHINE_SIGNATURE", machine_signature())

    manage("wait_for_db")
    manage("wait_for_migrations")
    manage("register_instance", os.environ["MACHINE_SIGNATURE"])
    manage("configure_instance")
    manage("create_bucket")
    manage("clear_cache")

    run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "taskflow.asgi:application",
            "--host",
            os.environ.get("TASKFLOW_API_HOST", "127.0.0.1"),
            "--port",
            os.environ.get("TASKFLOW_API_PORT", os.environ.get("PORT", "8000")),
        ]
    )


if __name__ == "__main__":
    main()
