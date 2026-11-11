# 12. Software bill of materials (initial, for Cyber Security)

**Track:** Cyber Security ([package index and decision register](README.md)).
**Status:** Draft, 2026-11-11. First provision to the Cyber Security team.
**Scope:** every piece of software that phase 1 (the SI service) brings into the lab, plus the lab-side
software it depends on and the firmware that ships on the hardware.
**Flat list:** [12-software-bom.csv](12-software-bom.csv), one row per component with the IDs used below.

**This list includes the alternatives we are still choosing between** (A3s, and the vLLM speech option in
A1), so Cyber can rule on all of them. The decisions are in the [decision register](README.md).

**Versions were checked against upstream on 2026-11-09** and match `delivery/versions.env`. The rule: the
newest stable release, unless that line is only days old and still getting hotfixes (then the last patch of the
previous line). The reason for each pin is written next to it in `versions.env`. The charts have not yet been
rendered or rehearsed at these versions ([11](../software/11-sandbox-bringup-plan.md), F4), and `01-check-latest.sh` runs
again before the real pull, so a patch version may move. Each sealed bundle carries its own exact,
machine-generated record (section 9), and this document is reissued against it.

## 1. How software enters the lab

Everything we bring arrives in **one signed release bundle** on approved transfer media ([06](../software/06-software-delivery.md)).
Nothing is downloaded inside the lab, and the services are set to make no outbound calls (section 8).

1. A connected build workstation (unclassified side) pulls every item from its upstream source and checks
   upstream SHA-256 checksums where the project publishes them.
2. Trivy scans every container image, and the reports go into the bundle.
3. `90-seal.sh` writes `SHA256SUMS` over every file and signs it (cosign or GPG). It refuses to seal from
   uncommitted source.
4. In the lab, `intake/verify.sh` refuses an unsigned bundle, a bad signature, or a checksum mismatch, and
   refuses any model file that could run code when loaded (pickle). Which model formats are allowed is
   Cyber's decision (S20).

