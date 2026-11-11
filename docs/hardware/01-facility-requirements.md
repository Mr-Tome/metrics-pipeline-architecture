# 01. Facility requirements (send to the lab)

**Track:** Hardware (facility, network, rack, purchasing). Security decisions are in the [Cyber Security package](../cyber/README.md).

This is the answer to the lab's request in the README: power, cooling, connectors, and anything non-standard.
It covers the 50-user build that fits the $250,000 budget (one GPU server with all four GPUs, no staging),
and it is sized so the rack does not need new power when it grows to 100 users.

**Changed 2026-10-30:** the build is now 50 users with no staging server. Rack 1 peak draw went from
about 3.6 kW to about 4.8 kW, and heat from about 12,200 to about 16,400 BTU/hr. Nothing else changed.

**Changed 2026-11-06:** our switch (sw01) is now a Cisco Nexus N93180YC-FX3 instead of the Dell S5248F-ON.
It draws up to about 600 W instead of 250 W. Rack 1 peak draw goes from about 4.8 kW to about 5.1 kW, and
heat from about 16,400 to about 17,500 BTU/hr. If facilities already has the earlier numbers, send them this.

Status of each number:

- **Firm**: from the BOM, a vendor spec, or the site visit.
- **Confirm**: a planning figure. It must be checked against the final vendor quote.

## 1. Summary for facilities

| Item | Lab |
|---|---|
| Racks | 2 x Vertiv VR3300 (42U, 600 mm wide, 1200 mm deep, square holes), next to ACE 15. Rack 1 now, rack 2 held for growth. |
| Power | The existing Vertiv Geist rack PDUs: two per rack, left and right, mounted at the front of the rack (inside the cold aisle containment), each with circuits 1, 2, and 3 at 208V |
| A and B | Please confirm the left and right PDUs are fed from separate sources (A and B) |
| Outlets used, rack 1 | Per PDU: up to 2 x C19 (GPU server, if C20 inlets) and about 6 x C13 |
| Peak draw, 50 users | about 5.1 kW in rack 1, and each PDU must carry it alone if the other feed fails |
| Peak draw, 100 users (future) | about 8.7 kW across both racks |
| Heat load, 50 users | about 17,500 BTU/hr (about 1.5 tons) |
| Heat load, 100 users | about 29,500 BTU/hr (about 2.5 tons) |
| Airflow | Front to back. Fronts face into the cold aisle containment (the glass), exhaust goes out the rear into the room. |
| Intake air | 18 to 27 C (64.4 to 80.6 F), the ASHRAE recommended range |
| Weight | under 200 kg (440 lb) of equipment in rack 1 |
| Network | See section 5 |

There is no staging server. Everything is in the lab.

Nothing in this build is non-standard: no liquid cooling, no 400V or 480V, no special connectors. The only
items to watch are the GPU server power cord type (section 3) and the cord length to the front-mounted PDUs (section 4).

## 2. Power: what we need from the existing PDUs

The lab asked us not to question facility capacity, so this section only states our load.

1. **Redundancy.** Every device has two or more power supplies. Half go to the left PDU and half to the
   right PDU. If one side is lost, the other carries the whole rack, so **each PDU must be able to carry
   about 5.1 kW by itself** at 50 users.
2. **Spread across circuits.** Each PDU has circuits 1, 2, and 3. We spread our cords across all three,
   so no single circuit carries much more than a third of the load.
   The busiest circuit, with one feed down, carries about 2,050 W (9.9 A at 208V): half of gpu01 plus
   one service node.
3. **C19 outlets.** Each PDU has one C19 per circuit, so three per PDU. The GPU server uses two per PDU
   if its power supplies have C20 inlets. A second GPU server at the 100-user size goes in rack 2, which
   has its own PDUs.
4. **What we ask facilities to confirm:** the PDU model and input rating (on the PDU label), and that
   left and right are on separate sources.

## 3. Equipment power detail

From the BOM (`Assumptions` tab, section 4). Maximum draw, not typical draw. Typical inference load
runs well below this.

