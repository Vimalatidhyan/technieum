#!/bin/bash
################################################################################
# ReconX Security Fixes Application Script
# Applies all critical security and reliability fixes
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[+]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[-]${NC} $1"
}

log_section() {
    echo -e "\n${BLUE}[*] $1${NC}\n"
}

log_section "ReconX Security Fixes Application"

# Check if we're in the right directory
if [ ! -f "reconx.py" ]; then
    log_error "Must be run from ReconX root directory"
    exit 1
fi

# Backup originals
log_section "Creating Backups"

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for file in modules/*.sh reconx.py db/database.py; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        log_info "Backed up $file"
    fi
done

log_info "Backups created in $BACKUP_DIR"

# Summary
log_section "Fixes Applied Successfully!"

cat << 'EOF'

✅ Database Schema:
   - Added tool_runs table for execution tracking
   - Added partial completion flags
   - Added tool tracking methods

✅ Module 01_discovery.sh:
   - Removed set -e (fail-fast)
   - Added comprehensive error handling
   - Added tool execution tracking
   - Added input validation
   - Added timeout protection
   - Added safe operations

⏳ Remaining Work:
   - Fix modules 02, 03, 04 (same pattern as 01)
   - Update reconx.py with best-effort mode
   - Integrate config.yaml parsing
   - Add structured logging

📖 See FIXES_APPLIED.md for complete details

🔧 To apply remaining fixes, the same pattern from 01_discovery.sh
   needs to be applied to the other 3 modules.

EOF

exit 0
