# homelab-starter

> **One command. Pick your apps. Walk away with a working home server.**

Homelab Starter sets up your home server so you can run your own apps — password manager, media server, photo backup, smart home hub, and more — without any technical knowledge required.

Answer a few questions, pick the apps you want from a menu, and it handles everything else: installing the software it needs, creating secure passwords automatically, and getting your apps running. No config files to edit. No guides to read. No passwords to copy-paste.

[![Ko-fi](https://img.shields.io/badge/Support-Ko--fi-ff5e5b?logo=ko-fi&logoColor=white)](https://ko-fi.com/moooosik)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?logo=github&logoColor=white)](https://github.com/sponsors/moooosik)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Quick start

Open a terminal on your home server and paste this:

```bash
curl -fsSL https://raw.githubusercontent.com/moooosik/homelab-starter/main/install.sh | bash
```

That's it. It checks what your server needs, installs anything missing, then walks you through the setup.

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

52 apps across 13 categories. Every app ships with a pre-configured compose snippet — ports, volumes, environment variables, and restart policies all set. The installer walks you through categories one at a time so you're never staring at a wall of 52 choices.

### Your Digital Life
| App | Port | Description |
|-----|------|-------------|
| **Vaultwarden** | 8080 | Self-hosted Bitwarden — password manager you fully own |
| **Actual Budget** | 5006 | Local-first personal finance and budgeting |
| **Nextcloud** | 8181 | Your own Google Drive — files, calendar, contacts, video calls |
| **Syncthing** | 8384 | Continuous file sync between all your devices — no cloud middleman |
| **Baikal** | 5232 | Lightweight CalDAV/CardDAV server — sync calendar and contacts to any phone or desktop app |
| **NAS Bundle** (Samba + FileBrowser) | 8082 | Network file share + browser-based file manager |

### Media
| App | Port | Description |
|-----|------|-------------|
| **Jellyfin** | 8096 | Free media server — movies, shows, music. No account required |
| **Plex** | 32400 | Full-featured media server with mobile and TV apps |
| **Immich** | 2283 | Self-hosted Google Photos — auto-backup, face recognition |
| **Navidrome** | 4533 | Subsonic-compatible music streaming server |
| **Kavita** | 5001 | Ebooks, manga, and comics server with a built-in reader |
| **Audiobookshelf** | 13378 | Audiobook and podcast server with a mobile app |

### Media Automation
| App | Port | Description |
|-----|------|-------------|
| **Sonarr** | 8989 | Automatic TV show downloads — monitors and grabs new episodes |
| **Radarr** | 7878 | Automatic movie downloads — monitors releases and quality |
| **Prowlarr** | 9696 | Indexer manager — one place to configure all your torrent/usenet sources |
| **qBittorrent** | 8091 | Torrent client with a web UI |
| **Jellyseerr** | 5055 | Request system for Jellyfin — family members can request shows and movies |
| **Bazarr** | 6767 | Automatic subtitle downloader for Sonarr and Radarr |

### AI
| App | Port | Description |
|-----|------|-------------|
| **Ollama + Open WebUI** | 3030 | Run LLMs locally (Llama 3, Mistral, Gemma) with a ChatGPT-style interface |

### Smart Home
| App | Port | Description |
|-----|------|-------------|
| **Home Assistant** | 8123 | Local smart home hub — 3,000+ integrations, no cloud |
| **Grocy** | 9283 | Pantry tracker and household shopping list manager |
| **Mealie** | 9925 | Recipe manager with meal planning and shopping export |

### Networking
| App | Port | Description |
|-----|------|-------------|
| **Caddy** | 80 / 443 | Automatic HTTPS reverse proxy |
| **DuckDNS** | — | Free dynamic DNS — keeps your domain pointing to your home IP |
| **Tailscale** | — | Zero-config VPN — access your server from anywhere |
| **Pi-hole** | 8053 | Network-wide DNS ad blocking for every device on your WiFi |
| **AdGuard Home** | 8054 | DNS-based ad and tracker blocking — alternative to Pi-hole |

### Security
| App | Port | Description |
|-----|------|-------------|
| **CrowdSec** | — | Collaborative IP blocklist + intrusion prevention |
| **Authentik** | 9001 | Self-hosted SSO + MFA — one login for all your apps |

### Documents
| App | Port | Description |
|-----|------|-------------|
| **Paperless-ngx** | 8000 | Scan, OCR, tag, and full-text search your physical documents |
| **Stirling-PDF** | 8085 | Convert, merge, split, compress, and OCR PDFs — entirely local |

### Productivity
| App | Port | Description |
|-----|------|-------------|
| **n8n** | 5678 | Workflow automation — connect your apps like Zapier, but self-hosted |
| **Gitea** | 3080 | Self-hosted GitHub — private Git repos, issues, pull requests |
| **BookStack** | 6875 | Wiki and knowledge base — write and organize your documentation |
| **Vikunja** | 3456 | To-do lists and project management — self-hosted Todoist |
| **Planka** | 1337 | Kanban boards — self-hosted Trello |
| **Miniflux** | 8070 | Minimalist RSS feed reader |
| **Hoarder** | 3210 | AI-powered bookmark manager — save links, auto-tag, full-text search |

### Communication
| App | Port | Description |
|-----|------|-------------|
| **Matrix + Element** | 8448 / 8880 | End-to-end encrypted self-hosted messaging — your own Signal/Slack |
| **Mattermost** | 8065 | Team messaging and file sharing — self-hosted Slack |
| **ntfy** | 8095 | Push notification server — send alerts to your phone from any script |

### Monitoring
| App | Port | Description |
|-----|------|-------------|
| **Uptime Kuma** | 3001 | Self-hosted uptime monitoring with status page |
| **Dozzle** | 8888 | Live container log browser in the browser |
| **Beszel** | 8090 | Lightweight server metrics — CPU, RAM, disk charted over time |
| **Changedetection.io** | 5000 | Alerts when any webpage changes |
| **Scrutiny** | 8083 | Hard drive health monitoring (S.M.A.R.T.) — know before a drive dies |
| **Grafana + Prometheus** | 3002 | Metrics dashboards + data collection — visualize anything |
| **Netdata** | 19999 | Real-time system metrics — CPU, RAM, disk, network, per-process |
| **Healthchecks** | 8020 | Cron job monitor — alerts you when a backup or scheduled task didn't run |

### Management
| App | Port | Description |
|-----|------|-------------|
| **Portainer** | 9000 | Visual Docker management dashboard — deploy, inspect, manage containers |
| **Homepage** | 3000 | App launcher dashboard with live service status tiles |

### Maintenance
| App | Port | Description |
|-----|------|-------------|
| **Watchtower** | — | Auto-pulls updated container images nightly |
| **Autoheal** | — | Automatically restarts unhealthy containers |

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
- Gitea, BookStack, Vikunja, Planka, Miniflux, Mattermost — database passwords
- Grafana admin password, Healthchecks secret key
- Hoarder and Matrix registration secrets

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
| n8n | Workflow engine breaks on major version bumps |

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
