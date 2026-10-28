#!/usr/bin/env bash
# Pulls the Zarf CLI and the matching Zarf init package (in-cluster registry and agent).
# The init package is what lets a bare RKE2 cluster accept images with no internet.
source "$(dirname "$0")/lib.sh"
require curl sha256sum

out="${BUNDLE_DIR}/zarf"
mkdir -p "${out}"
base="https://github.com/zarf-dev/zarf/releases/download/${ZARF_VERSION}"
bin="zarf_${ZARF_VERSION}_Linux_${ARCH}"
init="zarf-init-${ARCH}-${ZARF_VERSION}.tar.zst"

download "${base}/checksums.txt" "${out}/checksums.txt"
download "${base}/${bin}" "${out}/${bin}"
download "${base}/${init}" "${out}/${init}"

log "verifying Zarf checksums"
( cd "${out}" && grep -E " (${bin}|${init})$" checksums.txt | sha256sum -c - )
chmod +x "${out}/${bin}"
ln -sf "${bin}" "${out}/zarf"

manifest "zarf ${ZARF_VERSION} cli + init package from ${base}"
log "Zarf ${ZARF_VERSION} ready in ${out}"
