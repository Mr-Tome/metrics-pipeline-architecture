# 08b. Quote request: network, rack, and setup items (not yet sent)

**Status: ready to send.** Revised for the new C9500X-28C8D above rows 2 and 3 (2026-11-04: 100G from
it to our switch is allowed, its uplink to the core is 10G, and we supply our own optics; 2026-11-05:
no patch panel in our racks, direct connection to the C9500X-28C8D, single-mode LC, IOS XE 17.15.06,
Cisco optics, racks next to ACE 15 with 20 m cords, management switch uplinked through our switch). The servers
and GPUs were submitted separately ([08a](08a-quote-servers-submitted.md)).

Item numbers are kept from the original single request so references in other docs still match.

## Answer these first (lab network team), before sending

Settled 2026-11-04: our switch connects to the new C9500X-28C8D above rows 2 and 3 at 100G, that
switch's own uplink to the core is 10G, and we supply the optics for both ends. The items below decide
which optics and cords to order (6a-6d) and how the management switch (7) connects (6e-6g).
Tracked in [07](07-open-questions.md). The email asking them is [10](10-lab-network-team-email.md).

| # | Question | Why it blocks the order | 07 ID |
|---|---|---|---|
| P1 | **Patch panels:** where do they go (in each rack, top of rack, or overhead), and do they reach our racks? Fiber type (OM4 multimode or single-mode)? Connector (MPO-12 or LC)? For MPO, which polarity (Type A, B, or C)? | **Answered 2026-11-05.** No panel in our racks; panels only in the middle rack of rows 2 and 3, for the main building. Our switch connects directly to the C9500X-28C8D. Fiber: single-mode, LC. Optic type: **100GBASE-CWDM4** (LR4 if the matrix lacks CWDM4). Cords: LC-LC duplex OS2. | N3 |
| P2 | ~~**Optic brand:** must the optics in the C9500X-28C8D be Cisco-branded, or are Cisco-compatible third-party optics allowed? Which IOS-XE version does it run?~~ | **Decided 2026-11-05: Cisco-branded** (our choice). Version: **IOS XE 17.15.06** (lab tracks the second-latest MD release). | N10 |
| P3 | ~~**Which racks:** which two adjacent racks in row 2 or 3 are ours?~~ | **Decided 2026-11-05: we keep the racks next to ACE 15** (row 4, to confirm). Uplink cords are 20 m. | F6 |
| P4 | ~~**Management network:** where does our management switch (item 7) uplink go?~~ | **Decided 2026-11-05: through our switch.** oob01 connects to sw01 inside the rack (items 6e-6g), and the management VLAN rides the 100G links. No extra C9500X-28C8D port. | N7 |

P1-P4 are settled and items 6a-6g below are final. The lab network team still has to confirm the cable
route and the VLAN plan ([10](10-lab-network-team-email.md), follow-up). Neither changes the parts.


---

**Subject:** Quote request: network, rack, and setup items, metrics analysis pipeline (50-user build)

Please get quotes for the items below. These go with the GPU server and service node order already
submitted. Government pricing (GSA, SEWP) is welcome.

**Network**

Items 6a-6d are the 100G uplink from our switch to the lab's new C9500X-28C8D, over single-mode LC
fiber. Please quote them; we have no price estimates yet. The C9500X-28C8D runs IOS XE 17.15.06, so please
confirm the Cisco optics are supported on that release.

