# 07. Open questions

Questions that block or change the plan. Each has an owner and a default. If the question is not
answered, the plan proceeds with the default. Update the Answer column as answers come in.

## Facility (F)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| F1 | Rack model, depth, hole type | Site visit | | Vertiv VR3300, 42U, 600 x 1200 mm, square holes, rails adjustable (29 in apart now). The CR035RA1A7X is the Liebert CRV in-row cooler. |
| F2 | Which racks will we get? | Facilities | | Two racks next to ACE 15: rack 1 now, rack 2 held for growth. Hot aisle containment (glass closes off the rear). |
| F3 | Are the existing left and right Geist PDUs fed from separate sources (A and B)? What is each PDU's input rating? | Facilities | Separate sources, each able to carry 5.1 kW | PDUs present: circuits 1-3 each, mostly C13, one C19 per circuit, 208V. Not marked A or B. Source and rating open. Lab is asking facilities (2026-11-04). |
| F4 | Is the rack frame bonded to facility ground? | Facilities | Yes | Door bonding straps seen; frame bond not seen. Open. |
| F5 | Rack PDU brand | Facilities | | Vertiv Geist, already installed. Nothing to buy. |
| F6 | Which two adjacent racks in row 2 or row 3 are ours? (The new C9500X-28C8D and patch panels are above rows 2 and 3.) | Facilities, lab network team | Stay next to ACE 15 | **Decided 2026-11-05: we keep the two racks next to ACE 15** (believed to be row 4; confirm on the next visit). The uplink runs from there to the C9500X-28C8D: 10 m is too short, 20 m is enough with a few meters spare. **2026-11-06:** the network team doesn't know "ACE 15". Asking what they call our racks and which RHINO they are in ([10](10-lab-network-team-email.md), round 3, Q1). **2026-11-06 (later):** racks are about 12 ft apart (network team estimate). We buy cords in 8 m and 15 m to cover it. |
| F7 | If we move to row 2 or 3: do those racks match what we planned for? Vertiv VR3300 (42U, 1200 mm deep, square holes), two Geist PDUs on separate A and B feeds that can each carry 4.8 kW alone, three C19 outlets per PDU, in-row CRV cooling, and hot aisle containment. | Facilities | Same as the ACE 15 racks | Yes, all the same (confirmed 2026-11-03). Moving to row 2 or 3 changes nothing for rack, power, or cooling. |

