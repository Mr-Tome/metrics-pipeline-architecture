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
    42: (1, "Fiber patch panel (uplink to core)", C["patch"]),
    41: (1, "sw01  Lab switch, Dell S5248F-ON (ports face rear)", C["sw"]),
    40: (1, "oob01  1G management switch (ports face rear)", C["oob"]),
    7: (1, "svc03  Service node, 1U", C["svc"]),
    6: (1, "svc02  Service node, 1U", C["svc"]),
    5: (1, "svc01  Service node, 1U", C["svc"]),
    4: (2, "RESERVED gpu02 (100-user growth), blanking panels", C["gpur"]),
    2: (2, "gpu01  GPU server, 2U, 2 of 4 GPU slots filled", C["gpu"]),
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
    b.append(text(x0 + w / 2, y0 + 4 + (42 - 24) * U + 4, "U8 to U39: blanking panels (required for containment)", 10.5, "middle", fill="#78909c"))
    if rear:
        b.append(rect(x0 - 52, y0 + 30, 14, 42 * U - 60, C["A"], "#000"))
        b.append(rect(x0 + w + 38, y0 + 30, 14, 42 * U - 60, C["B"], "#000"))
        b.append(text(x0 - 45, y0 + 22, "PDU-A", 11, "middle", "bold", C["A"]))
        b.append(text(x0 + w + 45, y0 + 22, "PDU-B", 11, "middle", "bold", C["B"]))
    return "".join(b), w