What does **not** come in the bundle: the server OS and its packages (from the lab's OS media and mirror),
the firmware on the hardware, and MATLAB (already in the lab).

| Category | Items | Section |
|---|---|---|
| OS and OS packages (lab-provided) | 5 | 2 |
| Kubernetes platform and air-gap tooling | 9 | 3 |
| NVIDIA driver and GPU Operator | 2 | 4 |
| Application services (container images) | 8 | 5 |
| Model weights and tokenizer data | 4 | 6 |
| Security tooling | 2 | 7 |
| Analyst workstation software | 6 | 7 |
| First-party code (this repository) | 2 | 7 |
| Firmware shipped on the hardware | 4 | 7 |

## 2. Operating system and OS packages (lab-provided, not in the bundle)

| ID | Component | Version | License | Where | Notes |
|---|---|---|---|---|---|
| P1 | Rocky Linux 9 (default), or RHEL 9 if accreditation requires it | 9.x, TBD | Open source (Rocky); Red Hat subscription (RHEL) | svc01-03, gpu01 | Open question [decision register](README.md) L1, including the hardening baseline (STIG or not) |
| P2 | gcc, make, kernel-devel for the running kernel, dkms | lab mirror | GPL family | gpu01 | Builds the NVIDIA kernel module. **dkms is in EPEL, not base Rocky/RHEL.** |
| P3 | rsync, openssl, python3, gnupg2, iperf3 | lab mirror | open source | all nodes | Used by `intake/deploy.sh` and `validate/` |
| P4 | container-selinux, rke2-selinux | lab mirror or Rancher RPM repo | GPL-2.0 / Apache-2.0 | all nodes | Needed with SELinux enforcing |
| P5 | ipmitool, NVIDIA DCGM (optional) | lab mirror | BSD-3 / Apache-2.0 | all / gpu01 | Hardware checks and burn-in only |

If the lab has no OS mirror, P2 to P4 must be added to the bundle as RPMs matched to the lab's kernel
([11](../software/11-sandbox-bringup-plan.md), W3).

## 3. Kubernetes platform and air-gap tooling

| ID | Component | Version | Source | License |
|---|---|---|---|---|
| K1 | RKE2 (binaries, air-gap image tarball, `install.sh`) | v1.37.2+rke2r1 | github.com/rancher/rke2 | Apache-2.0 |
| K2 | Canal CNI (Calico + Flannel), inside K1 | Calico v3.32.2, Flannel v0.28.10 | SUSE Rancher hardened images | Apache-2.0 |
| K3 | CoreDNS, inside K1 | v1.14.7 | same | Apache-2.0 |
| K4 | **Traefik** ingress controller, inside K1 | v3.7.16 | same | MIT |
| K5 | metrics-server, snapshot-controller, helm-controller, cluster-autoscaler for CoreDNS, pause, inside K1 | metrics-server v0.9.0 | same | Apache-2.0 |
| K6 | local-path-provisioner | v0.0.37 | github.com/rancher/local-path-provisioner | Apache-2.0 |
| K7 | busybox (helper image for K6) | 1.38.0 | docker.io/library/busybox | GPL-2.0 |
| K8 | Zarf CLI | v0.89.0 | github.com/zarf-dev/zarf | Apache-2.0 |
| K9 | Zarf init package: injector, seed registry, registry (CNCF Distribution), mutating agent | v0.89.0 | same | Apache-2.0 |

K1 also contains kubelet, kube-apiserver, etcd v3.7.1, containerd v2.3.7, runc, kubectl, and crictl, all
Apache-2.0, and `rke2-security-responder` (section 8).

**Ingress: Traefik, not ingress-nginx.** ingress-nginx was retired upstream in March 2026 and gets no more
fixes. RKE2 made Traefik the default in v1.36 and removed ingress-nginx in v1.37. Traefik ships inside RKE2,
so it adds no new supplier, and `deploy.sh` sets `ingress-controller: traefik` on every server. Traefik puts no
limit on how long a service takes to answer and no limit on body size, so the long requests and 50 MB uploads
that needed nginx annotations need nothing now.
The Zarf init uses its default components only (no Git server, no logging stack).

## 4. NVIDIA driver and GPU Operator

| ID | Component | Version | Source | License |
|---|---|---|---|---|
| G1 | NVIDIA data center driver, open kernel modules | 580.196.07 now; **planned R620** (620.70.06) | us.download.nvidia.com (`.run` installer) | Kernel modules MIT/GPL-2.0; user-space libraries under NVIDIA's proprietary license |
| G2 | NVIDIA GPU Operator (Helm chart and images) | v26.7.2 | helm.ngc.nvidia.com, nvcr.io | Apache-2.0; images include NVIDIA components under NVIDIA terms |

G2 supports Kubernetes 1.33 to 1.37, Rocky Linux 9.7, RHEL 9.2 to 9.8, and the RTX PRO 6000 Blackwell Server
Edition. **We plan to deliver R620**, NVIDIA's newest long-term support branch (end of life September 2029;
first release 620.70.06 on 2026-11-04). Until a GPU Operator release lists R620, G1 stays on R580, the previous
long-term support branch (end of life June 2028), which G2 lists. On 2026-11-11 the newest GPU Operator is still
v26.7.2. Both branches run CUDA 13.0 (the vLLM image) natively. We skip 595 (production branch, end of life
March 2027) and 615 (short-lived feature branch), because each driver branch change in an air-gapped lab costs a
rebuild, a rehearsal, and a transfer. The driver is built on gpu01 with DKMS. If Secure Boot is required ([decision register](README.md) S4), the module
must be signed with a key enrolled on the server. G2 has its driver container turned off. Its expected images
are gpu-operator, node-feature-discovery, container-toolkit, k8s-device-plugin, gpu-feature-discovery,
dcgm-exporter, operator-validator, and mig-manager. `package/IMAGES.txt` in the bundle is the exact list.

