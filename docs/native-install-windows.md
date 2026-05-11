# Native Windows Install

Supported targets are Windows 10 x64, Windows 11 x64, Windows Server 2019+, and Windows Server 2022+.

The MVP installer is a controlled installer. It checks for native dependencies and reports missing tools:

- Python 3.12
- Node.js 22
- pnpm through Corepack
- PostgreSQL
- RabbitMQ
- bundled or externally provided Redis-compatible server
- bundled MinIO
- WinSW

Build the installer on Windows:

```powershell
pnpm install --frozen-lockfile
pnpm build
.\tools\install\windows\build-exe.ps1
```

Install:

```powershell
.\TaskflowSetup-1.3.0-x64.exe
taskflowctl doctor
taskflowctl status
```

Installed paths:

- `C:\Program Files\Taskflow`
- `C:\ProgramData\Taskflow`
- `C:\ProgramData\Taskflow\logs`

Open:

- `http://localhost:3001/god-mode/`
- `http://localhost:3000/`