## Network (N)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| N1 | Exact access switch model | Lab network team | | C9300-48S (confirmed). One in the analysts' building, one in the rack building, both uplinked to the C9500X. **New 2026-11-03:** the lab is installing a C9500X-28C8D above rows 2 and 3, plus patch panels. **2026-11-05:** we assume the C9300s are not in our path; the C9500X-28C8D is the only lab switch we connect to. |
| N2 | May our switch connect directly to the new C9500X-28C8D above rows 2 and 3? | Lab network team | | **Yes (2026-11-04).** 100G from the C9500X-28C8D to our switch. That switch's uplink to the core is 10G. Option B (C9300-48S) is no longer the plan. **Reversed 2026-11-06:** most likely **not** direct to the C9500X. It is the core/aggregation layer and the link to the other building. Our access switch is a Cisco N93180YC-FX3 (N11-N14). **Re-confirmed 2026-11-06 (later): yes, direct.** The N93180YC-FX3 answer was a mix-up (they thought the Dell was a server). 2 x 100G on the C9500X-28C8D. |
| N3 | The new patch panels: where do they go (in each rack, at the top of the rack, or overhead) and which racks do they reach? Multimode (OM4) or single-mode? MPO-12 or LC? For MPO, which polarity (Type A, B, or C)? | Lab network team | OM4 multimode, MPO-12, Type B (fits 100GBASE-SR4) | **Answered 2026-11-05.** Only the middle rack of row 2 and of row 3 gets a patch panel, and it carries fiber back to the main building. Our racks get none: our switch connects straight to the C9500X-28C8D. The lab's fiber is **single-mode, LC**. So our optics are single-mode LC: 100GBASE-CWDM4 (plan) or LR4. No MPO, so polarity does not apply. **2026-11-06:** single-mode LC describes the patch panels to the main building. The fiber to the N93180YC-FX3 is unknown (N13). **Decided 2026-11-06:** direct cords, so we pick the fiber. 100G: single-mode LC (100GBASE-FR). Cisco lists no 100G multimode LC optic that interoperates with Dell ([03](03-network-and-switch-capacity.md), section 3). **Changed 2026-11-06 (switch now Cisco Nexus):** multimode LC after all, as the engineer said. QSFP-40/100-SRBD at both ends, listed for both the C9500X-28C8D and the N93180YC-FX3. |
| N4 | The C9500X-28C8D uplink to the core is 10G: is it one link or two, and what else shares it? | Lab network team | Shared 10G, under 50% load | Low priority. SI traffic is under 10 Mbps at 50 users. Matters only for later bulk data. |
| N5 | IP subnets for servers (/27) and BMC (/28), plus DNS names for the chat and API endpoints | Lab network team | Assigned at install | Not needed for purchasing. Ask after the order. |
| N6 | DNS, NTP, and the internal CA (for the HTTPS certificate) | Lab network team | Lab provides all three | Not needed for purchasing. Ask after the order. |
| N7 | Where does the management switch uplink go: the C9500X-28C8D or a separate lab management switch? Fiber or copper? | Lab network team | Lab management VLAN over copper | **Decided 2026-11-05 (our design): through sw01.** oob01 connects to sw01 port 1/1/48 at 10G inside the rack, and the management VLAN rides the 2 x 100G links. No extra C9500X-28C8D port. Asking the lab to confirm and give VLAN IDs ([10](10-lab-network-team-email.md), follow-up). **Reopened 2026-11-06** for the N93180YC-FX3 design (round 3, Q5). Our plan is unchanged: through sw01. **Decided 2026-11-06 (network team's recommendation):** separate 10G link from oob01 to a third C9500X-28C8D port (CVR-QSFP-SFP10G adapter, supported per Cisco's matrix). Fallback parts through sw01 also ordered. |
| N8 | Who supplies the optics for the C9500X-28C8D ports? | Lab network team | | **We do (2026-11-04)**, both ends. Type depends on N3. |
| N9 | 100G or 10G between the C9500X-28C8D and our switch? | Lab network team | | **100G allowed (2026-11-04).** Plan: 2 x 100G LACP. |
| N10 | Must the optics in the C9500X-28C8D be Cisco-branded, or are Cisco-compatible third-party optics allowed? Which IOS-XE version does it run? | Lab network team | Cisco-branded | **Version answered 2026-11-05:** IOS XE **17.15.06**. The lab runs the second-latest Cisco MD (maintenance deployment) release, so it will move up over time: check the optics against 17.15 and the next MD train. **Brand: our choice, decided 2026-11-05: Cisco-branded** in the C9500X-28C8D. **2026-11-06:** 17.15.06 is the C9500X. We now connect to an N93180YC-FX3 (NX-OS); brand and version re-asked (N13). **2026-11-06 (later):** back to the C9500X-28C8D, IOS XE 17.15.06, Cisco-branded optics. Matrix checked ([03](03-network-and-switch-capacity.md), section 3). |
| N11 | What do they call our racks (which RHINO)? Which N93180YC-FX3 serves them, and how far away is it? | Lab network team | | Asked 2026-11-06 (round 3, Q1). Sets cord length. **Closed 2026-11-06:** not needed; direct to the C9500X-28C8D. |
| N12 | May our switch (sw01) connect to the N93180YC-FX3, or must the servers plug in directly? | Lab network team | Our switch, as in [03](03-network-and-switch-capacity.md) | Asked 2026-11-06 (round 3, Q2). If direct: 8 x 25G SFP28 from them, and we drop sw01 (item 4). **Closed 2026-11-06:** our switch connects directly to the C9500X-28C8D. |
| N13 | 2 x 100G QSFP28 or 2 x 25G SFP28? Direct cord or panel? Single-mode or multimode, LC? Cisco optics required? NX-OS version? | Lab network team | 2 x 25G SFP28, Cisco optics | Asked 2026-11-06 (round 3, Q3-Q4). Decides items 6a-6d. **Closed 2026-11-06:** 2 x 100G, FR single-mode LC, Cisco optics, IOS XE 17.15.06. |
| N14 | **Deferred until after the order:** single switch or vPC pair, LACP/vPC, cable route and who runs it, L2 trunk or routed, VLAN IDs and subnets, 802.1X/NAC, port security, MTU | Lab network team | L2 trunk, LACP, lab gateway | Not needed for purchasing. Ask after the order. |
| N15 | Is the lab network team comfortable with our top-of-rack switch being a Cisco Nexus N93180YC-FX3 (their own access model), using two of its six 100G QSFP28 ports to the C9500X-28C8D? | Lab network team | Yes | Asked 2026-11-06 ([10](10-lab-network-team-email.md), last section). The engineer noted it is "rated for 25G": true for its 48 server ports; its 6 uplink ports are 40/100G. |

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
| V4 | Rail kits fit a VR3300 (square holes, 1200 mm deep, rails 29 in apart and adjustable)? | Thinkmate, Cisco (sw01) | Yes | |
