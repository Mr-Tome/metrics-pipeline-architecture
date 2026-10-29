# 02. Budget and BOM

Target: **$250,000.00**. Source of the base numbers: `Metrics_Analysis_Pipeline_Hardware_BOM.xlsx`.

## 1. Which tier fits

| Tier | Hardware subtotal | With 10% contingency | Fits $250k? |
|---|---|---|---|
| 20 users | $221,086 | $243,194.60 | Yes |
| 50 users | $257,578 | $283,335.80 | No |
| 100 users | $382,869 | $421,155.90 | No |

**Recommendation: buy the 20-user tier.** It already includes the full staging environment, all three
service nodes, and a 4-slot GPU server with 2 slots empty. Growing to 50 users later means adding two
GPUs to the server we already own. Nothing gets replaced.

## 2. What the BOM leaves out

The BOM's `Assumptions` tab, section 5, excludes racks, power distribution, cooling, and facility work.
The site visit confirmed the lab supplies racks (Vertiv VR3300), rack PDUs (Vertiv Geist, two per rack),
and cooling (Liebert CRV). The items below are still on us. Without them the rack can't be connected
or set up.

Part numbers and links are in the quote request, [08-quote-request-email.md](08-quote-request-email.md).

| ID | Item | Qty | Est. total | Why |
|---|---|---|---|---|
| A1 | Uplink lot: 10G optics at both ends, two long fiber cords to the lab switch (the racks have no patch panels), spare short cords, and a C9300-NM-8X module if the lab switch has no free 10G ports | 1 lot | $3,110 | Our switch to the lab network. The BOM line "Cables and optics" ($1,000) covers only the in-rack 25G cables. |
| A2 | 1G management switch, Cisco C1300-24T-4X | 1 | $1,100 | Keeps server management (BMC) off the data network |
| A3 | Blanking panels (80, both racks), Cat6 patch cables | 1 lot | $824 | The racks have none, and hot aisle containment does not work with open U spaces |
| A4 | Encrypted SSD, 4 TB, FIPS 140-2 | 2 | $3,600 | Software and model transfer. Use the lab's approved type; drop if the lab provides it. |
| A5 | Rack console, 1U LCD and keyboard | 1 | $1,200 | First boot and BIOS setup. The lab has no crash cart. |
| A6 | Setup kit (labels, velcro, cage nuts, ESD strap, fiber cleaner, console cables, hand tools) | 1 lot | $500 | Needed on install day |
| | **Additions total** | | **$10,334** | |

Only if needed, not in the total:

| ID | Item | Est. total | When |
|---|---|---|---|
| C1 | Red Hat Enterprise Linux Server subscriptions, 5 servers, 1 year | $7,000 per year | Only if the lab requires RHEL. Rocky Linux 9 is free. Not in the original BOM. |
| C2 | Rack PDUs for staging (2) | $3,600 | Only if staging goes somewhere without rack PDUs |

All items are estimates. Get quotes before you finalize.

**Terms used above:**

- **Rack PDU:** a power strip built for a rack. The ones already in the racks are the Vertiv Geist
  strips on the left and right. Each server cord plugs into one of their outlets.
- **Uplink optics:** the transceiver modules that plug into a switch port and turn the signal into
  light for a fiber cable. One goes in each end of the link. Each end must be coded for its own switch
  brand, so the Dell switch end uses a Dell-coded optic and the Cisco end uses a Cisco-coded optic.
  Switches often refuse other brands.
- **Patch cords:** short fiber cables from the optic to the fiber panel, or optic to optic.
- **Management switch:** a small separate switch for each server's BMC port, the built-in remote
  console used for power and BIOS control.
- **Blanking panels:** flat plates that cover empty rack spaces. They stop hot exhaust air from
  circling back to the front.
- **Rack console:** a fold-out screen and keyboard in a 1U drawer. It plugs into one server at a time
  for first setup. After each server's BMC has an IP address, the servers are managed over the network.
- **Transfer media:** the approved encrypted drives that carry software into the lab.

## 3. Budget fit

| Line | Amount |
|---|---|
| BOM hardware, 20-user tier | $221,086.00 |
| Additions (A1-A6) | $10,334.00 |
| **Committed subtotal** | **$231,420.00** |
| Contingency left inside $250k | $18,580.00 (7.4%) |
| **Total** | **$250,000.00** |

If both conditional items (C1, C2) are needed, the subtotal is $242,020 and $7,980 (3.2%) is left.

Two things can add margin:

1. **GPU price.** The BOM uses $18,246 per GPU (Thinkmate quote). CDW listed the same card at
   $13,824.99 in late October 2026 (CDW 8426124). Across 3 GPUs that saves about $13,263.
2. **Government pricing.** The BOM already notes GSA and SEWP may come in lower than commercial.

## 4. Items to fix in the BOM workbook

These are corrections, not new scope:

1. **Server link.** The reference system, "GPX GE95-2206-41", is at
   https://www.thinkmate.com/system/gpx-ge95-2206-41. The base system has dual 10GbE RJ45 and 4 x 2000 W PSUs.
2. **GPU server network card.** The service node line says "2 x 25 GbE", but the GPU server line does not
   name a NIC. The base system has only 10GbE RJ45 onboard. Add the Intel E810-XXVDA2 (2 x SFP28, offered
   in the Thinkmate configurator). The chassis has 7 PCIe x16 slots, so there is room next to 4 GPUs.
3. **Switch airflow.** Order the S5248F-ON with **PSU-to-port airflow ("port-side exhaust")**. The switch
   ports face the hot aisle (see [05-rack-build-guide.md](05-rack-build-guide.md)). The wrong airflow pulls
   hot air in.
4. **Power cord type** for the GPU server PSUs (C19/C20 vs C13/C14). Ask Thinkmate when you request the
   quote. The configurator's cord options are NEMA 5-15P wall plugs, which do not fit a 208V rack PDU.
5. **Cell B21 on the BOM tab** ("Additional Research area under Cables and Optics: Infiniband"). It is
   answered in [03-network-and-switch-capacity.md](03-network-and-switch-capacity.md), section 4.
   InfiniBand is not needed for this design.
6. **Service node network card.** The RAX RE95-1104-01 base has a single 1GbE RJ45 port. Add the Broadcom
   N225P OCP 3.0 (2 x SFP28) in the configurator to match the BOM's "2 x 25 GbE".
7. **Operating system cost.** The `Software` tab assumes no license cost. That holds for Rocky Linux 9 or
   Ubuntu. If the lab requires RHEL, add subscriptions (section 2, C1).

## 5. Growth path (nothing thrown away)

| Step | Add | Est. cost | Reuses |
|---|---|---|---|
| 50 users | 2 x RTX PRO 6000 into gpu01's empty slots | about $36,500 | Same server, rack, PDUs, switch ports |
| 100 users (after 50) | gpu02, 4 GPUs, 2 NVMe, second 25G switch, cables | about $125,300 | Rack 2 (held next to rack 1) and its PDUs, same software. gpu02 can go in rack 1 at U3-U4 instead if the PSUs use C14 inlets, since each PDU has only three C19 outlets. |
| Rest of the pipeline | CPU workloads on the lab's existing CPU servers (BOM scope note) | n/a | Same Kubernetes platform, Harbor, GitLab, Argo CD |
