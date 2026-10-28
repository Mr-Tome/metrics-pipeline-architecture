# Shared helpers for the delivery scripts. Source this file; do not run it.

set -euo pipefail

DELIVERY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=versions.env
source "${DELIVERY_DIR}/versions.env"

# Where the release bundle is assembled. Override with BUNDLE_DIR=/path ./pull-all.sh
BUNDLE_DIR="${BUNDLE_DIR:-${DELIVERY_DIR}/out/${RELEASE_NAME}-$(date +%Y%m%d)}"
mkdir -p "${BUNDLE_DIR}"
BUNDLE_DIR="$(cd "${BUNDLE_DIR}" && pwd)"

log()  { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }
warn() { printf '[%s] WARNING: %s\n' "$(date +%H:%M:%S)" "$*" >&2; }
die()  { printf '[%s] ERROR: %s\n' "$(date +%H:%M:%S)" "$*" >&2; exit 1; }

require() {
    local missing=0
    for cmd in "$@"; do
        if ! command -v "${cmd}" >/dev/null 2>&1; then
            warn "missing tool: ${cmd}"
            missing=1
        fi
    done
    [[ ${missing} -eq 0 ]] || die "install the missing tools (see delivery/README.md) and re-run"
}

# download URL DEST: resumable, fails on HTTP errors, skips if DEST already exists.
download() {
    local url="$1" dest="$2"
    if [[ -s "${dest}" ]]; then
        log "already have $(basename "${dest}")"
        return 0
    fi
    log "downloading ${url}"
    curl -fL --retry 5 --retry-delay 5 -C - -o "${dest}.part" "${url}"
    mv "${dest}.part" "${dest}"
}

# Record a line in the bundle manifest (what is in the bundle and where it came from).
manifest() {
    printf '%s\n' "$*" >> "${BUNDLE_DIR}/MANIFEST.txt"
}

# URL-encode the '+' in versions like v1.33.1+rke2r1
urlver() { printf '%s' "${1//+/%2B}"; }
