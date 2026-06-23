#!/usr/bin/env python3
"""Thesis-defense deck — modern, minimal, ivory/brown.

Design language: lots of negative space, thin "skeleton" line figures,
hero typography (big numbers / few words), one idea per slide.
Pure vector output -> crisp at any zoom.

    python3 build_pdf.py  ->  adaptive-swarm-crypto.pdf
"""

import math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os

OUT = os.path.join(os.path.dirname(__file__), "adaptive-swarm-crypto.pdf")
W, H = 960.0, 540.0

# ---- palette ---------------------------------------------------------------
IVORY      = HexColor("#F4EEE0")
IVORY_2    = HexColor("#EFE7D5")
CARD       = HexColor("#FBF8F1")
LINE       = HexColor("#D9CBB2")
LINE_SOFT  = HexColor("#E6DBC6")
BROWN_DK   = HexColor("#43301F")
BROWN      = HexColor("#8A6646")
BROWN_SOFT = HexColor("#B0876255")  # unused placeholder
TAN        = HexColor("#C7A87E")
TAN_LT     = HexColor("#E3CFAD")
TEXT_MUT   = HexColor("#857157")
CREAM      = HexColor("#F3E9D6")

HEAVY_C    = HexColor("#5A3A22")
BALANCED_C = HexColor("#B0825A")
LIGHT_C    = HexColor("#D8C3A0")
GOOD_C     = HexColor("#7C9A6E")
WARN_C     = HexColor("#A8502E")

# ---- fonts -----------------------------------------------------------------
# Liberation (serif/sans) + DejaVu (mono). Search known font dirs so the deck
# builds on the usual Linux fontconfig layout and on other machines where the
# same TTFs live elsewhere. Override with DECK_FONT_DIRS (os.pathsep-separated).
_HERE = os.path.dirname(os.path.abspath(__file__))
_FONT_DIRS = [
    d for d in os.environ.get("DECK_FONT_DIRS", "").split(os.pathsep) if d
] + [
    os.path.join(_HERE, "fonts"),       # bundled with the deck → builds anywhere
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype",
    "/usr/share/fonts",
    "/Library/Fonts",
    os.path.expanduser("~/Library/Fonts"),
]


def _reg(name, filename):
    for d in _FONT_DIRS:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name, p))
            return
    raise FileNotFoundError(
        f"{filename} not found in {_FONT_DIRS}; set DECK_FONT_DIRS")


_reg("Serif",   "LiberationSerif-Regular.ttf")
_reg("Serif-B", "LiberationSerif-Bold.ttf")
_reg("Serif-I", "LiberationSerif-Italic.ttf")
_reg("Sans",    "LiberationSans-Regular.ttf")
_reg("Sans-B",  "LiberationSans-Bold.ttf")
_reg("Sans-I",  "LiberationSans-Italic.ttf")
_reg("Mono",    "DejaVuSansMono.ttf")
_reg("Mono-B",  "DejaVuSansMono-Bold.ttf")

c = canvas.Canvas(OUT, pagesize=(W, H))

# ============================================================================
# primitives (TOP-LEFT coordinates; y grows downward)
# ============================================================================

def _y(top, h=0):
    return H - top - h


def bg(color=IVORY):
    c.setFillColor(color); c.rect(0, 0, W, H, stroke=0, fill=1)


def rrect(x, y, w, h, fill=None, stroke=None, lw=1.2, r=10):
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(lw)
    c.roundRect(x, _y(y, h), w, h, r, stroke=0 if stroke is None else 1,
                fill=0 if fill is None else 1)


def _clip_card(x, y, w, h, r=10):
    """Clip subsequent drawing to a rounded card so accent bars keep its
    rounded corners. Caller must pair with c.restoreState()."""
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, _y(y, h), w, h, r)
    c.clipPath(p, stroke=0, fill=0)


def rect(x, y, w, h, fill=None, stroke=None, lw=1.2):
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(lw)
    c.rect(x, _y(y, h), w, h, stroke=0 if stroke is None else 1,
           fill=0 if fill is None else 1)


def circle(cx, cy, rad, fill=None, stroke=None, lw=1.2):
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(lw)
    c.circle(cx, H - cy, rad, stroke=0 if stroke is None else 1,
             fill=0 if fill is None else 1)


def line(x1, y1, x2, y2, color=BROWN, lw=1.4, dash=None, cap=1):
    c.setStrokeColor(color); c.setLineWidth(lw); c.setLineCap(cap)
    if dash:
        c.setDash(dash)
    c.line(x1, H - y1, x2, H - y2)
    c.setDash()
    c.setLineCap(0)


def poly(pts, fill=None, stroke=None, lw=1.4, close=True):
    p = c.beginPath()
    p.moveTo(pts[0][0], H - pts[0][1])
    for (px, py) in pts[1:]:
        p.lineTo(px, H - py)
    if close:
        p.close()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(lw); c.setLineJoin(1)
    c.drawPath(p, stroke=0 if stroke is None else 1, fill=0 if fill is None else 1)


def txt(x, y, s, font="Sans", size=12, color=BROWN_DK, align="l", tracking=0):
    c.setFont(font, size); c.setFillColor(color)
    yb = _y(y, size) + size * 0.16
    if tracking:
        # advance width with tracking so we can align manually
        sw = c.stringWidth(s, font, size) + tracking * max(len(s) - 1, 0)
        if align == "c":
            x = x - sw / 2
        elif align == "r":
            x = x - sw
        c.saveState()                # scope the Tc change so it can't leak
        t = c.beginText(x, yb)
        t.setFont(font, size); t.setFillColor(color)
        t.setCharSpace(tracking)
        t.textOut(s)
        c.drawText(t)
        c.restoreState()
        return
    if align == "l":
        c.drawString(x, yb, s)
    elif align == "c":
        c.drawCentredString(x, yb, s)
    else:
        c.drawRightString(x, yb, s)


