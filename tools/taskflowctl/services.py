from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from paths import CONFIG_DIR, DATA_DIR, INSTALL_DIR, IS_LINUX, IS_WINDOWS, LINUX_SERVICE_DIR, LOG_DIR, REPO_ROOT, SERVICE_STOP_ORDER, TASKFLOW_SERVICES
from process import command_ok, run, which


def install_deps() -> int:
    if IS_LINUX:
        run(["apt-get", "update"])
        run(
            [
                "apt-get",
                "install",
                "-y",
                "ca-certificates",
                "curl",
                "git",
                "build-essential",
                "pkg-config",
                "python3",
                "python3-venv",
                "python3-dev",
                "libpq-dev",
                "libxml2-dev",
                "libxslt1-dev",
                "libffi-dev",
                "libssl-dev",
                "cargo",
                "rsync",
                "postgresql",
                "postgresql-contrib",
                "redis-server",
                "rabbitmq-server",
            ]
        )
        if not which("node"):
            with tempfile.NamedTemporaryFile(prefix="nodesource-setup-", suffix=".sh", delete=False) as setup_script:
                setup_path = setup_script.name
            run(["curl", "-fsSL", "https://deb.nodesource.com/setup_22.x", "-o", setup_path])
            run(["bash", setup_path])
            run(["apt-get", "install", "-y", "nodejs"])
            Path(setup_path).unlink(missing_ok=True)
        if which("corepack"):
            run(["corepack", "enable"], check=False)
        return 0

    if IS_WINDOWS:
        for package in ["Python.Python.3.12", "OpenJS.NodeJS.LTS", "PostgreSQL.PostgreSQL", "RabbitMQ.RabbitMQ"]:
            run(["winget", "install", package], check=False)
        return 0

    print("Unsupported OS")
    return 1


def service_install() -> int:
    if IS_LINUX:
        template_dir = REPO_ROOT / "tools" / "taskflowctl" / "templates" / "linux"
        LINUX_SERVICE_DIR.mkdir(parents=True, exist_ok=True)
        for service_file in template_dir.glob("taskflow-*.service"):
            target = LINUX_SERVICE_DIR / service_file.name
            shutil.copy2(service_file, target)
            print(f"installed: {target}")
        run(["systemctl", "daemon-reload"])
        for service in TASKFLOW_SERVICES:
            run(["systemctl", "enable", service], check=False)
        return 0

    if IS_WINDOWS:
        script = REPO_ROOT / "tools" / "install" / "windows" / "register-services.ps1"
        run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script])
        return 0

    print("Unsupported OS")
    return 1


def service_uninstall() -> int:
    if IS_LINUX:
        for service in TASKFLOW_SERVICES:
            run(["systemctl", "disable", service], check=False)
            run(["systemctl", "stop", service], check=False)
        for service_file in LINUX_SERVICE_DIR.glob("taskflow-*.service"):
            service_file.unlink(missing_ok=True)
        run(["systemctl", "daemon-reload"], check=False)
        return 0

    if IS_WINDOWS:
        script = REPO_ROOT / "tools" / "install" / "windows" / "unregister-services.ps1"
        run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script])
        return 0

    print("Unsupported OS")
    return 1


def service_action(action: str) -> int:
    if IS_LINUX:
        services = TASKFLOW_SERVICES if action != "stop" else [svc for svc in SERVICE_STOP_ORDER if svc.startswith("taskflow-")]
        for service in services:
            run(["systemctl", action, service], check=False)
        return 0

    if IS_WINDOWS:
        services = TASKFLOW_SERVICES if action != "stop" else [svc for svc in SERVICE_STOP_ORDER if svc.startswith("taskflow-")]
        for service in services:
            if action == "restart":
                run(["sc.exe", "stop", service], check=False)
                run(["sc.exe", "start", service], check=False)
            else:
                run(["sc.exe", action, service], check=False)
        return 0

    print("Unsupported OS")
    return 1


def status() -> int:
    failed = 0
    if IS_LINUX:
        for service in TASKFLOW_SERVICES:
            ok = command_ok(["systemctl", "is-active", "--quiet", service])
            print(f"{service}: {'running' if ok else 'not running'}")
            failed += 0 if ok else 1
        return 0 if failed == 0 else 1

    if IS_WINDOWS:
        for service in TASKFLOW_SERVICES:
            ok = command_ok(["sc.exe", "query", service])
            print(f"{service}: {'registered' if ok else 'missing'}")
            failed += 0 if ok else 1
        return 0 if failed == 0 else 1

    print("Unsupported OS")
    return 1


def uninstall(*, purge: bool = False) -> int:
    service_uninstall()
    if purge:
        for path in [INSTALL_DIR, CONFIG_DIR, DATA_DIR, LOG_DIR]:
            if path and str(path) not in {"", ".", "/"} and path.exists():
                shutil.rmtree(path)
                print(f"removed: {path}")
    return 0
