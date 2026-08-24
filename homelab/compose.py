"""Build and write a merged docker-compose.yml + .env from selected app entries."""

import os
import re
import secrets
from pathlib import Path

import yaml

from homelab.apps import APPS


_AUTO_SECRETS = {
    # Original apps
    "IMMICH_DB_PASSWORD": 32,
    "NEXTCLOUD_DB_PASSWORD": 32,
    "NEXTCLOUD_ADMIN_PASSWORD": 16,
    "PAPERLESS_DB_PASSWORD": 32,
    "PAPERLESS_SECRET_KEY": 64,
    "PAPERLESS_ADMIN_PASSWORD": 16,
    "AUTHENTIK_DB_PASSWORD": 32,
    "AUTHENTIK_SECRET_KEY": 50,
    # New apps
    "GITEA_DB_PASSWORD": 32,
    "BOOKSTACK_DB_PASSWORD": 32,
    "BOOKSTACK_ROOT_PASSWORD": 16,
    "VIKUNJA_DB_PASSWORD": 32,
    "VIKUNJA_JWT_SECRET": 50,
    "PLANKA_DB_PASSWORD": 32,
    "PLANKA_SECRET_KEY": 50,
    "MINIFLUX_DB_PASSWORD": 32,
    "MINIFLUX_ADMIN_PASSWORD": 16,
    "GRAFANA_ADMIN_PASSWORD": 16,
    "HEALTHCHECKS_SECRET_KEY": 50,
    "HOARDER_SECRET": 50,
    "HOARDER_MEILI_KEY": 50,
    "MATRIX_REGISTRATION_SECRET": 50,
    "MATTERMOST_DB_PASSWORD": 32,
    "PIHOLE_PASSWORD": 16,
    "NAS_PASSWORD": 16,
    "GHOST_DB_PASSWORD": 32,
    "GHOST_DB_ROOT_PASSWORD": 32,
}


def build(selected_ids: list[str], server_ip: str, user_config: dict) -> tuple[dict, dict]:
    """
    Returns (compose_dict, env_dict).

    compose_dict is the full docker-compose structure ready for yaml.dump.
    env_dict maps env var name → value for the .env file.
    """
    services: dict = {}
    volumes: dict = {}
    tz = _detect_tz()
    env: dict = {"TZ": tz, "SERVER_IP": server_ip}

    for app_id in selected_ids:
        app = APPS[app_id]
        services.update(app["services"])
        volumes.update(app["volumes"])

    env.update({k: user_config.get(k, "") for k in user_config})
    _fill_auto_secrets(env)
    _expand_scrutiny_drives(services, env)
    _set_app_url_defaults(selected_ids, env)

    compose = {
        "services": services,
        "networks": {"homelab": {"driver": "bridge"}},
    }
    if volumes:
        compose["volumes"] = volumes

    return compose, env


def _detect_tz() -> str:
    tz_file = Path("/etc/timezone")
    if tz_file.exists():
        tz = tz_file.read_text().strip()
        if tz:
            return tz
    localtime = Path("/etc/localtime")
    if localtime.is_symlink():
        target = str(localtime.resolve())
        if "/zoneinfo/" in target:
            return target.split("/zoneinfo/", 1)[1]
    return "UTC"


def _fill_auto_secrets(env: dict) -> None:
    for key, length in _AUTO_SECRETS.items():
        if key not in env or not env[key]:
            env[key] = secrets.token_urlsafe(length)


def _expand_scrutiny_drives(services: dict, env: dict) -> None:
    if "scrutiny" not in services:
        return
    raw = env.get("SCRUTINY_DRIVES", "/dev/sda")
    drives = [d.strip() for d in raw.split(",") if d.strip()]
    if not drives:
        drives = ["/dev/sda"]
    services["scrutiny"]["devices"] = drives
    env["SCRUTINY_DRIVES"] = ",".join(drives)


def _set_app_url_defaults(selected_ids: list[str], env: dict) -> None:
    server_ip = env.get("SERVER_IP", "localhost")
    if "ghost" in selected_ids and not env.get("GHOST_URL"):
        env["GHOST_URL"] = f"http://{server_ip}:2368"


def write_files(compose: dict, env: dict, deploy_dir: Path, selected_ids: list[str] | None = None) -> None:
    deploy_dir.mkdir(parents=True, exist_ok=True)
    compose_path = deploy_dir / "docker-compose.yml"
    env_path = deploy_dir / ".env"

    with open(compose_path, "w") as f:
        yaml.dump(compose, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    fd = os.open(env_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with open(fd, "w") as f:
        for key, value in env.items():
            safe_value = str(value).replace("\n", "").replace("\r", "")
            f.write(f"{key}={safe_value}\n")

    if selected_ids:
        for app_id in selected_ids:
            for filename, content in APPS[app_id].get("side_files", {}).items():
                expanded = re.sub(
                    r"\{([A-Z][A-Z0-9_]*)\}",
                    lambda m: str(env.get(m.group(1), m.group(0))),
                    content,
                )
                (deploy_dir / filename).write_text(expanded)
