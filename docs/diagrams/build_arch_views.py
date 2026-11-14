"""Add the Security, Delivery, Keys, and Review views to metrics_architecture.html.

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


# ---------- 4. CSS, radios, JS ----------
VIEWS = ["sec", "del", "keys", "rev"]
hide = []
for v in VIEWS:
    others = ", ".join(f"body:has(#m-{v}:checked) #{o}" for o in ["svg", "topo"] + [w for w in VIEWS if w != v])
    hide.append(f"#{v} {{ display: none; }}\n{others} {{ display: none !important; }}\nbody:has(#m-{v}:checked) #{v} {{ display: block; }}")
    hide.append(f"body:has(#m-{v}:checked) .legend, body:has(#m-{v}:checked) .js-only, body:has(#m-{v}:checked) ol.steps {{ display: none !important; }}")
css = """<!-- GEN:CSS START -->
<style>
:root { --deny: #c0262d; --deny-f: #fdecec; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --deny: #ff7b7b; --deny-f: #3b1618; } }
:root[data-theme="dark"] { --deny: #ff7b7b; --deny-f: #3b1618; }
""" + "\n".join(hide) + """
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
</style>
<!-- GEN:CSS END -->"""
t = t.replace("</head>", css + "</head>", 1)

radios = ('<!-- GEN:RADIO START -->'
          '<input type="radio" name="mode" id="m-sec"><label for="m-sec">Security</label>'
          '<input type="radio" name="mode" id="m-del"><label for="m-del">Delivery</label>'
          '<input type="radio" name="mode" id="m-keys"><label for="m-keys">Keys</label>'
          '<input type="radio" name="mode" id="m-rev"><label for="m-rev">Review</label>'
          '<!-- GEN:RADIO END -->')
anchor = '<input type="radio" name="mode" id="m-deploy"><label for="m-deploy">Deployment</label>'
assert anchor in t
t = t.replace(anchor, anchor + radios, 1)

svgs = "<!-- GEN:SVG START -->\n" + sec_svg + "\n" + del_svg + "\n" + keys_svg + "\n" + rev_svg + "\n<!-- GEN:SVG END -->"
del_end = t.index("</svg>", t.index("<svg id=\"topo\""))
t = t[:del_end + len("</svg>")] + svgs + t[del_end + len("</svg>"):]

KEYDATA = {k: dict(title=v["title"], damage=v.get("damage", ""), rows=v["rows"], s=v.get("summary", {})) for k, v in keys.items()}
EXTRA = {
    "bundle": dict(title="Release bundle", damage="", rows=[["What it is", "Everything phase 1 brings in, on one approved transfer drive, with a list of every file's checksum. The list is signed with KC1."], ["Why it matters", "The signature is what lets the lab trust the bundle. Without it, the checksums only prove the copy is complete, not who made it."]], s={}),
    "verify": dict(title="verify.sh", damage="", rows=[["What it does", "Runs in the lab before anything is installed. It checks the signature with KC2, every file's checksum, that no file was added, and that no model file can run code when loaded."], ["Known gap", "It accepts a signature from any key in the admin's keyring, not only ours (finding R5). Fix before transfer."]], s={}),
}
KEYDATA.update(EXTRA)
REVDATA = {f["id"]: f for f in findings}
AREANAME = dict(areas)

js = """<!-- GEN:JS START -->
<script>
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
["sec", "del"].forEach(v => {
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
  ["sec", "del"].forEach(v => { const s = document.getElementById(v); focus(s, "vi", null); select(s, null); if (document.getElementById("m-" + v).checked) panel.innerHTML = OVER[v]; });
  if (document.getElementById("m-keys").checked) panel.innerHTML = keysOverview();
  if (document.getElementById("m-rev").checked) panel.innerHTML = revOverview();
}));
})();
</script>
<!-- GEN:JS END -->""" % (json.dumps(KEYDATA), json.dumps(REVDATA), json.dumps(AREANAME), json.dumps(SHORT), json.dumps(INFO))
t = t.replace("</body>", js + "</body>", 1)
page.write_text(t)
print(f"info items {len(INFO)}; findings {len(findings)} areas {len(areas)} keys {len([k for k in keys if k.startswith('KC')])}")
