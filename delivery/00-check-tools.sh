#!/usr/bin/env bash
# Checks the build workstation has every tool and enough disk before a pull.
source "$(dirname "$0")/lib.sh"

require curl jq sha256sum tar skopeo helm python3

if command -v hf >/dev/null 2>&1; then
    log "Hugging Face CLI: hf"
elif command -v huggingface-cli >/dev/null 2>&1; then
    log "Hugging Face CLI: huggingface-cli"
else
    die "missing Hugging Face CLI. Install with: pipx install 'huggingface_hub[cli]'"
fi

# zarf and trivy are downloaded by the scripts themselves if missing.

need_gb=500
free_gb=$(df -BG --output=avail "${BUNDLE_DIR}" | tail -1 | tr -dc '0-9')
if (( free_gb < need_gb )); then
    die "only ${free_gb} GB free at ${BUNDLE_DIR}; want at least ${need_gb} GB (model ~65 GB, images, compression scratch)"
fi
log "disk OK: ${free_gb} GB free at ${BUNDLE_DIR}"

if [[ -z "${REGISTRY1_USER:-}" || -z "${REGISTRY1_TOKEN:-}" ]]; then
    warn "REGISTRY1_USER / REGISTRY1_TOKEN not set. Iron Bank pulls (registry1.dso.mil) will fail."
    warn "Phase 1 uses upstream images; this only matters once Iron Bank images are listed in zarf.yaml."
fi
if [[ -z "${HF_TOKEN:-}" ]]; then
    warn "HF_TOKEN not set. Public models still download, but slower and rate-limited."
fi
log "tools OK"
