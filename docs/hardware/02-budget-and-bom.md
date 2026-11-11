# 02. Budget and BOM

**Track:** Hardware (facility, network, rack, purchasing). Security decisions are in the [Cyber Security package](../cyber/README.md).

Target: **$250,000.00**. Source of the base numbers: `Metrics_Analysis_Pipeline_Hardware_BOM.xlsx`.

## 1. Which tier fits

The BOM tiers include a staging environment (one GPU server with one GPU, $66,038). The lab decided
not to have staging, so the lab-only figures are what count.

| Tier | BOM with staging | Lab only (no staging) | Lab only + additions (section 2) | Fits $250k? |
|---|---|---|---|---|
| 20 users | $221,086 | $155,048 | about $202,000 | Yes |
| **50 users** | $257,578 | **$191,540** | **$238,517 + switch license** | **Yes, $11,483 left** |
| 100 users | $382,869 | $316,831 | about $364,000 | No |

**Decision: buy the 50-user tier, no staging.** It fills all four GPU slots in gpu01 and keeps all three
service nodes. The money that was staging pays for the two extra GPUs, the Cisco Nexus switch, and the install items,
with about $11,500 left before the switch license (section 3).
Growing to 100 users later means adding a second GPU server in rack 2. Nothing gets replaced.

BOM sizing (`Assumptions` tab, column C): 50 users, 10 simultaneous requests at peak, 2 GPUs for the
language model plus 1 for speech-to-text and document search = 3 GPUs needed. The fourth GPU runs a
third language model copy, which also gives headroom during updates (one copy at a time is replaced).

**What dropping staging costs.** Every install and update now lands first on the production rack.
[04-prototype-plan.md](../software/04-prototype-plan.md) covers how the build workstation rehearses each bundle
instead, and how the four GPUs let an update roll out one copy at a time.

## 2. What the BOM leaves out

The BOM's `Assumptions` tab, section 5, excludes racks, power distribution, cooling, and facility work.
The site visit confirmed the lab supplies racks (Vertiv VR3300), rack PDUs (Vertiv Geist, two per rack),
and cooling (Liebert CRV). The items below are still on us. Without them the rack can't be connected
or set up.

Part numbers and links are in the quote request, [08a](08a-quote-servers-submitted.md) and [08b](08b-quote-network-and-rack.md).

| ID | Item | Qty | Est. total | Why |
|---|---|---|---|---|
| A1 | Uplink lot: 4 x Cisco QSFP-40/100-SRBD (2 per end), OM4 multimode LC cords (3 x 8 m, 3 x 15 m), and a separate 10G management link (QSA adapter, 2 x Cisco SFP-10G-SR-S) | 1 lot | $9,963.87 | Our switch to the lab network. The BOM line "Cables and optics" ($1,000) covers only the in-rack 25G cables. |
| A2 | 1G management switch, Cisco C1300-24T-4X | 1 | $1,047.99 | Keeps server management (BMC) off the data network |
| A3 | Blanking panels (80, both racks), Cat6 patch cables (10 ft) | 1 lot | $935.92 | The racks have none, and cold aisle containment does not work with open U spaces |
| A4 | Encrypted SSD, 4 TB, FIPS 140-2 | 2 | $5,549.98 | Software and model transfer. Use the lab's approved type; drop if the lab provides it (saves $5,550). |
| A5 | Rack console, 1U LCD and keyboard | 1 | $1,200 | First boot and BIOS setup. The lab has no crash cart. |
| A6 | Setup kit (labels, velcro, cage nuts, ESD strap, fiber cleaner, console cables, hand tools) | 1 lot | $500 | Needed on install day |
| | **Additions total** | | **$19,197.76** | |

Only if needed, not in the total:

| ID | Item | Est. total | When |
|---|---|---|---|
| C1 | Red Hat Enterprise Linux Server subscriptions, 4 servers (gpu01, svc01-svc03), 1 year | $5,600 per year | Only if the lab requires RHEL. Rocky Linux 9 is free. Not in the original BOM. |

A1-A4 use CDW's advertised prices on 2026-11-06 (links in 08b); A5, A6, and the Cat6 cables are estimates.
Get quotes before you finalize.

**Terms used above:**

- **Rack PDU:** a power strip built for a rack. The ones already in the racks are the Vertiv Geist
  strips on the left and right. Each server cord plugs into one of their outlets.
- **Uplink optics:** the transceiver modules that plug into a switch port and turn the signal into
  light for a fiber cable. One goes in each end of the link. Each end must be coded for its own switch
  brand. Both our switch and the lab's are Cisco, so every optic is a Cisco part, checked in Cisco's
  compatibility matrix for the switch it goes in.
- **Patch cords:** fiber cables from optic to optic. Ours run straight from sw01 and oob01 to the lab C9500X-28C8D (8 m or 15 m).
- **Management switch:** a small separate switch for each server's BMC port, the built-in remote
  console used for power and BIOS control.
- **Blanking panels:** flat plates that cover empty rack spaces. They stop warm exhaust air from
  leaking into the contained cold aisle at the front, and cool air from escaping it.
