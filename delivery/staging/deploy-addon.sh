#!/usr/bin/env bash
# Deploys the staging add-on (CPU stand-ins). Run as root on the model node (the VM named in MODEL_NODES),
# after ./deploy.sh apps --staging and gateway-key:
#
#   ./deploy-addon.sh /srv/si/staging-addon /srv/si/bundle
set -euo pipefail
addon="${1:?usage: deploy-addon.sh ADDON_DIR BUNDLE_DIR}"
bundle="${2:?usage: deploy-addon.sh ADDON_DIR BUNDLE_DIR}"
export PATH="/var/lib/rancher/rke2/bin:${PATH}" KUBECONFIG=/etc/rancher/rke2/rke2.yaml
log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }
die() { printf '[%s] ERROR: %s\n' "$(date +%H:%M:%S)" "$*" >&2; exit 1; }
[[ ${EUID} -eq 0 ]] || die "run as root"
node="$(kubectl get nodes -l node-role.si/models=true -o jsonpath='{.items[0].metadata.name}')"
[[ "${node}" == "$(hostname -s)" || "${node}" == "$(hostname -f)" || "${node}" == "$(hostname)" ]] \
    || die "run this on the model node (${node}); the stand-in weights must be on its disk"

mkdir -p /var/lib/models/staging
rsync -a "${addon}/models/" /var/lib/models/staging/
( cd /var/lib/models/staging/standin-llm && sha256sum --quiet -c SHA256SUMS ) || die "stand-in model checksum failed"
log "stand-in model in /var/lib/models/staging, checksums OK"

pkg=$(ls "${addon}"/package/zarf-package-si-staging-addon-*.tar.zst | head -1)
( cd "${bundle}/zarf" && ./zarf package deploy "${pkg}" --confirm )
log "add-on deployed. The stand-in model takes a few minutes to load: kubectl -n si get pods -w"
