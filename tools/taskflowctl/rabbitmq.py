from __future__ import annotations

import platform
import subprocess

from env import load_runtime_env
from process import command_ok, run, which


def rabbitmqctl() -> str | None:
    return which("rabbitmqctl.bat" if platform.system().lower() == "windows" else "rabbitmqctl") or which("rabbitmqctl")


def rabbitmq_init(*, system: bool = False) -> int:
    env_values = load_runtime_env(system=system)
    ctl = rabbitmqctl()
    if not ctl:
        print("rabbitmqctl not found")
        return 1

    user = env_values.get("RABBITMQ_USER", "taskflow")
    password = env_values.get("RABBITMQ_PASSWORD", "taskflow")
    vhost = env_values.get("RABBITMQ_VHOST", "taskflow")

    run([ctl, "add_user", user, password], check=False)
    run([ctl, "add_vhost", vhost], check=False)
    run([ctl, "set_permissions", "-p", vhost, user, ".*", ".*", ".*"])
    return 0


def check_rabbitmq(*, system: bool = False) -> bool:
    env_values = load_runtime_env(system=system)
    ctl = rabbitmqctl()
    if not ctl:
        return False
    if not command_ok([ctl, "status"]):
        return False
    vhost = env_values.get("RABBITMQ_VHOST", "taskflow")
    try:
        proc = subprocess.run([ctl, "list_vhosts"], text=True, capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    return vhost in proc.stdout.split()
