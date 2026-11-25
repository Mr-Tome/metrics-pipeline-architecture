"""Build docs/software/5-staging-artifacts.md: every artifact the bring-up scripts fetch, where it ends up,
and whether it matches the ISSM list.

Reads the pins the scripts use (delivery/versions.env, models.txt, os-packages.txt, convert-requirements.txt,
staging/addon-versions.env) and the ISSM list (docs/cyber/16-sbom-phase-0-1.csv).
Nothing here changes what the scripts do or what the ISSM sees; it only reports.

Usage: python3 -I docs/diagrams/build_staging_artifacts.py .   (from the repository root, after changing any
of the files above). Run build_phased_sbom.py first if the ISSM list changed.
"""
import re
import sys
from pathlib import Path

repo = Path(sys.argv[1])
sys.path.insert(0, str(repo / "docs/diagrams"))
d = repo / "delivery"


def env(path):
    return dict(re.findall(r'^([A-Z0-9_]+)="([^"]*)"', path.read_text(), re.M))


def issm_list():
    """The ISSM list rows (docs/cyber/16-sbom-phase-0-1.csv), keyed by ID."""
    import csv
    with open(repo / "docs/cyber/16-sbom-phase-0-1.csv", newline="") as f:
        return {r["ID"].strip(): {k: v.strip() for k, v in r.items()} for r in csv.DictReader(f) if r["ID"].strip()}


V = env(d / "versions.env")
A = env(d / "staging/addon-versions.env")
WB = issm_list()
BUNDLE, BUILD, STAGING, LATER = "Lab bundle", "Build side only", "Staging only", "Later phase (left out)"


def check(sbom_id, pin):
    """Compare one pin with the ISSM list row."""
    if not sbom_id:
        return "Not on the ISSM list (not delivered)"
    r = WB.get(sbom_id)
    if not r:
        return f"Not in the ISSM list ({sbom_id} is a later phase)"
    text = " ".join(r.values())
    if r["Phase"].endswith("(Currently considering)"):
        return f"**Differs:** the ISSM list lists {sbom_id} as an option; the scripts deliver it"
    missing = [t for t in pin.split() if t not in text]
    return "Same" if not missing else f"**Differs:** the ISSM list does not show {', '.join(missing)}"


rows = []  # (group, artifact, pin, where, sbom id, check)
img = lambda ref: ref.split(":", 1)[1] if ":" in ref else ref
lab = [
    ("Kubernetes", "RKE2 (binaries, air-gap images, installer)", V["RKE2_VERSION"], "K1"),
    ("Kubernetes", "local-path-provisioner", V["LOCAL_PATH_VERSION"], "K6"),
    ("Kubernetes", "busybox", img(V["BUSYBOX_IMAGE"]), "K7"),
    ("Kubernetes", "Zarf CLI and init package", V["ZARF_VERSION"], "K8"),
    ("GPU", "NVIDIA driver (.run)", V["NVIDIA_DRIVER_VERSION"], "G1"),
    ("GPU", "NVIDIA GPU Operator", V["GPU_OPERATOR_VERSION"], "G2"),
    ("Applications", "vLLM", img(V["VLLM_IMAGE"]), "A1"),
    ("Applications", "LiteLLM image and chart", f'{img(V["LITELLM_IMAGE"])} {V["LITELLM_CHART_VERSION"]}', "A2"),
    ("Applications", "Open WebUI image and chart", f'{img(V["OPEN_WEBUI_IMAGE"])} {V["OPEN_WEBUI_CHART_VERSION"]}', "A3"),
    ("Applications", "speaches (Whisper server)", img(V["WHISPER_IMAGE"]), "A4"),
    ("Applications", "Text Embeddings Inference", img(V["EMBED_IMAGE"]), "A5"),
    ("Applications", "Apache Tika", img(V["TIKA_IMAGE"]), "A6"),
    ("Applications", "CloudNativePG chart", V["CNPG_CHART_VERSION"], "A7"),
    ("Applications", "PostgreSQL", img(V["POSTGRES_IMAGE"]), "A8"),
    ("Security tools", "Trivy", V["TRIVY_VERSION"], "Sec1"),
    ("Security tools", "Trivy vulnerability databases", "", "Sec2"),
]
for g, a, pin, i in lab:
    rows.append((g, a, pin or "downloaded at pull time", BUNDLE, i, check(i, pin)))

