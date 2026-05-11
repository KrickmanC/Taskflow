from __future__ import annotations

import os
import secrets
import shlex
from pathlib import Path

from paths import CONFIG_DIR, ENV_TARGETS, REPO_ROOT, local_env_path, system_env_path


SECRET_KEYS = {
    "SECRET_KEY",
    "LIVE_SERVER_SECRET_KEY",
    "POSTGRES_PASSWORD",
    "RABBITMQ_PASSWORD",
    "AWS_SECRET_ACCESS_KEY",
    "MINIO_ROOT_PASSWORD",
}


def parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None

    try:
        token = shlex.split(stripped, comments=True, posix=True)[0]
    except (IndexError, ValueError):
        return None

    key, value = token.split("=", 1)
    return key, value


def quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = parse_env_line(line)
        if parsed:
            key, value = parsed
            values[key] = value
    return values


def load_runtime_env(system: bool = False) -> dict[str, str]:
    env_values = os.environ.copy()
    candidates = [system_env_path(".env"), system_env_path("api.env")] if system else [REPO_ROOT / ".env", REPO_ROOT / "apps" / "api" / ".env"]
    for path in candidates:
        env_values.update(load_env(path))
    return env_values


def export_runtime_env(system: bool = False) -> None:
    for key, value in load_runtime_env(system=system).items():
        os.environ.setdefault(key, value)


def generate_values() -> dict[str, str]:
    postgres_password = secrets.token_urlsafe(32)
    rabbitmq_password = secrets.token_urlsafe(32)
    aws_secret = secrets.token_urlsafe(32)
    live_secret = secrets.token_urlsafe(48)

    return {
        "SECRET_KEY": secrets.token_urlsafe(64),
        "LIVE_SERVER_SECRET_KEY": live_secret,
        "POSTGRES_PASSWORD": postgres_password,
        "RABBITMQ_PASSWORD": rabbitmq_password,
        "AWS_SECRET_ACCESS_KEY": aws_secret,
        "MINIO_ROOT_PASSWORD": aws_secret,
        "DATABASE_URL": f"postgresql://taskflow:{postgres_password}@localhost:5432/taskflow",
        "REDIS_URL": "redis://localhost:6379/",
        "AMQP_URL": f"amqp://taskflow:{rabbitmq_password}@localhost:5672/taskflow",
        "DOCKERIZED": "0",
        "USE_MINIO": "1",
        "MINIO_ENDPOINT_SSL": "0",
    }


def render_template(template: Path, generated: dict[str, str]) -> str:
    lines: list[str] = []
    for raw_line in template.read_text(encoding="utf-8").splitlines():
        parsed = parse_env_line(raw_line)
        if not parsed:
            lines.append(raw_line)
            continue

        key, _value = parsed
        if key in generated:
            lines.append(f"{key}={quote(generated[key])}")
        else:
            lines.append(raw_line)

    if template.name == ".env.native.example" and "apps/api" in template.as_posix() and "AMQP_URL" not in load_env(template):
        lines.append(f"AMQP_URL={quote(generated['AMQP_URL'])}")

    return "\n".join(lines).rstrip() + "\n"


def chmod_secret(path: Path) -> None:
    if os.name != "nt":
        path.chmod(0o600)


def init_env(*, system: bool = False, force: bool = False) -> int:
    generated = generate_values()
    if system:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    for name, template in ENV_TARGETS.items():
        target = system_env_path(name) if system else local_env_path(name)
        if target.exists() and not force:
            print(f"exists: {target}")
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_template(template, generated), encoding="utf-8")
        chmod_secret(target)
        print(f"created: {target}")

    minio_target = system_env_path("minio.env") if system else REPO_ROOT / "minio.env"
    if not minio_target.exists() or force:
        minio_volumes = "/var/lib/taskflow/minio" if os.name != "nt" else "C:\\ProgramData\\Taskflow\\minio"
        minio_target.parent.mkdir(parents=True, exist_ok=True)
        minio_target.write_text(
            "\n".join(
                [
                    "MINIO_ROOT_USER=access-key",
                    f"MINIO_ROOT_PASSWORD={quote(generated['MINIO_ROOT_PASSWORD'])}",
                    f"MINIO_VOLUMES={quote(minio_volumes)}",
                    'MINIO_OPTS=--console-address ":9090"',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        chmod_secret(minio_target)
        print(f"created: {minio_target}")

    return 0
