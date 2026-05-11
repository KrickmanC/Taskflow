#!/usr/bin/env python3
import os
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


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.check_call(cmd)


def main() -> None:
    load_env_file(os.environ.get("TASKFLOW_ENV_FILE"))
    load_env_file(Path.cwd() / ".env")
    load_env_file(Path.cwd() / ".env.native")
    settings_args = sys.argv[1:] or ["--settings=taskflow.settings.local"]

    run([sys.executable, "manage.py", "wait_for_db", *settings_args])
    run([sys.executable, "manage.py", "migrate", *settings_args])


if __name__ == "__main__":
    main()
