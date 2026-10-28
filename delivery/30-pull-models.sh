#!/usr/bin/env bash
# Pulls the model weights listed in models.txt.
#
# - Resolves each revision to a commit hash and records it, so the exact weights are known.
# - Downloads safetensors only. Pickle-based formats (.bin, .pt, .pth, .pkl) can carry executable
#   code and are refused (BOM, Assumptions A17).
# - Checks every file against the SHA-256 that Hugging Face publishes, then writes SHA256SUMS.
source "$(dirname "$0")/lib.sh"
require curl jq python3

HF="$(command -v hf || command -v huggingface-cli || true)"
[[ -n "${HF}" ]] || die "missing Hugging Face CLI (pipx install 'huggingface_hub[cli]')"
auth=()
[[ -n "${HF_TOKEN:-}" ]] && auth=(-H "Authorization: Bearer ${HF_TOKEN}")

out="${BUNDLE_DIR}/models"
mkdir -p "${out}"
excludes=(--exclude "original/*" --exclude "metal/*" --exclude "*.bin" --exclude "*.pt"
          --exclude "*.pth" --exclude "*.pkl" --exclude "*.ckpt" --exclude "*.gguf")

grep -vE '^\s*(#|$)' "${DELIVERY_DIR}/models.txt" | while read -r name repo rev layout; do
    commit=$(curl -fsSL "${auth[@]}" "https://huggingface.co/api/models/${repo}/revision/${rev}" | jq -r .sha)
    [[ "${commit}" =~ ^[0-9a-f]{40}$ ]] || die "could not resolve ${repo}@${rev}"
    log "${name}: ${repo}@${rev} = ${commit}"

    if [[ "${layout}" == "local" ]]; then
        dest="${out}/${name}"
        "${HF}" download "${repo}" --revision "${commit}" --local-dir "${dest}" "${excludes[@]}"
        rm -rf "${dest}/.cache"
        files_root="${dest}"
    else
        dest="${out}/hf-cache"
        "${HF}" download "${repo}" --revision "${commit}" --cache-dir "${dest}" "${excludes[@]}"
        files_root="${dest}/models--${repo/\//--}/snapshots/${commit}"
    fi

    bad=$(find -L "${files_root}" -type f \( -name '*.bin' -o -name '*.pt' -o -name '*.pth' -o -name '*.pkl' -o -name '*.ckpt' \) | head -1)
    [[ -z "${bad}" ]] || die "${name}: refused non-safetensors weight file ${bad}"

    log "${name}: checking files against published SHA-256"
    curl -fsSL "${auth[@]}" "https://huggingface.co/api/models/${repo}/tree/${commit}?recursive=true" > "${out}/.tree.json"
    python3 - "${files_root}" "${out}/.tree.json" <<'EOF'
import hashlib, json, os, sys
root, tree = sys.argv[1], json.load(open(sys.argv[2]))
checked = 0
for entry in tree:
    lfs = entry.get("lfs")
    path = os.path.join(root, entry["path"])
    if entry.get("type") != "file" or not lfs or not os.path.exists(path):
        continue
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            h.update(block)
    if h.hexdigest() != lfs["oid"]:
        sys.exit(f"CHECKSUM MISMATCH: {entry['path']}")
    checked += 1
print(f"  {checked} large files match the published SHA-256")
EOF
    rm -f "${out}/.tree.json"
    ( cd "${files_root}" && find -L . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS )
    manifest "model ${name}: ${repo} commit ${commit} (layout ${layout})"
done
log "models ready in ${out} ($(du -sh "${out}" | cut -f1))"
