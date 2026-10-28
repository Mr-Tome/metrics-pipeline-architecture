#!/usr/bin/env bash
# Shows the pinned version next to the newest upstream version for each item.
# Read-only: it never changes versions.env. Edit that file by hand, then re-run.
#
# Exit code 1 if any pinned version does not exist upstream.
source "$(dirname "$0")/lib.sh"
require curl jq skopeo helm

bad=0
row() { printf '%-22s pinned %-32s latest %s\n' "$1" "$2" "$3"; }

gh_latest() {  # owner/repo -> newest release tag (not pre-release)
    curl -fsSL "https://api.github.com/repos/$1/releases/latest" | jq -r .tag_name
}
gh_has() {     # owner/repo tag -> 0 if the release exists
    curl -fsS -o /dev/null "https://api.github.com/repos/$1/releases/tags/$(urlver "$2")"
}
check_gh() {   # label owner/repo pinned
    local latest; latest=$(gh_latest "$2" || echo "?")
    row "$1" "$3" "${latest}"
    gh_has "$2" "$3" || { warn "$1 ${3} not found upstream"; bad=1; }
}
check_image() {  # label image:tag
    local repo="${2%:*}" tag="${2##*:}" newest
    newest=$(skopeo list-tags "docker://${repo}" 2>/dev/null \
        | jq -r '.Tags[]' | grep -E '^v?[0-9]+\.[0-9]+' | grep -viE 'rc|dev|nightly' \
        | sort -V | tail -1 || true)
    row "$1" "${tag}" "${newest:-?}"
    skopeo inspect --raw "docker://$2" >/dev/null 2>&1 || { warn "$1 image $2 not found"; bad=1; }
}
check_chart() {  # label repo-url-or-oci chart pinned
    local newest
    if [[ "$2" == oci://* ]]; then
        newest=$(skopeo list-tags "docker://${2#oci://}/$3" 2>/dev/null | jq -r '.Tags[]' | sort -V | tail -1 || true)
        helm show chart "$2/$3" --version "$4" >/dev/null 2>&1 || { warn "$1 chart $4 not found"; bad=1; }
    else
        newest=$(helm show chart "$3" --repo "$2" 2>/dev/null | awk '/^version:/{print $2}' || true)
        helm show chart "$3" --repo "$2" --version "$4" >/dev/null 2>&1 || { warn "$1 chart $4 not found"; bad=1; }
    fi
    row "$1" "$4" "${newest:-?}"
}

check_gh    "rke2"            rancher/rke2        "${RKE2_VERSION}"
check_gh    "zarf"            zarf-dev/zarf       "${ZARF_VERSION}"
check_gh    "gpu-operator"    NVIDIA/gpu-operator "${GPU_OPERATOR_VERSION}"
check_gh    "trivy"           aquasecurity/trivy  "v${TRIVY_VERSION}"
check_image "vllm"            "${VLLM_IMAGE}"
check_image "litellm"         "${LITELLM_IMAGE}"
check_image "open-webui"      "${OPEN_WEBUI_IMAGE}"
check_image "whisper"         "${WHISPER_IMAGE}"
check_image "postgres"        "${POSTGRES_IMAGE}"
check_chart "litellm chart"   oci://ghcr.io/berriai litellm-helm "${LITELLM_CHART_VERSION}"
check_chart "open-webui chart" https://helm.openwebui.com open-webui "${OPEN_WEBUI_CHART_VERSION}"
check_chart "cnpg chart"      https://cloudnative-pg.github.io/charts cloudnative-pg "${CNPG_CHART_VERSION}"
check_chart "gpu-op chart"    https://helm.ngc.nvidia.com/nvidia gpu-operator "${GPU_OPERATOR_VERSION}"

if [[ -n "${NVIDIA_DRIVER_VERSION}" ]]; then
    url="https://us.download.nvidia.com/tesla/${NVIDIA_DRIVER_VERSION}/NVIDIA-Linux-x86_64-${NVIDIA_DRIVER_VERSION}.run"
    if curl -fsIL -o /dev/null "${url}"; then row "nvidia driver" "${NVIDIA_DRIVER_VERSION}" "(exists)"
    else warn "nvidia driver ${NVIDIA_DRIVER_VERSION} not found at ${url}"; bad=1; fi
fi

(( bad == 0 )) && log "all pinned versions exist upstream" || die "fix versions.env, then re-run"
