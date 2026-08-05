"""Main interactive CLI flow for homelab-starter."""

import subprocess
import sys
from pathlib import Path

import click
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


@click.command()
@click.option("--dry-run", is_flag=True, help="Generate files but do not deploy.")
def main(dry_run: bool) -> None:
    console.print(Panel(BANNER.strip(), border_style="cyan", expand=False))
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

    if has_domain and domain:
        _print_domain_instructions(domain, selected_ids)


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
        name = app["name"].lower().replace(" ", "-").replace("(", "").replace(")", "")
        lines.append(f"{name}.{host} {{")
        # Find the first service name for the upstream
        first_service = next(iter(app["services"]))
        lines.append(f"    reverse_proxy {first_service}:{port}")
        lines.append("}")
        lines.append("")

    caddyfile_path = DEPLOY_DIR / "Caddyfile"
    with open(caddyfile_path, "w") as f:
        f.write("\n".join(lines))
    console.print(f"[dim]Caddyfile written to {caddyfile_path}[/dim]")


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
