# homelab-starter

> **One command. Pick your apps. Walk away with a working home server.**

homelab-starter is an interactive CLI that bootstraps a full self-hosted stack on any Linux machine. It handles Docker installation, generates all config files, creates secure passwords automatically, and deploys everything with a single `docker compose up`. No YAML editing. No copy-pasting passwords. No reading three different guides.

[![Ko-fi](https://img.shields.io/badge/Support-Ko--fi-ff5e5b?logo=ko-fi&logoColor=white)](https://ko-fi.com/moooosik)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?logo=github&logoColor=white)](https://github.com/sponsors/moooosik)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Quick start

SSH into your home server and run:

```bash
curl -fsSL https://raw.githubusercontent.com/moooosik/homelab-starter/main/install.sh | bash
```

That's it. The installer checks for Python and Docker, installs either if missing, then launches the interactive setup.

**Alternative — install with pipx (keeps it isolated):**

```bash
pipx install git+https://github.com/moooosik/homelab-starter.git
homelab-starter
```

---

## What happens when you run it

```
1.  Checks Docker is installed
      → If not: offers to install it automatically via get.docker.com
      → Adds your user to the docker group (no logout needed)

2.  Detects your server's local IP (e.g. 192.168.0.101)

3.  Asks your configuration depth:
      basic    — sensible defaults for everything, just pick apps
      guided   — prompts for passwords, file paths, and tokens
      advanced — all options exposed

4.  Shows a scrollable app checklist
      ↑↓ to navigate · Space to select · Enter to confirm

5.  Offers Caddy (reverse proxy) with a plain-English explanation
      → If you say yes, generates a Caddyfile automatically

6.  Asks if you have a custom domain
      → If yes: prints port-forwarding instructions + CrowdSec setup guide

7.  For guided/advanced: prompts for config specific to selected apps
      (media paths, admin passwords, API tokens)

8.  Generates ~/homelab-starter/docker-compose.yml + .env
      → Passwords and secret keys are cryptographically generated
      → You never need to touch the .env manually

9.  Runs: docker compose up -d --pull always

10. Prints the URL for every installed service

11. If Homepage was selected: prints the dashboard URL on its own line
      → "Bookmark this — it's your homelab home page."
```

---

## App catalog

28 apps across 12 categories. Every app ships with a pre-configured compose snippet — ports, volumes, environment variables, and restart policies all set.

| # | App | Category | Default port | Description |
|---|-----|----------|-------------|-------------|
| 1 | **Vaultwarden** | Security | 8080 | Self-hosted Bitwarden — password manager you fully own |
| 2 | **Caddy** | Networking | 80 / 443 | Automatic HTTPS reverse proxy |
| 3 | **CrowdSec** | Security | — | Collaborative IP blocklist + intrusion prevention |
| 4 | **Watchtower** | Maintenance | — | Auto-pulls updated container images nightly |
| 5 | **Autoheal** | Maintenance | — | Restarts unhealthy containers automatically |
| 6 | **Actual Budget** | Finance | 5006 | Local-first personal budgeting app |
| 7 | **DuckDNS** | Networking | — | Free dynamic DNS — keeps your domain pointing to your home IP |
| 8 | **Tailscale** | Networking | — | Zero-config VPN — access your server from anywhere |
| 9 | **Paperless-ngx** | Documents | 8000 | Scan, OCR, tag, and search your physical documents |
| 10 | **Dozzle** | Monitoring | 8888 | Live container log browser in the browser |
| 11 | **Portainer** | Management | 9000 | Visual Docker dashboard — deploy and manage containers |
| 12 | **Grocy** | Home | 9283 | Pantry tracker and shopping list manager |
| 13 | **Mealie** | Home | 9925 | Recipe manager with meal planning and shopping export |
| 14 | **Pi-hole** | Networking | 8053 | Network-wide DNS ad blocking for every device on your WiFi |
| 15 | **Home Assistant** | Home | 8123 | Local smart home hub — 3,000+ integrations, no cloud |
| 16 | **Uptime Kuma** | Monitoring | 3001 | Self-hosted uptime monitoring with status page |
| 17 | **Jellyfin** | Media | 8096 | Free media server — movies, shows, music. No account required |
| 18 | **Plex** | Media | 32400 | Full-featured media server with mobile and TV apps |
| 19 | **Immich** | Photos | 2283 | Self-hosted Google Photos — auto-backup, face recognition |
| 20 | **Nextcloud** | Files | 8181 | Your own Google Drive — files, calendar, contacts, video calls |
| 21 | **Homepage** | Dashboard | 3000 | App launcher dashboard with live service status tiles |
| 22 | **Stirling-PDF** | Documents | 8085 | Convert, merge, split, OCR PDFs — entirely local |
| 23 | **Authentik** | Security | 9001 | Self-hosted SSO + MFA — one login for all your apps |
| 24 | **Navidrome** | Media | 4533 | Subsonic-compatible music streaming server |
| 25 | **Changedetection.io** | Monitoring | 5000 | Alerts when any webpage changes |
| 26 | **Beszel** | Monitoring | 8090 | Lightweight server metrics — CPU, RAM, disk charted over time |
| 27 | **Kavita** | Media | 5001 | Ebooks, manga, and comics server with a built-in reader |
| 28 | **NAS Bundle** | Files | 8082 | Samba network share + FileBrowser web UI |

---

## Configuration modes

### Basic
Uses defaults for everything. Recommended for first-timers who just want to get running.
- No questions asked beyond the app checklist
- All passwords auto-generated
- All data stored under Docker named volumes

### Guided *(default)*
Prompts for the important stuff — file paths, admin passwords, API keys — and uses defaults for the rest. The right choice for most people.

Example prompts:
```
  Path to your media library [/mnt/media]: /data/movies
  Nextcloud admin password: ••••••••
  Tailscale auth key (from tailscale.com/settings/keys): tskey-auth-...
```

### Advanced
Exposes every configurable option. For users who want full control over every volume path and environment variable.

---

## Auto-generated secrets

homelab-starter uses Python's `secrets` module to generate cryptographically secure passwords for every app that needs one. You never have to create or remember these — they live in `~/homelab-starter/.env`.

Apps that get auto-generated secrets:
- Immich database password
- Nextcloud database + admin password (if not provided in guided mode)
- Paperless-ngx database password, secret key, and admin password
- Authentik database password and secret key

---

## Watchtower — automatic updates

Watchtower is always included. It checks for new container image versions every night at 4 AM and updates them automatically.

**Apps excluded from auto-update** (they require manual migration steps on major version bumps):

| App | Reason |
|-----|--------|
| Vaultwarden | Major versions change the database schema |
| Nextcloud | Major versions require a manual migration script |
| Authentik | Auth provider config breaks on schema changes |
| Immich | Frequent breaking changes between major versions |
| Paperless-ngx | Migration scripts must be run manually |

To update an excluded app safely:
```bash
cd ~/homelab-starter
docker compose pull <service-name>
docker compose up -d <service-name>
# run any migration steps listed in the app's changelog
```

---

## Custom domain setup

When the installer asks "Do you have a custom domain?", answering yes triggers:

1. **Port forwarding instructions** — forward ports 80 and 443 from your router to the server IP
2. **DNS instructions** — point your domain (and `*.domain`) to your public IP
3. **Caddyfile generation** — pre-populated with subdomains for each selected app
4. **CrowdSec guide** — how to wire the CrowdSec bouncer to Caddy to block bad actors

If you don't have a domain, all apps are still accessible by local IP (e.g. `http://192.168.0.101:8096` for Jellyfin).

---

## Dry run

Preview the generated files without deploying anything:

```bash
homelab-starter --dry-run
```

Files land in `~/homelab-starter/`. Inspect and edit them, then deploy manually:

```bash
cd ~/homelab-starter
docker compose up -d
```

---

## Deploy directory

Everything lives in `~/homelab-starter/` on your server:

```
~/homelab-starter/
├── docker-compose.yml   ← merged config for all selected apps
├── .env                 ← all secrets and config values — keep this private
└── Caddyfile            ← generated if Caddy was selected
```

To add or remove an app after initial setup, edit `docker-compose.yml` and re-run `docker compose up -d`.

---

## Requirements

| Requirement | Notes |
|---|---|
| Linux server | Debian / Ubuntu recommended. Raspberry Pi works. |
| Docker | Offered automatically if missing — uses [get.docker.com](https://get.docker.com) |
| docker compose plugin | Installed automatically if missing (apt / dnf) |
| Python 3.11+ | Required to run the CLI |
| curl | For the one-line install |

**Tested on:** Ubuntu 22.04, Ubuntu 24.04, Debian 12, Raspberry Pi OS (64-bit)

---

## Uninstalling

To stop everything:
```bash
cd ~/homelab-starter
docker compose down
```

To remove all data (destructive — this deletes your app data):
```bash
cd ~/homelab-starter
docker compose down -v
rm -rf ~/homelab-starter
```

---

## vs. alternatives

| | homelab-starter | Deployrr | DockSTARTer |
|---|---|---|---|
| curl \| bash install | ✅ | Partial | ❌ |
| Auto-installs Docker | ✅ | ✅ | ❌ |
| Auto-generated secrets | ✅ | ❌ | ❌ |
| Works without Cloudflare | ✅ | ❌ | ✅ |
| Caddy / NPM / no proxy | Choice | Traefik only | Partial |
| Fully open source | ✅ | Freemium | ✅ |

---

## Support

If homelab-starter saved you an afternoon of config-file wrestling, a coffee goes a long way:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/moooosik)

---

## Contributing

Bug reports and app addition requests welcome — [open an issue](https://github.com/moooosik/homelab-starter/issues).

To add a new app, add an entry to `homelab/apps.py` following the existing pattern (services dict + volumes dict + optional guided_prompts).

---

## License

MIT — do whatever you want with it.