def rack_svg():
    b = [text(30, 34, "Lab rack elevation, 42U (20-user build)", 20, weight="bold"),
         text(30, 56, "Heaviest gear at the bottom. Switches at the top. Servers face the cold aisle; their rear I/O faces the hot aisle.", 12, fill="#444")]
    f, w = rack(110, 100, "FRONT (cold aisle)")
    r, _ = rack(560, 100, "REAR (hot aisle)", rear=True)
    b += [f, r]
    y = 100 + 42 * U + 40
    notes = [
        "1. Order the S5248F-ON and the OOB switch with PSU-to-port airflow (\"port-side exhaust\"). Their ports sit at the rear, so air must exit at the rear.",
        "2. Fill every open U with a blanking panel. Gaps let hot air back into the cold aisle and the in-row cooler cannot keep up.",
        "3. PDUs mount in the zero-U space at the rear: PDU-A on the left (feed A), PDU-B on the right (feed B).",
        "4. U3-U4 is held for a second GPU server at the 100-user size. The rack power and switch ports are already sized for it.",
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
    b.append(text(150, 138, "208V 3-phase WYE, 30A, 60 Hz", 11, "middle"))
    b.append(text(150, 152, "NEMA L21-30R receptacle", 11, "middle"))
    b.append(rect(740, 90, 220, 70, "#e3f2fd", C["B"], 2, 6))
    b.append(text(850, 118, "Facility feed B", 14, "middle", "bold", C["B"]))
    b.append(text(850, 138, "208V 3-phase WYE, 30A, 60 Hz", 11, "middle"))
    b.append(text(850, 152, "NEMA L21-30R (separate source)", 11, "middle"))
    b.append(rect(40, 210, 220, 60, "#ffcdd2", C["A"], 2, 6))
    b.append(text(150, 236, "PDU-A (rear left, zero-U)", 13, "middle", "bold"))
    b.append(text(150, 254, "L21-30P, C13/C19 combo outlets", 11, "middle"))
    b.append(rect(740, 210, 220, 60, "#bbdefb", C["B"], 2, 6))
    b.append(text(850, 236, "PDU-B (rear right, zero-U)", 13, "middle", "bold"))
    b.append(text(850, 254, "L21-30P, C13/C19 combo outlets", 11, "middle"))
    b.append(line(150, 160, 150, 210, C["A"], 4))
    b.append(line(850, 160, 850, 210, C["B"], 4))
    devs = [("gpu01 GPU server", "PSU1, PSU3", "PSU2, PSU4", "C19 to C20 (confirm)", 2100),
            ("svc01 service node", "PSU1", "PSU2", "C13 to C14", 400),
            ("svc02 service node", "PSU1", "PSU2", "C13 to C14", 400),
            ("svc03 service node", "PSU1", "PSU2", "C13 to C14", 400),
            ("sw01 lab switch", "PSU1", "PSU2", "C13 to C14", 250),
            ("oob01 mgmt switch", "PSU1 / only", "PSU2 if fitted", "C13 to C14", 30)]
    y = 320
    for name, a, bb, cord, wt in devs:
        b.append(rect(380, y, 240, 44, "#f5f5f5", "#333", 1.5, 4))
        b.append(text(500, y + 18, name, 13, "middle", "bold"))
        b.append(text(500, y + 35, f"{cord}, up to {wt} W", 10.5, "middle", fill="#444"))
        b.append(path(f"M260 {240} C 320 {240}, 320 {y+22}, 380 {y+22}", C["A"], 2))
        b.append(text(372, y + 14, a, 10, "end", fill=C["A"]))
        b.append(path(f"M740 {240} C 680 {240}, 680 {y+22}, 620 {y+22}", C["B"], 2))
        b.append(text(628, y + 14, bb, 10, "start", fill=C["B"]))
        y += 62
    rules = ["Rules",
             "- Never plug both supplies of one device into the same PDU.",
             "- Label each cord at both ends: device, PSU number, PDU outlet (example: gpu01-PSU1 / A-07).",
             "- Spread load across the three phases (outlet banks) on each PDU. The PDU display shows per-phase current.",
             "- Test: pull feed A at the breaker, confirm everything stays up. Restore. Repeat with feed B.",
             "- Usable per feed: 30A x 208V x 1.732 x 0.8 = about 8.6 kW. 20-user rack peak: about 3.6 kW. 100-user: about 8.3 kW."]
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
         text(30, 56, "The lab switch hangs off the existing core. Users reach the AI service through their normal access switches. Nothing about the existing user network changes.", 12, fill="#444")]
    b.append(box(80, 90, 250, 70, "Analyst workstations", ["Jupyter, VS Code, MATLAB, browser", "existing desks"], "#f3e5f5"))
    b.append(box(80, 210, 250, 70, "Access: Cisco C9300-48? x2", ["existing; model to confirm", "10G fiber uplinks to core"], "#e0e0e0"))
    b.append(box(80, 340, 250, 70, "Core: Cisco C9500X", ["existing; 100G QSFP28 ports", "need 2 free ports (preferred)"], "#e0e0e0"))
    b.append(line(205, 160, 205, 210, C["cu"], 2))
    b.append(text(215, 190, "1G copper or fiber (existing)", 10.5, fill=C["cu"]))
    b.append(line(195, 280, 195, 340, C["fiber"], 3))
    b.append(line(215, 280, 215, 340, C["fiber"], 3))
    b.append(text(225, 315, "2 x 10G fiber (existing)", 10.5, fill=C["fiber"]))
    b.append(box(540, 340, 500, 70, "sw01 Lab switch, Dell S5248F-ON", ["48 x 25G SFP28, 4 x 100G QSFP28", "new, in the lab rack"], C["sw"]))
    b.append(path("M330 365 L540 365", C["fiber"], 4))
    b.append(path("M330 385 L540 385", C["fiber"], 4))
    b.append(text(435, 357, "Option A: 2 x 100G fiber (LACP)", 11, "middle", "bold", C["fiber"]))
    b.append(text(435, 402, "C9500X 100G port to sw01 QSFP28", 10, "middle", fill=C["fiber"]))
    b.append(path("M330 240 C 450 240, 600 260, 640 340", C["fiber"], 2, "6 4"))
    b.append(text(500, 245, "Option B (fallback): 2 x 10G from C9300 NM-8X", 10.5, fill=C["fiber"]))
    b.append(text(500, 259, "to sw01 SFP28 ports running at 10G", 10.5, fill=C["fiber"]))
    nodes = [("gpu01", "1/1/1-2", C["gpu"]), ("svc01", "1/1/3-4", C["svc"]), ("svc02", "1/1/5-6", C["svc"]),
             ("svc03", "1/1/7-8", C["svc"]), ("gpu02", "future, 1/1/9-10", C["gpur"])]
    x = 545
    for n, p, col in nodes:
        b.append(box(x, 520, 92, 64, n, ["2 x 25G", p], col))
        b.append(line(x + 38, 410, x + 38, 520, C["dac"], 2))
        b.append(line(x + 54, 410, x + 54, 520, C["dac"], 2))
        x += 102
    b.append(text(530, 462, "25G SFP28 passive DAC, 3 m", 11, "end", fill=C["dac"])); b.append(text(530, 477, "two per node, bonded (LACP)", 11, "end", fill=C["dac"]))
    b.append(box(80, 620, 250, 62, "oob01 1G management switch", ["BMC / IPMI ports only", "separate VLAN, no user access"], C["oob"]))
    x = 545
    for n, _, _ in nodes[:4]:
        b.append(path(f"M330 650 C 360 650, {x+20} 640, {x+20} 584", C["mgmt"], 1.5, "3 3"))
        x += 102
    b.append(text(340, 700, "Cat6 from each server BMC port to oob01. oob01 uplink goes where the lab network team says (their management network).", 11, fill=C["mgmt"]))
    leg = [(C["fiber"], "Fiber (optics + patch cord)", None), (C["dac"], "Direct-attach copper (DAC)", None),
           (C["cu"], "Existing user links", None), (C["mgmt"], "Management (BMC) Cat6", "3 3")]
    y = 740
    b.append(text(80, y, "Legend", 13, weight="bold"))
    for i, (col, lab, d) in enumerate(leg):
        b.append(line(160 + i * 220, y - 4, 200 + i * 220, y - 4, col, 3, d))
        b.append(text(206 + i * 220, y, lab, 11))
    return svg(1100, 780, "".join(b), "Network cabling")

