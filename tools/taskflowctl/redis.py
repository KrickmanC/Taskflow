from __future__ import annotations

from env import load_runtime_env
from process import command_ok, which


def redis_check(*, system: bool = False) -> int:
    env_values = load_runtime_env(system=system)
    if not which("redis-cli"):
        print("redis-cli not found")
        return 1

    host = env_values.get("REDIS_HOST", "localhost")
    port = env_values.get("REDIS_PORT", "6379")
    if command_ok(["redis-cli", "-h", host, "-p", port, "ping"]):
        print("Redis PING returned PONG")
        return 0

    print("Redis PING failed")
    return 1


def check_redis(*, system: bool = False) -> bool:
    env_values = load_runtime_env(system=system)
    if not which("redis-cli"):
        return False

    host = env_values.get("REDIS_HOST", "localhost")
    port = env_values.get("REDIS_PORT", "6379")
    return command_ok(["redis-cli", "-h", host, "-p", port, "ping"])
