# Native Troubleshooting

Run diagnostics first:

```bash
taskflowctl doctor
taskflowctl status
```

Dependency checks:

```bash
psql "postgresql://taskflow:taskflow@localhost:5432/taskflow" -c "SELECT 1;"
redis-cli ping
rabbitmqctl status
curl http://localhost:9000/minio/health/live
```

HTTP smoke checks:

```bash
curl -I http://localhost:8000
curl -I http://localhost:3000
curl -I http://localhost:3001/god-mode/
curl -I http://localhost:3002/spaces
curl -I http://localhost:3100/live
```

Common issues:

- Celery on Windows must use `--pool solo`.
- Redis on Windows should be bundled or replaced with a compatible native service.
- RabbitMQ requires Erlang.
- Port conflicts should be resolved before installation.
- Static production secrets should never be committed; use `taskflowctl init-env`.
