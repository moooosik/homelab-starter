## What does this PR do?

<!-- One or two sentences. -->

## Type of change

- [ ] Bug fix
- [ ] New app
- [ ] Documentation update
- [ ] Other (describe below)

## New app checklist (skip if not adding an app)

- [ ] Entry added to `APPS` dict in `homelab/apps.py`
- [ ] App ID added to `CATEGORIES`
- [ ] Auto-generated secrets (if any) added to `_AUTO_SECRETS` in `homelab/compose.py`
- [ ] `watchtower_exclude` set correctly
- [ ] `networks: ["homelab"]` present (or `network_mode: host` where required)

## Testing

- [ ] `pytest tests/ -v` passes

## Notes for reviewers

<!-- Anything unusual about this change, port conflicts to watch for, etc. -->