def para(x, y, w, html, size=12.5, leading=None, color=TEXT_MUT, font="Sans",
         align=TA_LEFT, h=400):
    leading = leading or size * 1.4
    st = ParagraphStyle("p", fontName=font, fontSize=size, leading=leading,
                        textColor=color, alignment=align)
    p = Paragraph(html, st)
    pw, ph = p.wrapOn(c, w, h)
    p.drawOn(c, x, _y(y, ph))
    return ph


def kicker_label(x, y, s, color=BROWN):
    """Small spaced uppercase label with a leading tick."""
    rect(x, y + 1, 14, 3, fill=color)
    txt(x + 22, y - 4, s.upper(), "Sans-B", 11, color, "l", tracking=1.5)

# ---- skeleton line icons (drawn in a box centred at cx,cy, size s) ---------

def _pen(col, lw):
    c.setStrokeColor(col); c.setLineWidth(lw); c.setLineCap(1); c.setLineJoin(1)


def ic_eye(cx, cy, s, col, lw=2.2):
    _pen(col, lw)
    p = c.beginPath()
    p.moveTo(cx - s/2, H - cy)
    p.curveTo(cx - s/4, H - (cy - s*0.42), cx + s/4, H - (cy - s*0.42), cx + s/2, H - cy)
    p.curveTo(cx + s/4, H - (cy + s*0.42), cx - s/4, H - (cy + s*0.42), cx - s/2, H - cy)
    c.drawPath(p, stroke=1, fill=0)
    circle(cx, cy, s*0.16, fill=col)


def ic_pen(cx, cy, s, col, lw=2.2):
    _pen(col, lw)
    # diagonal body
    line(cx - s*0.34, cy + s*0.34, cx + s*0.18, cy - s*0.18, col, lw)
    line(cx + s*0.18, cy - s*0.18, cx + s*0.34, cy - s*0.02, col, lw)
    line(cx + s*0.34, cy - s*0.02, cx - s*0.18, cy + s*0.50, col, lw)
    # nib tip
    poly([(cx - s*0.34, cy + s*0.34), (cx - s*0.18, cy + s*0.50),
          (cx - s*0.40, cy + s*0.52)], fill=col)


def ic_key(cx, cy, s, col, lw=2.2):
    _pen(col, lw)
    circle(cx - s*0.18, cy, s*0.22, stroke=col, lw=lw)
    line(cx + s*0.08, cy, cx + s*0.46, cy, col, lw)   # shaft starts at the bow edge
    line(cx + s*0.30, cy, cx + s*0.30, cy + s*0.16, col, lw)
    line(cx + s*0.46, cy, cx + s*0.46, cy + s*0.20, col, lw)


def ic_lock(cx, cy, s, col, lw=2.2):
    _pen(col, lw)
    bw, bh = s*0.74, s*0.52
    rrect(cx - bw/2, cy - s*0.04, bw, bh, stroke=col, lw=lw, r=3)
    # shackle
    rad = s*0.24
    p = c.beginPath()
    p.arc(cx - rad, H - (cy - s*0.04) - rad*0 - 0, cx + rad,
          H - (cy - s*0.04) + 0, 0, 180)
    # simpler shackle via two lines + arc approximation
    c.setStrokeColor(col); c.setLineWidth(lw)
    c.arc(cx - rad, H - (cy - s*0.04), cx + rad, H - (cy - s*0.04) + 2*rad, 0, 180)
    circle(cx, cy + s*0.18, s*0.06, fill=col)


def ic_shield(cx, cy, s, col, lw=2.2, check=True):
    _pen(col, lw)
    top = cy - s*0.46
    poly([(cx, top), (cx + s*0.42, top + s*0.16), (cx + s*0.42, cy + s*0.10),
          (cx, cy + s*0.50), (cx - s*0.42, cy + s*0.10),
          (cx - s*0.42, top + s*0.16)], stroke=col, lw=lw)
    if check:
        _pen(col, lw)
        line(cx - s*0.18, cy + s*0.02, cx - s*0.02, cy + s*0.18, col, lw)
        line(cx - s*0.02, cy + s*0.18, cx + s*0.22, cy - s*0.16, col, lw)


def ic_check(cx, cy, s, col, lw=2.4):
    _pen(col, lw)
    line(cx - s*0.30, cy + s*0.02, cx - s*0.06, cy + s*0.26, col, lw)
    line(cx - s*0.06, cy + s*0.26, cx + s*0.32, cy - s*0.24, col, lw)


def ic_cpu(cx, cy, s, col, lw=2.0):
    _pen(col, lw)
    b = s*0.46
    rrect(cx - b, cy - b, 2*b, 2*b, stroke=col, lw=lw, r=3)
    rrect(cx - b*0.45, cy - b*0.45, b*0.9, b*0.9, stroke=col, lw=lw, r=2)
    for t in (-0.5, 0, 0.5):
        line(cx + t*b, cy - b, cx + t*b, cy - b - s*0.16, col, lw)
        line(cx + t*b, cy + b, cx + t*b, cy + b + s*0.16, col, lw)
        line(cx - b, cy + t*b, cx - b - s*0.16, cy + t*b, col, lw)
        line(cx + b, cy + t*b, cx + b + s*0.16, cy + t*b, col, lw)


def ic_node(cx, cy, s, col, lw=2.0):
    """tiny robot/agent glyph: rounded square + antenna + dot."""
    _pen(col, lw)
    b = s*0.42
    rrect(cx - b, cy - b*0.7, 2*b, 1.5*b, stroke=col, lw=lw, r=3)
    line(cx, cy - b*0.7, cx, cy - b*0.7 - s*0.18, col, lw)
    circle(cx, cy - b*0.7 - s*0.22, s*0.06, fill=col)
    circle(cx - b*0.4, cy, s*0.05, fill=col)
    circle(cx + b*0.4, cy, s*0.05, fill=col)

# ============================================================================
# shared furniture
# ============================================================================

