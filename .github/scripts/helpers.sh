#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

run_with_retry() {
    local max_attempts=3
    local delay=5
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if "$@"; then
            return 0
        else
            log_warn "Attempt $attempt/$max_attempts failed. Retrying in ${delay}s..."
            sleep $delay
            attempt=$((attempt + 1))
            delay=$((delay * 2))
        fi
    done

    log_error "Command failed after $max_attempts attempts: $*"
    return 1
}

detect_changed_packages() {
    local base_ref="${1:-main}"
    git diff --name-only "origin/$base_ref...HEAD" | cut -d/ -f1-3 | sort -u
}

package_changed() {
    local pkg="$1"
    local base_ref="${2:-main}"
    git diff --name-only "origin/$base_ref...HEAD" | grep -q "^packages/$pkg/"
}