# ---------------------------------------------------------------- prototype
def proto_svg():
    b = [text(30, 34, "Prototype on the unclassified side (becomes staging)", 20, weight="bold"),
         text(30, 56, "The staging GPU server from the BOM is the prototype. It stays on the unclassified side for good. Nothing gets rebuilt later.", 12, fill="#444")]
    b.append(rect(30, 80, 1040, 330, "#f1f8e9", "#558b2f", 2, 8))
    b.append(text(46, 102, "UNCLASSIFIED", 13, weight="bold", fill="#33691e"))
    b.append(box(60, 130, 250, 80, "Build workstation", ["internet access", "runs delivery/ pull scripts", "existing machine, 2 TB+ free disk"], "#fff3e0"))
    b.append(box(420, 130, 280, 80, "stg01 staging GPU server", ["BOM items S1, S2, S3", "1 x RTX PRO 6000, RKE2 single node", "2 x 25G NIC"], C["gpu"]))
    b.append(box(800, 130, 240, 80, "Unclass workstation(s)", ["prototype users", "browser, Jupyter, VS Code"], "#f3e5f5"))
    b.append(path("M310 160 L420 160", C["cu"], 2))
    b.append(text(365, 152, "Phase P1 only", 10, "middle", fill=C["cu"]))
    b.append(text(365, 178, "LAN, pulls direct", 10, "middle", fill=C["cu"]))
    b.append(path("M185 210 L185 300 L560 300 L560 210", "#795548", 2, "6 4"))
    b.append(text(372, 292, "Phase P2+: approved transfer media only (same as the lab)", 11, "middle", fill="#795548"))
    b.append(path("M700 170 L800 170", C["dac"], 3))
    b.append(text(750, 162, "Direct cable", 10, "middle"))
    b.append(text(750, 190, "25G DAC or 10G", 10, "middle"))
    b.append(text(60, 345, "Direct cable option: one workstation plugs straight into stg01's second 25G port with a DAC (or 10G SFP+ if", 11))
    b.append(text(60, 361, "the workstation only has 10G). Static IPs, no switch. For more than one or two users, use the unclassified LAN instead.", 11))
    b.append(text(60, 385, "Either way, users hit the same LiteLLM gateway URL and API keys they will use in the lab.", 11, weight="bold"))
    b.append(rect(30, 440, 1040, 110, "#ffebee", "#b71c1c", 2, 8))
    b.append(text(46, 462, "LAB (CLASSIFIED / AIR-GAPPED)", 13, weight="bold", fill="#b71c1c"))
    b.append(text(60, 490, "Lab GPU servers never connect to unclassified machines once they are in the lab. Hardware and media only move one way: in.", 12))
    b.append(text(60, 510, "Optional, with ISSM approval: burn in new lab hardware on the unclassified side BEFORE it enters the lab (catch dead parts early).", 12))
    b.append(text(60, 530, "Software reaches the lab only as a sealed, checksummed release bundle that already passed staging.", 12))
    b.append(text(560, 428, "one way only: sealed release bundle on approved media, after staging sign-off", 11, "middle", "bold", "#795548"))
    return svg(1100, 580, "".join(b), "Prototype topology")

os.makedirs(OUT, exist_ok=True)
for name, fn in [("rack-elevation", rack_svg), ("power-wiring", power_svg), ("network-cabling", network_svg), ("prototype-topology", proto_svg)]:
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(fn())
    print("wrote", name)
