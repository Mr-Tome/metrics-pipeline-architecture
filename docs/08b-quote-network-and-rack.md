# 08b. Quote request: network, rack, and setup items (not yet sent)

**Status: ready to send (2026-11-06).** The network team confirmed a direct connection to the C9500X-28C8D:
2 x 100G for data and a third port for a separate management link. Our switch (item 4) is now a Cisco
Nexus N93180YC-FX3, so every optic is a Cisco part listed for the switch it goes in. Items 4, 5, and 6a-6e
are final. The servers and
GPUs were submitted separately ([08a](08a-quote-servers-submitted.md)).

Item numbers are kept from the original single request so references in other docs still match.

## Settled with the lab network team

| # | Question | Answer | 07 ID |
|---|---|---|---|
| P1 | Fiber and connector | Direct cords, no patch panel. Multimode LC for everything: QSFP-40/100-SRBD for 100G, SFP-10G-SR-S for management. Compatibility check: [03](03-network-and-switch-capacity.md), section 3. | N3 |
| P2 | Optic brand and version | Cisco-branded (our choice). IOS XE 17.15.06 (second-latest MD release). | N10 |
| P3 | Racks and distance | Racks next to ACE 15. About 12 ft between racks (their estimate); cords bought in 8 m and 15 m to cover the unmeasured route. | F6 |
| P4 | Management | Separate 10G link from oob01 to a third C9500X-28C8D port (QSA adapter). | N7 |
| P5 | Our switch | Cisco Nexus N93180YC-FX3 (the lab's own access model). Confirming the lab is comfortable with it ([10](10-lab-network-team-email.md), last section). | N15 |

---

**Subject:** Quote request: network, rack, and setup items, metrics analysis pipeline (50-user build)

Please get quotes for the items below. These go with the GPU server and service node order already
submitted. Government pricing (GSA, SEWP) is welcome.

**Network**

Item 4 is our top-of-rack switch: a **Cisco Nexus N93180YC-FX3**, replacing the Dell S5248F-ON. Items 6a-6c
are the two 100G data links from it to the lab's Cisco C9500X-28C8D (IOS XE 17.15.06), and items 6b-6e
include a separate 10G management link from our management switch (item 7) to the same C9500X. Every optic
is listed in Cisco's Optics-to-Device Compatibility Matrix for the switch it goes in. Cords come in two
lengths because the cable route is not measured yet; the unused length is the spare.

| # | Item | Part / model | Qty | Est. each | Est. total | Link |
|---|---|---|---|---|---|---|
| 4 | Top-of-rack switch, 48 x 1/10/25G SFP28, 6 x 40/100G QSFP28, NX-OS. **Airflow: port-side exhaust** (2 x NXA-PAC-650W-PE power supplies, NXA-FAN-35CFM-PE fans). Rack-mount kit for a 4-post rack. License: NX-OS (DCN) Essentials, shortest term offered (3 years); we do not need Advantage. 2 x C14-to-C13 power cords. New, not refurbished. | Cisco Nexus N9K-C93180YC-FX3, with 2 x NXA-PAC-650W-PE and NXA-FAN-35CFM-PE fans | 1 | $30,993.93 (switch $29,297.99, 2 x power supply $487.99, 4 x fan $179.99) + license | $30,993.93 + license | https://www.cdw.com/product/cisco-nexus-93180yc-fx3-switch-48-ports-managed-rack-mountable/6462067 (power supply: https://www.cdw.com/product/cisco-power-supply-hot-plug-redundant-650-watt/4236988, fan: https://www.cdw.com/product/cisco-network-device-fan-module/5497378) |
| 5 | 25G SFP28 passive direct attach cable, 3 m. Inside the rack: server 25G ports to our switch (item 4). 8 used, 2 spare. | Cisco SFP-H25G-CU3M= | 10 | $129.99 | $1,299.90 | https://www.cdw.com/product/cisco-sfp28-passive-copper-cable-direct-attach-cable-10-ft-orange/4285569 |
| 6a | 100G optic, QSFP28 BiDi, multimode, LC duplex. Two go in the lab C9500X-28C8D, two in our switch (item 4): one at each end of each data link. | Cisco QSFP-40/100-SRBD= | 4 | $2,014.99 | $8,059.96 | https://www.cdw.com/product/cisco-qsfp-transceiver-module-40gbe-100gbe/4899042 |
| 6b | Fiber cord, LC-LC duplex, OM4 multimode, **8 m**. Two for the data links (6a to 6a), one for the management link (6e to 6e). Plenum or riser rated if the lab requires. | any (example: Axiom) | 3 | $35.99 | $107.97 | https://www.cdw.com/product/axiom-lc-lc-multimode-duplex-om4-50-125-fiber-optic-cable-8m-aqua-patch-cable-8-m-8-m/6067521 |
| 6c | Fiber cord, LC-LC duplex, OM4 multimode, **15 m** (same as 6b, longer, in case the route is longer than estimated) | any (example: Axiom) | 3 | $45.99 | $137.97 | https://www.cdw.com/product/axiom-lc-lc-multimode-duplex-om4-50-125-fiber-optic-cable-15m-aqua-patch-cable-15-m-15-m/5863985 |
| 6d | QSFP to SFP+ adapter (QSA): goes in a QSFP28 port of the lab C9500X-28C8D and holds one 6e | Cisco CVR-QSFP-SFP10G= | 1 | $377.99 | $377.99 | https://www.cdw.com/product/cisco-network-adapter/4890545 |
| 6e | 10G optic, 10GBASE-SR SFP+ (multimode, LC). One in 6d (lab end), one in an SFP+ port of item 7 (our end). | Cisco SFP-10G-SR-S | 2 | $639.99 | $1,279.98 | https://www.cdwg.com/product/cisco-sfp-transceiver-module-10gbe/3731455 |
| 7 | Management switch, 24 x 1G, 4 x 10G SFP+ | Cisco Catalyst C1300-24T-4X | 1 | $1,047.99 | $1,047.99 | https://www.cdw.com/product/cisco-catalyst-1300-24t-4x-switch-24-ports-managed-rack-mountable/8112270 |
| 8 | Blanking panels, tool-less 1U, 10-pack (both racks) | Vertiv VRA2000 | 8 | $98.99 | $791.92 | https://www.cdw.com/product/vertiv-rack-toolless-airflow-blanking-panel-1u/5323823 |
| 9 | Cat6 patch cable, 10 ft (3 m), 10-pack. 3 ft is too short: BMC ports at U1-U7 run to the management switch at U40. | any | 2 | $72 | $144 | |
| 10 | Encrypted SSD, 4 TB, FIPS 140-2 (or the lab's approved type) | Apricorn Aegis Padlock Fortress A25-3PL256-S4000F | 2 | $2,774.99 | $5,549.98 | https://www.cdw.com/product/apricorn-4tb-fips-validated-aegis/4456344 |
| 11 | Rack console, 1U, 17" LCD, keyboard, VGA/USB | StarTech RKCONS1701 | 1 | $1,200 | $1,200 | https://www.startech.com/en-us/server-management/rkcons1701 |
| 12 | Setup kit (list below) | see list | 1 lot | $500 | $500 | |

**Total: $51,491.59 plus the item 4 license** (to be quoted). Prices are CDW's advertised prices on
2026-11-06, except items 9, 11 and 12 (estimates); item 4 counts the 4 fan modules its install guide lists. With the servers and GPUs (08a,
$187,025), the build comes to $238,516.59 plus the license, leaving **$11,483.41** under $250,000 for the
license and contingency. Please flag it if your quote for items 4-12, license included, passes $62,975.

**Setup checklist (item 12)**

- Label maker, Brother PT-E550W, plus 2 x Brother TZe-FX231 flexible ID tape (for cables)
- VELCRO brand ONE-WRAP ties, 3/4" x 8", 100-pack
- M6 cage nuts and screws, 50-pack, plus cage nut tool (the racks have square holes)
- ESD wrist strap
- Fiber cleaner, one-click, LC 1.25 mm
- Console cable: USB to RJ45 serial (the Nexus and C1300 consoles are both RJ45)
- #2 Phillips screwdriver, flashlight, 25 ft tape measure

**Questions**

1. **Rails.** The racks are Vertiv VR3300 with square holes, vertical rails adjustable, currently 29 in
   apart. Does the rack-mount kit for item 4 fit?
2. **Lead time** for each item, especially item 4.
3. **Switch configuration (item 4).** Please confirm the quote is for port-side exhaust airflow
   (NXA-PAC-650W-PE power supplies and NXA-FAN-35CFM-PE fans, not the -PI parts), that the power supplies
   and the full set of fans are included, and that the license is NX-OS Essentials at the shortest term.
4. **10G optic in item 7 (6e).** Please confirm the Catalyst C1300-24T-4X accepts Cisco SFP-10G-SR-S.
