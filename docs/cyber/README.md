# Cyber Security review package

**Track:** Cyber Security. This folder is the one place for everything the ISSM and the Cyber Security team are
asked to review or decide. Hardware, facility, and network work is in [`../hardware/`](../hardware/), and building
and installing the software is in [`../software/`](../software/). Those folders link here when they depend on a
security decision. Security decisions are not tracked anywhere else.

**Status:** Draft, 2026-11-14. First provision.

**Phase 1 scope:** analysts use SI through the chat page in a browser. There is no API address for their own
tools and no analyst API keys. Jupyter, VS Code, and MATLAB access is a later phase; items that only apply to it
are marked "later phase".

## How to read this package

We are listing **everything we want to bring into the lab, including the alternatives we are still choosing
between**, with the facts Cyber needs to judge each one. Cyber decides what is allowed. Where we have a
recommendation or a proposed control, we say so, but we have not left anything off the list because we expected
it to be refused.

| Document | What it covers |
|---|---|
| [12 Software BOM](12-software-bom.md) ([CSV](12-software-bom.csv)) | Every piece of software: version, supplier, license, how it arrives, outbound connections and how they are switched off |
| [13 Model BOM](13-model-bom.md) | Every model and model data file: publisher, country of origin, commit, license, file format, size, how it is checked, and the models that ride inside container images |
| [14 Key and certificate inventory](14-key-and-certificate-inventory.md) | Every key, password, token, and certificate: what it protects, who creates and holds it, when it expires, what to do if it leaks |
| [15 Security review](15-security-review.md) | Our own review of the plan before meeting the ISSM: 33 findings, each with how it could be misused, the fix, and when |
| Decision register (below) | Every question for the ISSM and Cyber, and what each answer affects |
| Not yet covered (below) | Content that is not software, a model, or a key |

## Decision register

**Affects** says which part of the work waits on the answer: **HW** (hardware purchase or install),
**SW** (software build and install), **Models**, or **Process** (how releases move and are signed). **Whose call**
says who decides: the ISSM or Cyber, the program, or us (listed so Cyber can approve either option).

### Lab entry, accreditation, and process

| ID | Decision needed | Affects | Whose call | Default if no answer | Answer |
|---|---|---|---|---|---|
| S1 | What is the approved process to bring hardware in? | HW | ISSM | | |
| S2 | May new lab hardware be burned in on the unclassified side before it enters (then wiped)? | HW | ISSM | No; burn in inside the lab | |
| S3 | Approved transfer media type, and how long a transfer takes | Process | ISSM | Encrypted SSD, 1 week turnaround | |
| S4 | Is Secure Boot required on servers? It changes how the NVIDIA driver is installed: the kernel module must be signed with a key enrolled on each server. | HW, SW | ISSM | Off | |
| S6 | Are upstream (non-Iron Bank) container images allowed in the lab for phase 1? Iron Bank images can be swapped in where they exist without changing the scripts. | SW | ISSM | Iron Bank where available, upstream otherwise | |
| S7 | Where may the staging server live? | HW | Program | | No staging server (decided 2026-10-30). The build workstation rehearses each bundle; see [04](../software/04-prototype-plan.md). |
| S8 | First switch setup needs a serial console. **Our plan, no laptop:** the rack console (con01, StarTech RKCONS1701, a 17-inch screen and keyboard drawer) plugs into svc01 over VGA and USB. A USB-to-RJ45 console cable (in the setup kit) runs from svc01 to the switch's console port, and the switch is set up from a terminal on svc01. May we connect that USB serial cable to svc01? | HW | ISSM | Yes | |
| L1 | Does accreditation require a specific server OS (for example RHEL 9 with STIG)? Is there a package mirror? Asked in the quote email ([08a](../hardware/08a-quote-servers-submitted.md), question 6). | HW, SW | ISSM, Lab IT | Rocky Linux 9 (free); RHEL 9 if required, at about $1,400 per server per year | Our choice unless accreditation says otherwise. The NVIDIA driver is built against the OS kernel, and RHEL needs paid subscriptions (not in the hardware budget). |
| S10 | Bundle signing: cosign or GPG, who holds the signing key, and how the public key reaches the lab ([11](../software/11-sandbox-bringup-plan.md), W5) | Process | ISSM | GPG (the OS already has `gpg`; `cosign` is not in the lab today and would have to be added) | |
| S11 | OS packages the driver build needs: gcc, kernel-devel, dkms (from EPEL, not base Rocky/RHEL), SELinux policy packages ([11](../software/11-sandbox-bringup-plan.md), W3) | SW | ISSM, Lab IT | Lab mirror with EPEL allowed; otherwise we add these RPMs to the bundle | |

