from __future__ import annotations

import os
import platform
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
API_DIR = REPO_ROOT / "apps" / "api"

IS_WINDOWS = platform.system().lower() == "windows"
IS_LINUX = platform.system().lower() == "linux"

INSTALL_DIR = Path(os.environ.get("TASKFLOW_INSTALL_DIR", r"C:\Program Files\Taskflow" if IS_WINDOWS else "/opt/taskflow"))
CONFIG_DIR = Path(os.environ.get("TASKFLOW_CONFIG_DIR", r"C:\ProgramData\Taskflow" if IS_WINDOWS else "/etc/taskflow"))
DATA_DIR = Path(os.environ.get("TASKFLOW_DATA_DIR", r"C:\ProgramData\Taskflow" if IS_WINDOWS else "/var/lib/taskflow"))
LOG_DIR = Path(os.environ.get("TASKFLOW_LOG_DIR", r"C:\ProgramData\Taskflow\logs" if IS_WINDOWS else "/var/log/taskflow"))
VENV_DIR = Path(os.environ.get("TASKFLOW_VENV_DIR", str(INSTALL_DIR / "venv")))

LINUX_SERVICE_DIR = Path(os.environ.get("TASKFLOW_SYSTEMD_DIR", "/etc/systemd/system"))

PORTS = {
    5432: "PostgreSQL",
    6379: "Redis",
    5672: "RabbitMQ AMQP",
    15672: "RabbitMQ management",
    9000: "MinIO S3 API",
    9090: "MinIO console",
    8000: "Taskflow API",
    3000: "Taskflow Web",
    3001: "Taskflow Admin",
    3002: "Taskflow Space",
    3100: "Taskflow Live",
}

SERVICE_START_ORDER = [
    "postgresql",
    "redis-server",
    "rabbitmq-server",
    "taskflow-minio",
    "taskflow-api",
    "taskflow-worker",
    "taskflow-beat",
    "taskflow-live",
    "taskflow-web",
    "taskflow-admin",
    "taskflow-space",
]

TASKFLOW_SERVICES = (["taskflow-redis"] if IS_WINDOWS else []) + [
    "taskflow-minio",
    "taskflow-api",
    "taskflow-worker",
    "taskflow-beat",
    "taskflow-live",
    "taskflow-web",
    "taskflow-admin",
    "taskflow-space",
]

SERVICE_STOP_ORDER = [
    "taskflow-space",
    "taskflow-admin",
    "taskflow-web",
    "taskflow-live",
    "taskflow-beat",
    "taskflow-worker",
    "taskflow-api",
    "taskflow-minio",
    "taskflow-redis",
    "rabbitmq-server",
    "redis-server",
    "postgresql",
]

ENV_TARGETS = {
    ".env": REPO_ROOT / ".env.native.example",
    "api.env": API_DIR / ".env.native.example",
    "web.env": REPO_ROOT / "apps" / "web" / ".env.native.example",
    "admin.env": REPO_ROOT / "apps" / "admin" / ".env.native.example",
    "space.env": REPO_ROOT / "apps" / "space" / ".env.native.example",
    "live.env": REPO_ROOT / "apps" / "live" / ".env.native.example",
}


def local_env_path(name: str) -> Path:
    if name == ".env":
        return REPO_ROOT / ".env"
    if name == "api.env":
        return API_DIR / ".env"
    return REPO_ROOT / "apps" / name.removesuffix(".env") / ".env"


def system_env_path(name: str) -> Path:
    return CONFIG_DIR / name
