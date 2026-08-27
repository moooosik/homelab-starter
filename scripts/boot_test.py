#!/usr/bin/env python3
"""Actually start a set of apps and verify the containers come up healthy.

The rest of the suite proves the generated compose file is *valid*. Nothing
proved it *works* — that Postgres accepts the healthcheck, that a dependent
service waits correctly, that an image runs at all. This closes that gap.

`docker compose up --wait` blocks until every service is healthy (or running,
for services without a healthcheck) and exits non-zero otherwise, so it is the
whole assertion.

Usage:
    python scripts/boot_test.py                  # default representative set
    python scripts/boot_test.py ghost miniflux   # specific apps
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from homelab.compose import build, write_files  # noqa: E402

# Chosen to exercise the parts most likely to break, while staying inside a
# CI runner's disk budget:
#   miniflux -> postgres healthcheck + depends_on: service_healthy
#   ghost    -> mysql healthcheck + depends_on: service_healthy
#   dozzle   -> host docker.sock mount
#   memos    -> SQLite-backed single container
#   it-tools -> static single container, no volumes
DEFAULT_APPS = ["memos", "it-tools", "dozzle", "miniflux", "ghost"]

PULL_TIMEOUT = 900
BOOT_TIMEOUT = 300


def _run(cmd: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, timeout=timeout, text=True, capture_output=True)


def _report_failure(deploy_dir: Path) -> None:
    """Print enough to diagnose without re-running locally."""
    ps = _run(["docker", "compose", "ps", "--all"], deploy_dir, 120)
    print("\n--- docker compose ps ---")
    print(ps.stdout or ps.stderr)

    unhealthy = _run(
        ["docker", "compose", "ps", "--all", "--format", "{{.Service}} {{.State}} {{.Health}}"],
        deploy_dir,
        120,
    )
    for line in unhealthy.stdout.splitlines():
        parts = line.split()
        if not parts:
            continue
        service, state = parts[0], (parts[1] if len(parts) > 1 else "")
        health = parts[2] if len(parts) > 2 else ""
        if state == "running" and health in ("", "healthy"):
            continue
        print(f"\n--- logs: {service} ({state} {health}) ---")
        logs = _run(["docker", "compose", "logs", "--tail", "60", service], deploy_dir, 120)
        print(logs.stdout or logs.stderr)


def boot(app_ids: list[str]) -> int:
    print(f"Booting {len(app_ids)} app(s): {', '.join(app_ids)}\n")
    compose, env = build(app_ids, "127.0.0.1", {})

    tmp = Path(tempfile.mkdtemp(prefix="homelab-boot-"))
    try:
        write_files(compose, env, tmp, app_ids)
        services = sorted(compose["services"])
        print(f"{len(services)} service(s): {', '.join(services)}\n")

        print("Pulling images...")
        pull = _run(["docker", "compose", "pull", "--quiet"], tmp, PULL_TIMEOUT)
        if pull.returncode != 0:
            print("docker compose pull failed:\n" + (pull.stderr or pull.stdout))
            return 1

        print(f"Starting, waiting up to {BOOT_TIMEOUT}s for healthy...")
        up = _run(
            ["docker", "compose", "up", "--detach", "--wait", "--wait-timeout", str(BOOT_TIMEOUT)],
            tmp,
            BOOT_TIMEOUT + 120,
        )
        if up.returncode != 0:
            print(f"\nFAILED: services did not become healthy.\n{up.stderr or up.stdout}")
            _report_failure(tmp)
            return 1

        print(f"\nAll {len(services)} service(s) started and healthy.")
        return 0
    finally:
        print("\nTearing down...")
        _run(["docker", "compose", "down", "--volumes", "--remove-orphans"], tmp, 300)
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apps", nargs="*", default=None, help="app ids (default: representative set)")
    args = parser.parse_args()

    if shutil.which("docker") is None:
        print("docker not found on PATH")
        return 1

    return boot(args.apps or DEFAULT_APPS)


if __name__ == "__main__":
    sys.exit(main())
