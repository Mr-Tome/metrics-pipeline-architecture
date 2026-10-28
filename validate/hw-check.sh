#!/usr/bin/env bash
# Hardware acceptance check for a GPU or service node. Run as root after the OS is installed.
#
#   ./hw-check.sh --gpus 2          lab gpu01 (2 GPUs at the 20-user size)
#   ./hw-check.sh --gpus 1          staging stg01
#   ./hw-check.sh --gpus 0          service node
#   ./hw-check.sh --gpus 2 --burn   adds a 24-hour-capable DCGM stress run (needs DCGM installed)
#
# Prints PASS/FAIL per check and exits non-zero if anything failed.
set -uo pipefail

gpus=0 burn=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --gpus) gpus="$2"; shift 2 ;;
        --burn) burn=1; shift ;;
        *) echo "usage: $0 --gpus N [--burn]"; exit 2 ;;
    esac
done

failed=0
pass() { printf 'PASS  %s\n' "$*"; }
fail() { printf 'FAIL  %s\n' "$*"; failed=1; }
info() { printf '      %s\n' "$*"; }

echo "== $(hostname) $(date -u +%Y-%m-%dT%H:%MZ)"
info "CPU: $(lscpu | sed -n 's/^Model name: *//p') x $(lscpu | sed -n 's/^Socket(s): *//p') sockets"
mem_gb=$(awk '/MemTotal/{printf "%d", $2/1048576}' /proc/meminfo)
info "Memory: ${mem_gb} GB"

# NVMe drives
nvme=$(lsblk -dno NAME,SIZE,MODEL | grep '^nvme' || true)
if [[ -n "${nvme}" ]]; then pass "NVMe drives found"; sed 's/^/      /' <<<"${nvme}"
else fail "no NVMe drives found"; fi

# NIC links: every port that has a cable should be at 25G
for dev in /sys/class/net/*; do
    n=$(basename "${dev}")
    [[ -e "${dev}/device" && "$(cat "${dev}/operstate")" == up ]] || continue
    speed=$(cat "${dev}/speed" 2>/dev/null || echo 0)
    if (( speed >= 25000 )); then pass "${n} link ${speed} Mb/s"
    elif (( speed >= 1000 )); then info "${n} link ${speed} Mb/s (BMC/management or 10G fallback?)"
    else fail "${n} link speed ${speed}"; fi
done

if (( gpus > 0 )); then
    if ! command -v nvidia-smi >/dev/null; then
        fail "nvidia-smi not found (driver not installed: deploy.sh driver)"
    else
        found=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
        (( found == gpus )) && pass "${found} GPUs present" || fail "expected ${gpus} GPUs, found ${found}"
        while IFS=, read -r idx name gen width temp plimit mem; do
            info "GPU${idx}:${name}, PCIe Gen${gen} x${width}, ${temp} C, limit ${plimit}, ${mem}"
            [[ "${gen// /}" == 5 && "${width// /}" == 16 ]] && pass "GPU${idx} on PCIe Gen5 x16" \
                || fail "GPU${idx} link Gen${gen} x${width}; reseat the card or check the slot (idle GPUs may show a lower Gen, re-run under load)"
            (( ${temp// /} < 60 )) && pass "GPU${idx} idle temp ${temp} C" || fail "GPU${idx} idle temp ${temp} C is high; check airflow and shroud"
        done < <(nvidia-smi --query-gpu=index,name,pcie.link.gen.max,pcie.link.width.current,temperature.gpu,power.limit,memory.total --format=csv,noheader)
        nvidia-smi -q | grep -qi 'Persistence Mode *: Enabled' || info "tip: nvidia-smi -pm 1 keeps the driver loaded"
    fi
    if (( burn == 1 )); then
        if command -v dcgmi >/dev/null; then
            echo "== DCGM level 3 diagnostic (about 30-60 minutes)"
            dcgmi diag -r 3 && pass "dcgmi diag -r 3" || fail "dcgmi diag -r 3"
        else
            fail "--burn needs DCGM (datacenter-gpu-manager) installed on the host"
        fi
    fi
fi

# BMC reachable from the OS (if ipmitool is present)
if command -v ipmitool >/dev/null; then
    ipmitool lan print 2>/dev/null | grep -E 'IP Address  |MAC Address' | sed 's/^/      BMC /'
    ipmitool sdr type 'Power Supply' 2>/dev/null | sed 's/^/      /'
fi

echo
(( failed == 0 )) && echo "RESULT: PASS" || echo "RESULT: FAIL"
exit "${failed}"
