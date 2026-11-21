# Hardware track: start here

Facility, power, cooling, network, rack, and purchasing for the GPU servers behind the SI service. Security
decisions that affect the hardware (for example S1, S2, S4, S8) are in the [Cyber Security package](../cyber/README.md).

The numbered documents are in reading order. Read them top to bottom the first time; after that, go straight
to the one you need.

## Read in this order

| Step | Document | What you get from it | Status |
|---|---|---|---|
| 1 | [Budget and BOM](1-budget-and-bom.md) | What we are buying, why the 50-user size, what the BOM leaves out, how it fits $250k. The workbook is [`Metrics_Analysis_Pipeline_Hardware_BOM.xlsx`](../../Metrics_Analysis_Pipeline_Hardware_BOM.xlsx). | Ready |
| 2 | [Facility requirements](2-facility-requirements.md) | Power, cooling, connectors, space, and network ports the rack needs from the lab | Sent to the lab. Any change has to be re-sent to facilities. |
| 3 | [Network and switch capacity](3-network-and-switch-capacity.md) | How the rack connects to the lab: Cisco Nexus sw01, 2 x 100G data and a separate 10G management link to the C9500X-28C8D | Decided |
| 4 | [Site visit checklist](4-site-visit-checklist.md) | What visit 1 found, and what to look at and ask on the next visit | Ready for the next visit |
| 5 | [Rack build guide](5-rack-build-guide.md) | Install day, step by step: delivery check, rack prep, power, cabling, first checks, sign-off | Ready |
| Practice | [Rack 1 install sim](../../training/rack1-install-sim.html) | Interactive run of step 5. Open it in a browser; it works offline. | Ready |

## Keep open while you work

| Document | What it is | Status |
|---|---|---|
| [Open questions](open-questions.md) | Facility (F), network (N), and vendor (V) questions still open, each with an owner and the default we use until it is answered | Living |
| [Decision log](decision-log.md) | Each hardware decision with the real options we weighed, what we picked, and why | Living |

## Records

Documents that have been sent or submitted. They are kept as the record of what went out. Don't edit them
and don't resend them; if something changes, write a new message and record it here.

| Record | What went out | Status |
|---|---|---|
| [Servers quote](records/quote-servers-and-gpus.md) | Quote request for the GPU server, GPUs, and service nodes | Submitted 2026-11-04 |
| [Network and rack quote](records/quote-network-and-rack.md) | Quote request for the switch, optics, cords, rack items, and setup kit | Submitted |
| [Network team Q&A](records/lab-network-team-qa.md) | Each round of questions to the lab network team, their answers, and what we did | Closed for purchasing. Nexus note sent; answer pending (open questions, N15). |

## Diagrams

[Rack elevation](../diagrams/rack-elevation.svg) · [Power wiring](../diagrams/power-wiring.svg) · [Network cabling](../diagrams/network-cabling.svg)
