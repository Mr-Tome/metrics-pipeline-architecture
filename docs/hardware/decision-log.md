# Hardware decision log

**Track:** Hardware (facility, network, rack, purchasing). Security decisions are in the [Cyber Security package](../cyber/README.md).

The other hardware documents state only the current plan. This page keeps the real choices we made: for each
decision, the options we weighed, what we picked, and why. It is the record for future builds and the starting
list of choices for a configurator: each decision below is one question a configurator would ask, with the
options and the facts that decide between them.

Information that turned out to be wrong (an early drawing, a misunderstanding, a mis-recorded site detail) is
not kept here. Once it is corrected, the documents carry only the correct answer.

Open questions are in [Hardware open questions](open-questions.md).

## D1. Size of the build (2026-10-30)

| Option | Original BOM with staging | Original BOM, lab only | Workbook now (lab, Nexus switch, additions) | Fits $250k? |
|---|---|---|---|---|
| 20 users | $221,086 | $155,048 | $202,024.59 | Yes |
| **50 users (chosen)** | $257,578 | $191,540 | $238,516.59 + switch license | Yes, $11,483 left |
| 100 users | $382,869 | $316,831 | $391,586.42 (two Nexus switches) | No |

**Picked:** 50 users, no staging. Fills all four GPU slots in gpu01 and keeps all three service nodes. Growing
to 100 users adds a second GPU server in rack 2; nothing is replaced ([Budget and BOM](1-budget-and-bom.md), section 5).

## D2. Staging server (2026-10-30)

| Option | Cost | Effect |
|---|---|---|
| Staging: one GPU server with one GPU, outside the lab | $66,038 | Every bundle tested on a GPU before it reaches the lab |
| **No staging (chosen)** | $0 | The build workstation rehearses each bundle in a VM; GPU-dependent steps are first tested on the lab rack ([Prototype plan](../software/1-prototype-plan.md)) |

**Why:** the lab decided not to have staging. The money paid for gpu01's third and fourth GPUs, the switch, and
the install items. Rack 1 peak draw went from about 3.6 kW to about 4.8 kW, and heat from about 12,200 to
about 16,400 BTU/hr ([Facility requirements](2-facility-requirements.md)).

## D3. Top-of-rack switch, sw01 (2026-11-06)

| Option | Price | For | Against |
|---|---|---|---|
| Dell S5248F-ON (in the original BOM) | $3,515 | Cheap; 48 x 25G, 4 x 100G | Cisco lists no 100G multimode LC optic for the C9500X-28C8D that a Dell switch supports, and Dell's site would not confirm a single-mode alternative. Every uplink optic would be a cross-vendor guess. |
| **Cisco Nexus N93180YC-FX3 (chosen)** | about $31,000 at CDW, plus the NX-OS license | Every optic on both ends is listed in Cisco's compatibility matrix. The lab already runs this model. 6 x 40/100G uplinks, room for gpu02. | Most of the budget change; the license must be Essentials, not Advantage ($19,405), to stay inside $250k |
| No switch: servers plug straight into a lab switch | $0 | Nothing to buy | The service nodes reach the GPU over the lab network, and the network team has to carry our east-west traffic. Not recommended. |

**Power:** the Nexus draws up to about 600 W instead of 250 W. Rack 1 peak draw went from about 4.8 kW to about
5.1 kW, and heat from about 16,400 to about 17,500 BTU/hr.

**"Rated for 25G."** The network engineer noted the N93180YC-FX3 is rated for 25G. That is true of its 48
server ports. Its 6 uplink ports are 40/100G QSFP28. In the lab's own network those uplinks are usually taken,
so a device plugged into their N93180YC-FX3 gets 25G. Ours is our own switch, so its uplinks are ours.

## D4. Link speed, fiber, and optics (2026-11-06)

| Option | Status |
|---|---|
| 2 x 25G SFP28 | Enough for chat traffic (under 10 Mbps at 50 users). Not needed once the lab offered 100G ports. |
| **2 x 100G QSFP28, LACP (chosen)** | Allowed by the lab 2026-11-04. Leaves room for later bulk data. |
| MPO-12 multimode through a patch panel (100GBASE-SR4) | Our racks have no patch panel. |
| Single-mode LC (100GBASE-CWDM4, LR4, or FR) | The only route with the Dell switch. Dropped with the Dell. |
| **Multimode LC, Cisco QSFP-40/100-SRBD at both ends (chosen)** | Listed for both the C9500X-28C8D and the N93180YC-FX3. |
| Third-party Cisco-compatible optics | Allowed to ask; we chose Cisco-branded (2026-11-05). |

## D5. Management (BMC) uplink (2026-11-06)

| Option | Status |
|---|---|
| Through sw01: oob01 to sw01 at 10G, management VLAN on the 2 x 100G links | Uses no extra lab port, but management depends on sw01 and the data links. |
| **Separate 10G link from oob01 to a third C9500X-28C8D port, CVR-QSFP-SFP10G adapter with SFP-10G-SR-S (chosen)** | The network team's recommendation, 2026-11-06. Management still works if sw01 or the data links go down. |

## D6. Rack location and cord length (2026-11-05, 2026-11-06)

| Option | Status |
|---|---|
| Two racks in row 2 or row 3, under the C9500X-28C8D | Facilities confirmed 2026-11-03 they are identical (VR3300, Geist PDUs, CRV cooling, cold aisle containment). |
| **The two racks next to ACE 15 (chosen)** | Decided 2026-11-05. Believed to be row 4; confirm on the next visit. |
| **Cords: 3 x 8 m and 3 x 15 m (chosen)** | The network team estimated about 12 ft between racks. Two lengths cover the unmeasured route; the unused set is the spare. |
