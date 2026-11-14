# 16. Phased software list with download links (for the ISSM)

**Track:** Cyber Security ([package index and decision register](README.md)).
**Status:** Draft, 2026-11-14. Every item we plan to bring into the lab, by phase, with the exact place it is
downloaded from. The same list as a spreadsheet: [16-phased-sbom.csv](16-phased-sbom.csv). Licenses and
details: [12](12-software-bom.md) (software) and [13](13-model-bom.md) (models).

Every link was checked on 2026-11-14 (container image tags against their registries). "image" means a
container image pulled from that registry address. Nothing is downloaded inside the lab: every item is
downloaded on the build workstation, scanned, and carried in on approved media in one signed bundle.

## The phases

| Phase | Analysts can | Needs first |
|---|---|---|
| 0. Approvals and hardware | Nothing yet. Servers bought, approved, racked, with the lab's OS. | ISSM approvals for hardware entry, OS, transfer media |
| 1. SI chat | Chat with SI in a browser: questions, voice input, document upload | Phase 0, and the phase 1 software approved |
| 2. Analyst tools | Call SI from Jupyter, VS Code, MATLAB, and scripts | Phase 1, and approval to open an API address and install tools on analyst PCs |
| 3. Platform services | Sign in with lab accounts; changes go through GitLab and Argo CD; monitoring | Phase 1's cluster |
| 4. Metrics pipeline | Run metrics on lab data, see results on pages and in notebooks | Phase 3 (change loop), phase 2 (notebooks calling SI), and approval to read lab data |

Phases 2 and 3 do not depend on each other; the order is our proposal.

## Phase 0. Approvals and hardware

Lab-provided or shipped on the hardware. Not in our bundle. Listed so the review covers everything that runs.

| ID | Component | Version | License | Download from | Notes |
|---|---|---|---|---|---|
| P1 | Rocky Linux 9 (default) or RHEL 9 if accreditation requires | 9.x (TBD) | GPL-2.0 and mixed open source (Rocky); Red Hat subscription (RHEL) | <https://rockylinux.org/download> (lab-provided image; RHEL: <https://access.redhat.com/downloads>) |  |
| P2 | gcc, make, kernel-devel (matching running kernel), dkms | OS mirror version | GPL family | Lab mirror. Upstream: <https://dl.rockylinux.org/pub/rocky/9/> and <https://dl.fedoraproject.org/pub/epel/9/> (dkms) |  |
| P3 | rsync, openssl, python3, gnupg2, iperf3 | OS mirror version | Mixed open source | Lab mirror. Upstream: <https://dl.rockylinux.org/pub/rocky/9/> |  |
| P4 | container-selinux, rke2-selinux | OS mirror / Rancher RPM repo | GPL-2.0 / Apache-2.0 | Lab mirror. Upstream: <https://dl.rockylinux.org/pub/rocky/9/> (container-selinux) and <https://rpm.rancher.io/> (rke2-selinux) |  |
| P5 | ipmitool, NVIDIA DCGM (datacenter-gpu-manager) | OS mirror version | BSD-3 / Apache-2.0 | Lab mirror. Upstream: <https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/> (DCGM) |  |
| H1 | Cisco NX-OS on sw01 (N93180YC-FX3) + NX-OS Essentials license | TBD (factory or lab-approved image) | Cisco EULA | Ships on the switch. Updates: <https://software.cisco.com/download/home> (Cisco account) |  |
| H2 | Server BIOS/UEFI and BMC firmware (Thinkmate GPU server and service nodes) | TBD at delivery | Vendor proprietary | Ships on the servers. Updates from Thinkmate / board vendor |  |
| H3 | NIC firmware (Intel E810-XXVDA2, Broadcom N225P), NVMe firmware, GPU VBIOS | TBD at delivery | Vendor proprietary | Ships on the cards. Updates from Intel / Broadcom / drive vendor |  |
| H4 | Geist PDU and Liebert CRV firmware | existing | Vendor proprietary | Already in the lab |  |

## Phase 1. SI chat

The first bundle. Analysts chat with SI in a browser. This is what we ask to review first.

