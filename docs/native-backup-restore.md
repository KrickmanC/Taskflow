# Native Backup And Restore

Backups include:

- PostgreSQL dump
- Taskflow env files
- MinIO data
- uploaded files
- version metadata

Create a backup:

```bash
taskflowctl backup
```

Restore:

```bash
taskflowctl restore /path/to/backup
```

Linux backups are stored under `/var/lib/taskflow/backups` by default. Windows backups are stored under `C:\ProgramData\Taskflow\backups`.
