# Native Linux Install

Supported distributions are Ubuntu 22.04+, Ubuntu 24.04+, and Debian 12+.

Build a package:

```bash
pnpm install --frozen-lockfile
pnpm build
bash tools/install/linux/build-deb.sh
```

Install on a target host:

```bash
sudo apt install ./dist/taskflow-native_1.3.0_amd64.deb
sudo /opt/taskflow/repo/tools/taskflowctl/taskflowctl.py --system doctor
sudo /opt/taskflow/repo/tools/taskflowctl/taskflowctl.py --system status
```

System paths:

- `/opt/taskflow/repo`
- `/opt/taskflow/venv`
- `/etc/taskflow/*.env`
- `/var/lib/taskflow`
- `/var/log/taskflow`

Service logs:

```bash
journalctl -u taskflow-api -f
journalctl -u taskflow-worker -f
journalctl -u taskflow-beat -f
journalctl -u taskflow-web -f
journalctl -u taskflow-admin -f
journalctl -u taskflow-space -f
journalctl -u taskflow-live -f
journalctl -u taskflow-minio -f
```

Open:

- `http://localhost:3001/god-mode/`
- `http://localhost:3000/`
