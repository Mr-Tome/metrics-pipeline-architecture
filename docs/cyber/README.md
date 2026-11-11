# Cyber Security review package

**Track:** Cyber Security. This folder is the one place for everything the ISSM and the Cyber Security team are
asked to review or decide. Hardware, facility, and network work is in [`../hardware/`](../hardware/), and building
and installing the software is in [`../software/`](../software/). Those folders link here when they depend on a
security decision. Security decisions are not tracked anywhere else.

**Status:** Draft, 2026-11-11. First provision.

## How to read this package

We are listing **everything we want to bring into the lab, including the alternatives we are still choosing
between**, with the facts Cyber needs to judge each one. Cyber decides what is allowed. Where we have a
recommendation or a proposed control, we say so, but we have not left anything off the list because we expected
it to be refused.

| Document | What it covers |
|---|---|
| [12 Software BOM](12-software-bom.md) ([CSV](12-software-bom.csv)) | Every piece of software: version, supplier, license, how it arrives, outbound connections and how they are switched off |
| [13 Model BOM](13-model-bom.md) | Every model and model data file: publisher, commit, license, file format, size, how it is checked, and the models that ride inside container images |
| Decision register (below) | Every question for the ISSM and Cyber, and what each answer affects |
| Still to write (below) | Content that is neither software nor a model, such as keys and certificates |

## Decision register

**Affects** says which part of the work waits on the answer: **HW** (hardware purchase or install),
**SW** (software build and install), **Models**, or **Process** (how releases move and are signed). **Whose call**
says who decides: the ISSM or Cyber, the program, or us (listed so Cyber can approve either option).

### Lab entry, accreditation, and process

| ID | Decision needed | Affects | Whose call | Default if no answer | Answer |
|---|---|---|---|---|---|
| S1 | Is the lab classified? What is the approved process to bring hardware in? | HW | ISSM | Classified; hardware goes one way only | |
| S2 | May new lab hardware be burned in on the unclassified side before it enters (then wiped)? | HW | ISSM | No; burn in inside the lab | |
| S3 | Approved transfer media type, and how long a transfer takes | Process | ISSM | Encrypted SSD, 1 week turnaround | |
| S4 | Is Secure Boot required on servers? It changes how the NVIDIA driver is installed: the kernel module must be signed with a key enrolled on each server. | HW, SW | ISSM | Off | |
| S6 | Are upstream (non-Iron Bank) container images allowed in the lab for phase 1? Iron Bank images can be swapped in where they exist without changing the scripts. | SW | ISSM | Iron Bank where available, upstream otherwise | |
| S7 | Where may the staging server live? | HW | Program | | No staging server (decided 2026-10-30). The build workstation rehearses each bundle; see [04](../software/04-prototype-plan.md). |
| S8 | Is a laptop allowed in the room for first switch setup over a console cable? | HW | ISSM | No; use the lab's approved device | |
| L1 | Does accreditation require a specific server OS (for example RHEL 9 with STIG)? Is there a package mirror? Asked in the quote email ([08a](../hardware/08a-quote-servers-submitted.md), question 6). | HW, SW | ISSM, Lab IT | Rocky Linux 9 (free); RHEL 9 if required, at about $1,400 per server per year | Our choice unless accreditation says otherwise. The NVIDIA driver is built against the OS kernel, and RHEL needs paid subscriptions (not in the hardware budget). |
| L5 | Internet access during the initial build and debug? | SW | ISSM | No. All software arrives on transfer media. | |
| S10 | Bundle signing: cosign or GPG, who holds the signing key, and how the public key reaches the lab ([11](../software/11-sandbox-bringup-plan.md), W5) | Process | ISSM | GPG (the OS already has `gpg`; `cosign` is not in the lab today and would have to be added) | |
| S11 | OS packages the driver build needs: gcc, kernel-devel, dkms (from EPEL, not base Rocky/RHEL), SELinux policy packages ([11](../software/11-sandbox-bringup-plan.md), W3) | SW | ISSM, Lab IT | Lab mirror with EPEL allowed; otherwise we add these RPMs to the bundle | |

### Software ([12](12-software-bom.md))