def header(kicker, title, num, title_size=27):
    rect(66, 50, 4, 58, fill=BROWN)
    txt(84, 54, kicker.upper(), "Sans-B", 11, BROWN, "l", tracking=1.6)
    txt(83, 72, title, "Serif-B", title_size, BROWN_DK, "l")
    txt(W - 66, 508, f"{num:02d} — 12", "Sans", 9.5, TEXT_MUT, "r")


def chip(x, y, w, h, label, fill, fg, size=11, font="Sans-B", r=10, stroke=None):
    rrect(x, y, w, h, fill=fill, r=r, stroke=stroke)
    c.setFont(font, size); c.setFillColor(fg)
    c.drawCentredString(x + w/2, _y(y, h) + h/2 - size*0.34, label)


def stat(cx, top, value, label, vcolor=BROWN_DK, vsize=52, lcolor=TEXT_MUT,
         lsize=11, unit=None):
    txt(cx, top, value, "Serif-B", vsize, vcolor, "c")
    if unit:
        txt(cx, top + vsize*0.06, unit, "Sans", lsize, lcolor, "c")
    txt(cx, top + vsize + 6, label.upper(), "Sans-B", lsize, lcolor, "c", tracking=1.2)

# ============================================================================
# 01 — Title
# ============================================================================

def s_title():
    bg(BROWN_DK)
    # skeleton swarm network (right)
    random_nodes = [(700, 250), (770, 150), (845, 205), (905, 130),
                    (880, 300), (800, 350), (720, 360), (915, 380),
                    (790, 255)]
    c.setStrokeColor(HexColor("#6A5238")); c.setLineWidth(1)
    for i in range(len(random_nodes)):
        for j in range(i+1, len(random_nodes)):
            if math.dist(random_nodes[i], random_nodes[j]) < 105:
                c.line(random_nodes[i][0], H-random_nodes[i][1],
                       random_nodes[j][0], H-random_nodes[j][1])
    for k, (nx, ny) in enumerate(random_nodes):
        if k == 8:
            circle(nx, ny, 9, fill=TAN)
        else:
            circle(nx, ny, 8, fill=BROWN_DK, stroke=TAN, lw=1.6)

    rect(66, 150, 4, 150, fill=TAN)
    txt(84, 150, "INNOPOLIS UNIVERSITY   ·   BACHELOR'S THESIS   ·   2026",
        "Sans-B", 11.5, TAN, "l", tracking=1.4)
    txt(83, 182, "Secure Communication", "Serif-B", 46, IVORY, "l")
    txt(83, 234, "for Swarm Robotics", "Serif-B", 46, IVORY, "l")
    txt(84, 300, "Adaptive lightweight cryptography that switches at runtime.",
        "Sans", 15, TAN, "l")
    txt(84, 330, "search & rescue   ·   agriculture   ·   inspection   ·   defence",
        "Sans", 12, BROWN, "l")

    txt(84, 408, "AUTHOR", "Sans-B", 10, BROWN, "l", tracking=1.4)
    txt(84, 422, "Georgii Butakov", "Serif-B", 18, IVORY, "l")
    txt(360, 408, "SUPERVISOR", "Sans-B", 10, BROWN, "l", tracking=1.4)
    txt(360, 422, "Oleg Bulichev", "Serif-B", 18, IVORY, "l")
    c.showPage()

# ============================================================================
# 02 — Context : what a swarm is, where it runs, why it matters now
# ============================================================================

def s_context():
    bg()
    header("Context", "Swarms are leaving the lab", 2)

    # left: swarm schematic — agents + live links
    kicker_label(96, 178, "what it is", BROWN)
    nodes = [(166, 262), (248, 224), (334, 246), (402, 306),
             (372, 390), (286, 420), (196, 376), (262, 318), (344, 336)]
    hub = 7
    c.setStrokeColor(TAN); c.setLineWidth(1.3); c.setLineCap(1)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if math.dist(nodes[i], nodes[j]) < 104:
                c.line(nodes[i][0], H - nodes[i][1],
                       nodes[j][0], H - nodes[j][1])
    for k, (nx, ny) in enumerate(nodes):
        if k == hub:
            circle(nx, ny, 9, fill=HEAVY_C)
        else:
            circle(nx, ny, 7, fill=CARD, stroke=BROWN, lw=1.8)
    txt(283, 452, "agents linked by live, shifting wireless channels",
        "Sans-I", 12, TEXT_MUT, "c")

    line(500, 196, 500, 446, LINE_SOFT, 1.2)

    # right: why it matters now — three short beats
    kicker_label(540, 178, "why it matters now", HEAVY_C)
    pts = [
        ("Communication is the system",
         "no central controller — agents act only on what they exchange"),
        ("Already in the field",
         "search & rescue · agriculture · inspection · defence"),
        ("An open research front",
         "lightweight crypto is active (NIST LWC, COSIC) — "
         "adapting it at runtime is not"),
    ]
    for i, (t, d) in enumerate(pts):
        y = 232 + i * 76
        circle(550, y + 6, 4, fill=HEAVY_C)
        txt(568, y - 4, t, "Serif-B", 16, BROWN_DK, "l")
        para(568, y + 18, 322, d, size=12, color=TEXT_MUT, leading=16)

    txt(W/2, 478,
        "Growing deployment makes protected swarm communication a timely, necessary problem.",
        "Serif-I", 13.5, BROWN, "c")
    c.showPage()

# ============================================================================
# 03 — Motivation : one big idea + skeleton spectrum
# ============================================================================

