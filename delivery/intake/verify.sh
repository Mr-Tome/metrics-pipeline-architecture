#!/usr/bin/env bash
# Intake check for a release bundle, run on the receiving side (build workstation rehearsal or lab) before anything
# is loaded. Exit code 0 means every file matches the sealed checksum list and the signature,
# if one was made, is valid.
#
#   ./verify.sh /path/to/bundle                         checksums only
#   COSIGN_PUB=cosign.pub ./verify.sh /path/to/bundle   checksums + cosign signature
#   ./verify.sh /path/to/bundle  (with SHA256SUMS.asc)  checksums + gpg signature (key must be imported)
set -euo pipefail

bundle="${1:?usage: verify.sh BUNDLE_DIR}"
cd "${bundle}"
fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f SHA256SUMS ]] || fail "no SHA256SUMS in ${bundle}; the bundle was not sealed"

if [[ -f SHA256SUMS.sig ]]; then
    [[ -n "${COSIGN_PUB:-}" ]] || fail "bundle is cosign-signed; set COSIGN_PUB to the public key"
    cosign verify-blob --key "${COSIGN_PUB}" --signature SHA256SUMS.sig SHA256SUMS || fail "cosign signature"
    echo "signature: cosign OK"
elif [[ -f SHA256SUMS.asc ]]; then
    gpg --verify SHA256SUMS.asc SHA256SUMS || fail "gpg signature"
    echo "signature: gpg OK"
else
    echo "WARNING: bundle is not signed. Checksums prove the copy is intact, not who built it."
fi

echo "checking $(wc -l < SHA256SUMS) files..."
sha256sum --quiet -c SHA256SUMS || fail "checksum mismatch (see lines above)"

# Files present that are not in the sealed list mean something was added after sealing.
extra=$(comm -13 <(sed 's/^[0-9a-f]*  //' SHA256SUMS | sort) \
                 <(find . -type f ! -name SHA256SUMS ! -name 'SHA256SUMS.*' | sort))
[[ -z "${extra}" ]] || fail "files not in the sealed list:"$'\n'"${extra}"

bad=$(find -L models -type f \( -name '*.bin' -o -name '*.pt' -o -name '*.pth' -o -name '*.pkl' -o -name '*.ckpt' \) 2>/dev/null | head -5)
[[ -z "${bad}" ]] || fail "non-safetensors model files present:"$'\n'"${bad}"

echo "PASS: ${bundle}"
echo "versions:"; sed -n 's/^\([A-Z_]*\)="\(.*\)"/  \1 = \2/p' VERSIONS.env
