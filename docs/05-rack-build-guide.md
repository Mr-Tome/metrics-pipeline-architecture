# 05. Rack build guide

Step-by-step for racking, powering, and cabling the lab rack (rack 1 of the two racks next to ACE 15).
Staging is the same with one server and no switches (see [04-prototype-plan.md](04-prototype-plan.md), section 4).

Site facts from visit 1 ([09](09-site-visit-checklist.md)):

- Vertiv VR3300 racks: 42U, 1200 mm deep, square holes, adjustable rails
- Vertiv Geist PDUs already mounted, left and right
- Hot aisle containment: the rear of the rack is inside the glass. That is where you work on cables and PDUs.
- No lift, crash cart, or console on site

Diagrams (open the SVG files for full size; they print well on 11x17):

- [Rack elevation](diagrams/rack-elevation.svg)
- [Power wiring](diagrams/power-wiring.svg)
- [Network cabling](diagrams/network-cabling.svg)

![Rack elevation](diagrams/rack-elevation.svg)

## 0. Vendor guides and videos

Use the vendor's own document for each step that touches their hardware. No official install videos
were found for the exact models in this build, so the vendor PDFs are the primary reference. Ask
Thinkmate whether they offer an install walkthrough with the order.

| Hardware | Official guide | What to read |
|---|---|---|
| Vertiv VR3300 rack | VR Rack Installer/User Guide, SL-11425: https://www.vertiv.com/globalassets/shared/sl-11425_rev0.pdf. Product page: https://www.vertiv.com/en-ca/products-catalog/facilities-enclosures-and-racks/racks-and-containment/vr3300/ | 4.6 rails, 4.9 grounding |
| Vertiv Geist rack PDU (already installed) | Vertiv rPDU and VR rack integration flyer: https://www.vertiv.com/49bd35/globalassets/shared/vertiv-rpdu-vr-rack-integration-flyer.pdf. For the full manual, search the model number from the PDU label on vertiv.com. | Outlet and circuit layout, display |
| Liebert CRV (the CR035RA unit) | Liebert CRV design manual: https://www.vertiv.com/globalassets/products/thermal-management/in-row-cooling/liebert-crv-row-based-cooling-system-design-manual.pdf | Facility's job, for reference only |
| Dell S5248F-ON | S5200F-ON Series Installation Guide: https://dl.dell.com/topicspdf/s5200-on_install_pub_en-us.pdf | ReadyRails 1U tool-less square-hole install, power, airflow |
| Thinkmate GPU server and service nodes | Ships with a quick-start and rail kit sheet. Ask Thinkmate for the motherboard and chassis manuals when you order. | Rails, GPU install, PSU, BMC first login |
| StarTech RKCONS1701 rack console | https://www.startech.com/en-us/server-management/rkcons1701 (manual under Support) | Rail and cage nut install |
| NVIDIA RTX PRO 6000 Server Edition | Server Edition product brief (NVIDIA site, PDF) | Passive card, 16-pin power, 400-600 W setting |

For video, search YouTube with the exact model number (for example "Vertiv VR3300 rail install" or
"S5248F-ON rack install"). Watch the vendor's own channel first. Generic "server rail install" videos
work fine for the sliding-rail steps, which are the same on almost every 2U server.

## 1. Before you start

**Tools:** the setup kit in the quote request ([08](08-quote-request-email.md), item 14) and the rack
console (item 13). Use velcro, not zip ties.

**People:** two people for the GPU server. Never lift it alone.

**Check the delivery against the BOM:**

- [ ] gpu01: 2 GPUs installed (or loose in boxes), 2 x 3.84 TB NVMe, dual-port 25G NIC, rail kit, power cords
- [ ] svc01, svc02, svc03: rail kits, cords
- [ ] sw01 S5248F-ON: airflow is **PSU-to-port (port-side exhaust)**. Check the fan and PSU handle color
      against the Dell guide. **If it is wrong, stop and swap it.** Don't install it.
- [ ] oob01 management switch
- [ ] Rack console (StarTech RKCONS1701) with its VGA/USB cable, rails, and cage nuts
- [ ] Power cords: C13-to-C14 for service nodes and switches; C13-to-C14 or C19-to-C20 for the GPU server (no wall-plug cords)
- [ ] 10 x 25G SFP28 DAC, 3 m (8 used now, 2 spare)
- [ ] Uplink optics and fiber patch cords (option A or B from [03](03-network-and-switch-capacity.md))
- [ ] Cat6 patch cables, 6 x 3 m (BMC and oob01 uplink)
- [ ] Blanking panels: 80 (about 30 for rack 1, 42 for rack 2, spares)

