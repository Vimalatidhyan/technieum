#!/bin/bash
################################################################################
# ReconX - Phase 2: Intelligence & Infrastructure
# Port scanning, OSINT, Takeover detection, Repo leaks
################################################################################

set -e
TARGET="$1"
OUTPUT_DIR="$2"

if [ -z "$TARGET" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <target> <output_dir>"
    exit 1
fi

PHASE_DIR="$OUTPUT_DIR/phase2_intel"
PHASE1_DIR="$OUTPUT_DIR/phase1_discovery"
mkdir -p "$PHASE_DIR"

echo "[*] Phase 2: Intelligence & Infrastructure for $TARGET"
echo "[*] Output directory: $PHASE_DIR"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[+]${NC} $1"
}

log_error() {
    echo -e "${RED}[-]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if alive hosts exist from Phase 1
if [ ! -f "$PHASE1_DIR/alive_hosts.txt" ]; then
    log_error "Phase 1 output not found. Run Phase 1 first!"
    exit 1
fi

ALIVE_HOSTS="$PHASE1_DIR/alive_hosts.txt"
ALIVE_COUNT=$(wc -l < "$ALIVE_HOSTS" | tr -d ' ')
log_info "Found $ALIVE_COUNT alive hosts from Phase 1"

################################################################################
# PHASE 2A: LIVE HOST VALIDATION
################################################################################

log_info "=== LIVE HOST VALIDATION ==="

# SubProber - Double check live hosts
if command -v subprober &> /dev/null; then
    log_info "Running SubProber for validation..."
    subprober -f "$ALIVE_HOSTS" -o "$PHASE_DIR/subprober_validated.txt" 2>/dev/null || log_warn "SubProber failed"

    if [ -f "$PHASE_DIR/subprober_validated.txt" ]; then
        VALIDATED_COUNT=$(wc -l < "$PHASE_DIR/subprober_validated.txt" | tr -d ' ')
        log_info "SubProber validated $VALIDATED_COUNT hosts"
    fi
else
    log_warn "SubProber not found, using Phase 1 alive hosts"
    cp "$ALIVE_HOSTS" "$PHASE_DIR/subprober_validated.txt"
fi

# Use validated hosts for remaining scans
SCAN_HOSTS="$PHASE_DIR/subprober_validated.txt"

################################################################################
# PHASE 2B: PORT SCANNING
################################################################################

log_info "=== PORT SCANNING ==="

PORTS_DIR="$PHASE_DIR/ports"
mkdir -p "$PORTS_DIR"

# Extract just hostnames/IPs for port scanning
cat "$SCAN_HOSTS" | sed -E 's|^https?://||' | sed 's|/.*||' | sort -u > "$PORTS_DIR/targets.txt"

# RustScan - Fast initial scan
if command -v rustscan &> /dev/null; then
    log_info "Running RustScan (fast port discovery)..."

    # Scan hosts in batches
    while IFS= read -r host; do
        log_info "RustScan: $host"
        rustscan -a "$host" --ulimit 5000 --range 1-65535 --timeout 1000 \
            >> "$PORTS_DIR/rustscan_raw.txt" 2>/dev/null || log_warn "RustScan failed for $host"
    done < "$PORTS_DIR/targets.txt"

    # Parse RustScan output to extract ports
    if [ -f "$PORTS_DIR/rustscan_raw.txt" ]; then
        grep -oP '\d+\.\d+\.\d+\.\d+:\d+|\[.*?\]' "$PORTS_DIR/rustscan_raw.txt" 2>/dev/null > "$PORTS_DIR/rustscan_ports.txt" || true
    fi
else
    log_warn "RustScan not found"
fi

# Nmap - Deep scan on discovered ports
if command -v nmap &> /dev/null; then
    log_info "Running Nmap (deep service detection)..."

    # Full comprehensive Nmap scan
    if [ -f "$PORTS_DIR/targets.txt" ]; then
        while IFS= read -r host; do
            log_info "Nmap: $host"
            nmap -sV -sC -T4 -Pn -p- "$host" \
                -oX "$PORTS_DIR/nmap_${host//[^a-zA-Z0-9]/_}.xml" \
                -oN "$PORTS_DIR/nmap_${host//[^a-zA-Z0-9]/_}.txt" \
                2>/dev/null || log_warn "Nmap failed for $host"
        done < "$PORTS_DIR/targets.txt"

        # Merge all XML outputs
        cat "$PORTS_DIR"/nmap_*.xml 2>/dev/null > "$PORTS_DIR/nmap_all.xml" || touch "$PORTS_DIR/nmap_all.xml"
    fi
else
    log_warn "Nmap not found"
fi

################################################################################
# PHASE 2C: OSINT & INFRASTRUCTURE
################################################################################

log_info "=== OSINT & INFRASTRUCTURE ==="

OSINT_DIR="$PHASE_DIR/osint"
mkdir -p "$OSINT_DIR"

# Shodan CLI
if command -v shodan &> /dev/null && [ ! -z "$SHODAN_API_KEY" ]; then
    log_info "Running Shodan..."

    while IFS= read -r host; do
        # Extract IP or hostname
        target=$(echo "$host" | sed -E 's|^https?://||' | sed 's|/.*||' | sed 's|:.*||')
        log_info "Shodan: $target"
        shodan host "$target" > "$OSINT_DIR/shodan_${target//[^a-zA-Z0-9]/_}.txt" 2>/dev/null || log_warn "Shodan failed for $target"
    done < "$SCAN_HOSTS"

    # Merge results
    cat "$OSINT_DIR"/shodan_*.txt 2>/dev/null > "$OSINT_DIR/shodan_all.txt" || touch "$OSINT_DIR/shodan_all.txt"
else
    log_warn "Shodan CLI not found or SHODAN_API_KEY not set"
fi

# ShodanX (Revolt suite)
if command -v shodanx &> /dev/null && [ ! -z "$SHODAN_API_KEY" ]; then
    log_info "Running ShodanX..."
    shodanx -d "$TARGET" -o "$OSINT_DIR/shodanx.json" 2>/dev/null || log_warn "ShodanX failed"
elif [ -f "/opt/shodanx/shodanx.py" ] && [ ! -z "$SHODAN_API_KEY" ]; then
    log_info "Running ShodanX (Python)..."
    python3 /opt/shodanx/shodanx.py -d "$TARGET" -o "$OSINT_DIR/shodanx.json" 2>/dev/null || log_warn "ShodanX failed"
else
    log_warn "ShodanX not found"
fi

# Censys CLI
if command -v censys &> /dev/null && [ ! -z "$CENSYS_API_ID" ] && [ ! -z "$CENSYS_API_SECRET" ]; then
    log_info "Running Censys..."

    while IFS= read -r host; do
        target=$(echo "$host" | sed -E 's|^https?://||' | sed 's|/.*||' | sed 's|:.*||')
        log_info "Censys: $target"
        censys search "$target" > "$OSINT_DIR/censys_${target//[^a-zA-Z0-9]/_}.json" 2>/dev/null || log_warn "Censys failed for $target"
    done < "$SCAN_HOSTS"

    # Merge results
    cat "$OSINT_DIR"/censys_*.json 2>/dev/null > "$OSINT_DIR/censys_all.json" || touch "$OSINT_DIR/censys_all.json"
else
    log_warn "Censys CLI not found or API credentials not set"
fi

# Additional OSINT: ASN Lookup
if command -v whois &> /dev/null; then
    log_info "Gathering ASN information..."

    # Get unique IPs from dnsx results
    if [ -f "$PHASE1_DIR/dnsx_resolved.json" ]; then
        cat "$PHASE1_DIR/dnsx_resolved.json" | jq -r '.a[]?' 2>/dev/null | sort -u > "$OSINT_DIR/all_ips.txt"

        # Lookup ASN for each IP (sample first 50 to avoid rate limits)
        head -n 50 "$OSINT_DIR/all_ips.txt" | while IFS= read -r ip; do
            whois "$ip" | grep -E "^(origin|OrgName|Organization|ASN)" >> "$OSINT_DIR/asn_info.txt" 2>/dev/null || true
        done
    fi
fi

################################################################################
# PHASE 2D: SUBDOMAIN TAKEOVER
################################################################################

log_info "=== SUBDOMAIN TAKEOVER DETECTION ==="

TAKEOVER_DIR="$PHASE_DIR/takeover"
mkdir -p "$TAKEOVER_DIR"

# Subjack
if command -v subjack &> /dev/null; then
    log_info "Running Subjack..."

    if [ -f "$PHASE1_DIR/all_subdomains.txt" ]; then
        subjack -w "$PHASE1_DIR/all_subdomains.txt" \
            -t 50 -timeout 30 -ssl -v \
            -o "$TAKEOVER_DIR/subjack_results.txt" 2>/dev/null || log_warn "Subjack failed"

        if [ -f "$TAKEOVER_DIR/subjack_results.txt" ]; then
            TAKEOVER_COUNT=$(wc -l < "$TAKEOVER_DIR/subjack_results.txt" | tr -d ' ')
            if [ "$TAKEOVER_COUNT" -gt 0 ]; then
                log_warn "Found $TAKEOVER_COUNT potential subdomain takeovers!"
            else
                log_info "No subdomain takeovers detected"
            fi
        fi
    fi
else
    log_warn "Subjack not found"
fi

# SubOver (alternative)
if command -v subover &> /dev/null && [ -f "$PHASE1_DIR/all_subdomains.txt" ]; then
    log_info "Running SubOver..."
    subover -l "$PHASE1_DIR/all_subdomains.txt" -o "$TAKEOVER_DIR/subover_results.txt" 2>/dev/null || log_warn "SubOver failed"
else
    log_warn "SubOver not found or no subdomains"
fi

################################################################################
# PHASE 2E: REPOSITORY LEAK DETECTION
################################################################################

log_info "=== REPOSITORY LEAK DETECTION ==="

LEAKS_DIR="$PHASE_DIR/leaks"
mkdir -p "$LEAKS_DIR"

# Gitleaks - Scan for secrets in git repos
if command -v gitleaks &> /dev/null; then
    log_info "Running Gitleaks..."

    # Check if target is a git repository or try to find company repos
    if [ -d ".git" ]; then
        log_info "Scanning local repository with Gitleaks..."
        gitleaks detect --source . --report-path "$LEAKS_DIR/gitleaks_report.json" 2>/dev/null || log_warn "Gitleaks scan failed"
    else
        log_info "No local git repository found for Gitleaks scan"
    fi

    # Try to scan GitHub if organization name matches
    if command -v gh &> /dev/null; then
        ORG_NAME=$(echo "$TARGET" | cut -d'.' -f1)
        log_info "Attempting to scan GitHub org: $ORG_NAME"

        # List repos (requires gh auth)
        gh repo list "$ORG_NAME" --limit 10 --json name -q '.[].name' 2>/dev/null | while read -r repo; do
            log_info "Scanning repo: $ORG_NAME/$repo"
            TEMP_DIR=$(mktemp -d)
            git clone --depth 1 "https://github.com/$ORG_NAME/$repo" "$TEMP_DIR/$repo" 2>/dev/null || continue
            gitleaks detect --source "$TEMP_DIR/$repo" --report-path "$LEAKS_DIR/gitleaks_${repo}.json" 2>/dev/null || true
            rm -rf "$TEMP_DIR"
        done
    fi
else
    log_warn "Gitleaks not found"
fi

# GitHunt - Search GitHub for leaked secrets
if [ -f "/opt/GitHunt/githunt.py" ] && [ ! -z "$GITHUB_TOKEN" ]; then
    log_info "Running GitHunt..."
    python3 /opt/GitHunt/githunt.py -t "$TARGET" -o "$LEAKS_DIR/githunt_results.txt" 2>/dev/null || log_warn "GitHunt failed"
elif command -v githunt &> /dev/null && [ ! -z "$GITHUB_TOKEN" ]; then
    log_info "Running GitHunt..."
    githunt -t "$TARGET" -o "$LEAKS_DIR/githunt_results.txt" 2>/dev/null || log_warn "GitHunt failed"
else
    log_warn "GitHunt not found or GITHUB_TOKEN not set"
fi

# TruffleHog (alternative secret scanner)
if command -v trufflehog &> /dev/null; then
    log_info "Running TruffleHog..."

    if [ -d ".git" ]; then
        trufflehog git file://. --json > "$LEAKS_DIR/trufflehog_report.json" 2>/dev/null || log_warn "TruffleHog failed"
    fi

    # Scan GitHub org
    if [ ! -z "$GITHUB_TOKEN" ]; then
        ORG_NAME=$(echo "$TARGET" | cut -d'.' -f1)
        trufflehog github --org="$ORG_NAME" --json > "$LEAKS_DIR/trufflehog_github.json" 2>/dev/null || log_warn "TruffleHog GitHub scan failed"
    fi
else
    log_warn "TruffleHog not found"
fi

# GitLeaks alternative: git-secrets
if command -v git-secrets &> /dev/null && [ -d ".git" ]; then
    log_info "Running git-secrets..."
    git secrets --scan --recursive > "$LEAKS_DIR/git_secrets.txt" 2>&1 || log_warn "git-secrets found issues (check output)"
else
    log_warn "git-secrets not found or not a git repo"
fi

################################################################################
# CLEANUP AND SUMMARY
################################################################################

log_info "=== PHASE 2 SUMMARY ==="
echo "Target: $TARGET"
echo "Scanned Hosts: $(wc -l < "$SCAN_HOSTS" 2>/dev/null | tr -d ' ')"

if [ -f "$PORTS_DIR/nmap_all.xml" ]; then
    OPEN_PORTS=$(grep -c "state=\"open\"" "$PORTS_DIR/nmap_all.xml" 2>/dev/null || echo "0")
    echo "Open Ports Found: $OPEN_PORTS"
fi

if [ -f "$TAKEOVER_DIR/subjack_results.txt" ]; then
    TAKEOVERS=$(wc -l < "$TAKEOVER_DIR/subjack_results.txt" 2>/dev/null | tr -d ' ')
    echo "Potential Takeovers: $TAKEOVERS"
fi

if [ -f "$LEAKS_DIR/gitleaks_report.json" ]; then
    GITLEAKS=$(jq length "$LEAKS_DIR/gitleaks_report.json" 2>/dev/null || echo "0")
    echo "Gitleaks Findings: $GITLEAKS"
fi

echo ""
echo "Output directories:"
echo "  - $PORTS_DIR: Port scan results"
echo "  - $OSINT_DIR: OSINT and infrastructure data"
echo "  - $TAKEOVER_DIR: Subdomain takeover results"
echo "  - $LEAKS_DIR: Repository leak detection"

# Create phase completion marker
touch "$PHASE_DIR/.completed"
log_info "Phase 2 completed successfully!"

exit 0
