#!/usr/bin/env bash
# ==============================================================================
# ReconX — Install all tools and libraries required to run the scan harness and API.
# Targets: Kali Linux, Debian, Ubuntu (apt-based).
# Usage: sudo ./install_tools.sh   (or run as root; apt requires elevated privileges)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use sudo for apt if not root
APT_CMD="apt-get"
if [[ $EUID -ne 0 ]] && command -v sudo &>/dev/null; then
    APT_CMD="sudo apt-get"
fi

# ------------------------------------------------------------------------------
# System packages used by lib/run_scan.sh (same names/flags as in harness)
# ------------------------------------------------------------------------------
# Phase 0 DNS:    dig, nslookup, host
# Phase 1:        subfinder, amass
# Phase 2:        nmap, nc (netcat)
# Phase 3:        httpx, curl
# Phase 4:        nuclei, nikto
# General:        timeout (coreutils)
# ------------------------------------------------------------------------------

APT_PACKAGES=(
    # DNS (phase 0)
    dnsutils          # dig, nslookup
    bind9-host        # host
    # Subdomain enum (phase 1)
    subfinder         # Kali/Debian: subfinder
    amass             # OWASP Amass
    # Port scan (phase 2)
    nmap
    netcat-openbsd    # nc
    # Web probe (phase 3)
    curl
    # httpx: on Kali = httpx-toolkit (binary name httpx)
    # nuclei + nikto (phase 4)
    nuclei
    nikto
)

# httpx binary: Kali = httpx-toolkit; other distros may need Go install (done below if missing)
APT_PACKAGES+=(httpx-toolkit)

echo "[install] ReconX dependency installer"
echo "[install] Script dir: $SCRIPT_DIR"
echo ""

# ------------------------------------------------------------------------------
# 1. APT (system tools)
# ------------------------------------------------------------------------------
if command -v apt-get &>/dev/null; then
    echo "[install] Updating apt cache..."
    $APT_CMD update -qq

    echo "[install] Installing system packages: ${APT_PACKAGES[*]} python3 python3-pip python3-venv"
    if ! DEBIAN_FRONTEND=noninteractive $APT_CMD install -y \
        "${APT_PACKAGES[@]}" \
        python3 \
        python3-pip \
        python3-venv; then
        echo "[install] Some packages could not be installed (e.g. httpx-toolkit/nuclei on non-Kali). Trying without optional..."
        DEBIAN_FRONTEND=noninteractive $APT_CMD install -y \
            dnsutils bind9-host subfinder amass nmap netcat-openbsd curl nikto \
            python3 python3-pip python3-venv 2>/dev/null || true
    fi

    # Fallback: if any Go-based tool missing (e.g. on non-Kali), try Go install
    export PATH="${PATH:-}:${HOME}/go/bin"
    if command -v go &>/dev/null; then
        for tool in httpx nuclei subfinder; do
            if ! command -v "$tool" &>/dev/null; then
                echo "[install] Installing $tool via Go..."
                case "$tool" in
                    httpx)    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest 2>/dev/null || true ;;
                    nuclei)   go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest 2>/dev/null || true ;;
                    subfinder) go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>/dev/null || true ;;
                esac
            fi
        done
        # Amass is OWASP; different repo
        if ! command -v amass &>/dev/null; then
            echo "[install] Installing amass via Go..."
            go install -v github.com/owasp-amass/amass/v4/...@master 2>/dev/null || true
        fi
    fi
else
    echo "[install] WARNING: apt-get not found. Install the following manually:"
    echo "  ${APT_PACKAGES[*]}"
    echo "  python3 python3-pip python3-venv"
fi

# ------------------------------------------------------------------------------
# 2. Python virtualenv and pip dependencies (requirements.txt + requirements-api.txt)
# ------------------------------------------------------------------------------
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" &>/dev/null; then
    echo "[install] ERROR: $PYTHON not found. Install python3 and re-run."
    exit 1
fi

VENV_DIR="${VENV_DIR:-.venv}"
if [[ ! -d "$VENV_DIR" ]]; then
    echo "[install] Creating virtualenv at $VENV_DIR..."
    "$PYTHON" -m venv "$VENV_DIR"
fi
echo "[install] Activating $VENV_DIR..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "[install] Upgrading pip..."
pip install --upgrade pip -q

REQ_TXT="$SCRIPT_DIR/requirements.txt"
REQ_API="$SCRIPT_DIR/requirements-api.txt"
if [[ -f "$REQ_TXT" ]]; then
    echo "[install] Installing Python deps from requirements.txt..."
    pip install -r "$REQ_TXT" -q
fi
if [[ -f "$REQ_API" ]]; then
    echo "[install] Installing Python deps from requirements-api.txt..."
    pip install -r "$REQ_API" -q
fi

# ------------------------------------------------------------------------------
# 3. Harness executable
# ------------------------------------------------------------------------------
RUN_SCAN="$SCRIPT_DIR/lib/run_scan.sh"
if [[ -f "$RUN_SCAN" ]]; then
    chmod +x "$RUN_SCAN"
    echo "[install] lib/run_scan.sh is executable."
fi

# ------------------------------------------------------------------------------
# 4. Report versions (match tools used in run_scan.sh)
# ------------------------------------------------------------------------------
echo ""
echo "[install] Installed versions (tools used by lib/run_scan.sh):"
for cmd in dig nslookup host subfinder amass nmap nc curl httpx nuclei nikto timeout; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" --version 2>/dev/null | head -1 || true)
        [[ -z "$ver" ]] && ver=$("$cmd" -V 2>/dev/null | head -1 || true)
        [[ -z "$ver" ]] && ver="(unknown version)"
        echo "  $cmd: $ver"
    else
        echo "  $cmd: NOT FOUND"
    fi
done
echo ""
echo "  Python: $("$PYTHON" --version 2>&1)"
echo "  pip:    $(pip --version 2>&1)"
echo ""
echo "[install] Done. Run the app with: ./start.sh"
echo "          Or run a single scan: ./lib/run_scan.sh 1 example.com full"
