#!/usr/bin/env bash
# Builds the Zarf package: every Helm chart and container image the AI phase needs, in one archive.
#
# 1. Renders the chart values and manifests with the pins from versions.env.
# 2. Runs `helm template` on each chart and lists every image it would pull,
#    including GPU Operator operands that only appear in its ClusterPolicy.
# 3. Renders zarf.yaml with those image lists and runs `zarf package create`,
#    which downloads the charts and images and writes an SBOM for each image.
#
# Images that the scan misses can be added by hand in zarf/extra-images/<COMPONENT>.txt.
source "$(dirname "$0")/lib.sh"
require helm python3
python3 -c 'import yaml' 2>/dev/null || die "python3 needs PyYAML (package python3-yaml)"

ZARF="${BUNDLE_DIR}/zarf/zarf"
[[ -x "${ZARF}" ]] || ZARF="$(command -v zarf || true)"
[[ -x "${ZARF}" ]] || die "zarf not found; run 15-pull-zarf.sh first"

build="${DELIVERY_DIR}/build"
rm -rf "${build}"
mkdir -p "${build}/values" "${build}/manifests" "${build}/images"

# Export every pin, plus repo/tag splits that chart values need.
set -a
# shellcheck source=versions.env
source "${DELIVERY_DIR}/versions.env"
RELEASE_VERSION="${RELEASE_VERSION:-$(date +%Y.%m.%d)}"
LITELLM_REPO="${LITELLM_IMAGE%:*}";       LITELLM_TAG="${LITELLM_IMAGE##*:}"
OPEN_WEBUI_REPO="${OPEN_WEBUI_IMAGE%:*}"; OPEN_WEBUI_TAG="${OPEN_WEBUI_IMAGE##*:}"
set +a

render() { python3 "${DELIVERY_DIR}/tools/render_zarf.py" "$1" "$2" "${build}/images"; }
for f in "${DELIVERY_DIR}"/zarf/values/*.yaml;    do render "${f}" "${build}/values/$(basename "${f}")"; done
for f in "${DELIVERY_DIR}"/zarf/manifests/*.yaml; do render "${f}" "${build}/manifests/$(basename "${f}")"; done

# scan COMPONENT RELEASE CHART-REF VERSION VALUES [extra helm args...]
scan() {
    local comp="$1" rel="$2" chart="$3" ver="$4" values="$5"; shift 5
    log "scanning images in ${chart} ${ver}"
    helm template "${rel}" "${chart}" --version "${ver}" -f "${build}/values/${values}" \
        --include-crds --kube-version "${RKE2_VERSION%%+*}" "$@" \
        | python3 "${DELIVERY_DIR}/tools/find_images.py" >> "${build}/images/${comp}.txt"
}
scan GPU_OPERATOR gpu-operator gpu-operator "${GPU_OPERATOR_VERSION}" gpu-operator.yaml \
     --repo https://helm.ngc.nvidia.com/nvidia --namespace gpu-operator
scan DATABASE cnpg cloudnative-pg "${CNPG_CHART_VERSION}" cnpg.yaml \
     --repo https://cloudnative-pg.github.io/charts --namespace cnpg-system
echo "${POSTGRES_IMAGE}" >> "${build}/images/DATABASE.txt"
scan GATEWAY litellm oci://ghcr.io/berriai/litellm-helm "${LITELLM_CHART_VERSION}" litellm.yaml --namespace ai
scan CHAT open-webui open-webui "${OPEN_WEBUI_CHART_VERSION}" open-webui.yaml \
     --repo https://helm.openwebui.com --namespace ai

for list in "${build}"/images/*.txt; do
    extra="${DELIVERY_DIR}/zarf/extra-images/$(basename "${list}")"
    [[ -f "${extra}" ]] && grep -vE '^\s*(#|$)' "${extra}" >> "${list}"
    sort -u -o "${list}" "${list}"
    log "$(basename "${list}" .txt): $(wc -l < "${list}") images"
    sed 's/^/    /' "${list}"
done

render "${DELIVERY_DIR}/zarf/zarf.yaml.in" "${build}/zarf.yaml"

mkdir -p "${BUNDLE_DIR}/package"
log "creating Zarf package (downloads all charts and images; this takes a while)"
( cd "${build}" && "${ZARF}" package create . --confirm --output "${BUNDLE_DIR}/package" )

cp "${build}/zarf.yaml" "${BUNDLE_DIR}/package/zarf.yaml.rendered"
cat "${build}"/images/*.txt | sort -u > "${BUNDLE_DIR}/package/IMAGES.txt"
manifest "zarf package ${RELEASE_NAME} ${RELEASE_VERSION}: $(wc -l < "${BUNDLE_DIR}/package/IMAGES.txt") images (see package/IMAGES.txt)"
log "package ready in ${BUNDLE_DIR}/package"
