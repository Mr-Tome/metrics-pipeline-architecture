#!/usr/bin/env bash
# Seals the bundle: copies the version pins in, checksums every file, and signs the checksum list.
# After this, nothing in the bundle may change. Any change means re-running the pull.
#
# Signing (optional, but the Delivery view expects it):
#   COSIGN_KEY=cosign.key ./90-seal.sh     signs with cosign
#   GPG_KEY=<key-id>      ./90-seal.sh     signs with gpg
source "$(dirname "$0")/lib.sh"
require sha256sum

cp "${DELIVERY_DIR}/versions.env" "${BUNDLE_DIR}/VERSIONS.env"
cp "${DELIVERY_DIR}/models.txt" "${BUNDLE_DIR}/MODELS.txt"
git -C "${DELIVERY_DIR}" rev-parse HEAD > "${BUNDLE_DIR}/SOURCE_COMMIT" 2>/dev/null || true

# Ship the intake scripts with the bundle so the receiving side runs the same code.
mkdir -p "${BUNDLE_DIR}/intake"
cp "${DELIVERY_DIR}"/intake/*.sh "${BUNDLE_DIR}/intake/"

log "checksumming every file (large bundles take several minutes)"
( cd "${BUNDLE_DIR}" && find . -type f ! -name SHA256SUMS ! -name 'SHA256SUMS.*' ! -name '*.part' -print0 \
    | sort -z | xargs -0 sha256sum > SHA256SUMS )

if [[ -n "${COSIGN_KEY:-}" ]]; then
    cosign sign-blob --yes --key "${COSIGN_KEY}" --output-signature "${BUNDLE_DIR}/SHA256SUMS.sig" "${BUNDLE_DIR}/SHA256SUMS"
    log "signed with cosign"
elif [[ -n "${GPG_KEY:-}" ]]; then
    gpg --batch --yes --local-user "${GPG_KEY}" --armor --detach-sign --output "${BUNDLE_DIR}/SHA256SUMS.asc" "${BUNDLE_DIR}/SHA256SUMS"
    log "signed with gpg"
else
    warn "bundle is NOT signed. Set COSIGN_KEY or GPG_KEY to sign."
fi

log "sealed: ${BUNDLE_DIR} ($(du -sh "${BUNDLE_DIR}" | cut -f1), $(wc -l < "${BUNDLE_DIR}/SHA256SUMS") files)"