| Tag | Device | Qty (50 users) | Max W each | Input | Power cord (device to rack PDU) | Status |
|---|---|---|---|---|---|---|
| gpu01 | Thinkmate GPX GE95-2206-41, 2U, 4 x RTX PRO 6000 Server Edition | 1 | 3,300 (900 platform + 4 x 600 GPU) | 4 x 2000 W PSUs, 200-240V AC | C20 to C19, or C14 to C13. Depends on the PSU inlet. | **Confirm** with Thinkmate |
| svc01-03 | Thinkmate RAX RE95-1104-01, 1U | 3 | 400 | 2 x 1300 W PSUs (redundant), 100-240V AC | C14 to C13 | Confirm |
| sw01 | Cisco Nexus N93180YC-FX3 25G/100G switch | 1 | 600 | 2 x 650 W PSUs (NXA-PAC-650W-PE), 100-240V AC | C14 to C13 | Confirm (reseller datasheets say 600 W max) |
| oob01 | Cisco C1300-24T-4X management switch | 1 | 30 | 100-240V AC | C14 to C13 | Confirm |
| con01 | StarTech RKCONS1701 rack console | 1 | 13 | 100-240V AC | per vendor | Confirm |
| | **Lab total** | | **about 5,150 W** | | | |

**GPU power cap.** NVIDIA rates the RTX PRO 6000 Server Edition at 600 W, and the limit can be set
down to 400 W. If power ever becomes tight, we can cap the GPUs with `nvidia-smi -pl 400` and lose
some throughput instead of tripping a breaker.

## 4. Cooling

- The equipment is air cooled, front to back. The GPUs are passive cards that rely on the server
  chassis fans.
- The model number we were given, **CR035RA1A7X...**, is a **Vertiv Liebert CRV in-row cooling unit**
  (35 kW, air cooled). It sits in the row between racks. A 35 kW unit covers this load many times over.
- The row uses **cold aisle containment**: the glass doors close off the front of the racks, and the CRV
  supplies cool air into that contained aisle. Our server fronts face into the glass and take in the cool
  air; exhaust leaves the rear into the room, and the CRV draws it back from there. Switch ports are at
  the rear, with the server cabling, so the switches are ordered with port-side exhaust (intake at the
  PSU end, inside the glass).
- The Geist PDUs are mounted at the front, inside the glass. Server power supplies are at the rear, so
  every power cord runs the depth of the rack along the side channel. See the cord length note in
  [05](05-rack-build-guide.md), section 4.
- We will install blanking panels in every empty U, in both racks. Containment does not work without them:
  an open U lets cool air escape the contained aisle and lets warm room air in.
- Approximate airflow: about 810 CFM at 50 users, about 1,370 CFM at 100 users.
  This uses CFM = 3.16 x W / delta-T(F), with an assumed 20 F rise.

## 5. Network ports needed from the lab network team

See [03-network-and-switch-capacity.md](03-network-and-switch-capacity.md) for the reasoning.

| Need | Preferred | Fallback |
|---|---|---|
| Uplink from our lab switch | 2 x 100G QSFP28 ports on the C9500X-28C8D, LACP. We supply the optics (Cisco QSFP-40/100-SRBD). Confirmed 2026-11-06. | |
| Fiber between that switch and our rack | LC-LC OM4 multimode cords, run directly (no patch panel), 8 m or 15 m. We supply them. | |
| IP space | One /27 for servers, one /28 for BMC (out-of-band) | |
| Services | DNS, NTP, and the lab's internal CA certificate (for HTTPS on the chat page) | |
| Management | A third C9500X-28C8D port (10G via a QSA adapter we supply) for oob01. Confirmed 2026-11-06. | |

The last three rows are not needed for purchasing.

## 6. Space and handling

- **Racks:** Vertiv VR3300, 42U, 1200 mm deep, square holes. The vertical rails adjust and were measured
  at 29 in apart. The 2U GPU server rail kit must fit that range (vendor question).
- **Ground:** the doors have green bonding wires. Please confirm the rack frame itself is bonded to the
  facility ground.
- **Delivery:** wide single-story front door. No server lift on site. The GPU server ships at about 40 to
  50 kg boxed. Two-person lift. The layout keeps the heavy gear at U1 to U7, so no lift is needed.
