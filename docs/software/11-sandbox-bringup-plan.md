# 11. Sandbox bring-up plan, and what is left before the air gap

**Track:** Software (building, moving, and installing the SI service). Security decisions are in the [Cyber Security package](../cyber/README.md).

**Goal:** when the SI workbench and its delivery pipeline are started in an offline sandbox, they come up and
*work*, not just show pods running. Then, list the weak spots, gaps, and shortcuts that must be dealt with
before the bundle crosses into the lab.

**Scope.**

| In scope | What it is |
|---|---|
| SI workbench | Model server (vLLM), gateway (LiteLLM, per-user keys), chat page (Open WebUI), speech-to-text (Whisper), and analyst access from Jupyter AI, VS Code (Continue), MATLAB, and Python |
| Pipeline functions it depends on | The delivery pipeline (pull, seal, verify, deploy) and the platform under the apps: RKE2, Zarf registry, local-path storage, CloudNativePG |
| Not built yet | The metrics pipeline itself (Dagster, readers, metric plugins, Evidence pages), JupyterHub, GitLab, Harbor, Argo CD. They exist only in `metrics_architecture.html`. Section 6 says what a minimal sandbox slice would be. |

The sandbox is the rehearsal VM from [04](04-prototype-plan.md) (P1), made stricter and given a stand-in model
so the request path can be tested without a GPU.

Status labels used below: **Confirmed** = checked against the code, the rendered charts, or the upstream
repository on 2026-11-04. **Likely** = known upstream behavior; the sandbox check in section 4 confirms or
clears it.

---

## 1. Fix before the first pull

These would fail in the sandbox, or worse, pass the sandbox and fail in the lab.

| # | Problem | Status | Fix |
|---|---|---|---|
| F1 | **Whisper ships with no weights.** `Systran/faster-whisper-large-v3` stores its weights in `model.bin` (3.09 GB, CTranslate2 format, not pickle). `30-pull-models.sh` excludes `*.bin`, so the download contains only config files. `intake/verify.sh` would also reject the file. The rehearsal skips Whisper, so this would first show up in the lab. | Confirmed | Add a format column to `models.txt` (`safetensors` or `ct2`). For `ct2` models, allow exactly `model.bin` and check it against the published SHA-256. Get ISSM agreement that CTranslate2 binaries meet the intent of A17 (no executable pickle). |
| F2 | **gpt-oss may download its tokenizer vocabulary at startup.** vLLM loads gpt-oss through `openai_harmony`, which fetches `o200k_base.tiktoken` from the internet unless a local copy is configured. The rehearsal runs 0 model copies, so it never sees this. | Likely | Pull the `.tiktoken` files into `models/tiktoken/`, mount them, and set `TIKTOKEN_ENCODINGS_BASE` in `vllm.yaml`. Section 4, check C3, proves it without a GPU. |
| F3 | **LiteLLM may reach the internet at startup.** It fetches its model price list from GitHub. Its database migration step (`prisma_migration.py`) may try to fetch Prisma engine files. | Likely | Set `LITELLM_LOCAL_MODEL_COST_MAP=True` in `values/litellm.yaml`. If the migration Job fails offline in the sandbox, switch to the LiteLLM image variant that ships the Prisma files already generated. |
| F4 | **The pinned versions are about 15 months old.** `versions.env` still says to bump before the first pull. RKE2, the GPU Operator, the driver branch, and vLLM all need current releases with RTX PRO 6000 Blackwell support. | Confirmed | Run `01-check-latest.sh`, bump, and commit. After bumping RKE2, check which ingress controller it ships by default. Both Ingresses use class `nginx`. |
| F5 | **Client wheels cover Python 3.11 only.** [07](07-open-questions.md) L3 says analysts run Python 3.9 to 3.13 on Windows and Linux. `jupyter-ai` is unpinned and Continue is pinned to `latest`, so two pulls can give different results. | Confirmed | Loop `50-pull-client-tools.sh` over 3.9 to 3.13. Pin `jupyter-ai` and `CONTINUE_VSCODE_VERSION`. Check which Jupyter AI major version works with the JupyterLab versions analysts have. |
| F6 | **RKE2 needs a default route.** A VM with no network interface, or with no default route, stops RKE2 from starting. That would be a false failure in the sandbox. | Confirmed (RKE2/K3s air-gap docs) | Give the VM an isolated network with a default route to a host that does not forward (section 2). |
| F7 | **The chat page cannot use Whisper or document upload offline.** With `OFFLINE_MODE`, Open WebUI won't download its built-in speech-to-text model or its document embedding model. | Likely | Point Open WebUI speech-to-text at the gateway (`AUDIO_STT_ENGINE=openai`, gateway URL). Serve an embedding model through the gateway and point the chat page's document upload at it. |
| F8 | **Long requests can time out at the ingress.** ingress-nginx closes requests after 60 s by default. MATLAB `webwrite` (no streaming, 120 s timeout) and long reasoning answers will hit it. | Likely | Add `nginx.ingress.kubernetes.io/proxy-read-timeout: "600"` and `proxy-send-timeout: "600"` to both Ingresses. |

