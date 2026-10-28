#!/usr/bin/env bash
# Pulls the NVIDIA data center driver installer for the GPU hosts.
# The host needs gcc, make, and kernel headers that match its running kernel to build the
# driver. In the lab those come from the lab's OS package mirror, not from this bundle.
source "$(dirname "$0")/lib.sh"
require curl sha256sum

if [[ -z "${NVIDIA_DRIVER_VERSION}" ]]; then
    log "NVIDIA_DRIVER_VERSION is empty; skipping driver download"
    exit 0
fi
out="${BUNDLE_DIR}/nvidia-driver"
mkdir -p "${out}"
run="NVIDIA-Linux-x86_64-${NVIDIA_DRIVER_VERSION}.run"
download "https://us.download.nvidia.com/tesla/${NVIDIA_DRIVER_VERSION}/${run}" "${out}/${run}"
chmod +x "${out}/${run}"
sh "${out}/${run}" --check >/dev/null || die "driver installer failed its own integrity check"

manifest "nvidia driver ${NVIDIA_DRIVER_VERSION} sha256 $(sha256sum "${out}/${run}" | cut -d' ' -f1)"
log "driver ready in ${out}"