### Software ([12](12-software-bom.md))

| ID | Decision needed | Affects | Whose call | Our recommendation | Answer |
|---|---|---|---|---|---|
| S12 | Speech-to-text. faster-whisper itself is maintained and its file format can't run code, so it is not the problem. The problem is the server around it. Options: **(a)** speaches (A4): no stable release since 2025-09-19. **(b)** whisper-asr-webservice (MIT, v1.10.0 in August 2026, runs faster-whisper): maintained, but its API isn't the OpenAI one, so the gateway and chat page can't call it without an adapter. **(c)** Our own small server: about 100 lines of Python around faster-whisper, with the OpenAI API, built into an image on the build side. Fully reviewable; we own its upkeep. **(d)** vLLM serving Whisper (M5 or M6): no new component, but no silence filtering. | SW, Models | Us (open); Cyber approves | Leaning faster-whisper. If so, (c) with weights we convert ourselves from OpenAI's files (S22). | |
| S13 | Chat page image, two options, both listed: **(a)** the standard Open WebUI image, or **(b)** the `slim` image ([13](13-model-bom.md), section 2). | SW, Models | Us (open); Cyber approves either | Open | |
| S14 | Licenses to note: NVIDIA's proprietary user-space driver and the CUDA EULA (G1, A1), Open WebUI's branding clause (A3), LiteLLM's `enterprise/` code present but unused (A2), gpt-oss usage policy (M1) | SW, Models | Legal or program, if required | | |
| S15 | `rke2-security-responder` ships with RKE2 and appears to report the cluster version to SUSE. What it contacts, and whether we turn it off. | SW | Us, for Cyber's information | Turn it off if it calls out. The sandbox network tripwire will show whether it tries. | |
| S16 | Known security shortcuts already tracked: no network policies yet (W8), local accounts and API keys until single sign-on (W9), what the audit log records (W10), no CIS hardening profile yet (W11) | SW | Cyber | See [11](../software/11-sandbox-bringup-plan.md), section 7 | |
| S17 | **For information.** Ingress is Traefik (K4), which ships inside RKE2. ingress-nginx was retired upstream in March 2026 and removed from RKE2 1.37. | SW | | No new supplier | |
| S18 | **For information.** NVIDIA driver branch: we plan R620 (long-term support to September 2029). Until a GPU Operator release lists R620, the pin stays on R580 (long-term support to June 2028). | SW | Us | R620 | |
| S19 | **For information.** First full scan results come with the first real pull. `SUMMARY.txt` goes to Cyber before the bundle is sealed. | SW | | | |

### Keys, accounts, and data ([14](14-key-and-certificate-inventory.md), [15](15-security-review.md))

