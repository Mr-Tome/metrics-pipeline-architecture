# 07. Open questions

Questions that block or change the plan. Each has an owner and a default. If the question is not
answered, the plan proceeds with the default. Update the Answer column as answers come in.

## Facility (F)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| F1 | The model number given, CR035RA1A7X..., decodes to a **Liebert CRV in-row cooling unit** (35 kW, air cooled), not aisle containment or a rack. What are the **rack** model numbers? (Label on the rear door or frame, starts with VR.) | Facilities | Assume Vertiv VR, 42U, 600 mm wide, 1100 mm deep | |
| F2 | Are the 96 racks all the same model, and which row and rack position will we get? Is that row served by a CRV and inside the containment? | Facilities | One rack in a contained row with a CRV | |
| F3 | Can you provide 2 x 208V 3-phase WYE 30A circuits on NEMA L21-30R per rack, from separate A and B sources? | Facilities | Yes (README says power is sufficient) | |
| F4 | Is facility ground available at the rack? | Facilities | Yes | |
| F5 | Any rule on rack PDU brand or model (some sites standardize on one)? | Facilities | Vertiv Geist, to match the racks | |

## Network (N)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| N1 | Exact access switch model: "C9300-485" is probably C9300-48S. Please send `show inventory` from each switch. | Lab network team | C9300-48S with an 8 x 10G network module | |
| N2 | Exact core model and two free 100G QSFP28 ports? (`show interfaces status`) | Lab network team | C9500X-28C8D, ports available, so option A | |
| N3 | Fiber type in the plant: multimode OM4 (MPO or LC) or single-mode? | Lab network team | OM4 MPO, 100G-SR4 | |
| N4 | Are the existing 10G links between access and core in a port-channel? What is their busy-hour 5-minute rate? | Lab network team | Bonded, under 50% | |
| N5 | IP subnets for servers (/27) and BMC (/28), plus DNS names for the chat and API endpoints | Lab network team | Assigned at install | |
| N6 | DNS, NTP, and the internal CA (for the HTTPS certificate) | Lab network team | Lab provides all three | |
| N7 | Where does the out-of-band management switch uplink go? | Lab network team | Lab management VLAN | |

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
| L1 | Server OS and version (RHEL 9? Rocky? Ubuntu?) and whether a local package mirror exists | Lab IT | RHEL 9 with a lab mirror | |
| L2 | Does the lab already run Kubernetes? (BOM: "RKE2 or the lab's existing Kubernetes") | Lab IT | No; we bring RKE2 | |
| L3 | Python version on analyst machines, and Windows or Linux? | Lab IT | Python 3.11, both | |
| L4 | Is MATLAB allowed to make HTTPS calls to an internal service? | Lab IT | Yes | |

## Vendor (V)

| ID | Question | Ask | Default if no answer | Answer |
|---|---|---|---|---|
| V1 | GPU server PSU wattage, count, and inlet type (C14 or C20) | Thinkmate | 4 x 2000 W+, C20 | |
| V2 | Does the quote include a dual-port 25GbE NIC that does not take a GPU slot? | Thinkmate | Add an OCP 3.0 2 x 25G NIC | |
| V3 | Lead time for the GPUs | Thinkmate, CDW | 4 to 8 weeks | |
| V4 | Rail kit fits a square-hole rack 1100 mm deep? | Thinkmate | Yes | |
