"""Build docs/cyber/16-phased-sbom.csv and .md from doc 12, adding each item's phase and download link.

Usage: python3 -I docs/diagrams/build_phased_sbom.py .   (from the repository root, after editing doc 12 or this file)
After a change, check that every https link loads and every image tag exists.
"""
import re
import csv, sys
from pathlib import Path
repo = Path(sys.argv[1])
bom = {r["ID"]: r for r in csv.DictReader(open(repo / "docs/cyber/12-software-bom.csv"))}
GH = "https://github.com"
R = "v1.37.2%2Brke2r1"
P0, P1, P1o, P2, P3, P4, GR = ("0. Approvals and hardware", "1. SI chat", "1. SI chat (option for Cyber)",
                               "2. Analyst tools", "3. Platform services", "4. Metrics pipeline", "Grow (any time after 1)")
# id, phase, download URL(s) (what the scripts fetch), project page, extra note
U = [
 ("OS1", P0, "https://rockylinux.org/download (lab-provided image; RHEL: https://access.redhat.com/downloads)", "https://rockylinux.org", ""),
 ("OS2", P0, "Lab mirror. Upstream: https://dl.rockylinux.org/pub/rocky/9/ and https://dl.fedoraproject.org/pub/epel/9/ (dkms)", "https://docs.fedoraproject.org/en-US/epel/", ""),
 ("OS3", P0, "Lab mirror. Upstream: https://dl.rockylinux.org/pub/rocky/9/", "https://rockylinux.org", ""),
 ("OS4", P0, "Lab mirror. Upstream: https://dl.rockylinux.org/pub/rocky/9/ (container-selinux) and https://rpm.rancher.io/ (rke2-selinux)", "https://github.com/rancher/rke2-selinux", ""),
 ("OS5", P0, "Lab mirror. Upstream: https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/ (DCGM)", "https://github.com/NVIDIA/DCGM", ""),
 ("H1", P0, "Ships on the switch. Updates: https://software.cisco.com/download/home (Cisco account)", "https://www.cisco.com/c/en/us/products/switches/nexus-9000-series-switches/index.html", ""),
 ("H2", P0, "Ships on the servers. Updates from Thinkmate / board vendor", "https://www.thinkmate.com", ""),
 ("H3", P0, "Ships on the cards. Updates from Intel / Broadcom / drive vendor", "", ""),
 ("H4", P0, "Already in the lab", "", ""),
 ("K1", P1, f"{GH}/rancher/rke2/releases/download/{R}/rke2-images.linux-amd64.tar.zst ; {GH}/rancher/rke2/releases/download/{R}/rke2.linux-amd64.tar.gz ; {GH}/rancher/rke2/releases/download/{R}/sha256sum-amd64.txt ; https://get.rke2.io", f"{GH}/rancher/rke2/releases/tag/{R}", ""),
 ("K2", P1, "Inside the K1 image tarball", f"{GH}/rancher/rke2/releases/tag/{R}", ""),
 ("K3", P1, "Inside the K1 image tarball", f"{GH}/rancher/rke2/releases/tag/{R}", ""),
 ("K4", P1, "Inside the K1 image tarball", f"{GH}/rancher/rke2/releases/tag/{R}", ""),
 ("K5", P1, "Inside the K1 image tarball", f"{GH}/rancher/rke2/releases/tag/{R}", ""),
 ("K6", P1, "https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.37/deploy/local-path-storage.yaml ; image docker.io/rancher/local-path-provisioner:v0.0.37", "https://hub.docker.com/r/rancher/local-path-provisioner", ""),
 ("K7", P1, "image docker.io/library/busybox:1.38.0", "https://hub.docker.com/_/busybox", ""),
 ("K8", P1, f"{GH}/zarf-dev/zarf/releases/download/v0.89.0/zarf_v0.89.0_Linux_amd64 ; {GH}/zarf-dev/zarf/releases/download/v0.89.0/checksums.txt", f"{GH}/zarf-dev/zarf/releases/tag/v0.89.0", ""),
 ("K9", P1, f"{GH}/zarf-dev/zarf/releases/download/v0.89.0/zarf-init-amd64-v0.89.0.tar.zst", f"{GH}/zarf-dev/zarf/releases/tag/v0.89.0", ""),
 ("G1", P1, "https://us.download.nvidia.com/tesla/580.196.07/NVIDIA-Linux-x86_64-580.196.07.run (planned: https://us.download.nvidia.com/tesla/620.70.06/NVIDIA-Linux-x86_64-620.70.06.run)", "https://docs.nvidia.com/datacenter/tesla/", ""),
 ("G2", P1, "https://helm.ngc.nvidia.com/nvidia/charts/gpu-operator-v26.7.2.tgz ; images from nvcr.io/nvidia (full list in the bundle's IMAGES.txt)", f"{GH}/NVIDIA/gpu-operator/releases", ""),
 ("A1", P1, "image docker.io/vllm/vllm-openai:v0.32.0", "https://hub.docker.com/r/vllm/vllm-openai", ""),
 ("A2", P1, "image ghcr.io/berriai/litellm:v1.108.4-lts ; chart oci://ghcr.io/berriai/litellm-helm:1.89.2", f"{GH}/BerriAI/litellm", ""),
 ("A3", P1, f"image ghcr.io/open-webui/open-webui:v0.12.5 ; chart {GH}/open-webui/helm-charts/releases/download/open-webui-17.5.0/open-webui-17.5.0.tgz", f"{GH}/open-webui/open-webui", "One of A3 or A3s (S13)."),
 ("A3s", P1o, f"image ghcr.io/open-webui/open-webui:v0.12.5-slim ; chart {GH}/open-webui/helm-charts/releases/download/open-webui-17.5.0/open-webui-17.5.0.tgz", f"{GH}/open-webui/open-webui", "One of A3 or A3s (S13)."),
 ("A4", P1, "image ghcr.io/speaches-ai/speaches:0.8.3-cuda", f"{GH}/speaches-ai/speaches", "Server choice open (S12)."),
 ("A5", P1, "image ghcr.io/huggingface/text-embeddings-inference:cpu-1.9.4", f"{GH}/huggingface/text-embeddings-inference", ""),
 ("A6", P1, "image docker.io/apache/tika:3.3.3.0-full", "https://hub.docker.com/r/apache/tika", ""),
 ("A7", P1, f"{GH}/cloudnative-pg/charts/releases/download/cloudnative-pg-v0.29.1/cloudnative-pg-0.29.1.tgz ; image ghcr.io/cloudnative-pg/cloudnative-pg:1.30.1", f"{GH}/cloudnative-pg/cloudnative-pg", ""),
 ("A8", P1, "image ghcr.io/cloudnative-pg/postgresql:18.6-standard-trixie", f"{GH}/cloudnative-pg/postgres-containers", ""),
 ("M1", P1, "https://huggingface.co/openai/gpt-oss-120b (safetensors files only; exact commit in the bundle's MODELS.txt)", "https://huggingface.co/openai/gpt-oss-120b", ""),
 ("M2", P1, "https://huggingface.co/Systran/faster-whisper-large-v3", "https://huggingface.co/Systran/faster-whisper-large-v3", "Converter is Systran (France); see S22 and M11."),
 ("M3", P1, "https://huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0 (safetensors only)", "https://huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0", "Built on a BAAI model (China); see S22 and M10."),
 ("M4", P1, "https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken ; https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken", f"{GH}/openai/tiktoken", ""),
 ("M5", P1o, "https://huggingface.co/openai/whisper-large-v3-turbo", "https://huggingface.co/openai/whisper-large-v3-turbo", ""),
 ("M6", P1o, "https://huggingface.co/openai/whisper-large-v3", "https://huggingface.co/openai/whisper-large-v3", ""),
 ("M10", P1o, "https://huggingface.co/ibm-granite/granite-embedding-278m-multilingual", "https://huggingface.co/ibm-granite/granite-embedding-278m-multilingual", "US replacement for M3."),
 ("M11", P1o, "Made by us from M5 or M6 with the CTranslate2 converter: https://pypi.org/project/ctranslate2/", f"{GH}/OpenNMT/CTranslate2", "US-only lineage replacement for M2."),
 ("Sec1", P1, f"{GH}/aquasecurity/trivy/releases/download/v0.76.2/trivy_0.76.2_Linux-64bit.tar.gz ; {GH}/aquasecurity/trivy/releases/download/v0.76.2/trivy_0.76.2_checksums.txt", f"{GH}/aquasecurity/trivy", ""),
 ("Sec2", P1, "images ghcr.io/aquasecurity/trivy-db:2 and ghcr.io/aquasecurity/trivy-java-db:1 (fetched by trivy)", f"{GH}/aquasecurity/trivy-db", ""),
 ("F1", P1, "Ours. In the bundle (intake/), no download", "", ""),
 ("F2", P1, "Ours. In the bundle, no download", "", ""),
 ("C1", P2, "https://pypi.org/project/jupyter-ai/2.31.7/", f"{GH}/jupyterlab/jupyter-ai", ""),
 ("C2", P2, "https://pypi.org/project/langchain-openai/0.3.35/ ; https://pypi.org/project/langchain/0.3.30/ ; https://pypi.org/project/langchain-core/0.3.86/", f"{GH}/langchain-ai/langchain", ""),
 ("C3", P2, "https://pypi.org/project/openai/2.48.0/", f"{GH}/openai/openai-python", ""),
 ("C4", P2, "https://pypi.org/ (each wheel's URL is listed in clients/RESOLVED.txt at pull time)", "https://pypi.org", ""),
 ("C5", P2, "https://open-vsx.org/api/Continue/continue/win32-x64/2.1.0 ; https://open-vsx.org/api/Continue/continue/linux-x64/2.1.0", "https://open-vsx.org/extension/Continue/continue", ""),
 ("C6", P2, "Already in the lab", "https://www.mathworks.com/products/matlab.html", ""),
 ("M9", GR, "https://huggingface.co/ibm-granite/granite-embedding-reranker-english-r2", "https://huggingface.co/ibm-granite/granite-embedding-reranker-english-r2", "Better document search."),
]
EXTRA = [  # items not in doc 12 rows
 ("A4b", P1o, "Speech-to-text server option (b): whisper-asr-webservice", "v1.10.0", "ahmetoner (GitHub)", "MIT", "image docker.io/onerahmet/openai-whisper-asr-webservice:v1.10.0-gpu", f"{GH}/ahmetoner/whisper-asr-webservice", "Not OpenAI-compatible; needs an adapter (S12)."),
 ("X1", P3, "Big Bang (Platform One baseline)", "not chosen yet", "Platform One (US DoD)", "Apache-2.0", "https://repo1.dso.mil/big-bang/bigbang", "https://repo1.dso.mil/big-bang/bigbang", "Installs Harbor, GitLab, Argo CD, Keycloak, monitoring on the phase 1 cluster."),
 ("X2", P3, "Iron Bank hardened images", "per image", "Platform One (US DoD)", "per image", "https://registry1.dso.mil (Platform One account)", "https://p1.dso.mil/services/iron-bank", "Can replace phase 1 upstream images (S6)."),
 ("X3", P3, "Keycloak (sign-in for the chat page and gateway)", "not chosen yet", "CNCF / Red Hat", "Apache-2.0", f"{GH}/keycloak/keycloak/releases", "https://www.keycloak.org", "Replaces local accounts."),
 ("X4", P3, "Harbor registry", "not chosen yet", "CNCF", "Apache-2.0", f"{GH}/goharbor/harbor/releases", "https://goharbor.io", "Replaces the Zarf registry."),
 ("X5", P3, "GitLab and GitLab Runner", "not chosen yet", "GitLab Inc.", "MIT (CE)", "https://about.gitlab.com/install/", "https://gitlab.com/gitlab-org/gitlab", "In-lab change loop."),
 ("X6", P3, "Argo CD", "not chosen yet", "CNCF", "Apache-2.0", f"{GH}/argoproj/argo-cd/releases", "https://argo-cd.readthedocs.io", ""),
 ("X7", P3, "Prometheus and Grafana (monitoring)", "not chosen yet", "CNCF / Grafana Labs", "Apache-2.0 / AGPL-3.0", f"{GH}/prometheus/prometheus/releases ; {GH}/grafana/grafana/releases", "https://prometheus.io", ""),
 ("X8", P4, "Dagster (orchestration)", "not chosen yet", "Dagster Labs", "Apache-2.0", f"{GH}/dagster-io/dagster/releases", "https://dagster.io", ""),
 ("X9", P4, "JupyterHub (analyst notebooks in the cluster)", "not chosen yet", "Project Jupyter", "BSD-3-Clause", f"{GH}/jupyterhub/zero-to-jupyterhub-k8s/releases", "https://jupyter.org/hub", ""),
 ("X10", P4, "Evidence (published metric pages)", "not chosen yet", "Evidence Dev", "MIT", f"{GH}/evidence-dev/evidence/releases", "https://evidence.dev", ""),
 ("X11", P4, "Metric readers and plugins", "ours, not written yet", "Us", "", "Ours. Written and tested in the lab", "", ""),
 ("X12", GR, "Second GPU server (100 users)", "hardware", "Thinkmate", "", "Same software bundle", "", "No software change."),
]
ORDER = [P0, P1, P1o, P2, P3, P4, GR]
rows = []
for i, ph, dl, page, note in U:
    b = bom[i]
    rows.append(dict(Phase=ph, ID=i, Component=b["Component"], Version=b[[k for k in b if k.startswith("Version")][0]],
                     Supplier=b["Supplier / source"], License=b["License"], **{"Download URL": dl, "Project page": page},
                     Notes=" ".join(x for x in [note] if x)))
