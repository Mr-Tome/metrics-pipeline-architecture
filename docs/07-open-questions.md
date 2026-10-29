# 07. Open questions

Questions that block or change the plan. Each has an owner and a default. If the question is not
answered, the plan proceeds with the default. Update the Answer column as answers come in.

## Facility (F)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| F1 | The model number given, CR035RA1A7X..., decodes to a **Liebert CRV in-row cooling unit** (35 kW, air cooled), not aisle containment or a rack. What we need from the rack: depth between rails, hole type, existing PDUs. The model label is a shortcut to those. | Site visit ([09](09-site-visit-checklist.md)) | Assume Vertiv VR, 42U, 600 mm wide, 1100 mm deep, square holes | |
| F2 | Are the 96 racks all the same model, and which position will we get? | Facilities | One rack in a contained row with a CRV | Same model, all empty, any position. Rows of 8, two rows joined with glass doors (aisle containment). Ask for: one rack near a CRV, the next rack held for growth. Confirm hot or cold aisle containment. |
| F3 | Can you provide 2 x 208V 3-phase WYE 30A circuits on NEMA L21-30R per rack, from separate A and B sources? | Facilities | Yes (README says power is sufficient) | |
| F4 | Is facility ground available at the rack? | Facilities | Yes | |
| F5 | Any rule on rack PDU brand or model (some sites standardize on one)? | Facilities | Vertiv Geist, to match the racks | |

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

## Lab IT (L)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| L1 | Does the lab's accreditation require a specific server OS (for example RHEL 9 with STIG)? Is there a package mirror? | Lab IT, ISSM | RHEL 9 | Our choice unless accreditation says otherwise. It matters for two reasons: the NVIDIA driver is built against the OS kernel, so the driver package must match it; and RHEL needs paid subscriptions (not in the BOM), while Rocky Linux 9 is free and compatible. |
| L2 | Does the lab already run Kubernetes? | Lab IT | | No. We bring our own (RKE2). |
| L3 | Python versions on analyst machines, and Windows or Linux? | Lab IT | | Many versions, mostly Windows, some Linux. Client packages must cover Python 3.9 to 3.13 on both. |
| L5 | Internet access during the initial build and debug? | ISSM | No. All software arrives on transfer media. | |
| L4 | Is MATLAB allowed to make HTTPS calls to an internal service? | Lab IT | Yes | |

## Vendor (V)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| V1 | GPU server PSU inlet type (C14 or C20) | Thinkmate | C20 | 4 x 2000 W (Thinkmate page). Inlet still open. |
| V2 | Does the quote include a dual-port 25GbE NIC that does not take a GPU slot? | Thinkmate | Add an OCP 3.0 2 x 25G NIC | |
| V3 | Lead time for the GPUs | Thinkmate, CDW | 4 to 8 weeks | |
| V4 | Rail kit fits a square-hole rack 1100 mm deep? | Thinkmate | Yes | |
