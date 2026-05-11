from __future__ import annotations

import sys

from backup import backup
from doctor import doctor
from paths import API_DIR, REPO_ROOT, system_env_path
from process import run
from services import service_action


def build() -> int:
    run(["pnpm", "install", "--frozen-lockfile"], cwd=REPO_ROOT)
    run(["pnpm", "build"], cwd=REPO_ROOT)
    return 0


def upgrade(*, system: bool = False) -> int:
    doctor(system=system, soft=True)
    backup(system=system)
    service_action("stop")
    build()
    env = {"TASKFLOW_ENV_FILE": str(system_env_path("api.env"))} if system else None
    args = ["--settings=taskflow.settings.production"] if system else []
    run([sys.executable, "bin/native_migrate.py", *args], cwd=API_DIR, env=env)
    service_action("restart")
    return doctor(system=system)