for i, ph, comp, ver, sup, lic, dl, page, note in EXTRA:
    rows.append(dict(Phase=ph, ID=i, Component=comp, Version=ver, Supplier=sup, License=lic, **{"Download URL": dl, "Project page": page}, Notes=note))
missing = set(bom) - {r["ID"] for r in rows}
assert not missing, missing
rows.sort(key=lambda r: ORDER.index(r["Phase"]))
cols = ["Phase", "ID", "Component", "Version", "Supplier", "License", "Download URL", "Project page", "Notes"]
with open(repo / "docs/cyber/16-phased-sbom.csv", "w", newline="") as f:
    w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(rows)
print(len(rows), "rows")

# ---------- readable version ----------
rows = list(csv.DictReader(open(repo / "docs/cyber/16-phased-sbom.csv")))
INTRO = {
 "0. Approvals and hardware": "Lab-provided or shipped on the hardware. Not in our bundle. Listed so the review covers everything that runs.",
 "1. SI chat": "The first bundle. Analysts chat with SI in a browser. This is what we ask to review first.",
 "1. SI chat (option for Cyber)": "Alternatives to phase 1 items. Cyber picks; we bring whichever is approved.",
 "2. Analyst tools": "Not in the first bundle. Jupyter, VS Code, MATLAB, and scripts reach SI through an API address with a personal key.",
 "3. Platform services": "Not chosen or pinned yet. Versions get pinned and checked when the phase is planned.",
 "4. Metrics pipeline": "Not chosen or pinned yet. Runs on the platform from phases 1 and 3.",
 "Grow (any time after 1)": "Optional additions that need no new design.",
}
def cell(s):
    s = s.replace("|", "/")
    return re.sub(r"(https://[^\s;()]+)", r"<\1>", s)
