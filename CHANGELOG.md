# Changelog

All notable changes to homelab-starter are documented here.

## [Unreleased]

### Added
- Connect steps for Sonarr, Radarr, Prowlarr, qBittorrent, Jellyseerr, Portainer, Uptime Kuma, Grafana, n8n, Paperless-ngx, Bazarr, Grocy, Mealie, Stirling-PDF — CONNECT.md now covers all major apps
- Port conflict guard: installer detects Pi-hole + AdGuard Home selected together and asks which to keep
- Homepage auto-configuration: generates `homepage-config/services.yaml` with all selected app tiles
- Multi-drive Scrutiny: guided prompt for `SCRUTINY_DRIVES` accepts comma-separated device paths (e.g. `/dev/sda,/dev/nvme0n1`)
- Pi-hole and NAS share password now shown in the credentials panel at end of install
- PyPI install option (`pip install homelab-starter`)

### Fixed
- Matrix Synapse first-boot failure: added `synapse-init` init container that generates `homeserver.yaml` before the main service starts
- `MATRIX_REGISTRATION_SECRET` wired into `SYNAPSE_REGISTRATION_SHARED_SECRET` env var
- `element-config.json` `server_name` now uses `MATRIX_SERVER_NAME` from guided prompt instead of hardcoded `matrix.local`
- Nextcloud `NEXTCLOUD_TRUSTED_DOMAINS` env var set automatically — eliminates "Access through untrusted domain" error on first visit
- Open WebUI image tag changed from `:main` (dev branch) to `:latest`
- Netdata: removed redundant `ports` mapping (ignored by Docker when `network_mode: host`)
- Homepage `services.yaml` indentation corrected — extra nesting level was preventing tiles from rendering

## [0.1.1] — 2026-08-05

### Added
- 53 apps across 13 categories with pre-configured compose snippets
- Interactive category-then-app selection flow
- Three configuration depths: basic, guided, advanced
- Auto-generated cryptographically secure secrets for all apps that need them
- Caddy reverse proxy with auto-generated Caddyfile
- Custom domain setup with port-forwarding and CrowdSec instructions
- Homepage dashboard with live service tiles
- Watchtower automatic nightly updates (excluded apps listed in README)
- `--dry-run` flag to preview files without deploying
- `CONNECT.md` written after install with per-app connection instructions
- Docker auto-install via get.docker.com if missing
