#!/usr/bin/env bash
# Pulls what analysts install on their own machines:
#   - Python wheels for Jupyter AI and the OpenAI client (Linux and Windows, every version in
#     CLIENT_PYTHON_VERSIONS). A Python version too new for some of Jupyter AI's packages (no wheels
#     published yet) gets the OpenAI client only (client-requirements-core.txt); RESOLVED.txt lists which.
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
# One folder per OS holds the wheels for every Python version; pip picks the matching ones at install.
pipdl() {  # os python-version requirements-file
    # shellcheck disable=SC2086  # the platform flags are meant to split
    python3 -m pip download -q -r "$3" --dest "${out}/wheels-$1" --only-binary=:all: ${platforms[$1]} \
        --python-version "$2" --implementation cp
}
support=()
for os in linux windows; do
    for py in ${CLIENT_PYTHON_VERSIONS}; do
        log "Python wheels for ${os}, Python ${py}"
        if pipdl "${os}" "${py}" "${DELIVERY_DIR}/client-requirements.txt" 2> "${out}/.pip.err"; then
            support+=("${os} python ${py}: Jupyter AI + OpenAI client")
        else
            warn "${os} python ${py}: $(grep -m1 -oE 'No matching distribution found for [^ ]+' "${out}/.pip.err" || tail -1 "${out}/.pip.err")"
            warn "${os} python ${py}: no wheels yet for part of Jupyter AI; pulling the OpenAI client only"
            pipdl "${os}" "${py}" "${DELIVERY_DIR}/client-requirements-core.txt" \
                || die "${os} python ${py}: even the OpenAI client has no wheels; drop ${py} from CLIENT_PYTHON_VERSIONS"
            support+=("${os} python ${py}: OpenAI client only (Jupyter AI not available yet)")
        fi
    done
    ls "${out}/wheels-${os}" | sed "s/^/${os}: /" >> "${out}/RESOLVED.txt"
done
rm -f "${out}/.pip.err"
printf '%s\n' "${support[@]}" > "${out}/SUPPORT.txt"
log "Python support in this bundle:"; sed 's/^/    /' "${out}/SUPPORT.txt"

for target in linux-x64 win32-x64; do
    meta=$(curl -fsSL "https://open-vsx.org/api/Continue/continue/${target}/${CONTINUE_VSCODE_VERSION}")
    ver=$(jq -r .version <<<"${meta}")
    download "$(jq -r .files.download <<<"${meta}")" "${out}/continue-${ver}-${target}.vsix"
    echo "vscode: Continue.continue ${ver} ${target}" >> "${out}/RESOLVED.txt"
done

manifest clients "see clients/SUPPORT.txt and clients/RESOLVED.txt"
log "client tools ready in ${out}"