### Fixed in `delivery/` on 2026-11-06 (not yet run end to end)

| Item | Change | Tested so far |
|---|---|---|
| F1 | `models.txt` has a format column. Whisper is `ct2`: its `model.bin` is pulled and kept, but only if it starts with the CTranslate2 header. `verify.sh` accepts that one file and still refuses every other pickle-style file. | Header confirmed on the real file. `verify.sh` passes a CTranslate2 file and refuses a pickle file in its place, and refuses a `.bin` in the safetensors model. |
| F2 | `30-pull-models.sh` pulls `o200k_base` and `cl100k_base` (checked against tiktoken's own SHA-256). `vllm.yaml` sets `TIKTOKEN_ENCODINGS_BASE=/models/tiktoken`. | Checksums confirmed. Sandbox check C3 still has to prove vLLM uses them. |
| F3 | `LITELLM_LOCAL_MODEL_COST_MAP=True` | Chart renders it into the gateway and its migration Job. The Prisma question stays open until the sandbox runs. |
| F4 | **Bumped 2026-11-09** against upstream (see `versions.env` for each reason): RKE2 v1.37.2, Zarf v0.89.0, GPU Operator v26.7.2, driver 580.196.07 (R580 long-term branch), vLLM v0.32.0, LiteLLM v1.108.4-lts (chart 1.89.2), Open WebUI v0.12.5 (chart 17.5.0), speaches 0.8.3, CloudNativePG chart 0.29.1, PostgreSQL 18.6, Trivy 0.76.2, local-path v0.0.37, busybox 1.38.0. RKE2 v1.37 has no ingress-nginx (retired upstream March 2026), so both Ingresses moved to Traefik, and `deploy.sh` sets `ingress-controller: traefik` on the servers. The Open WebUI chart's default Redis is turned off. | Driver and GPU Operator checked against NVIDIA's 26.7 component matrix; image tags and chart versions confirmed to exist; the values keys we set are unchanged in the new LiteLLM and Open WebUI charts. **Not rendered with helm and not rehearsed** (this machine has no helm and is ARM). |
| F5 | Wheels pulled for Python 3.9 to 3.15 into one folder per OS. Pinned `jupyter-ai==2.31.7`, `langchain-openai==0.3.35`, `openai==2.48.0` (plus `langchain` and `langchain-core`, so pip fails fast). A version too new for Jupyter AI's packages gets the OpenAI client only, listed in `clients/SUPPORT.txt`. Continue pinned to 2.1.0. Anaconda steps (a separate virtual environment on their own Python) in [06](06-software-delivery.md); package route question added as [07](07-open-questions.md) L6. | Resolves on 3.9 to 3.14, Linux and Windows. On 3.15 (Nov 2026), `PyYAML`, `frozenlist`, `zstandard`, and on Windows `faiss-cpu` have no wheels yet, so 3.15 gets the OpenAI client only, which resolves. Fallback logic tested with a stub. Continue 2.1.0 exists for both. |
| F6 | Sandbox setup, section 2 | |
| F7 | Chat page speech-to-text goes to `whisper` through the gateway. Document upload is on: new `embed` service (Text Embeddings Inference on CPU, `snowflake-arctic-embed-l-v2.0`) behind the gateway as `arctic-embed`; chat page uses it with a `query: ` prefix, batches of 32, 2,000-character pieces, 10 per question. Per file, analysts can switch to "Using Entire Document". Text extraction and OCR: new `tika` service (Apache Tika 3.3.3.0, full image with Tesseract) on the service nodes; PDF pages with too little text are OCR'd. | Setting names checked in Open WebUI 0.6.22 and TEI 1.9.4 source; model listed as supported by TEI; charts render. Not run. |
| (found while doing F7) | vLLM and Whisper images were missing from `package/IMAGES.txt`, so step 45 didn't scan them and C2 couldn't check them. Each plain-manifest image now has its own list in `20-build-zarf-package.sh`. | Template renders |
| F8 | Was nginx annotations. **Now Traefik (2026-11-09):** it has no response-time limit and no body-size limit by default, so no annotations are needed. Its one default limit is 60 s to receive a request. The chat page enforces its own 50 MB file limit. | Traefik v3.7 defaults checked in its docs. Sandbox C11b (upload) and C14 (MATLAB, non-streaming) prove it. |
| W5 | `90-seal.sh` and `verify.sh` refuse unsigned bundles (`ALLOW_UNSIGNED=1` for throw-away tests only) | Both refusals tested |
| W6, part of W7 | New `45-scan-images.sh`: Trivy report per image, `SUMMARY.txt`, `IMAGE-DIGESTS.txt` in `scanner/reports/` | Summary tested on a sample report; Trivy not run (this machine is ARM) Harbor's built-in scanner takes over the in-lab scanning when Harbor arrives with Big Bang. This build-side scan stays as the check before transfer (the Delivery view lists "SBOM and scan results" in the release package), so a critical finding doesn't cost a transfer cycle. |
| W12, part | Continue telemetry setting added to [06](06-software-delivery.md) | |
| W17 | Port-forward waits for the gateway to answer. Join token read from a prompt or a file and given to RKE2 as `token-file`. One `MANIFEST.txt` line per key. Sealing refuses uncommitted changes in `delivery/`. | Manifest and dirty-tree refusal tested; RKE2 parts need the sandbox |

## 2. Build the sandbox

The host must be the **x86_64** build workstation. The Zarf, Trivy, and RKE2 downloads are amd64. Rebuild the
VMs from a script (kickstart or cloud-init) for every release so nothing carries over.

| Item | Setting | Why |
|---|---|---|
| Node VM | Same OS, version, **and hardening** as the lab ([security decisions](../cyber/README.md) L1). If the lab uses STIG: SELinux enforcing, FIPS mode, fapolicyd, `noexec` on `/tmp`. 12 vCPU, 48 GB RAM, 400 GB disk. | A plain OS install hides the failures that a STIG'd host causes (SELinux policy for RKE2, binaries blocked by fapolicyd). More CPU and RAM than doc 04 because the stand-in model runs on CPU. |
| Bundle disk | Attached **read-only** | Proves nothing in the install writes into the bundle |
| Client VMs | One Windows and one Linux, with Python 3.9 and 3.13, VS Code, and MATLAB if a license is free. No internet. | Analysts are mostly on Windows (L3). This is the only way to test the workbench side. |
| Network | Host-only network (example `10.99.0.0/24`), no NAT. The host is `10.99.0.1` and is the default route, but it does not forward traffic. | RKE2 gets its default route, and nothing reaches the internet |
| DNS | dnsmasq on the host, or `/etc/hosts` on every VM: `chat.sandbox.lab` and `api.sandbox.lab` point to the node | Same name-based setup as the lab |
| Certificates | A sandbox CA, imported into the client VMs' trust stores, issues one certificate for both names (commands below) | Rehearses the lab CA steps on the clients, which a self-signed certificate skips |
| Egress tripwire | `tcpdump -ni <host-only bridge> 'not dst net 10.99.0.0/24'` on the host, plus the CoreDNS `log` plugin | Every attempt to reach the internet (telemetry, a runtime download) is recorded, even when the component fails over quietly |

```bash
# Sandbox CA and one certificate for both names
openssl req -x509 -newkey rsa:3072 -nodes -days 90 -keyout ca.key -out ca.crt -subj "/CN=SI Sandbox CA"
openssl req -newkey rsa:3072 -nodes -keyout si.key -out si.csr -subj "/CN=chat.sandbox.lab"
openssl x509 -req -in si.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 90 -out si.crt \
  -extfile <(printf 'subjectAltName=DNS:chat.sandbox.lab,DNS:api.sandbox.lab')
```

**Rehearsal add-on, kept separate from the lab bundle.** A small, separately built Zarf package on its own disk,
never sealed into the lab bundle:

- **Stand-in model.** vLLM's CPU image serving a small approved safetensors model (for example a 0.5B instruct
  model) under `--served-model-name=gpt-oss-120b`. The gateway config, keys, and client settings are then
  identical to the lab. This tests the request path, not the GPU image.
