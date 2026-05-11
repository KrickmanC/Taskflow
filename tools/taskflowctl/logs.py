from __future__ import annotations

from paths import IS_LINUX, IS_WINDOWS, LOG_DIR, TASKFLOW_SERVICES
from process import run


def logs(service: str | None = None, follow: bool = False) -> int:
    if IS_LINUX:
        unit = service or "taskflow-api"
        cmd = ["journalctl", "-u", unit]
        if follow:
            cmd.append("-f")
        run(cmd, check=False)
        return 0

    if IS_WINDOWS:
        candidates = [LOG_DIR / f"{service}.out.log"] if service else sorted(LOG_DIR.glob("*.log"))
        for path in candidates:
            if path.exists():
                print(path)
                run(["powershell.exe", "-Command", f"Get-Content -Path '{path}' {'-Wait' if follow else '-Tail 200'}"], check=False)
                return 0
        print(f"No logs found in {LOG_DIR}")
        return 1

    print("Unsupported OS")
    return 1
