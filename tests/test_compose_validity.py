"""Validate generated compose files against Docker itself.

The tests in test_compose.py assert on Python dicts. These go one step further
and hand the written docker-compose.yml to `docker compose config`, which
resolves ${VAR} interpolation from .env and validates the schema — catching
malformed keys and unresolved variables that dict-level assertions miss.

Skipped when Docker is unavailable, so local runs on a machine without Docker
still pass. CI runs on ubuntu-latest, which ships Docker.
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from homelab.apps import APPS
from homelab.compose import build, write_files


def _docker_compose_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


requires_docker = pytest.mark.skipif(
    not _docker_compose_available(),
    reason="docker compose is not available on this machine",
)


def _assert_valid(selected_ids: list[str]) -> None:
    """Build, write, and run `docker compose config` over the result."""
    compose, env = build(selected_ids, "10.0.0.1", {})
    with tempfile.TemporaryDirectory() as tmp:
        deploy_dir = Path(tmp)
        write_files(compose, env, deploy_dir, selected_ids)
        result = subprocess.run(
            ["docker", "compose", "config", "--quiet"],
            cwd=deploy_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
    assert result.returncode == 0, (
        f"docker compose rejected {selected_ids}:\n{result.stderr.strip()}"
    )


@requires_docker
@pytest.mark.parametrize("app_id", sorted(APPS))
def test_each_app_generates_valid_compose(app_id: str) -> None:
    _assert_valid([app_id])


@requires_docker
def test_all_apps_together_generate_valid_compose() -> None:
    """The merged config for every app at once must still be valid."""
    _assert_valid(sorted(APPS))


@requires_docker
@pytest.mark.parametrize(
    "combo",
    [
        pytest.param(
            ["jellyfin", "sonarr", "radarr", "prowlarr", "qbittorrent", "jellyseerr", "bazarr"],
            id="media-stack",
        ),
        pytest.param(
            ["immich", "nextcloud", "paperless", "authentik"],
            id="database-backed",
        ),
        pytest.param(
            ["caddy", "vaultwarden", "homepage", "uptime-kuma"],
            id="reverse-proxied",
        ),
        pytest.param(
            ["matrix", "mattermost", "ntfy"],
            id="communication",
        ),
        pytest.param(
            ["homeassistant", "netdata", "portainer"],
            id="host-network-mode",
        ),
    ],
)
def test_realistic_combos_generate_valid_compose(combo: list[str]) -> None:
    _assert_valid(combo)


# Credentials the user supplies from an external service. There is no sensible
# default for these, and Docker accepts a blank environment value, so they are
# allowed to render empty. Anything NOT on this list rendering blank is a bug —
# most importantly a blank in a volume/port/device spec, which Docker rejects
# outright (see _fill_prompt_defaults in homelab/compose.py).
OPTIONAL_BLANK_VARS = {
    "TAILSCALE_AUTHKEY",   # generated at tailscale.com/settings/keys
    "DUCKDNS_TOKEN",       # generated at duckdns.org
    "PLEX_CLAIM",          # generated at plex.tv/claim
    "HOARDER_OPENAI_KEY",  # optional — Hoarder runs without AI tagging
    "FLOWISE_PASSWORD",    # optional — prompted for in guided mode
}


@requires_docker
def test_no_unexpected_unresolved_variables() -> None:
    """Only known-optional credentials may render blank; anything else is a bug."""
    selected = sorted(APPS)
    compose, env = build(selected, "10.0.0.1", {})
    with tempfile.TemporaryDirectory() as tmp:
        deploy_dir = Path(tmp)
        write_files(compose, env, deploy_dir, selected)
        result = subprocess.run(
            ["docker", "compose", "config"],
            cwd=deploy_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
    assert result.returncode == 0, result.stderr.strip()
    unresolved = set(re.findall(r'The "([A-Z][A-Z0-9_]*)" variable is not set', result.stderr))
    unexpected = sorted(unresolved - OPTIONAL_BLANK_VARS)
    assert not unexpected, (
        "Variables rendered blank without a default:\n  " + "\n  ".join(unexpected)
    )
