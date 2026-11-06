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
    42: (1, "Blanking (no patch panel; uplink fiber runs straight to sw01)", C["blank"]),
    41: (1, "sw01  Lab switch, Cisco Nexus N93180YC-FX3 (ports face rear)", C["sw"]),
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
        # circuits along each PDU: C1 at the top, C3 at the bottom
        sec = (42 * U - 60) / 3
        for px in (x0 - 52, x0 + w + 38):
            for c in (1, 2, 3):
                sy = y0 + 30 + (c - 1) * sec
                if c > 1:
                    b.append(line(px, sy, px + 14, sy, "#ffffff", 1.5))
                b.append(text(px + 7, sy + 16, f"C{c}", 8, "middle", "bold", "#ffffff"))
    return "".join(b), w

def rack_svg():
    b = [text(30, 34, "Lab rack 1 elevation, Vertiv VR3300 42U (50-user build)", 20, weight="bold"),
         text(30, 56, "Heaviest gear at the bottom. Switches at the top. Fronts face the room; the rear is inside the hot aisle containment.", 12, fill="#444")]
    f, w = rack(110, 100, "FRONT (room side)")
    r, _ = rack(560, 100, "REAR (inside hot aisle containment)", rear=True)
    b += [f, r]
    y = 100 + 42 * U + 40
    notes = [
        "1. Order sw01 (Nexus, -PE power supplies and fans) and the OOB switch with port-side exhaust airflow. Their ports sit at the rear, so air must exit at the rear.",
        "2. Fill every open U with a blanking panel. Gaps let hot air leak out of the containment. Rack 2 gets a full set too.",
        "3. The Geist PDUs are already installed at the rear, left and right, circuit C1 at the top. Facilities says which side is feed A.",
        "4. U3-U4 is held for a second GPU server (needs C14 inlets, since each PDU has 3 C19). Otherwise it goes in rack 2.",
    ]
    for i, n in enumerate(notes):
        b.append(text(40, y + i * 20, n, 12))
    return svg(1000, y + 100, "".join(b), "Lab rack elevation")

