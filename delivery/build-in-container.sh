#!/usr/bin/env bash
# Runs pull-all.sh inside the pinned build container, so the host needs only podman. Used in staging, where
# the build host is also a cluster node: no build tool (helm, skopeo, the Hugging Face CLI, the Whisper
# converter) is installed on it, so the install still tests a clean node.
#
#   sudo SI_ROOT=/srv/si GPG_KEY=<key-id> ./build-in-container.sh            the release bundle (pull-all.sh)
#   sudo SI_ROOT=/srv/si ./build-in-container.sh staging/build-addon.sh      the staging add-on, afterwards
#
# Layout under SI_ROOT (default /srv/si):
#   bundle/            the release bundle (what verify.sh and deploy.sh read)
#   bundle.pull.log    the pull log
#   work/              build scratch: the converter, Whisper source weights, temp files. Not in the bundle.
#
# Passed through to pull-all.sh when set: SKIP, WITH_CLIENTS, OS_KERNEL, GPG_KEY, HF_TOKEN, ALLOW_DIRTY,
# ALLOW_UNSIGNED, RELEASE_VERSION. With GPG_KEY, the signing key comes from GNUPGHOME (default ~/.gnupg).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "${here}/.." && pwd)"
# shellcheck source=versions.env
source "${here}/versions.env"
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
command -v podman >/dev/null || die "podman is not installed (dnf install podman)"
[[ "$(uname -m)" == x86_64 ]] || die "the bundle is amd64; build it on an x86_64 host"

script="${1:-pull-all.sh}"
[[ -f "${here}/${script}" ]] || die "no ${script} in ${here}"
root="${SI_ROOT:-/srv/si}"
mkdir -p "${root}/bundle" "${root}/work/tmp"

tag="localhost/si-build:helm-${HELM_VERSION}-hf-${HF_HUB_VERSION}"
podman build -t "${tag}" \
    --build-arg BUILD_IMAGE="${BUILD_IMAGE}" --build-arg HELM_VERSION="${HELM_VERSION}" \
    --build-arg HF_HUB_VERSION="${HF_HUB_VERSION}" -f "${here}/build-container/Containerfile" "${here}/build-container"

gpg=()
if [[ -n "${GPG_KEY:-}" ]]; then
    home="${GNUPGHOME:-${HOME}/.gnupg}"
    [[ -d "${home}" ]] || die "GPG_KEY is set but ${home} does not exist"
    gpg=(-v "${home}:/root/.gnupg")
fi

env_args=()
for v in SKIP WITH_CLIENTS OS_KERNEL GPG_KEY HF_TOKEN ALLOW_DIRTY ALLOW_UNSIGNED RELEASE_VERSION; do
    [[ -n "${!v:-}" ]] && env_args+=(-e "${v}=${!v}")
done

# label=disable: the container reads the repository and writes SI_ROOT without relabeling host folders.
exec podman run --rm --security-opt label=disable \
    -v "${repo}:/src" -v "${root}:/si" "${gpg[@]}" "${env_args[@]}" \
    -e BUNDLE_DIR=/si/bundle -e WORK_DIR=/si/work -e TMPDIR=/si/work/tmp -e HF_HOME=/si/work/hf-home \
    "${tag}" "/src/delivery/${script}"
