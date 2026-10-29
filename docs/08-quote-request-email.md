# 08. Quote request (email text)

Copy everything below the line into the email.

---

**Subject:** Quote request: GPU servers and rack items, metrics analysis pipeline (20-user build)

Please get quotes for the items below. Estimated total is $238,386, under the $250,000 limit.
Government pricing (GSA, SEWP) is welcome.

**Lab**

| # | Item | Part / model | Qty | Est. each | Est. total | Link |
|---|---|---|---|---|---|---|
| 1 | GPU server, 2U, 4 GPU slots. Configure: 2 x AMD EPYC 9115, 384 GB DDR5, 2 x 3.84 TB U.2 NVMe, Intel E810-XXVDA2 (2 x 25G SFP28), 4 x 2000 W PSU, rail kit, 5-yr parts warranty | Thinkmate GPX GE95-2206-41 | 1 | $47,792 | $47,792 | https://www.thinkmate.com/system/gpx-ge95-2206-41 |
| 2 | GPU, installed in item 1 | NVIDIA RTX PRO 6000 Blackwell Server Edition 96 GB, mfr NVRTXPRO6000TCGPU-KIT | 2 | $18,246 | $36,492 | https://www.cdw.com/product/nvidia-rtx-pro-6000-blackwell-server-edition-graphics-card-rtx-pro-60/8426124 |
| 3 | Service node, 1U. Configure: 16+ cores, 128 GB RAM, 2 x 1.92 TB NVMe, 2 x 25G SFP28, 2 PSUs, rail kit | Thinkmate RAX RE95-1104-01 | 3 | $22,083 | $66,249 | https://www.thinkmate.com/system/rax-re95-1104-01 |
| 4 | 25G switch, 48 x SFP28, 4 x QSFP28, OS10. **Airflow: PSU-to-I/O (port-side exhaust)** | Dell S5248F-ON, 210-APFB | 1 | $3,515 | $3,515 | https://directmacro.com/dell-210-apfb.html |
| 5 | 25G SFP28 direct attach cable, 3 m | Dell 470-ACEU | 10 | $100 | $1,000 | https://www.networktigers.com/a/s/products/dell-470-aceu-54m38-3m-25gb-sfp28-passive-direct-attach-cable |

**Staging**

| # | Item | Part / model | Qty | Est. each | Est. total | Link |
|---|---|---|---|---|---|---|
| 6 | GPU server, same configuration as item 1 | Thinkmate GPX GE95-2206-41 | 1 | $47,792 | $47,792 | https://www.thinkmate.com/system/gpx-ge95-2206-41 |
| 7 | GPU, installed in item 6 | NVIDIA RTX PRO 6000 Blackwell Server Edition 96 GB | 1 | $18,246 | $18,246 | (as item 2) |

**Rack, power, and network items**

| # | Item | Part / model | Qty | Est. each | Est. total | Link |
|---|---|---|---|---|---|---|
| 8 | Rack PDU, 208V 3-phase, NEMA L21-30P plug, 12 combination C13/C19 outlets, metered (2 lab, 2 staging) | Vertiv Geist MNR3E1R6-12CF18-3TL21A0H10-S | 4 | $1,800 | $7,200 | https://icgsupply.com/products/geist-rpdu-mnr3e1r6-12cf18-3tl21a0h10-s-12-outlets-pdu |
| 9 | Uplink lot, 10G (default): 2 x Cisco SFP-10G-SR-S, 2 x Dell 407-BBOU 10G SR SFP+ (Dell or compatible), 4 x LC-LC OM4 duplex patch cord 3 m. Include 1 x Cisco C9300-NM-8X only if the lab switch has no free 10G ports. | see item text | 1 lot | $3,000 | $3,000 | https://edgeoptic.com/products/dell-force10/407-bbou |
| 9-alt | Uplink lot, 100G (only if the lab allows the core connection): 2 x Cisco QSFP-100G-SR4-S, 2 x Dell 407-BBWV 100G SR4 QSFP28, 4 x MPO-12 OM4 patch cord 3 m | see item text | 1 lot | ($3,000) | (replaces 9) | https://www.dell.com/en-us/shop/dell-networking-transceiver-100gbe-qsfp28-sr4-no-fec-capable-mpo-mmf/apd/407-bbwv/networking |
| 10 | Management switch, 24 x 1G, 4 x 10G SFP+ | Cisco Catalyst C1300-24T-4X | 1 | $1,100 | $1,100 | https://www.cdw.com/product/cisco-catalyst-1300-24t-4x-switch-24-ports-managed-rack-mountable/8112270 |
| 11 | Blanking panels, tool-less 1U, 10-pack | Vertiv VRA2000 | 4 | $139 | $556 | https://www.shi.com/product/37069994/Vertiv-Rack-toolless-airflow-blanking-panel |
| 12 | Cat6 patch cable, 3 ft, 10-pack | any | 2 | $72 | $144 | |
| 13 | Encrypted SSD, 4 TB, FIPS 140-2 (or the lab's approved type) | Apricorn Aegis Padlock Fortress A25-3PL256-S4000F | 2 | $1,800 | $3,600 | https://www.cdw.com/product/apricorn-4tb-fips-validated-aegis/4456344 |
| 14 | Rack console, 1U, 17" LCD, keyboard, VGA/USB (skip if the lab has a crash cart) | StarTech RKCONS1701 | 1 | $1,200 | $1,200 | https://www.startech.com/en-us/server-management/rkcons1701 |
| 15 | Setup kit (list below) | see list | 1 lot | $500 | $500 | |

**Totals**

| | |
|---|---|
| Lab (1-5) | $155,048 |
| Staging (6-7) | $66,038 |
| Rack, power, network (8-15) | $17,300 |
| **Total** | **$238,386** |
| Left under $250,000 | $11,614 |

**Setup checklist (item 15)**

- Label maker, Brother PT-E550W, plus 2 x Brother TZe-FX231 flexible ID tape (for cables)
- VELCRO brand ONE-WRAP ties, 3/4" x 8", 100-pack
- M6 cage nuts and screws, 50-pack, plus cage nut tool (only if the rack has square holes)
- ESD wrist strap
- Fiber cleaner, one-click, LC 1.25 mm (and MPO, if 9-alt)
- Console cables: USB to RJ45 serial, and USB-A to micro-USB (Dell switch console port)
- #2 Phillips screwdriver, flashlight, 25 ft tape measure

**Questions for the vendor**

1. The GPU server has 4 x 2000 W PSUs. Is the PSU inlet C14 or C20? If C20, we need C19-to-C20 cords. If C14, we need C13-to-C14 cords. Either way, 4 cords per server, 6 ft, for a 208V rack PDU. Do not ship NEMA 5-15P (wall plug) cords.
2. Same question for the service nodes (item 3): C14 inlet assumed, so C13-to-C14 cords, 2 per node.
3. Please install the GPUs (items 2, 7) and the 25G NIC at the factory.
4. Do the rail kits fit a rack with [square / round] holes and [___] in between the front and rear rails? (Filled in after the site visit.)
5. Lead time for each item, especially the GPUs.
