"""Build and write a merged docker-compose.yml + .env from selected app entries."""

import secrets
import socket
from pathlib import Path

import yaml

from homelab.apps import APPS


_AUTO_SECRETS = {
    "IMMICH_DB_PASSWORD": 32,
    "NEXTCLOUD_DB_PASSWORD": 32,
    "NEXTCLOUD_ADMIN_PASSWORD": 16,
    "PAPERLESS_DB_PASSWORD": 32,
    "PAPERLESS_SECRET_KEY": 64,
    "PAPERLESS_ADMIN_PASSWORD": 16,
    "AUTHENTIK_DB_PASSWORD": 32,
    "AUTHENTIK_SECRET_KEY": 50,
}


def build(selected_ids: list[str], server_ip: str, user_config: dict) -> tuple[dict, dict]:
    """
    Returns (compose_dict, env_dict).

    compose_dict is the full docker-compose structure ready for yaml.dump.
    env_dict maps env var name → value for the .env file.
    """
    services: dict = {}
    volumes: dict = {}
    env: dict = {"TZ": "America/Denver", "SERVER_IP": server_ip}

    for app_id in selected_ids:
        app = APPS[app_id]
        services.update(app["services"])
        volumes.update(app["volumes"])

    env.update({k: user_config.get(k, "") for k in user_config})
    _fill_auto_secrets(env)

    compose = {
        "services": services,
        "networks": {"homelab": {"driver": "bridge"}},
    }
    if volumes:
        compose["volumes"] = volumes

    return compose, env


def _fill_auto_secrets(env: dict) -> None:
    for key, length in _AUTO_SECRETS.items():
        if key not in env or not env[key]:
            env[key] = secrets.token_urlsafe(length)


def write_files(compose: dict, env: dict, deploy_dir: Path) -> None:
    deploy_dir.mkdir(parents=True, exist_ok=True)
    compose_path = deploy_dir / "docker-compose.yml"
    env_path = deploy_dir / ".env"

    with open(compose_path, "w") as f:
        yaml.dump(compose, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    with open(env_path, "w") as f:
        for key, value in env.items():
            f.write(f"{key}={value}\n")
