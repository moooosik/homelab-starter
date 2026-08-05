import shutil
import subprocess
import sys

from rich.console import Console

console = Console()


def check() -> None:
    """Exit with a helpful message if Docker or docker compose is missing."""
    if not shutil.which("docker"):
        console.print("[bold red]Docker is not installed.[/bold red]")
        console.print("Install it with:  curl -fsSL https://get.docker.com | sh")
        sys.exit(1)

    result = subprocess.run(
        ["docker", "compose", "version"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        console.print("[bold red]docker compose plugin not found.[/bold red]")
        console.print("Update Docker Desktop or install the compose plugin:")
        console.print("  apt install docker-compose-plugin")
        sys.exit(1)