## 5. Application services (container images, in the Zarf package)

| ID | Component | Version | Image source | License | Where |
|---|---|---|---|---|---|
| A1 | vLLM, model server | v0.32.0 (CUDA 13.0) | docker.io/vllm/vllm-openai | Apache-2.0; image includes the CUDA runtime (NVIDIA CUDA EULA) and PyTorch (BSD-3) | gpu01 |
| A2 | LiteLLM, gateway (keys, logging, usage limits) | image v1.108.4-lts, chart 1.89.2 | ghcr.io/berriai/litellm | MIT core. The image also carries an `enterprise/` folder under BerriAI's commercial license; we don't enable it. | service nodes |
| A3 | Open WebUI, chat page, standard image | image v0.12.5, chart 17.5.0 | ghcr.io/open-webui/open-webui | Open WebUI License (BSD-3 based, with a clause that keeps its branding) | service nodes |
| A3s | **Alternative to A3:** Open WebUI `slim` image | v0.12.5-slim, same chart | ghcr.io/open-webui/open-webui | Same as A3 | service nodes |
| A4 | speaches (faster-whisper server), speech-to-text. **Alternative:** vLLM (A1) serves Whisper instead, with no extra image (S12). | 0.8.3-cuda | ghcr.io/speaches-ai/speaches | MIT | gpu01 |
| A5 | Text Embeddings Inference, CPU | cpu-1.9.4 | ghcr.io/huggingface/text-embeddings-inference | Apache-2.0 | gpu01 (CPU) |
| A6 | Apache Tika server, full image with Tesseract OCR | 3.3.3.0-full | docker.io/apache/tika | Apache-2.0 | service nodes |
| A7 | CloudNativePG operator | chart 0.29.1 (operator 1.30.1) | cloudnative-pg.github.io/charts | Apache-2.0 | service nodes |
| A8 | PostgreSQL 18 with pgvector | 18.6-standard-trixie | ghcr.io/cloudnative-pg/postgresql | PostgreSQL License; Debian 13 base | service nodes |

Why some lines are not the very newest: vLLM v0.33.0 has an image but no release yet (v0.32.0 is the latest
release). Open WebUI 0.13.0 came out on 2026-11-03 and had three hotfix releases on 2026-11-08, so we take
0.12.5, the last patch of 0.12. LiteLLM is on its LTS line. Its published Helm chart stops at 1.89.2, and that
chart still takes every setting we use. Tika 3.3.3.0 is the newest 3.x; 4.2.0 is the current major (section 10).

A3 or A3s is our open choice (S13). The standard image carries three small models we don't use
([13](13-model-bom.md), section 2) and the libraries to run them locally. The `slim` image leaves those out, but
it also has no built-in vector store, so the chat page's document vectors would move to PostgreSQL (A8). The Open WebUI chart also deploys a Redis 7.4 by default. **It is turned off.** One chat-page replica doesn't
need it, and Redis 7.4 is under RSALv2/SSPLv1, which are not open-source licenses.

Every image is an upstream image, referenced by tag, not by Iron Bank. Whether that is allowed for phase 1 is
open ([decision register](README.md) S6). Iron Bank images can be swapped in where they exist, without
changing the scripts. Each image's digest is recorded at build time (`scanner/reports/IMAGE-DIGESTS.txt`).

## 6. Model weights and tokenizer data

The full model list, including the models built into container images, is in the model BOM ([13](13-model-bom.md)).

| ID | Model | Format | Source | License | Size |
|---|---|---|---|---|---|
| M1 | gpt-oss-120b | safetensors only | huggingface.co/openai/gpt-oss-120b | Apache-2.0, plus OpenAI's gpt-oss usage policy | about 65 GB |
| M2 | faster-whisper-large-v3 | CTranslate2 `model.bin` | huggingface.co/Systran/faster-whisper-large-v3 | MIT | 3.09 GB |
| M3 | snowflake-arctic-embed-l-v2.0 | safetensors only | huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0 | Apache-2.0 | 568M parameters |
| M4 | tiktoken vocabularies `o200k_base`, `cl100k_base` | text | openaipublic.blob.core.windows.net | distributed with tiktoken (MIT); to confirm | small |