out = ["# 16. Phased software list with download links (for the ISSM)", "",
"**Track:** Cyber Security ([package index and decision register](README.md)).",
"**Status:** Draft, 2026-11-14. Every item we plan to bring into the lab, by phase, with the exact place it is",
"downloaded from. The same list as a spreadsheet: [16-phased-sbom.csv](16-phased-sbom.csv). Licenses and",
"details: [12](12-software-bom.md) (software) and [13](13-model-bom.md) (models).", "",
"Every link was checked on 2026-11-14 (container image tags against their registries). \"image\" means a",
"container image pulled from that registry address. Nothing is downloaded inside the lab: every item is",
"downloaded on the build workstation, scanned, and carried in on approved media in one signed bundle.", "",
"## The phases", "",
"| Phase | Analysts can | Needs first |",
"|---|---|---|",
"| 0. Approvals and hardware | Nothing yet. Servers bought, approved, racked, with the lab's OS. | ISSM approvals for hardware entry, OS, transfer media |",
"| 1. SI chat | Chat with SI in a browser: questions, voice input, document upload | Phase 0, and the phase 1 software approved |",
"| 2. Analyst tools | Call SI from Jupyter, VS Code, MATLAB, and scripts | Phase 1, and approval to open an API address and install tools on analyst PCs |",
"| 3. Platform services | Sign in with lab accounts; changes go through GitLab and Argo CD; monitoring | Phase 1's cluster |",
"| 4. Metrics pipeline | Run metrics on lab data, see results on pages and in notebooks | Phase 3 (change loop), phase 2 (notebooks calling SI), and approval to read lab data |",
"", "Phases 2 and 3 do not depend on each other; the order is our proposal.", ""]
for ph in INTRO:
    rs = [r for r in rows if r["Phase"] == ph]
    out += [f"## Phase {ph}", "", INTRO[ph], "", "| ID | Component | Version | License | Download from | Notes |", "|---|---|---|---|---|---|"]
    for r in rs:
        out.append(f"| {r['ID']} | {cell(r['Component'])} | {cell(r['Version'])} | {cell(r['License'])} | {cell(r['Download URL'])} | {cell(r['Notes'])} |")
    out.append("")
(repo / "docs/cyber/16-phased-sbom.md").write_text("\n".join(out))
print(len(out))
