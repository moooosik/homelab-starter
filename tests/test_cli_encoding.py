"""The CLI must not crash when stdout uses a legacy codepage.

Windows consoles and redirected output frequently default to cp1252, which
cannot encode the box-drawing characters in the banner or in Rich's panel and
table borders. `--list` is documented as usable on any machine, so it has to
survive that.

cp1252 is a stdlib codec on every platform, so these run on Linux CI too.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
INVOKE_LIST = "from homelab.cli import main; main(['--list'], standalone_mode=False)"


def _run_with_encoding(encoding: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", INVOKE_LIST],
        capture_output=True,
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONIOENCODING": encoding},
        timeout=120,
    )


@pytest.mark.parametrize("encoding", ["cp1252", "ascii", "utf-8"])
def test_list_survives_narrow_stdout_encoding(encoding: str) -> None:
    result = _run_with_encoding(encoding)
    assert result.returncode == 0, (
        f"--list crashed with PYTHONIOENCODING={encoding}:\n"
        + result.stderr.decode("utf-8", errors="replace")
    )


def test_list_still_prints_the_catalog_on_a_narrow_encoding() -> None:
    """Surviving is not enough — the catalog itself must still come through."""
    result = _run_with_encoding("cp1252")
    out = result.stdout.decode("utf-8", errors="replace")
    for expected in ("Jellyfin", "Vaultwarden", "SearXNG"):
        assert expected in out, f"{expected!r} missing from --list output"
