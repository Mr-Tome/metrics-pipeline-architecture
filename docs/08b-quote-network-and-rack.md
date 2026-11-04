# 08b. Quote request: network, rack, and setup items (not yet sent)

**Status: not sent.** Being revised for the new C9500X-28C8D above rows 2 and 3 (2026-11-04: 100G from
it to our switch is allowed, its uplink to the core is 10G, and we supply our own optics). The servers
and GPUs were submitted separately ([08a](08a-quote-servers-submitted.md)).

Item numbers are kept from the original single request so references in other docs still match.

## Answer these first (lab network team), before sending

Settled 2026-11-04: our switch connects to the new C9500X-28C8D above rows 2 and 3 at 100G, that
switch's own uplink to the core is 10G, and we supply the optics for both ends. The items below decide
which optics and cords to order (6a-6e) and whether the management switch needs an optic pair (7).
Tracked in [07](07-open-questions.md). The email asking them is [10](10-lab-network-team-email.md).

| # | Question | Why it blocks the order | 07 ID |
|---|---|---|---|
| P1 | **Patch panels:** where do they go (in each rack, top of rack, or overhead), and do they reach our racks? Fiber type (OM4 multimode or single-mode)? Connector (MPO-12 or LC)? For MPO, which polarity (Type A, B, or C)? | Picks the optic type (100G-SR4 for MPO multimode, 100G SR1.2 BiDi for LC multimode, CWDM4 or LR4 for single-mode) and the patch cords. **Not asked yet.** | N3 |
| P2 | **Optic brand:** must the optics in the C9500X-28C8D be Cisco-branded, or are Cisco-compatible third-party optics allowed? Which IOS-XE version does it run? | Cisco-branded 100G optics cost several times more. The version is needed to check the Cisco compatibility matrix. | N10 |
| P3 | **Which racks:** which two adjacent racks in row 2 or 3 are ours? | The panel has to reach them. Moving rows changes nothing else (F7). | F6 |
| P4 | **Management network:** where does our management switch (item 7) uplink go? To the C9500X-28C8D, or to a separate lab management switch? Fiber or copper? | If it is the C9500X-28C8D, we add one more optic pair. | N7 |

When P1-P4 are answered: replace 6a with 2 Cisco 100G optics, 6b with 2 Dell-compatible 100G QSFP28
optics of the same type, drop 6c and 6e, and match 6d to the panel connector.


---

**Subject:** Quote request: network, rack, and setup items, metrics analysis pipeline (50-user build)

Please get quotes for the items below. These go with the GPU server and service node order already
submitted. Government pricing (GSA, SEWP) is welcome.

**Network**

Items 6a-6e still show the old 10G design to the lab's C9300-48S. They will change to 100G optics for
the new C9500X-28C8D once the questions at the top are answered. Please hold 6a-6e until we confirm.

| # | Item | Part / model | Qty | Est. each | Est. total | Link |
|---|---|---|---|---|---|---|
| 4 | 25G switch, 48 x SFP28, 4 x QSFP28, OS10. On the Dell page choose S5248F-ON, then **airflow: PSU to I/O (port-side exhaust)**. New, not refurbished. | Dell PowerSwitch S5248F-ON, 210-APFB | 1 | $3,515 | $3,515 | https://www.dell.com/en-us/shop/povw/networking-s-series-25-100gbe |
| 5 | 25G SFP28 direct attach cable, 3 m. Inside the rack: server 25G ports to our switch (item 4). 8 used, 2 spare. | Dell 470-ACEU | 10 | $100 | $1,000 | https://www.networktigers.com/a/s/products/dell-470-aceu-54m38-3m-25gb-sfp28-passive-direct-attach-cable |
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

**Total: $14,849** (items 4-12). With the servers and GPUs (08a, $187,025), the build comes to $201,874,
leaving $48,126 under $250,000.

**Setup checklist (item 12)**

- Label maker, Brother PT-E550W, plus 2 x Brother TZe-FX231 flexible ID tape (for cables)
- VELCRO brand ONE-WRAP ties, 3/4" x 8", 100-pack
- M6 cage nuts and screws, 50-pack, plus cage nut tool (the racks have square holes)
- ESD wrist strap
- Fiber cleaner, one-click, LC 1.25 mm
- Console cables: USB to RJ45 serial, and USB-A to micro-USB (Dell switch console port)
- #2 Phillips screwdriver, flashlight, 25 ft tape measure

**Questions**

1. **Rails.** The racks are Vertiv VR3300 with square holes, vertical rails adjustable, currently 29 in
   apart. Do the rail kits for item 4 fit?
2. **Lead time** for each item.
3. **100G optics.** Once we confirm the type (above), please quote 2 Cisco 100G QSFP28 optics for the
   lab's C9500X-28C8D and 2 Dell-compatible optics of the same type for our switch (item 4), plus
   Cisco-compatible third-party options if the lab allows them.
