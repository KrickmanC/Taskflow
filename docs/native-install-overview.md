# Native Install Overview

Taskflow native install runs the same application stack without Docker or Docker Compose. The installer path uses native PostgreSQL, Redis-compatible server, RabbitMQ, MinIO, Python, Node.js, pnpm, and OS services.

Supported MVP targets:

- Ubuntu 22.04+, Ubuntu 24.04+, Debian 12+
- Windows 10 x64, Windows 11 x64, Windows Server 2019+

Primary artifacts:

- Linux: `taskflow-native_<version>_amd64.deb`
- Windows: `TaskflowSetup-<version>-x64.exe`

Common management command:

```bash
taskflowctl doctor
taskflowctl init-env
taskflowctl db-init
taskflowctl rabbitmq-init
taskflowctl minio-init
taskflowctl migrate
taskflowctl service-install
taskflowctl start
taskflowctl status
taskflowctl backup
taskflowctl restore <backup-dir>
taskflowctl upgrade
```

The native installer must not require Docker, Docker Compose, Docker Desktop, Docker Engine, or WSL.

Optional reverse proxy mode can be added in front of native services.

Caddy example:

```caddyfile
taskflow.example.com {
    reverse_proxy /api/* localhost:8000
    reverse_proxy /live/* localhost:3100
    reverse_proxy /god-mode/* localhost:3001
    reverse_proxy /spaces/* localhost:3002
    reverse_proxy localhost:3000
}
```

Nginx example:

```nginx
server {
    listen 80;
    server_name taskflow.example.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /live/ {
        proxy_pass http://127.0.0.1:3100;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /god-mode/ {
        proxy_pass http://127.0.0.1:3001;
    }

    location /spaces/ {
        proxy_pass http://127.0.0.1:3002;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
    }
}
```
