#!/usr/bin/env bash
# Installs a verified release bundle in the lab (or a single-node test install). Run as root, from inside the bundle.
# Run verify.sh first. Steps, in order (see docs/software/2-software-delivery.md):
#
#   On every node, first (no package mirror): ./deploy.sh os-packages        (add --gpu on gpu01)
#   On svc01 (or the single node):          ./deploy.sh server-init
#   On svc02 and svc03:                     ./deploy.sh server-join <svc01-ip>   (asks for the join token)
#   On gpu01:                               ./deploy.sh agent-join <svc01-ip>    (or RKE2_TOKEN_FILE=<file>)
#                                           ./deploy.sh driver
#                                           ./deploy.sh models
#   On svc01:                               ./deploy.sh platform
#                                           ./deploy.sh apps --chat-host H [--api-host H] --tls-cert F --tls-key F [--llm-gpus N] [--single-node | --rehearsal | --staging]
#                                           ./deploy.sh gateway-key
#   Any time on svc01:                      ./deploy.sh user-key <name>
#                                           ./deploy.sh status
#
# A single-node test install runs server-init, driver, models, platform, apps --single-node, gateway-key.
# --llm-gpus sets the language model replicas (default 3: four GPUs, one for Whisper).
# A rehearsal on the build workstation VM (no GPU) runs server-init, models, platform, apps --rehearsal:
# like --single-node, but with 0 model replicas, so nothing waits for a GPU that isn't there.
# Staging (three VMs, no GPU; docs/software/4-staging-runbook.md) runs the lab sequence without driver, with
# SERVICE_NODES and MODEL_NODES set to the VM names for platform, and apps --staging: three PostgreSQL
# instances, 0 model replicas, no GPU Whisper.
set -euo pipefail

BUNDLE="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="/var/lib/rancher/rke2/bin:${PATH}"
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
ARCH=amd64

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }
die() { printf '[%s] ERROR: %s\n' "$(date +%H:%M:%S)" "$*" >&2; exit 1; }
[[ ${EUID} -eq 0 ]] || die "run as root"

install_rke2() {  # type (server|agent)
    # RKE2's known issues for RHEL-family hosts: firewalld conflicts with its Canal network, NetworkManager
    # must leave the network's interfaces alone, and nm-cloud-setup must be off.
    if systemctl is-active --quiet firewalld && [[ "${ALLOW_FIREWALLD:-0}" != 1 ]]; then
        die "firewalld is running. RKE2 says to turn it off (systemctl disable --now firewalld). If the lab requires it (S27), open RKE2's ports and set ALLOW_FIREWALLD=1."
    fi
    if systemctl is-active --quiet NetworkManager; then
        cat > /etc/NetworkManager/conf.d/rke2-canal.conf <<'NM'
[keyfile]
unmanaged-devices=interface-name:flannel*;interface-name:cali*;interface-name:tunl*;interface-name:vxlan.calico;interface-name:vxlan-v6.calico;interface-name:wireguard.cali;interface-name:wg-v6.cali
NM
        systemctl reload NetworkManager
    fi
    systemctl disable --now nm-cloud-setup.service nm-cloud-setup.timer >/dev/null 2>&1 || true
    mkdir -p /var/lib/rancher/rke2/agent/images /etc/rancher/rke2
    cp "${BUNDLE}"/rke2/rke2-images.linux-${ARCH}.tar.zst "${BUNDLE}"/rke2/extra-image-*.tar \
        /var/lib/rancher/rke2/agent/images/
    INSTALL_RKE2_ARTIFACT_PATH="${BUNDLE}/rke2" INSTALL_RKE2_METHOD=tar INSTALL_RKE2_TYPE="$1" \
        sh "${BUNDLE}/rke2/install.sh"
}

# selinux_config: RKE2 must be told when SELinux is enforcing, and then needs rke2-selinux (os-packages).
selinux_config() {
    if command -v getenforce >/dev/null 2>&1 && [[ "$(getenforce)" == Enforcing ]]; then
        rpm -q rke2-selinux >/dev/null 2>&1 || die "SELinux is enforcing but rke2-selinux is not installed; run ./deploy.sh os-packages first"
        echo "selinux: true"
    fi
}

json_field() { python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }

