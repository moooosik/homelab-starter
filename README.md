# homelab-starter

Interactive CLI that bootstraps a full Docker Compose homelab stack from zero — pick your apps, answer a few questions, and get everything running.

## Quick start

SSH into your homelab server, then:

```bash
curl -fsSL https://raw.githubusercontent.com/moooosik/homelab-starter/main/install.sh | bash
```

Or with pipx:

```bash
pipx install git+https://github.com/moooosik/homelab-starter.git
homelab-starter
```

## What it does

1. Checks Docker is installed (prints install instructions if not)
2. Detects your server's local IP
3. Asks your config depth: **basic** / **guided** / **advanced**
4. Shows a scrollable app checklist (28 apps across 10 categories)
5. Optionally sets up Caddy reverse proxy + generates a Caddyfile
6. Asks if you have a custom domain (prints port-forwarding + CrowdSec instructions)
7. For guided/advanced mode: prompts for paths and passwords per selected app
8. Generates `~/homelab-starter/docker-compose.yml` + `.env` with auto-generated secrets
9. Runs `docker compose up -d`
10. Prints the full URL list for every installed service
11. Highlights the Homepage dashboard URL and suggests bookmarking it

## App catalog (28 apps)

| Category | Apps |
|---|---|
| Security | Vaultwarden, CrowdSec, Authentik |
| Networking | Caddy, DuckDNS, Tailscale, Pi-hole |
| Media | Jellyfin, Plex, Navidrome, Kavita |
| Photos | Immich |
| Files | Nextcloud, NAS Bundle (Samba + FileBrowser) |
| Documents | Paperless-ngx, Stirling-PDF |
| Home | Home Assistant, Grocy, Mealie |
| Monitoring | Uptime Kuma, Dozzle, Beszel, Changedetection.io |
| Finance | Actual Budget |
| Management | Portainer |
| Maintenance | Watchtower, Autoheal |
| Dashboard | Homepage |

## Watchtower policy

Watchtower is always included and auto-updates containers nightly (4 AM). Apps that require manual migration steps on major version bumps are pinned with `com.centurylinklabs.watchtower.enable=false`:

> Vaultwarden, Nextcloud, Authentik, Immich, Paperless-ngx

## Dry run

Generate the compose files without deploying:

```bash
homelab-starter --dry-run
```

Files land in `~/homelab-starter/`. Edit them, then run `docker compose up -d` manually.

## Requirements

- Linux server (Debian/Ubuntu recommended)
- Docker + docker compose plugin ([install](https://get.docker.com))
- Python 3.11+

## Deploy directory

All files go to `~/homelab-starter/`:

```
~/homelab-starter/
├── docker-compose.yml
├── .env              ← auto-generated secrets, keep private
└── Caddyfile         ← if Caddy was selected
```

## License

MIT