The model BOM also lists the alternative and later models we are asking about (M5 to M8).

Weights are meant to be data, not code. How the intake keeps it that way:

- Model files whose format can run code when loaded (pickle: `.bin`, `.pt`, `.pth`, `.pkl`, `.ckpt`) are
  refused at pull and again at `verify.sh`. M2's CTranslate2 `model.bin` is not pickle; it is accepted only if
  it starts with the CTranslate2 header. Why the line is drawn there, and the options for Cyber, are in
  [13](13-model-bom.md), section 4 (decision S20).
- No service sets `trust_remote_code`, so Python files in a model folder are never run. The pull does not yet
  refuse `.py` files (S21).
- Each model is pinned to a Hugging Face commit at pull time, with a SHA-256 for every file.
- Model approval is open ([decision register](README.md) S5).

## 7. Other items

**Security tooling**

| ID | Component | Version | Source | License |
|---|---|---|---|---|
| S1 | Trivy scanner | 0.76.2 | github.com/aquasecurity/trivy | Apache-2.0 |
| S2 | Trivy vulnerability DB and Java DB (data) | download date in `MANIFEST.txt` | ghcr.io/aquasecurity | Apache-2.0; advisory sources have their own terms |

**Analyst workstations** (installed by analysts on their own Windows and Linux machines, from the bundle)

| ID | Component | Version | Source | License |
|---|---|---|---|---|
| C1 | jupyter-ai | 2.31.7 | PyPI | BSD-3-Clause |
| C2 | langchain-openai, langchain, langchain-core | 0.3.35, 0.3.30, 0.3.86 | PyPI | MIT |
| C3 | openai (Python client) | 2.48.0 | PyPI | Apache-2.0 |
| C4 | All dependency wheels of C1 to C3 | as resolved | PyPI | Mixed open source |
| C5 | Continue VS Code extension (Linux and Windows VSIX) | 2.1.0 | open-vsx.org | Apache-2.0 |
| C6 | MATLAB | existing install | MathWorks | existing license; nothing added |

Wheels only, no source builds, for Python 3.9 to 3.14 (3.15 gets the OpenAI client only).
`clients/RESOLVED.txt` in each bundle lists every wheel by name and version. Expect 100 or more per platform.

**First-party code** (this repository, reviewable as source; the commit is in `SOURCE_COMMIT`)

| ID | Component | Language |
|---|---|---|
| F1 | `intake/verify.sh`, `intake/deploy.sh`, Zarf template, chart values, Kubernetes manifests | Bash, YAML |
| F2 | `validate/hw-check.sh`, `net-test.sh`, `llm-load-test.py` | Bash, Python standard library only |

**Firmware on the hardware** (not in the bundle; versions recorded at the delivery check)

| ID | Component | Vendor |
|---|---|---|
| H1 | NX-OS on sw01 (Cisco Nexus N93180YC-FX3), with the NX-OS Essentials license | Cisco |
| H2 | BIOS/UEFI and BMC firmware on gpu01 and svc01-03 | Thinkmate / board vendor |
| H3 | NIC firmware (Intel E810-XXVDA2, Broadcom N225P), NVMe firmware, GPU VBIOS | Intel, Broadcom, drive vendor, NVIDIA |
| H4 | Geist PDU and Liebert CRV firmware (lab-owned, listed for completeness) | Vertiv |

## 8. Outbound connections and how they are switched off

The lab has no internet, but these components try to reach it by default. Each is turned off in the bundle.
The sandbox rehearsal records every outbound attempt (tcpdump plus CoreDNS logging) and must show none
([11](../software/11-sandbox-bringup-plan.md), C16).

