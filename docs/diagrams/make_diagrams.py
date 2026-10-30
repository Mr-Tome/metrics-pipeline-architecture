import os, sys
OUT = sys.argv[1]
FONT = "font-family='Helvetica, Arial, sans-serif'"

def svg(w, h, body, title):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' {FONT}>"
            f"<title>{title}</title><rect width='{w}' height='{h}' fill='#ffffff'/>{body}</svg>\n")

def rect(x, y, w, h, fill, stroke="#333", sw=1, rx=0):
    return f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}' rx='{rx}'/>"

def text(x, y, s, size=12, anchor="start", weight="normal", fill="#111"):
    return f"<text x='{x}' y='{y}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' fill='{fill}'>{s}</text>"

def line(x1, y1, x2, y2, color="#333", sw=2, dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{color}' stroke-width='{sw}'{d}/>"

def path(d, color="#333", sw=2, dash=None):
    da = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<path d='{d}' fill='none' stroke='{color}' stroke-width='{sw}'{da}/>"

C = dict(gpu="#c8e6c9", gpur="#eeeeee", svc="#bbdefb", sw="#ffe0b2", oob="#fff9c4", patch="#d7ccc8",
         blank="#fafafa", A="#c62828", B="#1565c0", fiber="#ef6c00", dac="#212121", cu="#2e7d32", mgmt="#6a1b9a")

# ---------------------------------------------------------------- rack elevation
U = 16
LAYOUT = {  # top U of each item: (height in U, label, color)
    42: (1, "Blanking (fiber patch panel later, if the lab adds one)", C["patch"]),
    41: (1, "sw01  Lab switch, Dell S5248F-ON (ports face rear)", C["sw"]),
    40: (1, "oob01  1G management switch (ports face rear)", C["oob"]),
    21: (1, "con01  Rack console, 1U LCD and keyboard (pull out to use)", C["patch"]),
    7: (1, "svc03  Service node, 1U", C["svc"]),
    6: (1, "svc02  Service node, 1U", C["svc"]),
    5: (1, "svc01  Service node, 1U", C["svc"]),
    4: (2, "RESERVED gpu02 (100-user growth), blanking panels", C["gpur"]),
    2: (2, "gpu01  GPU server, 2U, 4 x RTX PRO 6000 (all slots)", C["gpu"]),
}

def rack(x0, y0, title, rear=False):
    w = 360
    b = [text(x0 + w / 2, y0 - 12, title, 15, "middle", "bold")]
    b.append(rect(x0 - 24, y0, w + 48, 42 * U + 8, "#455a64", "#263238", 2, 4))
    b.append(rect(x0, y0 + 4, w, 42 * U, "#eceff1", "#263238"))
    covered = set()
    for top, (h, lab, col) in LAYOUT.items():
        for u in range(top - h + 1, top + 1):
            covered.add(u)
        y = y0 + 4 + (42 - top) * U
        b.append(rect(x0 + 2, y + 1, w - 4, h * U - 2, col, "#37474f"))
        lab2 = lab
        if rear and top in (41, 40):
            lab2 = lab.replace("(ports face rear)", "ports + cables here")
        b.append(text(x0 + 8, y + h * U / 2 + 4, lab2, 10.5))
    for u in range(1, 43):
        y = y0 + 4 + (42 - u) * U
        if u not in covered:
            b.append(rect(x0 + 2, y + 1, w - 4, U - 2, C["blank"], "#cfd8dc"))
        b.append(text(x0 - 6, y + 12, str(u), 9, "end", fill="#eceff1"))
    b.append(text(x0 + w / 2, y0 + 4 + (42 - 24) * U + 4, "U8 to U39 (except U21): blanking panels", 10.5, "middle", fill="#78909c"))
    if rear:
        b.append(rect(x0 - 52, y0 + 30, 14, 42 * U - 60, C["A"], "#000"))
        b.append(rect(x0 + w + 38, y0 + 30, 14, 42 * U - 60, C["B"], "#000"))
        b.append(text(x0 - 45, y0 + 22, "PDU-A", 11, "middle", "bold", C["A"]))
        b.append(text(x0 + w + 45, y0 + 22, "PDU-B", 11, "middle", "bold", C["B"]))
    return "".join(b), w

def rack_svg():
    b = [text(30, 34, "Lab rack 1 elevation, Vertiv VR3300 42U (50-user build)", 20, weight="bold"),
         text(30, 56, "Heaviest gear at the bottom. Switches at the top. Fronts face the room; the rear is inside the hot aisle containment.", 12, fill="#444")]
    f, w = rack(110, 100, "FRONT (room side)")
    r, _ = rack(560, 100, "REAR (inside hot aisle containment)", rear=True)
    b += [f, r]
    y = 100 + 42 * U + 40
    notes = [
        "1. Order the S5248F-ON and the OOB switch with PSU-to-port airflow (\"port-side exhaust\"). Their ports sit at the rear, so air must exit at the rear.",
        "2. Fill every open U with a blanking panel. Gaps let hot air leak out of the containment. Rack 2 gets a full set too.",
        "3. The Geist PDUs are already installed at the rear, left and right. Facilities says which side is feed A.",
        "4. U3-U4 is held for a second GPU server (needs C14 inlets, since each PDU has 3 C19). Otherwise it goes in rack 2.",
    ]
    for i, n in enumerate(notes):
        b.append(text(40, y + i * 20, n, 12))
    return svg(1000, y + 100, "".join(b), "Lab rack elevation")

# ---------------------------------------------------------------- power
def power_svg():
    b = [text(30, 34, "Power wiring: A and B feeds", 20, weight="bold"),
         text(30, 56, "Each device has two (or four) power supplies. Half go to PDU-A, half to PDU-B. Either feed alone carries the whole rack.", 12, fill="#444")]
    b.append(rect(40, 90, 220, 70, "#ffebee", C["A"], 2, 6))
    b.append(text(150, 118, "Facility feed A", 14, "middle", "bold", C["A"]))
    b.append(text(150, 138, "208V, existing, upstream of the PDU", 11, "middle"))
    b.append(text(150, 152, "facilities switches it, confirm source", 11, "middle"))
    b.append(rect(740, 90, 220, 70, "#e3f2fd", C["B"], 2, 6))
    b.append(text(850, 118, "Facility feed B", 14, "middle", "bold", C["B"]))
    b.append(text(850, 138, "208V, existing, separate source", 11, "middle"))
    b.append(text(850, 152, "facilities switches it, confirm source", 11, "middle"))
    b.append(rect(40, 210, 220, 60, "#ffcdd2", C["A"], 2, 6))
    b.append(text(150, 236, "PDU-A: existing Geist, rear left", 13, "middle", "bold"))
    b.append(text(150, 254, "circuits 1-3, C13s + one C19 each", 11, "middle"))
    b.append(rect(740, 210, 220, 60, "#bbdefb", C["B"], 2, 6))
    b.append(text(850, 236, "PDU-B: existing Geist, rear right", 13, "middle", "bold"))
    b.append(text(850, 254, "circuits 1-3, C13s + one C19 each", 11, "middle"))
    b.append(line(150, 160, 150, 210, C["A"], 4))
    b.append(line(850, 160, 850, 210, C["B"], 4))
    devs = [("gpu01 GPU server", "PSU1 c1, PSU3 c2", "PSU2 c1, PSU4 c2", "C19-C20 or C13-C14 (confirm)", 3300),
            ("svc01 service node", "PSU1 c1", "PSU2 c1", "C13 to C14", 400),
            ("svc02 service node", "PSU1 c2", "PSU2 c2", "C13 to C14", 400),
            ("svc03 service node", "PSU1 c3", "PSU2 c3", "C13 to C14", 400),
            ("sw01 lab switch", "PSU1 c3", "PSU2 c3", "C13 to C14", 250),
            ("con01 rack console", "", "only cord c3", "per vendor", 13),
            ("oob01 mgmt switch", "only cord c3", "", "C13 to C14", 30)]
    y = 320
    labels = []
    for name, a, bb, cord, wt in devs:
        b.append(rect(380, y, 240, 44, "#f5f5f5", "#333", 1.5, 4))
        b.append(text(500, y + 18, name, 13, "middle", "bold"))
        b.append(text(500, y + 35, f"{cord}, up to {wt} W", 10.5, "middle", fill="#444"))
        if a:
            b.append(path(f"M260 {240} C 320 {240}, 320 {y+22}, 380 {y+22}", C["A"], 2))
            labels.append(rect(374 - len(a) * 5.6 - 3, y + 29, len(a) * 5.6 + 4, 12, "#ffffff", "#ffffff", 0))
            labels.append(text(374, y + 38, a, 10, "end", fill=C["A"]))
        if bb:
            b.append(path(f"M740 {240} C 680 {240}, 680 {y+22}, 620 {y+22}", C["B"], 2))
            labels.append(rect(624, y + 29, len(bb) * 5.6 + 4, 12, "#ffffff", "#ffffff", 0))
            labels.append(text(626, y + 38, bb, 10, "start", fill=C["B"]))
        y += 62
    b += labels
    rules = ["Rules",
             "- Never plug both supplies of one device into the same PDU.",
             "- Label each cord at both ends: device, PSU number, PDU outlet (example: gpu01-PSU1 / A-c1-C19).",
             "- c1, c2, c3 = PDU circuit 1, 2, 3. Spread load across them; the PDU display shows current per circuit.",
             "- Test: facilities switches feed A off upstream; everything with two or more PSUs stays up. Restore. Repeat with feed B.",
             "- Each PDU must carry the whole rack alone: about 4.8 kW at 50 users. Confirm the PDU input rating on its label."]
    for i, r in enumerate(rules):
        b.append(text(40, y + 20 + i * 19, r, 13 if i == 0 else 12, weight="bold" if i == 0 else "normal"))
    return svg(1000, y + 150, "".join(b), "Power wiring")

# ---------------------------------------------------------------- network
def box(x, y, w, h, title, sub, fill):
    out = [rect(x, y, w, h, fill, "#333", 1.5, 6), text(x + w / 2, y + 20, title, 13, "middle", "bold")]
    for i, s in enumerate(sub):
        out.append(text(x + w / 2, y + 37 + i * 14, s, 10.5, "middle", fill="#333"))
    return "".join(out)

def network_svg():
    b = [text(30, 34, "Network cabling: lab", 20, weight="bold"),
         text(30, 56, "Our switch connects to the C9300-48S in the rack building. Users reach the AI service through their normal switches. The existing network does not change.", 12, fill="#444")]
    b.append(box(80, 80, 250, 62, "Analyst workstations", ["Jupyter, VS Code, MATLAB, browser"], "#f3e5f5"))
    b.append(box(80, 180, 250, 62, "Cisco C9300-48S", ["existing, analysts' building"], "#e0e0e0"))
    b.append(box(80, 280, 250, 62, "Cisco C9500X core", ["existing"], "#e0e0e0"))
    b.append(box(80, 380, 250, 70, "Cisco C9300-48S", ["existing, rack building", "C9300-NM-8X: 8 x 10G SFP+"], "#e0e0e0"))
    b.append(line(205, 142, 205, 180, C["cu"], 2))
    b.append(text(215, 166, "1G (existing)", 10.5, fill=C["cu"]))
    for x0, y0 in ((195, 242), (195, 342)):
        b.append(line(x0, y0, x0, y0 + 38, C["fiber"], 3))
        b.append(line(x0 + 20, y0, x0 + 20, y0 + 38, C["fiber"], 3))
        b.append(text(225, y0 + 24, "10G fiber (existing)", 10.5, fill=C["fiber"]))
    b.append(box(540, 380, 500, 70, "sw01 Lab switch, Dell S5248F-ON", ["48 x 25G SFP28, 4 x 100G QSFP28", "new, in lab rack 1"], C["sw"]))
    b.append(path("M330 405 L540 405", C["fiber"], 4))
    b.append(path("M330 425 L540 425", C["fiber"], 4))
    b.append(text(435, 397, "2 x 10G fiber (LACP), plan", 11, "middle", "bold", C["fiber"]))
    b.append(text(435, 442, "Cisco SFP-10G-SR-S to Dell 407-BBOU", 10, "middle", fill=C["fiber"]))
    b.append(text(435, 470, "Racks have no patch panels:", 10, "middle", fill="#444"))
    b.append(text(435, 484, "one LC-LC OM4 cord per link, length per path", 10, "middle", fill="#444"))
    b.append(path("M330 300 C 470 300, 620 320, 660 380", C["fiber"], 2, "6 4"))
    b.append(text(480, 298, "Only if the lab allows: 2 x 100G to the core", 10.5, fill=C["fiber"]))
    nodes = [("gpu01", "1/1/1-2", C["gpu"]), ("svc01", "1/1/3-4", C["svc"]), ("svc02", "1/1/5-6", C["svc"]),
             ("svc03", "1/1/7-8", C["svc"]), ("gpu02", "future, 1/1/9-10", C["gpur"])]
    x = 545
    for n, p, col in nodes:
        b.append(box(x, 560, 92, 64, n, ["2 x 25G", p], col))
        b.append(line(x + 38, 450, x + 38, 560, C["dac"], 2))
        b.append(line(x + 54, 450, x + 54, 560, C["dac"], 2))
        x += 102
    b.append(text(530, 512, "25G SFP28 passive DAC, 3 m", 11, "end", fill=C["dac"])); b.append(text(530, 527, "two per node, bonded (LACP)", 11, "end", fill=C["dac"]))
    b.append(box(80, 660, 250, 62, "oob01 1G management switch", ["BMC / IPMI ports only", "separate VLAN, no user access"], C["oob"]))
    x = 545
    for n, _, _ in nodes[:4]:
        b.append(path(f"M330 690 C 360 690, {x+20} 680, {x+20} 624", C["mgmt"], 1.5, "3 3"))
        x += 102
    b.append(text(340, 740, "Cat6 from each server BMC port to oob01. oob01 uplink goes where the lab network team says (their management network).", 11, fill=C["mgmt"]))
    leg = [(C["fiber"], "Fiber (optics + patch cord)", None), (C["dac"], "Direct-attach copper (DAC)", None),
           (C["cu"], "Existing user links", None), (C["mgmt"], "Management (BMC) Cat6", "3 3")]
    y = 780
    b.append(text(80, y, "Legend", 13, weight="bold"))
    for i, (col, lab, d) in enumerate(leg):
        b.append(line(160 + i * 220, y - 4, 200 + i * 220, y - 4, col, 3, d))
        b.append(text(206 + i * 220, y, lab, 11))
    return svg(1100, 810, "".join(b), "Network cabling")

# ---------------------------------------------------------------- prototype
def proto_svg():
    b = [text(30, 34, "Software path: build workstation to the lab", 20, weight="bold"),
         text(30, 56, "No staging server. The build workstation rehearses each bundle; the lab rack is production from day 1.", 12, fill="#444")]
    b.append(rect(30, 80, 1040, 230, "#f1f8e9", "#558b2f", 2, 8))
    b.append(text(46, 102, "UNCLASSIFIED (internet)", 13, weight="bold", fill="#33691e"))
    b.append(box(60, 130, 300, 96, "Build workstation", ["existing Linux machine, 2 TB+ free disk", "runs delivery/pull-all.sh", "rehearses verify.sh + deploy.sh in a VM"], "#fff3e0"))
    b.append(box(460, 130, 240, 96, "Transfer drive", ["Apricorn A25-3PL256-S4000F", "ext4, sealed bundle", "SHA256SUMS (+ signature)"], C["oob"]))
    b.append(box(800, 130, 240, 96, "ISSM intake", ["approved media process", "scan with the bundled Trivy", "one way only: in"], "#f3e5f5"))
    b.append(path("M360 178 L460 178", C["cu"], 2))
    b.append(path("M700 178 L800 178", "#795548", 2, "6 4"))
    b.append(text(60, 260, "Rehearsal without a GPU catches most problems: missing images, checksum errors, script bugs, wrong versions.", 11))
    b.append(text(60, 278, "GPU driver and model problems first show up in the lab. The 4-GPU rolling update keeps users served while a new version proves itself.", 11))
    b.append(rect(30, 340, 1040, 200, "#ffebee", "#b71c1c", 2, 8))
    b.append(text(46, 362, "LAB (AIR-GAPPED)", 13, weight="bold", fill="#b71c1c"))
    b.append(box(60, 390, 300, 96, "Rack 1, production", ["gpu01: 4 x RTX PRO 6000", "svc01-03: RKE2, gateway, database", "sw01 2 x 10G to the lab C9300-48S"], C["gpu"]))
    b.append(box(460, 390, 240, 96, "Update, one GPU at a time", ["vLLM replicas 3 -> new version on 1", "other 2 keep serving", "stalls if the new one fails"], C["svc"]))
    b.append(box(800, 390, 240, 96, "Lab users", ["browser, Jupyter, VS Code, MATLAB", "https://api.&lt;lab-domain&gt;/v1", "per-user gateway keys"], "#f3e5f5"))
    b.append(path("M920 226 L920 300 L210 300 L210 390", "#795548", 2, "6 4"))
    b.append(text(565, 294, "sealed release bundle on approved media", 11, "middle", "bold", "#795548"))
    b.append(path("M360 438 L460 438", C["dac"], 2))
    b.append(path("M700 438 L800 438", C["cu"], 2))
    b.append(text(60, 520, "Lab hardware never connects to unclassified machines. Hardware and media only move one way: in.", 12))
    return svg(1100, 570, "".join(b), "Software path")

os.makedirs(OUT, exist_ok=True)
for name, fn in [("rack-elevation", rack_svg), ("power-wiring", power_svg), ("network-cabling", network_svg), ("prototype-topology", proto_svg)]:
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(fn())
    print("wrote", name)
