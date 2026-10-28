#!/usr/bin/env bash
# Pulls the RKE2 air-gap install artifacts and verifies them against the upstream checksums.
source "$(dirname "$0")/lib.sh"
require curl sha256sum

out="${BUNDLE_DIR}/rke2"
mkdir -p "${out}"
base="https://github.com/rancher/rke2/releases/download/$(urlver "${RKE2_VERSION}")"

for f in "rke2-images.linux-${ARCH}.tar.zst" "rke2.linux-${ARCH}.tar.gz" "sha256sum-${ARCH}.txt"; do
    download "${base}/${f}" "${out}/${f}"
done
download "https://get.rke2.io" "${out}/install.sh"
chmod +x "${out}/install.sh"

log "verifying RKE2 checksums"
( cd "${out}" && grep -E "rke2-images.linux-${ARCH}.tar.zst|rke2.linux-${ARCH}.tar.gz" "sha256sum-${ARCH}.txt" | sha256sum -c - )

# Local-path storage: the first storage class, needed by the Zarf registry and PostgreSQL.
# Saved as image tarballs; RKE2 imports any tarball in agent/images/ at startup, so this
# works before a registry exists.
require skopeo
lp="rancher/local-path-provisioner:${LOCAL_PATH_VERSION}"
download "https://raw.githubusercontent.com/rancher/local-path-provisioner/${LOCAL_PATH_VERSION}/deploy/local-path-storage.yaml" \
    "${out}/local-path-storage.yaml"
for ref in "docker.io/${lp}" "${BUSYBOX_IMAGE}"; do
    tarball="${out}/extra-image-$(basename "${ref%%:*}").tar"
    [[ -s "${tarball}" ]] || skopeo copy --override-os linux --override-arch "${ARCH}" \
        "docker://${ref}" "docker-archive:${tarball}:${ref#docker.io/}"
done
# The upstream manifest pins busybox by bare name; point it at the exact version we ship.
sed -i "s#image: busybox\b.*#image: ${BUSYBOX_IMAGE#docker.io/library/}#" "${out}/local-path-storage.yaml"

manifest "rke2 ${RKE2_VERSION} from ${base}"
manifest "local-path-provisioner ${LOCAL_PATH_VERSION}, ${BUSYBOX_IMAGE}"
log "RKE2 ${RKE2_VERSION} ready in ${out}"
