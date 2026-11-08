#!/usr/bin/env bash
# Installs a verified release bundle in the lab (or a single-node test install). Run as root, from inside the bundle.
# Run verify.sh first. Steps, in order (see docs/06-software-delivery.md):
#
#   On svc01 (or the single node):          ./deploy.sh server-init
#   On svc02 and svc03:                     ./deploy.sh server-join <svc01-ip>   (asks for the join token)
#   On gpu01:                               ./deploy.sh agent-join <svc01-ip>    (or RKE2_TOKEN_FILE=<file>)
#                                           ./deploy.sh driver
#                                           ./deploy.sh models
#   On svc01:                               ./deploy.sh platform
#                                           ./deploy.sh apps --chat-host H --api-host H --tls-cert F --tls-key F [--llm-gpus N] [--single-node | --rehearsal]
#                                           ./deploy.sh gateway-key
#   Any time on svc01:                      ./deploy.sh user-key <name>
#                                           ./deploy.sh status
#
# A single-node test install runs server-init, driver, models, platform, apps --single-node, gateway-key.
# --llm-gpus sets the language model replicas (default 3: four GPUs, one for Whisper).
# A rehearsal on the build workstation VM (no GPU) runs server-init, models, platform, apps --rehearsal:
# like --single-node, but with 0 model replicas, so nothing waits for a GPU that isn't there.
set -euo pipefail

BUNDLE="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="/var/lib/rancher/rke2/bin:${PATH}"
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
ARCH=amd64

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }
die() { printf '[%s] ERROR: %s\n' "$(date +%H:%M:%S)" "$*" >&2; exit 1; }
[[ ${EUID} -eq 0 ]] || die "run as root"

install_rke2() {  # type (server|agent)
    mkdir -p /var/lib/rancher/rke2/agent/images /etc/rancher/rke2
    cp "${BUNDLE}"/rke2/rke2-images.linux-${ARCH}.tar.zst "${BUNDLE}"/rke2/extra-image-*.tar \
        /var/lib/rancher/rke2/agent/images/
    INSTALL_RKE2_ARTIFACT_PATH="${BUNDLE}/rke2" INSTALL_RKE2_METHOD=tar INSTALL_RKE2_TYPE="$1" \
        sh "${BUNDLE}/rke2/install.sh"
}

json_field() { python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }

cmd="${1:-}"; shift || true
case "${cmd}" in
server-init)
    install_rke2 server
    cat > /etc/rancher/rke2/config.yaml <<EOF
tls-san:
  - $(hostname -f)
write-kubeconfig-mode: "0600"
EOF
    systemctl enable --now rke2-server
    log "RKE2 server up. Join token for the other nodes (also in /var/lib/rancher/rke2/server/node-token):"
    cat /var/lib/rancher/rke2/server/node-token
    ;;
server-join|agent-join)
    first="${1:?usage: $0 ${cmd} <svc01-ip>}"
    # The token goes in a root-only file, never on the command line or in the environment, where it
    # would land in shell history and the process list.
    tokfile=/etc/rancher/rke2/join-token
    install -d -m 700 /etc/rancher/rke2
    if [[ -n "${RKE2_TOKEN_FILE:-}" ]]; then
        [[ -s "${RKE2_TOKEN_FILE}" ]] || die "RKE2_TOKEN_FILE ${RKE2_TOKEN_FILE} is empty or missing"
        install -m 600 "${RKE2_TOKEN_FILE}" "${tokfile}"
    else
        read -rsp "Join token (printed by server-init on svc01): " token; echo
        [[ -n "${token}" ]] || die "no token given"
        ( umask 077; printf '%s\n' "${token}" > "${tokfile}" )
        unset token
    fi
    type=server; [[ "${cmd}" == agent-join ]] && type=agent
    install_rke2 "${type}"
    cat > /etc/rancher/rke2/config.yaml <<EOF
server: https://${first}:9345
token-file: ${tokfile}
EOF
    systemctl enable --now "rke2-${type}"
    log "joined ${first} as ${type}"
    ;;
driver)
    run=$(ls "${BUNDLE}"/nvidia-driver/NVIDIA-Linux-x86_64-*.run 2>/dev/null | head -1)
    [[ -n "${run}" ]] || die "no driver in bundle"
    rpm -q gcc make "kernel-devel-$(uname -r)" >/dev/null 2>&1 \
        || dpkg -s gcc make "linux-headers-$(uname -r)" >/dev/null 2>&1 \
        || die "install gcc, make, and kernel headers for $(uname -r) from the OS mirror first"
    # Blackwell GPUs require NVIDIA's open kernel modules.
    sh "${run}" --silent --dkms --kernel-module-type=open
    nvidia-smi
    ;;
models)
    mkdir -p /var/lib/models
    rsync -a "${BUNDLE}/models/" /var/lib/models/
    for sums in $(find -L /var/lib/models -name SHA256SUMS); do
        ( cd "$(dirname "${sums}")" && sha256sum --quiet -c SHA256SUMS ) || die "model check failed: ${sums}"
    done
    log "models in /var/lib/models ($(du -sh /var/lib/models | cut -f1)), checksums OK"
    ;;
