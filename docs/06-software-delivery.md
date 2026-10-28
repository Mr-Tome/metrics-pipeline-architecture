# 06. Software delivery: pulling, moving, and installing

This follows the **Delivery** view in `FUTURE_NEED_TO_WORK_metrics_architecture_with_Sec_Dep.html`:

1. A connected build environment pulls everything.
2. It packs everything into one sealed release bundle.
3. The bundle moves by the approved media process to staging.
4. After staging sign-off, the same bundle moves to the lab.

The scripts are in [`delivery/`](../delivery) and [`validate/`](../validate).

## 1. What the bundle contains

| Folder | Contents | Script |
|---|---|---|
| `rke2/` | RKE2 Kubernetes air-gap images, binaries, installer, and local-path storage (as image tarballs) | `10-pull-rke2.sh` |
| `zarf/` | Zarf CLI and init package (in-cluster registry, image agent) | `15-pull-zarf.sh` |
| `package/` | One Zarf package with every chart and image: GPU Operator, CloudNativePG + PostgreSQL, vLLM, LiteLLM, Open WebUI, Whisper. Includes SBOMs and `IMAGES.txt`. | `20-build-zarf-package.sh` |
| `models/` | gpt-oss-120b (safetensors only), faster-whisper-large-v3, with SHA256SUMS per model | `30-pull-models.sh` |
| `scanner/` | Trivy and its vulnerability databases | `40-pull-vuln-db.sh` |
| `clients/` | Python wheels (Linux and Windows) for Jupyter AI and the OpenAI client; the Continue VS Code extension | `50-pull-client-tools.sh` |
| `nvidia-driver/` | NVIDIA data center driver installer | `60-pull-nvidia-driver.sh` |
| `intake/` | `verify.sh` and `deploy.sh`, shipped with the bundle | `90-seal.sh` |
| `SHA256SUMS` (+ `.sig` / `.asc`) | Checksum of every file, optionally signed | `90-seal.sh` |
| `MANIFEST.txt`, `VERSIONS.env`, `MODELS.txt`, `SOURCE_COMMIT` | Exactly what is inside and where it came from | all |

Expected size: roughly 120 to 200 GB. The model is about 65 GB and the images are most of the rest.

## 2. Build workstation setup (once)

Use a Linux x86_64 machine on the unclassified side with internet access and 500 GB free. Install:

| Tool | Why | Install |
|---|---|---|
| curl, jq, tar, sha256sum, python3 + PyYAML, pip | basics | OS packages (`python3-yaml`) |
| skopeo | image checks, storage image tarballs | OS package |
| helm | chart rendering | https://helm.sh/docs/intro/install/ |
| Hugging Face CLI (`hf`) | model download | `pipx install 'huggingface_hub[cli]'` |
| cosign or gpg | signing (optional) | OS package or sigstore release |

Zarf and Trivy are downloaded by the scripts.

Set credentials as environment variables. Never put them in files in this repo:

```bash
export HF_TOKEN=...            # Hugging Face read token (optional, avoids rate limits)
export REGISTRY1_USER=...      # Platform One, once Iron Bank images are added
export REGISTRY1_TOKEN=...
```

## 3. Pull a release

```bash
cd delivery
./01-check-latest.sh          # compare pins with upstream; edit versions.env, then commit it
./pull-all.sh                 # full bundle into delivery/out/<release>-<date>/
```

Useful variations:

```bash
BUNDLE_DIR=/mnt/xfer/ai-2026-11 ./pull-all.sh    # write straight to the transfer drive
SKIP="30" ./pull-all.sh                         # skip the model (already pulled)
COSIGN_KEY=~/keys/cosign.key ./90-seal.sh        # re-seal with a signature
```

Every step can be re-run. Downloads resume, and files already present are skipped. If any step
fails, fix it and run `pull-all.sh` again.

**Before the first real pull:** the pins in `versions.env` were set from known releases and are older
than the pull date. Run `./01-check-latest.sh`, bump each line to a current release, and commit. For the
RTX PRO 6000, check that the driver branch and GPU Operator release list Blackwell RTX PRO support.

