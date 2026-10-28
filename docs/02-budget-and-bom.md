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

| ID | Item | Qty | Est. unit | Est. total | Why |
|---|---|---|---|---|---|
| A1 | Rack PDU, Vertiv Geist, 208V 3-phase WYE 30A, L21-30P plug, combination C13/C19 outlets, 0U | 2 | $1,800 | $3,600 | Lab rack, feeds A and B. The racks are empty. |
| A2 | Same PDU for staging | 2 | $1,800 | $3,600 | Same model as A1, so one spare covers both |
| A3 | Uplink optics: 4 x 100G QSFP28 (2 Dell-coded, 2 Cisco-coded), plus patch cords | 1 lot | $3,000 | $3,000 | Lab switch to C9500X core. The BOM line "Cables and optics" ($1,000) covers only the in-rack 25G DACs. |
| A4 | 1G managed switch for out-of-band (BMC) | 1 | $600 | $600 | Keeps server management off the data network |
| A5 | Blanking panels, cable management, labels | 1 lot | $400 | $400 | Required for aisle containment |
| A6 | Transfer media (encrypted SSDs, 4 TB) | 2 | $400 | $800 | Release bundles; the model alone is about 65 GB. Use the lab's approved media type. |
| A7 | USB crash-cart adapter (KVM to laptop) | 1 | $500 | $500 | First boot and BIOS setup before networking is up |
| | **Additions total** | | | **$12,500** | |

All A-items are estimates. Get quotes before you finalize.

## 3. Budget fit

| Line | Amount |
|---|---|
| BOM hardware, 20-user tier | $221,086.00 |
| Additions (A1-A7) | $12,500.00 |
| **Committed subtotal** | **$233,586.00** |
| Contingency left inside $250k | $16,414.00 (7.0%) |
| **Total** | **$250,000.00** |

The BOM assumed 10% contingency. 7.0% is still reasonable, and two levers bring it back to 10%:

1. **GPU price.** The BOM uses $18,246 per GPU (Thinkmate quote). The same tab notes CDW at $16,115.
   Across 3 GPUs (2 lab, 1 staging), that saves $6,393, and contingency rises to $22,807 (9.1%).
2. **Government pricing.** The BOM already notes GSA and SEWP may come in lower than commercial.

## 4. Items to fix in the BOM workbook

These are corrections, not new scope:

1. **Server family name.** `Assumptions!A21` / `E21` call the reference system "GPX GE95-2206-41". Thinkmate lists
   the GE95-2206-41 under its **RAX** line (2U, EPYC 9004/9005, 7 x PCIe 5.0 x16). Correct the name so
   the quote can be reproduced.
2. **GPU server network card.** The service node line says "2 x 25 GbE", but the GPU server line does not
   name a NIC. Make sure the quote includes a dual-port 25GbE NIC (OCP 3.0 slot preferred), so it does not
   use one of the four GPU slots.
3. **Switch airflow.** Order the S5248F-ON with **PSU-to-port airflow ("port-side exhaust")**. The switch
   ports face the hot aisle (see [05-rack-build-guide.md](05-rack-build-guide.md)). The wrong airflow pulls
   hot air in.
4. **Power cord type** for the GPU server PSUs (C19/C20 vs C13/C14). Ask Thinkmate when you request the quote.
5. **Cell B21 on the BOM tab** ("Additional Research area under Cables and Optics: Infiniband"). It is
   answered in [03-network-and-switch-capacity.md](03-network-and-switch-capacity.md), section 4.
   InfiniBand is not needed for this design.

## 5. Growth path (nothing thrown away)

| Step | Add | Est. cost | Reuses |
|---|---|---|---|
| 50 users | 2 x RTX PRO 6000 into gpu01's empty slots | about $36,500 | Same server, rack, PDUs, switch ports |
| 100 users (after 50) | gpu02 (U3-U4, already reserved), 4 GPUs, 2 NVMe, second 25G switch, cables | about $125,300 | Same rack, same circuits (sized for 8.3 kW), same software |
| Rest of the pipeline | CPU workloads on the lab's existing CPU servers (BOM scope note) | n/a | Same Kubernetes platform, Harbor, GitLab, Argo CD |
