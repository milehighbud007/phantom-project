#!/usr/bin/env bash
# PHANTOM Project Reorganization Script - Optimized

set -euo pipefail

# Constants
PROJECT_ROOT="$(pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${PROJECT_ROOT}/../phantom_backup_${TIMESTAMP}"
DRY_RUN=false

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Parse flags
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}[DRY RUN MODE ACTIVE]${NC}"
fi

log() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

# 1. Safety Check & Backup
log "Creating backup at ${BACKUP_DIR}..."
if [ "$DRY_RUN" = false ]; then
    mkdir -p "$BACKUP_DIR"
    cp -r "$PROJECT_ROOT"/* "$BACKUP_DIR/" 2>/dev/null || warn "Some files skipped in backup"
fi

# 2. Define New Structure
DIRS=(
    "core/engine"
    "core/mcp"
    "modules/scanners"
    "modules/exploits"
    "interface/web"
    "interface/cli"
    "data/logs"
    "data/vault"
    "docs"
    "tests"
)

log "Building directory structure..."
for dir in "${DIRS[@]}"; do
    [ "$DRY_RUN" = false ] && mkdir -p "$PROJECT_ROOT/$dir"
done

# 3. Intelligent Migration (Mapping)
# Format: "source_pattern|destination_dir"
MAPPINGS=(
    "*.py|core/engine"
    "mcp_*|core/mcp"
    "scan_*|modules/scanners"
    "exploit_*|modules/exploits"
    "templates/*|interface/web"
    "static/*|interface/web"
    "*.md|docs"
    "test_*|tests"
)

log "Migrating files..."
for map in "${MAPPINGS[@]}"; do
    pattern="${map%|*}"
    dest="${map#*|}"
    
    # Use find to handle patterns safely
    find . -maxdepth 1 -name "$pattern" -not -path "*/.*" -exec bash -c "
        if [ \"$DRY_RUN\" = true ]; then
            echo \"Would move {} to $dest/\"
        else
            mv {} \"$dest/\" 2>/dev/null || true
        fi
    " \;
done

# 4. Cleanup
log "Cleaning up empty directories..."
if [ "$DRY_RUN" = false ]; then
    find . -type d -empty -delete
fi

echo -e "${GREEN}Successfully reorganized PHANTOM.${NC}"
