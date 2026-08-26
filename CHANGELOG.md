# Changelog

All notable changes to homelab-starter are documented here.

## [Unreleased]

### Fixed
- **`--list` crashed on Windows terminals**: the banner's box-drawing characters cannot be encoded in cp1252, the default codepage for many Windows consoles and for redirected output (`homelab-starter --list > apps.txt`). The command died with `UnicodeEncodeError` after ~68 bytes. An ASCII banner is now used when the output encoding cannot represent the original, and unencodable characters elsewhere degrade instead of aborting. UTF-8 terminals are unaffected and still get the full banner.

## [0.2.0] — 2026-08-26

Adds 8 apps (53 → 61), two new CLI flags, and fixes two bugs that made a
first-time install fail outright. **If you are on 0.1.2, upgrade** — basic
mode could not deploy any Media app.

### Added
- **Weekly image-tag verification** (`.github/workflows/verify-image-tags.yml` + `scripts/verify_image_tags.py`): checks that all 73 image references in `apps.py` still resolve at their registry, so an upstream retag or deletion is caught before a user hits it during `docker compose up`. Registry-aware — Docker Hub via the Hub catalogue API (avoids the anonymous pull-rate limit), GHCR/LSCR/others via the OCI registry v2 manifest endpoint with anonymous bearer auth. Opens a labelled issue on failure, or comments on the existing one.
- **Compose validation test suite** (`tests/test_compose_validity.py`): hands every generated compose file to `docker compose config`, which resolves `${VAR}` interpolation and validates the schema — covering all 61 apps individually, all apps merged, and 5 realistic multi-app combos. Skipped automatically when Docker is unavailable.
- Regression guards for silent-collision bugs: duplicate service names, volume names, and `container_name` values across apps (all merged via `dict.update()`, so a duplicate would overwrite silently)
- Guard against single-brace `{VAR}` placeholders in service definitions, which never interpolate
- **Memos** (port 5230) — lightweight self-hosted notes and microblog; single container, SQLite-backed
- **IT Tools** (port 8079) — 100+ browser-based IT utilities (base64, JWT, regex, cron, UUID, etc.); single container, no login required
- **SearXNG** (port 8093) — privacy-respecting metasearch engine; queries Google/Bing/DDG without tracking
- **`--update` flag**: `homelab-starter --update` re-generates `docker-compose.yml` and `.env` from the existing install without re-running the interactive flow — preserves all secrets, detects app selection from the current compose file
- **`--list` flag**: `homelab-starter --list` prints all 61 apps grouped by category with ports and descriptions — browse the catalog without running the installer
- **Flowise** (port 3100) — drag-and-drop AI workflow builder, chain LLMs and tools visually; connects to local Ollama
- **AnythingLLM** (port 3110) — chat with your documents using local or cloud LLMs; private RAG on your own server
- **ArchiveBox** (port 8099) — self-hosted internet archive, saves full webpage copies
- **LibreSpeed** (port 8088) — self-hosted network speed test server
- **Ghost** (port 2368) — professional blogging and newsletter platform, self-hosted Substack
- Connect steps for all 61 apps — CONNECT.md covers every service with first-login URLs and client setup
- Port conflict guard: installer detects Pi-hole + AdGuard Home selected together and asks which to keep
- Homepage auto-configuration: generates `homepage-config/services.yaml` with all selected app tiles
- Multi-drive Scrutiny: guided prompt for `SCRUTINY_DRIVES` accepts comma-separated device paths (e.g. `/dev/sda,/dev/nvme0n1`)
- Pi-hole and NAS share password now shown in the credentials panel at end of install
- PyPI install option (`pip install homelab-starter`)

### Fixed
- **Flowise started with a blank admin password**: `FLOWISE_PASSWORD` was a guided prompt defaulting to an empty string, so in basic mode Flowise came up with an unauthenticated admin panel — unlike every other admin password in the project, which are auto-generated. It is now in `_AUTO_SECRETS` (16 bytes) and shown in the post-install credentials panel alongside the configured username.
- **Basic mode generated an unusable compose file**: config depth `basic` skips the guided prompts, which left path variables (`MEDIA_PATH`, `DOWNLOADS_PATH`, `BOOKS_PATH`, and 9 others) unset. `${MEDIA_PATH}:/media` then rendered as `:/media`, a volume spec Docker rejects outright — so `docker compose up` failed immediately for all 12 affected apps, including every Media app. Prompt defaults are now applied for any key the user did not supply, in all config depths.
- SearXNG `SEARXNG_BASE_URL` used single-brace `{SERVER_IP}`, which is only expanded in side files and connect steps — the container received the literal string. Now uses compose-native `${SERVER_IP}`.
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
- Immich Redis upgraded from EOL `redis:6.2-alpine` to `redis:7-alpine`

## [0.1.2] — 2026-08-12

Published to PyPI from a working copy whose version bump was never committed —
no `0.1.2` ever existed in `pyproject.toml`, so this release corresponds to no
tag or commit. Reconstructed from the repository state at the time.

### Added
- Security policy, CI workflow, CodeQL analysis, and Dependabot configuration
- PyPI metadata: keywords, classifiers, project URLs

### Fixed
- Security hardening and assorted bug fixes (#4)

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
