from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable


def which(name: str) -> str | None:
    return shutil.which(name)


def printable(cmd: Iterable[str | Path]) -> str:
    return " ".join(str(part) for part in cmd)


def run(
    cmd: list[str | Path],
    *,
    cwd: str | Path | None = None,
    check: bool = True,
    capture: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    print("+", printable(cmd), flush=True)
    return subprocess.run(
        [str(part) for part in cmd],
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        capture_output=capture,
        env=merged_env,
    )


def command_ok(cmd: list[str | Path], *, cwd: str | Path | None = None, env: dict[str, str] | None = None) -> bool:
    try:
        run(cmd, cwd=cwd, env=env, capture=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
