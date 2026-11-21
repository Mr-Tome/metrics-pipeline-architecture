# Metrics Analysis Pipeline: hardware and SI bring-up

Hardware, facility, and delivery plan for the GPU servers behind the metrics analysis pipeline. Phase 1
gives analysts SI through a chat page in their browser (language model, gateway, chat page, speech-to-text,
document upload). Access from Jupyter, VS Code, and MATLAB is a later phase, and the rest of the pipeline
follows on the same platform.

- **Budget:** $250,000.00. The 50-user build (one GPU server with 4 GPUs, no staging) plus the install items comes to $238,517 at CDW prices, with $11,483 left for the switch license and contingency ([Budget and BOM](docs/hardware/1-budget-and-bom.md)).
- **Site:** existing Vertiv racks (empty, next to ACE 15) with Liebert CRV in-row cooling.
  Our switch, a Cisco Nexus N93180YC-FX3, connects directly to the lab's C9500X-28C8D: 2 x 100G for data,
  plus a separate 10G link from our management switch ([Network and switch capacity](docs/hardware/3-network-and-switch-capacity.md), section 3).

## Start here

The work is split into three tracks, each in its own folder. **Open the README in your track's folder first.**
It lists that track's documents in reading order, what each one gives you, and its status. Documents that
have already been sent or submitted are kept separately as records.

| Track | Start with | Concern | Audience |
|---|---|---|---|
| Hardware | [`docs/hardware/README.md`](docs/hardware/README.md) | Facility, power, cooling, network, rack, purchasing | Lab facilities, lab network team, vendors, purchasing, installers |
| Software | [`docs/software/README.md`](docs/software/README.md) | Building, moving, and installing the SI service ([`delivery/`](delivery)) | Us, the installers, Lab IT |
| Cyber Security | [`docs/cyber/README.md`](docs/cyber/README.md) | What comes into the lab, and every decision the ISSM and Cyber must make | ISSM, Cyber Security, program approval |

A track that depends on another links to it instead of repeating it.

**Where things stand (2026-11-21):** both quote requests are submitted, the facility requirements are sent to
the lab, and the first ISSM email went out with the phase 1 software list. Training for installers:
[Rack 1 install sim](training/rack1-install-sim.html), then [SI bring-up sim](training/si-bringup-sim.html).

### Cyber Security documents

The cyber documents keep their numbers because the ISSM already has files that use them.

| # | Document | For | Status |
|---|---|---|---|
| | [Cyber Security package](docs/cyber/README.md) | **Start here for Cyber.** What is in the package, and the decision register: every question for the ISSM and Cyber (S, L1), with what each answer affects (hardware, software, models, process) | Draft, 2026-11-13 |
| 12 | [Software BOM](docs/cyber/12-software-bom.md) ([CSV](docs/cyber/12-software-bom.csv)) | Every software item phase 1 brings in, including the alternatives still being chosen: version, source, license, how it arrives | Draft, versions checked 2026-11-09 |
| 13 | [Model BOM](docs/cyber/13-model-bom.md) | Every model and model data file, including alternatives: publisher, commit, license, format, size, how it is checked, and the models inside container images | Draft |
| 14 | [Key and certificate inventory](docs/cyber/14-key-and-certificate-inventory.md) | Every key, password, token, and certificate: what it protects, who creates and holds it, expiry, what to do if it leaks | Draft, 2026-11-13 |
| 15 | [Security review](docs/cyber/15-security-review.md) | Our own review of the plan before the ISSM meeting: 33 findings with fixes, and what to bring to the meeting | Draft, 2026-11-13 |
| 16 | [Phased software list](docs/cyber/16-phased-sbom.md) ([CSV](docs/cyber/16-phased-sbom.csv)) | Everything by phase, with download links, for the ISSM | Phase 1 sent to the ISSM; later phases draft |
| 17 | [First email to the ISSM](docs/cyber/17-issm-intro-email.md) | Introduction, quick questions, then detailed questions | Sent with the phase 1 list |

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
metrics_architecture.html                      full pipeline architecture, and the chat feature deployment (interactive)
program_views.html                             phases, security, delivery, keys, review (interactive, generated)
docs/hardware/                                 hardware track (README = reading order; records/ = sent or submitted)
docs/software/                                 software track (README = reading order)
docs/cyber/                                    Cyber Security package: BOMs and decision register
docs/diagrams/                                 diagrams (shared)
training/                                      rack1-install-sim.html and si-bringup-sim.html, interactive practice
delivery/                                      scripts that build the release bundle (connected side)
delivery/intake/                               scripts that verify and install it (rehearsal VM and lab)
validate/                                      hardware, network, and load checks
```

## Lab request

The lab's original request, which this repository answers (see [Facility requirements](docs/hardware/2-facility-requirements.md)):

> Get your technical specs, part numbers. Model numbers, etc ASAP.
>
> Don't ask us if our facility power is sufficient. The answer is yes it is. Get us your power needs. ASAP.
> Voltage, current, power, phase, frequency. Connector type(s).
> Anything unique that is not standard? Get it to us.
>
> Cooling. Again, you tell us what is needed. We are not mind readers. Normal cooled air cooling.
