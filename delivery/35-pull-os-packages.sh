#!/usr/bin/env bash
# Pulls the OS packages in os-packages.txt, with all their dependencies, into the bundle as a local package
# repository (os-packages/). We assume the lab has no package mirror (L1, S11), so the bundle must carry them.
#
# Runs on an EL9 system with dnf: the build container (build-in-container.sh) is Rocky 9.9, so the packages
# match Rocky 9.9. Sources: Rocky BaseOS, AppStream, and CRB; EPEL 9 (dkms); Rancher's RKE2 repository
# (rke2-selinux); NVIDIA's CUDA repository for RHEL 9 (DCGM). Every package must carry a valid signature from
# one of those four publishers' keys, which are shipped next to the packages.
#
#   OS_KERNEL=5.14.0-611.5.1.el9_7.x86_64 ./35-pull-os-packages.sh   also pull kernel-devel for that kernel
#
# The NVIDIA driver build needs kernel-devel for the exact kernel the GPU server runs. Until the lab's kernel
# is known, only the newest Rocky 9.9 kernel-devel is pulled, and deploy.sh says so if it does not match.
source "$(dirname "$0")/lib.sh"
require dnf createrepo_c rpmkeys curl
dnf download --help >/dev/null 2>&1 || die "dnf download is missing (package dnf-plugins-core)"
grep -q 'platform:el9' /etc/os-release || die "run this on an EL9 system; use build-in-container.sh"

out="${BUNDLE_DIR}/os-packages"
mkdir -p "${out}/rpms" "${out}/keys"

declare -A keys=(
    [RPM-GPG-KEY-Rocky-9]=https://dl.rockylinux.org/pub/rocky/RPM-GPG-KEY-Rocky-9
    [RPM-GPG-KEY-EPEL-9]=https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-9
    [RPM-GPG-KEY-Rancher]=https://rpm.rancher.io/public.key
    [RPM-GPG-KEY-NVIDIA-CUDA]=https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/D42D0685.pub
)
for k in "${!keys[@]}"; do download "${keys[${k}]}" "${out}/keys/${k}"; done

repos=(
    --enablerepo=baseos,appstream,crb
    --repofrompath=si-epel,https://dl.fedoraproject.org/pub/epel/9/Everything/x86_64/
    --repofrompath=si-rancher,https://rpm.rancher.io/rke2/stable/common/centos/9/noarch
    --repofrompath=si-nvidia,https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64
)
pkgs=$(awk '!/^#/ && NF {print $2}' "${DELIVERY_DIR}/os-packages.txt")
[[ -n "${OS_KERNEL:-}" ]] && pkgs+=" kernel-devel-${OS_KERNEL} kernel-headers-${OS_KERNEL}"

log "downloading $(wc -w <<<"${pkgs}") packages and every dependency"
# --alldeps: the whole dependency tree, not only what this container happens to lack, so a minimal node
# can install from the bundle alone.
# shellcheck disable=SC2086
dnf -q download "${repos[@]}" --resolve --alldeps --arch x86_64,noarch --destdir "${out}/rpms" ${pkgs}

log "checking every package signature against the four shipped keys"
tmpdb=$(mktemp -d)
trap 'rm -rf "${tmpdb}"' EXIT
rpm --dbpath "${tmpdb}" --initdb
for k in "${out}"/keys/*; do rpmkeys --dbpath "${tmpdb}" --import "${k}"; done
unsigned=$(rpmkeys --dbpath "${tmpdb}" --checksig "${out}"/rpms/*.rpm | grep -vE ': digests signatures OK$' || true)
[[ -z "${unsigned}" ]] || die "packages without a valid signature from a shipped key:"$'\n'"${unsigned}"

createrepo_c --quiet "${out}/rpms"
cp "${DELIVERY_DIR}/os-packages.txt" "${out}/os-packages.txt"
( cd "${out}/rpms" && ls -1 ./*.rpm | sed 's#^\./##' ) > "${out}/PACKAGES.txt"
manifest os-packages "$(wc -l < "${out}/PACKAGES.txt") RPMs for $(. /etc/os-release; echo "${NAME} ${VERSION_ID}") from Rocky, EPEL 9, Rancher RKE2 stable, NVIDIA CUDA rhel9 (kernel-devel: ${OS_KERNEL:-newest only})"
log "OS packages ready in ${out} ($(du -sh "${out}" | cut -f1), $(wc -l < "${out}/PACKAGES.txt") RPMs)"
