# 08. Quote request (email text)

Copy everything below the line into the email.

Links were checked on 2026-10-29. Thinkmate links open the configurator at its default settings.
Thinkmate does not support links with options already selected, so the options to pick are listed in
each item. "Save This Config" or "Email" on the Thinkmate page creates a saved configuration that
can be sent with the quote request. All other links go straight to the exact part.

---

**Subject:** Quote request: GPU servers and rack items, metrics analysis pipeline (50-user build)

Please get quotes for the items below. Estimated total is $201,874, under the $250,000 limit.
Government pricing (GSA, SEWP) is welcome.

**Lab**

| # | Item | Part / model | Qty | Est. each | Est. total | Link |
|---|---|---|---|---|---|---|
| 1 | GPU server, 2U, 4 GPU slots. Select: 2 x AMD EPYC 9115 (16-core, 2.60 GHz); 12 x 32GB DDR5-6400 ECC RDIMM (384 GB); 2 x 3.84TB Micron 7600 PRO U.2 NVMe; Intel E810-XXVDA2 (2 x 25G SFP28); TPM 2.0; 5 Year Advanced Parts Replacement Warranty; OS per question 6 below. | Thinkmate GPX GE95-2206-41 | 1 | $47,792 | $47,792 | https://www.thinkmate.com/system/gpx-ge95-2206-41 |
| 2 | GPU, installed in item 1 (select in item 1 as "NVIDIA RTX PRO 6000 Blackwell Server Edition - 96GB", qty 4, all four GPU slots) | NVIDIA RTX PRO 6000 Blackwell Server Edition 96 GB, mfr NVRTXPRO6000TCGPU-KIT | 4 | $18,246 | $72,984 | https://www.cdw.com/product/nvidia-rtx-pro-6000-blackwell-server-edition-graphics-card-rtx-pro-60/8426124 |
| 3 | Service node, 1U. Redundant 1300 W PSUs are part of the base system (the "Barebone" line), nothing to select. Select: AMD EPYC 9115 (16-core); 128 GB DDR5 ECC RDIMM; 2 x 1.92TB U.2 NVMe; Broadcom N225P OCP 3.0 (2 x 25G SFP28); 5 Year Advanced Parts Replacement Warranty | Thinkmate RAX RE95-1104-01 | 3 | $22,083 | $66,249 | https://www.thinkmate.com/system/rax-re95-1104-01 |
| 4 | 25G switch, 48 x SFP28, 4 x QSFP28, OS10. On the Dell page choose S5248F-ON, then **airflow: PSU to I/O (port-side exhaust)**. New, not refurbished. | Dell PowerSwitch S5248F-ON, 210-APFB | 1 | $3,515 | $3,515 | https://www.dell.com/en-us/shop/povw/networking-s-series-25-100gbe |
| 5 | 25G SFP28 direct attach cable, 3 m. Inside the rack: server 25G ports to our switch (item 4). 8 used, 2 spare. | Dell 470-ACEU | 10 | $100 | $1,000 | https://www.networktigers.com/a/s/products/dell-470-aceu-54m38-3m-25gb-sfp28-passive-direct-attach-cable |

**Network, rack, and setup items**

