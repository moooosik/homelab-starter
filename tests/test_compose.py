"""Tests for compose builder logic."""

from homelab.apps import APPS, checklist_choices, get_guided_prompts
from homelab.compose import build


def test_build_single_app():
    compose, env = build(["dozzle"], "192.168.0.101", {})
    assert "dozzle" in compose["services"]
    assert compose["services"]["dozzle"]["image"] == "amir20/dozzle:latest"
    assert "TZ" in env
    assert env["SERVER_IP"] == "192.168.0.101"


def test_build_multi_service_app():
    compose, env = build(["paperless"], "10.0.0.1", {})
    assert "paperless-ngx" in compose["services"]
    assert "paperless-db" in compose["services"]
    assert "paperless-redis" in compose["services"]
    assert "PAPERLESS_DB_PASSWORD" in env
    assert len(env["PAPERLESS_DB_PASSWORD"]) > 0


def test_auto_secrets_generated():
    compose, env = build(["immich"], "10.0.0.1", {})
    assert "IMMICH_DB_PASSWORD" in env
    assert len(env["IMMICH_DB_PASSWORD"]) >= 10


def test_user_config_overrides_auto_secret():
    _, env = build(["nextcloud"], "10.0.0.1", {"NEXTCLOUD_ADMIN_PASSWORD": "mypassword"})
    assert env["NEXTCLOUD_ADMIN_PASSWORD"] == "mypassword"


def test_watchtower_label_on_excluded_apps():
    compose, _ = build(["vaultwarden", "watchtower"], "10.0.0.1", {})
    labels = compose["services"]["vaultwarden"].get("labels", [])
    assert any("watchtower" in label and "false" in label for label in labels)


def test_watchtower_no_label_on_normal_apps():
    compose, _ = build(["dozzle", "watchtower"], "10.0.0.1", {})
    labels = compose["services"]["dozzle"].get("labels", [])
    assert not any("watchtower" in label and "false" in label for label in labels)


def test_all_app_ids_have_required_fields():
    required = {"name", "description", "port", "services", "volumes"}
    for app_id, app in APPS.items():
        missing = required - app.keys()
        assert not missing, f"{app_id} missing fields: {missing}"


def test_checklist_choices_returns_all_apps():
    choices = checklist_choices()
    ids = [app_id for _, app_id in choices]
    assert set(ids) == set(APPS.keys())


def test_guided_prompts_deduplication():
    # jellyfin and navidrome both ask for MEDIA_PATH and MUSIC_PATH respectively
    prompts = get_guided_prompts(["jellyfin", "jellyfin"])
    keys = [p["key"] for p in prompts]
    assert len(keys) == len(set(keys)), "Duplicate prompt keys returned"


def test_homelab_network_in_compose():
    compose, _ = build(["portainer"], "10.0.0.1", {})
    assert "homelab" in compose["networks"]


def test_volumes_merged_across_apps():
    compose, _ = build(["vaultwarden", "dozzle"], "10.0.0.1", {})
    assert "vaultwarden-data" in compose["volumes"]


def test_network_mode_host_apps_excluded_from_homelab_network():
    compose, _ = build(["homeassistant"], "10.0.0.1", {})
    svc = compose["services"]["homeassistant"]
    assert svc.get("network_mode") == "host"
    assert "networks" not in svc
