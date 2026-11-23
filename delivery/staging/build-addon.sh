#!/usr/bin/env bash
# Builds the staging add-on: the stand-in model's weights and a small Zarf package with the CPU stand-ins
# (addon/). Run it after the main pull, inside the build container:
#
#   sudo SI_ROOT=/srv/si ../build-in-container.sh staging/build-addon.sh
#
# Output: SI_ROOT/staging-addon/ (models/ and package/). It is never sealed into the lab bundle.
source "$(dirname "$0")/../lib.sh"
# shellcheck source=addon-versions.env
source "$(dirname "$0")/addon-versions.env"
require curl jq python3
HF="$(command -v hf || true)"; [[ -n "${HF}" ]] || die "missing Hugging Face CLI (hf)"
ZARF="${BUNDLE_DIR}/zarf/zarf"
[[ -x "${ZARF}" ]] || die "no zarf in ${BUNDLE_DIR}; run the main pull first"

addon="${ADDON_DIR:-$(dirname "${BUNDLE_DIR}")/staging-addon}"
build="${WORK_DIR:-${BUNDLE_DIR%/}.work}/addon-build"
rm -rf "${build}"; mkdir -p "${build}/images" "${addon}/models" "${addon}/package"

# Stand-in model: safetensors only, every large file checked against Hugging Face's published SHA-256.
dest="${addon}/models/standin-llm"
log "stand-in model ${STANDIN_REPO}@${STANDIN_COMMIT}"
"${HF}" download "${STANDIN_REPO}" --revision "${STANDIN_COMMIT}" --local-dir "${dest}" \
    --exclude "*.bin" --exclude "*.pt" --exclude "*.pth" --exclude "*.pkl" --exclude "*.gguf" --exclude "onnx/*"
rm -rf "${dest}/.cache"
curl -fsSL "https://huggingface.co/api/models/${STANDIN_REPO}/tree/${STANDIN_COMMIT}?recursive=true" > "${build}/tree.json"
python3 - "${dest}" "${build}/tree.json" <<'PY'
import hashlib, json, os, sys
root, tree = sys.argv[1], json.load(open(sys.argv[2]))
n = 0
for e in tree:
    p = os.path.join(root, e["path"])
    if e.get("type") == "file" and e.get("lfs") and os.path.exists(p):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 24), b""):
                h.update(b)
        if h.hexdigest() != e["lfs"]["oid"]:
            sys.exit(f"CHECKSUM MISMATCH: {e['path']}")
        n += 1
print(f"  {n} large files match the published SHA-256")
PY
( cd "${dest}" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS )

# Package: same renderer as the lab package.
set -a; RELEASE_VERSION="${RELEASE_VERSION:-$(date +%Y.%m.%d)}"; set +a
echo "${VLLM_CPU_IMAGE}"    > "${build}/images/STANDIN.txt"
echo "${WHISPER_CPU_IMAGE}" > "${build}/images/WHISPER_CPU.txt"
export VLLM_CPU_IMAGE WHISPER_CPU_IMAGE
for f in "$(dirname "$0")"/addon/*; do
    python3 "${DELIVERY_DIR}/tools/render_zarf.py" "${f}" "${build}/$(basename "${f%.in}")" "${build}/images"
done
log "creating the add-on Zarf package"
( cd "${build}" && "${ZARF}" package create . --confirm --output "${addon}/package" )
cp "$(dirname "$0")/addon-versions.env" "${addon}/"
log "add-on ready in ${addon} ($(du -sh "${addon}" | cut -f1))"