- **Whisper on CPU.** The CPU tag of the same speaches version, loading the **real** `faster-whisper-large-v3`
  from `/var/lib/models`. This proves F1 is fixed.

## 3. Deploy (exactly as the lab will)

From the read-only bundle disk, as root on the node VM:

```bash
COSIGN_PUB=cosign.pub ./intake/verify.sh /mnt/bundle    # must print PASS; unsigned bundles are refused
./intake/deploy.sh server-init
./intake/deploy.sh models
./intake/deploy.sh platform
./intake/deploy.sh apps --chat-host chat.sandbox.lab --api-host api.sandbox.lab \
    --tls-cert si.crt --tls-key si.key --rehearsal
./intake/deploy.sh gateway-key
# then deploy the rehearsal add-on package from its own disk
```

Skip `driver`. There is no GPU.

## 4. Checks: what "it works" means

A check script (proposed as `validate/smoke-test.sh`) runs these and prints PASS or FAIL for each. Every check
must pass before the bundle goes on the transfer drive.

**Platform**

| # | Check | How |
|---|---|---|
| C1 | All pods Running or Completed. No `ImagePullBackOff`. | `deploy.sh status` |
| C2 | Every image in `package/IMAGES.txt` is in the Zarf registry | `zarf tools registry catalog`, compared with `IMAGES.txt` |
| C3 | **The real vLLM image loads gpt-oss's tokenizer and vocabulary offline** (F2) | One-off pod: the bundle's vLLM image, `/var/lib/models` mounted, runs `AutoTokenizer.from_pretrained('/models/gpt-oss-120b')` and `load_harmony_encoding(HARMONY_GPT_OSS)`. No GPU needed. |
| C4 | Trivy scans one image offline with the shipped database | `trivy image --skip-db-update --skip-java-db-update --offline-scan ...` |

