"""
App catalog. Each entry defines display metadata + docker-compose snippet (services + volumes).
Apps with watchtower_exclude=True get label com.centurylinklabs.watchtower.enable=false.
"""

WATCHTOWER_LABEL = "com.centurylinklabs.watchtower.enable=false"

APPS: dict[str, dict] = {
    "vaultwarden": {
        "name": "Vaultwarden",
        "description": "Self-hosted Bitwarden-compatible password vault",
        "category": "Security",
        "port": 8080,
        "url_path": "",
        "watchtower_exclude": True,
        "services": {
            "vaultwarden": {
                "image": "vaultwarden/server:latest",
                "container_name": "vaultwarden",
                "restart": "unless-stopped",
                "ports": ["8080:80"],
                "volumes": ["vaultwarden-data:/data"],
                "environment": {"WEBSOCKET_ENABLED": "true"},
                "networks": ["homelab"],
                "labels": [WATCHTOWER_LABEL],
            }
        },
        "volumes": {"vaultwarden-data": None},
    },

    "caddy": {
        "name": "Caddy",
        "description": "Automatic HTTPS reverse proxy — routes your domain to services",
        "category": "Networking",
        "port": 80,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "caddy": {
                "image": "caddy:latest",
                "container_name": "caddy",
                "restart": "unless-stopped",
                "ports": ["80:80", "443:443", "443:443/udp"],
                "volumes": [
                    "caddy-data:/data",
                    "caddy-config:/config",
                    "./Caddyfile:/etc/caddy/Caddyfile:ro",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"caddy-data": None, "caddy-config": None},
    },

    "crowdsec": {
        "name": "CrowdSec",
        "description": "Collaborative IP blocklist + intrusion prevention engine",
        "category": "Security",
        "port": None,
        "url_path": None,
        "watchtower_exclude": False,
        "services": {
            "crowdsec": {
                "image": "crowdsecurity/crowdsec:latest",
                "container_name": "crowdsec",
                "restart": "unless-stopped",
                "environment": {
                    "GID": "1000",
                    "COLLECTIONS": "crowdsecurity/linux crowdsecurity/nginx",
                },
                "volumes": [
                    "crowdsec-db:/var/lib/crowdsec/data",
                    "crowdsec-config:/etc/crowdsec",
                    "/var/log:/var/log:ro",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"crowdsec-db": None, "crowdsec-config": None},
    },

    "watchtower": {
        "name": "Watchtower",
        "description": "Auto-pulls updated container images nightly (recommended)",
        "category": "Maintenance",
        "port": None,
        "url_path": None,
        "watchtower_exclude": False,
        "services": {
            "watchtower": {
                "image": "containrrr/watchtower:latest",
                "container_name": "watchtower",
                "restart": "unless-stopped",
                "volumes": ["/var/run/docker.sock:/var/run/docker.sock"],
                "environment": {
                    "WATCHTOWER_CLEANUP": "true",
                    "WATCHTOWER_SCHEDULE": "0 0 4 * * *",
                },
                "networks": ["homelab"],
            }
        },
        "volumes": {},
    },

    "autoheal": {
        "name": "Autoheal",
        "description": "Automatically restarts unhealthy containers",
        "category": "Maintenance",
        "port": None,
        "url_path": None,
        "watchtower_exclude": False,
        "services": {
            "autoheal": {
                "image": "willfarrell/autoheal:latest",
                "container_name": "autoheal",
                "restart": "unless-stopped",
                "environment": {"AUTOHEAL_CONTAINER_LABEL": "all"},
                "volumes": ["/var/run/docker.sock:/var/run/docker.sock"],
                "networks": ["homelab"],
            }
        },
        "volumes": {},
    },

    "actual": {
        "name": "Actual Budget",
        "description": "Local-first personal finance and budgeting app",
        "category": "Finance",
        "port": 5006,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "actual": {
                "image": "actualbudget/actual-server:latest",
                "container_name": "actual",
                "restart": "unless-stopped",
                "ports": ["5006:5006"],
                "volumes": ["actual-data:/data"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"actual-data": None},
    },

    "duckdns": {
        "name": "DuckDNS",
        "description": "Free dynamic DNS — keeps your domain pointing to your home IP",
        "category": "Networking",
        "port": None,
        "url_path": None,
        "watchtower_exclude": False,
        "guided_prompts": [
            {"key": "DUCKDNS_SUBDOMAINS", "label": "DuckDNS subdomain(s) (comma-separated)", "default": "myhomelab"},
            {"key": "DUCKDNS_TOKEN", "label": "DuckDNS token", "default": "", "secret": True},
        ],
        "services": {
            "duckdns": {
                "image": "lscr.io/linuxserver/duckdns:latest",
                "container_name": "duckdns",
                "restart": "unless-stopped",
                "environment": {
                    "TZ": "${TZ}",
                    "SUBDOMAINS": "${DUCKDNS_SUBDOMAINS}",
                    "TOKEN": "${DUCKDNS_TOKEN}",
                },
                "volumes": ["duckdns-config:/config"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"duckdns-config": None},
    },

    "tailscale": {
        "name": "Tailscale",
        "description": "Zero-config VPN — access your homelab securely from anywhere",
        "category": "Networking",
        "port": None,
        "url_path": None,
        "watchtower_exclude": False,
        "guided_prompts": [
            {"key": "TAILSCALE_AUTHKEY", "label": "Tailscale auth key (from tailscale.com/settings/keys)", "default": "", "secret": True},
        ],
        "services": {
            "tailscale": {
                "image": "tailscale/tailscale:latest",
                "container_name": "tailscale",
                "restart": "unless-stopped",
                "network_mode": "host",
                "cap_add": ["NET_ADMIN", "NET_RAW"],
                "environment": {
                    "TS_AUTHKEY": "${TAILSCALE_AUTHKEY}",
                    "TS_STATE_DIR": "/var/lib/tailscale",
                },
                "volumes": [
                    "tailscale-data:/var/lib/tailscale",
                    "/dev/net/tun:/dev/net/tun",
                ],
            }
        },
        "volumes": {"tailscale-data": None},
    },

    "paperless": {
        "name": "Paperless-ngx",
        "description": "OCR, tag, and full-text search your physical documents",
        "category": "Documents",
        "port": 8000,
        "url_path": "",
        "watchtower_exclude": True,
        "services": {
            "paperless-ngx": {
                "image": "ghcr.io/paperless-ngx/paperless-ngx:latest",
                "container_name": "paperless-ngx",
                "restart": "unless-stopped",
                "ports": ["8000:8000"],
                "environment": {
                    "PAPERLESS_REDIS": "redis://paperless-redis:6379",
                    "PAPERLESS_DBHOST": "paperless-db",
                    "PAPERLESS_DBUSER": "paperless",
                    "PAPERLESS_DBPASS": "${PAPERLESS_DB_PASSWORD}",
                    "PAPERLESS_DBNAME": "paperless",
                    "PAPERLESS_SECRET_KEY": "${PAPERLESS_SECRET_KEY}",
                    "PAPERLESS_TIME_ZONE": "${TZ}",
                    "PAPERLESS_OCR_LANGUAGE": "eng",
                    "PAPERLESS_ADMIN_USER": "admin",
                    "PAPERLESS_ADMIN_PASSWORD": "${PAPERLESS_ADMIN_PASSWORD}",
                },
                "volumes": [
                    "paperless-data:/usr/src/paperless/data",
                    "paperless-media:/usr/src/paperless/media",
                    "paperless-export:/usr/src/paperless/export",
                    "paperless-consume:/usr/src/paperless/consume",
                ],
                "depends_on": ["paperless-db", "paperless-redis"],
                "networks": ["homelab"],
                "labels": [WATCHTOWER_LABEL],
            },
            "paperless-redis": {
                "image": "redis:7-alpine",
                "container_name": "paperless-redis",
                "restart": "unless-stopped",
                "networks": ["homelab"],
            },
            "paperless-db": {
                "image": "postgres:15-alpine",
                "container_name": "paperless-db",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_DB": "paperless",
                    "POSTGRES_USER": "paperless",
                    "POSTGRES_PASSWORD": "${PAPERLESS_DB_PASSWORD}",
                },
                "volumes": ["paperless-db:/var/lib/postgresql/data"],
                "networks": ["homelab"],
            },
        },
        "volumes": {
            "paperless-data": None,
            "paperless-media": None,
            "paperless-export": None,
            "paperless-consume": None,
            "paperless-db": None,
        },
    },

    "dozzle": {
        "name": "Dozzle",
        "description": "Real-time container log browser — no more SSH to read logs",
        "category": "Monitoring",
        "port": 8888,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "dozzle": {
                "image": "amir20/dozzle:latest",
                "container_name": "dozzle",
                "restart": "unless-stopped",
                "ports": ["8888:8080"],
                "volumes": ["/var/run/docker.sock:/var/run/docker.sock"],
                "networks": ["homelab"],
            }
        },
        "volumes": {},
    },

    "portainer": {
        "name": "Portainer",
        "description": "Visual Docker management dashboard — deploy, inspect, manage containers",
        "category": "Management",
        "port": 9000,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "portainer": {
                "image": "portainer/portainer-ce:latest",
                "container_name": "portainer",
                "restart": "unless-stopped",
                "ports": ["9000:9000"],
                "volumes": [
                    "/var/run/docker.sock:/var/run/docker.sock",
                    "portainer-data:/data",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"portainer-data": None},
    },

    "grocy": {
        "name": "Grocy",
        "description": "Household supplies tracker, shopping lists, and pantry management",
        "category": "Home",
        "port": 9283,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "grocy": {
                "image": "lscr.io/linuxserver/grocy:latest",
                "container_name": "grocy",
                "restart": "unless-stopped",
                "ports": ["9283:80"],
                "environment": {"TZ": "${TZ}", "PUID": "1000", "PGID": "1000"},
                "volumes": ["grocy-config:/config"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"grocy-config": None},
    },

    "mealie": {
        "name": "Mealie",
        "description": "Recipe manager with shopping list export and meal planning",
        "category": "Home",
        "port": 9925,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "mealie": {
                "image": "ghcr.io/mealie-recipes/mealie:latest",
                "container_name": "mealie",
                "restart": "unless-stopped",
                "ports": ["9925:9000"],
                "environment": {
                    "TZ": "${TZ}",
                    "PUID": "1000",
                    "PGID": "1000",
                    "MAX_WORKERS": "1",
                    "WEB_CONCURRENCY": "1",
                    "BASE_URL": "http://${SERVER_IP}:9925",
                },
                "volumes": ["mealie-data:/app/data"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"mealie-data": None},
    },

    "pihole": {
        "name": "Pi-hole",
        "description": "Network-wide DNS ad and tracker blocking",
        "category": "Networking",
        "port": 8053,
        "url_path": "/admin",
        "watchtower_exclude": False,
        "guided_prompts": [
            {"key": "PIHOLE_PASSWORD", "label": "Pi-hole web admin password", "default": "admin", "secret": True},
        ],
        "services": {
            "pihole": {
                "image": "pihole/pihole:latest",
                "container_name": "pihole",
                "restart": "unless-stopped",
                "ports": ["53:53/tcp", "53:53/udp", "8053:80"],
                "environment": {
                    "TZ": "${TZ}",
                    "WEBPASSWORD": "${PIHOLE_PASSWORD}",
                    "PIHOLE_DNS_": "8.8.8.8;8.8.4.4",
                },
                "volumes": [
                    "pihole-etc:/etc/pihole",
                    "pihole-dnsmasq:/etc/dnsmasq.d",
                ],
                "cap_add": ["NET_ADMIN"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"pihole-etc": None, "pihole-dnsmasq": None},
    },

    "homeassistant": {
        "name": "Home Assistant",
        "description": "Local smart home hub — 3,000+ integrations, no cloud required",
        "category": "Home",
        "port": 8123,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "homeassistant": {
                "image": "ghcr.io/home-assistant/home-assistant:stable",
                "container_name": "homeassistant",
                "restart": "unless-stopped",
                "network_mode": "host",
                "privileged": True,
                "environment": {"TZ": "${TZ}"},
                "volumes": [
                    "homeassistant-config:/config",
                    "/etc/localtime:/etc/localtime:ro",
                ],
            }
        },
        "volumes": {"homeassistant-config": None},
    },

    "uptime-kuma": {
        "name": "Uptime Kuma",
        "description": "Self-hosted uptime monitoring with status page and alerts",
        "category": "Monitoring",
        "port": 3001,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "uptime-kuma": {
                "image": "louislam/uptime-kuma:latest",
                "container_name": "uptime-kuma",
                "restart": "unless-stopped",
                "ports": ["3001:3001"],
                "volumes": [
                    "uptime-kuma-data:/app/data",
                    "/var/run/docker.sock:/var/run/docker.sock",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"uptime-kuma-data": None},
    },

    "jellyfin": {
        "name": "Jellyfin",
        "description": "Free media server — movies, shows, music. No phone-home, no account required",
        "category": "Media",
        "port": 8096,
        "url_path": "",
        "watchtower_exclude": False,
        "guided_prompts": [
            {"key": "MEDIA_PATH", "label": "Path to your media library", "default": "/mnt/media"},
        ],
        "services": {
            "jellyfin": {
                "image": "jellyfin/jellyfin:latest",
                "container_name": "jellyfin",
                "restart": "unless-stopped",
                "ports": ["8096:8096"],
                "environment": {"TZ": "${TZ}"},
                "volumes": [
                    "jellyfin-config:/config",
                    "jellyfin-cache:/cache",
                    "${MEDIA_PATH}:/media:ro",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"jellyfin-config": None, "jellyfin-cache": None},
    },

    "plex": {
        "name": "Plex",
        "description": "Full-featured media server with mobile apps and TV clients (requires Plex account)",
        "category": "Media",
        "port": 32400,
        "url_path": "/web",
        "watchtower_exclude": False,
        "guided_prompts": [
            {"key": "MEDIA_PATH", "label": "Path to your media library", "default": "/mnt/media"},
            {"key": "PLEX_CLAIM", "label": "Plex claim token (from plex.tv/claim)", "default": "", "secret": True},
        ],
        "services": {
            "plex": {
                "image": "lscr.io/linuxserver/plex:latest",
                "container_name": "plex",
                "restart": "unless-stopped",
                "network_mode": "host",
                "environment": {
                    "TZ": "${TZ}",
                    "PUID": "1000",
                    "PGID": "1000",
                    "VERSION": "docker",
                    "PLEX_CLAIM": "${PLEX_CLAIM}",
                },
                "volumes": [
                    "plex-config:/config",
                    "${MEDIA_PATH}:/media:ro",
                ],
            }
        },
        "volumes": {"plex-config": None},
    },

    "immich": {
        "name": "Immich",
        "description": "Self-hosted Google Photos replacement — auto-backup, face recognition, albums",
        "category": "Photos",
        "port": 2283,
        "url_path": "",
        "watchtower_exclude": True,
        "guided_prompts": [
            {"key": "IMMICH_UPLOAD_PATH", "label": "Path for Immich uploads/library", "default": "/mnt/photos"},
        ],
        "services": {
            "immich-server": {
                "image": "ghcr.io/immich-app/immich-server:release",
                "container_name": "immich-server",
                "restart": "unless-stopped",
                "ports": ["2283:2283"],
                "environment": {
                    "DB_HOSTNAME": "immich-postgres",
                    "DB_USERNAME": "postgres",
                    "DB_PASSWORD": "${IMMICH_DB_PASSWORD}",
                    "DB_DATABASE_NAME": "immich",
                    "REDIS_HOSTNAME": "immich-redis",
                    "TZ": "${TZ}",
                },
                "volumes": [
                    "${IMMICH_UPLOAD_PATH}:/usr/src/app/upload",
                    "/etc/localtime:/etc/localtime:ro",
                ],
                "depends_on": ["immich-redis", "immich-postgres"],
                "networks": ["homelab"],
                "labels": [WATCHTOWER_LABEL],
            },
            "immich-machine-learning": {
                "image": "ghcr.io/immich-app/immich-machine-learning:release",
                "container_name": "immich-machine-learning",
                "restart": "unless-stopped",
                "environment": {
                    "DB_HOSTNAME": "immich-postgres",
                    "DB_USERNAME": "postgres",
                    "DB_PASSWORD": "${IMMICH_DB_PASSWORD}",
                    "DB_DATABASE_NAME": "immich",
                    "REDIS_HOSTNAME": "immich-redis",
                },
                "volumes": ["immich-model-cache:/cache"],
                "networks": ["homelab"],
                "labels": [WATCHTOWER_LABEL],
            },
            "immich-redis": {
                "image": "redis:6.2-alpine",
                "container_name": "immich-redis",
                "restart": "unless-stopped",
                "networks": ["homelab"],
            },
            "immich-postgres": {
                "image": "tensorchord/pgvecto-rs:pg14-v0.2.0",
                "container_name": "immich-postgres",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_PASSWORD": "${IMMICH_DB_PASSWORD}",
                    "POSTGRES_USER": "postgres",
                    "POSTGRES_DB": "immich",
                    "POSTGRES_INITDB_ARGS": "--data-checksums",
                },
                "volumes": ["immich-postgres-data:/var/lib/postgresql/data"],
                "networks": ["homelab"],
                "labels": [WATCHTOWER_LABEL],
            },
        },
        "volumes": {
            "immich-model-cache": None,
            "immich-postgres-data": None,
        },
    },

    "nextcloud": {
        "name": "Nextcloud",
        "description": "Self-hosted Dropbox + Office suite — files, calendar, contacts, video calls",
        "category": "Files",
        "port": 8181,
        "url_path": "",
        "watchtower_exclude": True,
        "guided_prompts": [
            {"key": "NEXTCLOUD_ADMIN_PASSWORD", "label": "Nextcloud admin password", "default": "", "secret": True},
        ],
        "services": {
            "nextcloud": {
                "image": "nextcloud:latest",
                "container_name": "nextcloud",
                "restart": "unless-stopped",
                "ports": ["8181:80"],
                "environment": {
                    "POSTGRES_HOST": "nextcloud-db",
                    "POSTGRES_DB": "nextcloud",
                    "POSTGRES_USER": "nextcloud",
                    "POSTGRES_PASSWORD": "${NEXTCLOUD_DB_PASSWORD}",
                    "NEXTCLOUD_ADMIN_USER": "admin",
                    "NEXTCLOUD_ADMIN_PASSWORD": "${NEXTCLOUD_ADMIN_PASSWORD}",
                },
                "volumes": ["nextcloud-data:/var/www/html"],
                "depends_on": ["nextcloud-db"],
                "networks": ["homelab"],
                "labels": [WATCHTOWER_LABEL],
            },
            "nextcloud-db": {
                "image": "postgres:15-alpine",
                "container_name": "nextcloud-db",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_DB": "nextcloud",
                    "POSTGRES_USER": "nextcloud",
                    "POSTGRES_PASSWORD": "${NEXTCLOUD_DB_PASSWORD}",
                },
                "volumes": ["nextcloud-db:/var/lib/postgresql/data"],
                "networks": ["homelab"],
            },
        },
        "volumes": {"nextcloud-data": None, "nextcloud-db": None},
    },

    "homepage": {
        "name": "Homepage",
        "description": "App launcher dashboard with live service status tiles — your homelab front door",
        "category": "Dashboard",
        "port": 3000,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "homepage": {
                "image": "ghcr.io/gethomepage/homepage:latest",
                "container_name": "homepage",
                "restart": "unless-stopped",
                "ports": ["3000:3000"],
                "volumes": [
                    "homepage-config:/app/config",
                    "/var/run/docker.sock:/var/run/docker.sock",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"homepage-config": None},
    },

    "stirling-pdf": {
        "name": "Stirling-PDF",
        "description": "Convert, merge, split, compress, and OCR PDFs — entirely local",
        "category": "Documents",
        "port": 8085,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "stirling-pdf": {
                "image": "frooodle/s-pdf:latest",
                "container_name": "stirling-pdf",
                "restart": "unless-stopped",
                "ports": ["8085:8080"],
                "environment": {"DOCKER_ENABLE_SECURITY": "false"},
                "volumes": [
                    "stirling-pdf-data:/usr/share/tessdata",
                    "stirling-pdf-configs:/configs",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"stirling-pdf-data": None, "stirling-pdf-configs": None},
    },

    "authentik": {
        "name": "Authentik",
        "description": "Self-hosted SSO + MFA identity provider — add login screens to all your apps",
        "category": "Security",
        "port": 9001,
        "url_path": "/if/user/",
        "watchtower_exclude": True,
        "services": {
            "authentik-server": {
                "image": "ghcr.io/goauthentik/server:latest",
                "container_name": "authentik-server",
                "command": "server",
                "restart": "unless-stopped",
                "ports": ["9001:9000", "9443:9443"],
                "environment": {
                    "AUTHENTIK_REDIS__HOST": "authentik-redis",
                    "AUTHENTIK_POSTGRESQL__HOST": "authentik-postgres",
                    "AUTHENTIK_POSTGRESQL__USER": "authentik",
                    "AUTHENTIK_POSTGRESQL__NAME": "authentik",
                    "AUTHENTIK_POSTGRESQL__PASSWORD": "${AUTHENTIK_DB_PASSWORD}",
                    "AUTHENTIK_SECRET_KEY": "${AUTHENTIK_SECRET_KEY}",
                },
                "volumes": ["authentik-media:/media", "authentik-certs:/certs"],
                "depends_on": ["authentik-postgres", "authentik-redis"],
                "networks": ["homelab"],
                "labels": [WATCHTOWER_LABEL],
            },
            "authentik-worker": {
                "image": "ghcr.io/goauthentik/server:latest",
                "container_name": "authentik-worker",
                "command": "worker",
                "restart": "unless-stopped",
                "environment": {
                    "AUTHENTIK_REDIS__HOST": "authentik-redis",
                    "AUTHENTIK_POSTGRESQL__HOST": "authentik-postgres",
                    "AUTHENTIK_POSTGRESQL__USER": "authentik",
                    "AUTHENTIK_POSTGRESQL__NAME": "authentik",
                    "AUTHENTIK_POSTGRESQL__PASSWORD": "${AUTHENTIK_DB_PASSWORD}",
                    "AUTHENTIK_SECRET_KEY": "${AUTHENTIK_SECRET_KEY}",
                },
                "volumes": ["authentik-media:/media", "authentik-certs:/certs"],
                "depends_on": ["authentik-postgres", "authentik-redis"],
                "networks": ["homelab"],
                "labels": [WATCHTOWER_LABEL],
            },
            "authentik-postgres": {
                "image": "postgres:15-alpine",
                "container_name": "authentik-postgres",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_DB": "authentik",
                    "POSTGRES_USER": "authentik",
                    "POSTGRES_PASSWORD": "${AUTHENTIK_DB_PASSWORD}",
                },
                "volumes": ["authentik-postgres:/var/lib/postgresql/data"],
                "networks": ["homelab"],
            },
            "authentik-redis": {
                "image": "redis:alpine",
                "container_name": "authentik-redis",
                "restart": "unless-stopped",
                "networks": ["homelab"],
            },
        },
        "volumes": {
            "authentik-media": None,
            "authentik-certs": None,
            "authentik-postgres": None,
        },
    },

    "navidrome": {
        "name": "Navidrome",
        "description": "Subsonic-compatible self-hosted music streaming server",
        "category": "Media",
        "port": 4533,
        "url_path": "",
        "watchtower_exclude": False,
        "guided_prompts": [
            {"key": "MUSIC_PATH", "label": "Path to your music library", "default": "/mnt/music"},
        ],
        "services": {
            "navidrome": {
                "image": "deluan/navidrome:latest",
                "container_name": "navidrome",
                "restart": "unless-stopped",
                "ports": ["4533:4533"],
                "environment": {
                    "TZ": "${TZ}",
                    "ND_SCANSCHEDULE": "1h",
                    "ND_LOGLEVEL": "info",
                    "ND_SESSIONTIMEOUT": "24h",
                    "ND_MUSICFOLDER": "/music",
                },
                "volumes": [
                    "navidrome-data:/data",
                    "${MUSIC_PATH}:/music:ro",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"navidrome-data": None},
    },

    "changedetection": {
        "name": "Changedetection.io",
        "description": "Get alerts when any webpage changes — prices, job postings, availability",
        "category": "Monitoring",
        "port": 5000,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "changedetection": {
                "image": "ghcr.io/dgtlmoon/changedetection.io:latest",
                "container_name": "changedetection",
                "restart": "unless-stopped",
                "ports": ["5000:5000"],
                "environment": {"TZ": "${TZ}"},
                "volumes": ["changedetection-data:/datastore"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"changedetection-data": None},
    },

    "beszel": {
        "name": "Beszel",
        "description": "Lightweight server metrics dashboard — CPU, RAM, disk, network over time",
        "category": "Monitoring",
        "port": 8090,
        "url_path": "",
        "watchtower_exclude": False,
        "services": {
            "beszel": {
                "image": "henrygd/beszel:latest",
                "container_name": "beszel",
                "restart": "unless-stopped",
                "ports": ["8090:8090"],
                "volumes": ["beszel-data:/beszel/data"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"beszel-data": None},
    },

    "kavita": {
        "name": "Kavita",
        "description": "Manga, comics, and ebooks server with a built-in reader",
        "category": "Media",
        "port": 5001,
        "url_path": "",
        "watchtower_exclude": False,
        "guided_prompts": [
            {"key": "BOOKS_PATH", "label": "Path to your books/manga/comics library", "default": "/mnt/books"},
        ],
        "services": {
            "kavita": {
                "image": "kizaing/kavita:latest",
                "container_name": "kavita",
                "restart": "unless-stopped",
                "ports": ["5001:5000"],
                "environment": {"TZ": "${TZ}"},
                "volumes": [
                    "kavita-config:/kavita/config",
                    "${BOOKS_PATH}:/books",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"kavita-config": None},
    },

    "nas": {
        "name": "NAS Bundle (Samba + FileBrowser)",
        "description": "Network file share (SMB drive) + browser-based file manager at port 8082",
        "category": "Files",
        "port": 8082,
        "url_path": "",
        "watchtower_exclude": False,
        "guided_prompts": [
            {"key": "NAS_PATH", "label": "Path to share as NAS storage", "default": "/mnt/nas"},
            {"key": "NAS_USER", "label": "SMB share username", "default": "nas"},
            {"key": "NAS_PASSWORD", "label": "SMB share password", "default": "", "secret": True},
        ],
        "services": {
            "filebrowser": {
                "image": "filebrowser/filebrowser:latest",
                "container_name": "filebrowser",
                "restart": "unless-stopped",
                "ports": ["8082:80"],
                "volumes": [
                    "filebrowser-db:/database",
                    "${NAS_PATH}:/srv",
                ],
                "networks": ["homelab"],
            },
            "samba": {
                "image": "dperson/samba:latest",
                "container_name": "samba",
                "restart": "unless-stopped",
                "network_mode": "host",
                "command": [
                    "-u", "${NAS_USER};${NAS_PASSWORD}",
                    "-s", "share;/mount;yes;no;no;${NAS_USER};none",
                ],
                "volumes": ["${NAS_PATH}:/mount"],
            },
        },
        "volumes": {"filebrowser-db": None},
    },
}


def checklist_choices() -> list[tuple[str, str]]:
    """Returns (display_label, app_id) pairs for questionary checkbox."""
    items = []
    for app_id, app in APPS.items():
        label = f"{app['name']:<26} — {app['description']}"
        items.append((label, app_id))
    return items


def get_guided_prompts(app_ids: list[str]) -> list[dict]:
    """Collect guided prompts for the selected apps, deduplicating by key."""
    seen: set[str] = set()
    prompts = []
    for app_id in app_ids:
        app = APPS[app_id]
        for prompt in app.get("guided_prompts", []):
            if prompt["key"] not in seen:
                seen.add(prompt["key"])
                prompts.append(prompt)
    return prompts