def s_motivation():
    bg()
    header("The problem", "No single cipher fits a whole mission", 3)

    # big spectrum slider
    sx, ex, yy = 150, 810, 300
    line(sx, yy, ex, yy, LINE, 3)
    # ticks
    for t, lab, col in [(0.0, "LIGHTWEIGHT", LIGHT_C), (0.5, "BALANCED", BALANCED_C),
                        (1.0, "HEAVY", HEAVY_C)]:
        x = sx + (ex - sx) * t
        circle(x, yy, 7, fill=col, stroke=CARD, lw=2)
        txt(x, yy + 26, lab, "Sans-B", 11.5, BROWN_DK, "c", tracking=1)
    # end captions
    txt(sx, yy - 34, "efficiency", "Serif-I", 16, TEXT_MUT, "l")
    txt(ex, yy - 34, "protection", "Serif-I", 16, TEXT_MUT, "r")

    # two failure modes, minimal
    rrect(150, 372, 312, 92, stroke=LINE, fill=CARD, r=12)
    txt(170, 392, "Always heavy", "Serif-B", 16, HEAVY_C, "l")
    txt(170, 420, "wastes throughput & battery", "Sans", 13, TEXT_MUT, "l")
    rrect(498, 372, 312, 92, stroke=LINE, fill=CARD, r=12)
    txt(518, 392, "Always light", "Serif-B", 16, BALANCED_C, "l")
    txt(518, 420, "unsafe when threat rises", "Sans", 13, TEXT_MUT, "l")

    txt(480, 178, "Security and performance are coupled —",
        "Serif", 19, BROWN_DK, "c")
    txt(480, 204, "so balance them while the mission runs.",
        "Serif-I", 19, BROWN, "c")
    c.showPage()

# ============================================================================
# 03 — Literature & the gap : two columns
# ============================================================================

def s_literature():
    bg()
    header("Literature", "Strong primitives — but fixed for the whole mission", 4)

    kicker_label(96, 178, "what the field offers", BROWN)
    field = [
        ("Lightweight crypto",
         "ECC, AEAD, hash tokens — efficient on constrained nodes"),
        ("Decentralised trust",
         "blockchain & attestation — strong assurance, heavy stack"),
        ("Resilient comms",
         "self-healing relays, risk-aware routing — little built-in security"),
    ]
    for i, (t, d) in enumerate(field):
        y = 232 + i * 76
        circle(106, y + 6, 4, fill=BROWN)
        txt(124, y - 4, t, "Serif-B", 16, BROWN_DK, "l")
        para(124, y + 18, 330, d, size=12, color=TEXT_MUT, leading=16)

    line(500, 196, 500, 446, LINE_SOFT, 1.2)

    kicker_label(540, 178, "the gap", HEAVY_C)
    gaps = [
        ("Static configuration",
         "security parameters fixed for the whole mission"),
        ("Fragmented layers",
         "trust, resilience & message protection studied apart"),
        ("No executable comparison",
         "adaptive ideas rarely benchmarked against static baselines"),
    ]
    for i, (t, d) in enumerate(gaps):
        y = 232 + i * 76
        circle(550, y + 6, 4, fill=HEAVY_C)
        txt(568, y - 4, t, "Serif-B", 16, BROWN_DK, "l")
        para(568, y + 18, 322, d, size=12, color=TEXT_MUT, leading=16)

    txt(W/2, 470,
        "Adaptive control of crypto settings is studied far less than the primitives themselves.",
        "Serif-I", 14, BROWN, "c")
    c.showPage()

# ============================================================================
# 04 — Aim, research question & contributions
# ============================================================================

def s_aim():
    bg()
    header("Aim & research question",
           "Does adapting crypto at runtime pay off?", 5, title_size=26)
    txt(84, 118, "— can it hold the right protection at lower cost than a fixed profile?",
        "Serif-I", 16, BROWN, "l")

    txt(66, 172, "HOW THIS THESIS ANSWERS IT", "Sans-B", 10.5, BROWN, "l", tracking=1.8)

    cols = [
        ("01", "MODEL", "Swarm graph + adaptation function",
         "F : S(t) → P", BROWN),
        ("02", "PROTOTYPE", "Pairwise testbed, four modes",
         "incl. adaptive switching", BALANCED_C),
        ("03", "EVIDENCE", "Measured in running code",
         "228 benchmark runs", HEAVY_C),
    ]
    cw = 252; gap = 36; x0 = 66; top = 206
    for i, (n, t, desc, mono, ac) in enumerate(cols):
        x = x0 + i * (cw + gap)
        txt(x, top, n, "Serif-B", 42, TAN, "l")
        line(x, top + 62, x + cw, top + 62, LINE, 1.4)
        txt(x, top + 78, t, "Sans-B", 14, BROWN_DK, "l", tracking=2)
        para(x, top + 106, cw, desc, size=13.5, color=TEXT_MUT, leading=19)
        txt(x, top + 172, mono, "Mono-B", 12, ac, "l")

    txt(W/2, 472, "Novelty: a bounded formal model paired with an executable benchmark.",
        "Serif-I", 15, BROWN, "c")
    c.showPage()

# ============================================================================
# 04 — Formal model : skeleton graph -> F -> P
# ============================================================================