| # | Item | Part / model | Qty | Est. each | Est. total | Link |
|---|---|---|---|---|---|---|
| 6a | 10G optic, lab end of the uplink: goes in the lab C9300-48S (C9300-NM-8X port) | Cisco SFP-10G-SR-S | 2 | $500 | $1,000 | https://www.cdwg.com/product/cisco-sfp-transceiver-module-10gbe/3731455 |
| 6b | 10G optic, our end of the uplink: goes in our switch (item 4). Fiber (6c) joins it to 6a. | Dell 407-BBOU | 2 | $150 | $300 | https://www.networktigers.com/a/s/products/407-bbou-dell-transceiver-new |
| 6c | Fiber cord, LC-LC duplex, OM4, one per uplink, run directly from our switch to the lab switch. Length to the measured cable path (estimate 30 m; plenum or riser rated if the lab requires). See question 7. | any | 2 | $80 | $160 | |
| 6d | Fiber patch cord, LC-LC duplex, OM4, 3 m (spares, and for the lab's patch panel if they install one) | any | 2 | $25 | $50 | |
| 6e | 8 x 10G uplink module for the C9300-48S. **Only if the lab's switch has no free 10G ports.** | Cisco C9300-NM-8X | 1 | $1,600 | $1,600 | https://www.disctech.com/Cisco-9300-NM-8X-8-Port-10GE-Network-Module |
| 7 | Management switch, 24 x 1G, 4 x 10G SFP+ | Cisco Catalyst C1300-24T-4X | 1 | $1,100 | $1,100 | https://www.cdw.com/product/cisco-catalyst-1300-24t-4x-switch-24-ports-managed-rack-mountable/8112270 |
| 8 | Blanking panels, tool-less 1U, 10-pack (both racks) | Vertiv VRA2000 | 8 | $85 | $680 | https://www.cdw.com/product/vertiv-rack-toolless-airflow-blanking-panel-1u/5323823 |
| 9 | Cat6 patch cable, 10 ft (3 m), 10-pack. 3 ft is too short: BMC ports at U1-U7 run to the management switch at U40. | any | 2 | $72 | $144 | |
| 10 | Encrypted SSD, 4 TB, FIPS 140-2 (or the lab's approved type) | Apricorn Aegis Padlock Fortress A25-3PL256-S4000F | 2 | $1,800 | $3,600 | https://www.cdw.com/product/apricorn-4tb-fips-validated-aegis/4456344 |
| 11 | Rack console, 1U, 17" LCD, keyboard, VGA/USB | StarTech RKCONS1701 | 1 | $1,200 | $1,200 | https://www.startech.com/en-us/server-management/rkcons1701 |
| 12 | Setup kit (list below) | see list | 1 lot | $500 | $500 | |

**Totals**

| | |
|---|---|
| Servers, GPUs, switch, cables (1-5) | $191,540 |
| Network, rack, setup (6-12) | $10,334 |
| **Total** | **$201,874** |
| Left under $250,000 | $48,126 |

**Only if needed (not in the total)**

| # | Item | When | Qty | Est. total | Link |
|---|---|---|---|---|---|
| 13 | Red Hat Enterprise Linux Server, Standard, 1 year, 2 sockets, 1 physical node (RH00004) | If the OS must be RHEL (question 6). One per server: gpu01 and svc01-svc03. Can also be selected in the Thinkmate configurator ("Red Hat Enterprise Linux 9 Server (Standard) (1 Year)"). Rocky Linux 9 is free and needs none. | 4 | $5,600 per year | https://cdw.com/product/red-hat-enterprise-linux-server-standard-subscription-2-sockets-1-phys/6905904 |

With it, the total is $207,474.

**Setup checklist (item 12)**

- Label maker, Brother PT-E550W, plus 2 x Brother TZe-FX231 flexible ID tape (for cables)
- VELCRO brand ONE-WRAP ties, 3/4" x 8", 100-pack
- M6 cage nuts and screws, 50-pack, plus cage nut tool (the racks have square holes)
- ESD wrist strap
- Fiber cleaner, one-click, LC 1.25 mm
- Console cables: USB to RJ45 serial, and USB-A to micro-USB (Dell switch console port)
- #2 Phillips screwdriver, flashlight, 25 ft tape measure

**Questions**

1. **GPU server power cords.** The server has 4 x 2000 W PSUs. Is the PSU inlet C14 or C20? The site's
   rack PDUs have mostly C13 outlets and three C19 outlets per PDU.
   - If C14: we need 4 x C13-to-C14 cords per server, 6 ft. (Preferred, if offered.)
   - If C20: we need 4 x C19-to-C20 cords per server, 6 ft.
   - Do not ship NEMA 5-15P (wall plug) cords. The configurator only offers those.
2. **Service node power cords.** 2 x C13-to-C14 cords per node, 6 ft, no NEMA 5-15P.
3. **Factory install.** Please install all 4 GPUs (item 2) and the 25G NICs at the factory, and burn in the GPU server with all 4 GPUs loaded.
4. **Rails.** The racks are Vertiv VR3300 with square holes, vertical rails adjustable, currently 29 in
   apart. Do the rail kits for items 1, 3, and 4 fit?
5. **Lead time** for each item, especially the GPUs.
6. **Operating system.** Does the lab require a specific server OS (for example RHEL 9 with STIG)? If it
   must be RHEL, each server needs a Red Hat subscription (item 13, about $1,400 per server per year),
   which is not in the original BOM. If the lab allows it, Rocky Linux 9 is compatible and free.
7. **Fiber to the lab switch.** There are no fiber patch panels in the racks, and the lab's C9300-48S is
   not in our row. Where is that switch, and how long is the cable path to our racks (overhead tray or
   under the raised floor)? Will the lab run the fiber, or should we order long cords (item 6c)? Does the
   lab require plenum or riser rated cable?
