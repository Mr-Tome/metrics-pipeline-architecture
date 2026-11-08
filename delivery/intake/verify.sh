#!/usr/bin/env bash
# Intake check for a release bundle, run on the receiving side (build workstation rehearsal or lab) before anything
# is loaded. Exit code 0 means the signature is valid and every file matches the sealed checksum list.
#
#   COSIGN_PUB=cosign.pub ./verify.sh /path/to/bundle   cosign signature + checksums
#   ./verify.sh /path/to/bundle  (with SHA256SUMS.asc)  gpg signature + checksums (key must be imported)
#   ALLOW_UNSIGNED=1 ./verify.sh /path/to/bundle        checksums only. Throw-away tests only, never the lab.
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
    [[ "${ALLOW_UNSIGNED:-0}" == 1 ]] \
        || fail "bundle is not signed. Checksums prove the copy is intact, not who built it. Refusing."
    echo "WARNING: bundle is not signed (ALLOW_UNSIGNED=1). Do not carry this bundle into the lab."
fi

echo "checking $(wc -l < SHA256SUMS) files..."
sha256sum --quiet -c SHA256SUMS || fail "checksum mismatch (see lines above)"

# Files present that are not in the sealed list mean something was added after sealing.
extra=$(comm -13 <(sed 's/^[0-9a-f]*  //' SHA256SUMS | sort) \
                 <(find . -type f ! -name SHA256SUMS ! -name 'SHA256SUMS.*' | sort))
[[ -z "${extra}" ]] || fail "files not in the sealed list:"$'\n'"${extra}"

# Pickle-style weight files are refused (A17). The only exception is model.bin of a model listed as
# format ct2 in MODELS.txt (CTranslate2, a flat binary), and only if it starts with the CTranslate2 header.
allowed=()
while read -r name repo _rev layout format; do
    [[ "${format:-}" == ct2 ]] || continue
    if [[ "${layout}" == local ]]; then allowed+=("models/${name}/model.bin")
    else allowed+=("models/hf-cache/models--${repo/\//--}/snapshots/*/model.bin"); fi
done < <(grep -vE '^\s*(#|$)' MODELS.txt 2>/dev/null || true)
ct2_header() { [[ "$(head -c 4 "$1" | od -An -tx1 | tr -d ' \n')" =~ ^(0[1-9a-f]|1[0-9a-f])000000$ ]]; }
bad=""
while IFS= read -r -d '' f; do
    ok=0
    for pattern in "${allowed[@]}"; do
        # shellcheck disable=SC2053  # pattern is a glob on purpose
        [[ "${f}" == ${pattern} ]] && ct2_header "${f}" && ok=1
    done
    [[ ${ok} -eq 1 ]] || bad+="${f}"$'\n'
done < <(find -L models -type f \( -name '*.bin' -o -name '*.pt' -o -name '*.pth' -o -name '*.pkl' -o -name '*.ckpt' \) -print0 2>/dev/null)
[[ -z "${bad}" ]] || fail "pickle-style model files present:"$'\n'"${bad}"

echo "PASS: ${bundle}"
echo "versions:"; sed -n 's/^\([A-Z_]*\)="\(.*\)"/  \1 = \2/p' VERSIONS.env
