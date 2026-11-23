#!/usr/bin/env bash
# Blocks and logs every new outbound connection from this VM and its pods to anything outside the staging
# network, so the install runs as if there were no internet (the lab has none). The staging VMs keep their
# internet route, which RKE2 needs (a default route), but nothing gets out. Each attempt is logged with the
# prefix SI-EGRESS, which is the tripwire for check C16.
#
#   sudo ./egress-block.sh on 10.20.30.0/24   allow only this network (the three VMs), block the rest
#   sudo ./egress-block.sh status             rules, blocked-packet counters, and the logged attempts
#   sudo ./egress-block.sh off                remove the block (for example, to pull a new bundle)
#
# Incoming connections (your SSH session, the browser test) are not affected. The block survives a reboot
# (unit si-egress.service), so the reboot check (C17) also runs blocked.
set -euo pipefail
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
[[ ${EUID} -eq 0 ]] || die "run as root"
rules=/etc/si-egress.nft unit=/etc/systemd/system/si-egress.service

case "${1:-}" in
on)
    shift; [[ $# -ge 1 ]] || die "give the staging network, for example: on 10.20.30.0/24"
    allow=$(IFS=,; echo "$*")
    # 10.42/16 and 10.43/16 are RKE2's pod and service networks.
    cat > "${rules}" <<NFT
table inet si_egress
delete table inet si_egress
table inet si_egress {
    set allow4 {
        type ipv4_addr; flags interval; auto-merge
        elements = { 127.0.0.0/8, 10.42.0.0/16, 10.43.0.0/16, 255.255.255.255, ${allow} }
    }
    chain host_out {
        type filter hook output priority 0; policy accept;
        oif "lo" accept
        ct state established,related accept
        ip daddr @allow4 accept
        ip6 daddr { ::1, fe80::/10, ff00::/8 } accept
        limit rate 20/second log prefix "SI-EGRESS host " level warn
        counter drop
    }
    chain pod_out {
        type filter hook forward priority 0; policy accept;
        ct state established,related accept
        ip daddr @allow4 accept
        ip6 daddr { fe80::/10, ff00::/8 } accept
        limit rate 20/second log prefix "SI-EGRESS pod " level warn
        counter drop
    }
}
NFT
    nft -f "${rules}"
    cat > "${unit}" <<UNIT
[Unit]
Description=Staging egress block (SI)
After=network-pre.target
Before=rke2-server.service rke2-agent.service
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/nft -f ${rules}
ExecStop=/usr/sbin/nft delete table inet si_egress
[Install]
WantedBy=multi-user.target
UNIT
    systemctl daemon-reload
    systemctl enable si-egress.service >/dev/null
    echo "egress blocked except ${allow}. Test: curl -m 5 https://github.com (must fail)"
    ;;
off)
    systemctl disable --now si-egress.service 2>/dev/null || true
    nft delete table inet si_egress 2>/dev/null || true
    rm -f "${unit}"; systemctl daemon-reload
    echo "egress block removed"
    ;;
status)
    nft list table inet si_egress 2>/dev/null || echo "no block in place"
    echo "--- logged attempts since boot:"
    journalctl -k -b --no-pager -g 'SI-EGRESS' || echo "none"
    ;;
*)
    sed -n '2,/^set -euo/p' "$0" | sed '$d'; exit 1 ;;
esac