**Gateway and model path**

| # | Check | How |
|---|---|---|
| C5 | Gateway health and model list | `GET /health/liveliness`; `GET /v1/models` lists `gpt-oss-120b` |
| C6 | Per-user key works, streaming and non-streaming | `deploy.sh user-key smoke`, then a chat completion both ways |
| C7 | A revoked key is refused | Delete the key; the next call returns 401 |
| C8 | The request is logged against the user | A row for `smoke` in LiteLLM's spend log table in PostgreSQL |
| C9 | Light load holds | `validate/llm-load-test.py --users 4 --ca ca.crt` against the stand-in model |
| C10 | Whisper transcribes through the gateway | `POST /v1/audio/transcriptions` with a short WAV file |
| C10b | Embeddings through the gateway | `POST /v1/embeddings` with model `arctic-embed` returns a 1,024-number vector. Runs in the rehearsal VM (CPU). |

**Workbench (from the client VMs)**

| # | Check | How |
|---|---|---|
| C11 | Chat page | HTTPS opens with no certificate warning; create the admin; ask a question; answer streams. Restart the pod; history is still there. |
| C11b | Document upload | Attach a 100-page PDF and a 5 MB log; time the indexing. Ask about a fact on one page only; the answer cites it. Switch the file to "Using Entire Document" and ask for a summary. Admin Panel, Settings, Documents shows engine `openai`, model `arctic-embed`, and a non-empty key (W23). Upload a scanned (image-only) 20-page PDF: its text is found, and record how long it takes. |
| C12 | Jupyter AI | `pip install --no-index --find-links wheels-<os>` on Python 3.9 **and** 3.13; configure per [06](06-software-delivery.md); one chat turn |
| C13 | VS Code | Install the Continue VSIX offline; configure; one chat turn. Telemetry is off in the config. |
| C14 | MATLAB | The [06](06-software-delivery.md) `webwrite` example. If no license is free, run the same request in PowerShell `Invoke-RestMethod`. |
| C15 | Python client | `openai` client with `SSL_CERT_FILE=ca.crt` |

**Resilience and the air gap**

| # | Check | How |
|---|---|---|
| C16 | **The egress tripwire log is empty**, or every entry is explained and switched off | tcpdump and CoreDNS logs from the whole run |
| C17 | Reboot the node VM; everything returns with no manual steps | `deploy.sh status`, then C5 and C11 |
| C18 | Re-running `deploy.sh apps` (the update path) changes nothing and breaks nothing | Run it twice |
| C19 | Rollback works | Deploy the previous bundle's `apps` over this one; C5 and C11 still pass. LiteLLM schema migrations may not go backwards, so this tests the rollback promise in [04](04-prototype-plan.md) P3. |

