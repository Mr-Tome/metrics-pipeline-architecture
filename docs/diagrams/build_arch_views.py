"""Build the chat feature Deployment view in metrics_architecture.html, and program_views.html (Phases, Security, Delivery, Keys, Review).

Security and Delivery show phase 1 (SI through the chat page). Keys and Review are built from docs 14 and 15.

Usage: python3 -I docs/diagrams/build_arch_views.py .   (run from the repository root after editing docs 14 or 15, or this file)
Idempotent: removes any earlier copy of the generated blocks before inserting.
"""
import html, json, re, sys
from pathlib import Path

repo = Path(sys.argv[1])
page = repo / "metrics_architecture.html"
t = page.read_text()

# remove earlier generated blocks
t = re.sub(r"<!-- GEN:([A-Z]+) START -->.*?<!-- GEN:\1 END -->", "", t, flags=re.S)


def plain(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = s.replace("**", "").replace("`", "").replace("~~", "")
    return s.strip()


def X(s):
    return html.escape(s, quote=True)


# ---------- 1. Data from the docs ----------
review = (repo / "docs/cyber/15-security-review.md").read_text()
areas, findings = [], []
for block in re.split(r"\n### ", review)[1:]:
    head = block.split("\n", 1)[0]
    m = re.match(r"([A-G])\. (.*)", head)
    if not m:
        continue
    areas.append((m.group(1), plain(m.group(2))))
    for line in block.splitlines():
        if re.match(r"\| R\d+ \|", line):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            findings.append(dict(id=c[0], area=m.group(1), new=c[1].startswith("New."),
                                 finding=plain(c[1].removeprefix("New.")), misuse=plain(c[2]),
                                 fix=plain(c[3]), sev=c[4], when=c[5], control=c[6]))

SHORT = {
    "R1": "Build machine unset", "R2": "Signing key custody", "R3": "Images pinned by tag",
    "R4": "Tool packages (later)", "R5": "Any GPG key passes", "R6": "Public key route",
    "R7": "Ban list, not allow list", "R8": "Lab intake unknown", "R9": "No network policies",
    "R10": "No CIS profile", "R11": "No cluster audit policy", "R12": "Join token printed",
    "R13": "Root sees everything", "R14": "Plain HTTP inside", "R15": "Expiry not tracked",
    "R16": "Session key unset", "R17": "First visitor is admin", "R18": "Keys never rotate",
    "R19": "Gateway admin (later)", "R20": "Unused code features", "R21": "speaches stale",
    "R22": "Outbound not proven", "R23": "Spoofable address", "R24": "Admins read chats",
    "R25": "Audit log gaps", "R26": "No backups", "R27": "No monitoring", "R28": "Keys in files (later)",
    "R29": "USA-only: lineage", "R30": "Model code files", "R31": "No incident steps",
    "R32": "Docs into the lab?", "R33": "SBOM format",
}
WHEN_SLUG = {"ISSM": "issm", "Before transfer": "transfer", "Before users": "users", "Later": "later"}

keysdoc = (repo / "docs/cyber/14-key-and-certificate-inventory.md").read_text()
keys = {}
for block in re.split(r"\n### ", keysdoc)[1:]:
    block = block.split("\n## ")[0]
    m = re.match(r"(KC\d+)\. (.*)", block.split("\n", 1)[0])
    if not m:
        continue
    rows = []
    for line in block.splitlines():
        r = re.match(r"\| ([A-Z][^|]*?) \| (.*) \|$", line)
        if r:
            rows.append([plain(r.group(1)), plain(r.group(2))])
    after = block.split("\n\n", 2)
    keys[m.group(1)] = dict(title=plain(m.group(2)), rows=rows)
summary = {}
for line in keysdoc.splitlines():
    r = re.match(r"\| (KC\d+) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$", line)
    if r:
        summary[r.group(1)] = dict(what=plain(r.group(2)), damage=plain(r.group(3)), by=plain(r.group(4)),
                                   where=plain(r.group(5)), expires=plain(r.group(6)))
for k, s in summary.items():
    keys.setdefault(k, dict(title=s["what"], rows=[]))
    keys[k]["damage"] = s["damage"]
    keys[k]["summary"] = s

def dmg_slug(d):
    d = d.lower()
    return "crit" if d.startswith("critical") else "high" if d.startswith("high") else "mod"

# ---------- 2. Keys view SVG ----------
SEV_STYLE = {  # fill, stroke
    "crit": ("var(--deny-f)", "var(--deny)"),
    "high": ("var(--z3-f)", "var(--z3)"),
    "mod": ("var(--panel)", "var(--pf)"),
    "": ("var(--bg)", "var(--ink)"),
}


def zone(x, y, w, h, label, color, fill=None, dash="none", cls="key-item"):
    f = f"var(--{fill})" if fill else "none"
    return (f'<g class="{cls}" data-p=""><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{f}" '
            f'fill-opacity="0.35" stroke="var(--{color})" stroke-width="1.6" stroke-dasharray="{dash}"/>'
            f'<text x="{x+16}" y="{y+24}" class="zone-label halo" text-anchor="start" fill="var(--{color})">{X(label)}</text></g>')


def node(key, x, y, w, h, title, sub, p, attr="data-kid", cls="key-item", dash="none"):
    fill, stroke = SEV_STYLE[p if p in SEV_STYLE else ""]
    return (f'<g class="tnode {cls}" tabindex="0" role="button" {attr}="{key}" data-p="{p}" aria-label="{X(title)}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.8" '
            f'stroke-dasharray="{dash}" class="box"/>'
            f'<text x="{x+12}" y="{y+23}" class="srv-t" text-anchor="start">{X(title)}</text>'
            f'<text x="{x+12}" y="{y+41}" class="edge-label" text-anchor="start">{X(sub)}</text></g>')


def flow(d, cls="tflow", marker="ka"):
    return f'<path class="{cls}" d="{d}" marker-end="url(#{marker})"/>'


def label(x, y, s, anchor="start", color="var(--muted)"):
    return f'<text x="{x}" y="{y}" class="edge-label halo" text-anchor="{anchor}" fill="{color}">{X(s)}</text>'


def filt(key, x, y, w, title, sub, p, attr):
    fill, stroke = SEV_STYLE[p] if p in SEV_STYLE else ("var(--panel)", "var(--pf)")
    return (f'<g class="tnode filt" tabindex="0" role="button" {attr}="{key}" aria-label="Highlight: {X(title)}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="52" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.8" class="box"/>'
            f'<text x="{x+14}" y="{y+22}" class="promise-t" text-anchor="start" fill="var(--ink)">{X(title)}</text>'
            f'<text x="{x+14}" y="{y+41}" class="edge-label" text-anchor="start">{X(sub)}</text></g>')


K = lambda k: keys[k]["damage"]
ks = []
ks.append('<svg id="keys" viewBox="0 0 1240 724" role="img" aria-label="Keys view: every key and secret in phase 1, where it lives, and what it controls">')
ks.append('<defs><marker id="ka" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--edge)"/></marker>'
          '<marker id="kx" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--deny)"/></marker></defs>')
ks.append(filt("crit", 16, 14, 396, "Critical if stolen", "Could put software into the lab or take over", "crit", "data-kf"))
ks.append(filt("high", 422, 14, 396, "High if stolen", "Could read others' data or act as another user", "high", "data-kf"))
ks.append(filt("mod", 828, 14, 396, "Moderate if stolen", "Could use the service without being identified", "mod", "data-kf"))
# zones
ks.append(zone(16, 84, 212, 420, "Build side (connected)", "z1", "z1-f"))
ks.append(zone(240, 84, 176, 420, "Transfer", "in", None, "9 6"))
ks.append(zone(428, 84, 222, 420, "Lab admin host", "pf", "pf-f"))
ks.append(zone(662, 84, 562, 420, "Cluster: svc01-03, gpu01", "k8", "k8-f"))
ks.append(zone(676, 120, 262, 372, "Platform", "pf", None, "6 4"))
ks.append(zone(950, 120, 262, 372, "SI services", "si", "si-f"))
ks.append(zone(16, 520, 600, 166, "Analyst workstations", "wb", "wb-f"))
ks.append(zone(628, 520, 596, 166, "Hardware (filled in by the installers)", "in", None, "9 6"))
# nodes
ks.append(node("KC1", 30, 126, 184, 58, "Signing private key", "KC1: signs each bundle", dmg_slug(K("KC1"))))
ks.append(node("bundle", 252, 126, 152, 58, "Release bundle", "Signed checksum list", ""))
ks.append(node("verify", 442, 126, 194, 58, "verify.sh", "Refuses a bad signature", ""))
ks.append(node("KC2", 442, 214, 194, 58, "Signing public key", "KC2: what our signature looks like", dmg_slug(K("KC2"))))
ks.append(node("KC3", 442, 330, 194, 58, "Lab CA", "KC3: held by the lab PKI team", dmg_slug(K("KC3")), dash="6 4"))
ks.append(node("KC8", 690, 156, 234, 58, "Cluster admin", "KC8: root, can read every secret", dmg_slug(K("KC8"))))
ks.append(node("KC9", 690, 238, 234, 58, "Join token", "KC9: lets a machine join", dmg_slug(K("KC9"))))
ks.append(node("KC10", 690, 320, 234, 58, "Cluster certificates", "KC10: and the secrets key", dmg_slug(K("KC10"))))
ks.append(node("KC11", 690, 402, 234, 58, "Image registry login", "KC11: decides what images run", dmg_slug(K("KC11"))))
ks.append(node("KC5", 964, 150, 234, 52, "Gateway master key", "KC5: makes user keys", dmg_slug(K("KC5"))))
ks.append(node("KC6", 964, 212, 234, 52, "Chat page's key", "KC6: chat page to gateway", dmg_slug(K("KC6"))))
ks.append(node("KC4", 964, 274, 234, 52, "TLS certificate", "KC4: encrypts users' traffic", dmg_slug(K("KC4"))))
ks.append(node("KC12", 964, 336, 234, 52, "Gateway database password", "KC12: set by the database operator", dmg_slug(K("KC12"))))
ks.append(node("KC13", 964, 398, 234, 52, "Chat login signing key", "KC13: nobody sets it today", dmg_slug(K("KC13")), dash="6 4"))
ks.append(node("KC7", 30, 566, 300, 58, "User API keys (later phase)", "KC7: none in phase 1", dmg_slug(K("KC7")), dash="6 4"))
ks.append(node("KC14", 642, 566, 300, 58, "BMC, switch, and OS accounts", "KC14: on each device", dmg_slug(K("KC14")), dash="6 4"))
# arrows
ks.append(flow("M214,155 H252"))
ks.append(flow("M404,155 H442"))
ks.append(flow("M122,184 V243 H442"))
ks.append(label(250, 236, "separate route"))
ks.append(flow("M539,214 V184"))
ks.append(label(546, 204, "checks"))
ks.append(flow("M636,140 H676"))
ks.append(label(640, 132, "installs"))
ks.append(flow("M636,359 H654 V498 H944 V300 H964"))
ks.append(label(800, 492, "signs", "middle"))
ks.append(f'<path class="tflow" style="stroke:var(--deny);stroke-dasharray:6 5" d="M924,185 H964" marker-end="url(#kx)"/>')
ks.append(flow("M1198,176 H1232 V706 H180 V624"))
ks.append(label(700, 700, "the master key creates user keys", "middle"))
ks.append(label(346, 590, "Phase 1: analysts sign in to the"))
ks.append(label(346, 606, "chat page and hold no key."))
ks.append(label(956, 590, "Hardware track; listed here"))
ks.append(label(956, 606, "so the list is complete."))
ks.append("</svg>")
keys_svg = "\n".join(ks)

# ---------- 3. Review view SVG ----------
rs = []
COLW, GAP, X0, Y0 = 168, 6, 16, 104
by_area = {a: [f for f in findings if f["area"] == a] for a, _ in areas}
height = Y0 + 64 + max(len(v) for v in by_area.values()) * 46 + 40
rs.append(f'<svg id="rev" viewBox="0 0 1240 {height}" role="img" aria-label="Review view: our security findings before the ISSM meeting">')
rs.append('<defs><marker id="ra" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--edge)"/></marker></defs>')
SEV_SLUG = {"High": "high", "Medium": "med", "Low": "low"}
RSTYLE = {"high": ("var(--deny-f)", "var(--deny)"), "med": ("var(--z3-f)", "var(--z3)"), "low": ("var(--panel)", "var(--pf)")}
count = {s: sum(1 for f in findings if SEV_SLUG[f["sev"]] == s) for s in RSTYLE}
cw = {w: sum(1 for f in findings if WHEN_SLUG.get(f["when"]) == w) for w in WHEN_SLUG.values()}
fb = [("high", "High", f"{count['high']} issues", RSTYLE["high"]), ("med", "Medium", f"{count['med']} issues", RSTYLE["med"]),
      ("low", "Low", f"{count['low']} issues", RSTYLE["low"]),
      ("issm", "Needs the ISSM", f"{cw['issm']} decisions to bring", ("var(--panel)", "var(--pf)")),
      ("transfer", "Before transfer", f"{cw['transfer']} to fix first", ("var(--panel)", "var(--pf)")),
      ("users", "Before users", f"{cw['users']} to fix first", ("var(--panel)", "var(--pf)"))]
for i, (k, title, sub, (fill, stroke)) in enumerate(fb):
    x = 16 + i * 204
    rs.append(f'<g class="tnode filt" tabindex="0" role="button" data-rf="{k}" aria-label="Highlight: {X(title)}">'
              f'<rect x="{x}" y="14" width="196" height="52" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.8" class="box"/>'
              f'<text x="{x+14}" y="36" class="promise-t" text-anchor="start" fill="var(--ink)">{X(title)}</text>'
              f'<text x="{x+14}" y="55" class="edge-label" text-anchor="start">{X(sub)}</text></g>')
AREA_SHORT = {"A": "Build and sign", "B": "Transfer and intake", "C": "Cluster platform", "D": "SI services",
              "E": "Data and records", "F": "Models", "G": "Process"}
AREA_COLOR = {"A": "z1", "B": "in", "C": "k8", "D": "si", "E": "z3", "F": "z4", "G": "pf"}
colh = height - Y0 - 16
rs.append(f'<path class="tflow" d="M16,88 H{X0 + 5*(COLW+GAP) - GAP}" marker-end="url(#ra)"/>')
rs.append(label(24, 82, 'The path software and data take, from building the bundle to what users store'))
for i, (a, _) in enumerate(areas):
    x = X0 + i * (COLW + GAP)
    c = AREA_COLOR[a]
    rs.append(f'<g class="rev-item" data-p=""><rect x="{x}" y="{Y0}" width="{COLW}" height="{colh}" rx="14" fill="var(--{c}-f)" '
              f'fill-opacity="0.35" stroke="var(--{c})" stroke-width="1.6"/>'
              f'<text x="{x+12}" y="{Y0+24}" class="zone-label halo" text-anchor="start" fill="var(--{c})">{X(AREA_SHORT[a])}</text>'
              f'<text x="{x+12}" y="{Y0+42}" class="edge-label" text-anchor="start">{len(by_area[a])} issues</text></g>')
    for j, f in enumerate(by_area[a]):
        s = SEV_SLUG[f["sev"]]
        fill, stroke = RSTYLE[s]
        y = Y0 + 56 + j * 46
        p = f'{s} {WHEN_SLUG.get(f["when"], "")}'
        rs.append(f'<g class="tnode rev-item" tabindex="0" role="button" data-rid="{f["id"]}" data-p="{p}" aria-label="{f["id"]} {X(SHORT[f["id"]])}">'
                  f'<rect x="{x+8}" y="{y}" width="{COLW-16}" height="38" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="1.6" class="box"/>'
                  f'<text x="{x+18}" y="{y+24}" class="edge-label" text-anchor="start" fill="var(--ink)">'
                  f'<tspan font-weight="700" fill="var(--ink)">{f["id"]}</tspan> {X(SHORT[f["id"]])}</text></g>')
rs.append("</svg>")
rev_svg = "\n".join(rs)

# ---------- 3b. Security and Delivery views (phase 1: SI through the chat page) ----------
INFO = {}


def inode(key, x, y, w, title, sub, p, rows, h=52, sev="", dash="none", kind=""):
    INFO[key] = dict(title=title, kind=kind, rows=rows)
    return node(key, x, y, w, h, title, sub, sev, attr="data-iid", cls="vi", dash=dash).replace(
        f'data-p="{sev}"', f'data-p="{p}"', 1)


def izone(x, y, w, h, lab, color, fill=None, dash="none"):
    return zone(x, y, w, h, lab, color, fill, dash, cls="zone-item")


def line(d):
    return f'<path d="{d}" fill="none" stroke="var(--edge)" stroke-width="1.6"/>'


def blocked(d, marker):
    return f'<path class="sflow-x" d="{d}" marker-end="url(#{marker})"/>'


def ifilt(key, x, w, title, sub):
    return filt(key, x, 14, w, title, sub, "", "data-f").replace('width="396"', f'width="{w}"')


def defs(a, x):
    return (f'<defs><marker id="{a}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--edge)"/></marker>'
            f'<marker id="{x}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--deny)"/></marker></defs>')


# Phases view: what goes in when, and what each phase needs first
PH = [
 dict(key="p0", name="Phase 0", title="Approvals and hardware", color="pf",
      info=[["Goal", "Get permission, then buy, rack, and power the servers with the lab's OS."], ["Analysts can", "Nothing yet."], ["Needs first", "Nothing. This is where everything starts."], ["Done when", "The ISSM has approved hardware entry, the OS, and transfer media, and the rack passes its hardware checks."], ["Work steps", "Prototype plan, P0, and the rack build guide."]],
      get=("Nothing for users yet", "Approved, racked, powered"),
      issm=[("Hardware entry process", "How new hardware is approved into the lab.", "S1"), ("Server OS baseline", "Which OS and hardening accreditation requires. We plan Rocky Linux 9; RHEL 9 if required. Is there a lab package mirror?", "L1"), ("Transfer media", "Approved media type, who provides it, how long a transfer takes.", "S3"), ("Secure Boot", "Required or not. It changes how the NVIDIA driver is installed.", "S4"), ("Switch setup cable", "A USB-to-serial console cable from svc01 to our own rack switch (sw01) for first setup, then removed. No laptop, no lab network.", "S8"), ("Burn-in outside the lab", "May new hardware be tested on the unclassified side first, then wiped?", "S2")],
      sw=[("Lab OS: Rocky or RHEL 9", "Installed on every server from the lab's image.", "16: OS1"), ("OS packages from mirror", "gcc, kernel-devel, dkms, SELinux packages for the driver and Kubernetes.", "16: OS2 to OS5"), ("Firmware on the hardware", "Switch, BIOS, BMC, NIC, and drive firmware as shipped.", "16: H1 to H4")],
      hw=[("gpu01: 4 GPUs", "One GPU server with four RTX PRO 6000 GPUs.", "Servers quote"), ("svc01-03 service nodes", "Three service servers run Kubernetes and the services.", "Servers quote"), ("Switches, console, cables", "sw01 data switch, oob01 management switch, rack console, cables, optics.", "Network and rack quote")]),
 dict(key="p1", name="Phase 1", title="SI chat", color="si",
      info=[["Goal", "Analysts use SI through a chat page in their browser."], ["Analysts can", "Ask questions, dictate by voice, and upload a document to ask about it. About 50 users."], ["Needs first", "Phase 0, and the phase 1 software approved by the ISSM."], ["Done when", "The first signed bundle is installed and analysts are signed in."], ["Work steps", "Prototype plan, P1 to P3: build and rehearse the bundle, install in the lab, then updates."]],
      get=("Chat with SI in a browser", "Questions, voice, documents"),
      issm=[("Upstream or Iron Bank images", "May we use upstream container images, or only Iron Bank where it has them?", "S6"), ("Model file formats", "We propose only formats that cannot run code when loaded.", "S20"), ("US-made rule: how far", "Publisher only, or also the base model and the converter?", "S22"), ("Bundle signing and key", "GPG or cosign, who holds the key, how the public key reaches the lab.", "S10"), ("Driver build packages", "From the lab mirror, or carried in the bundle?", "S11"), ("Speech-to-text server", "Which server runs faster-whisper.", "S12"), ("Chat page image", "Standard or slim Open WebUI image.", "S13"), ("Who is cluster admin", "Cluster admin can read every chat and log.", "S24"), ("Encryption at rest", "For chat history, uploads, databases, models.", "S25"), ("Audit log content", "What is recorded, how long, where it goes.", "S26"), ("Key lifetimes", "Gateway keys and the TLS certificate.", "S23")],
      sw=[("Kubernetes (RKE2), Zarf", "The platform and the air-gap delivery tool.", "16: K1 to K9"), ("NVIDIA driver, GPU Operator", "GPU support.", "16: G1, G2"), ("Language model", "gpt-oss-120b (OpenAI), three copies.", "16: A1, M1"), ("Gateway (LiteLLM)", "Every model request goes through it and is logged.", "16: A2"), ("Chat page (Open WebUI)", "The web page analysts use.", "16: A3"), ("Speech-to-text (Whisper)", "Voice input.", "16: A4, M2"), ("Document upload", "Text extraction and OCR (Tika) and embeddings.", "16: A5, A6, M3"), ("Database (PostgreSQL)", "The gateway's request log.", "16: A7, A8"), ("Scanner (Trivy)", "Scans every image, before and after transfer.", "16: Sec1, Sec2")],
      hw=[("Phase 0 hardware", "Nothing new.", "")]),
 dict(key="p2", name="Phase 2", title="Analyst tools", color="wb",
      info=[["Goal", "Analysts call SI from their own tools."], ["Analysts can", "Use SI from Jupyter, VS Code, MATLAB, and Python scripts."], ["Needs first", "Phase 1."], ["Done when", "Each analyst has a personal key and the tools work from lab PCs."], ["Status", "The scripts can already do this. It stays off until approved."]],
      get=("SI in Jupyter, VS Code, MATLAB", "Personal key per analyst"),
      issm=[("Open an API address", "Lets analyst tools reach the gateway from desks.", "15: R19"), ("Tools on analyst PCs", "Python packages and a VS Code extension on lab PCs.", "15: R4"), ("Handing out personal keys", "How keys reach analysts and how long they last.", "S23"), ("Keys kept in files", "Guidance so keys stay out of shared notebooks.", "15: R28")],
      sw=[("Jupyter AI + libraries", "Python packages for Jupyter.", "16: C1, C2, C4"), ("Continue for VS Code", "VS Code extension.", "16: C5"), ("OpenAI Python client", "For scripts.", "16: C3"), ("MATLAB (already there)", "Calls the gateway with webwrite. Nothing added.", "16: C6")],
      hw=[("No new hardware", "", "")]),
 dict(key="p3", name="Phase 3", title="Platform services", color="k8",
      info=[["Goal", "Shared services that later phases need: lab sign-in, a registry, a change process, monitoring."], ["Analysts can", "Sign in with their lab account. Changes go through review in GitLab."], ["Needs first", "Phase 1's cluster. Does not need phase 2."], ["Status", "Not chosen or pinned yet."]],
      get=("Sign in with lab account", "Reviewed changes, monitoring"),
      issm=[("Platform One / Iron Bank", "Account and use of Big Bang and Iron Bank.", "S6"), ("Single sign-on", "Connect Keycloak to the lab's accounts.", "15"), ("GitLab in the lab", "A code and change system inside the lab.", "")],
      sw=[("Big Bang baseline", "Platform One's package of the services below.", "16: X1, X2"), ("Keycloak sign-in", "Replaces local accounts.", "16: X3"), ("Harbor registry", "Replaces the Zarf registry.", "16: X4"), ("GitLab and Runner", "Code and change review.", "16: X5"), ("Argo CD", "Deploys approved changes.", "16: X6"), ("Prometheus, Grafana", "Monitoring.", "16: X7")],
      hw=[("Same servers", "Capacity on svc01-03 to check when it is planned.", "")]),
 dict(key="p4", name="Phase 4", title="Metrics pipeline", color="z3",
      info=[["Goal", "The metrics pipeline in the Data flow tab."], ["Analysts can", "Run metrics on lab data and see results on pages and in notebooks."], ["Needs first", "Phase 3 (change process) and phase 2 (notebooks calling SI), plus approval to read lab data."], ["Status", "Not chosen or pinned yet. None of this code exists yet."]],
      get=("Metrics on lab data", "Pages and notebooks"),
      issm=[("Read access to lab data", "Read-only access to the lab's post-processed data.", ""), ("Code written in the lab", "Metric plugins written and reviewed inside the lab.", ""), ("Notebook per analyst", "JupyterHub in the cluster.", "")],
      sw=[("Dagster", "Runs the pipeline.", "16: X8"), ("Readers, metric plugins", "Ours, written in the lab.", "16: X11"), ("Evidence pages", "Published metric pages.", "16: X10"), ("JupyterHub", "Analyst notebooks.", "16: X9")],
      hw=[("More servers likely", "Memory-heavy jobs; to size when planned.", "")]),
]
CW, CG, CX0 = 232, 12, 16
LANES = [("get", "What analysts get", "wb"), ("issm", "ISSM decides", "deny"), ("sw", "Software it brings", "k8"), ("hw", "Hardware", "pf")]
CH, CGAP = 26, 4
pv = []
y_head = 150
y = y_head + 64 + 24
lane_y = {}
for k, _, _ in LANES:
    n = 1 if k == "get" else max(len(p[k]) for p in PH)
    h = 46 if k == "get" else n * (CH + CGAP) - CGAP
    lane_y[k] = (y + 20, h)
    y += 20 + h + 22
grow_y = y
height = grow_y + 70
pv.append(f'<svg id="phs" viewBox="0 0 1240 {height}" role="img" aria-label="Phases view: what goes in when, and what each phase needs first">')
pv.append(defs("pa", "px"))
pv.append(ifilt("get", 16, 296, "What analysts get", "When each phase is finished"))
pv.append(ifilt("issm", 320, 296, "ISSM decides", "Approvals each phase needs"))
pv.append(ifilt("sw", 624, 296, "Software it brings", "Full list with links: doc 16"))
pv.append(ifilt("hw", 928, 296, "Hardware", "What has to be bought or racked"))
pv.append(f'<g class="zone-item"><rect x="8" y="88" width="{2*CW+CG+16}" height="{height-96}" rx="16" fill="var(--z3-f)" fill-opacity="0.45" stroke="var(--z3)" stroke-width="2"/>'
          f'<text x="22" y="110" class="zone-label halo" text-anchor="start" fill="var(--z3)">Step one: get approved, then SI chat</text></g>')
for i, p in enumerate(PH):
    x = CX0 + i * (CW + CG)
    INFO[p["key"]] = dict(title=f'{p["name"]}. {p["title"]}', kind="", rows=p["info"])
    pv.append(f'<g class="tnode vi" tabindex="0" role="button" data-iid="{p["key"]}" data-p="get issm sw hw" aria-label="{X(p["name"])}">'
              f'<rect x="{x}" y="{y_head}" width="{CW}" height="64" rx="12" fill="var(--{p["color"]}-f)" stroke="var(--{p["color"]})" stroke-width="2.2" class="box"/>'
              f'<text x="{x+14}" y="{y_head+26}" class="promise-t" text-anchor="start" fill="var(--ink)">{X(p["name"])}</text>'
              f'<text x="{x+14}" y="{y_head+48}" class="srv-t" text-anchor="start">{X(p["title"])}</text></g>')
    for k, _, c in LANES:
        ly, lh = lane_y[k]
        if k == "get":
            gt, s = p["get"]
            key = f'{p["key"]}_get'
            INFO[key] = dict(title=gt, kind="", rows=[["When", f'{p["name"]} is finished'], ["Detail", s]])
            pv.append(node(key, x, ly, CW, 46, gt, s, "", attr="data-iid", cls="vi").replace('data-p=""', 'data-p="get"', 1))
            continue
        for j, (ct, d, ref) in enumerate(p[k]):
            key = f'{p["key"]}_{k}{j}'
            rows = [["What", d]] if d else []
            if ref:
                rows.append(["Listed in", ref if not ref[0] == "S" and not ref[0] == "L" else f"Decision register, {ref}"])
            INFO[key] = dict(title=ct, kind="", rows=rows or [["What", ct]])
            cy = ly + j * (CH + CGAP)
            fill, stroke = {"issm": ("var(--deny-f)", "var(--deny)"), "sw": ("var(--k8-f)", "var(--k8)"), "hw": ("var(--panel)", "var(--pf)")}[k]
            pv.append(f'<g class="tnode vi" tabindex="0" role="button" data-iid="{key}" data-p="{k}" aria-label="{X(ct)}">'
                      f'<rect x="{x+6}" y="{cy}" width="{CW-12}" height="{CH}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.4" class="box"/>'
                      f'<text x="{x+16}" y="{cy+17}" class="edge-label" text-anchor="start" fill="var(--ink)">{X(ct)}</text></g>')
for k, lab, c in LANES:
    ly, _ = lane_y[k]
    pv.append(label(CX0 + 2*(CW+CG) + 8, ly - 6, lab, "start", f"var(--{c})"))
    pv.append(label(CX0 + 4, ly - 6, lab, "start", f"var(--{c})"))
# dependencies
pv.append(flow(f"M{CX0+CW},{y_head+32} H{CX0+CW+CG}", marker="pa"))
pv.append(flow(f"M{CX0+2*CW+CG},{y_head+32} H{CX0+2*(CW+CG)}", marker="pa"))
pv.append(flow(f"M{CX0+4*CW+3*CG},{y_head+32} H{CX0+4*(CW+CG)}", marker="pa"))
x1 = CX0 + (CW + CG) + 180; x3 = CX0 + 3 * (CW + CG) + 60
pv.append(flow(f"M{x1},{y_head} V{y_head-20} H{x3} V{y_head}", marker="pa"))
pv.append(label(x1 + 8, y_head - 26, "phase 3 needs phase 1, not 2", "start"))
x2 = CX0 + 2 * (CW + CG) + 180; x4 = CX0 + 4 * (CW + CG) + 120
pv.append(f'<path class="tflow" style="stroke-dasharray:6 5" d="M{x2},{y_head} V{y_head-44} H{x4} V{y_head}" marker-end="url(#pa)"/>')
pv.append(label(x4 - 8, y_head - 50, "phase 4 also needs phase 2", "end"))
# grow
INFO["grow1"] = dict(title="100 users: add gpu02", kind="", rows=[["When", "Any time after phase 1."], ["What", "A second GPU server with 4 GPUs in rack 2. Same software bundle, no design change."], ["Listed in", "Budget and BOM, section 5; 16: X12"]])
INFO["grow2"] = dict(title="Better document search", kind="", rows=[["When", "Any time after phase 1."], ["What", "Add IBM's reranker model (US-made)."], ["Listed in", "16: M9"]])
pv.append(label(CX0 + 2*(CW+CG) + 8, grow_y + 4, "Any time after phase 1", "start", "var(--muted)"))
pv.append(node("grow1", CX0 + 2*(CW+CG), grow_y + 14, 2*CW+CG, 46, "100 users: add gpu02", "Same bundle, no design change", "", attr="data-iid", cls="vi", dash="6 4").replace('data-p=""', 'data-p="hw"', 1))
pv.append(node("grow2", CX0 + 4*(CW+CG), grow_y + 14, CW, 46, "Better document search", "IBM reranker model", "", attr="data-iid", cls="vi", dash="6 4").replace('data-p=""', 'data-p="sw"', 1))
pv.append("</svg>")
phs_svg = "\n".join(pv)

# Security view
sv = ['<svg id="sec" viewBox="0 0 1240 612" role="img" aria-label="Security view: how phase 1 keeps the chat service closed and recorded">', defs("sa", "sx")]
sv.append(ifilt("net", 16, 296, "No internet", "The lab has no outside connection"))
sv.append(ifilt("door", 320, 296, "One way in", "Analysts reach only the chat page"))
sv.append(ifilt("sw", 624, 296, "Only signed software", "Nothing runs unless the bundle brought it"))
sv.append(ifilt("log", 928, 296, "Every request recorded", "Who asked what, and when"))
sv.append(izone(16, 84, 1208, 436, "Lab network (no internet)", "in", None, "9 6"))
sv.append(izone(30, 116, 210, 178, "Analyst desks", "wb", "wb-f"))
sv.append(izone(30, 306, 210, 200, "Lab admin host", "pf", "pf-f"))
sv.append(izone(256, 116, 954, 390, "Cluster: svc01-03, gpu01", "k8", "k8-f"))
sv.append(inode("u_browser", 44, 156, 182, "Analyst's browser", "Phase 1: the only way in", "door", [
    ["What it is", "The analyst's normal lab browser. Nothing is installed on the analyst's machine."],
    ["Control", "The analyst signs in to the chat page with an account the admin created. The page uses HTTPS with a certificate from the lab CA, so the browser shows no warning."]]))
sv.append(inode("u_tools", 44, 222, 182, "Analyst tools", "Later phase: no access", "door net", [
    ["What it is", "Jupyter, VS Code, MATLAB, and scripts calling the model directly through an API address with a personal key."],
    ["Phase 1", "Not available. There is no API address, so these tools cannot reach the model. Adding them later is a separate decision for the ISSM."]], dash="6 4"))
sv.append(inode("adm", 44, 346, 182, "Admin commands", "verify.sh, deploy.sh, kubectl", "door sw", [
    ["What it is", "The one machine where the cluster is managed. The cluster admin file (KC8) lives here."],
    ["Control", "Checks every bundle before install (verify.sh), installs it (deploy.sh), and creates the chat page's gateway key. No admin work is done from an analyst desk."],
    ["Open items", "Who may be cluster admin (S24). The join token is printed on screen today (R12)."]]))
sv.append(inode("bundle", 44, 430, 182, "Signed bundle", "The only way software arrives", "sw", [
    ["What it is", "One transfer drive with everything phase 1 needs: Kubernetes, images, models, the NVIDIA driver, and the scripts."],
    ["Control", "The list of every file's checksum is signed. verify.sh refuses the bundle if the signature, a checksum, or a file type is wrong."],
    ["Open items", "verify.sh accepts a signature from any key in the admin's keyring (R5). Who holds the signing key (S10)."]]))
sv.append(inode("fd", 272, 156, 196, "Front door (Traefik)", "HTTPS, chat address only", "door net", [
    ["What it is", "The only entrance into the cluster from the lab network."],
    ["Control", "Answers only the chat address, over HTTPS. Phase 1 opens no API address, so the gateway and the models cannot be reached from a desk."]]))
sv.append(inode("chat", 492, 156, 210, "Chat page (Open WebUI)", "Sign-in, accounts by admin", "door log", [
    ["What it is", "The web page analysts use: chat, voice input, and document upload."],
    ["Control", "Local accounts. The admin account is created during install and sign-up is turned off, so nobody can make their own account (R17)."],
    ["Open items", "Its login signing key is not set by us and may change on every restart (KC13, R16). Admins can read every chat (R24)."]]))
sv.append(inode("gw", 726, 156, 210, "SI gateway (LiteLLM)", "Reachable inside the cluster only", "net log", [
    ["What it is", "Sits between the chat page and the models. Every model request goes through it."],
    ["Control", "Reachable only inside the cluster. The chat page uses its own key (KC6). The gateway records every request and its user in its database."],
    ["Open items", "Master key never changes (R18). What the log records and how long it is kept (S26)."]]))
sv.append(inode("m_llm", 960, 140, 236, "Language model (vLLM)", "gpt-oss-120b, 3 copies", "sw", [
    ["What it is", "Answers the chat. Three copies on three GPUs, so an update keeps two serving."],
    ["Control", "Model files are a data-only format that cannot run code when loaded, checked by verify.sh. No internet to reach."]]))
sv.append(inode("m_stt", 960, 202, 236, "Speech-to-text", "Whisper, fourth GPU", "sw", [
    ["What it is", "Turns the chat page's microphone input into text."],
    ["Open items", "Which server runs it (S12)."]]))
sv.append(inode("m_emb", 960, 264, 236, "Embeddings", "Document search, on CPU", "sw", [
    ["What it is", "Finds the parts of an uploaded document that match the question."],
    ["Open items", "Which model: the USA-only rule rules out the current one if it covers model lineage (S22)."]]))
sv.append(inode("k_api", 272, 404, 196, "Kubernetes control", "Admin host only", "door log", [
    ["What it is", "The Kubernetes API that controls every service in the cluster."],
    ["Control", "Used only from the lab admin host with the cluster admin file (KC8)."],
    ["Open items", "No Kubernetes audit policy yet (R11). No network policies between services yet (R9)."]]))
sv.append(inode("ow", 492, 404, 210, "Chats and uploads", "Chat page's own storage", "log", [
    ["What it is", "Chat history and uploaded files, on the chat page's disk in the cluster."],
    ["Open items", "Encryption at rest (S25). Backups (R26)."]]))
sv.append(inode("db", 726, 404, 210, "Gateway database", "PostgreSQL: request log", "log", [
    ["What it is", "The gateway's records: who sent each request, when, and how large."],
    ["Control", "Its password is created by the database operator at install (KC12). Nobody types it."]]))
sv.append(inode("reg", 960, 404, 236, "Image registry (Zarf)", "Only images from the bundle", "sw", [
    ["What it is", "Holds every container image the cluster runs."],
    ["Control", "Filled only from the signed bundle. The cluster pulls images only from here, so nothing else can run."]]))
sv.append(inode("inet", 16, 538, 296, "Internet", "No connection to the lab", "net", [
    ["Fact", "The lab has no internet connection. Every service is also set to make no outbound calls, and the rehearsal records any attempt (R22)."]], sev="crit"))
sv.append(flow("M226,182 H272", marker="sa"))
sv.append(label(249, 174, "HTTPS", "middle"))
sv.append(flow("M468,182 H492", marker="sa"))
sv.append(flow("M702,182 H726", marker="sa"))
sv.append(flow("M936,182 H948 V166 H960", marker="sa"))
sv.append(flow("M948,182 V228 H960", marker="sa"))
sv.append(flow("M948,228 V290 H960", marker="sa"))
sv.append(flow("M597,208 V404", marker="sa"))
sv.append(label(606, 312, "saves"))
sv.append(flow("M831,208 V404", marker="sa"))
sv.append(label(840, 312, "logs every request"))
sv.append(blocked("M226,248 H248 V204 H272", "sx"))
sv.append(label(48, 288, "red: no API address in phase 1"))
sv.append(flow("M226,372 H248 V430 H272", marker="sa"))
sv.append(flow("M135,430 V400", marker="sa"))
sv.append(blocked("M164,538 V524", "sx"))
sv.append(label(180, 534, "blocked"))
sv.append(label(330, 564, "Phase 1 gives analysts SI through the chat page only. There is no other way in."))
sv.append("</svg>")
sec_svg = "\n".join(sv)

# Delivery view
dv = ['<svg id="del" viewBox="0 0 1240 584" role="img" aria-label="Delivery view: how a release gets from the internet into the lab">', defs("da", "dx")]
dv.append(ifilt("chk", 16, 396, "Security checks", "Where a bad or missing file is caught"))
dv.append(ifilt("x", 422, 396, "What crosses the air gap", "One signed bundle, nothing else"))
dv.append(ifilt("key", 828, 396, "Where keys are used", "Signing key, lab CA certificate"))
dv.append(izone(16, 84, 196, 400, "Upstream (internet)", "in", None, "9 6"))
dv.append(izone(224, 84, 336, 400, "Build workstation", "z1", "z1-f"))
dv.append(label(240, 124, "unclassified side, has internet"))
dv.append(izone(394, 140, 154, 332, "Rehearsal VM", "z2", "z2-f", "6 4"))
dv.append(izone(572, 84, 148, 400, "Transfer", "in", None, "9 6"))
dv.append(izone(732, 84, 492, 400, "Lab (no internet)", "pf", "pf-f"))
dv.append(izone(746, 120, 196, 352, "Lab admin host", "pf", None, "6 4"))
dv.append(izone(956, 120, 254, 352, "Cluster", "k8", "k8-f"))
UP = [("up_img", "Container images", "Upstream or Iron Bank", "Each service's image, pinned by version. Iron Bank images replace upstream ones where Cyber requires (S6)."),
      ("up_k8s", "RKE2, Zarf, charts", "Pinned releases", "Kubernetes (RKE2), the Zarf delivery tool, and the Helm charts that describe each service."),
      ("up_mod", "Model weights", "USA-made, no-code files", "From Hugging Face. Only formats that cannot run code when loaded, and only models made in the USA (S22)."),
      ("up_drv", "NVIDIA driver", "R580 now, R620 planned", "The data center driver for gpu01. R620 once a GPU Operator release supports it."),
      ("up_db", "Vulnerability data", "Trivy database", "Lets the scanner check images offline, here and again in the lab.")]
for i, (k, ti, su, d) in enumerate(UP):
    dv.append(inode(k, 28, 124 + i * 68, 172, ti, su, "", [["What it is", d]]))
dv.append(line("M200,150 H206 V422 H200"))
dv.append(flow("M206,236 H236", marker="da"))
dv.append(inode("b_pin", 236, 140, 148, "Version pins", "versions.env, reviewed", "chk", [
    ["What it is", "One file that names the exact version of everything in the bundle."],
    ["Control", "Changes are reviewed and committed before a pull, so the bundle records exactly what built it."]]))
dv.append(inode("b_pull", 236, 220, 148, "Pull scripts", "Download, checksum", "chk", [
    ["What it does", "Downloads everything named in the pins and checks each download's checksum."]]))
dv.append(inode("b_scan", 236, 300, 148, "Scan", "Trivy, every image", "chk", [
    ["What it does", "Scans every container image for known vulnerabilities. The report travels with the bundle."],
    ["Open items", "Images are pinned by tag, not by digest (R3)."]]))
dv.append(inode("b_seal", 236, 380, 148, "Seal and sign", "Signed with KC1", "chk x key", [
    ["What it does", "Writes the checksum of every file into one list and signs it with our signing key (KC1)."],
    ["Open items", "Who holds the signing key and where (S10, R2). Which machine is the build workstation (R1)."]]))
dv.append(inode("b_reh", 404, 220, 134, "Full install", "No GPU, no internet", "chk", [
    ["What it does", "Installs the bundle from start to finish in an offline VM, the same way the lab will."],
    ["Why", "There is no staging server. A missing file fails here instead of in the lab."],
    ["Limit", "It has no GPU, so GPU problems show up first in the lab."]]))
dv.append(label(412, 300, "Missing files"))
dv.append(label(412, 316, "fail here"))
dv.append(flow("M384,406 H522 V272", marker="da"))
dv.append(label(452, 400, "rehearse", "middle"))
dv.append(inode("t_media", 584, 220, 124, "Signed bundle", "Approved media", "x", [
    ["What crosses", "One bundle on approved transfer media. Nothing else enters, and nothing is downloaded inside the lab."],
    ["Open items", "Media type and turnaround (S3). How the lab checks media on arrival (R8)."]]))
dv.append(flow("M538,246 H584", marker="da"))
dv.append(label(561, 238, "passes", "middle"))
dv.append(inode("a_verify", 758, 150, 172, "verify.sh", "Must print PASS", "chk key", [
    ["What it does", "Checks the signature with our public key (KC2), every checksum, that no file was added, and that no model file can run code."],
    ["Open items", "Accepts any key in the admin's keyring (R5). Blocks known bad file types instead of allowing known good ones (R7)."]]))
dv.append(flow("M708,246 H733 V176 H758", marker="da"))
dv.append(inode("a_deploy", 758, 270, 172, "deploy.sh", "Installs in order", "", [
    ["What it does", "Installs Kubernetes on the four servers, the NVIDIA driver, the models, the platform, and the chat service."]]))
dv.append(flow("M844,202 V270", marker="da"))
dv.append(label(852, 242, "PASS"))
dv.append(inode("c_plat", 968, 150, 230, "RKE2 and GPU Operator", "Kubernetes and GPU support", "", [
    ["What it is", "The platform: Kubernetes on svc01-03 and gpu01, and NVIDIA's operator for the GPUs."]]))
dv.append(inode("c_reg", 968, 230, 230, "Image registry (Zarf)", "Only images from the bundle", "chk", [
    ["What it is", "Holds the images from the bundle. The cluster pulls only from here."]]))
dv.append(inode("c_app", 968, 310, 230, "SI chat service", "Chat page, gateway, models", "key", [
    ["What it is", "Phase 1: the chat page, gateway, language model, speech-to-text, and document search."],
    ["Keys", "Uses a TLS certificate signed by the lab CA (KC4)."]]))
dv.append(inode("c_upd", 968, 390, 230, "Updates", "Same path, one copy at a time", "", [
    ["How", "Every update is a new bundle through the same steps. Models are replaced one copy at a time, so two keep serving."]], dash="6 4"))
dv.append(flow("M930,296 H948 V176 H968", marker="da"))
dv.append(flow("M948,256 H968", marker="da"))
dv.append(flow("M948,296 V336 H968", marker="da"))
dv.append(inode("n_nostage", 16, 500, 396, "No staging server", "The rehearsal VM is the only test before the lab", "", [
    ["Decided", "2026-10-30. The money bought gpu01's third and fourth GPUs. Every install lands first on the production rack."]]))
dv.append(inode("n_noinet", 422, 500, 396, "No internet in the lab", "A missing file means a new bundle", "x", [
    ["Fact", "Nothing is downloaded inside the lab. Every service is set to make no outbound calls."]]))
dv.append(inode("n_scope", 828, 500, 396, "Phase 1: chat service only", "Analyst tools come in a later bundle", "", [
    ["Scope", "Phase 1 brings what the chat page needs. Analyst tools (Jupyter, VS Code, MATLAB) and the metrics pipeline come later, through the same path."]]))
dv.append("</svg>")
del_svg = "\n".join(dv)

# ---------- 3c. Deployment view: chat feature (goes in metrics_architecture.html) ----------
DINFO = {}


def dnode(key, x, y, w, title, sub, p, rows, h=50, sev="", dash="none"):
    DINFO[key] = dict(title=title, rows=rows)
    return node(key, x, y, w, h, title, sub, sev, attr="data-did", cls="vi", dash=dash).replace(
        f'data-p="{sev}"', f'data-p="{p}"', 1)


def dfilt(key, x, w, title, sub):
    return filt(key, x, 14, w, title, sub, "", "data-df").replace('width="396"', f'width="{w}"')


cv = ['<svg id="dchat" viewBox="0 0 1240 732" role="img" aria-label="Deployment view, chat feature: proposed physical and logical connections for the metrics pipeline">', defs("ca", "cx")]
cv.append(dfilt("path", 16, 296, "General user's access point", "Browser to the model and back"))
cv.append(dfilt("mgmt", 320, 296, "Admin and management", "Separate from general users' access"))
cv.append(dfilt("lab", 624, 296, "Lab provides", "Addresses, names, time, and certificates"))
cv.append(dfilt("ask", 928, 296, "Questions for the lab", "RF Network and Admin teams"))
cv.append(izone(16, 84, 436, 540, "Lab (existing)", "in", None, "9 6"))
cv.append(izone(464, 84, 760, 540, "Our rack (3221A, next to ACE 15)", "pf", "pf-f"))
cv.append(izone(680, 124, 530, 396, "Cluster (RKE2)", "k8", "k8-f"))
cv.append(izone(694, 156, 250, 352, "svc01-03", "k8", None, "6 4"))
cv.append(izone(958, 156, 240, 352, "gpu01", "si", "si-f"))
# lab, user side
cv.append(dnode("u_browser", 30, 120, 196, "User's browser", "User's workstation", "path", [
    ["What it is", "The user's normal lab browser. Nothing new is installed on the desk."],
    ["How it connects", "Over the lab network to https://chat.<lab-domain>. This is the only address that the cluster exposes for the chat feature."]]))
cv.append(dnode("l_net", 30, 258, 196, "Lab network", " ", "path", [
    ["What it is", "The lab's existing network between general users' machines and the lab core."],
    ["Load", "IDT's iDSO team has 200 users chatting and using SI agents, and uses about 10% of a 10G uplink at nominal peak load."]]))
cv.append(dnode("l_core", 30, 460, 196, "C9500X-28C8D", "Lab core (3 ports for us)", "path mgmt", [
    ["What it is", "The lab's core switch above rows 2 and 3 of 3221A, running IOS XE 17.15.06 (per Mr. Watkins)."],
    ["Decided", "Three ports between the lab core and the metrics analysis pipeline cluster: 2 x 100G data to sw01 and 1 x 10G management to oob01 (Mr. Watkins)."]], h=64))
cv.append(flow("M128,170 V258", marker="ca"))
cv.append(label(136, 218, "1G desk port"))
cv.append(label(136, 234, "(assumed)"))
cv.append(flow("M128,308 V460", marker="ca"))
cv.append(label(136, 388, "10G uplink"))
cv.append(label(136, 404, "(assumed)"))
# lab services
cv.append(dnode("l_dns", 242, 120, 196, "DNS name", "chat.<lab-domain>", "lab ask", [
    ["What it is", "The address users type in their browser to reach the chat page. The chat page's certificate must be issued for this address."],
    ["Questions", "What is the chat name, and which addresses does it point to? Which DNS servers should our servers use?"],
    ["Our default", "One name pointing at the three service nodes (svc01-03), so the chat page stays up if one node is down. Confirm in the rehearsal that the ingress answers on each node's address."]], dash="6 4"))
cv.append(dnode("l_ip", 242, 182, 196, "Addresses and VLANs", "Servers /27, BMCs /28 (Proposed)", "lab ask", [
    ["What it is", "The data addresses for the four servers (svc01-03 and gpu01), and separate management addresses for the BMCs, oob01, and sw01."],
    ["Why it matters", "RKE2 will not start without a default route on each node."],
    ["Questions", "Guidance on the server and BMC subnets, their default gateways, and the VLAN IDs. The VLANs are not decided yet."]], dash="6 4"))
cv.append(dnode("l_ntp", 242, 244, 196, "Time (NTP)", "Tick-Tock", "lab ask", [
    ["What it is", "The lab's time servers."],
    ["Why it matters", "The cluster database (etcd) and the certificates fail when the servers' clocks drift apart."],
    ["Question", "What are the NTP server addresses?"]], dash="6 4"))
cv.append(dnode("l_ca", 242, 306, 196, "Lab CA", "Signs the chat certificate", "lab ask", [
    ["What it is", "The lab's certificate authority. When it signs the chat certificate, users' browsers open the chat page without a warning."],
    ["Questions", "Does the lab have a CA? Who issues the certificate for the chat name? How long does it last? How is it renewed?"]], dash="6 4"))
cv.append(dnode("l_mgmt", 242, 368, 196, "Management access", "Who may reach the BMCs", "mgmt lab ask", [
    ["What it is", "The lab side of the 10G management link."],
    ["Questions", "Which VLAN will the BMCs join, and who can reach it?"],
    ["Our default", "Only lab admins can reach it. General users cannot."]], dash="6 4"))
# links into the rack
cv.append(flow("M226,479 H480", marker="ca"))
cv.append(label(350, 471, "2 x 100G, bonded (LACP)", "middle"))
cv.append(label(350, 497, "(discussed with Mr. Watkins)", "middle"))
cv.append(flow("M226,512 H458 V581 H480", marker="ca"))
cv.append(label(236, 530, "10G management link"))
cv.append(label(236, 546, "(discussed with Mr. Watkins)"))
cv.append(label(30, 600, "Dashed boxes are assumed to exist."))
# our rack: switches and console
cv.append(dnode("con", 480, 150, 180, "Rack console (con01)", "svc01's screen and admin work", "mgmt", [
    ["What it is", "The StarTech rack console, cabled to svc01. It is svc01's screen and keyboard."],
    ["Used for", "First switch setup, approved software setup, and RKE2 cluster admin (kubectl). In the current plan, all admin work is done here."],
    ["Question", "Who may be a cluster admin?"]]))
cv.append(flow("M660,175 H694", marker="ca"))
cv.append(dnode("sw01", 480, 454, 180, "sw01 data switch", "Nexus N93180YC-FX3", "path", [
    ["What it is", "Our rack's data switch. It has 2 x 100G uplinks to the lab's C9500X, bonded (LACP). Inside the rack, each server has 2 x 25G data links to it, also bonded."],
    ["Why our own switch", "Traffic between the chat page, gateway, and model stays inside the rack. This reduces attack vectors by giving each feature a single way in and out of the rack. It also allows performance tuning and load balancing inside the rack, and room for multi-server GPU work later."],
    ["First setup", "From svc01 over a USB-A to RJ45 console cable (on the HBOM). The cable can be removed after first setup if desired."]]))
cv.append(flow("M570,454 V213 H706", marker="ca"))
cv.append(label(578, 330, "2 x 25G to"))
cv.append(label(578, 346, "each server"))
cv.append(dnode("oob01", 480, 556, 180, "oob01 management", "C1300, BMC ports", "mgmt", [
    ["What it is", "A small Cisco C1300-24T-4X switch (on the HBOM), used as the out-of-band management switch. Each server's BMC port and sw01's management port connect to it."],
    ["Why separate", "Remote management still works if sw01 or the data links go down (Mr. Watkins's recommendation)."]]))
cv.append(line("M570,504 V556"))
cv.append(label(578, 534, "sw01 mgmt port"))
cv.append(dnode("bmc", 706, 556, 480, "Server BMCs", "gpu01 and svc01-03: power, screen, and software management", "mgmt", [
    ["What it is", "Each server's built-in remote management chip. It lets admins connect to the server remotely, even when the OS is down."],
    ["Power", "Admins can power each server on, off, or restart it from here."],
    ["Control", "Reachable only through oob01, on its own VLAN (a /28 suggested to Mr. Watkins, awaiting concurrence). It gives remote access and diagnostics when a server OS is down or fails, or when software must be installed or reinstalled."]]))
cv.append(line("M660,581 H706"))
cv.append('<path d="M819,556 V508 M1078,556 V508" fill="none" stroke="var(--edge)" stroke-width="1.6" stroke-dasharray="4 4"/>')
cv.append(label(827, 536, "one BMC in each server"))
# cluster
cv.append(dnode("fd", 706, 188, 226, "Ingress (Traefik)", "HTTPS 443 for the SI-Chat address", "path lab", [
    ["What it is", "RKE2's ingress controller. It is the only way for general users to reach SI-Chat from the lab network."],
    ["Control", "HTTPS on port 443 for the chat address only."],
    ["API address", "(Future phases) A second address that lets tools such as Jupyter or MATLAB call the model directly. It is not opened for the chat feature."],
    ["Certificate", "Comes from the lab CA and is loaded at install."]]))
cv.append(dnode("chat", 706, 252, 226, "Chat page (Open WebUI)", "Sign-in, chats, and uploads", "path", [
    ["What it is", "The web page general users open for SI-Chat and document uploads."],
    ["Sign-in", "To start, admins would create Local accounts. I know this is more to maintain in the short-term, but I'm hoping that it can be tracked as a POAM item until Keycloak is in place."],
    ["Single sign-on", "In future phases, we'd like to use Keycloak to connect to the lab's existing login."],
    ["Where it runs", "Kubernetes picks the node and the chats and uploads are stored within the chat-pages own volume."]]))
cv.append(dnode("gw", 706, 316, 226, "Gateway (LiteLLM)", "Inside the cluster only", "path", [
    ["What it is", "Every model request from the chat page goes through this gateway and is logged with the user."],
    ["Control", "LiteLLM has no address outside the cluster in the chat feature."]]))
cv.append(dnode("db", 706, 380, 226, "Database (PostgreSQL)", "Gateway's request log", "", [
    ["What it is", "PostgreSQL, run by the CloudNativePG operator. Holds the gateway's log of user requests."],
    ["Where it runs", "On the service nodes (svc01-03)."]]))
cv.append(dnode("tika", 706, 444, 226, "Text extraction (Tika)", "Uploaded documents, OCR", "", [
    ["What it is", "Apache Tika extracts text. When a user uploads documents, the chat page sends them to Tika. Tika separates the text from the file's formatting and metadata so the language model gets clean text."],
    ["Where it runs", "On the service nodes (svc01-03)."]]))
cv.append(flow("M819,238 V252", marker="ca"))
cv.append(flow("M819,302 V316", marker="ca"))
cv.append(flow("M819,366 V380", marker="ca"))
cv.append(dnode("llm", 970, 188, 216, "Language model (vLLM)", "gpt-oss-120b on 3 GPUs", "path", [
    ["What it is", "vLLM serving gpt-oss-120b. Three copies share the load, which keeps the chat available and response times low. During an update, two copies keep serving."],
    ["Weights", "About 65 GB, loaded from gpu01's NVMe."]]))
cv.append(dnode("stt", 970, 252, 216, "Speech-to-text", "Whisper on the fourth GPU", "", [
    ["What it is", "faster-whisper turns audio into text. Many of our systems record audio, and today someone has to listen to the playback. Where Tika pulls text from documents, faster-whisper pulls text from audio, so important times and events can be noted from the actual voices on the system. Users can also give it audio files such as .mp3."],
    ["Open items", "Which server program runs faster-whisper. The ready-made options are either no longer maintained or do not speak the API the chat page uses. The likely choice is a small server we write around faster-whisper."]]))
cv.append(dnode("emb", 970, 316, 216, "Embeddings", "Document search, on CPU", "", [
    ["What it is", "A small separate model that finds the parts of an uploaded document that match the question. gpt-oss-120b then writes the answer from those parts."],
    ["Where it runs", "On gpu01's CPU."],
    ["Open items", "Which embedding model meets the USA-only rule."]]))
cv.append(flow("M932,341 H970", marker="ca"))
cv.append(label(972, 400, "4 x RTX PRO 6000"))
cv.append(label(972, 416, "Model files on its own NVMe"))
cv.append(flow("M946,341 V213 H970", marker="ca"))
cv.append(flow("M946,277 H970", marker="ca"))
# questions for the network team
cv.append(label(16, 652, "These items need to be worked through with the Network and Admin teams. We deferred these discussions until after the HBOM was finalized."))
QS = [("q1", "Addresses", "Subnets, gateways, and VLAN IDs",
       "Requested subnets for the servers (/27) and BMCs (/28), their default gateways, and the VLAN IDs. These are needed to complete the install."),
      ("q2", "Names and time", "Chat name, DNS, and NTP servers",
       "The chat name and which addresses it points to, the lab's DNS servers, and the lab's NTP servers."),
      ("q3", "Certificate", "Lab CA signs chat.<lab-domain>",
       "Who issues the chat's certificate from the lab's CA? How long will it last? How will it be renewed?"),
      ("q4", "Switch and access rules", "LACP, trunk, MTU, 802.1X, 443",
       "One lab switch or a vPC pair? L2 trunk or routed link? What MTU? Does the lab use 802.1X/NAC or port security on these ports? Which lab networks may reach port 443 on the chat address?")]
for i, (k, ti, su, ask) in enumerate(QS):
    cv.append(dnode(k, 16 + i * 304, 664, 296, ti, su, "ask", [["Questions" if ask.count("?") != 1 else "Question", ask]], h=52, sev="high"))
cv.append("</svg>")
dchat_svg = "\n".join(cv)

# ---------- 3d. Deployment view: analyst tools (phase 2, goes in metrics_architecture.html) ----------
DASH = '<path d="{}" fill="none" stroke="var(--edge)" stroke-width="1.6" stroke-dasharray="5 4"/>'
tv = ['<svg id="dtools" viewBox="0 0 1240 732" role="img" aria-label="Deployment view, analyst tools: analysts reach the same SI service from their own tools through a second address">', defs("tva", "tvx")]
tv.append(dfilt("path", 16, 296, "Analyst's request path", "Tool to the model and back"))
tv.append(dfilt("key", 320, 296, "Keys and logging", "Who is asking, and the record"))
tv.append(dfilt("new", 624, 296, "New in this phase", "Everything else is the chat feature"))
tv.append(dfilt("ask", 928, 296, "Decisions for the ISSM", "Needed before this bundle is built"))
tv.append(izone(16, 84, 436, 540, "Lab (existing)", "in", None, "9 6"))
tv.append(izone(464, 84, 760, 540, "Our rack (3221A, next to ACE 15)", "pf", "pf-f"))
tv.append(izone(680, 124, 530, 396, "Cluster (RKE2)", "k8", "k8-f"))
tv.append(izone(694, 156, 250, 352, "svc01-03", "k8", None, "6 4"))
tv.append(izone(958, 156, 240, 352, "gpu01", "si", "si-f"))
tv.append(izone(24, 118, 212, 260, "Analyst workstations", "wb", "wb-f"))
# analyst side
tv.append(dnode("t_jup", 34, 150, 192, "Jupyter", "Jupyter AI chat and %%ai", "path new", [
    ["What it is", "Jupyter AI adds an SI chat sidebar to JupyterLab 4, and a %%ai cell command that works in any notebook."],
    ["Setup", "Installed from the bundle's clients/ folder with pip, with no internet. Anaconda users install into their own environment so their existing packages are not replaced."],
    ["Settings", "Base URL https://api.<lab-domain>/v1, model gpt-oss-120b, and the analyst's own key."]], h=48))
tv.append(dnode("t_vsc", 34, 206, 192, "VS Code", "Continue extension", "path new", [
    ["What it is", "The Continue extension gives VS Code an SI chat panel and code help."],
    ["Setup", "Installed from the .vsix file in the bundle's clients/ folder. Telemetry is turned off in its settings."]], h=48))
tv.append(dnode("t_mat", 34, 262, 192, "MATLAB", "webwrite, no toolbox", "path new", [
    ["What it is", "MATLAB calls SI with webwrite, which MATLAB already has. Nothing is installed."],
    ["Lab IT", "MATLAB may make HTTPS calls to an internal service (L4)."],
    ["Example", "In the software delivery doc, section 5."]], h=48))
tv.append(dnode("t_py", 34, 318, 192, "Python scripts", "OpenAI client library", "path new", [
    ["What it is", "Any Python script can call SI with the openai package, pointed at the lab address instead of the internet."],
    ["Python versions", "Packages in the bundle cover Python 3.9 to 3.15 on Windows and Linux (L3)."]], h=48))
tv.append(flow("M128,378 V396", marker="tva"))
tv.append(dnode("t_net", 30, 396, 196, "Lab network", "Same links as the chat page", "path", [
    ["What it is", "The lab's existing network. Requests from the tools use the same desk ports and uplink as the chat page."]]))
tv.append(flow("M128,446 V460", marker="tva"))
tv.append(dnode("t_core", 30, 460, 196, "C9500X-28C8D", "Lab core (3 ports for us)", "path", [
    ["What it is", "The lab's core switch. No new ports or links for this phase."]], h=64))
tv.append(dnode("t_dns", 242, 132, 196, "DNS name", "api.<lab-domain>", "ask new", [
    ["What it is", "A second name for the tools to use. It points at the same three service nodes as the chat name."],
    ["Question", "What should the name be?"]], dash="6 4"))
tv.append(dnode("t_ca", 242, 194, 196, "Lab CA", "Signs the API certificate", "new", [
    ["What it is", "The same lab CA as the chat feature, signing one more certificate for the API name."]], dash="6 4"))
tv.append(dnode("t_pcs", 242, 256, 196, "Software on analyst PCs", "Who installs it, and how", "ask new", [
    ["What it is", "The Python packages and the VS Code extension go on analysts' own machines. That is the first time this project puts anything on a desk."],
    ["Size", "100 or more Python packages per platform, plus one extension."],
    ["Scanning", "Container images are scanned today. The packages and extension would be scanned before transfer too (R4)."],
    ["Question", "Who installs them: the analysts, or Lab IT?"]], dash="6 4"))
tv.append(dnode("t_key", 242, 318, 196, "Personal key", "One per analyst", "key ask new", [
    ["What it is", "Each analyst gets their own key (KC7), made by an admin with deploy.sh user-key. The tool sends it with every request."],
    ["Where it lives", "In an environment variable or the tool's secret setting, never in a notebook or script that gets shared (R28)."],
    ["If it leaks", "An admin revokes it and the next request is refused. Every request made with it is in the gateway's log."]], dash="6 4"))
tv.append(DASH.format("M242,281 H236"))
tv.append(DASH.format("M242,343 H236"))
tv.append(flow("M226,479 H480", marker="tva"))
tv.append(label(350, 471, "same 2 x 100G links", "middle"))
tv.append(label(30, 600, "Dashed boxes are assumed to exist or are still open."))
# rack
tv.append(dnode("t_clients", 480, 150, 180, "clients/ folder", "In the signed bundle", "new", [
    ["What it is", "The Python packages (wheels) and the VS Code extension, pulled on the build workstation and carried in the same signed bundle as everything else."],
    ["Today", "Left out of the phase 1 bundle. It is added only when this phase is approved (WITH_CLIENTS=1)."]]))
tv.append(DASH.format("M480,175 H458 V281 H438"))
tv.append(label(470, 236, "carried to"))
tv.append(label(470, 252, "analyst PCs"))
tv.append(dnode("t_sw", 480, 454, 180, "sw01 data switch", "No change", "path", [
    ["What it is", "Our rack's data switch. The tools' requests come in on the same bonded links as the chat page."]]))
tv.append(flow("M570,454 V213 H706", marker="tva"))
# cluster
tv.append(dnode("t_fd", 706, 188, 226, "Ingress (Traefik)", "chat and api addresses, HTTPS 443", "path new", [
    ["What it is", "The same ingress controller. It answers a second name, api.<lab-domain>, for the tools."],
    ["Control", "Only the model paths are open on the API address. The gateway's admin page and admin API stay blocked (R19)."],
    ["How", "deploy.sh apps --api-host. The phase 1 install leaves it out, so there is no API address today."]]))
tv.append(dnode("t_gw", 706, 252, 226, "Gateway (LiteLLM)", "Checks the key, logs the request", "path key new", [
    ["What it is", "The same gateway the chat page uses. Every request from a tool must carry a personal key."],
    ["Control", "Each key can have its own limits and can be revoked at any time. The model has no other way in."]]))
tv.append(dnode("t_db", 706, 316, 226, "Database (PostgreSQL)", "Every request, by key", "key", [
    ["What it is", "The same PostgreSQL. The gateway records each request against the analyst's key, so every call can be traced to a person."]]))
tv.append(dnode("t_chat", 706, 380, 226, "Chat page (Open WebUI)", "No change", "", [
    ["What it is", "The chat feature keeps working as before. Analysts can use either one."]], dash="6 4"))
tv.append(flow("M819,238 V252", marker="tva"))
tv.append(flow("M819,302 V316", marker="tva"))
tv.append(dnode("t_llm", 970, 188, 216, "Language model (vLLM)", "Same gpt-oss-120b copies", "path", [
    ["What it is", "The same three copies of gpt-oss-120b serve the chat page and the tools."],
    ["Load", "Tools can send longer and more frequent requests than people typing. The per-key limits keep one script from slowing everyone else down."]]))
tv.append(dnode("t_stt", 970, 252, 216, "Speech-to-text", "Same Whisper", "", [
    ["What it is", "Tools can send audio files through the same gateway address."]]))
tv.append(dnode("t_emb", 970, 316, 216, "Embeddings", "Same model", "", [
    ["What it is", "Tools can use the same embedding model for their own document search."]]))
tv.append(flow("M932,277 H950 V213 H970", marker="tva"))
tv.append(flow("M950,277 H970", marker="tva"))
tv.append(flow("M950,277 V341 H970", marker="tva"))
tv.append(label(972, 400, "4 x RTX PRO 6000"))
tv.append(label(972, 416, "No new hardware"))
# decisions for the ISSM
tv.append(label(16, 652, "These need ISSM decisions before the analyst tools bundle is built."))
TQS = [("tq1", "Open the API address", "api.<lab-domain>, model paths only",
        "May we open a second address to the lab network, with only the model paths reachable and the gateway's admin paths blocked (R19)?"),
       ("tq2", "Software on analyst PCs", "Python packages and one extension",
        "May analysts install the Python packages and the VS Code extension from the bundle, after they are scanned (R4)? Who installs them?"),
       ("tq3", "Keys on workstations", "One personal key per analyst",
        "Is a personal key kept in an environment variable acceptable (R28), or must analyst access wait for single sign-on?"),
       ("tq4", "Who gets access", "Which analysts, approved by whom",
        "Which analysts or groups get a key, who approves each one, and how often are keys reviewed?")]
for i, (k, ti, su, ask) in enumerate(TQS):
    tv.append(dnode(k, 16 + i * 304, 664, 296, ti, su, "ask", [["Questions" if ask.count("?") != 1 else "Question", ask]], h=52, sev="high"))
tv.append("</svg>")
dtools_svg = "\n".join(tv)


# ---------- 4. Shared CSS ----------
VIEWS = ["phs", "sec", "del", "keys", "rev"]
SHARED_CSS = """:root { --deny: #c0262d; --deny-f: #fdecec; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --deny: #ff7b7b; --deny-f: #3b1618; } }
:root[data-theme="dark"] { --deny: #ff7b7b; --deny-f: #3b1618; }
.promise-t { font-size: 15px; font-weight: 700; }
.sflow-x { fill: none; stroke: var(--deny); stroke-width: 2.2; stroke-dasharray: 6 5; }
.key-item, .rev-item, .vi { transition: opacity .25s; }
.sdim { opacity: 0.15; }
#panel dl.facts { margin: 10px 0 0; }
#panel dl.facts dt { font-weight: 700; font-size: 13px; margin-top: 10px; color: var(--ink); }
#panel dl.facts dd { margin: 2px 0 0; font-size: 14px; line-height: 1.45; }
#panel .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 700; margin-right: 6px; border: 1.5px solid; }
#panel .b-crit, #panel .b-high { color: var(--deny); border-color: var(--deny); background: var(--deny-f); }
#panel .b-med { color: var(--z3); border-color: var(--z3); background: var(--z3-f); }
#panel .b-hi2 { color: var(--z3); border-color: var(--z3); background: var(--z3-f); }
#panel .b-low, #panel .b-mod { color: var(--pf); border-color: var(--pf); background: var(--pf-f); }
"""
base_css = re.search(r"<style>.*?</style>", t, re.S).group(0)

# ---------- 5. metrics_architecture.html: Deployment view, chat feature ----------
css = """<!-- GEN:CSS START -->
<style>
""" + SHARED_CSS + """#dchat { display: none; }
.dmodes { display: none; margin: 0 0 10px; }
body:has(#m-deploy:checked) .dmodes { display: inline-flex; }
html[data-deployment="off"] .dmodes { display: none !important; }
body:has(#m-deploy:checked) #topo, body:has(#m-deploy:checked) label.toggle { display: none !important; }
#dtools { display: none; }
html:not([data-deployment="off"]) body:has(#m-deploy:checked):has(#d-chat:checked) #dchat { display: block; }
html:not([data-deployment="off"]) body:has(#m-deploy:checked):has(#d-tools:checked) #dtools { display: block; }
.dmodes label.todo { text-decoration: line-through; opacity: 0.55; pointer-events: none; cursor: not-allowed; }
.dmodes label.todo::after { content: " (TODO)"; text-decoration: none; display: inline-block; margin-left: 4px; font-size: 0.8em; }
</style>
<!-- GEN:CSS END -->"""
t = t.replace("</head>", css + "</head>", 1)

dswitch = ('<!-- GEN:DSWITCH START --><div class="modes dmodes" role="radiogroup" aria-label="Deployment view">'
           '<input type="radio" name="dview" id="d-chat" checked><label for="d-chat">Chat feature (Proposed)</label>'
           '<input type="radio" name="dview" id="d-tools"><label for="d-tools">Analyst tools (Proposed)</label>'
           + "".join(f'<input type="radio" name="dview" id="d-{k}" disabled><label for="d-{k}" class="todo">{n}</label>'
                     for k, n in [("plat", "Platform services"), ("pipe", "Metrics pipeline")]) +
           '</div><!-- GEN:DSWITCH END -->')
anchor = '<div class="diagram"><svg id="svg"'
assert anchor in t
t = t.replace(anchor, dswitch + anchor, 1)

topo_end = t.index("</svg>", t.index("<svg id=\"topo\""))
t = t[:topo_end + len("</svg>")] + "<!-- GEN:SVG START -->\n" + dchat_svg + "\n" + dtools_svg + "\n<!-- GEN:SVG END -->" + t[topo_end + len("</svg>"):]

main_js = """<!-- GEN:JS START -->
<script>
(() => {
const INFO = %s;
const panel = document.getElementById("panel");
const e = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
const OVER = {dchat: `<h2>Deployment: chat feature (Proposed)</h2><p class="kind">Proposed connection between our rack and the existing lab infrastructure</p>
  <p>Users reach the chat page from their browser. The traffic goes through the lab network and the lab core identified by Mr. Watkins, then into sw01 and the cluster. The chat page is intended to be the only thing users can reach.</p>
  <p>Management has its own link through oob01, the small out-of-band management switch in our rack, so the BMCs can still be reached if the data side goes down. Mr. Watkins asked us to keep the data and management links separate. In this setup, admin work is done at the rack console on svc01.</p>
  <p>The amber boxes at the bottom are items to work through with the RF Network and Admin teams, so our setup fits their existing schemes. Dashed boxes are assumed to exist.</p>`,
  dtools: `<h2>Deployment: analyst tools (Proposed)</h2><p class="kind">Phase 2: the same SI service, reached from analysts' own tools</p>
  <p>Analysts call SI from Jupyter, VS Code, MATLAB, and Python scripts. Each request goes over the lab network to a second address, api.&lt;lab-domain&gt;, and into the same gateway the chat page uses. The model, the GPUs, and the rack do not change.</p>
  <p>Each analyst gets a personal key. The gateway checks it on every request, logs the request against it, and an admin can revoke it at any time.</p>
  <p>The tools come in the same signed bundle, in a clients/ folder. The amber boxes at the bottom are the decisions the ISSM needs to make before this phase. Dashed boxes are assumed to exist or are still open.</p>`};
const SVGS = ["dchat", "dtools"].map(id => document.getElementById(id));
const current = () => document.getElementById("d-tools").checked ? "dtools" : "dchat";
function select(svg, g) { svg.querySelectorAll(".tnode.sel").forEach(x => x.classList.remove("sel")); if (g) g.classList.add("sel"); }
function focus(svg, p) { svg.querySelectorAll(".vi").forEach(x => x.classList.toggle("sdim", !!p && !(x.dataset.p || "").split(" ").includes(p))); }
function bind(g, go) {
  g.addEventListener("click", ev => { ev.stopPropagation(); go(); });
  g.addEventListener("keydown", ev => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); go(); } });
}
SVGS.forEach(svg => {
  svg.querySelectorAll(".tnode[data-did]").forEach(g => bind(g, () => {
    focus(svg, null); select(svg, g); const d = INFO[g.dataset.did];
    panel.innerHTML = `<h2>${e(d.title)}</h2><dl class="facts">${d.rows.map(([a, b]) => `<dt>${e(a)}</dt><dd>${e(b)}</dd>`).join("")}</dl>`;
  }));
  svg.querySelectorAll(".filt").forEach(g => bind(g, () => {
    const on = !g.classList.contains("sel"); select(svg, on ? g : null); focus(svg, on ? g.dataset.df : null);
    panel.innerHTML = OVER[svg.id];
  }));
});
function sync() {
  if (!document.getElementById("m-deploy").checked) return;
  SVGS.forEach(svg => { focus(svg, null); select(svg, null); }); panel.innerHTML = OVER[current()];
}
document.querySelectorAll('input[name="dview"]').forEach(r => r.addEventListener("change", sync));
document.querySelectorAll('input[name="mode"]').forEach(r => r.addEventListener("change", sync));
})();
</script>
<!-- GEN:JS END -->""" % json.dumps(DINFO)
t = t.replace("</body>", main_js + "</body>", 1)
page.write_text(t)

# ---------- 6. program_views.html: Phases, Security, Delivery, Keys, Review ----------
KEYDATA = {k: dict(title=v["title"], damage=v.get("damage", ""), rows=v["rows"], s=v.get("summary", {})) for k, v in keys.items()}
EXTRA = {
    "bundle": dict(title="Release bundle", damage="", rows=[["What it is", "Everything phase 1 brings in, on one approved transfer drive, with a list of every file's checksum. The list is signed with KC1."], ["Why it matters", "The signature is what lets the lab trust the bundle. Without it, the checksums only prove the copy is complete, not who made it."]], s={}),
    "verify": dict(title="verify.sh", damage="", rows=[["What it does", "Runs in the lab before anything is installed. It checks the signature with KC2, every file's checksum, that no file was added, and that no model file can run code when loaded."], ["Known gap", "It accepts a signature from any key in the admin's keyring, not only ours (finding R5). Fix before transfer."]], s={}),
}
KEYDATA.update(EXTRA)
REVDATA = {f["id"]: f for f in findings}
AREANAME = dict(areas)

prog_js = """<script>
(() => {
const KEYS = %s;
const REV = %s;
const AREAS = %s;
const SHORT = %s;
const INFO = %s;
const panel = document.getElementById("panel");
const e = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
const dmgClass = d => /^critical/i.test(d) ? "b-crit" : /^high/i.test(d) ? "b-hi2" : "b-mod";
const svgK = document.getElementById("keys"), svgR = document.getElementById("rev");
function select(svg, g) { svg.querySelectorAll(".tnode.sel").forEach(x => x.classList.remove("sel")); if (g) g.classList.add("sel"); }
function focus(svg, cls, p) { svg.querySelectorAll("." + cls).forEach(x => x.classList.toggle("sdim", !!p && !(x.dataset.p || "").split(" ").includes(p))); }
function bind(g, go) {
  g.addEventListener("click", ev => { ev.stopPropagation(); go(); });
  g.addEventListener("keydown", ev => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); go(); } });
}
function keysOverview() {
  return `<h2>Keys view</h2><p class="kind">Every key, password, and certificate in phase 1</p>
  <p><b>A key is a secret that proves who you are or unlocks something.</b> Whoever holds it can do what it allows.</p>
  <p>Each box is one secret, placed where it lives. Arrows show what it controls.</p>
  <p><b>If stolen:</b></p>
  <p><span class="badge b-crit">Red</span> someone could put their own software into the lab, or take over.</p>
  <p><span class="badge b-hi2">Amber</span> someone could read other people's data, or act as them.</p>
  <p><span class="badge b-mod">Gray</span> someone could use the service without being identified.</p>
  <p>Dashed boxes are held by someone else, or not managed yet. Select a box for what it protects, what happens if it is stolen, and who sets it. Full list: docs/cyber/14.</p>`;
}
function revOverview() {
  return `<h2>Review view</h2><p class="kind">Our own security review, before meeting the ISSM</p>
  <p>Each box is one issue we found in the plan as it is today. Columns follow the path: building the bundle, carrying it in, the cluster, the services, the data. Models and process are on the right.</p>
  <p><span class="badge b-high">Red</span>high <span class="badge b-med">Amber</span>medium <span class="badge b-low">Gray</span>low</p>
  <p>Use the buttons at the top to see what needs an ISSM decision, or what must be fixed before the transfer or before users. Select any issue for how it could be misused and the fix. Full list: docs/cyber/15.</p>`;
}
const OVER = {
  phs: `<h2>Phases view</h2><p class="kind">What goes in when, and what each phase needs first</p>
  <p>Each column is a phase, named by what analysts can do when it is finished. Arrows show what a phase needs first.</p>
  <p><b>Step one</b> (shaded) is phases 0 and 1: get the ISSM's approvals and the hardware in, then give analysts SI through the chat page. Everything else waits.</p>
  <p>Red boxes are what the ISSM decides. Phase 0's questions are the first ones to ask, because nothing can start without them.</p>
  <p>Phases 2 and 3 do not depend on each other. The prototype plan's P0 to P3 are the work steps inside step one.</p>
  <p>Select any box for details. The software list with download links is doc 16.</p>`,
  sec: `<h2>Security view</h2><p class="kind">Phase 1: SI through the chat page</p>
  <p>How phase 1 keeps the chat service closed and recorded. Each box is one part of the system, placed where it runs.</p>
  <p>Use the four buttons at the top to see which parts carry each promise. Red dashed lines are paths that are blocked.</p>
  <p>Select a box for what it does, the control it provides, and what is still open. Open items point to the decision register (S) and our review (R).</p>`,
  del: `<h2>Delivery view</h2><p class="kind">How a release gets into the lab</p>
  <p>Everything is downloaded on a build workstation outside the lab, checked, and sealed into one signed bundle.</p>
  <p>The bundle is installed first in an offline VM on that workstation. There is no staging server. If it passes, the same bundle crosses on approved media, and verify.sh must print PASS before anything is installed.</p>
  <p>The buttons at the top show where files are checked, what crosses, and where keys are used.</p>`,
};
function showInfo(svg, id, g) {
  const d = INFO[id]; select(svg, g);
  panel.innerHTML = `<h2>${e(d.title)}</h2><dl class="facts">${d.rows.map(([a, b]) => `<dt>${e(a)}</dt><dd>${e(b)}</dd>`).join("")}</dl>`;
}
["phs", "sec", "del"].forEach(v => {
  const svg = document.getElementById(v);
  svg.querySelectorAll(".tnode[data-iid]").forEach(g => bind(g, () => { focus(svg, "vi", null); svg.querySelectorAll(".filt.sel").forEach(x => x.classList.remove("sel")); showInfo(svg, g.dataset.iid, g); }));
  svg.querySelectorAll(".filt").forEach(g => bind(g, () => {
    const on = !g.classList.contains("sel"); select(svg, on ? g : null); focus(svg, "vi", on ? g.dataset.f : null);
    panel.innerHTML = OVER[v];
  }));
});
function showKey(k, g) {
  const d = KEYS[k]; select(svgK, g);
  const rows = d.rows.map(([a, b]) => `<dt>${e(a)}</dt><dd>${e(b)}</dd>`).join("");
  const s = d.s || {};
  const meta = s.by ? `<dt>Created by</dt><dd>${e(s.by)}</dd><dt>Lives in</dt><dd>${e(s.where)}</dd><dt>Expires</dt><dd>${e(s.expires)}</dd>` : "";
  const have = new Set(d.rows.map(r => r[0]));
  panel.innerHTML = `<h2>${e(d.title)}</h2><p class="kind">${k.startsWith("KC") ? e(k) : "Not a key"}${d.damage ? `, <span class="badge ${dmgClass(d.damage)}">${e(d.damage.split(" ")[0])} if stolen</span>` : ""}</p>
    <dl class="facts">${rows}${have.has("Created by") || have.has("Who sets it") ? "" : meta}</dl>`;
}
function showRev(id, g) {
  const f = REV[id]; select(svgR, g);
  const sev = {High: "b-high", Medium: "b-med", Low: "b-low"}[f.sev];
  panel.innerHTML = `<h2>${e(id)}. ${e(SHORT[id])}</h2>
    <p class="kind">${e(AREAS[f.area])}</p>
    <p><span class="badge ${sev}">${e(f.sev)}</span><span class="badge b-low">${e(f.when)}</span>${f.new ? '<span class="badge b-low">New</span>' : ""}</p>
    <dl class="facts"><dt>What we found</dt><dd>${e(f.finding)}</dd><dt>How it could be misused</dt><dd>${e(f.misuse)}</dd>
    <dt>Fix</dt><dd>${e(f.fix)}</dd><dt>Control family (NIST 800-53)</dt><dd>${e(f.control)}</dd></dl>`;
}
svgK.querySelectorAll(".tnode[data-kid]").forEach(g => bind(g, () => { focus(svgK, "key-item", null); svgK.querySelectorAll(".filt.sel").forEach(x => x.classList.remove("sel")); showKey(g.dataset.kid, g); }));
svgR.querySelectorAll(".tnode[data-rid]").forEach(g => bind(g, () => { focus(svgR, "rev-item", null); svgR.querySelectorAll(".filt.sel").forEach(x => x.classList.remove("sel")); showRev(g.dataset.rid, g); }));
svgK.querySelectorAll(".filt").forEach(g => bind(g, () => {
  const on = !g.classList.contains("sel"); select(svgK, on ? g : null); focus(svgK, "key-item", on ? g.dataset.kf : null);
  if (!on) panel.innerHTML = keysOverview();
}));
svgR.querySelectorAll(".filt").forEach(g => bind(g, () => {
  const on = !g.classList.contains("sel"); select(svgR, on ? g : null); focus(svgR, "rev-item", on ? g.dataset.rf : null);
  if (!on) panel.innerHTML = revOverview();
}));
document.querySelectorAll('input[name="mode"]').forEach(r => r.addEventListener("change", () => {
  focus(svgK, "key-item", null); focus(svgR, "rev-item", null); select(svgK, null); select(svgR, null);
  ["phs", "sec", "del"].forEach(v => { const s = document.getElementById(v); focus(s, "vi", null); select(s, null); if (document.getElementById("m-" + v).checked) panel.innerHTML = OVER[v]; });
  if (document.getElementById("m-keys").checked) panel.innerHTML = keysOverview();
  if (document.getElementById("m-rev").checked) panel.innerHTML = revOverview();
}));
{ const c = document.querySelector('input[name="mode"]:checked'); if (c) c.dispatchEvent(new Event("change")); }
})();
</script>""" % (json.dumps(KEYDATA), json.dumps(REVDATA), json.dumps(AREANAME), json.dumps(SHORT), json.dumps(INFO))

hide = []
for v in VIEWS:
    hide.append(f"#{v} {{ display: none; }}\nbody:has(#m-{v}:checked) #{v} {{ display: block; }}")
NAMES = {"phs": "Phases", "sec": "Security", "del": "Delivery", "keys": "Keys", "rev": "Review"}
radios = "".join(f'<input type="radio" name="mode" id="m-{v}"{" checked" if v == "phs" else ""}><label for="m-{v}">{NAMES[v]}</label>' for v in VIEWS)
prog = f"""<!DOCTYPE html>
<!-- Generated by docs/diagrams/build_arch_views.py from docs/cyber/14 and 15. Edit those or the script, not this file. -->
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Program views</title>
{base_css}
<style>
{SHARED_CSS}{chr(10).join(hide)}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Program views</h1>
    <p>Planning and security views for the chat feature, kept apart from the architecture page. Phases shows what goes in when. Security, Delivery, Keys, and Review show how the chat feature is kept closed, how a release gets into the lab, every key, and our own findings before the ISSM meeting.</p>
  </header>
  <div class="controls">
    <div class="modes" role="radiogroup" aria-label="View">{radios}</div>
  </div>
  <div class="layout">
    <div>
      <div class="diagram">
{phs_svg}
{sec_svg}
{del_svg}
{keys_svg}
{rev_svg}
      </div>
    </div>
    <aside aria-live="polite"><div id="panel"></div></aside>
  </div>
</div>
{prog_js}
</body></html>
"""
(repo / "program_views.html").write_text(prog)
print(f"deployment items {len(DINFO)}; info items {len(INFO)}; findings {len(findings)} areas {len(areas)} keys {len([k for k in keys if k.startswith('KC')])}")
