# Contributing to homelab-starter

Thanks for taking the time to contribute. This project is intentionally simple — the bar for contribution is low.

## Ways to contribute

- **Report a bug** — open an issue with reproduction steps
- **Request an app** — open an issue with the app name, Docker Hub / GHCR image, and the port it runs on
- **Add an app** — add an entry to `homelab/apps.py` and open a PR (see below)
- **Improve docs** — fix typos, clarify steps, add examples

## Adding an app

Every app lives in `homelab/apps.py` as an entry in the `APPS` dict. Copy an existing entry as a template. The required fields are:

```python
"your-app-id": {
    "name": "Display Name",
    "description": "One-line description shown in the picker",
    "category": "One of the existing category names",
    "port": 8080,          # primary web UI port, or None if no web UI
    "url_path": "",        # path suffix for the URL (e.g. "/admin"), or None
    "watchtower_exclude": False,  # True if major-version upgrades require manual steps
    "services": {
        "service-name": {
            "image": "org/image:tag",
            "container_name": "service-name",
            "restart": "unless-stopped",
            "ports": ["8080:8080"],
            "volumes": ["volume-name:/data"],
            "networks": ["homelab"],
        }
    },
    "volumes": {"volume-name": None},
}
```

Optional fields:

- `guided_prompts` — list of `{key, label, default, secret}` dicts for user-facing config
- `connect` — list of plain-English connection instructions shown after deploy (use `{SERVER_IP}` as a placeholder)
- `side_files` — dict of `filename: content` for extra files written to the deploy dir (e.g. config stubs)

If the app needs an auto-generated secret, add the env var key and desired byte length to `_AUTO_SECRETS` in `homelab/compose.py`.

Then add the app ID to the appropriate list in `CATEGORIES` at the bottom of `apps.py`.

## Running tests

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest tests/ -v
```

All tests must pass before opening a PR.

## Pull request checklist

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] New app entry follows the existing pattern (services, volumes, networks)
- [ ] Secrets use `${ENV_VAR}` substitution, not hardcoded values
- [ ] `watchtower_exclude: True` if the app is known to have breaking major-version upgrades
- [ ] App added to the correct `CATEGORIES` list
- [ ] PR description explains what the app does and why it belongs in homelab-starter

## Commit style

Use conventional commits:

```
feat: add Stirling-PDF to Documents category
fix: correct Caddyfile upstream for network_mode: host services
docs: update auto-generated secrets list in README
chore: bump PyYAML to 6.0.2
```

## What we won't merge

- Apps that require a paid account or proprietary cloud dependency to function
- Apps with no maintained Docker image
- Changes that add interactive prompts for things that can be auto-generated
- Unrelated refactors bundled with a feature or fix