| Component | Default behavior | Setting in the bundle |
|---|---|---|
| Open WebUI (A3) | Downloads models, sends telemetry | `OFFLINE_MODE=true`, `SCARF_NO_ANALYTICS`, `DO_NOT_TRACK`, `ANONYMIZED_TELEMETRY=false`; Ollama and Pipelines off |
| LiteLLM (A2) | Fetches its price list from GitHub at start | `LITELLM_LOCAL_MODEL_COST_MAP=True`. Prisma engine download at migration: to confirm in the sandbox. |
| vLLM (A1) | Downloads tokenizer vocabularies | `TIKTOKEN_ENCODINGS_BASE` points at the shipped copy (M4) |
| Continue (C5) | Anonymous telemetry | `allowAnonymousTelemetry: false` in each user's config (user-side setting) |
| Trivy (S1) | Updates its databases | Run with `--skip-db-update --skip-java-db-update --offline-scan` |
| RKE2 (K1) | Ships `rke2-security-responder`, which looks to be SUSE's version-reporting component | To check: what it contacts, and whether to turn it off in the RKE2 config. The sandbox tripwire (C16) shows whether it tries. |

## 9. Machine-readable records in every bundle

This document is the overview. For each sealed bundle, these files are the exact record:

| File | Contents |
|---|---|
| `package/IMAGES.txt` | Every container image in the Zarf package |
| Zarf package SBOMs | A Syft SBOM for every image, generated by `zarf package create` (view with `zarf package inspect --sbom-out`) |
| `scanner/reports/` | Trivy report per image, `SUMMARY.txt` (counts by severity), `IMAGE-DIGESTS.txt` |
| `clients/RESOLVED.txt`, `clients/SUPPORT.txt` | Every analyst wheel and the VSIX, and which Python versions are covered |
| `MODELS.txt`, `models/*/SHA256SUMS` | Model commits and per-file checksums |
| `VERSIONS.env`, `MANIFEST.txt`, `SOURCE_COMMIT` | Pinned versions, what each step pulled and from where, the repo commit that built it |
| `SHA256SUMS` + `.sig` or `.asc` | Checksum of every file, signed |

If the Cyber team needs a standard format (CycloneDX or SPDX), we can add a CycloneDX export for every image
and the wheel set to `45-scan-images.sh`.

## 10. Decisions for the Cyber team

All decisions are in one place: the [decision register](README.md). Those raised by this list:

| Register ID | Topic |
|---|---|
| S6 | Upstream images, not Iron Bank |
| S10 | Bundle signing: cosign or GPG, key custody |
| S4, L1, S11 | Secure Boot, OS and hardening baseline, OS packages for the driver build (dkms is in EPEL) |
| S12 | Speech-to-text: speaches (A4) or vLLM (A1) |
| S13 | Chat page image: standard (A3) or slim (A3s) |
| S14 | Licenses to note |
| S15 | `rke2-security-responder` outbound reporting |
| S16 | Known security shortcuts (W8 to W11) |
| S17, S18, S19 | For information: Traefik ingress, NVIDIA driver branch R620, scan results |

Tika (A6) stays on the 3.x line until the upload checks pass on 4.x in the sandbox. That is our call, not a
Cyber decision.

## 11. Not in this phase (coming later)

Listed so the Cyber team can plan reviews. None of this is in the phase 1 bundle.

| Item | Notes |
|---|---|
| Big Bang (Platform One): Harbor, GitLab, Argo CD, Keycloak, Prometheus/Grafana | Iron Bank images; Harbor replaces the Zarf registry |
| JupyterHub, Dagster, Evidence, metrics plugins | The metrics pipeline ([`metrics_architecture.html`](../../metrics_architecture.html)) |
| Reranker model `BAAI/bge-reranker-v2-m3` | Better document search ([11](../software/11-sandbox-bringup-plan.md), W20) |
| Typed decision model (Cloudflare Clef) with SGLang | Deferred. Ships a Python code file that runs at load time; needs ISSM review (S9). |
