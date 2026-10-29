# 07. Open questions

Questions that block or change the plan. Each has an owner and a default. If the question is not
answered, the plan proceeds with the default. Update the Answer column as answers come in.

## Facility (F)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| F1 | Rack model, depth, hole type | Site visit | | Vertiv VR3300, 42U, 600 x 1200 mm, square holes, rails adjustable (29 in apart now). The CR035RA1A7X is the Liebert CRV in-row cooler. |
| F2 | Which racks will we get? | Facilities | | Two racks next to ACE 15: rack 1 now, rack 2 held for growth. Hot aisle containment (glass closes off the rear). |
| F3 | Are the existing left and right Geist PDUs fed from separate sources (A and B)? What is each PDU's input rating? | Facilities | Separate sources, each able to carry 3.6 kW | PDUs present: circuits 1-3 each, mostly C13, one C19 per circuit, 208V. Not marked A or B. Source and rating open. |
| F4 | Is the rack frame bonded to facility ground? | Facilities | Yes | Door bonding straps seen; frame bond not seen. Open. |
| F5 | Rack PDU brand | Facilities | | Vertiv Geist, already installed. Nothing to buy. |

## Network (N)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| N1 | Exact access switch model | Lab network team | | C9300-48S (confirmed). One in the analysts' building, one in the rack building, both uplinked to the C9500X. |
| N2 | May our switch connect directly to the C9500X core, or only to the C9300-48S in the rack building? Free 10G ports on that C9300-48S? (The network team runs `show interfaces status`; we have no access to their switches.) | Lab network team | Through the C9300-48S, 2 x 10G (option B, quote item 9) | Likely not direct to the core. Open. |
| N3 | Fiber type between that switch and our rack: multimode or single-mode, LC or MPO? | Lab network team | OM4 multimode, LC | |
| N4 | Load on the existing 10G links between the C9300s and the core | Lab network team | Under 50% | Low priority. Our racks are empty, but these links already carry other traffic. Ask only if we connect through them. |
| N5 | IP subnets for servers (/27) and BMC (/28), plus DNS names for the chat and API endpoints | Lab network team | Assigned at install | Not needed for purchasing. Ask after the order. |
| N6 | DNS, NTP, and the internal CA (for the HTTPS certificate) | Lab network team | Lab provides all three | Not needed for purchasing. Ask after the order. |
| N7 | Where does the management switch uplink go? | Lab network team | Lab management VLAN | Not needed for purchasing. Ask after the order. |

## Security (S)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| S1 | Is the lab classified? What is the approved process to bring hardware in? | ISSM | Classified; hardware one way only | |
| S2 | May new lab hardware be burned in on the unclassified side before it enters (then wiped)? | ISSM | No; burn in inside the lab | |
| S3 | Approved transfer media type, and how long a transfer takes | ISSM | Encrypted SSD, 1 week turnaround | |
| S4 | Is Secure Boot required on servers? (It changes how the NVIDIA driver is installed.) | ISSM | Off | |
| S5 | Is there an approved model list? Is gpt-oss-120b (Apache 2.0) acceptable? | Program | Yes, pending approval | |
| S6 | Are upstream (non-Iron Bank) images allowed in staging and the lab for phase 1? | ISSM | Allowed in staging; Iron Bank where available for the lab | |
| S7 | Where may the staging server live, and may it have internet access? | ISSM | Unclassified side, with internet | |
| S8 | Is a laptop allowed in the room for first switch setup over a console cable? | ISSM | No; use the lab's approved device | |

## Lab IT (L)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| L1 | Does the lab's accreditation require a specific server OS (for example RHEL 9 with STIG)? Is there a package mirror? Asked in the quote email ([08](08-quote-request-email.md), question 6). | Lab IT, ISSM | Rocky Linux 9 (free); RHEL 9 if required, at about $1,400 per server per year | Our choice unless accreditation says otherwise. It matters for two reasons: the NVIDIA driver is built against the OS kernel, so the driver package must match it; and RHEL needs paid subscriptions (not in the BOM), while Rocky Linux 9 is free and compatible. |
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
