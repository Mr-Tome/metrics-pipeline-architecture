#!/usr/bin/env bash
# Pulls the model weights listed in models.txt.
#
# - Resolves each revision to a commit hash and records it, so the exact weights are known.
# - Downloads safetensors only. Pickle-based formats (.bin, .pt, .pth, .pkl) can carry executable
#   code and are refused (BOM, Assumptions A17). The one exception is a CTranslate2 model (format ct2
#   in models.txt): its weights are a flat binary named model.bin, accepted only if it starts with the
#   CTranslate2 header.
# - Checks every file against the SHA-256 that Hugging Face publishes, then writes SHA256SUMS.
# - Pulls the tiktoken vocabulary files gpt-oss needs, so vLLM never downloads them at startup.
source "$(dirname "$0")/lib.sh"
require curl jq python3

HF="$(command -v hf || command -v huggingface-cli || true)"
[[ -n "${HF}" ]] || die "missing Hugging Face CLI (pipx install 'huggingface_hub[cli]')"
auth=()
[[ -n "${HF_TOKEN:-}" ]] && auth=(-H "Authorization: Bearer ${HF_TOKEN}")

out="${BUNDLE_DIR}/models"
mkdir -p "${out}"
excludes=(--exclude "original/*" --exclude "metal/*" --exclude "*.pt"
          --exclude "*.pth" --exclude "*.pkl" --exclude "*.ckpt" --exclude "*.gguf"
          --exclude "onnx/*" --exclude "*.onnx" --exclude "*.onnx_data")  # ONNX copies: unused, several GB

# ct2_header FILE: 0 if FILE starts with a CTranslate2 binary version (small little-endian uint32).
# Pickle starts with 0x80, PyTorch zip files with "PK"; neither passes.
ct2_header() {
    [[ "$(head -c 4 "$1" | od -An -tx1 | tr -d ' \n')" =~ ^(0[1-9a-f]|1[0-9a-f])000000$ ]]
}

grep -vE '^\s*(#|$)' "${DELIVERY_DIR}/models.txt" | while read -r name repo rev layout format; do
    case "${format}" in
        safetensors) excl=("${excludes[@]}" --exclude "*.bin") ;;
        ct2)         excl=("${excludes[@]}") ;;
        *)           die "${name}: format must be safetensors or ct2 (models.txt), got '${format}'" ;;
    esac
    commit=$(curl -fsSL "${auth[@]}" "https://huggingface.co/api/models/${repo}/revision/${rev}" | jq -r .sha)
    [[ "${commit}" =~ ^[0-9a-f]{40}$ ]] || die "could not resolve ${repo}@${rev}"
    log "${name}: ${repo}@${rev} = ${commit}"

    if [[ "${layout}" == "local" ]]; then
        dest="${out}/${name}"
        "${HF}" download "${repo}" --revision "${commit}" --local-dir "${dest}" "${excl[@]}"
        rm -rf "${dest}/.cache"
        files_root="${dest}"
    else
        dest="${out}/hf-cache"
        "${HF}" download "${repo}" --revision "${commit}" --cache-dir "${dest}" "${excl[@]}"
        files_root="${dest}/models--${repo/\//--}/snapshots/${commit}"
    fi

    allow="/none"
    if [[ "${format}" == ct2 ]]; then
        allow="${files_root}/model.bin"
        [[ -f "${allow}" ]] || die "${name}: ct2 model has no model.bin"
        ct2_header "${allow}" || die "${name}: model.bin does not start with a CTranslate2 header; refused"
    fi
    bad=$(find -L "${files_root}" -type f \( -name '*.bin' -o -name '*.pt' -o -name '*.pth' -o -name '*.pkl' -o -name '*.ckpt' \) \
          ! -path "${allow}" | head -1)
    [[ -z "${bad}" ]] || die "${name}: refused pickle-style weight file ${bad}"

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
    manifest "model-${name}" "${repo} commit ${commit} (layout ${layout}, format ${format})"
done

# gpt-oss loads its tokenizer through openai_harmony, which downloads these vocabulary files at startup
# unless TIKTOKEN_ENCODINGS_BASE points at a local copy (set in zarf/manifests/vllm.yaml).
# The SHA-256 values are the ones the tiktoken library itself checks.
tk="${out}/tiktoken"
mkdir -p "${tk}"
declare -A tiktoken_sha=(
    [o200k_base]=446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d
    [cl100k_base]=223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7
)
for enc in "${!tiktoken_sha[@]}"; do
    download "https://openaipublic.blob.core.windows.net/encodings/${enc}.tiktoken" "${tk}/${enc}.tiktoken"
    echo "${tiktoken_sha[${enc}]}  ${tk}/${enc}.tiktoken" | sha256sum --quiet -c - || die "tiktoken ${enc}: checksum mismatch"
done
( cd "${tk}" && sha256sum ./*.tiktoken > SHA256SUMS )
manifest tiktoken "o200k_base, cl100k_base from openaipublic.blob.core.windows.net (checksums match tiktoken's)"

log "models ready in ${out} ($(du -sh "${out}" | cut -f1))"
