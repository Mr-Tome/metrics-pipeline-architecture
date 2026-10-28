#!/usr/bin/env bash
# Network throughput test between nodes, with iperf3.
#
#   On the target node:  ./net-test.sh server
#   On another node:     ./net-test.sh client <target-ip>
#
# Expect about 23 Gb/s per 25G link node to node in the rack, and close to the desk port speed
# (about 940 Mb/s on 1G) from an analyst workstation. See docs/03, section 5.
set -euo pipefail
command -v iperf3 >/dev/null || { echo "install iperf3 from the OS mirror"; exit 1; }

case "${1:-}" in
server)
    echo "iperf3 server on port 5201 (Ctrl-C to stop)"
    iperf3 -s ;;
client)
    target="${2:?usage: $0 client <target-ip>}"
    echo "== single stream, 20 s"
    iperf3 -c "${target}" -t 20 | tail -4
    echo "== 4 parallel streams, 20 s (fills a bonded pair)"
    iperf3 -c "${target}" -t 20 -P 4 | tail -4
    echo "== reverse direction"
    iperf3 -c "${target}" -t 20 -P 4 -R | tail -4 ;;
*)
    sed -n '2,8p' "$0"; exit 2 ;;
esac