def s_model():
    bg()
    header("Formal model", "The swarm as a dynamic graph", 6)

    # left: skeleton graph
    txt(280, 176, "G ( V, E, t )", "Mono-B", 18, BROWN_DK, "c")
    txt(280, 202, "nodes = agents   ·   edges = live links", "Sans", 12, TEXT_MUT, "c")
    cxg, cyg = 280, 332
    nodes = [(cxg-132, cyg-74), (cxg-18, cyg-92), (cxg+96, cyg-62),
             (cxg+134, cyg+30), (cxg+24, cyg+84), (cxg-96, cyg+68), (cxg-6, cyg-4)]
    nsize = [30 if k == 6 else 26 for k in range(len(nodes))]
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            xi, yi = nodes[i]; xj, yj = nodes[j]
            d = math.dist(nodes[i], nodes[j])
            if d < 140:
                ux, uy = (xj - xi) / d, (yj - yi) / d
                ri, rj = nsize[i] * 0.55, nsize[j] * 0.55   # stop at body edge
                line(xi + ux*ri, yi + uy*ri, xj - ux*rj, yj - uy*rj, TAN, 1.4)
    for k, (px, py) in enumerate(nodes):
        ic_node(px, py, 30 if k == 6 else 26, HEAVY_C if k == 6 else BROWN, lw=2.1)
    txt(280, 450, "each node carries energy · keys · position",
        "Sans-I", 12, TEXT_MUT, "c")

    # divider
    line(560, 176, 560, 478, LINE_SOFT, 1.2)

    # right: vertical S(t) -> F -> P flow
    rcx = 728
    kicker_label(616, 178, "the adaptation function", BROWN)
    txt(616, 202, "F : S(t) → P", "Mono-B", 24, BROWN_DK, "l")

    # S(t) token
    rrect(616, 262, 224, 58, stroke=LINE, fill=CARD, r=12)
    txt(rcx, 274, "S(t)", "Serif-B", 18, BROWN_DK, "c")
    txt(rcx, 298, "energy · threat · density · loss", "Sans", 11, TEXT_MUT, "c")
    line(rcx, 320, rcx, 344, TAN, 1.6)
    poly([(rcx-5, 338), (rcx+5, 338), (rcx, 344)], fill=TAN)

    # F node
    circle(rcx, 370, 23, fill=BROWN_DK)
    txt(rcx, 360, "F", "Serif-B", 22, IVORY, "c")
    line(rcx, 393, rcx, 417, TAN, 1.6)
    poly([(rcx-5, 411), (rcx+5, 411), (rcx, 417)], fill=TAN)

    # P token: three profile dots, centred as a group with padding
    rrect(616, 418, 224, 60, stroke=LINE, fill=CARD, r=12)
    txt(rcx, 430, "P", "Serif-B", 18, BROWN_DK, "c")
    profs = [("heavy", HEAVY_C), ("balanced", BALANCED_C), ("light", LIGHT_C)]
    igap = 22
    widths = [14 + c.stringWidth(pn, "Sans-B", 10.5) for pn, _ in profs]
    gx = 616 + (224 - (sum(widths) + igap * (len(profs) - 1))) / 2
    for (pn, pc), wseg in zip(profs, widths):
        circle(gx + 4, 463, 4.5, fill=pc)
        txt(gx + 14, 458, pn, "Sans-B", 10.5, BROWN_DK, "l")
        gx += wseg + igap
    c.showPage()

# ============================================================================
# 06 — Security model : adversary -> hybrid stack that answers it
# ============================================================================

def s_security():
    bg()
    header("Security model", "Three threats, and a data plane that adapts", 7)

    # left: adversary capabilities
    kicker_label(96, 178, "the adversary can", HEAVY_C)
    adv = [(ic_eye, "Eavesdrop", "read traffic"),
           (ic_pen, "Tamper", "inject / modify"),
           (ic_key, "Compromise", "leak keys & memory")]
    for i, (ic, t, d) in enumerate(adv):
        y = 252 + i * 76
        circle(126, y, 23, stroke=LINE, fill=CARD, lw=1.4)
        ic(126, y, 27, HEAVY_C)
        txt(166, y - 13, t, "Serif-B", 16, BROWN_DK, "l")
        txt(166, y + 7, d, "Sans", 12, TEXT_MUT, "l")

    line(452, 196, 452, 452, LINE_SOFT, 1.2)

    # right: the stack — a fixed setup layer + an adaptive data-plane layer
    x, w = 496, 398
    kicker_label(x, 178, "our defence", GOOD_C)

    y0, h0 = 216, 66
    y1, h1 = 300, 150
    rrect(x, y0, w, h0, stroke=LINE, fill=CARD, r=12)
    _clip_card(x, y0, w, h0, 12)
    rect(x, y0, 5, h0, fill=BROWN_DK)
    c.restoreState()
    txt(x + 22, y0 + 15, "SESSION SETUP", "Sans-B", 9.5, BROWN, "l", tracking=1.6)
    chip(x + w - 82, y0 + 19, 66, 24, "fixed", IVORY_2, BROWN, 9.5, "Sans-B", r=12)
    txt(x + 22, y0 + 32, "X25519 + HKDF-SHA256", "Mono-B", 13, BROWN_DK, "l")
    txt(x + 22, y0 + 48, "forward secrecy · epoch rekeying", "Sans", 11, TEXT_MUT, "l")

    line(x + w/2, y0 + h0 + 2, x + w/2, y1 - 2, TAN, 1.4)
    poly([(x + w/2 - 4, y1 - 8), (x + w/2 + 4, y1 - 8), (x + w/2, y1 - 2)],
         fill=TAN)

    rrect(x, y1, w, h1, stroke=LINE, fill=CARD, r=12)
    _clip_card(x, y1, w, h1, 12)
    seg = h1 / 3                       # 3-colour edge = three runtime modes
    for k, col in enumerate((HEAVY_C, BALANCED_C, LIGHT_C)):
        rect(x, y1 + k * seg, 5, seg, fill=col)
    c.restoreState()
    txt(x + 22, y1 + 16, "DATA PLANE", "Sans-B", 9.5, BROWN, "l", tracking=1.6)
    chip(x + w - 98, y1 + 19, 82, 24, "adaptive", TAN_LT, BROWN_DK, 9.5,
         "Sans-B", r=12)
    rows = [("Heavy", HEAVY_C, "AES-256-GCM + HMAC"),
            ("Balanced", BALANCED_C, "AES-192-GCM + HMAC"),
            ("Lightweight", LIGHT_C, "ChaCha20-Poly1305 + token")]
    ry = y1 + 54
    for nm, col, prim in rows:
        circle(x + 26, ry, 5, fill=col,
               stroke=(BROWN if col == LIGHT_C else None), lw=1)
        txt(x + 40, ry - 6, nm, "Sans-B", 11.5, BROWN_DK, "l")
        txt(x + 162, ry - 6, prim, "Mono", 11.5, TEXT_MUT, "l")
        ry += 32
    c.showPage()

# ============================================================================
# 07 — Profiles : three columns, hero crypto-work numbers
# ============================================================================