for line in (d / "models.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    name, repo_id, rev, _layout, fmt = line.split()
    i = {"gpt-oss-120b": "M1", "faster-whisper-large-v3": "M11",
         "granite-embedding-278m-multilingual": "M10"}.get(name, "")
    what = f"{repo_id}, converted to CTranslate2 by us" if fmt == "ct2-convert" else repo_id
    rows.append(("Models", what, f"commit {rev[:8]}" if len(rev) == 40 else rev, BUNDLE, i, check(i, rev[:8])))
rows.append(("Models", "tiktoken vocabularies (o200k_base, cl100k_base)", "fixed files, SHA-256 checked", BUNDLE, "M4", "Same"))

pk = [l.split()[:2] for l in (d / "os-packages.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
for role, label in (("all", "every node"), ("gpu", "gpu01 only")):
    names = ", ".join(n for r, n in pk if r == role)
    rows.append(("OS packages", f"For {label}: {names}, and every package they depend on", "Rocky 9.9 repos, EPEL 9, Rancher, NVIDIA",
                 BUNDLE, "OS2 to OS5",
                 "**Differs:** the ISSM list says these come from a lab mirror; with no mirror the bundle carries them, with many more dependencies"))
rows.append(("Later phase", "Analyst tools: Python wheels and the Continue extension", f'Python {V["CLIENT_PYTHON_VERSIONS"]}; Continue {V["CONTINUE_VSCODE_VERSION"]}',
             LATER, "C1 to C5", "Only with WITH_CLIENTS=1. Staging leaves them out."))

rows.append(("Build tools", "Build container base image", V["BUILD_IMAGE"].split("/", 1)[1], BUILD, "", check("", "")))
rows.append(("Build tools", "Helm", V["HELM_VERSION"], BUILD, "", check("", "")))
rows.append(("Build tools", "Hugging Face CLI (huggingface_hub)", V["HF_HUB_VERSION"], BUILD, "", check("", "")))
rows.append(("Build tools", "Container OS tools: jq, skopeo, git, createrepo_c, python3.12, and others", "Rocky 9.9 repos at build time", BUILD, "", check("", "")))
for l in (d / "convert-requirements.txt").read_text().splitlines():
    m = re.match(r"([A-Za-z0-9_.-]+)==(\S+)", l)
    if m:
        rows.append(("Build tools", f"Whisper converter: {m.group(1)}", m.group(2), BUILD, "", "Not on the ISSM list (not delivered). Writes M11."))

rows.append(("Staging add-on", "vLLM CPU image", img(A["VLLM_CPU_IMAGE"]), STAGING, "", "Not on the ISSM list. Never sealed into the bundle."))
rows.append(("Staging add-on", "speaches CPU image", img(A["WHISPER_CPU_IMAGE"]), STAGING, "", "Not on the ISSM list. Never sealed into the bundle."))
rows.append(("Staging add-on", f'Stand-in chat model: {A["STANDIN_REPO"]}', f'commit {A["STANDIN_COMMIT"][:8]}', STAGING, "", "Not on the ISSM list. Never sealed into the bundle."))

# Items on the ISSM list that the scripts do not fetch
fetched = {r[4] for r in rows}
skipped = [(i, WB[i]) for i in WB if i not in fetched and not i.startswith(("OS", "H", "F")) and i not in ("K2", "K3", "K4", "K5", "K9")]

out = ["# 5. Staging artifact list: what the bring-up scripts fetch", "",
       "**Track:** Software. **Generated** by `docs/diagrams/build_staging_artifacts.py` from the pin files in",
       "`delivery/` and the ISSM list. Do not edit by hand.", "",
       "Every artifact the scripts download, where it ends up, and whether it matches what the ISSM has. Three places:", "",
       f"- **{BUNDLE}:** sealed into the signed bundle and installed in the lab. Should match the ISSM list.",
       f"- **{BUILD}:** used on the build workstation (or VM1 in staging) to make the bundle. Never crosses.",
       f"- **{STAGING}:** the staging add-on for the VMs with no GPU ([Staging runbook](4-staging-runbook.md)). Never crosses.", "",
       "A **Differs** row is a place where the scripts and the ISSM list disagree. Each one is either a decision we",
       "are waiting on or an update to send for the ISSM list.", "",
       "| Group | Artifact | Pin | Where it ends up | ISSM ID | Against the ISSM list |", "|---|---|---|---|---|---|"]
for g, a, pin, where, i, c in rows:
    out.append(f"| {g} | {a} | {pin} | {where} | {i} | {c} |")
out += ["", "## On the ISSM list but not fetched by the scripts", "",
        "Inside the RKE2 image tarball (K2 to K5, K9 with K8), on the hardware (H), our own scripts (F), and the OS itself",
        "(OS1) are left out of this check. The rest:", "",
        "| ISSM ID | Component | Phase on the ISSM list | Why the scripts don't fetch it |", "|---|---|---|---|"]
WHY = {"M2": "Replaced by M11 under the whole-lineage USA-only reading (S22)",
       "M3": "Replaced by M10 under the whole-lineage USA-only reading (S22)",
       "M5": "Option; M11 is converted from M6", "M6": "Its weights are fetched and converted into M11 (build side only)",
       "A3.1": "Option; the standard image (A3) is used for now (S13)", "A4.1": "Option; speaches (A4) is used (S12)"}
for i, r in skipped:
    out.append(f"| {i} | {r['Component']} | {r['Phase']} | {WHY.get(i, '')} |")
out.append("")
(repo / "docs/software/5-staging-artifacts.md").write_text("\n".join(out))
print(len(rows), "artifacts;", sum("Differs" in r[5] for r in rows), "differ;", len(skipped), "on the list but not fetched")