## 5. What the sandbox cannot prove

The GPU path is still not covered: driver build against the lab kernel, the GPU Operator on RKE2, the
`nvidia` runtime class, vLLM's gpt-oss (MXFP4) kernels on RTX PRO 6000 Blackwell, 3 copies plus Whisper on 4
GPUs, and real throughput. C3 removes the vocabulary download risk, but not the others. See W1.

## 6. Metrics pipeline: the minimal slice for a later sandbox

None of this code exists yet. When it does, the smallest slice worth rehearsing the same way is: a directory
watcher on a test folder, then Dagster registering the dataset in PostgreSQL, then one reader that writes
Parquet, then one metric plugin with its evals, then results in PostgreSQL, then one static Evidence page, with
JupyterHub reading the Parquet. Each becomes a Zarf component, and the C-checks gain one "drop a golden
dataset, see the metric on the page" test.

---

## 7. Weak spots, gaps, and shortcuts to deal with before the air gap

**Before transfer** = the bundle should not cross until this is fixed or formally accepted.
**Before users** = may cross, but fix before analysts are given access.
**Later** = a known shortcut of phase 1, written down so it is a choice, not a surprise.

### Untested or will break

| ID | Item | When | What to do |
|---|---|---|---|
| W1 | **The GPU path is first exercised in the lab.** Doc 04 accepts this, but it is now the largest single risk: a new GPU generation, a new driver branch, and a quantized model format, all untested together. | Before transfer | Decide now, not after a failure: (a) a single-GPU Blackwell test machine from the ~$48k left ([04](04-prototype-plan.md), section 4), or (b) ask Thinkmate to run our vLLM image and model during factory burn-in. At minimum, find published evidence of the exact vLLM + driver + gpt-oss combination working on RTX PRO 6000. |
| W2 | F1 to F8 above | Before transfer | Section 1 |
| W3 | **OS packages come from a lab mirror that may not exist** ([security decisions](../cyber/README.md) L1 is open). The driver needs gcc, make, and kernel headers for the exact running kernel. SELinux needs `rke2-selinux` and `container-selinux`. Also rsync and openssl. | Before transfer | If there is no mirror, add these RPMs to the bundle, matched to the lab's kernel, and test them in the sandbox. Secure Boot (S4) adds module signing. |
| W4 | **The sandbox OS must match the lab's hardening.** Otherwise the sandbox passes and the lab fails. | Before transfer | Section 2. If L1 is still open, rehearse with the strictest likely baseline (RHEL 9 STIG). |

### Security shortcuts

| ID | Item | When | What to do |
|---|---|---|---|
| W5 | **An unsigned bundle passes intake.** `verify.sh` only warns. | Before transfer | Make a signature required in `verify.sh`. Agree key custody and how the public key gets into the lab with the ISSM. |
| W6 | **No vulnerability scan results in the bundle.** Trivy and its database are shipped, but nothing scans. The Delivery view promises "SBOM and scan results". | Before transfer | Scan every image in `IMAGES.txt` at build time. Put the reports in the bundle and review them before sealing. |
| W7 | **Upstream images, not Iron Bank** (S6 open). Pins are tags, not digests. | Before transfer (ISSM answer) | Get S6 answered. Record each image's digest in `MANIFEST.txt` from the Zarf SBOMs. Swap to Iron Bank where it exists ([06](06-software-delivery.md), section 6). |
| W8 | **No network policies.** The architecture says default-deny. Today any pod can call vLLM directly and bypass the gateway's keys and logging. | Before users | Default-deny in `si`. Allow only gateway to vLLM and Whisper, chat page to gateway, gateway to PostgreSQL, and ingress to the chat page and gateway. |
| W9 | **Sign-in is keys plus local accounts.** The first person to open the chat page becomes admin. Keys are handed out by hand. The master key never rotates. | Before users | Create the admin during install, then turn off open sign-up. Write down key issue, revoke, and rotate steps. Keycloak SSO is later (Big Bang). |
| W10 | **Audit logging falls short of the architecture.** LiteLLM logs who called and how much, not the request and response text. "Requests, responses" is in the Security view. | Before users | ISSM decides what must be kept and for how long. Then turn on prompt and response logging, or document why not. |
| W11 | **No RKE2 CIS profile, no pod security enforcement** | Later, ISSM may require before users | Turn on `profile: cis`, exempt the GPU Operator and storage namespaces, and rehearse. Expect pods to need security-context changes. |
| W12 | **Telemetry off-switches are set, not proven** | Before transfer | C16 proves it. Add Continue's `allowAnonymousTelemetry: false` to the client instructions. |

