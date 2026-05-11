from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request

from env import load_runtime_env
from paths import API_DIR
from process import command_ok, run


def minio_init(*, system: bool = False) -> int:
    env_values = load_runtime_env(system=system)
    env = os.environ.copy()
    env.update(env_values)
    run([sys.executable, "bin/native_create_bucket.py"], cwd=API_DIR, env=env)
    return 0


def check_minio(*, system: bool = False) -> bool:
    env_values = load_runtime_env(system=system)
    endpoint = env_values.get("AWS_S3_ENDPOINT_URL", "http://localhost:9000").rstrip("/")
    try:
        with urllib.request.urlopen(f"{endpoint}/minio/health/live", timeout=5) as response:
            return response.status < 500
    except (urllib.error.URLError, TimeoutError):
        return False


def check_bucket(*, system: bool = False) -> bool:
    env_values = load_runtime_env(system=system)
    env = os.environ.copy()
    env.update(env_values)
    return command_ok([sys.executable, "bin/native_create_bucket.py"], cwd=API_DIR, env=env)