platform)
    log "storage: local-path as the default storage class"
    kubectl apply -f "${BUNDLE}/rke2/local-path-storage.yaml"
    kubectl label namespace local-path-storage zarf.dev/agent=ignore --overwrite
    kubectl patch storageclass local-path \
        -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
    log "labels: service nodes run the database and gateway"
    nodes=$(kubectl get nodes -o name)
    if [[ $(wc -l <<<"${nodes}") -eq 1 ]]; then
        kubectl label ${nodes} node-role.si/service=true --overwrite
    else
        for n in ${SERVICE_NODES:-$(grep -o 'svc[0-9]*' <<<"${nodes}")}; do
            kubectl label "node/${n}" node-role.si/service=true --overwrite
        done
    fi
    log "labels: the node with /var/lib/models runs the embedding model"
    if [[ $(wc -l <<<"${nodes}") -eq 1 ]]; then
        kubectl label ${nodes} node-role.si/models=true --overwrite
    else
        for n in ${MODEL_NODES:-$(grep -o 'gpu[0-9]*' <<<"${nodes}")}; do
            kubectl label "node/${n}" node-role.si/models=true --overwrite
        done
    fi
    log "zarf init (in-cluster registry and image agent)"
    ( cd "${BUNDLE}/zarf" && ./zarf init --confirm )
    ;;
apps)
    chat="" api="" cert="" key="" single=0 rehearse=0 llm=3
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --chat-host) chat="$2"; shift 2 ;;
            --api-host)  api="$2";  shift 2 ;;
            --tls-cert)  cert="$2"; shift 2 ;;
            --tls-key)   key="$2";  shift 2 ;;
            --llm-gpus)  llm="$2";  shift 2 ;;
            --single-node) single=1; shift ;;
            --rehearsal) rehearse=1; shift ;;
            *) die "unknown option $1" ;;
        esac
    done
    [[ -n "${chat}" && -n "${api}" && -f "${cert}" && -f "${key}" ]] \
        || die "need --chat-host, --api-host, --tls-cert, --tls-key (certificate from the lab CA)"
    kubectl create namespace si --dry-run=client -o yaml | kubectl apply -f -
    kubectl -n si create secret tls si-tls --cert "${cert}" --key "${key}" --dry-run=client -o yaml | kubectl apply -f -
    kubectl -n si get secret litellm-masterkey >/dev/null 2>&1 \
        || kubectl -n si create secret generic litellm-masterkey --from-literal=masterkey="sk-$(openssl rand -hex 24)"
    pkg=$(ls "${BUNDLE}"/package/zarf-package-*.tar.zst | head -1)
    pg=3 components="transcription"
    if [[ ${single} -eq 1 ]]; then pg=1 llm=1 components=""; fi  # one GPU: no room for whisper
    if [[ ${rehearse} -eq 1 ]]; then pg=1 llm=0 components=""; fi  # no GPU: images load, nothing waits for one
    ( cd "${BUNDLE}/zarf" && ./zarf package deploy "${pkg}" --confirm \
        --set CHAT_HOST="${chat}" --set API_HOST="${api}" --set PG_INSTANCES="${pg}" --set VLLM_REPLICAS="${llm}" \
        ${components:+--components="${components}"} )
    log "deployed. Next: ./deploy.sh gateway-key"
    ;;
gateway-key|user-key)
    alias="open-webui"; [[ "${cmd}" == user-key ]] && alias="${1:?usage: $0 user-key <name>}"
    mk=$(kubectl -n si get secret litellm-masterkey -o jsonpath='{.data.masterkey}' | base64 -d)
    kubectl -n si port-forward svc/litellm 14000:4000 >/dev/null 2>&1 &
    pf=$!; trap 'kill ${pf} 2>/dev/null || true' EXIT
    for i in $(seq 30); do
        curl -fsS -o /dev/null http://127.0.0.1:14000/health/liveliness && break
        (( i < 30 )) || die "gateway did not answer through the port-forward in 30 s (kubectl -n si get pods)"
        sleep 1
    done
    newkey=$(curl -fsS http://127.0.0.1:14000/key/generate \
        -H "Authorization: Bearer ${mk}" -H 'Content-Type: application/json' \
        -d "{\"key_alias\": \"${alias}\"}" | json_field key)
    if [[ "${cmd}" == gateway-key ]]; then
        kubectl -n si create secret generic open-webui-gateway-key --from-literal=key="${newkey}" \
            --dry-run=client -o yaml | kubectl apply -f -
        kubectl -n si rollout restart statefulset/open-webui
        log "chat page now uses its own gateway key"
    else
        log "key for ${alias} (give it to them over an approved channel; it is shown once):"
        echo "${newkey}"
    fi
    ;;
status)
    kubectl get nodes -o wide
    kubectl get pods -A -o wide | grep -vE 'Running|Completed' || log "all pods running"
    kubectl -n si get pods,svc,ingress
    command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=index,name,temperature.gpu,power.draw,memory.used --format=csv
    ;;
*)
    sed -n '2,/^set -euo/p' "$0" | sed '$d'; exit 1 ;;
esac
