# 07. Open questions

Questions that block or change the plan. Each has an owner and a default. If the question is not
answered, the plan proceeds with the default. Update the Answer column as answers come in.

## Facility (F)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| F1 | Rack model, depth, hole type | Site visit | | Vertiv VR3300, 42U, 600 x 1200 mm, square holes, rails adjustable (29 in apart now). The CR035RA1A7X is the Liebert CRV in-row cooler. |
| F2 | Which racks will we get? | Facilities | | Two racks next to ACE 15: rack 1 now, rack 2 held for growth. Hot aisle containment (glass closes off the rear). |
| F3 | Are the existing left and right Geist PDUs fed from separate sources (A and B)? What is each PDU's input rating? | Facilities | Separate sources, each able to carry 4.8 kW | PDUs present: circuits 1-3 each, mostly C13, one C19 per circuit, 208V. Not marked A or B. Source and rating open. Lab is asking facilities (2026-11-04). |
| F4 | Is the rack frame bonded to facility ground? | Facilities | Yes | Door bonding straps seen; frame bond not seen. Open. |
| F5 | Rack PDU brand | Facilities | | Vertiv Geist, already installed. Nothing to buy. |
| F6 | Which two adjacent racks in row 2 or row 3 are ours? (The new C9500X-28C8D and patch panels are above rows 2 and 3.) | Facilities, lab network team | Stay next to ACE 15 | 2026-11-04: our switch will connect to the C9500X-28C8D, so rows 2 or 3. Exact racks open. Blocks the network order ([08b](08b-quote-network-and-rack.md), P3). |
| F7 | If we move to row 2 or 3: do those racks match what we planned for? Vertiv VR3300 (42U, 1200 mm deep, square holes), two Geist PDUs on separate A and B feeds that can each carry 4.8 kW alone, three C19 outlets per PDU, in-row CRV cooling, and hot aisle containment. | Facilities | Same as the ACE 15 racks | Yes, all the same (confirmed 2026-11-03). Moving to row 2 or 3 changes nothing for rack, power, or cooling. |

## Network (N)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| N1 | Exact access switch model | Lab network team | | C9300-48S (confirmed). One in the analysts' building, one in the rack building, both uplinked to the C9500X. **New 2026-11-03:** the lab is installing a C9500X-28C8D above rows 2 and 3, plus patch panels. |
| N2 | May our switch connect directly to the new C9500X-28C8D above rows 2 and 3? | Lab network team | | **Yes (2026-11-04).** 100G from the C9500X-28C8D to our switch. That switch's uplink to the core is 10G. Option B (C9300-48S) is no longer the plan. |
| N3 | The new patch panels: where do they go (in each rack, at the top of the rack, or overhead) and which racks do they reach? Multimode (OM4) or single-mode? MPO-12 or LC? For MPO, which polarity (Type A, B, or C)? | Lab network team | OM4 multimode, MPO-12, Type B (fits 100GBASE-SR4) | Panels announced 2026-11-03. **Not asked yet.** Blocks the network order ([08b](08b-quote-network-and-rack.md), P1). |
| N4 | The C9500X-28C8D uplink to the core is 10G: is it one link or two, and what else shares it? | Lab network team | Shared 10G, under 50% load | Low priority. SI traffic is under 10 Mbps at 50 users. Matters only for later bulk data. |
| N5 | IP subnets for servers (/27) and BMC (/28), plus DNS names for the chat and API endpoints | Lab network team | Assigned at install | Not needed for purchasing. Ask after the order. |
| N6 | DNS, NTP, and the internal CA (for the HTTPS certificate) | Lab network team | Lab provides all three | Not needed for purchasing. Ask after the order. |
| N7 | Where does the management switch uplink go: the C9500X-28C8D or a separate lab management switch? Fiber or copper? | Lab network team | Lab management VLAN over copper | Now blocks the network order: one more optic pair if it goes to the C9500X-28C8D ([08b](08b-quote-network-and-rack.md), P4). |
| N8 | Who supplies the optics for the C9500X-28C8D ports? | Lab network team | | **We do (2026-11-04)**, both ends. Type depends on N3. |
| N9 | 100G or 10G between the C9500X-28C8D and our switch? | Lab network team | | **100G allowed (2026-11-04).** Plan: 2 x 100G LACP. |
| N10 | Must the optics in the C9500X-28C8D be Cisco-branded, or are Cisco-compatible third-party optics allowed? Which IOS-XE version does it run? | Lab network team | Cisco-branded | Open. Blocks the network order ([08b](08b-quote-network-and-rack.md), P2). |

