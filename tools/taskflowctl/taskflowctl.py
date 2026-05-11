#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from backup import backup, restore
from db import db_init
from doctor import doctor
from env import init_env
from minio import minio_init
from paths import API_DIR, system_env_path
from process import run
from rabbitmq import rabbitmq_init
from redis import redis_check
from services import install_deps, service_action, service_install, service_uninstall, status, uninstall
from upgrade import build, upgrade
import logs as logs_module


def migrate(*, system: bool = False) -> int:
    env = {}
    args = []
    if system:
        env["TASKFLOW_ENV_FILE"] = str(system_env_path("api.env"))
        args.append("--settings=taskflow.settings.production")
    run([sys.executable, "bin/native_migrate.py", *args], cwd=API_DIR, env=env)
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    system_requested = "--system" in argv
    argv = [arg for arg in argv if arg != "--system"]

    parser = argparse.ArgumentParser(prog="taskflowctl")
    parser.add_argument("--system", action="store_true", help="Use system install paths such as /etc/taskflow or C:\\ProgramData\\Taskflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor")

    init_parser = subparsers.add_parser("init-env")
    init_parser.add_argument("--force", action="store_true")

    subparsers.add_parser("install-deps")
    subparsers.add_parser("db-init")
    subparsers.add_parser("rabbitmq-init")
    subparsers.add_parser("minio-init")
    subparsers.add_parser("redis-check")
    subparsers.add_parser("migrate")
    subparsers.add_parser("build")
    subparsers.add_parser("service-install")
    subparsers.add_parser("service-uninstall")
    subparsers.add_parser("start")
    subparsers.add_parser("stop")
    subparsers.add_parser("restart")
    subparsers.add_parser("status")

    logs_parser = subparsers.add_parser("logs")
    logs_parser.add_argument("service", nargs="?")
    logs_parser.add_argument("-f", "--follow", action="store_true")

    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("--destination", type=Path)

    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("source", type=Path)

    subparsers.add_parser("upgrade")

    uninstall_parser = subparsers.add_parser("uninstall")
    uninstall_parser.add_argument("--purge", action="store_true")

    args = parser.parse_args(argv)
    args.system = args.system or system_requested

    commands = {
        "doctor": lambda: doctor(system=args.system),
        "init-env": lambda: init_env(system=args.system, force=args.force),
        "install-deps": install_deps,
        "db-init": lambda: db_init(system=args.system),
        "rabbitmq-init": lambda: rabbitmq_init(system=args.system),
        "minio-init": lambda: minio_init(system=args.system),
        "redis-check": lambda: redis_check(system=args.system),
        "migrate": lambda: migrate(system=args.system),
        "build": build,
        "service-install": service_install,
        "service-uninstall": service_uninstall,
        "start": lambda: service_action("start"),
        "stop": lambda: service_action("stop"),
        "restart": lambda: service_action("restart"),
        "status": status,
        "logs": lambda: logs_module.logs(args.service, args.follow),
        "backup": lambda: backup(system=args.system, destination=args.destination),
        "restore": lambda: restore(args.source, system=args.system),
        "upgrade": lambda: upgrade(system=args.system),
        "uninstall": lambda: uninstall(purge=args.purge),
    }

    return commands[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
