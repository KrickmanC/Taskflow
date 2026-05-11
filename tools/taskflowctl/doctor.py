from __future__ import annotations

import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path

from db import check_db
from env import load_runtime_env
from minio import check_minio
from paths import API_DIR, PORTS, REPO_ROOT, TASKFLOW_SERVICES
from process import command_ok, which
from rabbitmq import check_rabbitmq
from redis import check_redis


def _print(name: str, ok: bool, detail: str = "") -> bool:
    suffix = f" - {detail}" if detail else ""
    print(f"[{'OK' if ok else 'FAIL'}] {name}{suffix}")
    return ok


def _version(cmd: list[str]) -> str:
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    except FileNotFoundError:
        return "not found"
    return (proc.stdout or proc.stderr).strip().splitlines()[0] if (proc.stdout or proc.stderr).strip() else "unknown"


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _check_build_dirs() -> bool:
    candidates = [
        REPO_ROOT / "apps" / "web" / "build",
        REPO_ROOT / "apps" / "admin" / "build",
        REPO_ROOT / "apps" / "space" / "build",
        REPO_ROOT / "apps" / "live" / "dist",
    ]
    return all(path.exists() for path in candidates)


def _ram_bytes() -> int | None:
    if platform.system().lower() == "linux":
        try:
            pages = int(subprocess.check_output(["getconf", "_PHYS_PAGES"], text=True).strip())
            page_size = int(subprocess.check_output(["getconf", "PAGE_SIZE"], text=True).strip())
            return pages * page_size
        except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
            return None
    return None


def doctor(*, system: bool = False, soft: bool = False) -> int:
    failures = 0
    env_values = load_runtime_env(system=system)

    checks = [
        ("OS", platform.system().lower() in {"linux", "windows"}, platform.platform()),
        ("CPU arch", platform.machine().lower() in {"x86_64", "amd64"}, platform.machine()),
        ("Python", which("python") is not None or which("python3") is not None, _version([sys.executable, "--version"])),
        ("Node.js", which("node") is not None, _version(["node", "--version"])),
        ("pnpm", which("pnpm") is not None, _version(["pnpm", "--version"])),
        ("Git", which("git") is not None, _version(["git", "--version"])),
        ("psql", which("psql") is not None, _version(["psql", "--version"])),
        ("redis-cli", which("redis-cli") is not None, _version(["redis-cli", "--version"])),
        ("rabbitmqctl", which("rabbitmqctl") is not None or which("rabbitmqctl.bat") is not None, "available" if which("rabbitmqctl") or which("rabbitmqctl.bat") else "not found"),
        ("Env files", bool(env_values.get("DATABASE_URL") and env_values.get("SECRET_KEY")), "loaded" if env_values else "missing"),
    ]

    for name, ok, detail in checks:
        failures += 0 if _print(name, ok, detail) else 1

    ram = _ram_bytes()
    if ram is not None:
        _print("RAM", ram >= 12 * 1024 * 1024 * 1024, f"{ram // (1024 ** 3)} GB")

    disk = shutil.disk_usage(REPO_ROOT)
    _print("Disk free", disk.free >= 10 * 1024 * 1024 * 1024, f"{disk.free // (1024 ** 3)} GB")

    for port, label in PORTS.items():
        _print(f"Port {port}", True, f"{label}: {'open' if _port_open(port) else 'closed'}")

    service_checks = [
        ("PostgreSQL", check_db(system=system), "connectable"),
        ("Redis", check_redis(system=system), "PING"),
        ("RabbitMQ", check_rabbitmq(system=system), "status/vhost"),
        ("MinIO", check_minio(system=system), "health endpoint"),
        ("Frontend build", _check_build_dirs(), "build directories"),
    ]

    for name, ok, detail in service_checks:
        failures += 0 if _print(name, ok, detail) else 1

    if command_ok([sys.executable, "manage.py", "check"], cwd=API_DIR, env=env_values):
        _print("Django check", True)
    else:
        failures += 1
        _print("Django check", False)

    if command_ok([sys.executable, "manage.py", "showmigrations", "--plan"], cwd=API_DIR, env=env_values):
        _print("Migrations", True, "showmigrations passed")
    else:
        failures += 1
        _print("Migrations", False, "showmigrations failed")

    for service in TASKFLOW_SERVICES:
        ok = command_ok(["systemctl", "is-active", "--quiet", service]) if platform.system().lower() == "linux" else command_ok(["sc.exe", "query", service])
        failures += 0 if _print(f"Service {service}", ok, "registered/running") else 1

    if failures and not soft:
        print(f"doctor failed: {failures} check(s) failed")
        return 1

    print("doctor completed")
    return 0
