"""Tests for docker_check — install offer logic."""

from unittest.mock import patch, MagicMock


def test_check_passes_when_docker_and_compose_present():
    with patch("shutil.which", return_value="/usr/bin/docker"), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        from homelab.docker_check import check
        check()  # should not raise or exit



def test_compose_plugin_install_attempted_when_missing():
    with patch("shutil.which", side_effect=lambda cmd: "/usr/bin/docker" if cmd == "docker" else (None if cmd == "apt-get" else None)), \
         patch("subprocess.run") as mock_run:
        # First call: docker compose version → fails; second: apt-get install → succeeds
        mock_run.side_effect = [
            MagicMock(returncode=1),   # docker compose version
            MagicMock(returncode=0),   # apt-get install
            MagicMock(returncode=0),   # docker compose version (re-check after install)
        ]
        from homelab import docker_check
        import importlib
        importlib.reload(docker_check)
        with patch("shutil.which", side_effect=lambda cmd: "/usr/bin/docker" if cmd == "docker" else ("/usr/bin/apt-get" if cmd == "apt-get" else None)):
            with patch("subprocess.run") as mock_run2:
                mock_run2.side_effect = [
                    MagicMock(returncode=1),  # compose version check
                    MagicMock(returncode=0),  # apt-get install
                ]
                docker_check._ensure_compose_plugin()