cmd="${1:-}"; shift || true
case "${cmd}" in
os-packages)
    # Installs the OS packages from the bundle (35-pull-os-packages.sh) with every other repository off, so
    # it works with no package mirror. --gpu adds the driver build tools and DCGM.
    gpu=0; [[ "${1:-}" == --gpu ]] && gpu=1
    repo="${BUNDLE}/os-packages"
    [[ -f "${repo}/rpms/repodata/repomd.xml" ]] || die "no os-packages repository in the bundle"
    for k in "${repo}"/keys/*; do rpm --import "${k}"; done
    pkgs=$(awk -v gpu="${gpu}" '!/^#/ && NF && ($1 == "all" || (gpu && $1 == "gpu")) {print $2}' "${repo}/os-packages.txt")
    if [[ ${gpu} -eq 1 ]]; then
        # The driver build needs kernel-devel for the running kernel, not the newest one.
        kver="$(uname -r)"
        pkgs=$(sed -e "s/^kernel-devel$/kernel-devel-${kver}/" -e "s/^kernel-headers$/kernel-headers-${kver%.*}/" <<<"${pkgs}")
        grep -q "^kernel-devel-${kver%.x86_64}" "${repo}/PACKAGES.txt" \
            || die "the bundle has no kernel-devel for this kernel (${kver}); re-pull with OS_KERNEL=${kver}"
    fi
    # shellcheck disable=SC2086
    dnf -y --disablerepo='*' --enablerepo=si-bundle \
        --repofrompath="si-bundle,file://${repo}/rpms" --setopt=si-bundle.gpgcheck=1 install ${pkgs}
    log "OS packages installed from the bundle"
    ;;
server-init)
    sel=$(selinux_config) || exit 1
    install_rke2 server
    cat > /etc/rancher/rke2/config.yaml <<EOF
tls-san:
  - $(hostname -f)
write-kubeconfig-mode: "0600"
ingress-controller: traefik
${sel}
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
    sel=$(selinux_config) || exit 1
    install_rke2 "${type}"
    cat > /etc/rancher/rke2/config.yaml <<EOF
server: https://${first}:9345
token-file: ${tokfile}
EOF
    # Servers must agree on the ingress controller (Traefik is also the v1.37 default; this makes it explicit).
    [[ "${type}" == server ]] && echo "ingress-controller: traefik" >> /etc/rancher/rke2/config.yaml
    [[ -n "${sel}" ]] && echo "${sel}" >> /etc/rancher/rke2/config.yaml
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
    for role in service models; do
        [[ -n "$(kubectl get nodes -l "node-role.si/${role}=true" -o name)" ]] \
            || die "no node labeled node-role.si/${role}; set SERVICE_NODES and MODEL_NODES to node names (kubectl get nodes)"
    done
    log "zarf init (in-cluster registry and image agent)"
    ( cd "${BUNDLE}/zarf" && ./zarf init --confirm )
    ;;
apps)
    chat="" api="" cert="" key="" single=0 rehearse=0 staging=0 llm=3
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --chat-host) chat="$2"; shift 2 ;;
            --api-host)  api="$2";  shift 2 ;;
            --tls-cert)  cert="$2"; shift 2 ;;
            --tls-key)   key="$2";  shift 2 ;;
            --llm-gpus)  llm="$2";  shift 2 ;;
            --single-node) single=1; shift ;;
            --rehearsal) rehearse=1; shift ;;
            --staging)   staging=1;  shift ;;
            *) die "unknown option $1" ;;
        esac
    done
    [[ -n "${chat}" && -f "${cert}" && -f "${key}" ]] \
        || die "need --chat-host, --tls-cert, --tls-key (certificate from the lab CA)"
    # Phase 1 is the chat page only. --api-host opens the gateway API to analyst tools (a later phase).
    api_on=false; [[ -n "${api}" ]] && api_on=true || api="unused.invalid"
    kubectl create namespace si --dry-run=client -o yaml | kubectl apply -f -
    kubectl -n si create secret tls si-tls --cert "${cert}" --key "${key}" --dry-run=client -o yaml | kubectl apply -f -
    kubectl -n si get secret litellm-masterkey >/dev/null 2>&1 \
        || kubectl -n si create secret generic litellm-masterkey --from-literal=masterkey="sk-$(openssl rand -hex 24)"
    pkg=$(ls "${BUNDLE}"/package/zarf-package-*.tar.zst | head -1)
    pg=3 components="transcription"
    if [[ ${single} -eq 1 ]]; then pg=1 llm=1 components=""; fi  # one GPU: no room for whisper
    if [[ ${rehearse} -eq 1 ]]; then pg=1 llm=0 components=""; fi  # no GPU: images load, nothing waits for one
    if [[ ${staging} -eq 1 ]]; then pg=3 llm=0 components=""; fi   # three VMs, no GPU: real database failover
    ( cd "${BUNDLE}/zarf" && ./zarf package deploy "${pkg}" --confirm \
        --set CHAT_HOST="${chat}" --set API_HOST="${api}" --set API_INGRESS="${api_on}" --set PG_INSTANCES="${pg}" --set VLLM_REPLICAS="${llm}" \
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
