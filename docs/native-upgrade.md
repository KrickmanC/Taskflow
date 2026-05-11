# Native Upgrade

Safe upgrade flow:

1. Run `taskflowctl doctor`.
2. Run `taskflowctl backup`.
3. Stop Taskflow services.
4. Install the new files or package.
5. Reinstall Python and Node dependencies.
6. Build frontend and live server assets.
7. Run migrations.
8. Restart services.
9. Run `taskflowctl doctor`.
10. Smoke test the local URLs.

Linux:

```bash
sudo taskflowctl backup
sudo systemctl stop taskflow-space taskflow-admin taskflow-web taskflow-live taskflow-beat taskflow-worker taskflow-api
sudo dpkg -i taskflow-native_<new_version>_amd64.deb
sudo taskflowctl migrate
sudo taskflowctl restart
sudo taskflowctl doctor
```

Windows:

```powershell
taskflowctl backup
taskflowctl stop
.\TaskflowSetup-<new_version>-x64.exe
taskflowctl migrate
taskflowctl restart
taskflowctl doctor
```