## 2. Rack prep

1. Confirm the rack: rack 1 of the two next to ACE 15. **The front faces the room. The rear is inside the
   hot aisle containment.** Servers go in from the front, cables are done from the rear.
2. Confirm with facilities that the rack frame is bonded to facility ground (SL-11425 section 4.9).
   The green wires on the doors only bond the doors to the frame.
3. Set the 19" rails. In VR racks, the built-in rail alignment marks set the front rail position. Set the
   rear rails so the depth matches the GPU server's rail kit (the server rail is the longest; set for it).
4. The Geist PDUs are already mounted, left and right, at the rear. Once facilities says which side is
   feed A, label the left PDU and the right PDU `PDU-A` and `PDU-B` (or the other way round).
5. Check each PDU's display is on (if fitted) and every outlet is empty.

## 3. Install equipment, bottom up

Install heaviest first, at the bottom, so the rack can't tip.

| U | Item | Notes |
|---|---|---|
| 1-2 | gpu01 | Rails first, then slide the server in with two people. Confirm it latches. |
| 3-4 | (reserved gpu02) | Blanking panels for now |
| 5 | svc01 | |
| 6 | svc02 | |
| 7 | svc03 | |
| 8-20 | blanking | Install all of them before power-on |
| 21 | con01 rack console | Eye height for a seated or kneeling person. Cage nuts (square holes). |
| 22-39 | blanking | |
| 40 | oob01 | Ports to the rear |
| 41 | sw01 | Ports to the rear, PSUs to the front. Dell ReadyRails, tool-less. |
| 42 | Fiber patch panel, if needed | Only if the lab's fiber needs one. Otherwise blanking. |

**Rack 2** (held for growth): fill all 42U with blanking panels now, so it doesn't leak hot air from
the contained aisle.

**GPU install, if the GPUs come loose:**

1. ESD strap on. Server unplugged, out on its rails or on a bench.
2. Use the slots the vendor marks for GPUs 1 and 2. Leave slots 3 and 4 for growth.
3. Seat the card fully. Fasten the bracket. Connect the 16-pin power cable until it clicks. A half-seated
   16-pin connector is the most common failure on 600 W cards: **push it in until there is no gap.**
4. Install the air shroud or baffle the vendor supplies. Passive GPUs overheat without it.
5. Fit slot covers or the vendor's blank fillers in the empty GPU slots.

## 4. Power cabling

![Power wiring](diagrams/power-wiring.svg)

**What A and B mean.** Each rack has two Geist PDUs, one left and one right. If facilities feeds them
from separate sources (A and B), losing one source leaves the other PDU running. Every server has two
or more power supplies, each with its own cord. Half of a server's cords go to the left PDU and half to
the right. Then if feed A fails, everything keeps running on B. Pictures of this:

- Oracle server guide, dual power feed: https://docs.oracle.com/cd/E55211_01/html/E55213/gqcnz.html
- Austin Hughes, A and B PDUs in a rack: https://www.austin-hughes.com/solutions/infrapower/dual-feed-pdu/

**How you know which is A and which is B.** The PDUs are not marked. Facilities knows which upstream
panel and breaker feed each one. Ask them ([09](09-site-visit-checklist.md)), then label the PDUs.

**Circuits on each PDU.** Each PDU has circuits 1, 2, and 3. Each circuit has its own breaker on the PDU,
mostly C13 outlets, and one C19. On a 3-phase PDU, each circuit is one phase pair.

0. **Before plugging anything in:** facilities confirms that the upstream feeds to both PDUs are off and
   locked out per the lab's lockout/tagout process, or confirms in writing that plugging in with the
   PDUs live is their normal practice. Check every PDU circuit breaker is switched off.
1. Label every cord at both ends **before** plugging in: `gpu01-PSU1 / A-C1-C19`, and so on.
2. Plug every device's odd-numbered PSU into PDU-A and its even-numbered PSU into PDU-B. **Never put
   both PSUs of one device on the same PDU.** The GPU server has 4 PSUs: PSU1 and PSU3 to A, PSU2 and PSU4 to B.
3. Spread the load across the PDU's three circuits. Plan for each PDU:
   - Circuit 1: gpu01 PSU (C19 if C20 cords, else a C13), svc01
   - Circuit 2: gpu01 PSU (C19 if C20 cords, else a C13), svc02
   - Circuit 3: svc03, sw01, and oob01 or the console (one on each PDU)

   After power-on, the PDU display shows the current on each circuit. If one is much higher than the
   others, move a cord to a lighter circuit.
