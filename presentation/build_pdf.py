#!/usr/bin/env python3
"""Build the thesis-defense slide deck as a vector PDF (ivory / brown palette).

Clean, low-text, schematic-driven.  ~12 slides for a 10-minute defense.
All graphics are native vector drawing -> crisp at any zoom.

    python3 build_pdf.py  ->  adaptive-swarm-crypto.pdf
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

OUT = os.path.join(os.path.dirname(__file__), "adaptive-swarm-crypto.pdf")

# ---- page (16:9) -----------------------------------------------------------
W, H = 960.0, 540.0  # points (13.333 x 7.5 in)

# ---- palette ---------------------------------------------------------------
IVORY      = HexColor("#F5EFE1")
CARD       = HexColor("#FCFAF4")
CARD_LINE  = HexColor("#E3D8C3")
BROWN_DK   = HexColor("#4A3527")
BROWN      = HexColor("#8C6A4A")
BROWN_SOFT = HexColor("#B08968")
TAN        = HexColor("#CFB593")
SAND       = HexColor("#EADCC6")
SAND_DEEP  = HexColor("#E0CFB2")
TEXT_MUT   = HexColor("#7A6A58")
WHITE      = HexColor("#FFFFFF")
SHADOW     = HexColor("#D8CBB4")

HEAVY_C    = HexColor("#5C3A21")
BALANCED_C = HexColor("#B0825A")
LIGHT_C    = HexColor("#D8C3A5")

# ---- fonts -----------------------------------------------------------------
FD = "/usr/share/fonts/truetype"
pdfmetrics.registerFont(TTFont("Serif",     f"{FD}/liberation/LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-B",   f"{FD}/liberation/LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-I",   f"{FD}/liberation/LiberationSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Sans",      f"{FD}/liberation/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Sans-B",    f"{FD}/liberation/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans-I",    f"{FD}/liberation/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Mono",      f"{FD}/dejavu/DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("Mono-B",    f"{FD}/dejavu/DejaVuSansMono-Bold.ttf"))

c = canvas.Canvas(OUT, pagesize=(W, H))

# ============================================================================
# primitives  (all take TOP-LEFT coordinates; y grows downward)
# ============================================================================

def _y(top, h=0):
    return H - top - h


def bg(color=IVORY):
    c.setFillColor(color); c.rect(0, 0, W, H, stroke=0, fill=1)


def rrect(x, y, w, h, fill=None, stroke=None, lw=1.0, r=8, shadow=False):
    if shadow:
        c.setFillColor(SHADOW)
        c.roundRect(x + 3, _y(y, h) - 3, w, h, r, stroke=0, fill=1)
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(lw)
    c.roundRect(x, _y(y, h), w, h, r, stroke=0 if stroke is None else 1,
                fill=0 if fill is None else 1)


def rect(x, y, w, h, fill=None, stroke=None, lw=1.0):
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(lw)
    c.rect(x, _y(y, h), w, h, stroke=0 if stroke is None else 1,
           fill=0 if fill is None else 1)


def circle(cx, cy, rad, fill=None, stroke=None, lw=1.0):
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(lw)
    c.circle(cx, H - cy, rad, stroke=0 if stroke is None else 1,
             fill=0 if fill is None else 1)


def line(x1, y1, x2, y2, color=BROWN, lw=1.5, dash=None):
    c.setStrokeColor(color); c.setLineWidth(lw)
    if dash:
        c.setDash(dash)
    c.line(x1, H - y1, x2, H - y2)
    c.setDash()


def tri(cx, cy, w, h, fill, up=True):
    """Filled triangle centred at (cx, cy)."""
    p = c.beginPath()
    if up:
        p.moveTo(cx, H - (cy - h / 2))
        p.lineTo(cx - w / 2, H - (cy + h / 2))
        p.lineTo(cx + w / 2, H - (cy + h / 2))
    else:
        p.moveTo(cx, H - (cy + h / 2))
        p.lineTo(cx - w / 2, H - (cy - h / 2))
        p.lineTo(cx + w / 2, H - (cy - h / 2))
    p.close()
    c.setFillColor(fill); c.drawPath(p, stroke=0, fill=1)


def txt(x, y, s, font="Sans", size=12, color=BROWN_DK, align="l"):
    """Draw single-line text; y = top of the cap height."""
    c.setFont(font, size); c.setFillColor(color)
    yb = _y(y, size) + size * 0.18
    if align == "l":
        c.drawString(x, yb, s)
    elif align == "c":
        c.drawCentredString(x, yb, s)
    else:
        c.drawRightString(x, yb, s)


def para(x, y, w, html, size=13, leading=None, color=BROWN_DK, font="Sans",
         align=TA_LEFT, h=400):
    leading = leading or size * 1.32
    st = ParagraphStyle("p", fontName=font, fontSize=size, leading=leading,
                        textColor=color, alignment=align)
    p = Paragraph(html, st)
    pw, ph = p.wrapOn(c, w, h)
    p.drawOn(c, x, _y(y, ph))
    return ph


def chip(x, y, w, h, label, fill, fg, size=11, font="Sans-B", r=10):
    rrect(x, y, w, h, fill=fill, r=r)
    c.setFont(font, size); c.setFillColor(fg)
    c.drawCentredString(x + w / 2, _y(y, h) + h / 2 - size * 0.36, label)

# ============================================================================
# shared furniture
# ============================================================================

def header(kicker, title, num, total=12):
    rect(0, 0, W, 9, fill=BROWN)
    txt(66, 40, kicker.upper(), "Sans-B", 11.5, BROWN, "l")
    txt(66, 60, title, "Serif-B", 27, BROWN_DK, "l")
    rect(68, 104, 78, 3.4, fill=BROWN_SOFT)
    # footer
    txt(66, 506, "Adaptive Lightweight Secure Communication for Swarms",
        "Sans-I", 9, TEXT_MUT, "l")
    txt(W - 66, 506, f"{num:02d} / {total:02d}", "Sans", 9.5, TEXT_MUT, "r")


def card_titled(x, y, w, h, title, accent=BROWN, tsize=14):
    rrect(x, y, w, h, fill=CARD, stroke=CARD_LINE, lw=1, r=10, shadow=True)
    rrect(x, y, 6, h, fill=accent, r=3)
    if title:
        txt(x + 20, y + 16, title, "Serif-B", tsize, BROWN_DK, "l")
    return x + 20, y + (40 if title else 16)

# ============================================================================
# SLIDE 1 — Title
# ============================================================================

def slide_title():
    bg(BROWN_DK)
    # decorative swarm network, right side
    import math
    nodes = [(740, 150), (820, 110), (880, 175), (790, 235), (870, 260),
             (760, 320), (845, 350), (905, 130), (700, 235)]
    c.setStrokeColor(HexColor("#6E5743")); c.setLineWidth(1)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if math.dist(nodes[i], nodes[j]) < 110:
                c.line(nodes[i][0], H - nodes[i][1], nodes[j][0], H - nodes[j][1])
    for (nx, ny) in nodes:
        circle(nx, ny, 6.5, fill=TAN)
        circle(nx, ny, 11, stroke=HexColor("#6E5743"), lw=1)

    rect(66, 132, 11, 132, fill=BROWN_SOFT)
    txt(90, 138, "INNOPOLIS UNIVERSITY   ·   BACHELOR'S THESIS   ·   2026",
        "Sans-B", 12.5, TAN, "l")
    txt(90, 172, "Secure Communication", "Serif-B", 44, IVORY, "l")
    txt(90, 222, "Protocols for Swarm Robotics", "Serif-B", 44, IVORY, "l")
    para(90, 286, 560,
         "An <b>adaptive lightweight</b> framework that switches cryptographic "
         "profiles at runtime — grounded in a reproducible benchmark.",
         size=15.5, color=TAN, font="Sans-I", leading=22)

    # author / supervisor
    rrect(90, 380, 330, 96, fill=None, stroke=BROWN_SOFT, lw=1.2, r=8)
    txt(110, 398, "AUTHOR", "Sans-B", 10, BROWN_SOFT, "l")
    txt(110, 412, "Georgii Butakov", "Serif-B", 17, IVORY, "l")
    txt(110, 440, "SUPERVISOR", "Sans-B", 10, BROWN_SOFT, "l")
    txt(110, 454, "Oleg Bulichev", "Serif-B", 17, IVORY, "l")
    c.showPage()

# ============================================================================
# SLIDE 2 — Motivation
# ============================================================================

def slide_motivation():
    bg()
    header("Motivation", "One fixed cipher never fits the whole mission", 2)
    para(66, 150, 480,
         "Swarms coordinate through constant messaging over "
         "<b>dynamic wireless links</b> — on devices with limited energy and "
         "compute.", size=15, leading=22)
    para(66, 232, 480,
         "A permanently <b><font color='#5C3A21'>heavy</font></b> profile wastes "
         "throughput and battery. A permanently "
         "<b><font color='#8C6A4A'>lightweight</font></b> one is unsafe when the "
         "threat level rises.", size=15, leading=22)
    rrect(66, 330, 480, 86, fill=SAND, r=10)
    para(86, 348, 440,
         "Security and performance are <b>coupled</b> — they must be balanced at "
         "<b>runtime</b>, not fixed at design time.",
         size=15, leading=22, color=BROWN_DK, font="Sans-I")

    # see-saw schematic card
    bx, by, bw, bh = 590, 150, 304, 300
    rrect(bx, by, bw, bh, fill=CARD, stroke=CARD_LINE, lw=1, r=12, shadow=True)
    txt(bx + bw / 2, by + 24, "THE CORE TRADE-OFF", "Sans-B", 11.5, BROWN, "c")
    fx = bx + bw / 2                         # fulcrum centre x
    apex_y = by + 168                        # apex of fulcrum triangle
    # beam (tilted: security side down-left, performance up-right)
    line(bx + 44, by + 188, bx + bw - 44, by + 150, BROWN_DK, 5)
    tri(fx, apex_y + 22, 46, 40, BROWN_SOFT, up=True)   # fulcrum
    rect(fx - 38, apex_y + 42, 76, 9, fill=BROWN)       # base
    # security weight (low / left)
    chip(bx + 34, by + 192, 96, 52, "Security", HEAVY_C, IVORY, 12.5, "Sans-B", r=10)
    # performance weight (high / right)
    chip(bx + bw - 134, by + 138, 96, 48, "Performance", TAN, BROWN_DK, 12, "Sans-B", r=10)
    txt(bx + bw / 2, by + 256, "Adaptation re-balances", "Sans-I", 11.5, TEXT_MUT, "c")
    txt(bx + bw / 2, by + 274, "as conditions change", "Sans-I", 11.5, TEXT_MUT, "c")
    c.showPage()

# ============================================================================
# SLIDE 3 — Goal & Contributions
# ============================================================================

def slide_goal():
    bg()
    header("Aim & Contributions", "Design it formally — then measure it", 3)

    rrect(66, 150, 828, 80, fill=BROWN_DK, r=12)
    txt(90, 168, "GOAL", "Sans-B", 11, TAN, "l")
    para(90, 186, 780,
         "Design and evaluate a <b>reproducible adaptive secure-communication "
         "framework</b> for swarm-oriented systems that exposes the "
         "security–performance trade-off instead of assuming it.",
         size=14.5, color=IVORY, leading=20)

    cards = [
        ("01", "Formal model", BROWN,
         "Swarm as a dynamic graph with an adaptation function "
         "<b>F : S(t) → P</b> mapping state to crypto profile."),
        ("02", "Working prototype", BROWN_SOFT,
         "A pairwise benchmark with <b>heavy, balanced, lightweight</b> and "
         "<b>adaptive</b> operating modes."),
        ("03", "Bounded evidence", TAN,
         "Repeatable measurements of latency, throughput, switching and a "
         "crypto-work metric under real constraints."),
    ]
    cw, gap = 264, 18
    for i, (n, t, ac, body) in enumerate(cards):
        x = 66 + i * (cw + gap)
        rrect(x, 256, cw, 150, fill=CARD, stroke=CARD_LINE, lw=1, r=12, shadow=True)
        circle(x + 38, 296, 20, fill=ac)
        txt(x + 38, 290, n, "Serif-B", 16, IVORY, "c")
        txt(x + 70, 282, t, "Serif-B", 16, BROWN_DK, "l")
        para(x + 22, 332, cw - 44, body, size=12, color=TEXT_MUT, leading=17)

    rrect(66, 430, 828, 56, fill=SAND, r=10)
    para(90, 446, 780,
         "<b>Novelty:</b> a bounded formal model paired with an <b>executable "
         "benchmark</b> — adaptive crypto is measured, not just proposed.",
         size=13.5, color=BROWN_DK, font="Sans-I", leading=18)
    c.showPage()

# ============================================================================
# SLIDE 4 — Formal model
# ============================================================================

def slide_model():
    bg()
    header("Formal Model", "The swarm as a dynamic graph", 4)

    # left: graph G(V,E,t)
    lx, ly, lw, lh = 66, 150, 400, 300
    rrect(lx, ly, lw, lh, fill=CARD, stroke=CARD_LINE, lw=1, r=12, shadow=True)
    txt(lx + 20, ly + 16, "G ( V, E, t )", "Mono-B", 15, BROWN_DK, "l")
    txt(lx + 20, ly + 40, "nodes = agents   ·   edges = live links",
        "Sans-I", 10.5, TEXT_MUT, "l")
    import math
    nx0, ny0 = lx + lw / 2, ly + 175
    nodes = [(nx0 - 120, ny0 - 70), (nx0 - 30, ny0 - 95), (nx0 + 70, ny0 - 60),
             (nx0 + 120, ny0 + 25), (nx0 + 30, ny0 + 70), (nx0 - 70, ny0 + 60),
             (nx0 - 20, ny0 - 10)]
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if math.dist(nodes[i], nodes[j]) < 130:
                line(nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1],
                     TAN, 1.4)
    for k, (px, py) in enumerate(nodes):
        circle(px, py, 13, fill=BROWN if k != 6 else HEAVY_C)
        circle(px, py, 13, stroke=CARD, lw=2)
    txt(lx + lw / 2, ly + lh - 30, "each node: position · energy · keys · CPU",
        "Sans", 10.5, TEXT_MUT, "c")

    # right: adaptation function mapping
    rx, ry, rw, rh = 500, 150, 394, 300
    sx, ax = rx + 18, rx + 18           # state chips x
    txt(rx, ry + 4, "Adaptation function", "Serif-B", 16, BROWN_DK, "l")
    # state list
    txt(sx, ry + 44, "STATE  S(t)", "Sans-B", 10.5, BROWN, "l")
    states = ["energy  ē", "threat  θ", "density  ρ", "packet loss  λ"]
    for i, sname in enumerate(states):
        yy = ry + 66 + i * 40
        rrect(sx, yy, 150, 30, fill=SAND, r=8)
        txt(sx + 14, yy + 9, sname, "Mono", 11.5, BROWN_DK, "l")
    # F box
    fx, fy, fw, fh = rx + 178, ry + 96, 56, 96
    rrect(fx, fy, fw, fh, fill=BROWN_DK, r=10)
    txt(fx + fw / 2, fy + 32, "F", "Serif-B", 30, IVORY, "c")
    txt(fx + fw / 2, fy + 66, "select", "Sans", 9, TAN, "c")
    # arrows state->F
    for i in range(4):
        yy = ry + 66 + i * 40 + 15
        line(sx + 150, yy, fx, fy + fh / 2, BROWN_SOFT, 1.3)
    # profiles out
    px = fx + fw + 40
    profs = [("heavy", HEAVY_C, IVORY), ("balanced", BALANCED_C, IVORY),
             ("lightweight", LIGHT_C, BROWN_DK)]
    txt(px, ry + 44, "PROFILE  P", "Sans-B", 10.5, BROWN, "l")
    for i, (pn, pc, fg) in enumerate(profs):
        yy = ry + 78 + i * 40
        chip(px, yy, 118, 30, pn, pc, fg, 11.5, "Sans-B", r=8)
        line(fx + fw, fy + fh / 2, px, yy + 15, BROWN_SOFT, 1.3)

    rrect(66, 466, 828, 0, fill=None)  # spacer noop
    para(66, 462, 828,
         "<b>F : S(t) → P</b>  &nbsp;maps the observed runtime state to a "
         "discrete cryptographic profile — the optimisation view is "
         "approximated by a threshold selector.",
         size=12.5, color=TEXT_MUT, font="Sans-I", align=TA_CENTER)
    c.showPage()

# ============================================================================
# SLIDE 5 — Threat model & requirements
# ============================================================================

def slide_threat():
    bg()
    header("Threat Model", "What we defend against — and guarantee", 5)

    # adversaries (left)
    txt(66, 150, "ADVERSARY CAPABILITIES", "Sans-B", 11.5, BROWN, "l")
    advs = [
        ("Passive", "eavesdrops on traffic"),
        ("Active", "modifies / injects messages"),
        ("Compromised node", "leaks keys & memory"),
    ]
    for i, (a, d) in enumerate(advs):
        y = 178 + i * 70
        rrect(66, y, 360, 58, fill=CARD, stroke=CARD_LINE, lw=1, r=10, shadow=True)
        circle(96, y + 29, 14, fill=BROWN_SOFT)
        txt(96, y + 23, str(i + 1), "Serif-B", 14, IVORY, "c")
        txt(124, y + 12, a, "Serif-B", 15, BROWN_DK, "l")
        txt(124, y + 33, d, "Sans", 12, TEXT_MUT, "l")

    # requirements (right)
    txt(470, 150, "DATA-PLANE GUARANTEES", "Sans-B", 11.5, BROWN, "l")
    reqs = [
        ("Confidentiality", "AEAD encryption, unique nonce per message"),
        ("Authentication", "HMAC-SHA256 / sequence-bound hash token"),
        ("Integrity", "authenticated encryption tag"),
        ("Compromise containment", "per-epoch X25519 rekeying"),
    ]
    for i, (a, d) in enumerate(reqs):
        y = 178 + i * 66
        rrect(470, y, 424, 54, fill=CARD, stroke=CARD_LINE, lw=1, r=10, shadow=True)
        rrect(470, y, 6, 54, fill=BROWN, r=3)
        # check mark
        circle(500, y + 27, 11, fill=BROWN)
        c.setStrokeColor(IVORY); c.setLineWidth(2.2)
        c.line(495, H - (y + 28), 499, H - (y + 32))
        c.line(499, H - (y + 32), 506, H - (y + 22))
        txt(522, y + 9, a, "Serif-B", 14.5, BROWN_DK, "l")
        txt(522, y + 31, d, "Sans", 11.5, TEXT_MUT, "l")

    txt(66, 452, "Scope is bounded to the data plane — a fully authenticated "
        "control plane is named as future work.", "Sans-I", 12, TEXT_MUT, "l")
    c.showPage()

# ============================================================================
# SLIDE 6 — Cryptographic building blocks (hybrid stack)
# ============================================================================

def slide_blocks():
    bg()
    header("Building Blocks", "A hybrid stack — each primitive where it fits", 6)

    layers = [
        ("SESSION SETUP", "X25519  +  HKDF-SHA256",
         "Ephemeral key exchange per epoch → forward secrecy", BROWN_DK, IVORY,
         "periodic"),
        ("PAYLOAD PROTECTION", "AES-GCM   /   ChaCha20-Poly1305",
         "AEAD confidentiality + integrity, 96-bit nonce, 128-bit tag",
         BROWN_SOFT, IVORY, "per message"),
        ("RUNTIME AUTH", "HMAC-SHA256   /   hash token",
         "Lightweight origin & replay check on the data path", TAN, BROWN_DK,
         "per message"),
    ]
    y = 156
    for title, prim, desc, fill, fg, tag in layers:
        rrect(66, y, 700, 92, fill=fill, r=12, shadow=True)
        txt(92, y + 18, title, "Sans-B", 11, fg if fg == IVORY else BROWN, "l")
        txt(92, y + 36, prim, "Mono-B", 18, fg, "l")
        txt(92, y + 66, desc, "Sans", 12, fg if fg == BROWN_DK else IVORY, "l")
        # frequency tag on the right
        chip(632, y + 32, 110, 28, tag, IVORY if fill != TAN else CARD,
             BROWN_DK, 10.5, "Sans-B", r=14)
        if y < 320:
            tri(416, y + 92 + 11, 26, 16, BROWN, up=False)
        y += 116

    # side note card
    rrect(786, 156, 108, 320, fill=SAND, r=12)
    txt(840, 176, "WHY", "Sans-B", 11, BROWN, "c")
    para(800, 200, 80,
         "Expensive asymmetric work stays <b>off</b> the per-message path; "
         "only fast symmetric primitives run per packet.",
         size=11.5, color=BROWN_DK, leading=16, align=TA_CENTER)
    c.showPage()

# ============================================================================
# SLIDE 7 — Three profiles
# ============================================================================

def slide_profiles():
    bg()
    header("Profiles", "Three discrete operating points", 7)

    profs = [
        ("HEAVY", HEAVY_C, IVORY,
         ["AES-256-GCM", "HMAC-SHA256"],
         "Maximum protection", "0.250 MiB", "crypto work / msg"),
        ("BALANCED", BALANCED_C, IVORY,
         ["AES-192-GCM", "HMAC-SHA256"],
         "Mixed conditions", "0.250 MiB", "crypto work / msg"),
        ("LIGHTWEIGHT", LIGHT_C, BROWN_DK,
         ["ChaCha20-Poly1305", "seq-bound hash token"],
         "Efficiency first", "0.125 MiB", "crypto work / msg"),
    ]
    cw, gap = 264, 18
    for i, (name, ac, fg, prims, tag, val, sub) in enumerate(profs):
        x = 66 + i * (cw + gap)
        rrect(x, 156, cw, 300, fill=CARD, stroke=CARD_LINE, lw=1, r=14, shadow=True)
        rrect(x, 156, cw, 56, fill=ac, r=14)
        rect(x, 196, cw, 16, fill=ac)            # square off bottom of header
        txt(x + cw / 2, 174, name, "Serif-B", 20, fg, "c")
        # primitives
        yy = 232
        for pr in prims:
            rrect(x + 22, yy, cw - 44, 36, fill=SAND, r=8)
            txt(x + cw / 2, yy + 11, pr, "Mono-B", 12.5, BROWN_DK, "c")
            yy += 46
        txt(x + cw / 2, yy + 6, tag, "Sans-I", 12.5, TEXT_MUT, "c")
        # metric
        line(x + 30, 388, x + cw - 30, 388, CARD_LINE, 1)
        txt(x + cw / 2, 400, val, "Serif-B", 26, ac if ac != LIGHT_C else BROWN_DK, "c")
        txt(x + cw / 2, 432, sub, "Sans", 10.5, TEXT_MUT, "c")

    txt(W / 2, 474, "Lightweight does half the per-message crypto work of the "
        "authenticated profiles.", "Sans-I", 12.5, TEXT_MUT, "c")
    c.showPage()

# ============================================================================
# SLIDE 8 — Adaptation logic (decision tree)
# ============================================================================

def slide_logic():
    bg()
    header("Adaptation Logic", "A transparent threshold selector", 8)

    # decision tree
    # start
    rrect(380, 150, 200, 44, fill=BROWN_DK, r=10)
    txt(480, 164, "read  θ, ē  each tick", "Mono", 13, IVORY, "c")
    line(480, 194, 480, 224, BROWN_SOFT, 1.6)

    # decision 1: threat
    dw, dh = 150, 64
    cx1 = 480
    diamond(cx1, 256, 184, 84, fill=SAND_DEEP, stroke=BROWN, lw=1.4)
    txt(cx1, 248, "θ ≥ 0.8 ?", "Sans-B", 14, BROWN_DK, "c")
    # yes -> heavy (right)
    line(cx1 + 92, 256, 760, 256, BROWN, 1.6)
    txt(640, 244, "yes", "Sans-B", 11, BROWN, "c")
    chip(760, 232, 134, 48, "HEAVY", HEAVY_C, IVORY, 15, "Serif-B", r=10)
    # no -> down to decision 2
    line(cx1, 298, cx1, 330, BROWN, 1.6)
    txt(cx1 + 22, 312, "no", "Sans-B", 11, BROWN, "c")

    diamond(cx1, 366, 200, 84, fill=SAND_DEEP, stroke=BROWN, lw=1.4)
    txt(cx1, 358, "ē ≤ 0.2·Emax ?", "Sans-B", 13.5, BROWN_DK, "c")
    # yes -> lightweight (right)
    line(cx1 + 100, 366, 760, 366, BROWN, 1.6)
    txt(648, 354, "yes", "Sans-B", 11, BROWN, "c")
    chip(760, 342, 134, 48, "LIGHTWEIGHT", LIGHT_C, BROWN_DK, 13.5, "Serif-B", r=10)
    # no -> balanced (left/down)
    line(cx1, 408, cx1, 440, BROWN, 1.6)
    txt(cx1 + 22, 422, "no", "Sans-B", 11, BROWN, "c")
    chip(cx1 - 67, 440, 134, 46, "BALANCED", BALANCED_C, IVORY, 15, "Serif-B", r=10)

    # left explanatory column
    rrect(66, 220, 250, 230, fill=CARD, stroke=CARD_LINE, lw=1, r=12, shadow=True)
    txt(86, 236, "Two triggers", "Serif-B", 15, BROWN_DK, "l")
    para(86, 266, 214,
         "<b><font color='#5C3A21'>Escalate</font></b> to heavy when the threat "
         "estimate is high.", size=12.5, color=TEXT_MUT, leading=17)
    para(86, 326, 214,
         "<b><font color='#8C6A4A'>Fall back</font></b> to lightweight when "
         "energy runs low.", size=12.5, color=TEXT_MUT, leading=17)
    para(86, 386, 214,
         "Otherwise stay <b>balanced</b>. The selector cost is negligible vs. "
         "packet protection.", size=12.5, color=TEXT_MUT, leading=17)
    c.showPage()


def diamond(cx, cy, w, h, fill, stroke=None, lw=1.0):
    p = c.beginPath()
    p.moveTo(cx, H - (cy - h / 2))
    p.lineTo(cx + w / 2, H - cy)
    p.lineTo(cx, H - (cy + h / 2))
    p.lineTo(cx - w / 2, H - cy)
    p.close()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(lw)
    c.drawPath(p, stroke=0 if stroke is None else 1, fill=0 if fill is None else 1)

# ============================================================================
# SLIDE 9 — Benchmark setup
# ============================================================================

def slide_setup():
    bg()
    header("Benchmark", "A constrained, reproducible two-peer testbed", 9)

    # two peers exchanging
    py = 200
    for i, (px, name) in enumerate([(150, "peer_a"), (610, "peer_b")]):
        rrect(px, py, 200, 150, fill=CARD, stroke=CARD_LINE, lw=1.2, r=14, shadow=True)
        rrect(px, py, 200, 40, fill=BROWN_DK, r=14)
        rect(px, py + 26, 200, 14, fill=BROWN_DK)
        txt(px + 100, py + 12, name, "Mono-B", 15, IVORY, "c")
        txt(px + 100, py + 58, "Docker container", "Sans-B", 11.5, BROWN, "c")
        para(px + 16, py + 80, 168,
             "CPU 0.05 core · 128 MiB RAM<br/>X25519 · AEAD · HMAC / token",
             size=11, color=TEXT_MUT, align=TA_CENTER, leading=16)

    # gRPC link
    line(350, py + 75, 610, py + 75, BROWN_SOFT, 2.4)
    tri(610, py + 75, 14, 12, BROWN_SOFT, up=False)  # arrow head approximated
    chip(415, py + 58, 130, 34, "gRPC · 64 KiB msgs", SAND, BROWN_DK, 11.5, "Sans-B", r=16)

    # metrics strip
    txt(66, 380, "MEASURED PER RUN  (60 s · 3 repeats · 228 summary rows)",
        "Sans-B", 11.5, BROWN, "l")
    metrics = ["latency p50/p95/p99", "throughput & drops", "mode switches",
               "crypto work / msg", "energy proxy"]
    mw = 156
    for i, m in enumerate(metrics):
        x = 66 + i * (mw + 12)
        rrect(x, 406, mw, 50, fill=CARD, stroke=CARD_LINE, lw=1, r=10)
        rrect(x, 406, mw, 5, fill=[HEAVY_C, BROWN, BROWN_SOFT, TAN, SAND_DEEP][i], r=2)
        para(x + 10, 420, mw - 20, f"<b>{m}</b>", size=11, color=BROWN_DK,
             align=TA_CENTER, leading=14)
    c.showPage()

# ============================================================================
# SLIDE 10 — Results I: crypto work + policy fit
# ============================================================================

def slide_results1():
    bg()
    header("Results · I", "Adaptive spends protection where it is needed", 10)

    # LEFT: crypto work bar chart
    lx, ly, lw_, lh = 66, 156, 400, 300
    rrect(lx, ly, lw_, lh, fill=CARD, stroke=CARD_LINE, lw=1, r=12, shadow=True)
    txt(lx + 20, ly + 16, "Crypto work per delivered message", "Serif-B", 14.5,
        BROWN_DK, "l")
    txt(lx + 20, ly + 38, "MiB · lower is cheaper", "Sans-I", 10.5, TEXT_MUT, "l")
    bars = [("Heavy", 0.250, HEAVY_C), ("Balanced", 0.250, BALANCED_C),
            ("Adaptive", 0.224, BROWN), ("Lightweight", 0.125, LIGHT_C)]
    base_y = ly + 250
    max_h = 150
    bx0 = lx + 60
    bw = 58; bgap = 26
    axis_max = 0.27
    for i, (nm, val, col) in enumerate(bars):
        bx = bx0 + i * (bw + bgap)
        bh = max_h * (val / axis_max)
        rrect(bx, base_y - bh, bw, bh, fill=col, r=5)
        txt(bx + bw / 2, base_y - bh - 18, f"{val:.3f}",
            "Sans-B", 12, BROWN_DK, "c")
        txt(bx + bw / 2, base_y + 8, nm, "Sans", 10.5, TEXT_MUT, "c")
    line(lx + 20, base_y, lx + lw_ - 20, base_y, CARD_LINE, 1)

    # RIGHT: policy fit
    rx, ry, rw, rh = 494, 156, 400, 300
    rrect(rx, ry, rw, rh, fill=CARD, stroke=CARD_LINE, lw=1, r=12, shadow=True)
    txt(rx + 20, ry + 16, "Policy fit over the 60-s schedule", "Serif-B", 14.5,
        BROWN_DK, "l")
    txt(rx + 20, ry + 38, "share of message-time at the right protection level",
        "Sans-I", 10.5, TEXT_MUT, "l")
    # stacked bars: matched / over / under
    rows = [
        ("Adaptive", 100, 0, 0),
        ("Always heavy", 40, 60, 0),
        ("Always balanced", 60, 0, 40),
        ("Always light", 20, 0, 80),
    ]
    bar_x = rx + 150
    bar_w = 218
    yy = ry + 70
    MATCH = HexColor("#7C9A6E"); OVER = BROWN_SOFT; UNDER = HEAVY_C
    for nm, m, o, u in rows:
        txt(rx + 20, yy + 6, nm, "Sans", 11.5, BROWN_DK, "l")
        xoff = bar_x
        for val, col in [(m, MATCH), (o, OVER), (u, UNDER)]:
            if val > 0:
                rect(xoff, yy, bar_w * val / 100, 22, fill=col)
                xoff += bar_w * val / 100
        yy += 42
    # legend
    leg = [("matched", MATCH), ("over-protect", OVER), ("under-protect", UNDER)]
    lxx = rx + 22
    for nm, col in leg:
        rrect(lxx, ry + rh - 34, 12, 12, fill=col, r=2)
        txt(lxx + 18, ry + rh - 34, nm, "Sans", 10, TEXT_MUT, "l")
        lxx += 26 + len(nm) * 5.6

    # takeaway band
    rrect(66, 470, 828, 0)  # noop
    para(66, 466, 828,
         "Adaptive matches the required profile for the <b>whole</b> schedule "
         "and saves <b>26.7%</b> of protection cost vs. always-heavy — without "
         "the under-protection of always-light.",
         size=12.5, color=BROWN_DK, font="Sans-I", align=TA_CENTER)
    c.showPage()

# ============================================================================
# SLIDE 11 — Results II: saturation / CPU-limited
# ============================================================================

def slide_results2():
    bg()
    header("Results · II", "Under a tight CPU cap, transport dominates", 11)

    # delivered-vs-offered line chart (left)
    lx, ly, lw_, lh = 66, 156, 470, 290
    rrect(lx, ly, lw_, lh, fill=CARD, stroke=CARD_LINE, lw=1, r=12, shadow=True)
    txt(lx + 20, ly + 16, "Delivered throughput vs. offered rate", "Serif-B",
        14.5, BROWN_DK, "l")
    txt(lx + 20, ly + 38, "0.05-core cap · msg/s", "Sans-I", 10.5, TEXT_MUT, "l")
    # axes
    ax0, ay0 = lx + 56, ly + 240
    axw, axh = 370, 170
    line(ax0, ay0, ax0 + axw, ay0, BROWN_DK, 1.2)         # x
    line(ax0, ay0, ax0, ay0 - axh, BROWN_DK, 1.2)         # y
    # offered (ideal) dashed
    rates = [25, 50, 75, 100, 150, 200, 300]
    deliv = [25, 47, 56, 61, 60, 61, 62]                  # approx medians
    def px(r): return ax0 + axw * (r / 300)
    def py(v): return ay0 - axh * (v / 70)
    # ideal line: delivered = offered (steep y=x, exits top at rate 70)
    line(ax0, ay0, px(70), py(70), TAN, 1.4, dash=(4, 3))
    txt(px(72), py(68) - 2, "offered = ideal", "Sans-I", 9.5, TEXT_MUT, "l")
    # delivered curve
    pts = list(zip([px(r) for r in rates], [py(v) for v in deliv]))
    c.setStrokeColor(HEAVY_C); c.setLineWidth(2.4)
    for i in range(len(pts) - 1):
        c.line(pts[i][0], H - pts[i][1], pts[i + 1][0], H - pts[i + 1][1])
    for (qx, qy) in pts:
        circle(qx, qy, 3.4, fill=HEAVY_C)
    txt(px(150), py(62) - 18, "delivered (measured)", "Sans-B", 9.5, HEAVY_C, "l")
    # knee marker
    circle(px(75), py(56), 9, stroke=BROWN, lw=1.6)
    txt(px(75) - 4, py(56) + 22, "saturation knee", "Sans-B", 10, BROWN, "l")
    # axis labels
    for r in [25, 100, 200, 300]:
        txt(px(r), ay0 + 8, str(r), "Sans", 9, TEXT_MUT, "c")
    txt(ax0 - 30, ay0 - axh - 2, "70", "Sans", 9, TEXT_MUT, "c")
    txt(ax0 - 30, ay0 - 6, "0", "Sans", 9, TEXT_MUT, "c")

    # right: CPU sensitivity + findings
    rx = 558
    txt(rx, 156, "CPU CAP REMOVES THE BOTTLENECK", "Sans-B", 11.5, BROWN, "l")
    cpu = [("0.05 core", 65, "65% drop"), ("0.10 core", 22, "22% drop"),
           ("0.25 core", 0, "no drop")]
    for i, (cap, drop, lab) in enumerate(cpu):
        y = 184 + i * 56
        rrect(rx, y, 336, 46, fill=CARD, stroke=CARD_LINE, lw=1, r=10)
        txt(rx + 16, y + 15, cap, "Mono-B", 13, BROWN_DK, "l")
        # mini bar of drop
        rect(rx + 118, y + 16, 130, 14, fill=SAND)
        rect(rx + 118, y + 16, 130 * (drop / 70), 14, fill=HEAVY_C)
        txt(rx + 258, y + 14, lab, "Sans-B", 10.5, TEXT_MUT, "l")

    rrect(rx, 360, 336, 86, fill=SAND, r=10)
    para(rx + 18, 376, 300,
         "The knee is <b>CPU-bound</b>, not a crypto-design limit: at 0.25 core "
         "all four modes sustain the full rate.",
         size=12.5, color=BROWN_DK, leading=18)

    para(66, 462, 828,
         "Above ~75 msg/s the prototype is queue-limited, so end-to-end curves "
         "converge — the profile difference shows up in <b>crypto work</b>, not "
         "wall-clock latency.", size=12, color=TEXT_MUT, font="Sans-I",
         align=TA_CENTER)
    c.showPage()

# ============================================================================
# SLIDE 12 — Conclusion & future work
# ============================================================================

def slide_conclusion():
    bg(BROWN_DK)
    rect(0, 0, W, 9, fill=BROWN_SOFT)
    txt(66, 46, "CONCLUSION", "Sans-B", 12, TAN, "l")
    txt(66, 66, "Adaptive crypto, measured — not just proposed", "Serif-B", 28,
        IVORY, "l")
    rect(68, 112, 78, 3.4, fill=BROWN_SOFT)

    # three takeaways
    items = [
        ("Formalised", "swarm graph + adaptation function F : S(t) → P"),
        ("Built", "pairwise prototype with heavy / balanced / lightweight / adaptive"),
        ("Measured", "lightweight is the cheapest default; adaptive allocates "
         "protection correctly over time"),
    ]
    for i, (h, d) in enumerate(items):
        x = 66 + i * 280
        rrect(x, 150, 256, 132, fill=HexColor("#5A4334"), r=12)
        circle(x + 34, 186, 16, fill=TAN)
        c.setStrokeColor(BROWN_DK); c.setLineWidth(2.4)
        c.line(x + 28, H - 188, x + 32, H - 192); c.line(x + 32, H - 192, x + 41, H - 181)
        txt(x + 60, 178, h, "Serif-B", 17, IVORY, "l")
        para(x + 20, 214, 220, d, size=12.5, color=TAN, leading=17)

    # future work
    txt(66, 318, "WHAT COMES NEXT", "Sans-B", 12, TAN, "l")
    fut = [("Authenticated control plane", "signed bootstrap & profile updates"),
           ("Multi-peer validation", "churn, contention, async switching"),
           ("Hardware & post-quantum", "real platforms; hybrid PQ session setup")]
    for i, (h, d) in enumerate(fut):
        x = 66 + i * 280
        rrect(x, 344, 256, 92, fill=None, stroke=BROWN_SOFT, lw=1.2, r=12)
        txt(x + 18, 360, f"{i+1}", "Serif-B", 18, BROWN_SOFT, "l")
        txt(x + 44, 362, h, "Serif-B", 14.5, IVORY, "l")
        para(x + 18, 392, 220, d, size=12, color=TAN, leading=16)

    # closing line + thanks
    rrect(66, 460, 828, 50, fill=HexColor("#5A4334"), r=10)
    txt(86, 476, "Thank you — questions welcome.", "Serif-I", 16, IVORY, "l")
    txt(W - 86, 476, "github.com/mazzz3r/adaptive-swarm-crypto-thesis",
        "Mono", 11, TAN, "r")
    c.showPage()

# ----------------------------------------------------------------------------
slide_title()
slide_motivation()
slide_goal()
slide_model()
slide_threat()
slide_blocks()
slide_profiles()
slide_logic()
slide_setup()
slide_results1()
slide_results2()
slide_conclusion()
c.save()
print("wrote", OUT)
