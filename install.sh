#!/usr/bin/env bash
# homelab-starter installer
# Usage: curl -fsSL https://raw.githubusercontent.com/moooosik/homelab-starter/main/install.sh | bash
set -e

REPO="https://github.com/moooosik/homelab-starter.git"
INSTALL_DIR="/tmp/homelab-starter-install"

echo ""
echo "  homelab-starter — Docker Compose homelab bootstrap"
echo "  ---------------------------------------------------"
echo ""

# Python 3.11+
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is required. Install it with:"
    echo "  sudo apt install python3 python3-pip"
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED="3.11"
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    :
else
    echo "Python 3.11+ required (found $PY_VER)."
    echo "Install with: sudo apt install python3.11"
    exit 1
fi

# Install via pip (prefer pipx for isolation)
PINNED_REF="v0.1.1"
if command -v pipx &>/dev/null; then
    pipx install "git+${REPO}@${PINNED_REF}" --force --quiet
    homelab-starter "$@"
elif pip3 install "git+${REPO}@${PINNED_REF}" --quiet --user 2>/dev/null; then
    # Try common user bin locations
    for bin in "$HOME/.local/bin" "$HOME/.local/Scripts"; do
        if [ -f "$bin/homelab-starter" ]; then
            "$bin/homelab-starter" "$@"
            exit 0
        fi
    done
    python3 -m homelab.cli "$@"
else
    # Fallback: clone and run in-place
    rm -rf "$INSTALL_DIR"
    git clone --depth=1 --branch "$PINNED_REF" "$REPO" "$INSTALL_DIR" --quiet
    cd "$INSTALL_DIR"
    pip3 install -e . --quiet
    homelab-starter "$@"
fi