## Security (S)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| S1 | Is the lab classified? What is the approved process to bring hardware in? | ISSM | Classified; hardware one way only | |
| S2 | May new lab hardware be burned in on the unclassified side before it enters (then wiped)? | ISSM | No; burn in inside the lab | |
| S3 | Approved transfer media type, and how long a transfer takes | ISSM | Encrypted SSD, 1 week turnaround | |
| S4 | Is Secure Boot required on servers? (It changes how the NVIDIA driver is installed.) | ISSM | Off | |
| S5 | Is there an approved model list? Is gpt-oss-120b (Apache 2.0) acceptable? | Program | Yes, pending approval | |
| S6 | Are upstream (non-Iron Bank) images allowed in the lab for phase 1? | ISSM | Iron Bank where available, upstream otherwise | |
| S7 | Where may the staging server live? | Program | | No staging server (decided 2026-10-30). The build workstation rehearses each bundle; see [04](04-prototype-plan.md). |
| S8 | Is a laptop allowed in the room for first switch setup over a console cable? | ISSM | No; use the lab's approved device | |
| S9 | Future phase: may a typed decision model (Cloudflare Clef, Qwen3.8-27B base, Apache 2.0) run in the lab? It ships a Python code file that runs at load time, and it needs its own model server (SGLang) and gateway route. | ISSM, Program | Deferred; not in phase 1 | Deferred 2026-10-30 |

## Lab IT (L)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| L1 | Does the lab's accreditation require a specific server OS (for example RHEL 9 with STIG)? Is there a package mirror? Asked in the quote email ([08a](08a-quote-servers-submitted.md), question 6). | Lab IT, ISSM | Rocky Linux 9 (free); RHEL 9 if required, at about $1,400 per server per year | Our choice unless accreditation says otherwise. It matters for two reasons: the NVIDIA driver is built against the OS kernel, so the driver package must match it; and RHEL needs paid subscriptions (not in the BOM), while Rocky Linux 9 is free and compatible. |
| L2 | Does the lab already run Kubernetes? | Lab IT | | No. We bring our own (RKE2). |
| L3 | Python versions on analyst machines, and Windows or Linux? | Lab IT | | Many versions, mostly Windows, some Linux. Client packages must cover Python 3.9 to 3.13 on both. |
| L5 | Internet access during the initial build and debug? | ISSM | No. All software arrives on transfer media. | |
| L4 | Is MATLAB allowed to make HTTPS calls to an internal service? | Lab IT | Yes | |

## Vendor (V)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| V1 | GPU server PSU inlet type (C14 or C20) | Thinkmate | C20 | 4 x 2000 W (Thinkmate page). Inlet still open. Matters because each site PDU has only three C19 outlets. |
| V2 | 25G NICs in the quote | Thinkmate | | Specified in the email: Intel E810-XXVDA2 in the GPU servers (7 PCIe slots, room beside 4 GPUs), Broadcom N225P OCP 3.0 in the service nodes. |
| V3 | Lead time for the GPUs | Thinkmate, CDW | 4 to 8 weeks | |
| V4 | Rail kits fit a VR3300 (square holes, 1200 mm deep, rails 29 in apart and adjustable)? | Thinkmate, Dell | Yes | |