# ---------------------------------------------------------------- power
def power_svg():
    # Rear view of rack 1, drawn to the same U scale as the elevation. Cords run from each PSU to its outlet.
    PU = 16
    RX, RW, RY = 360, 280, 190            # rack opening, rear view
    AX, BX, PW = 232, 722, 46             # PDU-A (rear left), PDU-B (rear right)
    def uy(u): return RY + (42 - u) * PU  # top edge of U u
    b = [text(30, 34, "Power wiring: rack 1 rear view (50-user build)", 20, weight="bold"),
         text(30, 56, "Seen from the rear, inside the containment. Odd PSUs go to PDU-A, even PSUs to PDU-B. Either PDU alone carries the whole rack.", 12, fill="#444"),
         text(30, 74, "C1 is at the top of each PDU, C3 at the bottom. Each cord goes to the circuit nearest its device, so the 6 ft cords reach.", 12, fill="#444")]
    # facility feeds and PDU input cords
    for x, p, col, fill, src in [(AX, "A", C["A"], "#ffebee", "existing"), (BX, "B", C["B"], "#e3f2fd", "separate source")]:
        bx = 40 if p == "A" else 740
        b.append(rect(bx, 92, 220, 56, fill, col, 2, 6))
        b.append(text(bx + 110, 114, f"Facility feed {p}", 14, "middle", "bold", col))
        b.append(text(bx + 110, 134, f"208V, {src}, facilities switches it", 11, "middle"))
        b.append(path(f"M{bx + 110} 148 L{bx + 110} 158 L{x + PW / 2} 158 L{x + PW / 2} {RY}", col, 4))
        b.append(text(x + PW / 2 + (-6 if p == "A" else 6), RY - 6, "PDU input cord", 10, "end" if p == "A" else "start", fill=col))
    # rack frame
    b.append(rect(RX - 20, RY - 8, RW + 40, 42 * PU + 16, "#455a64", "#263238", 2, 4))
    b.append(rect(RX, RY, RW, 42 * PU, "#eceff1", "#263238"))
    for u in range(1, 43):
        b.append(text(RX - 6, uy(u) + 12, str(u), 9, "end", fill="#eceff1"))
    # devices, rear view: (top U, height, name, PSU count, color)
    devs = {"gpu01": (2, 2, "gpu01  GPU server, 3,300 W", 4, C["gpu"]),
            "svc01": (5, 1, "svc01", 2, C["svc"]), "svc02": (6, 1, "svc02", 2, C["svc"]), "svc03": (7, 1, "svc03", 2, C["svc"]),
            "con01": (21, 1, "con01  console, 1 cord", 1, C["patch"]),
            "oob01": (40, 1, "oob01  1 cord", 1, C["oob"]), "sw01": (41, 1, "sw01", 2, C["sw"])}
    b.append(rect(RX + 2, uy(4) + 1, RW - 4, 2 * PU - 2, C["gpur"], "#90a4ae"))
    b.append(text(RX + RW / 2, uy(4) + 20, "U3-U4 held for gpu02", 10, "middle", fill="#607d8b"))
    b.append(text(RX + RW / 2, uy(30) + 4, "blanking panels", 10.5, "middle", fill="#90a4ae"))
    b.append(text(RX + RW / 2, uy(14) + 4, "blanking panels", 10.5, "middle", fill="#90a4ae"))
    psu, front = {}, []   # front: PSUs and labels, drawn over the cords
    for name, (top, h, lab, n, col) in devs.items():
        y = uy(top)
        b.append(rect(RX + 2, y + 1, RW - 4, h * PU - 2, col, "#37474f"))
        front.append(f"<text x='{RX + 8}' y='{y + h * PU / 2 + 4}' font-size='10' fill='#111' stroke='{col}' "
                     f"stroke-width='4' paint-order='stroke'>{lab}</text>")
        # PSUs drawn left to right as PSU1..n (check the server's rear label)
        for i in range(n):
            px = RX + RW - 18 - (n - i) * 30 if n > 1 else RX + RW - 48
            front.append(rect(px, y + 3, 26, h * PU - 6, "#263238", "#000", 1, 2))
            front.append(text(px + 13, y + h * PU / 2 + 3, f"P{i + 1}" if n > 1 else "P", 8, "middle", fill="#ffffff"))
            # a 2U server's cords leave at staggered heights so parallel runs stay apart
            psu[(name, i + 1)] = (px + 13, y + h * PU / 2 + ((i - 1.5) * 5 if h > 1 else 0))
    # PDUs: three circuits each, C1 at the top (as on the site's PDUs); one C19 and six C13 per circuit
    SEC = (42 * PU - 30) / 3
    outlet = {}
    for x, p, col, fill in [(AX, "A", C["A"], "#ffcdd2"), (BX, "B", C["B"], "#bbdefb")]:
        b.append(rect(x, RY, PW, 42 * PU, fill, col, 2, 4))
        b.append(text(x + PW / 2, RY + 42 * PU + 16, f"PDU-{p}", 12, "middle", "bold", col))
        for c in (1, 2, 3):
            sy = RY + 10 + (c - 1) * SEC
            if c < 3:
                b.append(line(x + 3, sy + SEC, x + PW - 3, sy + SEC, col, 1.5, "4 3"))
            b.append(rect(x + 8, sy + 4, PW - 16, 14, "#ffffff", col, 1, 2))
            b.append(text(x + PW / 2, sy + 15, f"C{c}", 10, "middle", "bold", col))
            b.append(text(x + PW / 2, sy + 30, "breaker", 7.5, "middle", fill="#555"))
            slots = ["C19"] + [f"C13.{i}" for i in range(1, 7)]
            for i, o in enumerate(slots):
                oy = sy + 40 + i * 24
                if o == "C19":
                    b.append(rect(x + 9, oy, 28, 14, "#212121", "#000", 1, 2))
                    b.append(text(x + PW / 2, oy + 10, "C19", 8, "middle", fill="#ffffff"))
                else:
                    b.append(rect(x + 14, oy, 18, 14, "#424242", "#000", 1, 2))
                outlet[(p, c, o)] = (x + (PW if p == "A" else 0), oy + 7)
    # cord plan: (device, PSU, PDU, circuit, outlet)
    plan = [("gpu01", 1, "A", 3, "C19"), ("gpu01", 3, "A", 2, "C19"), ("gpu01", 2, "B", 3, "C19"), ("gpu01", 4, "B", 2, "C19"),
            ("svc01", 1, "A", 3, "C13.1"), ("svc01", 2, "B", 3, "C13.1"),
            ("svc02", 1, "A", 2, "C13.1"), ("svc02", 2, "B", 2, "C13.1"),
            ("svc03", 1, "A", 1, "C13.6"), ("svc03", 2, "B", 1, "C13.6"),
            ("con01", 1, "B", 1, "C13.5"),
            ("sw01", 1, "A", 1, "C13.1"), ("sw01", 2, "B", 1, "C13.1"), ("oob01", 1, "A", 1, "C13.2")]
    # Each cord runs across the device rear, then up or down a lane at the side of the rack, then into
    # its outlet. Lanes are assigned by outlet height so cords on one side don't cross each other.
    cords = []
    for p in ("A", "B"):
        mine = sorted([c for c in plan if c[2] == p], key=lambda c: outlet[(p, c[3], c[4])][1])
        for k, (dev, n, _, c, o) in enumerate(mine):
            sx, sy = psu[(dev, n)]
            ox, oy = outlet[(p, c, o)]
            col = C["A"] if p == "A" else C["B"]
            lane = (RX - 30 - k * 6) if p == "A" else (RX + RW + 26 + k * 6)
            cords.append(f"<polyline points='{sx},{sy} {lane},{sy} {lane},{oy} {ox},{oy}' fill='none' stroke='{col}' "
                         f"stroke-width='2.2' stroke-linejoin='round' opacity='0.9'/>")
            cords.append(f"<circle cx='{ox}' cy='{oy}' r='3' fill='{col}'/>")
    b += cords + front
    # load table
    y = RY + 42 * PU + 50
    b.append(text(40, y, "Load per circuit at max draw (same on both PDUs; oob01 is on A-C1, con01 on B-C1)", 13, weight="bold"))
    rows = [("Circuit", "Cords on it", "Both feeds up", "Other feed down"),
            ("C1 (top)", "svc03, sw01, oob01 or con01", "about 530 W, 2.5 A", "about 1,030 W, 5.0 A"),
            ("C2", "gpu01 PSU (C19), svc02", "1,025 W, 4.9 A", "2,050 W, 9.9 A"),
            ("C3 (bottom)", "gpu01 PSU (C19), svc01", "1,025 W, 4.9 A", "2,050 W, 9.9 A")]
    for i, r in enumerate(rows):
        for j, (cell, cx) in enumerate(zip(r, (40, 140, 400, 600))):
            b.append(text(cx, y + 24 + i * 20, cell, 12, weight="bold" if i == 0 else "normal"))
    y += 24 + len(rows) * 20 + 16
    rules = ["Rules",
             "- Never plug both supplies of one device into the same PDU. Cords from a server's right-hand PSUs cross to the left PDU; that is expected.",
             "- If gpu01 has C14 inlets: same circuits, C13 outlets instead of the C19s, and all C19s stay free.",
             "- Label each cord at both ends: device, PSU, PDU, circuit, outlet (example: gpu01-PSU1 / A-C3-C19).",
             "- All six PDU breakers off before the first cord goes in. Route cords along the sides, clear of server exhaust.",
             "- Test: facilities switches feed A off; everything with two or more PSUs stays up, oob01 goes dark. Restore. Repeat with B (con01 goes dark).",
             "- Each PDU must carry the whole rack alone: about 5.1 kW at 50 users. PSU positions and outlet counts: check the real labels."]
    for i, r in enumerate(rules):
        b.append(text(40, y + i * 19, r, 13 if i == 0 else 12, weight="bold" if i == 0 else "normal"))
    return svg(1000, y + len(rules) * 19 + 20, "".join(b), "Power wiring")

