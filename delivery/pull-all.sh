#!/usr/bin/env bash
# Builds a complete release bundle on the connected build workstation.
#
#   ./pull-all.sh                     full bundle
#   SKIP=30 ./pull-all.sh             skip steps by number (example: models already pulled)
#   BUNDLE_DIR=/mnt/xfer/b1 ./pull-all.sh
#
# Each step is safe to re-run; downloads resume and finished files are skipped.
source "$(dirname "$0")/lib.sh"

steps=(00-check-tools 01-check-latest 10-pull-rke2 15-pull-zarf 20-build-zarf-package
       30-pull-models 40-pull-vuln-db 50-pull-client-tools 60-pull-nvidia-driver 90-seal)

exec > >(tee -a "${BUNDLE_DIR%/}.pull.log") 2>&1  # log sits next to the bundle, not in it, so sealing is not disturbed
log "bundle: ${BUNDLE_DIR}"
for step in "${steps[@]}"; do
    if [[ " ${SKIP:-} " == *" ${step%%-*} "* ]]; then
        log "=== ${step}: skipped"
        continue
    fi
    log "=== ${step}"
    BUNDLE_DIR="${BUNDLE_DIR}" bash "${DELIVERY_DIR}/${step}.sh"
done
log "done. Next: move ${BUNDLE_DIR} by the approved media process, then run intake/verify.sh on the far side."
