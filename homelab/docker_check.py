import os
import shlex
import shutil
import subprocess
import sys

import questionary
from rich.console import Console

console = Console()


def check() -> None:
    """Ensure Docker + docker compose are installed. Offer to install if missing."""
    if not shutil.which("docker"):
        _offer_install_docker()

    _ensure_compose_plugin()


def _offer_install_docker() -> None:
    console.print("[yellow]Docker is not installed on this machine.[/yellow]")
    install = questionary.confirm(
        "Install Docker now using the official get.docker.com script?",
        default=True,
    ).ask()

    if not install:
        console.print(
            "Install Docker manually and re-run homelab-starter:\n"
            "  curl -fsSL https://get.docker.com | sh"
        )
        sys.exit(0)

    console.print("\n[bold cyan]Installing Docker...[/bold cyan]")
    result = subprocess.run(
        ["bash", "-c", "curl -fsSL https://get.docker.com | sh"],
        check=False,
    )
    if result.returncode != 0:
        console.print("[bold red]Docker installation failed.[/bold red] Check the output above.")
        sys.exit(1)

    # Add current user to the docker group so they don't need sudo
    username = os.environ.get("USER") or os.environ.get("LOGNAME") or ""
    if username:
        subprocess.run(["usermod", "-aG", "docker", username], check=False)
        console.print(
            f"\n[green]Added [bold]{username}[/bold] to the docker group.[/green]\n"
            "Group membership activates in this session via [bold]sg docker[/bold].\n"
        )
        # Re-exec this process inside the docker group so docker commands work immediately
        # without requiring the user to log out and back in.
        if os.getuid() != 0:
            os.execvp("sg", ["sg", "docker", "-c", shlex.join(sys.argv)])

    console.print("[green]Docker installed.[/green]\n")


def _ensure_compose_plugin() -> None:
    result = subprocess.run(
        ["docker", "compose", "version"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return

    console.print("[yellow]docker compose plugin not found. Installing...[/yellow]")

    # Try apt first (Debian/Ubuntu), then dnf (Fedora/RHEL)
    if shutil.which("apt-get"):
        r = subprocess.run(
            ["apt-get", "install", "-y", "docker-compose-plugin"],
            check=False,
        )
    elif shutil.which("dnf"):
        r = subprocess.run(
            ["dnf", "install", "-y", "docker-compose-plugin"],
            check=False,
        )
    else:
        console.print(
            "[bold red]Could not install docker-compose-plugin automatically.[/bold red]\n"
            "Install it manually: https://docs.docker.com/compose/install/"
        )
        sys.exit(1)

    if r.returncode != 0:
        console.print("[bold red]docker compose plugin installation failed.[/bold red]")
        sys.exit(1)

    console.print("[green]docker compose plugin installed.[/green]\n")