| ID | Decision needed | Affects | Whose call | Our recommendation | Answer |
|---|---|---|---|---|---|
| S12 | Speech-to-text, two options, both listed in the BOMs: **(a)** speaches server with faster-whisper (A4, model M2), or **(b)** vLLM, which we already run, serving OpenAI's Whisper (model M5 or M6). faster-whisper itself is the most widely used engine for self-hosted Whisper and is actively maintained. The concern is the speaches server around it: no stable release since 2025-09-19. | SW, Models | Us (open); Cyber approves either | Open. Needs a GPU test that the sandbox can't do. | |
| S13 | Chat page image, two options, both listed: **(a)** the standard Open WebUI image, or **(b)** the `slim` image ([13](13-model-bom.md), section 2). | SW, Models | Us (open); Cyber approves either | Open | |
| S14 | Licenses to note: NVIDIA's proprietary user-space driver and the CUDA EULA (G1, A1), Open WebUI's branding clause (A3), LiteLLM's `enterprise/` code present but unused (A2), gpt-oss usage policy (M1) | SW, Models | Legal or program, if required | | |
| S15 | `rke2-security-responder` ships with RKE2 and appears to report the cluster version to SUSE. What it contacts, and whether we turn it off. | SW | Us, for Cyber's information | Turn it off if it calls out. The sandbox network tripwire will show whether it tries. | |
| S16 | Known security shortcuts already tracked: no network policies yet (W8), local accounts and API keys until single sign-on (W9), what the audit log records (W10), no CIS hardening profile yet (W11) | SW | Cyber | See [11](../software/11-sandbox-bringup-plan.md), section 7 | |
| S17 | **For information.** Ingress is Traefik (K4), which ships inside RKE2. ingress-nginx was retired upstream in March 2026 and removed from RKE2 1.37. | SW | | No new supplier | |
| S18 | **For information.** NVIDIA driver branch: we plan R620 (long-term support to September 2029). Until a GPU Operator release lists R620, the pin stays on R580 (long-term support to June 2028). | SW | Us | R620 | |
| S19 | **For information.** First full scan results come with the first real pull. `SUMMARY.txt` goes to Cyber before the bundle is sealed. | SW | | | |

### Models ([13](13-model-bom.md))

| ID | Decision needed | Affects | Whose call | Our recommendation | Answer |
|---|---|---|---|---|---|
| S5 | Is there an approved model list? Approve each requested model in [13](13-model-bom.md), sections 1 and 3: gpt-oss-120b, the speech models, the embedding models, the reranker. | Models | Program, ISSM | | |
| S20 | **Which model file formats are allowed.** See [13](13-model-bom.md), section 4 for why the line matters. Options: **(a)** formats that cannot run code when loaded (safetensors, CTranslate2), **(b)** safetensors only, **(c)** also pickle-format files, with scanning and restricted loading. | Models | ISSM | (a). The line that matters is whether loading a file can run code, not the file extension. | |
| S21 | Controls for model files: refuse `.py` files at pull, and scan container images for model files that bypass the model intake | Models | Cyber | Add both | |
| S9 | Future phase: may a typed decision model (Cloudflare Clef, Qwen3.8-27B base, Apache 2.0) run in the lab? It ships a Python code file that runs at load time, and it needs its own model server (SGLang) and gateway route. | Models, SW | ISSM, Program | Deferred; not in phase 1 | Deferred 2026-10-30 |

IDs are never reused. S1 to S9, L1, and L5 came from the old open-questions list (doc 07), which now holds only
hardware questions ([hardware/07](../hardware/07-open-questions.md)) and Lab IT software questions
([software/07](../software/07-open-questions.md)).

## Still to write: content that is neither software nor a model

| Content | Examples | Plan |
|---|---|---|
| **Keys and certificates** | Bundle signing public key, lab CA and TLS certificates, the gateway master key and user API keys (created in the lab), RKE2 join token | A key and certificate inventory (CycloneDX 1.6 calls it a CBOM): who holds each key, where it lives, how it rotates. Write next. |
| **Configuration** | Chart values, Kubernetes manifests, RKE2 config, the Zarf package definition | Ours are in this repository at the commit in each bundle's `SOURCE_COMMIT`. Settings made in the lab after install (chat page admin settings, gateway keys) are not recorded yet. |
| **Data files** | Trivy vulnerability databases, LiteLLM price list, tokenizer vocabularies | Listed in 12 and 13 |
| **Firmware** | BIOS, BMC, NIC, NVMe, GPU VBIOS, NX-OS | Listed in 12 (H1 to H4); versions recorded at the delivery check |
| **License and entitlement files** | NX-OS Essentials license, RHEL subscriptions if used | To list with the firmware |
| **Documents and training pages** | This repository's documents, the two training pages (HTML with JavaScript), vendor manuals | Decision needed: do they go into the lab at all? |
| **Test data** | Smoke-test audio and PDF files, load-test prompts, later the metrics pipeline's sample data | A dataset list when the pipeline arrives |
| **Data created in the lab** | Chat history, uploaded documents, document vectors, gateway logs | Not a BOM item. Cyber will want storage and retention rules ([11](../software/11-sandbox-bringup-plan.md), W10, W13). |