| ID | Decision needed | Affects | Whose call | Our proposal | Answer |
|---|---|---|---|---|---|
| S23 | How long keys last (gateway master key, chat page's gateway key, TLS certificate), and, for the later analyst-tools phase, how user API keys are handed out | Process | ISSM | Master and chat page keys 6 months, TLS per lab CA. Later phase: user keys in person or approved secure messaging, 90 days. | |
| S24 | Who may hold cluster admin (root on svc01-03). Root there can read every secret, every chat, and every log. | Process | ISSM, Program | Two named admins. Later, personal accounts through single sign-on. | |
| S25 | Must data on the server disks be encrypted at rest (chat history, uploads, databases, models)? | HW, SW | ISSM | Encrypted data disks if required. Decide before install: it is hard to add later. | |
| S26 | What the audit log must contain (prompts and responses?), how long it is kept, and where it goes so admins can't change it (W10) | SW | ISSM | Prompts and responses kept; retention per lab policy; copy to the lab's log service if there is one | |

### Models ([13](13-model-bom.md))

| ID | Decision needed | Affects | Whose call | Our recommendation | Answer |
|---|---|---|---|---|---|
| S5 | Is there an approved model list? Approve each requested model in [13](13-model-bom.md), sections 1 and 3: gpt-oss-120b, the speech models, the embedding models, the reranker. All must also meet the USA-only rule (S22). | Models | Program, ISSM | | |
| S20 | **Which model file formats are allowed.** See [13](13-model-bom.md), section 4 for why the line matters. Options: **(a)** formats that cannot run code when loaded (safetensors, CTranslate2), **(b)** safetensors only, **(c)** also pickle-format files, with scanning and restricted loading. | Models | ISSM | (a). The line that matters is whether loading a file can run code, not the file extension. | |
| S21 | Controls for model files: refuse `.py` files at pull, and scan container images for model files that bypass the model intake | Models | Cyber | Add both | |
| S22 | **Program rule (2026-11-13): models must be made in the USA.** Does the rule cover only the publisher, or the whole lineage (the base model and who converted it)? It changes M2, M3, and the chat page image ([13](13-model-bom.md), section 1a). | Models | Program, ISSM | Whole lineage (the stricter reading) | Rule decided; scope open |
| S9 | Future phase: may a typed decision model (Cloudflare Clef, Qwen3.8-27B base, Apache 2.0) run in the lab? It ships a Python code file that runs at load time, and it needs its own model server (SGLang) and gateway route. | Models, SW | ISSM, Program | Deferred; not in phase 1 | Deferred 2026-10-30. Also ruled out by the USA-only rule (S22): its base model, Qwen, is from Alibaba (China). |

IDs are never reused. L5 (internet access) was removed on 2026-11-14: the lab has no internet, so it is not a question. S1 to S9, L1, and L5 came from the old open-questions list (doc 07), which now holds only
hardware questions ([hardware/07](../hardware/07-open-questions.md)) and Lab IT software questions
([software/07](../software/07-open-questions.md)).

## Not yet covered: content that is not software, a model, or a key

| Content | Examples | Plan |
|---|---|---|
| **Keys and certificates** | Signing keys, CA, TLS, gateway keys, cluster credentials | Done: [14](14-key-and-certificate-inventory.md) |
| **Configuration** | Chart values, Kubernetes manifests, RKE2 config, the Zarf package definition | Ours are in this repository at the commit in each bundle's `SOURCE_COMMIT`. Settings made in the lab after install (chat page admin settings, gateway keys) are not recorded yet. |
| **Data files** | Trivy vulnerability databases, LiteLLM price list, tokenizer vocabularies | Listed in 12 and 13 |
| **Firmware** | BIOS, BMC, NIC, NVMe, GPU VBIOS, NX-OS | Listed in 12 (H1 to H4); versions recorded at the delivery check |
| **License and entitlement files** | NX-OS Essentials license, RHEL subscriptions if used | To list with the firmware |
| **Documents and training pages** | This repository's documents, the two training pages (HTML with JavaScript), vendor manuals | Decision needed: do they go into the lab at all? |
| **Test data** | Smoke-test audio and PDF files, load-test prompts, later the metrics pipeline's sample data | A dataset list when the pipeline arrives |
| **Data created in the lab** | Chat history, uploaded documents, document vectors, gateway logs | Not a BOM item. Cyber will want storage and retention rules ([11](../software/11-sandbox-bringup-plan.md), W10, W13). |
