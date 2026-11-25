# 5. Staging artifact list: what the bring-up scripts fetch

**Track:** Software. **Generated** by `docs/diagrams/build_staging_artifacts.py` from the pin files in
`delivery/` and the ISSM list. Do not edit by hand.

Every artifact the scripts download, where it ends up, and whether it matches what the ISSM has. Three places:

- **Lab bundle:** sealed into the signed bundle and installed in the lab. Should match the ISSM list.
- **Build side only:** used on the build workstation (or VM1 in staging) to make the bundle. Never crosses.
- **Staging only:** the staging add-on for the VMs with no GPU ([Staging runbook](4-staging-runbook.md)). Never crosses.

A **Differs** row is a place where the scripts and the ISSM list disagree. Each one is either a decision we
are waiting on or an update to send for the ISSM list.

| Group | Artifact | Pin | Where it ends up | ISSM ID | Against the ISSM list |
|---|---|---|---|---|---|
| Kubernetes | RKE2 (binaries, air-gap images, installer) | v1.37.2+rke2r1 | Lab bundle | K1 | Same |
| Kubernetes | local-path-provisioner | v0.0.37 | Lab bundle | K6 | Same |
| Kubernetes | busybox | 1.38.0 | Lab bundle | K7 | Same |
| Kubernetes | Zarf CLI and init package | v0.89.0 | Lab bundle | K8 | Same |
| GPU | NVIDIA driver (.run) | 580.196.07 | Lab bundle | G1 | Same |
| GPU | NVIDIA GPU Operator | v26.7.2 | Lab bundle | G2 | Same |
| Applications | vLLM | v0.32.0 | Lab bundle | A1 | Same |
| Applications | LiteLLM image and chart | v1.108.4-lts 1.89.2 | Lab bundle | A2 | Same |
| Applications | Open WebUI image and chart | v0.12.5 17.5.0 | Lab bundle | A3 | Same |
| Applications | speaches (Whisper server) | 0.8.3-cuda | Lab bundle | A4 | Same |
| Applications | Text Embeddings Inference | cpu-1.9.4 | Lab bundle | A5 | Same |
| Applications | Apache Tika | 3.3.3.0-full | Lab bundle | A6 | Same |
| Applications | CloudNativePG chart | 0.29.1 | Lab bundle | A7 | Same |
| Applications | PostgreSQL | 18.6-standard-trixie | Lab bundle | A8 | Same |
| Security tools | Trivy | 0.76.2 | Lab bundle | Sec1 | Same |
| Security tools | Trivy vulnerability databases | downloaded at pull time | Lab bundle | Sec2 | Same |
| Models | openai/gpt-oss-120b | commit b5c939de | Lab bundle | M1 | Same |
| Models | openai/whisper-large-v3, converted to CTranslate2 by us | commit 06f233fe | Lab bundle | M11 | **Differs:** the ISSM list lists M11 as an option; the scripts deliver it |
| Models | ibm-granite/granite-embedding-278m-multilingual | commit a9cb5338 | Lab bundle | M10 | **Differs:** the ISSM list lists M10 as an option; the scripts deliver it |
| Models | tiktoken vocabularies (o200k_base, cl100k_base) | fixed files, SHA-256 checked | Lab bundle | M4 | Same |
| OS packages | For every node: container-selinux, rke2-selinux, rsync, openssl, python3, gnupg2, iperf3, ipmitool, and every package they depend on | Rocky 9.9 repos, EPEL 9, Rancher, NVIDIA | Lab bundle | OS2 to OS5 | **Differs:** the ISSM list says these come from a lab mirror; with no mirror the bundle carries them, with many more dependencies |
| OS packages | For gpu01 only: gcc, make, kernel-devel, kernel-headers, elfutils-libelf-devel, dkms, datacenter-gpu-manager, and every package they depend on | Rocky 9.9 repos, EPEL 9, Rancher, NVIDIA | Lab bundle | OS2 to OS5 | **Differs:** the ISSM list says these come from a lab mirror; with no mirror the bundle carries them, with many more dependencies |
| Later phase | Analyst tools: Python wheels and the Continue extension | Python 3.9 3.10 3.11 3.12 3.13 3.14 3.15; Continue 2.1.0 | Later phase (left out) | C1 to C5 | Only with WITH_CLIENTS=1. Staging leaves them out. |
| Build tools | Build container base image | rockylinux/rockylinux:9.9 | Build side only |  | Not on the ISSM list (not delivered) |
| Build tools | Helm | v4.3.2 | Build side only |  | Not on the ISSM list (not delivered) |
| Build tools | Hugging Face CLI (huggingface_hub) | 2.4.0 | Build side only |  | Not on the ISSM list (not delivered) |
| Build tools | Container OS tools: jq, skopeo, git, createrepo_c, python3.12, and others | Rocky 9.9 repos at build time | Build side only |  | Not on the ISSM list (not delivered) |
| Build tools | Whisper converter: ctranslate2 | 4.5.0 | Build side only |  | Not on the ISSM list (not delivered). Writes M11. |
| Build tools | Whisper converter: transformers | 4.46.3 | Build side only |  | Not on the ISSM list (not delivered). Writes M11. |
| Build tools | Whisper converter: torch | 2.5.1+cpu | Build side only |  | Not on the ISSM list (not delivered). Writes M11. |
| Build tools | Whisper converter: numpy | 1.26.4 | Build side only |  | Not on the ISSM list (not delivered). Writes M11. |
| Staging add-on | vLLM CPU image | v0.32.0-x86_64 | Staging only |  | Not on the ISSM list. Never sealed into the bundle. |
| Staging add-on | speaches CPU image | 0.8.3-cpu | Staging only |  | Not on the ISSM list. Never sealed into the bundle. |
| Staging add-on | Stand-in chat model: ibm-granite/granite-3.3-2b-instruct | commit 707f574c | Staging only |  | Not on the ISSM list. Never sealed into the bundle. |

## On the ISSM list but not fetched by the scripts

Inside the RKE2 image tarball (K2 to K5, K9 with K8), on the hardware (H), our own scripts (F), and the OS itself
(OS1) are left out of this check. The rest:

| ISSM ID | Component | Phase on the ISSM list | Why the scripts don't fetch it |
|---|---|---|---|
| M2 | faster-whisper-large-v3 | 1. SI chat | Replaced by M11 under the whole-lineage USA-only reading (S22) |
| M3 | snowflake-arctic-embed-l-v2.0 | 1. SI chat | Replaced by M10 under the whole-lineage USA-only reading (S22) |
| A3.1 | Open WebUI, slim image (alternative to A3) | 1. SI chat (Currently considering) | Option; the standard image (A3) is used for now (S13) |
| M5 | whisper-large-v3-turbo | 1. SI chat (Currently considering) | Option; M11 is converted from M6 |
| M6 | whisper-large-v3 | 1. SI chat (Currently considering) | Its weights are fetched and converted into M11 (build side only) |
| A4.1 | Speech-to-text server option (b): whisper-asr-webservice (alternative to A4) | 1. SI chat (Currently considering) | Option; speaches (A4) is used (S12) |
