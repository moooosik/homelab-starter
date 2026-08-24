"""
App catalog. Each entry defines display metadata + docker-compose snippet (services + volumes).
Apps with watchtower_exclude=True get label com.centurylinklabs.watchtower.enable=false.
"""

WATCHTOWER_LABEL = "com.centurylinklabs.watchtower.enable=false"

APPS: dict[str, dict] = {
    # -------------------------------------------------------------------------
    # YOUR DIGITAL LIFE
    # -------------------------------------------------------------------------
    "vaultwarden": {
        "name": "Vaultwarden",
        "description": "Self-hosted Bitwarden-compatible password vault",
        "category": "Your Digital Life",
        "port": 8080,
        "url_path": "",
        "watchtower_exclude": True,
        "connect": [
            "Mobile app (iOS/Android): Install Bitwarden → Settings → Self-hosted server → http://{SERVER_IP}:8080",
            "Browser extension: Settings → Self-hosted server → http://{SERVER_IP}:8080",
            "First use: create your account at http://{SERVER_IP}:8080",
        ],
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

    "actual": {
        "name": "Actual Budget",
        "description": "Local-first personal finance and budgeting app",
        "category": "Your Digital Life",
        "port": 5006,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:5006 — create a new budget file on first visit",
            "Mobile: use the Actual Budget web app in your phone browser at http://{SERVER_IP}:5006",
        ],
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

    "nextcloud": {
        "name": "Nextcloud",
        "description": "Self-hosted Dropbox + Office suite — files, calendar, contacts, video calls",
        "category": "Your Digital Life",
        "port": 8181,
        "url_path": "",
        "watchtower_exclude": True,
        "guided_prompts": [
            {"key": "NEXTCLOUD_ADMIN_PASSWORD", "label": "Nextcloud admin password", "default": "", "secret": True},
        ],
        "connect": [
            "Mobile app (iOS/Android): Install Nextcloud → Add account → Server: http://{SERVER_IP}:8181",
            "Desktop sync client: Add account → Server: http://{SERVER_IP}:8181",
            "CalDAV (calendar sync): http://{SERVER_IP}:8181/remote.php/dav",
            "CardDAV (contacts sync): http://{SERVER_IP}:8181/remote.php/dav",
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
                    "NEXTCLOUD_TRUSTED_DOMAINS": "${SERVER_IP}",
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

    "syncthing": {
        "name": "Syncthing",
        "description": "Continuous file sync between all your devices — no cloud middleman",
        "category": "Your Digital Life",
        "port": 8384,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Install Syncthing on each device you want to sync",
            "Find this server's Device ID at http://{SERVER_IP}:8384 → Actions → Show ID",
            "On each device: Add remote device → paste the Device ID",
        ],
        "services": {
            "syncthing": {
                "image": "syncthing/syncthing:latest",
                "container_name": "syncthing",
                "restart": "unless-stopped",
                "ports": [
                    "8384:8384",
                    "22000:22000/tcp",
                    "22000:22000/udp",
                ],
                "environment": {
                    "PUID": "1000",
                    "PGID": "1000",
                },
                "volumes": ["syncthing-data:/var/syncthing"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"syncthing-data": None},
    },

    "nas": {
        "name": "NAS Bundle (Samba + FileBrowser)",
        "description": "Network file share (SMB drive) + browser-based file manager at port 8082",
        "category": "Your Digital Life",
        "port": 8082,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "File browser UI: open http://{SERVER_IP}:8082 — login: admin / admin (change immediately)",
            "Windows SMB: open File Explorer, type \\\\{SERVER_IP}\\nas in the address bar",
            "macOS SMB: Finder > Go > Connect to Server > smb://{SERVER_IP}/nas",
            "Linux SMB: mount -t cifs //{SERVER_IP}/nas /mnt/point -o username=homelab",
        ],
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

    "baikal": {
        "name": "Baikal",
        "description": "Lightweight CalDAV/CardDAV server — sync your calendar and contacts to any phone or desktop app",
        "category": "Your Digital Life",
        "port": 5232,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "iOS Calendar: Settings → Calendar → Accounts → Add Account → Other → CalDAV → Server: http://{SERVER_IP}:5232/dav.php",
            "iOS Contacts: Settings → Contacts → Accounts → Add Account → Other → CardDAV → Server: http://{SERVER_IP}:5232/dav.php",
            "Android: Install DAVx⁵ (free, F-Droid/Play) → Add account → URL: http://{SERVER_IP}:5232/dav.php",
            "Thunderbird: Add CalDAV calendar → URL: http://{SERVER_IP}:5232/dav.php",
        ],
        "services": {
            "baikal": {
                "image": "ckulka/baikal:nginx",
                "container_name": "baikal",
                "restart": "unless-stopped",
                "ports": ["5232:80"],
                "volumes": [
                    "baikal-config:/var/www/baikal/Specific",
                    "baikal-data:/var/www/baikal/data",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"baikal-config": None, "baikal-data": None},
    },

    # -------------------------------------------------------------------------
    # MEDIA
    # -------------------------------------------------------------------------
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
        "connect": [
            "Mobile app (iOS/Android): Install Jellyfin → Add server → http://{SERVER_IP}:8096",
            "Smart TV: Install Jellyfin app on your TV → Add server → http://{SERVER_IP}:8096",
            "Infuse (Apple TV/iOS): Settings → Add Jellyfin → http://{SERVER_IP}:8096",
            "Kodi: install the Jellyfin for Kodi add-on",
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
        "connect": [
            "Sign in to your plex.tv account in any Plex app — your server appears automatically",
            "Web player: http://{SERVER_IP}:32400/web",
            "Note: a free plex.tv account is required",
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
        "category": "Media",
        "port": 2283,
        "url_path": "",
        "watchtower_exclude": True,
        "guided_prompts": [
            {"key": "IMMICH_UPLOAD_PATH", "label": "Path for Immich uploads/library", "default": "/mnt/photos"},
        ],
        "connect": [
            "Mobile app (iOS/Android): Install Immich → Server URL: http://{SERVER_IP}:2283",
            "Enable auto-backup: in the app → Settings → turn on Background Backup",
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
        "connect": [
            "Android: Symfonium or DSub → Add server (Subsonic) → http://{SERVER_IP}:4533",
            "iOS: Substreamer or Finamp → Server: http://{SERVER_IP}:4533",
            "Desktop: Sonixd → http://{SERVER_IP}:4533",
            "Use the username and password you set in Navidrome's web UI",
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
        "connect": [
            "Web UI: http://{SERVER_IP}:5001 (works on any device browser)",
            "E-reader OPDS feed: http://{SERVER_IP}:5001/api/opds/{{your-api-key}} (find API key in Kavita → User Settings → 3rd party clients)",
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

    "audiobookshelf": {
        "name": "Audiobookshelf",
        "description": "Audiobook and podcast server — stream from any device",
        "category": "Media",
        "port": 13378,
        "url_path": "",
        "watchtower_exclude": False,
        "guided_prompts": [
            {"key": "AUDIOBOOKS_PATH", "label": "Path to your audiobooks", "default": "/mnt/audiobooks"},
            {"key": "PODCASTS_PATH", "label": "Path to your podcasts", "default": "/mnt/podcasts"},
        ],
        "connect": [
            "Mobile app (iOS/Android): Install Audiobookshelf → Server URL: http://{SERVER_IP}:13378",
            "Log in with your Audiobookshelf username and password",
        ],
        "services": {
            "audiobookshelf": {
                "image": "ghcr.io/advplyr/audiobookshelf:latest",
                "container_name": "audiobookshelf",
                "restart": "unless-stopped",
                "ports": ["13378:80"],
                "environment": {"TZ": "${TZ}"},
                "volumes": [
                    "${AUDIOBOOKS_PATH}:/audiobooks",
                    "${PODCASTS_PATH}:/podcasts",
                    "audiobookshelf-config:/config",
                    "audiobookshelf-metadata:/metadata",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"audiobookshelf-config": None, "audiobookshelf-metadata": None},
    },

    # -------------------------------------------------------------------------
    # MEDIA AUTOMATION
    # -------------------------------------------------------------------------
    "sonarr": {
        "name": "Sonarr",
        "description": "Auto-downloads and organizes TV shows",
        "category": "Media Automation",
        "port": 8989,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:8989 — Sonarr will walk you through initial setup",
            "Add a root folder: Settings > Media Management > Root Folders > /media",
            "Connect qBittorrent: Settings > Download Clients > Add > qBittorrent > host=qbittorrent, port=8080",
            "Connect Prowlarr: Settings > Indexers > Add Indexer > Torznab (point to Prowlarr)",
        ],
        "guided_prompts": [
            {"key": "MEDIA_PATH", "label": "Path to your media library", "default": "/mnt/media"},
            {"key": "DOWNLOADS_PATH", "label": "Path to your downloads folder", "default": "/mnt/downloads"},
        ],
        "services": {
            "sonarr": {
                "image": "lscr.io/linuxserver/sonarr:latest",
                "container_name": "sonarr",
                "restart": "unless-stopped",
                "ports": ["8989:8989"],
                "environment": {
                    "TZ": "${TZ}",
                    "PUID": "1000",
                    "PGID": "1000",
                },
                "volumes": [
                    "sonarr-config:/config",
                    "${MEDIA_PATH}:/media",
                    "${DOWNLOADS_PATH}:/downloads",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"sonarr-config": None},
    },

    "radarr": {
        "name": "Radarr",
        "description": "Auto-downloads and organizes movies",
        "category": "Media Automation",
        "port": 7878,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:7878 — Radarr will walk you through initial setup",
            "Add a root folder: Settings > Media Management > Root Folders > /media",
            "Connect qBittorrent: Settings > Download Clients > Add > qBittorrent > host=qbittorrent, port=8080",
            "Connect Prowlarr: Settings > Indexers > Add Indexer > Torznab (point to Prowlarr)",
        ],
        "guided_prompts": [
            {"key": "MEDIA_PATH", "label": "Path to your media library", "default": "/mnt/media"},
            {"key": "DOWNLOADS_PATH", "label": "Path to your downloads folder", "default": "/mnt/downloads"},
        ],
        "services": {
            "radarr": {
                "image": "lscr.io/linuxserver/radarr:latest",
                "container_name": "radarr",
                "restart": "unless-stopped",
                "ports": ["7878:7878"],
                "environment": {
                    "TZ": "${TZ}",
                    "PUID": "1000",
                    "PGID": "1000",
                },
                "volumes": [
                    "radarr-config:/config",
                    "${MEDIA_PATH}:/media",
                    "${DOWNLOADS_PATH}:/downloads",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"radarr-config": None},
    },

    "prowlarr": {
        "name": "Prowlarr",
        "description": "Indexer manager for Sonarr and Radarr — connects to torrent sites",
        "category": "Media Automation",
        "port": 9696,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:9696 — add your indexers (torrent sites) here",
            "Connect to Sonarr: Settings > Apps > Add Application > Sonarr > http://sonarr:8989",
            "Connect to Radarr: Settings > Apps > Add Application > Radarr > http://radarr:7878",
        ],
        "services": {
            "prowlarr": {
                "image": "lscr.io/linuxserver/prowlarr:latest",
                "container_name": "prowlarr",
                "restart": "unless-stopped",
                "ports": ["9696:9696"],
                "environment": {
                    "TZ": "${TZ}",
                    "PUID": "1000",
                    "PGID": "1000",
                },
                "volumes": ["prowlarr-config:/config"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"prowlarr-config": None},
    },

    "qbittorrent": {
        "name": "qBittorrent",
        # WebUI on host port 8091 to avoid conflict with Vaultwarden (8080)
        "description": "Torrent client with a web UI — where Sonarr and Radarr send downloads",
        "category": "Media Automation",
        "port": 8091,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:8091 — default login is admin / adminadmin (change it immediately)",
            "Sonarr/Radarr connect to this using host=qbittorrent, port=8080 (internal Docker port)",
        ],
        "guided_prompts": [
            {"key": "DOWNLOADS_PATH", "label": "Path to your downloads folder", "default": "/mnt/downloads"},
        ],
        "services": {
            "qbittorrent": {
                "image": "lscr.io/linuxserver/qbittorrent:latest",
                "container_name": "qbittorrent",
                "restart": "unless-stopped",
                "ports": [
                    "8091:8080",
                    "6881:6881",
                    "6881:6881/udp",
                ],
                "environment": {
                    "TZ": "${TZ}",
                    "PUID": "1000",
                    "PGID": "1000",
                    "WEBUI_PORT": "8080",
                },
                "volumes": [
                    "qbittorrent-config:/config",
                    "${DOWNLOADS_PATH}:/downloads",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"qbittorrent-config": None},
    },

    "jellyseerr": {
        "name": "Jellyseerr",
        "description": "Media request UI — family members request movies and shows",
        "category": "Media Automation",
        "port": 5055,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:5055 — sign in with your Jellyfin account to configure",
            "Connect Jellyfin: Setup Wizard > Jellyfin > http://jellyfin:8096",
            "Share http://{SERVER_IP}:5055 with family — they can request movies and shows",
        ],
        "services": {
            "jellyseerr": {
                "image": "fallenbagel/jellyseerr:latest",
                "container_name": "jellyseerr",
                "restart": "unless-stopped",
                "ports": ["5055:5055"],
                "environment": {
                    "TZ": "${TZ}",
                    "LOG_LEVEL": "debug",
                },
                "volumes": ["jellyseerr-config:/app/config"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"jellyseerr-config": None},
    },

    "bazarr": {
        "name": "Bazarr",
        "description": "Auto-downloads subtitles for movies and shows",
        "category": "Media Automation",
        "port": 6767,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:6767 to configure Bazarr",
            "Connect Sonarr: Settings > Sonarr > host=sonarr, port=8989, API key from Sonarr > Settings > General",
            "Connect Radarr: Settings > Radarr > host=radarr, port=7878, API key from Radarr > Settings > General",
            "Add subtitle providers: Settings > Subtitles > pick OpenSubtitles, Subscene, etc.",
        ],
        "guided_prompts": [
            {"key": "MEDIA_PATH", "label": "Path to your media library", "default": "/mnt/media"},
        ],
        "services": {
            "bazarr": {
                "image": "lscr.io/linuxserver/bazarr:latest",
                "container_name": "bazarr",
                "restart": "unless-stopped",
                "ports": ["6767:6767"],
                "environment": {
                    "TZ": "${TZ}",
                    "PUID": "1000",
                    "PGID": "1000",
                },
                "volumes": [
                    "bazarr-config:/config",
                    "${MEDIA_PATH}:/media",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"bazarr-config": None},
    },

    # -------------------------------------------------------------------------
    # AI
    # -------------------------------------------------------------------------
    "ai": {
        "name": "AI Bundle (Ollama + Open WebUI)",
        "description": "Run AI chat locally — like ChatGPT but on your own hardware, no internet needed",
        "category": "AI",
        "port": 3030,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Web UI: http://{SERVER_IP}:3030 — works from any browser on your network",
            "Ollama API (for other apps): http://{SERVER_IP}:11434",
        ],
        "services": {
            "ollama": {
                "image": "ollama/ollama:latest",
                "container_name": "ollama",
                "restart": "unless-stopped",
                "ports": ["11434:11434"],
                "volumes": ["ollama-data:/root/.ollama"],
                "networks": ["homelab"],
            },
            "open-webui": {
                "image": "ghcr.io/open-webui/open-webui:latest",
                "container_name": "open-webui",
                "restart": "unless-stopped",
                "ports": ["3030:8080"],
                "environment": {
                    "OLLAMA_BASE_URL": "http://ollama:11434",
                },
                "volumes": ["open-webui-data:/app/backend/data"],
                "depends_on": ["ollama"],
                "networks": ["homelab"],
            },
        },
        "volumes": {"ollama-data": None, "open-webui-data": None},
    },

    # -------------------------------------------------------------------------
    # SMART HOME
    # -------------------------------------------------------------------------
    "homeassistant": {
        "name": "Home Assistant",
        "description": "Local smart home hub — 3,000+ integrations, no cloud required",
        "category": "Smart Home",
        "port": 8123,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Mobile app (iOS/Android): Install Home Assistant → Connect → http://{SERVER_IP}:8123",
            "Remote access: pair with Tailscale or use Nabu Casa (paid cloud relay)",
        ],
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

    "grocy": {
        "name": "Grocy",
        "description": "Household supplies tracker, shopping lists, and pantry management",
        "category": "Smart Home",
        "port": 9283,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:9283 — default login is admin / admin (change it in Settings)",
            "Mobile app: install Grocy for Android or iOS, then set server to http://{SERVER_IP}:9283",
        ],
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
        "category": "Smart Home",
        "port": 9925,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:9925 — default login is changeme@example.com / MyPassword (change immediately)",
            "Import recipes by URL: click + > Create Recipe > Import from URL",
        ],
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

    # -------------------------------------------------------------------------
    # NETWORKING
    # -------------------------------------------------------------------------
    "caddy": {
        "name": "Caddy",
        "description": "Automatic HTTPS reverse proxy — routes your domain to services",
        "category": "Networking",
        "port": 80,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Edit ~/homelab-starter/Caddyfile to set up your subdomains — stubs are pre-generated",
            "Reload config after changes: docker exec caddy caddy reload --config /etc/caddy/Caddyfile",
            "Caddy auto-provisions HTTPS certificates when your domain DNS is pointed at this server",
        ],
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
        "connect": [
            "Install Tailscale on each device (iOS, Android, Windows, Mac, Linux) from tailscale.com",
            "Sign in with the same account — this server appears automatically as a node",
            "Use the Tailscale IP to reach all your services from anywhere, no port forwarding needed",
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

    "pihole": {
        "name": "Pi-hole",
        "description": "Network-wide DNS ad and tracker blocking",
        "category": "Networking",
        "port": 8053,
        "url_path": "/admin",
        "watchtower_exclude": False,
        "connect": [
            "Admin UI: http://{SERVER_IP}:8053/admin — login with your Pi-hole password",
            "To block ads on a device: set its DNS server to {SERVER_IP} in your router or device network settings",
            "To block ads network-wide: set your router's DNS to {SERVER_IP} (check your router admin for 'DNS server' setting)",
        ],
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

    # NOTE: adguardhome and pihole both claim port 53 — do not run both at the same time.
    "adguardhome": {
        "name": "AdGuard Home",
        "description": "DNS ad blocker with a polished UI — alternative to Pi-hole",
        "category": "Networking",
        "port": 8054,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Setup wizard runs on first visit: http://{SERVER_IP}:8054 — follow the prompts",
            "After setup the dashboard moves to http://{SERVER_IP}:8054",
            "Point your router or devices' DNS to {SERVER_IP} to start blocking ads network-wide",
        ],
        "services": {
            "adguardhome": {
                "image": "adguard/adguardhome:latest",
                "container_name": "adguardhome",
                "restart": "unless-stopped",
                "ports": [
                    "53:53/tcp",
                    "53:53/udp",
                    "8054:3000",
                ],
                "volumes": [
                    "adguardhome-work:/opt/adguardhome/work",
                    "adguardhome-conf:/opt/adguardhome/conf",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"adguardhome-work": None, "adguardhome-conf": None},
    },

    "librespeed": {
        "name": "LibreSpeed",
        "description": "Self-hosted network speed test — measure download, upload, and ping from any browser",
        "category": "Networking",
        "port": 8088,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:8088 and click Go — tests your speed to this server",
            "Share with others on your network to test their connection to the server",
        ],
        "services": {
            "librespeed": {
                "image": "lscr.io/linuxserver/librespeed:latest",
                "container_name": "librespeed",
                "restart": "unless-stopped",
                "ports": ["8088:80"],
                "environment": {
                    "TZ": "${TZ}",
                    "PUID": "1000",
                    "PGID": "1000",
                    "MODE": "standalone",
                },
                "volumes": ["librespeed-config:/config"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"librespeed-config": None},
    },

    # -------------------------------------------------------------------------
    # SECURITY
    # -------------------------------------------------------------------------
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

    "authentik": {
        "name": "Authentik",
        "description": "Self-hosted SSO + MFA identity provider — add login screens to all your apps",
        "category": "Security",
        "port": 9001,
        "url_path": "/if/user/",
        "watchtower_exclude": True,
        "connect": [
            "Open http://{SERVER_IP}:9001/if/flow/initial-setup/ to set the admin password",
            "Admin panel: http://{SERVER_IP}:9001/if/admin/",
            "To protect an app: Admin > Applications > Create > add a proxy provider pointing to the app's internal URL",
        ],
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

    # -------------------------------------------------------------------------
    # DOCUMENTS
    # -------------------------------------------------------------------------
    "paperless": {
        "name": "Paperless-ngx",
        "description": "OCR, tag, and full-text search your physical documents",
        "category": "Documents",
        "port": 8000,
        "url_path": "",
        "watchtower_exclude": True,
        "connect": [
            "Open http://{SERVER_IP}:8000 — login: admin / see credentials panel above",
            "Upload documents via the web UI, or drop files into the consume folder",
            "Mobile scan: use the Paperless app (iOS/Android) — Server URL: http://{SERVER_IP}:8000",
        ],
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

    "stirling-pdf": {
        "name": "Stirling-PDF",
        "description": "Convert, merge, split, compress, and OCR PDFs — entirely local",
        "category": "Documents",
        "port": 8085,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:8085 — no login required, all tools available immediately",
        ],
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

    "archivebox": {
        "name": "ArchiveBox",
        "description": "Self-hosted internet archive — save full copies of any webpage: HTML, PDF, screenshot",
        "category": "Documents",
        "port": 8099,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:8099 — create your admin account with the on-screen prompt",
            "Add URLs to archive via the web UI, CLI, or by importing bookmarks/RSS feeds",
            "Browser extension: install ArchiveBox Exporter to save pages in one click",
        ],
        "services": {
            "archivebox": {
                "image": "archivebox/archivebox:latest",
                "container_name": "archivebox",
                "restart": "unless-stopped",
                "ports": ["8099:8000"],
                "environment": {
                    "ALLOWED_HOSTS": "*",
                    "MEDIA_MAX_SIZE": "750m",
                },
                "volumes": ["archivebox-data:/data"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"archivebox-data": None},
    },

    # -------------------------------------------------------------------------
    # PRODUCTIVITY
    # -------------------------------------------------------------------------
    "n8n": {
        "name": "n8n",
        # watchtower_exclude: True — n8n frequently introduces breaking changes on major versions
        "description": "Workflow automation — connect your apps like Zapier, but self-hosted",
        "category": "Productivity",
        "port": 5678,
        "url_path": "",
        "watchtower_exclude": True,
        "connect": [
            "Open http://{SERVER_IP}:5678 — create your owner account on first visit",
            "Browse community workflows at https://n8n.io/workflows to get started fast",
        ],
        "services": {
            "n8n": {
                "image": "n8nio/n8n:latest",
                "container_name": "n8n",
                "restart": "unless-stopped",
                "ports": ["5678:5678"],
                "environment": {
                    "N8N_HOST": "${SERVER_IP}",
                    "N8N_PORT": "5678",
                    "N8N_PROTOCOL": "http",
                    "WEBHOOK_URL": "http://${SERVER_IP}:5678",
                    "GENERIC_TIMEZONE": "${TZ}",
                },
                "volumes": ["n8n-data:/home/node/.n8n"],
                "networks": ["homelab"],
                "labels": [WATCHTOWER_LABEL],
            }
        },
        "volumes": {"n8n-data": None},
    },

    "gitea": {
        "name": "Gitea",
        "description": "Self-hosted GitHub — private Git repos, issues, pull requests",
        "category": "Productivity",
        "port": 3080,
        "url_path": "",
        "watchtower_exclude": False,
        # Auto-secret: GITEA_DB_PASSWORD
        "connect": [
            "Web UI: http://{SERVER_IP}:3080 — create your account here first",
            "Git over HTTPS: git remote add origin http://{SERVER_IP}:3080/{{username}}/{{repo}}.git",
            "Git over SSH: git remote add origin ssh://git@{SERVER_IP}:222/{{username}}/{{repo}}.git",
        ],
        "services": {
            "gitea": {
                "image": "gitea/gitea:latest",
                "container_name": "gitea",
                "restart": "unless-stopped",
                "ports": ["3080:3000", "222:22"],
                "environment": {
                    "USER_UID": "1000",
                    "USER_GID": "1000",
                    "GITEA__database__DB_TYPE": "postgres",
                    "GITEA__database__HOST": "gitea-db:5432",
                    "GITEA__database__NAME": "gitea",
                    "GITEA__database__USER": "gitea",
                    "GITEA__database__PASSWD": "${GITEA_DB_PASSWORD}",
                },
                "volumes": [
                    "gitea-data:/data",
                    "/etc/localtime:/etc/localtime:ro",
                ],
                "depends_on": ["gitea-db"],
                "networks": ["homelab"],
            },
            "gitea-db": {
                "image": "postgres:15-alpine",
                "container_name": "gitea-db",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_DB": "gitea",
                    "POSTGRES_USER": "gitea",
                    "POSTGRES_PASSWORD": "${GITEA_DB_PASSWORD}",
                },
                "volumes": ["gitea-db:/var/lib/postgresql/data"],
                "networks": ["homelab"],
            },
        },
        "volumes": {"gitea-data": None, "gitea-db": None},
    },

    "bookstack": {
        "name": "BookStack",
        "description": "Wiki and documentation platform — like Notion but self-hosted",
        "category": "Productivity",
        "port": 6875,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:6875 — login: admin@example.com / see credentials panel above",
            "Change the admin email: Users > Admin > Edit",
        ],
        # Auto-secrets: BOOKSTACK_DB_PASSWORD, BOOKSTACK_ROOT_PASSWORD
        "services": {
            "bookstack": {
                "image": "lscr.io/linuxserver/bookstack:latest",
                "container_name": "bookstack",
                "restart": "unless-stopped",
                "ports": ["6875:80"],
                "environment": {
                    "PUID": "1000",
                    "PGID": "1000",
                    "TZ": "${TZ}",
                    "APP_URL": "http://${SERVER_IP}:6875",
                    "DB_HOST": "bookstack-db",
                    "DB_USER": "bookstack",
                    "DB_PASS": "${BOOKSTACK_DB_PASSWORD}",
                    "DB_DATABASE": "bookstack",
                },
                "volumes": ["bookstack-config:/config"],
                "depends_on": ["bookstack-db"],
                "networks": ["homelab"],
            },
            "bookstack-db": {
                "image": "mariadb:10.11",
                "container_name": "bookstack-db",
                "restart": "unless-stopped",
                "environment": {
                    "MYSQL_ROOT_PASSWORD": "${BOOKSTACK_ROOT_PASSWORD}",
                    "MYSQL_DATABASE": "bookstack",
                    "MYSQL_USER": "bookstack",
                    "MYSQL_PASSWORD": "${BOOKSTACK_DB_PASSWORD}",
                },
                "volumes": ["bookstack-db:/var/lib/mysql"],
                "networks": ["homelab"],
            },
        },
        "volumes": {"bookstack-config": None, "bookstack-db": None},
    },

    "vikunja": {
        "name": "Vikunja",
        "description": "Task manager and to-do lists — like Todoist but self-hosted",
        "category": "Productivity",
        "port": 3456,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:3456 — register a new account on first visit",
            "Mobile: install the Vikunja app or use the web UI in your mobile browser",
        ],
        # Auto-secrets: VIKUNJA_DB_PASSWORD, VIKUNJA_JWT_SECRET
        "services": {
            "vikunja": {
                "image": "vikunja/vikunja:latest",
                "container_name": "vikunja",
                "restart": "unless-stopped",
                "ports": ["3456:3456"],
                "environment": {
                    "VIKUNJA_DATABASE_TYPE": "postgres",
                    "VIKUNJA_DATABASE_HOST": "vikunja-db",
                    "VIKUNJA_DATABASE_DATABASE": "vikunja",
                    "VIKUNJA_DATABASE_USER": "vikunja",
                    "VIKUNJA_DATABASE_PASSWORD": "${VIKUNJA_DB_PASSWORD}",
                    "VIKUNJA_SERVICE_JWTSECRET": "${VIKUNJA_JWT_SECRET}",
                    "VIKUNJA_SERVICE_FRONTENDURL": "http://${SERVER_IP}:3456",
                    "TZ": "${TZ}",
                },
                "volumes": ["vikunja-files:/app/vikunja/files"],
                "depends_on": ["vikunja-db"],
                "networks": ["homelab"],
            },
            "vikunja-db": {
                "image": "postgres:15-alpine",
                "container_name": "vikunja-db",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_DB": "vikunja",
                    "POSTGRES_USER": "vikunja",
                    "POSTGRES_PASSWORD": "${VIKUNJA_DB_PASSWORD}",
                },
                "volumes": ["vikunja-db:/var/lib/postgresql/data"],
                "networks": ["homelab"],
            },
        },
        "volumes": {"vikunja-files": None, "vikunja-db": None},
    },

    "planka": {
        "name": "Planka",
        "description": "Kanban board — like Trello but self-hosted",
        "category": "Productivity",
        "port": 1337,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:1337 — register the first account (it becomes admin)",
        ],
        # Auto-secrets: PLANKA_DB_PASSWORD, PLANKA_SECRET_KEY
        "services": {
            "planka": {
                "image": "ghcr.io/plankanban/planka:latest",
                "container_name": "planka",
                "restart": "unless-stopped",
                "ports": ["1337:1337"],
                "environment": {
                    "BASE_URL": "http://${SERVER_IP}:1337",
                    "DATABASE_URL": "postgresql://planka:${PLANKA_DB_PASSWORD}@planka-db:5432/planka",
                    "SECRET_KEY": "${PLANKA_SECRET_KEY}",
                    "TZ": "${TZ}",
                },
                "volumes": [
                    "planka-avatars:/app/public/user-avatars",
                    "planka-backgrounds:/app/public/project-background-images",
                    "planka-attachments:/app/private/attachments",
                ],
                "depends_on": ["planka-db"],
                "networks": ["homelab"],
            },
            "planka-db": {
                "image": "postgres:15-alpine",
                "container_name": "planka-db",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_DB": "planka",
                    "POSTGRES_USER": "planka",
                    "POSTGRES_PASSWORD": "${PLANKA_DB_PASSWORD}",
                },
                "volumes": ["planka-db:/var/lib/postgresql/data"],
                "networks": ["homelab"],
            },
        },
        "volumes": {
            "planka-avatars": None,
            "planka-backgrounds": None,
            "planka-attachments": None,
            "planka-db": None,
        },
    },

    "miniflux": {
        "name": "Miniflux",
        "description": "Minimal RSS reader — follow websites and blogs without algorithmic feeds",
        "category": "Productivity",
        "port": 8070,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:8070 — login: admin / see credentials panel above",
            "Add feeds: Feeds > Add Feed > paste any RSS/Atom URL",
            "Use a Fever-compatible RSS app (Reeder, NetNewsWire) by pointing it to http://{SERVER_IP}:8070/fever/",
        ],
        # Auto-secrets: MINIFLUX_DB_PASSWORD, MINIFLUX_ADMIN_PASSWORD
        "services": {
            "miniflux": {
                "image": "miniflux/miniflux:latest",
                "container_name": "miniflux",
                "restart": "unless-stopped",
                "ports": ["8070:8080"],
                "environment": {
                    "DATABASE_URL": "postgres://miniflux:${MINIFLUX_DB_PASSWORD}@miniflux-db:5432/miniflux?sslmode=disable",
                    "RUN_MIGRATIONS": "1",
                    "CREATE_ADMIN": "1",
                    "ADMIN_USERNAME": "admin",
                    "ADMIN_PASSWORD": "${MINIFLUX_ADMIN_PASSWORD}",
                },
                "depends_on": ["miniflux-db"],
                "networks": ["homelab"],
            },
            "miniflux-db": {
                "image": "postgres:15-alpine",
                "container_name": "miniflux-db",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_DB": "miniflux",
                    "POSTGRES_USER": "miniflux",
                    "POSTGRES_PASSWORD": "${MINIFLUX_DB_PASSWORD}",
                },
                "volumes": ["miniflux-db:/var/lib/postgresql/data"],
                "networks": ["homelab"],
            },
        },
        "volumes": {"miniflux-db": None},
    },

    "hoarder": {
        "name": "Hoarder",
        "description": "Save links, articles, and screenshots — AI tagging if you have an OpenAI key",
        "category": "Productivity",
        "port": 3210,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:3210 — create an account on first visit",
            "Browser extension: install Hoarder for Chrome or Firefox to save pages in one click",
            "Mobile: install the Hoarder app (iOS/Android) and set server to http://{SERVER_IP}:3210",
        ],
        # Auto-secrets: HOARDER_SECRET, HOARDER_MEILI_KEY
        "guided_prompts": [
            {
                "key": "HOARDER_OPENAI_KEY",
                "label": "OpenAI API key for AI tagging (optional — press Enter to skip)",
                "default": "",
                "secret": True,
            },
        ],
        "services": {
            "hoarder": {
                "image": "ghcr.io/hoarder-app/hoarder:latest",
                "container_name": "hoarder",
                "restart": "unless-stopped",
                "ports": ["3210:3000"],
                "environment": {
                    "NEXTAUTH_SECRET": "${HOARDER_SECRET}",
                    "NEXTAUTH_URL": "http://${SERVER_IP}:3210",
                    "DATA_DIR": "/data",
                    "MEILI_ADDR": "http://hoarder-meili:7700",
                    "MEILI_MASTER_KEY": "${HOARDER_MEILI_KEY}",
                    "OPENAI_API_KEY": "${HOARDER_OPENAI_KEY}",
                },
                "volumes": ["hoarder-data:/data"],
                "depends_on": ["hoarder-meili"],
                "networks": ["homelab"],
            },
            "hoarder-meili": {
                "image": "getmeili/meilisearch:v1.6",
                "container_name": "hoarder-meili",
                "restart": "unless-stopped",
                "environment": {
                    "MEILI_NO_ANALYTICS": "true",
                    "MEILI_MASTER_KEY": "${HOARDER_MEILI_KEY}",
                },
                "volumes": ["hoarder-meili:/meili_data"],
                "networks": ["homelab"],
            },
        },
        "volumes": {"hoarder-data": None, "hoarder-meili": None},
    },

    "ghost": {
        "name": "Ghost",
        "description": "Professional blogging and newsletter platform — self-hosted Substack",
        "category": "Productivity",
        "port": 2368,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:2368/ghost — complete the setup wizard to create your site",
            "Your blog is live at http://{SERVER_IP}:2368",
            "Members can subscribe at http://{SERVER_IP}:2368/#subscribe",
        ],
        "guided_prompts": [
            {"key": "GHOST_URL", "label": "Public URL for your Ghost site (e.g. https://blog.example.com)", "default": "http://localhost:2368"},
        ],
        "services": {
            "ghost": {
                "image": "ghost:latest",
                "container_name": "ghost",
                "restart": "unless-stopped",
                "ports": ["2368:2368"],
                "environment": {
                    "database__client": "mysql",
                    "database__connection__host": "ghost-db",
                    "database__connection__user": "ghost",
                    "database__connection__password": "${GHOST_DB_PASSWORD}",
                    "database__connection__database": "ghost",
                    "url": "${GHOST_URL}",
                },
                "volumes": ["ghost-content:/var/lib/ghost/content"],
                "depends_on": ["ghost-db"],
                "networks": ["homelab"],
            },
            "ghost-db": {
                "image": "mysql:8.0",
                "container_name": "ghost-db",
                "restart": "unless-stopped",
                "environment": {
                    "MYSQL_ROOT_PASSWORD": "${GHOST_DB_ROOT_PASSWORD}",
                    "MYSQL_USER": "ghost",
                    "MYSQL_PASSWORD": "${GHOST_DB_PASSWORD}",
                    "MYSQL_DATABASE": "ghost",
                },
                "volumes": ["ghost-db:/var/lib/mysql"],
                "networks": ["homelab"],
            },
        },
        "volumes": {"ghost-content": None, "ghost-db": None},
    },

    # -------------------------------------------------------------------------
    # COMMUNICATION
    # -------------------------------------------------------------------------
    "ntfy": {
        "name": "ntfy",
        "description": "Push notifications to your phone from scripts, alerts, or other apps",
        "category": "Communication",
        "port": 8095,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Mobile app (iOS/Android): Install ntfy → Settings → Default server → http://{SERVER_IP}:8095",
            "Subscribe or publish from any device: http://{SERVER_IP}:8095",
            "Send a notification from a script: curl -d 'hello' http://{SERVER_IP}:8095/your-topic",
        ],
        "services": {
            "ntfy": {
                "image": "binwiederhier/ntfy:latest",
                "container_name": "ntfy",
                "restart": "unless-stopped",
                "command": "serve",
                "ports": ["8095:80"],
                "volumes": [
                    "ntfy-cache:/var/cache/ntfy",
                    "ntfy-etc:/etc/ntfy",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"ntfy-cache": None, "ntfy-etc": None},
    },

    "matrix": {
        "name": "Matrix (Synapse + Element)",
        "description": "Private encrypted messaging — self-hosted Signal/WhatsApp alternative",
        "category": "Communication",
        "port": 8880,
        "url_path": "",
        "watchtower_exclude": False,
        # Auto-secret: MATRIX_REGISTRATION_SECRET
        "connect": [
            "Element web UI is at http://{SERVER_IP}:8880 — use this to create your account first",
            "Element mobile (iOS/Android): Add account → Other → Homeserver: http://{SERVER_IP}:8448",
            "Any Matrix client: set homeserver to http://{SERVER_IP}:8448",
        ],
        "guided_prompts": [
            {
                "key": "MATRIX_SERVER_NAME",
                "label": "Matrix server name (e.g. matrix.home.local)",
                "default": "matrix.local",
            },
        ],
        "side_files": {
            "element-config.json": (
                '{\n'
                '  "default_server_config": {\n'
                '    "m.homeserver": {\n'
                '      "base_url": "http://synapse:8448",\n'
                '      "server_name": "{MATRIX_SERVER_NAME}"\n'
                '    }\n'
                '  }\n'
                '}\n'
            ),
        },
        "services": {
            "synapse-init": {
                # Generates homeserver.yaml on first boot (idempotent — skips if file exists).
                "image": "matrixdotorg/synapse:latest",
                "container_name": "synapse-init",
                "command": "generate",
                "restart": "no",
                "environment": {
                    "SYNAPSE_SERVER_NAME": "${MATRIX_SERVER_NAME}",
                    "SYNAPSE_REPORT_STATS": "no",
                },
                "volumes": ["synapse-data:/data"],
                "networks": ["homelab"],
            },
            "synapse": {
                "image": "matrixdotorg/synapse:latest",
                "container_name": "synapse",
                "restart": "unless-stopped",
                "ports": ["8448:8448"],
                "environment": {
                    "SYNAPSE_SERVER_NAME": "${MATRIX_SERVER_NAME}",
                    "SYNAPSE_REPORT_STATS": "no",
                    "SYNAPSE_REGISTRATION_SHARED_SECRET": "${MATRIX_REGISTRATION_SECRET}",
                },
                "volumes": ["synapse-data:/data"],
                "depends_on": {
                    "synapse-init": {"condition": "service_completed_successfully"},
                },
                "networks": ["homelab"],
            },
            "element": {
                "image": "vectorim/element-web:latest",
                "container_name": "element",
                "restart": "unless-stopped",
                "ports": ["8880:80"],
                "volumes": ["./element-config.json:/app/config.json:ro"],
                "networks": ["homelab"],
            },
        },
        "volumes": {"synapse-data": None},
    },

    "mattermost": {
        "name": "Mattermost",
        "description": "Slack alternative — team messaging, channels, file sharing",
        "category": "Communication",
        "port": 8065,
        "url_path": "",
        "watchtower_exclude": False,
        # Auto-secret: MATTERMOST_DB_PASSWORD
        "connect": [
            "Desktop app: Add server → http://{SERVER_IP}:8065",
            "Mobile app (iOS/Android): Install Mattermost → Add server → http://{SERVER_IP}:8065",
        ],
        "services": {
            "mattermost": {
                "image": "mattermost/mattermost-team-edition:latest",
                "container_name": "mattermost",
                "restart": "unless-stopped",
                "ports": ["8065:8065"],
                "environment": {
                    "MM_SQLSETTINGS_DRIVERNAME": "postgres",
                    "MM_SQLSETTINGS_DATASOURCE": "postgres://mattermost:${MATTERMOST_DB_PASSWORD}@mattermost-db:5432/mattermost?sslmode=disable&connect_timeout=10",
                    "MM_SERVICESETTINGS_SITEURL": "http://${SERVER_IP}:8065",
                },
                "volumes": [
                    "mattermost-data:/mattermost/data",
                    "mattermost-logs:/mattermost/logs",
                    "mattermost-config:/mattermost/config",
                    "mattermost-plugins:/mattermost/plugins",
                ],
                "depends_on": ["mattermost-db"],
                "networks": ["homelab"],
            },
            "mattermost-db": {
                "image": "postgres:15-alpine",
                "container_name": "mattermost-db",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_DB": "mattermost",
                    "POSTGRES_USER": "mattermost",
                    "POSTGRES_PASSWORD": "${MATTERMOST_DB_PASSWORD}",
                },
                "volumes": ["mattermost-db:/var/lib/postgresql/data"],
                "networks": ["homelab"],
            },
        },
        "volumes": {
            "mattermost-data": None,
            "mattermost-logs": None,
            "mattermost-config": None,
            "mattermost-plugins": None,
            "mattermost-db": None,
        },
    },

    # -------------------------------------------------------------------------
    # MONITORING
    # -------------------------------------------------------------------------
    "uptime-kuma": {
        "name": "Uptime Kuma",
        "description": "Self-hosted uptime monitoring with status page and alerts",
        "category": "Monitoring",
        "port": 3001,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:3001 — create your admin account on first visit",
            "Add a monitor: New Monitor > HTTP(s) > paste any of the URLs from this guide",
            "Set up notifications: Settings > Notifications > add Telegram, email, or ntfy",
        ],
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

    "dozzle": {
        "name": "Dozzle",
        "description": "Real-time container log browser — no more SSH to read logs",
        "category": "Monitoring",
        "port": 8888,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:8888 — no login required, all container logs visible immediately",
        ],
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

    "beszel": {
        "name": "Beszel",
        "description": "Lightweight server metrics dashboard — CPU, RAM, disk, network over time",
        "category": "Monitoring",
        "port": 8090,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:8090 — create your admin account on first visit",
            "To monitor other machines: add a system in the UI, then install the beszel-agent on that machine",
        ],
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

    "changedetection": {
        "name": "Changedetection.io",
        "description": "Get alerts when any webpage changes — prices, job postings, availability",
        "category": "Monitoring",
        "port": 5000,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:5000 — no login required by default",
            "Add a watch: paste any URL, set check interval, add notification (email, ntfy, etc.)",
        ],
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

    "scrutiny": {
        "name": "Scrutiny",
        "description": "Hard drive health monitoring (S.M.A.R.T.) — know before a drive dies",
        "category": "Monitoring",
        "port": 8083,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:8083 — drive health data appears automatically after startup",
            "Find your drives: run 'lsblk' on your server to list device paths before setup",
        ],
        "guided_prompts": [
            {
                "key": "SCRUTINY_DRIVES",
                "label": "Drive paths to monitor — comma-separated (e.g. /dev/sda  or  /dev/sda,/dev/nvme0n1)",
                "default": "/dev/sda",
            },
        ],
        "services": {
            "scrutiny": {
                "image": "ghcr.io/analogj/scrutiny:master-omnibus",
                "container_name": "scrutiny",
                "restart": "unless-stopped",
                "ports": ["8083:8080"],
                "cap_add": ["SYS_RAWIO", "SYS_ADMIN"],
                "devices": "__SCRUTINY_DRIVES__",
                "volumes": [
                    "/run/udev:/run/udev:ro",
                    "scrutiny-config:/opt/scrutiny/config",
                    "scrutiny-influx:/opt/scrutiny/influxdb",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {"scrutiny-config": None, "scrutiny-influx": None},
    },

    "grafana": {
        "name": "Grafana + Prometheus",
        "description": "Metrics dashboards (Grafana) + data collection (Prometheus) — visualize anything",
        "category": "Monitoring",
        "port": 3002,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Grafana: http://{SERVER_IP}:3002 — login: admin / see credentials panel above",
            "Add Prometheus data source: Connections > Data Sources > Prometheus > URL: http://prometheus:9090",
            "Import a dashboard: Dashboards > Import > enter ID 1860 for Node Exporter Full",
        ],
        # Auto-secret: GRAFANA_ADMIN_PASSWORD
        "side_files": {
            "prometheus.yml": (
                "global:\n"
                "  scrape_interval: 15s\n"
                "\n"
                "scrape_configs:\n"
                "  - job_name: prometheus\n"
                "    static_configs:\n"
                "      - targets: ['prometheus:9090']\n"
            ),
        },
        "services": {
            "grafana": {
                "image": "grafana/grafana:latest",
                "container_name": "grafana",
                "restart": "unless-stopped",
                "ports": ["3002:3000"],
                "environment": {
                    "GF_SECURITY_ADMIN_PASSWORD": "${GRAFANA_ADMIN_PASSWORD}",
                    "GF_USERS_ALLOW_SIGN_UP": "false",
                },
                "volumes": ["grafana-data:/var/lib/grafana"],
                "networks": ["homelab"],
            },
            "prometheus": {
                "image": "prom/prometheus:latest",
                "container_name": "prometheus",
                "restart": "unless-stopped",
                "ports": ["9090:9090"],
                "volumes": [
                    "prometheus-data:/prometheus",
                    "./prometheus.yml:/etc/prometheus/prometheus.yml:ro",
                ],
                "command": [
                    "--config.file=/etc/prometheus/prometheus.yml",
                    "--storage.tsdb.path=/prometheus",
                ],
                "networks": ["homelab"],
            },
        },
        "volumes": {"grafana-data": None, "prometheus-data": None},
    },

    "netdata": {
        "name": "Netdata",
        "description": "Real-time system metrics — CPU, RAM, disk, network, per-process, zero config",
        "category": "Monitoring",
        "port": 19999,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:19999 — metrics appear immediately, no configuration needed",
        ],
        # network_mode: host — no "networks" key for this service
        "services": {
            "netdata": {
                "image": "netdata/netdata:latest",
                "container_name": "netdata",
                "restart": "unless-stopped",
                "network_mode": "host",
                "pid": "host",
                "cap_add": ["SYS_PTRACE", "SYS_ADMIN"],
                "security_opt": ["apparmor:unconfined"],
                "volumes": [
                    "netdata-config:/etc/netdata",
                    "netdata-lib:/var/lib/netdata",
                    "netdata-cache:/var/cache/netdata",
                    "/etc/passwd:/host/etc/passwd:ro",
                    "/etc/group:/host/etc/group:ro",
                    "/proc:/host/proc:ro",
                    "/sys:/host/sys:ro",
                    "/etc/os-release:/host/etc/os-release:ro",
                    "/var/run/docker.sock:/var/run/docker.sock:ro",
                ],
            }
        },
        "volumes": {
            "netdata-config": None,
            "netdata-lib": None,
            "netdata-cache": None,
        },
    },

    "healthchecks": {
        "name": "Healthchecks",
        "description": "Cron job monitor — alerts you when a backup or scheduled task didn't run",
        "category": "Monitoring",
        "port": 8020,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:8020 — create an account on first visit",
            "Create a check, then add 'curl -fsS http://{SERVER_IP}:8020/ping/<uuid>' to your cron job",
        ],
        # Auto-secret: HEALTHCHECKS_SECRET_KEY
        "services": {
            "healthchecks": {
                "image": "healthchecks/healthchecks:latest",
                "container_name": "healthchecks",
                "restart": "unless-stopped",
                "ports": ["8020:8000"],
                "environment": {
                    "SECRET_KEY": "${HEALTHCHECKS_SECRET_KEY}",
                    "ALLOWED_HOSTS": "${SERVER_IP}",
                    "DEBUG": "False",
                },
                "volumes": ["healthchecks-data:/data"],
                "networks": ["homelab"],
            }
        },
        "volumes": {"healthchecks-data": None},
    },

    # -------------------------------------------------------------------------
    # MANAGEMENT
    # -------------------------------------------------------------------------
    "portainer": {
        "name": "Portainer",
        "description": "Visual Docker management dashboard — deploy, inspect, manage containers",
        "category": "Management",
        "port": 9000,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Open http://{SERVER_IP}:9000 — create your admin account on first visit",
            "Select 'Get Started' to manage the local Docker environment",
        ],
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

    "homepage": {
        "name": "Homepage",
        "description": "App launcher dashboard with live service status tiles — your homelab front door",
        "category": "Management",
        "port": 3000,
        "url_path": "",
        "watchtower_exclude": False,
        "connect": [
            "Bookmark http://{SERVER_IP}:3000 — this is your homelab home page",
            "All your selected apps are pre-configured as tiles — edit ~/homelab-starter/homepage-config/services.yaml to customize",
        ],
        "services": {
            "homepage": {
                "image": "ghcr.io/gethomepage/homepage:latest",
                "container_name": "homepage",
                "restart": "unless-stopped",
                "ports": ["3000:3000"],
                "volumes": [
                    "./homepage-config:/app/config",
                    "/var/run/docker.sock:/var/run/docker.sock",
                ],
                "networks": ["homelab"],
            }
        },
        "volumes": {},
    },

    # -------------------------------------------------------------------------
    # MAINTENANCE
    # -------------------------------------------------------------------------
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
}


# ---------------------------------------------------------------------------
# Category index — display order within each category is intentional
# ---------------------------------------------------------------------------
CATEGORIES: dict[str, list[str]] = {
    "Your Digital Life": ["vaultwarden", "actual", "nextcloud", "syncthing", "baikal", "nas"],
    "Media": ["jellyfin", "plex", "immich", "navidrome", "kavita", "audiobookshelf"],
    "Media Automation": ["sonarr", "radarr", "prowlarr", "qbittorrent", "jellyseerr", "bazarr"],
    "AI": ["ai"],
    "Smart Home": ["homeassistant", "grocy", "mealie"],
    "Networking": ["caddy", "duckdns", "tailscale", "pihole", "adguardhome", "librespeed"],
    "Security": ["crowdsec", "authentik"],
    "Documents": ["paperless", "stirling-pdf", "archivebox"],
    "Productivity": ["n8n", "gitea", "bookstack", "vikunja", "planka", "miniflux", "hoarder", "ghost"],
    "Communication": ["matrix", "mattermost", "ntfy"],
    "Monitoring": ["uptime-kuma", "dozzle", "beszel", "changedetection", "scrutiny", "grafana", "netdata", "healthchecks"],
    "Management": ["portainer", "homepage"],
    "Maintenance": ["watchtower", "autoheal"],
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

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