def s_profiles():
    bg()
    header("Profiles", "Three operating points", 8)

    profs = [
        ("HEAVY", HEAVY_C, IVORY, "AES-256-GCM", "+ HMAC-SHA256",
         "High threat", "strongest protection"),
        ("BALANCED", BALANCED_C, IVORY, "AES-192-GCM", "+ HMAC-SHA256",
         "Steady state", "balanced default"),
        ("LIGHTWEIGHT", LIGHT_C, BROWN_DK, "ChaCha20-Poly1305", "+ hash token",
         "Low energy", "lowest per-message cost"),
    ]
    cw = 268; gap = 14; x0 = 66; top = 178; hh = 250
    for i, (name, ac, fg, p1, p2, level, note) in enumerate(profs):
        x = x0 + i * (cw + gap)
        ac_t = ac if ac != LIGHT_C else BROWN_DK
        rrect(x, top, cw, hh, stroke=LINE, fill=CARD, r=14)
        _clip_card(x, top, cw, hh, 14)
        rect(x, top, cw, 6, fill=ac)
        c.restoreState()
        chip(x + 22, top + 26, 110, 26, name, ac, fg, 11, "Sans-B", r=13)
        if name == "HEAVY":
            qlbl, qsz = "GROVER-RESISTANT", 8.5
            qw = pdfmetrics.stringWidth(qlbl, "Sans-B", qsz) + 22
            chip(x + cw - 22 - qw, top + 28, qw, 22, qlbl, GOOD_C, IVORY, qsz, "Sans-B", r=11)
        txt(x + 24, top + 70, p1, "Mono-B", 14.5, BROWN_DK, "l")
        txt(x + 24, top + 92, p2, "Mono", 12.5, TEXT_MUT, "l")
        line(x + 24, top + 126, x + cw - 24, top + 126, LINE_SOFT, 1.2)
        txt(x + 24, top + 150, "SELECTED WHEN", "Sans-B", 9.5, TEXT_MUT, "l", tracking=1.6)
        txt(x + 24, top + 174, level, "Serif-B", 19, ac_t, "l")
        txt(x + 24, top + 198, note, "Sans", 12, TEXT_MUT, "l")

    txt(W/2, 452, "Three operating points on one protection-versus-cost axis.",
        "Serif-I", 15, BROWN, "c")
    txt(W/2, 480, "A simple rule moves between them at runtime: high threat selects heavy, low energy drops to lightweight, otherwise balanced.",
        "Sans-I", 11, TEXT_MUT, "c")
    c.showPage()

# ============================================================================
# 08 — Adaptation logic : skeleton decision tree
# ============================================================================

def diamond(cx, cy, w, h, fill=None, stroke=None, lw=1.4):
    poly([(cx, cy - h/2), (cx + w/2, cy), (cx, cy + h/2), (cx - w/2, cy)],
         fill=fill, stroke=stroke, lw=lw)


def s_logic():
    bg()
    header("Adaptation logic", "A transparent threshold selector", 8)

    cx = 430
    chip(cx - 145, 184, 290, 40, "read θ, ē  every tick", BROWN_DK, IVORY, 13, "Mono", r=10)
    line(cx, 224, cx, 252, TAN, 1.6)

    diamond(cx, 286, 190, 78, fill=CREAM, stroke=BROWN, lw=1.6)
    txt(cx, 280, "θ ≥ 0.8 ?", "Sans-B", 15, BROWN_DK, "c")
    line(cx + 95, 286, 730, 286, BROWN, 1.6)
    txt((cx+95+730)/2, 274, "yes", "Sans-B", 11, BROWN, "c")
    chip(730, 262, 150, 48, "HEAVY", HEAVY_C, IVORY, 16, "Serif-B", r=12)
    line(cx, 325, cx, 356, BROWN, 1.6)
    txt(cx + 18, 340, "no", "Sans-B", 11, BROWN, "c")

    diamond(cx, 392, 210, 78, fill=CREAM, stroke=BROWN, lw=1.6)
    txt(cx, 386, "ē ≤ 0.2·Emax ?", "Sans-B", 14, BROWN_DK, "c")
    line(cx + 105, 392, 730, 392, BROWN, 1.6)
    txt((cx+105+730)/2, 380, "yes", "Sans-B", 11, BROWN, "c")
    chip(730, 368, 150, 48, "LIGHTWEIGHT", LIGHT_C, BROWN_DK, 14, "Serif-B", r=12)
    line(cx, 431, cx, 458, BROWN, 1.6)
    txt(cx + 18, 446, "no", "Sans-B", 11, BROWN, "c")
    chip(cx - 75, 458, 150, 44, "BALANCED", BALANCED_C, IVORY, 16, "Serif-B", r=12)

    # left micro-legend
    txt(96, 200, "TWO TRIGGERS", "Sans-B", 10.5, BROWN, "l", tracking=1.8)
    txt(96, 230, "↑ threat", "Serif-B", 16, HEAVY_C, "l")
    txt(96, 252, "escalate to heavy", "Sans", 12, TEXT_MUT, "l")
    txt(96, 292, "↓ energy", "Serif-B", 16, BALANCED_C, "l")
    txt(96, 314, "fall back to light", "Sans", 12, TEXT_MUT, "l")
    txt(96, 354, "otherwise", "Serif-B", 16, BROWN, "l")
    txt(96, 376, "stay balanced", "Sans", 12, TEXT_MUT, "l")
    c.showPage()

# ============================================================================
# 09 — Benchmark : hero constraint stats + tiny peer schematic
# ============================================================================

