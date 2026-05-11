from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path

from env import load_runtime_env
from paths import CONFIG_DIR, DATA_DIR, REPO_ROOT
from process import run


def backup(*, system: bool = False, destination: Path | None = None) -> int:
    env_values = load_runtime_env(system=system)
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = destination or DATA_DIR / "backups" / timestamp
    backup_root.mkdir(parents=True, exist_ok=True)

    database_url = env_values.get("DATABASE_URL", "postgresql://taskflow:taskflow@localhost:5432/taskflow")
    run(["pg_dump", database_url, "-f", backup_root / "taskflow.sql"])

    env_dir = CONFIG_DIR if system else REPO_ROOT
    if env_dir.exists():
        target = backup_root / ("etc-taskflow" if system else "env")
        if target.exists():
            shutil.rmtree(target)
        if system:
            shutil.copytree(env_dir, target)
        else:
            target.mkdir(parents=True, exist_ok=True)
            for path in [REPO_ROOT / ".env", REPO_ROOT / "apps" / "api" / ".env"]:
                if path.exists():
                    shutil.copy2(path, target / path.name)

    for name in ["minio", "uploads"]:
        source = DATA_DIR / name
        if source.exists():
            target = backup_root / name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)

    (backup_root / "version.txt").write_text("taskflow-native-backup\n", encoding="utf-8")
    print(f"backup created: {backup_root}")
    return 0


def restore(source: Path, *, system: bool = False) -> int:
    env_values = load_runtime_env(system=system)
    database_url = env_values.get("DATABASE_URL", "postgresql://taskflow:taskflow@localhost:5432/taskflow")
    sql = source / "taskflow.sql"
    if sql.exists():
        run(["psql", database_url, "-f", sql])

    for name in ["minio", "uploads"]:
        backup_path = source / name
        target = DATA_DIR / name
        if backup_path.exists():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(backup_path, target)

    print(f"restored from: {source}")
    return 0