# ---------------------------------------------------------------- network
def box(x, y, w, h, title, sub, fill):
    out = [rect(x, y, w, h, fill, "#333", 1.5, 6), text(x + w / 2, y + 20, title, 13, "middle", "bold")]
    for i, s in enumerate(sub):
        out.append(text(x + w / 2, y + 37 + i * 14, s, 10.5, "middle", fill="#333"))
    return "".join(out)

def network_svg():
    b = [text(30, 34, "Network cabling: lab", 20, weight="bold"),
         text(30, 56, "sw01 connects to the lab's C9500X-28C8D with 2 x 100G. oob01 has its own 10G link, so management does not depend on the data side.", 12, fill="#444")]
    b.append(box(80, 80, 250, 62, "Analyst workstations", ["Jupyter, VS Code, MATLAB, browser"], "#f3e5f5"))
    b.append(box(80, 180, 250, 62, "Lab network", ["existing"], "#e0e0e0"))
    b.append(box(80, 380, 250, 70, "Cisco C9500X-28C8D", ["lab core, above rows 2 and 3", "3 ports for us, IOS XE 17.15"], "#e0e0e0"))
    b.append(line(205, 142, 205, 180, C["cu"], 2))
    b.append(text(215, 166, "1G (existing)", 10.5, fill=C["cu"]))
    b.append(line(205, 242, 205, 380, C["fiber"], 3))
    b.append(text(215, 316, "10G uplink (existing)", 10.5, fill=C["fiber"]))
    b.append(box(540, 380, 500, 70, "sw01 Lab switch, Cisco Nexus N93180YC-FX3", ["48 x 25G SFP28, 6 x 40/100G QSFP28", "new, in lab rack 1 (next to ACE 15)"], C["sw"]))
    b.append(path("M330 405 L540 405", C["fiber"], 4))
    b.append(path("M330 425 L540 425", C["fiber"], 4))
    b.append(text(435, 397, "2 x 100G multimode (LACP)", 11, "middle", "bold", C["fiber"]))
    b.append(text(435, 442, "Cisco QSFP-40/100-SRBD at both ends", 10, "middle", fill=C["fiber"]))
    b.append(text(435, 456, "LC-LC OM4 cord, 8 m or 15 m, no patch panel", 10, "middle", fill="#444"))
    b.append(text(435, 370, "data only", 10, "middle", fill="#444"))
    b.append(path("M120 660 L120 450", C["fiber"], 2))
    b.append(text(128, 560, "M06: 10G management, OM4 LC", 10, fill=C["fiber"])); b.append(text(128, 574, "QSA adapter + SFP-10G-SR-S", 10, fill=C["fiber"]))
    nodes = [("gpu01", "1/1/1-2", C["gpu"]), ("svc01", "1/1/3-4", C["svc"]), ("svc02", "1/1/5-6", C["svc"]),
             ("svc03", "1/1/7-8", C["svc"]), ("gpu02", "future, 1/1/9-10", C["gpur"])]
    x = 545
    for n, p, col in nodes:
        b.append(box(x, 560, 92, 64, n, ["2 x 25G", p], col))
        b.append(line(x + 38, 450, x + 38, 560, C["dac"], 2))
        b.append(line(x + 54, 450, x + 54, 560, C["dac"], 2))
        x += 102
    b.append(text(530, 530, "Cisco SFP-H25G-CU3M DAC, 3 m", 11, "end", fill=C["dac"])); b.append(text(530, 545, "two per node, bonded (LACP)", 11, "end", fill=C["dac"]))
    b.append(box(80, 660, 250, 62, "oob01 1G management switch", ["BMC / IPMI ports only", "separate VLAN, no user access"], C["oob"]))
    x = 545
    for n, _, _ in nodes[:4]:
        b.append(path(f"M330 690 C 360 690, {x+20} 680, {x+20} 624", C["mgmt"], 1.5, "3 3"))
        x += 102
    b.append(text(340, 740, "Cat6 from each server BMC port to oob01. oob01 uplinks to its own C9500X-28C8D port (M06).", 11, fill=C["mgmt"]))
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
    b.append(box(60, 390, 300, 96, "Rack 1, production", ["gpu01: 4 x RTX PRO 6000", "svc01-03: RKE2, gateway, database", "sw01 2 x 100G + oob01 10G to the lab C9500X"], C["gpu"]))
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