def s_setup():
    bg()
    header("Benchmark", "A constrained, reproducible testbed", 9)

    # tiny two-peer schematic
    py = 210
    for (px, name) in [(250, "peer_a"), (650, "peer_b")]:
        rrect(px - 70, py - 34, 140, 68, stroke=BROWN, fill=CARD, lw=1.6, r=12)
        ic_node(px, py - 6, 30, BROWN, lw=2)
        txt(px, py + 16, name, "Mono-B", 12, BROWN_DK, "c")
    line(326, py, 566, py, TAN, 2)
    poly([(566, py - 5), (566, py + 5), (574, py)], fill=TAN)
    chip(398, py - 17, 104, 34, "gRPC", IVORY_2, BROWN, 12, "Mono-B", r=16)
    txt(450, py + 52, "two containers · encrypted data path", "Sans-I", 12, TEXT_MUT, "c")

    # hero constraint stats
    line(96, 300, 864, 300, LINE_SOFT, 1.2)
    stats = [("0.05", "CPU CORES", "main · up to 0.25"), ("128", "MiB RAM", None),
             ("64", "KiB / MSG", None), ("60", "SECONDS", None), ("×3", "REPEATS", None)]
    n = len(stats); slot = 768 / n
    for i, (v, l, note) in enumerate(stats):
        cx = 96 + slot * i + slot/2
        txt(cx, 330, v, "Serif-B", 46, BROWN_DK, "c")
        txt(cx, 388, l, "Sans-B", 10.5, TEXT_MUT, "c", tracking=1.4)
        if note:
            txt(cx, 404, note, "Sans-I", 8.5, TEXT_MUT, "c")

    txt(W/2, 446, "Measured: latency · throughput · drops · switches · crypto work",
        "Sans", 13, TEXT_MUT, "c")
    c.showPage()

# ============================================================================
# 10 — Results I : crypto work bars + policy fit
# ============================================================================

def s_results1():
    bg()
    header("Results · I", "Adaptive avoids both failure modes", 10)
    txt(84, 116, "Every static profile fails one way; adaptive fails neither.",
        "Serif-I", 15, BROWN, "l")

    # failure-mode scorecard
    mx = 110                                  # profile-name column
    cu, co, cc = 462, 650, 818                # under / over / cost column centres
    hy = 198
    txt(mx, hy, "PROFILE", "Sans-B", 10, TEXT_MUT, "l", tracking=1.4)
    txt(cu, hy, "UNDER-PROTECTS", "Sans-B", 10, BROWN, "c", tracking=1.2)
    txt(co, hy, "OVER-PROTECTS", "Sans-B", 10, BROWN, "c", tracking=1.2)
    txt(cc, hy, "PROTECTION COST", "Sans-B", 10, BROWN, "c", tracking=1.2)
    txt(cc, hy + 14, "vs. always-heavy", "Sans-I", 8.5, TEXT_MUT, "c")
    line(90, hy + 28, 884, hy + 28, LINE, 1.2)

    rows = [
        ("Always-heavy",    ("never", GOOD_C), ("60% of run", WARN_C), "100%"),
        ("Always-balanced", ("40% of run", WARN_C), ("20% of run", WARN_C), "67%"),
        ("Always-light",    ("80% of run", WARN_C), ("never", GOOD_C), "33%"),
        ("Adaptive",        ("never", GOOD_C), ("never", GOOD_C), "73%"),
    ]
    ry, rh = 262, 50
    for i, (nm, (ut, uc), (ot, oc), cost) in enumerate(rows):
        y = ry + i * rh
        adaptive = (i == len(rows) - 1)
        if adaptive:
            rrect(90, y - 25, 794, 48, fill=CARD, stroke=LINE, r=10)
        txt(mx, y - 8, nm, "Serif-B" if adaptive else "Serif", 16, BROWN_DK, "l")
        txt(cu, y - 8, ut, "Sans-B", 13, uc, "c")
        txt(co, y - 8, ot, "Sans-B", 13, oc, "c")
        txt(cc, y - 8, cost, "Serif-B", 16, BROWN_DK, "c")

    txt(W/2, 466,
        "Only adaptive is never wrong either way — at 27% less protection work than always-heavy.",
        "Serif-I", 14.5, BROWN, "c")
    txt(W/2, 490,
        "And the cost tracks the mission — a calmer schedule trends toward lightweight's cost, still escalating when it matters.",
        "Sans-I", 11, TEXT_MUT, "c")
    c.showPage()

# ============================================================================
# 11 — Results II : saturation curve + CPU bars
# ============================================================================

def s_results2():
    bg()
    header("Results · II", "Under a tight CPU cap, transport dominates", 11)

    # LEFT: delivered vs offered
    txt(96, 186, "DELIVERED vs OFFERED RATE", "Sans-B", 10.5, BROWN, "l", tracking=1.6)
    txt(96, 202, "0.05-core cap", "Sans-I", 11, TEXT_MUT, "l")
    ax0, ay0, axw, axh = 130, 410, 330, 160
    line(ax0, ay0, ax0 + axw, ay0, BROWN_DK, 1.4)
    line(ax0, ay0, ax0, ay0 - axh, BROWN_DK, 1.4)
    def px(r): return ax0 + axw * r/300
    def py(v): return ay0 - axh * v/70
    # Y axis: title + numeric ticks
    txt(ax0 - 6, py(70) - 24, "delivered · msg/s", "Sans-B", 9, BROWN, "l", tracking=0.4)
    for v in (0, 30, 60):
        line(ax0 - 4, py(v), ax0, py(v), BROWN_DK, 1.2)
        txt(ax0 - 9, py(v) - 5, str(v), "Sans", 9, TEXT_MUT, "r")
    # ideal
    line(ax0, ay0, px(70), py(70), TAN, 1.4, dash=(4, 3))
    txt(px(74), py(70) - 2, "ideal", "Sans-I", 10, TEXT_MUT, "l")
    rates = [25, 50, 75, 100, 150, 200, 300]
    deliv = [25, 47, 56, 61, 60, 61, 62]
    pts = list(zip([px(r) for r in rates], [py(v) for v in deliv]))
    c.setStrokeColor(HEAVY_C); c.setLineWidth(2.6); c.setLineCap(1); c.setLineJoin(1)
    for i in range(len(pts) - 1):
        c.line(pts[i][0], H-pts[i][1], pts[i+1][0], H-pts[i+1][1])
    for (qx, qy) in pts:
        circle(qx, qy, 3.4, fill=HEAVY_C)
    txt(px(150), py(62) - 16, "delivered", "Sans-B", 10, HEAVY_C, "l")
    circle(px(75), py(56), 9, stroke=BROWN, lw=1.6)
    txt(px(75) - 2, py(56) + 22, "knee", "Sans-B", 10, BROWN, "l")
    # X axis: ticks + title
    for r in (25, 100, 200, 300):
        txt(px(r), ay0 + 8, str(r), "Sans", 9, TEXT_MUT, "c")
    txt(ax0 + axw/2, ay0 + 24, "offered rate · msg/s", "Sans-B", 9, BROWN, "c", tracking=0.4)

    # RIGHT: CPU bars + hero
    txt(540, 186, "CPU CAP REMOVES THE BOTTLENECK", "Sans-B", 10.5, BROWN, "l", tracking=1.3)
    cpu = [("0.05 core", 65, "65% drop"), ("0.10 core", 22, "22% drop"),
           ("0.25 core", 0, "no drop")]
    y = 224; barx = 660; barw = 150
    for cap, drop, lab in cpu:
        txt(540, y + 4, cap, "Mono-B", 12.5, BROWN_DK, "l")
        rect(barx, y, barw, 16, fill=LINE_SOFT)
        if drop:
            rect(barx, y, barw * drop/70, 16, fill=HEAVY_C)
        txt(barx + barw + 12, y + 3, lab, "Sans-B", 11, TEXT_MUT, "l")
        y += 44

    txt(540, 392, "The ceiling is CPU.", "Serif-B", 20, BROWN_DK, "l")
    txt(540, 416, "The crypto design keeps up.", "Serif-I", 18, BROWN, "l")
    txt(96, 452, "Near saturation the pipeline converges; the profile difference shows up in crypto work and policy fit.",
        "Sans-I", 12.5, TEXT_MUT, "l")
    c.showPage()

