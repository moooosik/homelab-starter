"""Main interactive CLI flow for homelab-starter."""

import re
import subprocess
import sys
from pathlib import Path

import click
import yaml
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from homelab import apps as app_catalog
from homelab import compose as compose_builder
from homelab.docker_check import check as check_docker
from homelab.network import get_local_ip

console = Console()

DEPLOY_DIR = Path.home() / "homelab-starter"

BANNER = """
██╗  ██╗ ██████╗ ███╗   ███╗███████╗██╗      █████╗ ██████╗
██║  ██║██╔═══██╗████╗ ████║██╔════╝██║     ██╔══██╗██╔══██╗
███████║██║   ██║██╔████╔██║█████╗  ██║     ███████║██████╔╝
██╔══██║██║   ██║██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██╔══██╗
██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗███████╗██║  ██║██████╔╝
╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝
              S T A R T E R
"""

# Windows consoles and redirected output often default to a legacy codepage
# (commonly cp1252) that cannot encode the box-drawing characters above. Rich
# already downgrades its own borders, but the banner is our content, so we
# carry an ASCII rendering for those terminals.
ASCII_BANNER = r"""
 _  _  ___  __  __ ___ _      _   ___
| || |/ _ \|  \/  | __| |    /_\ | _ )
| __ | (_) | |\/| | _|| |__ / _ \| _ \
|_||_|\___/|_|  |_|___|____/_/ \_\___/
              S T A R T E R
"""


def _supports(text: str, stream) -> bool:
    """Can this stream's encoding represent every character in text?"""
    encoding = getattr(stream, "encoding", None) or "utf-8"
    try:
        text.encode(encoding)
    except (UnicodeEncodeError, LookupError):
        return False
    return True


