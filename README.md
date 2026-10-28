# Metrics Analysis Pipeline: hardware and AI bring-up

Hardware, facility, and delivery plan for the GPU servers behind the metrics analysis pipeline. The first
goal is getting the AI service (language model, gateway, chat page, and access from Jupyter, VS Code,
and MATLAB) running in the lab. The rest of the pipeline follows on the same platform.

- **Budget:** $250,000.00. The 20-user build plus the install items fits with 7% contingency ([02](docs/02-budget-and-bom.md)).
- **Site:** existing Vertiv racks (empty) with Liebert CRV in-row cooling; Cisco C9300 access and C9500X core.

## Start here

| # | Document | For | Status |
|---|---|---|---|
| 01 | [Facility requirements](docs/01-facility-requirements.md) | **Send to the lab now.** Power, cooling, connectors, space, network ports. | Ready to send |
| 02 | [Budget and BOM](docs/02-budget-and-bom.md) | Which tier fits $250k, what the BOM leaves out, corrections | Ready |
| 03 | [Network and switch capacity](docs/03-network-and-switch-capacity.md) | Is 10G enough, how our rack connects, what to ask the network team | Ready |
| 04 | [Prototype plan](docs/04-prototype-plan.md) | Unclassified prototype that becomes staging, then the lab install | Ready |
| 05 | [Rack build guide](docs/05-rack-build-guide.md) | Step-by-step install, cable schedule, wiring diagrams, vendor guides | Ready |
| 06 | [Software delivery](docs/06-software-delivery.md) | Pull scripts, release bundle, install, connecting users | Ready, versions to bump |
| 07 | [Open questions](docs/07-open-questions.md) | Everything still to confirm, with owners and defaults | Living |

## Diagrams

| | |
|---|---|
| [Rack elevation](docs/diagrams/rack-elevation.svg) | [Power wiring](docs/diagrams/power-wiring.svg) |
| [Network cabling](docs/diagrams/network-cabling.svg) | [Prototype topology](docs/diagrams/prototype-topology.svg) |

To change a diagram, edit `docs/diagrams/make_diagrams.py` and run `python3 docs/diagrams/make_diagrams.py docs/diagrams`.

## Repository layout

```
README.md                                      this page
Metrics_Analysis_Pipeline_Hardware_BOM.xlsx    hardware BOM (Summary, BOM, Assumptions, Software tabs)
metrics_architecture.html                      full pipeline architecture (interactive)
docs/                                          numbered documents above, diagrams/
delivery/                                      scripts that build the release bundle (connected side)
delivery/intake/                               scripts that verify and install it (staging and lab)
validate/                                      hardware, network, and load checks
```

## Lab request

The lab's original request, which this repository answers (see [01](docs/01-facility-requirements.md)):

> Get your technical specs, part numbers. Model numbers, etc ASAP.
>
> Don't ask us if our facility power is sufficient. The answer is yes it is. Get us your power needs. ASAP.
> Voltage, current, power, phase, frequency. Connector type(s).
> Anything unique that is not standard? Get it to us.
>
> Cooling. Again, you tell us what is needed. We are not mind readers. Normal cooled air cooling.
