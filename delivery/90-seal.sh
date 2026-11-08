#!/usr/bin/env bash
# Seals the bundle: copies the version pins in, checksums every file, and signs the checksum list.
# After this, nothing in the bundle may change. Any change means re-running the pull.
#
# A signature is required; intake/verify.sh refuses unsigned bundles.
#   COSIGN_KEY=cosign.key ./90-seal.sh     signs with cosign
#   GPG_KEY=<key-id>      ./90-seal.sh     signs with gpg
#   ALLOW_UNSIGNED=1      ./90-seal.sh     no signature. Throw-away tests only; never for the lab.
#
# The bundle records the git commit of delivery/ (SOURCE_COMMIT). Sealing refuses uncommitted changes
# in delivery/, so that commit describes exactly what built the bundle (ALLOW_DIRTY=1 overrides).
source "$(dirname "$0")/lib.sh"
require sha256sum

if [[ -z "${COSIGN_KEY:-}" && -z "${GPG_KEY:-}" && "${ALLOW_UNSIGNED:-0}" != 1 ]]; then
    die "set COSIGN_KEY or GPG_KEY to sign the bundle (ALLOW_UNSIGNED=1 only for a throw-away test)"
fi

if git -C "${DELIVERY_DIR}" rev-parse --git-dir >/dev/null 2>&1; then
    dirty=$(git -C "${DELIVERY_DIR}" status --porcelain -- .)
    if [[ -n "${dirty}" ]]; then
        [[ "${ALLOW_DIRTY:-0}" == 1 ]] || die "delivery/ has uncommitted changes; commit them first:"$'\n'"${dirty}"
        warn "sealing with uncommitted changes in delivery/ (ALLOW_DIRTY=1)"
    fi
    { git -C "${DELIVERY_DIR}" rev-parse HEAD; [[ -z "${dirty}" ]] || echo "plus uncommitted changes"; } \
        > "${BUNDLE_DIR}/SOURCE_COMMIT"
else
    warn "delivery/ is not a git checkout; SOURCE_COMMIT not recorded"
fi

cp "${DELIVERY_DIR}/versions.env" "${BUNDLE_DIR}/VERSIONS.env"
cp "${DELIVERY_DIR}/models.txt" "${BUNDLE_DIR}/MODELS.txt"

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
    warn "bundle is NOT signed (ALLOW_UNSIGNED=1). verify.sh will refuse it unless ALLOW_UNSIGNED=1 there too."
fi

log "sealed: ${BUNDLE_DIR} ($(du -sh "${BUNDLE_DIR}" | cut -f1), $(wc -l < "${BUNDLE_DIR}/SHA256SUMS") files)"