- **Rack console:** a fold-out screen and keyboard in a 1U drawer. It plugs into one server at a time
  for first setup. After each server's BMC has an IP address, the servers are managed over the network.
- **Transfer media:** the approved encrypted drives that carry software into the lab.

## 3. Budget fit

| Line | Amount |
|---|---|
| BOM hardware, 50-user tier, lab only | $191,540.00 |
| Switch and 25G cables at CDW prices, minus the BOM's Dell switch ($3,515) and cables ($1,000): $32,293.83 - $4,515 (section 4, item 3) | $27,778.83 |
| Additions (A1-A6) | $19,197.76 |
| **Committed subtotal** | **$238,516.59** |
| Left inside $250k, for the NX-OS license and contingency | $11,483.41 (4.6%) |
| **Total** | **$250,000.00** |

Same total another way: servers and GPUs (08a) $187,025 plus network, rack, and setup (08b) $51,491.59.

If RHEL (C1) is needed, the subtotal is $244,116.59 and $5,883.41 (2.4%) is left.

**The margin is thin.** The switch (about $31,000 at CDW) is most of the change. Ask for NX-OS Essentials,
not Advantage ($19,405 at CDW), or the license alone breaks the budget.

A small single-GPU test machine ([04](../software/04-prototype-plan.md)) no longer fits unless the margin below comes through.

Three things can add margin:

1. **GPU price.** The BOM uses $18,246 per GPU (Thinkmate quote). CDW listed the same card at
   $13,824.99 in late October 2026 (CDW 8426124). Across 4 GPUs that saves about $17,684.
2. **Government pricing.** The BOM already notes GSA and SEWP may come in lower than commercial. Cisco
   partners also often quote the switch below CDW's advertised price.
3. **Transfer drives (A4).** If the lab supplies approved drives, drop A4 and save $5,550.

## 4. Items to fix in the BOM workbook

These are corrections, not new scope:

1. **Server link.** The reference system, "GPX GE95-2206-41", is at
   https://www.thinkmate.com/system/gpx-ge95-2206-41. The base system has dual 10GbE RJ45 and 4 x 2000 W PSUs.
2. **GPU server network card.** The service node line says "2 x 25 GbE", but the GPU server line does not
   name a NIC. The base system has only 10GbE RJ45 onboard. Add the Intel E810-XXVDA2 (2 x SFP28, offered
   in the Thinkmate configurator). The chassis has 7 PCIe x16 slots, so there is room next to 4 GPUs.
3. **Switch.** Replace the Dell S5248F-ON ($3,515 in the BOM) with a **Cisco Nexus N93180YC-FX3**
   (48 x 1/10/25G SFP28, 6 x 40/100G QSFP28), ordered **port-side exhaust** (NXA-PAC-650W-PE power supplies,
   NXA-FAN-35CFM-PE fans). Reason: every optic between it and the lab's Cisco C9500X-28C8D is then listed in
   Cisco's compatibility matrix, and the lab already runs this model. Price by quote, including the NX-OS
   NX-OS Essentials license (shortest term). At CDW prices the switch with power supplies and fans is
   $30,993.93 plus the license, so the totals rise by about $27,479 plus the license. Its ports face the hot
   aisle (see [05-rack-build-guide.md](05-rack-build-guide.md)); the wrong airflow pulls hot air in.
4. **Power cord type** for the GPU server PSUs (C19/C20 vs C13/C14). Ask Thinkmate when you request the
   quote. The configurator's cord options are NEMA 5-15P wall plugs, which do not fit a 208V rack PDU.
5. **Cell B21 on the BOM tab** ("Additional Research area under Cables and Optics: Infiniband"). It is
   answered in [03-network-and-switch-capacity.md](03-network-and-switch-capacity.md), section 4.
   InfiniBand is not needed for this design.
6. **Service node network card.** The RAX RE95-1104-01 base has a single 1GbE RJ45 port. Add the Broadcom
   N225P OCP 3.0 (2 x SFP28) in the configurator to match the BOM's "2 x 25 GbE".
7. **Operating system cost.** The `Software` tab assumes no license cost. That holds for Rocky Linux 9 or
   Ubuntu. If the lab requires RHEL, add subscriptions (section 2, C1).
8. **Staging rows S1-S3 on the BOM tab.** Set their quantities to 0. The lab decided not to have staging.
   The tier totals in cells I17-K17 then drop by $66,038 each, and the 50-user lab total reads $191,540.

## 5. Growth path (nothing thrown away)

| Step | Add | Est. cost | Reuses |
|---|---|---|---|
| 50 users | Bought now: all 4 GPU slots in gpu01 filled | in the budget | |
| 100 users | gpu02, 4 GPUs, 2 NVMe, second 25G switch, cables | about $125,300 | Rack 2 (held next to rack 1) and its PDUs, same software. gpu02 can go in rack 1 at U3-U4 instead if the PSUs use C14 inlets, since each PDU has only three C19 outlets. |
| Rest of the pipeline | CPU workloads on the lab's existing CPU servers (BOM scope note) | n/a | Same Kubernetes platform, Harbor, GitLab, Argo CD |
