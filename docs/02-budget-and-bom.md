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
The lab supplies racks and cooling. The items below are still on us. Without them the rack can't be
powered or connected.

Part numbers and links are in the quote request, [08-quote-request-email.md](08-quote-request-email.md).

| ID | Item | Qty | Est. total | Why |
|---|---|---|---|---|
| A1 | Rack PDU, Vertiv Geist, 208V 3-phase, L21-30P, 12 combination C13/C19 outlets, metered | 2 | $3,600 | Lab rack, feeds A and B. The CRV (CR035RA) is a cooler and has no outlets. **Drop if the site visit finds rack PDUs already in the racks.** |
| A2 | Same PDU for staging | 2 | $3,600 | Depends on where staging lives. Drop if it goes in a rack that already has PDUs. |
| A3 | Uplink lot: optics at both ends plus fiber patch cords | 1 lot | $3,000 | Our switch to the lab network. The BOM line "Cables and optics" ($1,000) covers only the in-rack 25G cables. |
| A4 | 1G management switch, Cisco C1300-24T-4X | 1 | $1,100 | Keeps server management (BMC) off the data network |
| A5 | Blanking panels (40), Cat6 patch cables | 1 lot | $700 | Containment does not work with open U spaces |
| A6 | Encrypted SSD, 4 TB, FIPS 140-2 | 2 | $3,600 | Software and model transfer. Use the lab's approved type; drop if the lab provides it. |
| A7 | Rack console, 1U LCD and keyboard | 1 | $1,200 | First boot and BIOS setup. Drop if the lab has a crash cart. |
| A8 | Setup kit (labels, velcro, cage nuts, ESD strap, fiber cleaner, console cables, hand tools) | 1 lot | $500 | Needed on install day |
| | **Additions total** | | **$17,300** | |

All A-items are estimates. Get quotes before you finalize.

**Terms used above:**

- **Rack PDU:** a power strip built for a rack. It plugs into the facility receptacle and gives each
  server cord an outlet.
- **Uplink optics:** the transceiver modules that plug into a switch port and turn the signal into
  light for a fiber cable. One goes in each end of the link. Each end must be coded for its own switch
  brand, so the Dell switch end uses a Dell-coded optic and the Cisco end uses a Cisco-coded optic.
  Switches often refuse other brands.
- **Patch cords:** short fiber cables from the optic to the fiber panel, or optic to optic.
- **Management switch:** a small separate switch for each server's BMC port, the built-in remote
  console used for power and BIOS control.
- **Blanking panels:** flat plates that cover empty rack spaces. They stop hot exhaust air from
  circling back to the front.
- **Transfer media:** the approved encrypted drives that carry software into the lab.

## 3. Budget fit

| Line | Amount |
|---|---|
| BOM hardware, 20-user tier | $221,086.00 |
| Additions (A1-A8) | $17,300.00 |
| **Committed subtotal** | **$238,386.00** |
| Contingency left inside $250k | $11,614.00 (4.6%) |
| **Total** | **$250,000.00** |

Three things can bring contingency back toward 10%:

1. **GPU price.** The BOM uses $18,246 per GPU (Thinkmate quote). CDW listed the same card at
   $13,824.99 in late October 2026 (CDW 8426124). Across 3 GPUs that saves about $13,263, and contingency
   rises to about $24,877 (10.0%).
2. **Items the site already has.** Rack PDUs (A1, A2), approved media (A6), and a crash cart (A7) together
   are $12,000.
3. **Government pricing.** The BOM already notes GSA and SEWP may come in lower than commercial.

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

## 5. Growth path (nothing thrown away)

| Step | Add | Est. cost | Reuses |
|---|---|---|---|
| 50 users | 2 x RTX PRO 6000 into gpu01's empty slots | about $36,500 | Same server, rack, PDUs, switch ports |
| 100 users (after 50) | gpu02 (U3-U4, already reserved), 4 GPUs, 2 NVMe, second 25G switch, cables | about $125,300 | Same rack, same circuits (sized for 8.3 kW), same software |
| Rest of the pipeline | CPU workloads on the lab's existing CPU servers (BOM scope note) | n/a | Same Kubernetes platform, Harbor, GitLab, Argo CD |
