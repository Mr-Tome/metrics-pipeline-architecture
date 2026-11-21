# Software track: start here

Building, moving, and installing the SI service: the scripts in [`delivery/`](../../delivery) build the release
bundle on the connected build workstation, and the scripts in [`delivery/intake/`](../../delivery/intake) verify and
install it in the lab. What Cyber must approve is in the [Cyber Security package](../cyber/README.md).

The numbered documents are in reading order. Read them top to bottom the first time; after that, go straight
to the one you need.

## Read in this order

| Step | Document | What you get from it | Status |
|---|---|---|---|
| 1 | [Prototype plan](1-prototype-plan.md) | The approach: the lab rack is production from day 1, the build works without internet, and each release is rehearsed without a staging server | Ready |
| 2 | [Software delivery](2-software-delivery.md) | Pull scripts, the release bundle, install, and connecting users | Ready. Versions bumped 2026-11-09, not yet rehearsed. |
| 3 | [Sandbox bring-up plan](3-sandbox-bringup-plan.md) | Making the SI service start and work in an offline sandbox, and what must be fixed before the air gap | Draft |
| Practice | [SI bring-up sim](../../training/si-bringup-sim.html) | Continues from the rack sim: verify the bundle, build the cluster, deploy the SI service, issue keys, run the checks, connect analysts. Three random faults per run. Works offline. | Draft |

## Keep open while you work

| Document | What it is | Status |
|---|---|---|
| [Open questions](open-questions.md) | Lab IT questions about Kubernetes, Python, packages, and MATLAB (L) | Living |

## Diagrams

[Software path](../diagrams/prototype-topology.svg)
