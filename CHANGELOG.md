# Changelog

All notable changes to homelab-starter are documented here.

## [Unreleased]

### Added
- **ArchiveBox** (port 8099) — self-hosted internet archive, saves full webpage copies
- **LibreSpeed** (port 8088) — self-hosted network speed test server
- **Ghost** (port 2368) — professional blogging and newsletter platform, self-hosted Substack
- Connect steps for all 56 apps — CONNECT.md covers every service with first-login URLs and client setup
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
- Ghost crashes on first boot: `ghost-db` (MySQL) now has a `mysqladmin ping` healthcheck; Ghost waits for `condition: service_healthy` before starting
- Ghost URL missing in basic mode: `GHOST_URL` now defaults to `http://<SERVER_IP>:2368` when no URL is provided
- FileBrowser default `admin / admin` credential now shown in the post-install credentials panel — prevents the default being missed
- All 12 postgres/redis/mariadb services now declare healthchecks; dependent apps upgraded to `condition: service_healthy` — eliminates DB-not-ready race conditions on first boot

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