| # | Item | Part / model | Qty | Est. each | Est. total | Link |
|---|---|---|---|---|---|---|
| 4 | 25G switch, 48 x SFP28, 4 x QSFP28, OS10. On the Dell page choose S5248F-ON, then **airflow: PSU to I/O (port-side exhaust)**. New, not refurbished. | Dell PowerSwitch S5248F-ON, 210-APFB | 1 | $3,515 | $3,515 | https://www.dell.com/en-us/shop/povw/networking-s-series-25-100gbe |
| 5 | 25G SFP28 direct attach cable, 3 m. Inside the rack: server 25G ports to our switch (item 4). 8 used, 2 spare. | Dell 470-ACEU | 10 | $100 | $1,000 | https://www.networktigers.com/a/s/products/dell-470-aceu-54m38-3m-25gb-sfp28-passive-direct-attach-cable |
| 6a | 100G optic, 100GBASE-CWDM4 QSFP28, lab end of the uplink: goes in the lab C9500X-28C8D. Cisco-branded. | Cisco QSFP-100G-CWDM4-S | 2 | quote | quote | |
| 6b | 100G optic, 100GBASE-CWDM4 QSFP28, our end of the uplink: goes in a QSFP28 port of our switch (item 4). Dell-branded or Dell-compatible. Fiber (6c) joins it to 6a. | Dell 100GBASE-CWDM4 QSFP28 | 2 | quote | quote | |
| 6c | Fiber cord, LC-LC duplex, **OS2 single-mode**, UPC, 20 m, one per uplink, run directly from our switch (row 4) to the C9500X-28C8D (above rows 2 and 3). Plenum or riser rated if the lab requires. | any | 2 | quote | quote | |
| 6d | Spare fiber cord, LC-LC duplex, OS2 single-mode, UPC, 20 m (same as 6c) | any | 1 | quote | quote | |
| 6e | 10G optic, management switch end: goes in an SFP+ port of item 7 | Cisco SFP-10G-SR-S | 1 | $500 | $500 | https://www.cdwg.com/product/cisco-sfp-transceiver-module-10gbe/3731455 |
| 6f | 10G optic, our switch end of the management link: goes in port 1/1/48 of item 4 | Dell 407-BBOU | 1 | $150 | $150 | https://www.networktigers.com/a/s/products/407-bbou-dell-transceiver-new |
| 6g | Fiber patch cord, LC-LC duplex, OM4, 3 m, joins 6e to 6f inside the rack | any | 1 | $25 | $25 | |
| 7 | Management switch, 24 x 1G, 4 x 10G SFP+ | Cisco Catalyst C1300-24T-4X | 1 | $1,100 | $1,100 | https://www.cdw.com/product/cisco-catalyst-1300-24t-4x-switch-24-ports-managed-rack-mountable/8112270 |
| 8 | Blanking panels, tool-less 1U, 10-pack (both racks) | Vertiv VRA2000 | 8 | $85 | $680 | https://www.cdw.com/product/vertiv-rack-toolless-airflow-blanking-panel-1u/5323823 |
| 9 | Cat6 patch cable, 10 ft (3 m), 10-pack. 3 ft is too short: BMC ports at U1-U7 run to the management switch at U40. | any | 2 | $72 | $144 | |
| 10 | Encrypted SSD, 4 TB, FIPS 140-2 (or the lab's approved type) | Apricorn Aegis Padlock Fortress A25-3PL256-S4000F | 2 | $1,800 | $3,600 | https://www.cdw.com/product/apricorn-4tb-fips-validated-aegis/4456344 |
| 11 | Rack console, 1U, 17" LCD, keyboard, VGA/USB | StarTech RKCONS1701 | 1 | $1,200 | $1,200 | https://www.startech.com/en-us/server-management/rkcons1701 |
| 12 | Setup kit (list below) | see list | 1 lot | $500 | $500 | |

**Total: $12,414 plus 6a-6d** (items 4-12; 6a-6d to be quoted). With the servers and GPUs (08a, $187,025),
the build comes to $199,439 plus 6a-6d, leaving $50,561 under $250,000 before 6a-6d.

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
3. **100G optics (6a, 6b).** Please confirm the Dell CWDM4 optic part number that our switch (item 4)
   supports, and that Cisco QSFP-100G-CWDM4-S is supported on the C9500X-28C8D at IOS XE 17.15.
4. **10G optic in item 7 (6e).** Please confirm the Catalyst C1300-24T-4X accepts Cisco SFP-10G-SR-S.