**Transfer media:** the Hugging Face cache layout uses symbolic links. Format the transfer drive ext4 or
XFS, or tar the bundle first (`tar -cf bundle.tar -C out <bundle>`). exFAT and NTFS drop the links.

## 4. Install on staging or in the lab

On the receiving side, from the bundle:

```bash
./intake/verify.sh /path/to/bundle                     # must print PASS
```

Then, as root ([`delivery/intake/deploy.sh`](../delivery/intake/deploy.sh) has the full list):

| Where | Command |
|---|---|
| svc01 (or the single staging node) | `./intake/deploy.sh server-init` (prints the join token) |
| svc02, svc03 | `RKE2_TOKEN=<token> ./intake/deploy.sh server-join <svc01-ip>` |
| gpu01 | `RKE2_TOKEN=<token> ./intake/deploy.sh agent-join <svc01-ip>` |
| gpu01 | `./intake/deploy.sh driver`, then `./intake/deploy.sh models` |
| svc01 | `./intake/deploy.sh platform` |
| svc01 | `./intake/deploy.sh apps --chat-host chat.<lab-domain> --api-host api.<lab-domain> --tls-cert ai.crt --tls-key ai.key` (add `--staging` on staging) |
| svc01 | `./intake/deploy.sh gateway-key` |
| svc01 | `./intake/deploy.sh status` |

For staging with one node, run every step on stg01 and use `apps --staging`. That gives one PostgreSQL
instance and no Whisper, because the single GPU runs the language model.

What the host needs from the lab's own OS mirror (not in the bundle): gcc, make, kernel headers for the
running kernel (to build the driver), rsync, openssl, iperf3, and optionally DCGM for burn-in.

## 5. Connecting users

Give each user (or team) their own gateway key, so usage is logged per person:

```bash
./intake/deploy.sh user-key jsmith
```

| Tool | Setup |
|---|---|
| Browser | `https://chat.<lab-domain>/`. The first account created becomes the admin. |
| Jupyter | `pip install --no-index --find-links clients/wheels-linux jupyter-ai langchain-openai` (Windows: `wheels-windows`). In the Jupyter AI settings, choose an OpenAI-compatible provider, base URL `https://api.<lab-domain>/v1`, model `gpt-oss-120b`, and the user's key. |
| VS Code | Extensions, then "Install from VSIX", then `clients/continue-*.vsix`. Add a model with provider `openai`, `apiBase: https://api.<lab-domain>/v1`, model `gpt-oss-120b`, and the user's key. |
| MATLAB | See below. |
| Python scripts | `from openai import OpenAI; c = OpenAI(base_url="https://api.<lab-domain>/v1", api_key="sk-...")` |

MATLAB (no toolbox needed):

```matlab
opts = weboptions("HeaderFields", ["Authorization", "Bearer " + getenv("LAB_AI_KEY")], ...
                  "MediaType", "application/json", "Timeout", 120);
body = struct("model", "gpt-oss-120b", ...
              "messages", {{struct("role", "user", "content", "Explain this test log line: ...")}});
r = webwrite("https://api.<lab-domain>/v1/chat/completions", body, opts);
disp(r.choices(1).message.content)
```

## 6. What this phase leaves for later (and keeps)

| Later | How it builds on this |
|---|---|
| Big Bang (Harbor, GitLab, Argo CD, Keycloak, monitoring) | Installs onto the same RKE2 cluster. Harbor replaces the Zarf registry as the long-term registry. LiteLLM and Open WebUI move to Keycloak sign-in. |
| Iron Bank images | Swap image references in `versions.env` to `registry1.dso.mil/...` where Iron Bank has them. The scripts don't change. |
| Document search | PostgreSQL already has pgvector enabled. Add an embedding model to `models.txt` and an embedding deployment. |
| Renovate | Points at `delivery/versions.env` to open update merge requests (Delivery view). |
| Metrics pipeline | Runs on the same platform. See `metrics_architecture.html`. |
