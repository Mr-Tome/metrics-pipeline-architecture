# Open questions: hardware, facility, network, vendor

**Track:** Hardware. Questions for facilities, the lab network team, and the vendors. Each has an owner and a
default. If the question is not answered, the plan proceeds with the default. Update the Answer column as
answers come in.

Questions for the ISSM and Cyber Security (S) are in the [Cyber Security package](../cyber/README.md), including
the ones that affect the hardware install (S1, S2, S4, S8). Lab IT questions about software (L) are in
[Lab IT open questions](../software/open-questions.md). Closed questions, and the options considered for each
decision, are in the [decision log](decision-log.md).

## Facility (F)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| F1 | Rack model, depth, hole type | Site visit | | Vertiv VR3300, 42U, 600 x 1200 mm, square holes, rails adjustable (29 in apart now). The CR035RA1A7X is the Liebert CRV in-row cooler. |
| F2 | Which racks will we get? | Facilities | Two racks next to ACE 15: rack 1 now, rack 2 held for growth. **Cold aisle containment**: the glass closes off the front of the racks, and the Geist PDUs are at the front, inside the glass. |
| F3 | Are the existing left and right Geist PDUs fed from separate sources (A and B)? What is each PDU's input rating? | Facilities | Separate sources, each able to carry 5.1 kW | PDUs present: circuits 1-3 each, mostly C13, one C19 per circuit, 208V. Not marked A or B. Source and rating open. Lab is asking facilities (2026-11-04). |
| F4 | Is the rack frame bonded to facility ground? | Facilities | Yes | Door bonding straps seen; frame bond not seen. Open. |
| F5 | Rack PDU brand | Facilities | | Vertiv Geist, already installed. Nothing to buy. |
| F6 | Which two racks are ours, and how far are they from the C9500X-28C8D? | Facilities, lab network team | Stay next to ACE 15 | **Decided 2026-11-05: the two racks next to ACE 15** (believed to be row 4; confirm on the next visit). About 12 ft from the C9500X-28C8D (network team estimate); cords bought in 8 m and 15 m. Options considered: [Decision log](decision-log.md), D6. |
| F8 | Do 6 ft power cords reach from the server PSUs (rear) to the Geist PDUs (front, inside the glass)? | Next site visit: measure the cord route (site visit checklist) | Order 10 ft (3 m) cords | Open (2026-11-09). The server quote asked for 6 ft cords, written when the PDUs were thought to be at the rear. Front to rear is about 29 in at the rails, plus the run up or down to the circuit. svc03 to C1 and gpu01 to C2 are the longest runs and likely need more than 6 ft. |

## Network (N)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| N3 | The new patch panels: where do they go (in each rack, at the top of the rack, or overhead) and which racks do they reach? Multimode (OM4) or single-mode? MPO-12 or LC? For MPO, which polarity (Type A, B, or C)? | Lab network team | OM4 multimode, MPO-12, Type B (fits 100GBASE-SR4) | **Answered.** No patch panel in our racks (only the middle racks of rows 2 and 3 get one, for fiber to the main building). Direct cords, so we picked the fiber: **multimode LC**, Cisco QSFP-40/100-SRBD at both ends, listed for both switches. MPO polarity does not apply. Options considered: [Decision log](decision-log.md), D4. |
| N4 | The C9500X-28C8D uplink to the core is 10G: is it one link or two, and what else shares it? | Lab network team | Shared 10G, under 50% load | Low priority. SI traffic is under 10 Mbps at 50 users. Matters only for later bulk data. |
| N5 | IP subnets for servers (/27) and BMC (/28), plus DNS names for the chat and API endpoints | Lab network team | Assigned at install | Not needed for purchasing. Ask after the order. |
| N6 | DNS, NTP, and the internal CA (for the HTTPS certificate) | Lab network team | Lab provides all three | Not needed for purchasing. Ask after the order. |
| N7 | Where does the management switch uplink go: the C9500X-28C8D or a separate lab management switch? Fiber or copper? | Lab network team | Lab management VLAN over copper | **Decided 2026-11-06 (network team's recommendation):** separate 10G link from oob01 to a third C9500X-28C8D port (CVR-QSFP-SFP10G adapter with SFP-10G-SR-S, supported per Cisco's matrix). Options considered: [Decision log](decision-log.md), D5. |
| N8 | Who supplies the optics for the C9500X-28C8D ports? | Lab network team | | **We do (2026-11-04)**, both ends. Type depends on N3. |
| N9 | 100G or 10G between the C9500X-28C8D and our switch? | Lab network team | | **100G allowed (2026-11-04).** Plan: 2 x 100G LACP. |
| N10 | Must the optics in the C9500X-28C8D be Cisco-branded, or are Cisco-compatible third-party optics allowed? Which IOS-XE version does it run? | Lab network team | Cisco-branded | **IOS XE 17.15.06**, the second-latest Cisco MD (maintenance deployment) release, so it will move up over time: check the optics against 17.15 and the next MD train. **Cisco-branded** optics (our choice, 2026-11-05). Matrix checked ([Network and switch capacity](3-network-and-switch-capacity.md), section 3). |
| N14 | **Deferred until after the order:** single switch or vPC pair, LACP/vPC, cable route and who runs it, L2 trunk or routed, VLAN IDs and subnets, 802.1X/NAC, port security, MTU | Lab network team | L2 trunk, LACP, lab gateway | Not needed for purchasing. Ask after the order. |
| N15 | Is the lab network team comfortable with our top-of-rack switch being a Cisco Nexus N93180YC-FX3 (their own access model), using two of its six 100G QSFP28 ports to the C9500X-28C8D? | Lab network team | Yes | Sent ([Network team Q&A](records/lab-network-team-qa.md), Nexus note). Answer not recorded yet. The engineer noted it is "rated for 25G": true for its 48 server ports; its 6 uplink ports are 40/100G. |

## Vendor (V)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| V1 | GPU server PSU inlet type (C14 or C20) | Thinkmate | C20 | 4 x 2000 W (Thinkmate page). Inlet still open. Matters because each site PDU has only three C19 outlets. |
| V2 | 25G NICs in the quote | Thinkmate | | Specified in the email: Intel E810-XXVDA2 in the GPU servers (7 PCIe slots, room beside 4 GPUs), Broadcom N225P OCP 3.0 in the service nodes. |
| V3 | Lead time for the GPUs | Thinkmate, CDW | 4 to 8 weeks | |
| V4 | Rail kits fit a VR3300 (square holes, 1200 mm deep, rails 29 in apart and adjustable)? | Thinkmate, Cisco (sw01) | Yes | |