def _relax_output_encoding() -> None:
    """Degrade unencodable characters instead of aborting the run.

    A safety net for anything beyond the banner — app descriptions and prompt
    hints also carry non-ASCII punctuation.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(errors="replace")
        except (OSError, ValueError):
            pass


@click.command()
@click.option("--dry-run", is_flag=True, help="Generate files but do not deploy.")
@click.option("--list", "list_apps", is_flag=True, help="List all available apps and exit.")
@click.option("--update", "do_update", is_flag=True, help="Re-generate files from existing .env without re-running the installer.")
def main(dry_run: bool, list_apps: bool, do_update: bool) -> None:
    _relax_output_encoding()
    banner = BANNER if _supports(BANNER, sys.stdout) else ASCII_BANNER
    console.print(Panel(banner.strip(), border_style="cyan", expand=False))

    if list_apps:
        _print_app_catalog()
        return

    if do_update:
        _run_update(dry_run)
        return

    console.print(
        "Interactive homelab bootstrap. Space = toggle, Enter = confirm.\n",
        style="dim",
    )

    check_docker()

    server_ip = get_local_ip()
    console.print(f"[green]Server IP detected:[/green] [bold]{server_ip}[/bold]\n")

    config_depth = questionary.select(
        "Configuration depth:",
        choices=[
            questionary.Choice("basic    — defaults for everything, just pick your apps", value="basic"),
            questionary.Choice("guided   — prompts for key options (passwords, paths)", value="guided"),
            questionary.Choice("advanced — all options exposed", value="advanced"),
        ],
        default="guided",
    ).ask()
    if config_depth is None:
        sys.exit(0)

    # Step 1: pick categories
    category_choices = [
        questionary.Choice(
            title=f"{cat}  ({len(app_catalog.CATEGORIES[cat])} apps)",
            value=cat,
        )
        for cat in app_catalog.CATEGORIES
    ]
    selected_categories: list[str] = questionary.checkbox(
        "Which categories do you want?",
        choices=category_choices,
        instruction="(↑↓ navigate, space select, enter confirm)",
    ).ask()
    if selected_categories is None:
        sys.exit(0)

    if not selected_categories:
        console.print("[yellow]No categories selected. Nothing to deploy.[/yellow]")
        sys.exit(0)

    # Step 2: pick apps within each category
    selected_ids: list[str] = []
    for cat in selected_categories:
        app_ids_in_cat = app_catalog.CATEGORIES[cat]
        cat_choices = [
            questionary.Choice(
                title=f"{app_catalog.APPS[aid]['name']:<26} — {app_catalog.APPS[aid]['description']}",
                value=aid,
                checked=True,
            )
            for aid in app_ids_in_cat
        ]
        picked: list[str] = questionary.checkbox(
            f"{cat}:",
            choices=cat_choices,
            instruction="(space toggle, enter confirm)",
        ).ask()
        if picked is None:
            sys.exit(0)
        selected_ids.extend(picked)

    if not selected_ids:
        console.print("[yellow]No apps selected. Nothing to deploy.[/yellow]")
        sys.exit(0)

    # Watchtower — always include (silently)
    if "watchtower" not in selected_ids:
        selected_ids.append("watchtower")

    # Port conflict: Pi-hole and AdGuard Home both bind port 53
    if "pihole" in selected_ids and "adguardhome" in selected_ids:
        console.print(
            "\n[bold yellow]Port conflict:[/bold yellow] Pi-hole and AdGuard Home both use port 53.\n"
            "Only one DNS blocker can run at a time. Which one do you want to keep?\n"
        )
        dns_choice = questionary.select(
            "Keep which DNS blocker?",
            choices=[
                questionary.Choice("Pi-hole", value="pihole"),
                questionary.Choice("AdGuard Home", value="adguardhome"),
            ],
        ).ask()
        if dns_choice is None:
            sys.exit(0)
        selected_ids.remove("pihole" if dns_choice == "adguardhome" else "adguardhome")

    # Custom domain
    has_domain = questionary.confirm(
        "Do you have a custom domain pointed at this server?",
        default=False,
    ).ask()
    domain = ""
    if has_domain:
        domain = questionary.text("Your domain (e.g. home.example.com):").ask() or ""

    # Per-app config
    user_config: dict = {}
    if config_depth in ("guided", "advanced"):
        prompts = app_catalog.get_guided_prompts(selected_ids)
        if prompts:
            console.print("\n[bold]App configuration[/bold] (press Enter to use default):\n")
        for prompt in prompts:
            if prompt.get("secret"):
                answer = questionary.password(
                    f"  {prompt['label']} [{prompt.get('default', '')}]:",
                ).ask()
            else:
                answer = questionary.text(
                    f"  {prompt['label']}:",
                    default=prompt.get("default", ""),
                ).ask()
            if answer is None:
                sys.exit(0)
            if answer:
                user_config[prompt["key"]] = answer

    # Build compose
    compose_dict, env_dict = compose_builder.build(selected_ids, server_ip, user_config)

    console.print(f"\n[dim]Writing files to {DEPLOY_DIR}...[/dim]")

    # Generate Caddyfile if Caddy selected
    if "caddy" in selected_ids:
        _write_caddyfile(selected_ids, domain or server_ip)

    # Generate Homepage services.yaml if Homepage selected
    if "homepage" in selected_ids:
        _write_homepage_services(selected_ids, server_ip)

    compose_builder.write_files(compose_dict, env_dict, DEPLOY_DIR, selected_ids)

    if dry_run:
        console.print(
            Panel(
                f"[bold]Dry run complete.[/bold]\n"
                f"Files written to [cyan]{DEPLOY_DIR}[/cyan]\n"
                f"Run [bold]docker compose up -d[/bold] in that directory to deploy.",
                border_style="yellow",
            )
        )
        _print_urls(selected_ids, server_ip, domain)
        _print_credentials(env_dict, selected_ids)
        _write_connect_guide(selected_ids, server_ip)
        return

    # Deploy
    console.print("\n[bold cyan]Deploying...[/bold cyan]\n")
    result = subprocess.run(
        ["docker", "compose", "up", "-d", "--pull", "always"],
        cwd=DEPLOY_DIR,
    )
    if result.returncode != 0:
        console.print("\n[bold red]Deploy failed.[/bold red] Check the output above.")
        console.print(f"You can retry manually:\n  cd {DEPLOY_DIR} && docker compose up -d")
        sys.exit(1)

    _print_urls(selected_ids, server_ip, domain)
    _print_credentials(env_dict, selected_ids)
    _write_connect_guide(selected_ids, server_ip)

    if has_domain and domain:
        _print_domain_instructions(domain, selected_ids)


def _run_update(dry_run: bool) -> None:
    """Re-generate docker-compose.yml and .env from the existing .env file."""
    env_path = DEPLOY_DIR / ".env"
    compose_path = DEPLOY_DIR / "docker-compose.yml"

    if not env_path.exists():
        console.print(
            "[bold red]No existing .env found.[/bold red] "
            f"Run [bold]homelab-starter[/bold] first to do an initial install.\n"
            f"Expected location: [cyan]{env_path}[/cyan]"
        )
        sys.exit(1)

    # Read existing .env to recover selected_ids and user_config
    user_config: dict = {}
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, _, value = line.partition("=")
            user_config[key.strip()] = value.strip()

    server_ip = user_config.get("SERVER_IP", get_local_ip())

    # Recover selected_ids from the existing compose file
    selected_ids: list[str] = []
    if compose_path.exists():
        import yaml as _yaml
        existing = _yaml.safe_load(compose_path.read_text()) or {}
        svc_names = set((existing.get("services") or {}).keys())
        for app_id, app in app_catalog.APPS.items():
            if svc_names & set(app["services"].keys()):
                selected_ids.append(app_id)
    else:
        console.print("[yellow]No existing docker-compose.yml found — rebuilding with all apps from .env.[/yellow]")

    console.print(f"[dim]Regenerating files for {len(selected_ids)} apps...[/dim]")

    compose_dict, env_dict = compose_builder.build(selected_ids, server_ip, user_config)

    if "caddy" in selected_ids:
        _write_caddyfile(selected_ids, server_ip)
    if "homepage" in selected_ids:
        _write_homepage_services(selected_ids, server_ip)

    compose_builder.write_files(compose_dict, env_dict, DEPLOY_DIR, selected_ids)

    if dry_run:
        console.print(
            Panel(
                f"[bold]Update dry run complete.[/bold]\n"
                f"Files written to [cyan]{DEPLOY_DIR}[/cyan]\n"
                f"Run [bold]docker compose up -d[/bold] in that directory to apply.",
                border_style="yellow",
            )
        )
        return

    console.print("\n[bold cyan]Applying update...[/bold cyan]\n")
    result = subprocess.run(
        ["docker", "compose", "up", "-d", "--pull", "always"],
        cwd=DEPLOY_DIR,
    )
    if result.returncode != 0:
        console.print("\n[bold red]Update failed.[/bold red] Check the output above.")
        sys.exit(1)

    console.print("\n[bold green]Update complete.[/bold green] All containers restarted with latest config.")


def _print_app_catalog() -> None:
    """Print all available apps grouped by category."""
    for cat, app_ids in app_catalog.CATEGORIES.items():
        table = Table(
            title=f"[bold]{cat}[/bold]",
            box=box.SIMPLE_HEAD,
            border_style="dim",
            show_header=True,
            header_style="bold dim",
        )
        table.add_column("App", style="bold", min_width=26)
        table.add_column("Port", justify="right", style="cyan", min_width=6)
        table.add_column("Description")
        for app_id in app_ids:
            app = app_catalog.APPS[app_id]
            port = str(app["port"]) if app.get("port") else "—"
            table.add_row(app["name"], port, app["description"])
        console.print(table)


def _write_caddyfile(selected_ids: list[str], host: str) -> None:
    """Generate a basic Caddyfile for selected apps."""
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    for app_id in selected_ids:
        if app_id == "caddy":
            continue
        app = app_catalog.APPS[app_id]
        port = app.get("port")
        if port is None:
            continue
        name = re.sub(r"[^a-z0-9]+", "-", app["name"].lower()).strip("-")
        lines.append(f"{name}.{host} {{")
        first_service = next(iter(app["services"]))
        svc = app["services"][first_service]
        if svc.get("network_mode") == "host":
            upstream = f"localhost:{port}"
        else:
            upstream = f"{first_service}:{port}"
        lines.append(f"    reverse_proxy {upstream}")
        lines.append("}")
        lines.append("")

    caddyfile_path = DEPLOY_DIR / "Caddyfile"
    with open(caddyfile_path, "w") as f:
        f.write("\n".join(lines))
    console.print(f"[dim]Caddyfile written to {caddyfile_path}[/dim]")


def _write_homepage_services(selected_ids: list[str], server_ip: str) -> None:
    """Generate Homepage services.yaml so the dashboard shows all selected apps."""
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    homepage_dir = DEPLOY_DIR / "homepage-config"
    homepage_dir.mkdir(exist_ok=True)

    skip = {"homepage", "watchtower", "autoheal", "caddy", "duckdns", "tailscale", "crowdsec"}
    by_category: dict[str, list[dict]] = {}

    for app_id in selected_ids:
        if app_id in skip:
            continue
        app = app_catalog.APPS[app_id]
        port = app.get("port")
        if not port:
            continue
        cat = app["category"]
        url_path = app.get("url_path", "")
        entry = {app["name"]: {"href": f"http://{server_ip}:{port}{url_path}", "description": app["description"]}}
        by_category.setdefault(cat, []).append(entry)

    doc = [
        {cat: [{name: cfg for name, cfg in entry.items()} for entry in entries]}
        for cat, entries in by_category.items()
    ]

    services_path = homepage_dir / "services.yaml"
    services_path.write_text(yaml.dump(doc, default_flow_style=False, allow_unicode=True))
    console.print(f"[dim]Homepage services.yaml written to {services_path}[/dim]")


def _print_urls(selected_ids: list[str], server_ip: str, domain: str) -> None:
    console.print()
    table = Table(title="Services", box=box.ROUNDED, border_style="cyan", show_header=True)
    table.add_column("App", style="bold")
    table.add_column("URL", style="cyan")

    has_homepage = "homepage" in selected_ids

    for app_id in selected_ids:
        app = app_catalog.APPS[app_id]
        port = app.get("port")
        if port is None:
            continue
        url_path = app.get("url_path", "")
        url = f"http://{server_ip}:{port}{url_path}"
        table.add_row(app["name"], url)

    console.print(table)
    console.print()

    if has_homepage:
        homepage_url = f"http://{server_ip}:3000"
        console.print(
            Panel(
                f"[bold green]Dashboard:[/bold green]  [bold cyan]{homepage_url}[/bold cyan]\n\n"
                "Bookmark this — it's your homelab home page.",
                border_style="green",
                title="Homepage",
            )
        )
        console.print()

    console.print(
        "[bold green]Done![/bold green] All services are starting. "
        "It may take a minute for each UI to become available."
    )


def _print_credentials(env: dict, selected_ids: list[str]) -> None:
    """Print admin login credentials for apps that have auto-generated passwords."""
    # Maps app_id → (app display name, login username/email, env key for password)
    _ADMIN_LOGINS: list[tuple[str, str, str, str]] = [
        ("paperless",  "Paperless-ngx",  "admin",                "PAPERLESS_ADMIN_PASSWORD"),
        ("nextcloud",  "Nextcloud",       "admin",                "NEXTCLOUD_ADMIN_PASSWORD"),
        ("grafana",    "Grafana",         "admin",                "GRAFANA_ADMIN_PASSWORD"),
        ("bookstack",  "BookStack",       "admin@example.com",    "BOOKSTACK_ROOT_PASSWORD"),
        ("miniflux",   "Miniflux",        "admin",                "MINIFLUX_ADMIN_PASSWORD"),
        ("pihole",     "Pi-hole",         "(web UI login)",       "PIHOLE_PASSWORD"),
        ("nas",        "NAS (Samba)",     "homelab",              "NAS_PASSWORD"),
        ("flowise",    "Flowise",         env.get("FLOWISE_USERNAME") or "admin", "FLOWISE_PASSWORD"),
    ]

    rows = [
        (app_name, username, env[env_key])
        for app_id, app_name, username, env_key in _ADMIN_LOGINS
        if app_id in selected_ids and env_key in env
    ]

    lines: list[str] = [
        f"All passwords are saved in [bold cyan]{DEPLOY_DIR / '.env'}[/bold cyan]",
        "[dim]Keep that file private — it contains every secret.[/dim]",
    ]

    if rows:
        lines.append("")
        lines.append("[bold]Admin login credentials:[/bold]")
        for app_name, username, password in rows:
            lines.append(f"  [bold]{app_name:<18}[/bold] {username}  /  [yellow]{password}[/yellow]")

    if "nas" in selected_ids:
        lines.append("")
        lines.append(
            "  [bold]FileBrowser[/bold]          admin  /  [yellow]admin[/yellow]"
            "  [dim](change immediately at :8082 > Settings > User management)[/dim]"
        )

    if "authentik" in selected_ids:
        lines.append("")
        lines.append(
            "  [bold]Authentik[/bold]            check logs after first boot:\n"
            "                       [dim]docker logs authentik-worker | grep 'Generated admin password'[/dim]"
        )

    console.print()
    console.print(
        Panel(
            "\n".join(lines),
            title="[bold]Your credentials",
            border_style="yellow",
            expand=False,
        )
    )
    console.print()


def _write_connect_guide(selected_ids: list[str], server_ip: str) -> None:
    """Write CONNECT.md with per-app connection instructions for selected apps."""
    sections = []
    for app_id in selected_ids:
        app = app_catalog.APPS[app_id]
        steps = app.get("connect", [])
        if not steps:
            continue
        port = app.get("port")
        port_str = f"  •  port {port}" if port else ""
        sections.append(f"## {app['name']}{port_str}\n")
        for step in steps:
            sections.append(f"- {step.format(SERVER_IP=server_ip)}\n")
        sections.append("\n")

    if not sections:
        return

    guide = (
        "# Connection Guide\n\n"
        "How to connect phones, desktop apps, and clients to each service.\n"
        f"Your server IP: `{server_ip}`\n\n"
        "---\n\n"
        + "".join(sections)
    )

    guide_path = DEPLOY_DIR / "CONNECT.md"
    guide_path.write_text(guide)
    console.print(
        Panel(
            f"[bold]Connection guide[/bold] saved to [cyan]{guide_path}[/cyan]\n"
            "Open it whenever you need to connect a new phone or device.",
            border_style="dim",
            expand=False,
        )
    )


def _print_domain_instructions(domain: str, selected_ids: list[str]) -> None:
    console.print()
    console.print(
        Panel(
            f"""[bold]Custom domain setup for {domain}[/bold]

[bold cyan]1. Port forwarding[/bold cyan] (on your router):
   • Forward external port 80  → {get_local_ip()}:80
   • Forward external port 443 → {get_local_ip()}:443

[bold cyan]2. DNS[/bold cyan]:
   • Point {domain} (and *.{domain}) to your public IP

[bold cyan]3. CrowdSec[/bold cyan] (if installed — protects public-facing services):
   Install the bouncer on the Caddy container:
     docker exec crowdsec cscli bouncers add caddy-bouncer
     # Copy the API key and add to your Caddyfile or CrowdSec bouncer config

[bold cyan]4. Caddy[/bold cyan]:
   Edit {DEPLOY_DIR}/Caddyfile and replace the generated stubs with real subdomains.
   Then reload:
     docker exec caddy caddy reload --config /etc/caddy/Caddyfile
""",
            border_style="yellow",
            title="Custom domain",
        )
    )