| ID | Component | Version | License | Download from | Notes |
|---|---|---|---|---|---|
| K1 | RKE2 (binaries + air-gap image tarball + install.sh) | v1.37.2+rke2r1 | Apache-2.0 | <https://github.com/rancher/rke2/releases/download/v1.37.2%2Brke2r1/rke2-images.linux-amd64.tar.zst> ; <https://github.com/rancher/rke2/releases/download/v1.37.2%2Brke2r1/rke2.linux-amd64.tar.gz> ; <https://github.com/rancher/rke2/releases/download/v1.37.2%2Brke2r1/sha256sum-amd64.txt> ; <https://get.rke2.io> |  |
| K2 | Canal CNI (Calico + Flannel) | with K1 (Calico v3.32.2, Flannel v0.28.10) | Apache-2.0 | Inside the K1 image tarball |  |
| K3 | CoreDNS | with K1 (v1.14.7) | Apache-2.0 | Inside the K1 image tarball |  |
| K4 | Traefik ingress controller | with K1 (v3.7.16, SUSE hardened build) | MIT | Inside the K1 image tarball |  |
| K5 | metrics-server, snapshot-controller, helm-controller, cluster-autoscaler (CoreDNS), pause | with K1 (metrics-server v0.9.0) | Apache-2.0 | Inside the K1 image tarball |  |
| K6 | local-path-provisioner | v0.0.37 | Apache-2.0 | <https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.37/deploy/local-path-storage.yaml> ; image docker.io/rancher/local-path-provisioner:v0.0.37 |  |
| K7 | busybox | 1.38.0 | GPL-2.0 | image docker.io/library/busybox:1.38.0 |  |
| K8 | Zarf CLI | v0.89.0 | Apache-2.0 | <https://github.com/zarf-dev/zarf/releases/download/v0.89.0/zarf_v0.89.0_Linux_amd64> ; <https://github.com/zarf-dev/zarf/releases/download/v0.89.0/checksums.txt> |  |
| K9 | Zarf init package: injector, seed registry, registry (CNCF Distribution), mutating agent | v0.89.0 | Apache-2.0 | <https://github.com/zarf-dev/zarf/releases/download/v0.89.0/zarf-init-amd64-v0.89.0.tar.zst> |  |
| G1 | NVIDIA data center driver (open kernel modules + user-space) | 580.196.07 now (R580 long-term support branch); planned R620 620.70.06 once a GPU Operator release lists it | Kernel modules MIT/GPL-2.0; user-space NVIDIA proprietary license | <https://us.download.nvidia.com/tesla/580.196.07/NVIDIA-Linux-x86_64-580.196.07.run> (planned: <https://us.download.nvidia.com/tesla/620.70.06/NVIDIA-Linux-x86_64-620.70.06.run>) |  |
| G2 | NVIDIA GPU Operator (Helm chart + images) | v26.7.2 | Apache-2.0 (images include NVIDIA components under NVIDIA terms) | <https://helm.ngc.nvidia.com/nvidia/charts/gpu-operator-v26.7.2.tgz> ; images from nvcr.io/nvidia (full list in the bundle's IMAGES.txt) |  |
| A1 | vLLM (OpenAI-compatible server) | v0.32.0 (CUDA 13.0) | Apache-2.0 (image includes CUDA runtime under NVIDIA CUDA EULA; PyTorch BSD-3) | image docker.io/vllm/vllm-openai:v0.32.0 |  |
| A2 | LiteLLM proxy (Helm chart + image) | image v1.108.4-lts; chart 1.89.2 | MIT (open-source core); enterprise/ directory under BerriAI commercial license (not enabled) | image ghcr.io/berriai/litellm:v1.108.4-lts ; chart oci://ghcr.io/berriai/litellm-helm:1.89.2 |  |
| A3 | Open WebUI, standard image (Helm chart + image) | image v0.12.5; chart 17.5.0 | Open WebUI License (BSD-3 based with branding clause) | image ghcr.io/open-webui/open-webui:v0.12.5 ; chart <https://github.com/open-webui/helm-charts/releases/download/open-webui-17.5.0/open-webui-17.5.0.tgz> | One of A3 or A3s (S13). |
| A4 | speaches (faster-whisper server) | 0.8.3-cuda | MIT (faster-whisper MIT; CTranslate2 MIT) | image ghcr.io/speaches-ai/speaches:0.8.3-cuda | Server choice open (S12). |
| A5 | Hugging Face Text Embeddings Inference (CPU) | cpu-1.9.4 | Apache-2.0 | image ghcr.io/huggingface/text-embeddings-inference:cpu-1.9.4 |  |
| A6 | Apache Tika server (full image with Tesseract OCR) | 3.3.3.0-full | Apache-2.0 (Tesseract Apache-2.0; image includes other OS packages) | image docker.io/apache/tika:3.3.3.0-full |  |
| A7 | CloudNativePG operator (Helm chart + image) | chart 0.29.1 (operator 1.30.1) | Apache-2.0 | <https://github.com/cloudnative-pg/charts/releases/download/cloudnative-pg-v0.29.1/cloudnative-pg-0.29.1.tgz> ; image ghcr.io/cloudnative-pg/cloudnative-pg:1.30.1 |  |
| A8 | PostgreSQL with pgvector (CloudNativePG standard image) | 18.6-standard-trixie | PostgreSQL License (pgvector PostgreSQL License); Debian 13 base | image ghcr.io/cloudnative-pg/postgresql:18.6-standard-trixie |  |
| M1 | gpt-oss-120b | main, resolved to a commit at pull time | Apache-2.0 plus gpt-oss usage policy | <https://huggingface.co/openai/gpt-oss-120b> (safetensors files only; exact commit in the bundle's MODELS.txt) |  |
| M2 | faster-whisper-large-v3 | main, resolved to a commit at pull time | MIT | <https://huggingface.co/Systran/faster-whisper-large-v3> | Converter is Systran (France); see S22 and M11. |
| M3 | snowflake-arctic-embed-l-v2.0 | main, resolved to a commit at pull time | Apache-2.0 | <https://huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0> (safetensors only) | Built on a BAAI model (China); see S22 and M10. |
| M4 | tiktoken vocabularies o200k_base, cl100k_base | fixed files | Distributed with tiktoken (MIT); confirm | <https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken> ; <https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken> |  |
| S1 | Trivy scanner | 0.76.2 | Apache-2.0 | <https://github.com/aquasecurity/trivy/releases/download/v0.76.2/trivy_0.76.2_Linux-64bit.tar.gz> ; <https://github.com/aquasecurity/trivy/releases/download/v0.76.2/trivy_0.76.2_checksums.txt> |  |
| S2 | Trivy vulnerability DB and Java DB | downloaded at pull time (date in MANIFEST.txt) | Apache-2.0 (advisory sources have own terms) | images ghcr.io/aquasecurity/trivy-db:2 and ghcr.io/aquasecurity/trivy-java-db:1 (fetched by trivy) |  |
| F1 | Delivery and intake scripts (verify.sh, deploy.sh), Zarf template, chart values, manifests | git commit in SOURCE_COMMIT | Program-owned (repo LICENSE) | Ours. In the bundle (intake/), no download |  |
| F2 | validate/ (hw-check.sh, net-test.sh, llm-load-test.py) | git commit in SOURCE_COMMIT | Program-owned (repo LICENSE) | Ours. In the bundle, no download |  |