### Reliability and operations

| ID | Item | When | What to do |
|---|---|---|---|
| W13 | **No backups.** Chat history (one local-path volume), the gateway database, and keys have no backup. CloudNativePG has 3 copies but no point-in-time backups. | Before users | A scheduled PostgreSQL dump and an Open WebUI data copy to the lab NFS share. Velero comes later. |
| W14 | **The Zarf registry is one pod on one node's local disk.** If that node fails, rescheduled pods can't pull images. | Later (Harbor) | Write down the recovery: re-run `zarf init` and redeploy the package. Harbor replaces it with Big Bang. |
| W15 | **No monitoring or alerting.** The DCGM exporter runs, but nothing collects it. `deploy.sh status` is the only view. | Before users | A minimal Prometheus and Grafana, or at least a scheduled status check that someone reads. |
| W16 | **One GPU server.** gpu01 down means SI down. | Accepted | Write it into the service description users get |
| W17 | **Small script weak spots.** `deploy.sh` waits a fixed 3 s for its port-forward. The join token is passed in the environment and lands in shell history. `MANIFEST.txt` gets duplicate lines on re-runs. Sealing doesn't refuse uncommitted changes. | Before transfer | Wait until the port-forward answers. Read the token from a file. Reset the manifest per run. Refuse to seal from a dirty working tree. |
| W18 | **Rollback across LiteLLM database migrations is unproven** | Before transfer | C19 |

### Workbench gaps

| ID | Item | When | What to do |
|---|---|---|---|
| W19 | **No server-side notebooks.** Phase 1 assumes analysts can `pip install` on their own lab machines. Managed lab desktops often block that. | Before users | Ask lab IT now whether analysts may install Python packages. If not, bring JupyterHub forward from the later phase. |
| W20 | **Document indexing runs on CPU.** Fine for questions; a large upload takes about a minute (estimate, not measured). No reranker, so exact terms like test IDs can rank below looser matches. OCR of a long scan takes minutes and can pass the 10-minute request limit. Tika ships English and a few European OCR languages only. Spreadsheets and CSVs get cut into text pieces, so totals and trends over a large table come out wrong; that work belongs in Jupyter. | Sandbox (timing), first lab week (real load) | Time C11b. If slow, split the Whisper GPU with MIG and move the embedding model there. Add `BAAI/bge-reranker-v2-m3` (safetensors, Apache 2.0) with hybrid search. Time OCR in C11b; if long scans time out, raise the chat ingress timeout or have analysts split them. Tell analysts to analyze tables in Jupyter. |
| W23 | **Chat page settings are copied into its database on first start.** If the gateway key isn't there yet, document upload and chat can keep an empty key after `gateway-key`. Vectors live on the chat page's volume (Chroma), not in PostgreSQL. | Sandbox | C11b checks the key. Later, move the chat page's data and vectors into PostgreSQL (pgvector is already enabled), which also puts them under the database's failover. |
| W21 | **gpt-oss is a reasoning model.** How Jupyter AI and Continue show `reasoning_content` varies by version, and the stand-in model can't show it. | First lab week | Check C12 and C13 again against the real model in the lab |
| W22 | **The metrics pipeline and the in-lab change loop don't exist yet.** No GitLab, Runner, Argo CD, Dagster, plugins, or golden datasets. On day 1, analysts can talk to SI but can't use it to build and deploy metric plugins as the architecture describes. | Later | Section 6. Plan this as the next release, not part of phase 1. |

## 8. Order of work

1. ~~Fix F1 to F8, W5, W6, and W17~~ (done except F6, see section 1). F4 bumped 2026-11-09: render the charts and rehearse.
2. Script the sandbox VMs (section 2) and build the rehearsal add-on.
3. Write `validate/smoke-test.sh` (section 4).
4. Pull, seal, rehearse. Repeat until C1 to C19 pass and the tripwire log is empty.
5. In parallel: get L1, S4, S5, S6, and W19 answered, and decide W1.
6. Only then copy the bundle to the transfer drive.
