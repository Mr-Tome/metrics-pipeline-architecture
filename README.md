# Metrics Analysis Pipeline: hardware and SI bring-up

Hardware, facility, and delivery plan for the GPU servers behind the metrics analysis pipeline. The first
goal is getting the SI service (language model, gateway, chat page, and access from Jupyter, VS Code,
and MATLAB) running in the lab. The rest of the pipeline follows on the same platform.

- **Budget:** $250,000.00. The 50-user build (one GPU server with 4 GPUs, no staging) plus the install items comes to $238,517 at CDW prices, with $11,483 left for the switch license and contingency ([02](docs/hardware/02-budget-and-bom.md)).
- **Site:** existing Vertiv racks (empty, next to ACE 15) with Liebert CRV in-row cooling.
  Our switch, a Cisco Nexus N93180YC-FX3, connects directly to the lab's C9500X-28C8D: 2 x 100G for data,
  plus a separate 10G link from our management switch ([03](docs/hardware/03-network-and-switch-capacity.md), section 3).

## Start here

The work is split into three tracks. Each document belongs to one of them, and each track has its own folder.
A track that depends on another links to it instead of repeating it.

| Track | Folder | Concern | Audience |
|---|---|---|---|
| Hardware | [`docs/hardware/`](docs/hardware/) | Facility, power, cooling, network, rack, purchasing | Lab facilities, lab network team, vendors, purchasing |
| Software | [`docs/software/`](docs/software/), [`delivery/`](delivery/) | Building, moving, and installing the SI service | Us, the installers, Lab IT |
| Cyber Security | [`docs/cyber/`](docs/cyber/) | What comes into the lab, and every decision the ISSM and Cyber must make | ISSM, Cyber Security, program approval |

### Hardware

| # | Document | For | Status |
|---|---|---|---|
| 01 | [Facility requirements](docs/hardware/01-facility-requirements.md) | **Send to the lab now.** Power, cooling, connectors, space, network ports. | Ready to send |
| 02 | [Budget and BOM](docs/hardware/02-budget-and-bom.md) | Which tier fits $250k, what the BOM leaves out, corrections | Ready |
| 03 | [Network and switch capacity](docs/hardware/03-network-and-switch-capacity.md) | Is 10G enough, how our rack connects, what to ask the network team | Decided: Cisco Nexus sw01, 2 x 100G data + 10G management to the C9500X-28C8D |
| 05 | [Rack build guide](docs/hardware/05-rack-build-guide.md) | Step-by-step install, cable schedule, wiring diagrams, vendor guides | Ready |
| 08a | [Quote request: servers and GPUs](docs/hardware/08a-quote-servers-submitted.md) | Items 1-3 and the vendor questions for them | Submitted 2026-11-04 |
| 08b | [Quote request: network, rack, setup](docs/hardware/08b-quote-network-and-rack.md) | **Send to purchasing.** Switch, cables, optics, rack items | Ready to send |
| 09 | [Site visit checklist](docs/hardware/09-site-visit-checklist.md) | What to look at and ask in the server room | Ready |
| 10 | [Email to the lab network team](docs/hardware/10-lab-network-team-email.md) | Lab network team emails and answers. **Send the short Nexus note** (last section) | Note ready to send |
| 07 | [Open questions: hardware](docs/hardware/07-open-questions.md) | Facility (F), network (N), and vendor (V) questions, with owners and defaults | Living |
| | [Rack 1 install sim](training/rack1-install-sim.html) | **Installers.** Interactive practice run of doc 05: delivery check to sign-off. Open in a browser, works offline. | Ready |

### Software

| # | Document | For | Status |
|---|---|---|---|
| 04 | [Prototype plan](docs/software/04-prototype-plan.md) | Lab rack as production from day 1, build without internet, rehearsing each release without a staging server | Ready |
| 06 | [Software delivery](docs/software/06-software-delivery.md) | Pull scripts, release bundle, install, connecting users | Ready, versions bumped 2026-11-09 (not yet rehearsed) |
| 11 | [Sandbox bring-up plan](docs/software/11-sandbox-bringup-plan.md) | Making the SI workbench start and work in an offline sandbox; what must be fixed before the air gap | Draft |
| 07 | [Open questions: Lab IT](docs/software/07-open-questions.md) | Lab IT questions about Kubernetes, Python, packages, MATLAB (L) | Living |
| | [SI bring-up sim](training/si-bringup-sim.html) | **Installers.** Continues from the rack sim: verify the bundle, build the cluster, deploy the SI service, issue keys, run the checks, connect analysts. Three random faults per run. Works offline. | Draft |

### Cyber Security

| # | Document | For | Status |
|---|---|---|---|
| | [Cyber Security package](docs/cyber/README.md) | **Start here for Cyber.** What is in the package, and the decision register: every question for the ISSM and Cyber (S, L1, L5), with what each answer affects (hardware, software, models, process) | Draft, 2026-11-11 |
| 12 | [Software BOM](docs/cyber/12-software-bom.md) ([CSV](docs/cyber/12-software-bom.csv)) | Every software item phase 1 brings in, including the alternatives still being chosen: version, source, license, how it arrives | Draft, versions checked 2026-11-09 |
| 13 | [Model BOM](docs/cyber/13-model-bom.md) | Every model and model data file, including alternatives: publisher, commit, license, format, size, how it is checked, and the models inside container images | Draft |

## Diagrams

| | |
|---|---|
| [Rack elevation](docs/diagrams/rack-elevation.svg) | [Power wiring](docs/diagrams/power-wiring.svg) |
| [Network cabling](docs/diagrams/network-cabling.svg) | [Software path](docs/diagrams/prototype-topology.svg) |

To change a diagram, edit `docs/diagrams/make_diagrams.py` and run `python3 docs/diagrams/make_diagrams.py docs/diagrams`.

## Repository layout

```
README.md                                      this page
Metrics_Analysis_Pipeline_Hardware_BOM.xlsx    hardware BOM (Summary, BOM, Assumptions, Software tabs)
metrics_architecture.html                      full pipeline architecture (interactive)
docs/hardware/                                 hardware track: facility, network, rack, quotes
docs/software/                                 software track: delivery plan, sandbox bring-up
docs/cyber/                                    Cyber Security package: BOMs and decision register
docs/diagrams/                                 diagrams (shared)
training/                                      rack1-install-sim.html and si-bringup-sim.html, interactive practice
delivery/                                      scripts that build the release bundle (connected side)
delivery/intake/                               scripts that verify and install it (rehearsal VM and lab)
validate/                                      hardware, network, and load checks
```

## Lab request

The lab's original request, which this repository answers (see [01](docs/hardware/01-facility-requirements.md)):

> Get your technical specs, part numbers. Model numbers, etc ASAP.
>
> Don't ask us if our facility power is sufficient. The answer is yes it is. Get us your power needs. ASAP.
> Voltage, current, power, phase, frequency. Connector type(s).
> Anything unique that is not standard? Get it to us.
>
> Cooling. Again, you tell us what is needed. We are not mind readers. Normal cooled air cooling.