## Phase 1. SI chat (option for Cyber)

Alternatives to phase 1 items. Cyber picks; we bring whichever is approved.

| ID | Component | Version | License | Download from | Notes |
|---|---|---|---|---|---|
| A3s | Open WebUI, slim image (alternative to A3) | v0.12.5-slim; chart 17.5.0 | Open WebUI License (BSD-3 based with branding clause) | image ghcr.io/open-webui/open-webui:v0.12.5-slim ; chart <https://github.com/open-webui/helm-charts/releases/download/open-webui-17.5.0/open-webui-17.5.0.tgz> | One of A3 or A3s (S13). |
| M5 | whisper-large-v3-turbo | commit 41f01f3f (2024-10-04) | MIT | <https://huggingface.co/openai/whisper-large-v3-turbo> |  |
| M6 | whisper-large-v3 | commit 06f233fe (2024-08-12) | Apache-2.0 | <https://huggingface.co/openai/whisper-large-v3> |  |
| M10 | granite-embedding-278m-multilingual | commit a9cb5338 (2025-08-19) | Apache-2.0 | <https://huggingface.co/ibm-granite/granite-embedding-278m-multilingual> | US replacement for M3. |
| M11 | whisper-large-v3 (or -turbo) converted to CTranslate2 by us | source commit of M6 or M5 | Apache-2.0 (large-v3) / MIT (turbo) | Made by us from M5 or M6 with the CTranslate2 converter: <https://pypi.org/project/ctranslate2/> | US-only lineage replacement for M2. |
| A4b | Speech-to-text server option (b): whisper-asr-webservice | v1.10.0 | MIT | image docker.io/onerahmet/openai-whisper-asr-webservice:v1.10.0-gpu | Not OpenAI-compatible; needs an adapter (S12). |

