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
# - Format ct2-convert (models.txt): pulls the source safetensors into WORK_DIR (outside the bundle), converts
#   them to CTranslate2 with the pinned converter (convert-requirements.txt), and stores the result in the
#   bundle as si/<name> in the Hugging Face cache layout, with a model card the whisper server can read.
source "$(dirname "$0")/lib.sh"
require curl jq python3
WORK_DIR="${WORK_DIR:-${BUNDLE_DIR%/}.work}"

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

# The converter runs in its own virtual environment under WORK_DIR, with the versions in convert-requirements.txt.
convert_venv() {
    local venv="${WORK_DIR}/convert-venv" py
    py=$(command -v python3.12 || command -v python3)
    if [[ ! -x "${venv}/bin/ct2-transformers-converter" ]]; then
        log "creating the converter environment (${py}, convert-requirements.txt)" >&2
        "${py}" -m venv "${venv}"
        "${venv}/bin/pip" install --quiet --upgrade pip >&2
        "${venv}/bin/pip" install --quiet -r "${DELIVERY_DIR}/convert-requirements.txt" >&2
    fi
    printf '%s' "${venv}"
}
convert_tools() {
    "${WORK_DIR}/convert-venv/bin/pip" freeze 2>/dev/null | grep -iE '^(ctranslate2|transformers|torch)==' | paste -sd' ' -
}

# convert_ct2 NAME REPO COMMIT SRC: converts SRC to CTranslate2 and stores it in the bundle's Hugging Face
# cache as si/NAME (blobs, a snapshot named after the source commit, refs/main), the layout the whisper
# server and huggingface_hub read offline. Prints the snapshot folder.
convert_ct2() {
    local name="$1" repo="$2" commit="$3" src="$4" venv tmp repo_dir snap f sum
    repo_dir="${out}/hf-cache/models--si--${name}"
    snap="${repo_dir}/snapshots/${commit}"
    if [[ -f "${snap}/model.bin" && -f "${repo_dir}/refs/main" ]]; then
        log "${name}: already converted" >&2
        printf '%s' "${snap}"; return 0
    fi
    venv=$(convert_venv)
    tmp="${WORK_DIR}/convert-out/${name}"
    rm -rf "${tmp}" "${repo_dir}"
    log "${name}: converting ${repo}@${commit} to CTranslate2 (float16)" >&2
    "${venv}/bin/ct2-transformers-converter" --model "${src}" --output_dir "${tmp}" \
        --copy_files tokenizer.json preprocessor_config.json --quantization float16 >&2
    # The whisper server lists a local model only if its model card says library ctranslate2 and task
    # automatic-speech-recognition.
    cat > "${tmp}/README.md" <<CARD
---
license: apache-2.0
library_name: ctranslate2
pipeline_tag: automatic-speech-recognition
tags:
  - audio
  - automatic-speech-recognition
base_model: ${repo}
---
# si/${name}

OpenAI's ${repo} (commit ${commit}), converted to CTranslate2 (float16) for faster-whisper on the build
side by delivery/30-pull-models.sh. Tools: $(convert_tools). Source weights: model.safetensors only.
CARD
    mkdir -p "${repo_dir}/blobs" "${repo_dir}/refs" "${snap}"
    for f in "${tmp}"/*; do
        sum=$(sha256sum "${f}" | cut -d' ' -f1)
        mv "${f}" "${repo_dir}/blobs/${sum}"
        ln -s "../../blobs/${sum}" "${snap}/$(basename "${f}")"
    done
    printf '%s' "${commit}" > "${repo_dir}/refs/main"
    rm -rf "${tmp}"
    printf '%s' "${snap}"
}

grep -vE '^\s*(#|$)' "${DELIVERY_DIR}/models.txt" | while read -r name repo rev layout format; do
    case "${format}" in
        safetensors) excl=("${excludes[@]}" --exclude "*.bin") ;;
        ct2)         excl=("${excludes[@]}") ;;
        # Source for a conversion: the one safetensors file only. Pickle (.bin), Flax (.msgpack), and the
        # duplicate fp32 shards are left out.
        ct2-convert) excl=("${excludes[@]}" --exclude "*.bin" --exclude "*.msgpack" --exclude "*.h5" \
                           --exclude "model.fp32-*" --exclude "*.index.fp32.json") ;;
        *)           die "${name}: format must be safetensors, ct2, or ct2-convert (models.txt), got '${format}'" ;;
    esac
    commit=$(curl -fsSL "${auth[@]}" "https://huggingface.co/api/models/${repo}/revision/${rev}" | jq -r .sha)
    [[ "${commit}" =~ ^[0-9a-f]{40}$ ]] || die "could not resolve ${repo}@${rev}"
    log "${name}: ${repo}@${rev} = ${commit}"

    if [[ "${format}" == ct2-convert ]]; then
        [[ "${layout}" == cache ]] || die "${name}: ct2-convert needs layout cache (the whisper server reads that)"
        dest="${WORK_DIR}/convert-src/${name}"
        "${HF}" download "${repo}" --revision "${commit}" --local-dir "${dest}" "${excl[@]}"
        rm -rf "${dest}/.cache"
        files_root="${dest}"
    elif [[ "${layout}" == "local" ]]; then
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
    if [[ "${format}" == ct2-convert ]]; then
        [[ -f "${files_root}/model.safetensors" ]] || die "${name}: source has no model.safetensors; refusing to convert"
    fi
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
    if [[ "${format}" == ct2-convert ]]; then
        files_root=$(convert_ct2 "${name}" "${repo}" "${commit}" "${files_root}")
        ct2_header "${files_root}/model.bin" || die "${name}: converted model.bin has no CTranslate2 header"
    fi
    ( cd "${files_root}" && find -L . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS )
    if [[ "${format}" == ct2-convert ]]; then
        manifest "model-${name}" "si/${name}: converted by us from ${repo} commit ${commit} ($(convert_tools))"
    else
        manifest "model-${name}" "${repo} commit ${commit} (layout ${layout}, format ${format})"
    fi
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