# ============================================================================
# 12 — Conclusion
# ============================================================================

def s_conclusion():
    bg(BROWN_DK)
    rect(66, 50, 4, 58, fill=TAN)
    txt(84, 54, "CONCLUSION", "Sans-B", 11, TAN, "l", tracking=1.6)
    txt(83, 72, "Adaptive crypto, built and measured", "Serif-B", 27, IVORY, "l")

    items = [("Formalised", "swarm graph + F : S(t) → P"),
             ("Built", "four modes incl. adaptive switching"),
             ("Measured", "lightweight cheapest; adaptive allocates well")]
    cw = 252; gap = 36
    for i, (h, d) in enumerate(items):
        x = 66 + i * (cw + gap)
        ic_check(x + 14, 178, 26, TAN, lw=2.6)
        txt(x + 40, 168, h, "Serif-B", 19, IVORY, "l")
        para(x, 206, cw, d, size=13, color=TAN, leading=18)

    line(66, 280, 894, 280, HexColor("#5C4631"), 1.2)

    txt(84, 304, "WHAT COMES NEXT", "Sans-B", 11, TAN, "l", tracking=1.6)
    fut = [("Authenticated control plane", "signed bootstrap & updates"),
           ("Multi-peer validation", "churn · contention · async"),
           ("Hardware & post-quantum", "real platforms; hybrid PQ")]
    for i, (h, d) in enumerate(fut):
        x = 66 + i * (cw + gap)
        txt(x, 338, f"0{i+1}", "Serif-B", 30, HexColor("#6E5238"), "l")
        txt(x + 52, 342, h, "Serif-B", 15, IVORY, "l")
        para(x + 52, 366, cw - 52, d, size=12, color=TAN, leading=16)

    txt(84, 456, "Thank you — questions welcome.", "Serif-I", 20, IVORY, "l")
    txt(894, 462, "github.com/mazzz3r/adaptive-swarm-crypto-thesis",
        "Sans", 12, TAN, "r")
    c.showPage()

# ============================================================================
# 13 — Limitations & scope  (BACKUP slide for Q&A)
# ============================================================================

def s_limitations():
    bg()
    rect(66, 50, 4, 58, fill=BROWN)
    txt(84, 54, "Q&A · BACKUP", "Sans-B", 11, BROWN, "l", tracking=1.6)
    txt(83, 72, "Limitations & scope", "Serif-B", 27, BROWN_DK, "l")
    txt(894, 508, "backup — not part of the 10-min talk", "Sans-I", 9.5, TEXT_MUT, "r")

    items = [
        ("Pairwise prototype",
         "two peers on the measured path; multi-hop & churn are out of scope"),
        ("Host environment",
         "Docker + gRPC containers; no embedded radios or microcontrollers"),
        ("Energy is a model proxy",
         "valid for relative comparison only, not battery-accurate"),
        ("Scripted inputs",
         "threat & energy are scripted, not sensed or estimated"),
        ("Data plane only",
         "no authenticated control plane (signed bootstrap / updates)"),
        ("Coarse cost metric",
         "crypto-work counts bytes, so heavy ≈ balanced; thresholds set by hand"),
    ]
    cw = 392; gap = 44; rh = 84; top = 168
    for i, (t, d) in enumerate(items):
        col = i % 2; row = i // 2
        x = 66 + col * (cw + gap); y = top + row * rh
        circle(x + 7, y + 13, 5, fill=BROWN)
        txt(x + 26, y + 4, t, "Serif-B", 16, BROWN_DK, "l")
        para(x + 26, y + 30, cw - 26, d, size=12.5, color=TEXT_MUT, leading=17)

    line(66, 446, 894, 446, LINE_SOFT, 1.2)
    para(66, 462, 828,
         "Every claim covers exactly what the constrained pairwise prototype "
         "<b>actually runs</b>.",
         size=14, color=BROWN, font="Sans-I", align=TA_CENTER)
    c.showPage()

# ----------------------------------------------------------------------------
# s_logic (Adaptation logic) is intentionally omitted from the rendered talk;
# the function is kept above so the slide can be re-enabled later if needed.
for fn in (s_title, s_context, s_motivation, s_literature, s_aim, s_model,
           s_security, s_profiles, s_setup, s_results1, s_results2,
           s_conclusion, s_limitations):
    fn()
c.save()
print("wrote", OUT)