## Phase 2. Analyst tools

Not in the first bundle. Jupyter, VS Code, MATLAB, and scripts reach SI through an API address with a personal key.

| ID | Component | Version | License | Download from | Notes |
|---|---|---|---|---|---|
| C1 | jupyter-ai | 2.31.7 | BSD-3-Clause | <https://pypi.org/project/jupyter-ai/2.31.7/> |  |
| C2 | langchain-openai / langchain / langchain-core | 0.3.35 / 0.3.30 / 0.3.86 | MIT | <https://pypi.org/project/langchain-openai/0.3.35/> ; <https://pypi.org/project/langchain/0.3.30/> ; <https://pypi.org/project/langchain-core/0.3.86/> |  |
| C3 | openai (Python client) | 2.48.0 | Apache-2.0 | <https://pypi.org/project/openai/2.48.0/> |  |
| C4 | Python wheel dependencies of C1-C3 | as resolved at pull time | Mixed open source (listed per wheel) | <https://pypi.org/> (each wheel's URL is listed in clients/RESOLVED.txt at pull time) |  |
| C5 | Continue VS Code extension (VSIX) | 2.1.0 (linux-x64 and win32-x64) | Apache-2.0 | <https://open-vsx.org/api/Continue/continue/win32-x64/2.1.0> ; <https://open-vsx.org/api/Continue/continue/linux-x64/2.1.0> |  |
| C6 | MATLAB | existing lab install | existing lab license | Already in the lab |  |

## Phase 3. Platform services

Not chosen or pinned yet. Versions get pinned and checked when the phase is planned.

| ID | Component | Version | License | Download from | Notes |
|---|---|---|---|---|---|
| X1 | Big Bang (Platform One baseline) | not chosen yet | Apache-2.0 | <https://repo1.dso.mil/big-bang/bigbang> | Installs Harbor, GitLab, Argo CD, Keycloak, monitoring on the phase 1 cluster. |
| X2 | Iron Bank hardened images | per image | per image | <https://registry1.dso.mil> (Platform One account) | Can replace phase 1 upstream images (S6). |
| X3 | Keycloak (sign-in for the chat page and gateway) | not chosen yet | Apache-2.0 | <https://github.com/keycloak/keycloak/releases> | Replaces local accounts. |
| X4 | Harbor registry | not chosen yet | Apache-2.0 | <https://github.com/goharbor/harbor/releases> | Replaces the Zarf registry. |
| X5 | GitLab and GitLab Runner | not chosen yet | MIT (CE) | <https://about.gitlab.com/install/> | In-lab change loop. |
| X6 | Argo CD | not chosen yet | Apache-2.0 | <https://github.com/argoproj/argo-cd/releases> |  |
| X7 | Prometheus and Grafana (monitoring) | not chosen yet | Apache-2.0 / AGPL-3.0 | <https://github.com/prometheus/prometheus/releases> ; <https://github.com/grafana/grafana/releases> |  |

## Phase 4. Metrics pipeline

Not chosen or pinned yet. Runs on the platform from phases 1 and 3.

| ID | Component | Version | License | Download from | Notes |
|---|---|---|---|---|---|
| X8 | Dagster (orchestration) | not chosen yet | Apache-2.0 | <https://github.com/dagster-io/dagster/releases> |  |
| X9 | JupyterHub (analyst notebooks in the cluster) | not chosen yet | BSD-3-Clause | <https://github.com/jupyterhub/zero-to-jupyterhub-k8s/releases> |  |
| X10 | Evidence (published metric pages) | not chosen yet | MIT | <https://github.com/evidence-dev/evidence/releases> |  |
| X11 | Metric readers and plugins | ours, not written yet |  | Ours. Written and tested in the lab |  |

## Phase Grow (any time after 1)

Optional additions that need no new design.

| ID | Component | Version | License | Download from | Notes |
|---|---|---|---|---|---|
| M9 | granite-embedding-reranker-english-r2 | commit d09d3d69 (2025-11-06) | Apache-2.0 | <https://huggingface.co/ibm-granite/granite-embedding-reranker-english-r2> | Better document search. |
| X12 | Second GPU server (100 users) | hardware |  | Same software bundle | No software change. |
