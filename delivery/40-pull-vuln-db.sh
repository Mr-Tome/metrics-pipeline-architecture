#!/usr/bin/env bash
# Pulls the Trivy scanner and its vulnerability databases, so scans inside staging and the lab
# use current data with no internet.
source "$(dirname "$0")/lib.sh"
require curl sha256sum tar

out="${BUNDLE_DIR}/scanner"
mkdir -p "${out}/bin" "${out}/trivy-cache"
base="https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}"
tgz="trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz"
sums="trivy_${TRIVY_VERSION}_checksums.txt"

download "${base}/${sums}" "${out}/${sums}"
download "${base}/${tgz}" "${out}/${tgz}"
( cd "${out}" && grep " ${tgz}$" "${sums}" | sha256sum -c - )
tar -xzf "${out}/${tgz}" -C "${out}/bin" trivy

log "downloading vulnerability databases"
"${out}/bin/trivy" image --download-db-only --cache-dir "${out}/trivy-cache"
"${out}/bin/trivy" image --download-java-db-only --cache-dir "${out}/trivy-cache"

manifest "trivy ${TRIVY_VERSION} + vulnerability DB downloaded $(date -u +%Y-%m-%dT%H:%MZ)"
log "scanner ready in ${out}. Inside the lab: trivy image --skip-db-update --skip-java-db-update --cache-dir ${out##*/}/trivy-cache ..."
