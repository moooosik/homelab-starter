"""Tests for compose builder logic."""

import tempfile
from pathlib import Path

import yaml

from homelab.apps import APPS, checklist_choices, get_guided_prompts
from homelab.compose import build, write_files


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


def test_matrix_synapse_init_container_present():
    compose, _ = build(["matrix"], "10.0.0.1", {})
    assert "synapse-init" in compose["services"]
    init = compose["services"]["synapse-init"]
    assert init["command"] == "generate"
    assert init["restart"] == "no"


def test_matrix_synapse_depends_on_init():
    compose, _ = build(["matrix"], "10.0.0.1", {})
    synapse = compose["services"]["synapse"]
    dep = synapse.get("depends_on", {})
    assert "synapse-init" in dep
    assert dep["synapse-init"]["condition"] == "service_completed_successfully"


def test_scrutiny_drives_default():
    compose, env = build(["scrutiny"], "10.0.0.1", {})
    assert compose["services"]["scrutiny"]["devices"] == ["/dev/sda"]
    assert env["SCRUTINY_DRIVES"] == "/dev/sda"


def test_scrutiny_drives_multiple():
    compose, env = build(["scrutiny"], "10.0.0.1", {"SCRUTINY_DRIVES": "/dev/sda,/dev/nvme0n1"})
    assert compose["services"]["scrutiny"]["devices"] == ["/dev/sda", "/dev/nvme0n1"]


def test_homepage_uses_bind_mount():
    compose, _ = build(["homepage"], "10.0.0.1", {})
    vols = compose["services"]["homepage"]["volumes"]
    assert any("homepage-config" in v and v.startswith("./") for v in vols)


def test_homepage_services_yaml_is_valid():
    """Regression: descriptions with ':' must not corrupt the YAML output."""
    import sys
    import types

    # Minimal stub of cli._write_homepage_services without deploying
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from homelab.cli import _write_homepage_services

    with tempfile.TemporaryDirectory() as tmp:
        # Monkeypatch DEPLOY_DIR so files go to the temp dir
        import homelab.cli as cli_mod
        orig = cli_mod.DEPLOY_DIR
        cli_mod.DEPLOY_DIR = Path(tmp)
        try:
            _write_homepage_services(["archivebox", "dozzle"], "10.0.0.1")
        finally:
            cli_mod.DEPLOY_DIR = orig

        svc_path = Path(tmp) / "homepage-config" / "services.yaml"
        content = svc_path.read_text()
        # Must parse without error
        parsed = yaml.safe_load(content)
        assert parsed is not None
        # ArchiveBox description contains ':' — verify it didn't corrupt the file
        flat = str(parsed)
        assert "ArchiveBox" in flat or "archivebox" in flat.lower()


def test_matrix_element_config_uses_server_name():
    compose, env = build(["matrix"], "10.0.0.1", {"MATRIX_SERVER_NAME": "chat.home.local"})
    with tempfile.TemporaryDirectory() as tmp:
        write_files(compose, env, Path(tmp), ["matrix"])
        cfg = (Path(tmp) / "element-config.json").read_text()
    assert "chat.home.local" in cfg
    assert "matrix.local" not in cfg


def test_ghost_url_defaults_to_server_ip():
    _, env = build(["ghost"], "10.0.0.1", {})
    assert env.get("GHOST_URL") == "http://10.0.0.1:2368"


def test_ghost_url_not_overridden_when_set():
    _, env = build(["ghost"], "10.0.0.1", {"GHOST_URL": "https://blog.example.com"})
    assert env["GHOST_URL"] == "https://blog.example.com"


def test_ghost_db_healthcheck_and_depends_on():
    compose, _ = build(["ghost"], "10.0.0.1", {})
    assert "healthcheck" in compose["services"]["ghost-db"]
    dep = compose["services"]["ghost"].get("depends_on", {})
    assert "ghost-db" in dep
    assert dep["ghost-db"]["condition"] == "service_healthy"


def test_archivebox_in_compose():
    compose, _ = build(["archivebox"], "10.0.0.1", {})
    assert "archivebox" in compose["services"]


def test_librespeed_in_compose():
    compose, _ = build(["librespeed"], "10.0.0.1", {})
    assert "librespeed" in compose["services"]


def test_flowise_in_compose():
    compose, _ = build(["flowise"], "10.0.0.1", {})
    assert "flowise" in compose["services"]


def test_anythingllm_in_compose():
    compose, _ = build(["anythingllm"], "10.0.0.1", {})
    assert "anythingllm" in compose["services"]


def test_ai_category_has_three_apps():
    from homelab.apps import CATEGORIES
    assert len(CATEGORIES["AI"]) == 3


def test_memos_in_compose():
    compose, _ = build(["memos"], "10.0.0.1", {})
    assert "memos" in compose["services"]


def test_it_tools_in_compose():
    compose, _ = build(["it-tools"], "10.0.0.1", {})
    assert "it-tools" in compose["services"]


