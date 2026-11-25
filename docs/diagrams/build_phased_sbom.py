"""Build docs/cyber/16-phased-sbom.csv and .md.

Phases 0 and 1 come from docs/cyber/16-sbom-phase-0-1.csv, the ISSM list (edit it in Excel and save as CSV;
it is the source for those rows and their wording). Later phases come from doc 12 plus the lists below.
Prints a WARN line when a version pinned in doc 12 does not appear in that list's row, so the two don't drift.

Usage: python3 -I docs/diagrams/build_phased_sbom.py .   (from the repository root, after editing the phase 0-1 list,
doc 12, or this file). After a change, check that every https link loads and every image tag exists.
"""
import re
import csv, sys
from pathlib import Path
repo = Path(sys.argv[1])
bom = {r["ID"]: r for r in csv.DictReader(open(repo / "docs/cyber/12-software-bom.csv"))}
ISSM_LIST = repo / "docs/cyber/16-sbom-phase-0-1.csv"
COLS = ["Phase", "ID", "Component", "Version", "Supplier", "License", "Download URL", "Project page", "Notes"]


def read_issm_list(path):
    """Rows of the phase 0-1 list as dicts. The header must match COLS."""
    with open(path, newline="") as f:
        r = csv.reader(f)
        head = next(r)
        assert head == COLS, f"columns changed: {head}"
        return [dict(zip(COLS, (c.strip() for c in row))) for row in r if len(row) > 1 and row[1].strip()]
GH = "https://github.com"
R = "v1.37.2%2Brke2r1"
P0, P1, P1o, P2, P3, P4, GR = ("0. Approvals and hardware", "1. SI chat", "1. SI chat (Currently considering)",
                               "2. Analyst tools", "3. Platform services", "4. Metrics pipeline", "Grow (any time after 1)")
# id, phase, download URL(s) (what the scripts fetch), project page, extra note
U = [
 ("C1", P2, "https://pypi.org/project/jupyter-ai/2.31.7/", f"{GH}/jupyterlab/jupyter-ai", ""),
 ("C2", P2, "https://pypi.org/project/langchain-openai/0.3.35/ ; https://pypi.org/project/langchain/0.3.30/ ; https://pypi.org/project/langchain-core/0.3.86/", f"{GH}/langchain-ai/langchain", ""),
 ("C3", P2, "https://pypi.org/project/openai/2.48.0/", f"{GH}/openai/openai-python", ""),
 ("C4", P2, "https://pypi.org/ (each wheel's URL is listed in clients/RESOLVED.txt at pull time)", "https://pypi.org", ""),
 ("C5", P2, "https://open-vsx.org/api/Continue/continue/win32-x64/2.1.0 ; https://open-vsx.org/api/Continue/continue/linux-x64/2.1.0", "https://open-vsx.org/extension/Continue/continue", ""),
 ("C6", P2, "Already in the lab", "https://www.mathworks.com/products/matlab.html", ""),
 ("M9", GR, "https://huggingface.co/ibm-granite/granite-embedding-reranker-english-r2", "https://huggingface.co/ibm-granite/granite-embedding-reranker-english-r2", "Better document search."),
]
EXTRA = [  # items not in doc 12 rows
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
rows = read_issm_list(ISSM_LIST)
for r in rows:
    assert r["Phase"] in (P0, P1, P1o), f"{r['ID']}: unknown phase {r['Phase']!r} in the ISSM list"
    b = bom.get(r["ID"])
    if b:  # a pinned version in doc 12 must show up somewhere in the ISSM list row
        ver = b[[k for k in b if k.startswith("Version")][0]]
        text = " ".join(r.values())
        for tok in re.findall(r"\bv?\d+\.\d+[\w.+-]*", ver):
            if tok.rstrip(".;,") not in text:
                print(f"WARN {r['ID']}: doc 12 says {tok!r}, the ISSM list row does not")
for i, ph, dl, page, note in U:
    b = bom[i]
    rows.append(dict(Phase=ph, ID=i, Component=b["Component"], Version=b[[k for k in b if k.startswith("Version")][0]],
                     Supplier=b["Supplier / source"], License=b["License"], **{"Download URL": dl, "Project page": page},
                     Notes=" ".join(x for x in [note] if x)))
for i, ph, comp, ver, sup, lic, dl, page, note in EXTRA:
    rows.append(dict(Phase=ph, ID=i, Component=comp, Version=ver, Supplier=sup, License=lic, **{"Download URL": dl, "Project page": page}, Notes=note))
missing = set(bom) - {r["ID"] for r in rows}
assert not missing, f"in doc 12 but in neither the ISSM list nor this script: {sorted(missing)}"
rows.sort(key=lambda r: ORDER.index(r["Phase"]))
cols = COLS
with open(repo / "docs/cyber/16-phased-sbom.csv", "w", newline="") as f:
    w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(rows)
print(len(rows), "rows")

# ---------- readable version ----------
rows = list(csv.DictReader(open(repo / "docs/cyber/16-phased-sbom.csv")))
INTRO = {
 "0. Approvals and hardware": "Lab-provided or shipped on the hardware. Not in our bundle. Listed so the review covers everything that runs.",
 "1. SI chat": "The first bundle. Analysts chat with SI in a browser. This is what we ask to review first.",
 "1. SI chat (Currently considering)": "Alternatives to phase 1 items. Cyber picks; we bring whichever is approved.",
 "2. Analyst tools": "Not in the first bundle. Jupyter, VS Code, MATLAB, and scripts reach SI through an API address with a personal key.",
 "3. Platform services": "Not chosen or pinned yet. Versions get pinned and checked when the phase is planned.",
 "4. Metrics pipeline": "Not chosen or pinned yet. Runs on the platform from phases 1 and 3.",
 "Grow (any time after 1)": "Optional additions that need no new design.",
}
def cell(s):
    lines = [ln.strip().replace("|", "/") for ln in s.split("\n")]
    return "<br>".join(re.sub(r"(https://[^\s;()]+)", r"<\1>", ln) for ln in lines if ln)
out = ["# 16. Phased software list with download links (for the ISSM)", "",
"**Track:** Cyber Security ([package index and decision register](README.md)).",
"**Status:** Phase 1 sent to the ISSM with the first email ([17](17-issm-intro-email.md)); phases 0 and 2 to 4 are still draft. Every item we plan to bring into the lab, by phase, with the exact place it is",
"downloaded from. Phases 0 and 1 come from the ISSM list,",
"[16-sbom-phase-0-1.csv](16-sbom-phase-0-1.csv). All phases as one spreadsheet: [16-phased-sbom.csv](16-phased-sbom.csv). Licenses and",
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