4. Facilities removes the lockout. Switch the PDU circuit breakers on.
5. Power on in this order: switches, then service nodes, then gpu01.
6. **Feed test:** with everything running, facilities switches feed A **off** upstream. Everything must stay
   up on PDU-B. Facilities switches A back on. Wait 2 minutes, then repeat with feed B off. Same result.
   Record the current on each circuit from each PDU display. Only facilities switches the upstream feeds.
7. Close the hot aisle containment doors when you finish. Cable work at the rear is done before power-on,
   because the contained aisle gets hot once the servers run.

## 5. Network cabling

![Network cabling](diagrams/network-cabling.svg)

### Cable schedule

Label each cable at both ends with its ID.

| ID | From | To | Cable | Purpose |
|---|---|---|---|---|
| D01 | gpu01 NIC port 1 | sw01 1/1/1 | 25G SFP28 DAC 3 m | data, bond member 1 |
| D02 | gpu01 NIC port 2 | sw01 1/1/2 | 25G SFP28 DAC 3 m | data, bond member 2 |
| D03 | svc01 NIC port 1 | sw01 1/1/3 | 25G SFP28 DAC 3 m | data |
| D04 | svc01 NIC port 2 | sw01 1/1/4 | 25G SFP28 DAC 3 m | data |
| D05 | svc02 NIC port 1 | sw01 1/1/5 | 25G SFP28 DAC 3 m | data |
| D06 | svc02 NIC port 2 | sw01 1/1/6 | 25G SFP28 DAC 3 m | data |
| D07 | svc03 NIC port 1 | sw01 1/1/7 | 25G SFP28 DAC 3 m | data |
| D08 | svc03 NIC port 2 | sw01 1/1/8 | 25G SFP28 DAC 3 m | data |
| (D09-D10) | reserved gpu02 | sw01 1/1/9-10 | | future |
| U01 | sw01 QSFP28 uplink 1 | patch panel port 1, then C9500X | 100G optic + fiber | uplink (option A) |
| U02 | sw01 QSFP28 uplink 2 | patch panel port 2, then C9500X | 100G optic + fiber | uplink (option A) |
| M01 | gpu01 BMC | oob01 port 1 | Cat6 3 m | management |
| M02 | svc01 BMC | oob01 port 2 | Cat6 3 m | management |
| M03 | svc02 BMC | oob01 port 3 | Cat6 3 m | management |
| M04 | svc03 BMC | oob01 port 4 | Cat6 3 m | management |
| M05 | sw01 mgmt port | oob01 port 5 | Cat6 3 m | management |
| M06 | oob01 uplink | lab management network | per lab | management |

Check sw01 port numbering on the faceplate. The Dell OS10 names are `ethernet 1/1/1` to `1/1/48` for
SFP28. The QSFP28 uplink numbers vary by OS10 version, so run `show interface status` to see them.

### Steps

1. Run DACs along the side of the rack in velcro bundles. Don't bend them tighter than about a 5 cm radius.
2. Fiber: keep the dust caps on until you plug in. Clean each connector with a one-click cleaner first.
   For MPO (100G-SR4), check polarity with the network team (usually Type B trunk).
3. Plug BMC Cat6 last so it doesn't get buried.
4. Install the rear door. Check that no cable bundle blocks server exhaust.

## 6. First power-on checks

1. **Switch:** console in, set the management IP, then confirm `show interface status` shows each D-cable
   link up at 25G.
2. **BMC:** each server's BMC gets an IP (DHCP or set at the BIOS screen using the rack console). Change the
   default password at first login. Record it in the lab's approved password store.
3. **BIOS settings on gpu01** (and stg01):
   - Above 4G decoding: on
   - Resizable BAR: on
   - SR-IOV: on
   - IOMMU: on
   - Power profile: performance
   - Boot mode: UEFI
   - Secure Boot: per lab policy. With Secure Boot on, the NVIDIA driver must be signed, so tell the
     software team.
4. Install the OS, then run `validate/hw-check.sh --gpus 2`. It checks:
   - GPU count, and that each GPU is on PCIe Gen5 x16
   - GPU temperature and power limit
   - NVMe drives present
   - NIC link speed
5. Run `validate/net-test.sh` between nodes.
6. Take photos of the front and rear of the finished rack, and of each PDU display under load. Add them to
   `docs/photos/` (the as-built record).

## 7. Sign-off

- [ ] Feed A / feed B test passed
- [ ] All D-links up at 25G, uplinks up and in a port-channel
- [ ] `hw-check.sh` passed on every node
- [ ] All empty U blanked, rear door on, cold-aisle intake in range
- [ ] Cable labels match this schedule
- [ ] Photos added
