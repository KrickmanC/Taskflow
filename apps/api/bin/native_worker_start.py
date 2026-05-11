#!/usr/bin/env python3
import os
import platform
import shlex
import subprocess
import sys
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
    for candidate in [os.environ.get("TASKFLOW_ENV_FILE"), Path.cwd() / ".env", Path.cwd() / ".env.native"]:
        load_env_file(candidate)


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.check_call(cmd)


def manage(*args: str) -> None:
    run([sys.executable, "manage.py", *args])


def main() -> None:
    load_native_env()
    manage("wait_for_db")
    manage("wait_for_migrations")

    cmd = ["celery", "-A", "taskflow", "worker", "-l", "info"]

    if platform.system().lower() == "windows":
        cmd.extend(["--pool", "solo"])

    run(cmd)


if __name__ == "__main__":
    main()