def test_searxng_in_compose():
    compose, _ = build(["searxng"], "10.0.0.1", {})
    assert "searxng" in compose["services"]


def test_no_port_conflicts():
    from homelab.apps import APPS
    ports: dict[int, str] = {}
    for app_id, app in APPS.items():
        port = app.get("port")
        if port is None:
            continue
        assert port not in ports, (
            f"Port {port} is used by both '{ports[port]}' and '{app_id}'"
        )
        ports[port] = app_id


def test_service_dicts_use_compose_interpolation():
    """Guard: service dicts are dumped raw to YAML, so placeholders need ${VAR}, not {VAR}.

    Single-brace {VAR} is only expanded in side_files and connect steps. A bare
    {VAR} inside a service definition reaches the container as a literal string.
    """
    import re
    from homelab.apps import APPS
    bare_placeholder = re.compile(r"(?<!\$)\{([A-Z][A-Z0-9_]*)\}")
    violations = []
    for app_id, app in APPS.items():
        dumped = yaml.dump(app["services"])
        for match in bare_placeholder.finditer(dumped):
            violations.append(f"{app_id}: {match.group(0)} should be ${match.group(0)}")
    assert not violations, (
        "Bare-brace placeholders in service definitions:\n  " + "\n  ".join(violations)
    )


def test_no_service_name_conflicts():
    """Guard: build() merges services with dict.update() — duplicate names overwrite silently."""
    from homelab.apps import APPS
    services: dict[str, str] = {}
    for app_id, app in APPS.items():
        for svc_name in app["services"]:
            assert svc_name not in services, (
                f"Service '{svc_name}' is defined by both '{services[svc_name]}' and '{app_id}'"
            )
            services[svc_name] = app_id


def test_no_volume_name_conflicts():
    """Guard: volumes are merged the same way — a shared name silently shares storage."""
    from homelab.apps import APPS
    volumes: dict[str, str] = {}
    for app_id, app in APPS.items():
        for vol_name in app["volumes"]:
            assert vol_name not in volumes, (
                f"Volume '{vol_name}' is declared by both '{volumes[vol_name]}' and '{app_id}'"
            )
            volumes[vol_name] = app_id


def test_no_container_name_conflicts():
    """Guard: Docker refuses to start two containers sharing a container_name."""
    from homelab.apps import APPS
    names: dict[str, str] = {}
    for app_id, app in APPS.items():
        for svc_name, svc in app["services"].items():
            container_name = svc.get("container_name")
            if container_name is None:
                continue
            owner = f"{app_id}/{svc_name}"
            assert container_name not in names, (
                f"container_name '{container_name}' is used by both "
                f"'{names[container_name]}' and '{owner}'"
            )
            names[container_name] = owner


def test_scrutiny_drives_empty_falls_back_to_default():
    compose, env = build(["scrutiny"], "10.0.0.1", {"SCRUTINY_DRIVES": ""})
    assert compose["services"]["scrutiny"]["devices"] == ["/dev/sda"]
    assert env["SCRUTINY_DRIVES"] == "/dev/sda"


def test_scrutiny_drives_whitespace_falls_back_to_default():
    compose, env = build(["scrutiny"], "10.0.0.1", {"SCRUTINY_DRIVES": "   "})
    assert compose["services"]["scrutiny"]["devices"] == ["/dev/sda"]
    assert env["SCRUTINY_DRIVES"] == "/dev/sda"


def test_scrutiny_drives_strips_whitespace_around_entries():
    compose, _ = build(["scrutiny"], "10.0.0.1", {"SCRUTINY_DRIVES": " /dev/sda , /dev/sdb "})
    assert compose["services"]["scrutiny"]["devices"] == ["/dev/sda", "/dev/sdb"]


def test_db_services_have_healthchecks():
    """Guard: every postgres/redis/mariadb/mysql service must declare a healthcheck."""
    from homelab.apps import APPS
    db_images = ("postgres", "redis", "mariadb", "mysql")
    missing = []
    for app_id, app in APPS.items():
        for svc_name, svc in app["services"].items():
            img = svc.get("image", "")
            if any(db in img for db in db_images) and "healthcheck" not in svc:
                missing.append(f"{app_id}/{svc_name} ({img})")
    assert not missing, f"DB services without healthcheck: {missing}"


def test_app_services_use_condition_depends_on():
    """Guard: depends_on referencing a DB service must use condition: service_healthy."""
    from homelab.apps import APPS
    db_images = ("postgres", "redis", "mariadb", "mysql")
    violations = []
    for app_id, app in APPS.items():
        db_svc_names = {
            svc_name
            for svc_name, svc in app["services"].items()
            if any(db in svc.get("image", "") for db in db_images)
        }
        for svc_name, svc in app["services"].items():
            dep = svc.get("depends_on")
            if isinstance(dep, list):
                for d in dep:
                    if d in db_svc_names:
                        violations.append(f"{app_id}/{svc_name} depends on {d} without service_healthy")
    assert not violations, f"List-form depends_on on DB services: {violations}"
