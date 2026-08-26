#!/usr/bin/env python3
"""Verify every image tag referenced in homelab/apps.py actually exists.

A typo'd tag ships silently and only fails when a user runs `docker compose up`.
This walks APPS, resolves each unique image reference, and checks the tag against
its registry.

Two strategies, because Docker Hub's registry endpoint counts against the
anonymous pull-rate limit (shared across GitHub runner IPs) while its Hub API
does not:

  docker.io  -> hub.docker.com/v2 catalogue API
  everything -> OCI registry v2 manifest HEAD, with anonymous bearer token
  else          (ghcr.io, lscr.io, quay.io, ...)

Exits non-zero if any tag cannot be resolved. Usage:

    python scripts/verify_image_tags.py [--verbose]
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from homelab.apps import APPS  # noqa: E402

USER_AGENT = "homelab-starter-tag-check/1.0"
TIMEOUT = 30
MANIFEST_ACCEPT = ", ".join(
    (
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    )
)


def parse_image(ref: str) -> tuple[str, str, str]:
    """Split an image reference into (registry, repository, tag).

    Follows Docker's rule: the first path component is a registry host only if
    it contains a '.' or ':', or is exactly 'localhost'. Otherwise the whole
    reference belongs to Docker Hub, and a single-component name is an official
    image living under 'library/'.
    """
    ref = ref.split("@", 1)[0]  # drop any digest
    first, _, rest = ref.partition("/")
    if rest and ("." in first or ":" in first or first == "localhost"):
        registry, remainder = first, rest
    else:
        registry, remainder = "docker.io", ref

    # A ':' only starts a tag if it is in the final path component.
    if ":" in remainder.rsplit("/", 1)[-1]:
        repo, _, tag = remainder.rpartition(":")
    else:
        repo, tag = remainder, "latest"

    if registry == "docker.io" and "/" not in repo:
        repo = f"library/{repo}"
    return registry, repo, tag


def _request(url: str, headers: dict[str, str], method: str = "GET") -> int:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **headers}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


def _check_docker_hub(repo: str, tag: str) -> bool:
    url = f"https://hub.docker.com/v2/repositories/{repo}/tags/{urllib.parse.quote(tag)}"
    return _request(url, {}) == 200


def _bearer_token(registry: str, repo: str) -> str | None:
    """Fetch an anonymous pull token, discovering the auth realm via a 401."""
    probe = urllib.request.Request(
        f"https://{registry}/v2/", headers={"User-Agent": USER_AGENT}, method="GET"
    )
    try:
        urllib.request.urlopen(probe, timeout=TIMEOUT)
        return None  # registry allows anonymous access outright
    except urllib.error.HTTPError as exc:
        if exc.code != 401:
            return None
        challenge = exc.headers.get("WWW-Authenticate", "")

    realm = re.search(r'realm="([^"]+)"', challenge)
    if not realm:
        return None
    service = re.search(r'service="([^"]+)"', challenge)

    params = {"scope": f"repository:{repo}:pull"}
    if service:
        params["service"] = service.group(1)
    token_url = f"{realm.group(1)}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(token_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            import json

            body = json.loads(resp.read())
        return body.get("token") or body.get("access_token")
    except (urllib.error.URLError, ValueError):
        return None


def _check_registry_v2(registry: str, repo: str, tag: str) -> bool:
    url = f"https://{registry}/v2/{repo}/manifests/{urllib.parse.quote(tag)}"
    headers = {"Accept": MANIFEST_ACCEPT}
    status = _request(url, headers, method="HEAD")
    if status == 200:
        return True
    if status in (401, 403):
        token = _bearer_token(registry, repo)
        if token:
            headers["Authorization"] = f"Bearer {token}"
            status = _request(url, headers, method="HEAD")
    return status == 200


def check_image(ref: str) -> tuple[str, bool, str]:
    registry, repo, tag = parse_image(ref)
    try:
        ok = _check_docker_hub(repo, tag) if registry == "docker.io" else _check_registry_v2(registry, repo, tag)
    except urllib.error.URLError as exc:
        return ref, False, f"network error: {exc.reason}"
    return ref, ok, f"{registry}/{repo}:{tag}"


def collect_images() -> dict[str, list[str]]:
    """Map each unique image reference to the app ids that use it."""
    images: dict[str, list[str]] = {}
    for app_id, app in APPS.items():
        for service in app["services"].values():
            image = service.get("image")
            if image:
                images.setdefault(image, []).append(app_id)
    return images


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="print every image, not just failures")
    args = parser.parse_args()

    images = collect_images()
    print(f"Checking {len(images)} unique image tags across {len(APPS)} apps...\n")

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(check_image, sorted(images)))

    failures = [(ref, detail) for ref, ok, detail in results if not ok]

    if args.verbose:
        for ref, ok, detail in results:
            print(f"  {'ok  ' if ok else 'FAIL'}  {ref}")
        print()

    if failures:
        print(f"{len(failures)} image tag(s) could not be resolved:\n")
        for ref, detail in failures:
            used_by = ", ".join(images[ref])
            print(f"  {ref}\n      resolved as: {detail}\n      used by:     {used_by}\n")
        return 1

    print(f"All {len(images)} image tags resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
