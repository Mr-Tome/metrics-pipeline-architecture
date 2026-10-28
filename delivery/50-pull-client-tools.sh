#!/usr/bin/env bash
# Pulls what analysts install on their own machines:
#   - Python wheels for Jupyter AI and the OpenAI client (Linux and Windows)
#   - The Continue extension for VS Code (from Open VSX)
# MATLAB needs nothing extra; it calls the gateway API with webwrite (see docs/06).
source "$(dirname "$0")/lib.sh"
require curl jq python3

out="${BUNDLE_DIR}/clients"
mkdir -p "${out}"

declare -A platforms=(
    [linux]="--platform manylinux2014_x86_64 --platform manylinux_2_28_x86_64 --platform manylinux_2_17_x86_64"
    [windows]="--platform win_amd64"
)
: > "${out}/RESOLVED.txt"
for os in linux windows; do
    log "Python wheels for ${os}, Python ${CLIENT_PYTHON_VERSION}"
    # shellcheck disable=SC2086  # the platform flags are meant to split
    python3 -m pip download -q -r "${DELIVERY_DIR}/client-requirements.txt" \
        --dest "${out}/wheels-${os}" --only-binary=:all: ${platforms[${os}]} \
        --python-version "${CLIENT_PYTHON_VERSION}" --implementation cp
    ls "${out}/wheels-${os}" | sed "s/^/${os}: /" >> "${out}/RESOLVED.txt"
done

for target in linux-x64 win32-x64; do
    meta=$(curl -fsSL "https://open-vsx.org/api/Continue/continue/${target}/${CONTINUE_VSCODE_VERSION}")
    ver=$(jq -r .version <<<"${meta}")
    download "$(jq -r .files.download <<<"${meta}")" "${out}/continue-${ver}-${target}.vsix"
    echo "vscode: Continue.continue ${ver} ${target}" >> "${out}/RESOLVED.txt"
done

manifest "client tools: see clients/RESOLVED.txt"
log "client tools ready in ${out}"
