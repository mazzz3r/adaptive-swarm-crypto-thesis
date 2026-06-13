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

# ---- fonts -----------------------------------------------------------------
FD = "/usr/share/fonts/truetype"
pdfmetrics.registerFont(TTFont("Serif",   f"{FD}/liberation/LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-B", f"{FD}/liberation/LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-I", f"{FD}/liberation/LiberationSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Sans",    f"{FD}/liberation/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Sans-B",  f"{FD}/liberation/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans-I",  f"{FD}/liberation/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Mono",    f"{FD}/dejavu/DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("Mono-B",  f"{FD}/dejavu/DejaVuSansMono-Bold.ttf"))

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
    line(cx - s*0.00, cy, cx + s*0.46, cy, col, lw)
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

    txt(84, 408, "AUTHOR", "Sans-B", 10, BROWN, "l", tracking=1.4)
    txt(84, 422, "Georgii Butakov", "Serif-B", 18, IVORY, "l")
    txt(360, 408, "SUPERVISOR", "Sans-B", 10, BROWN, "l", tracking=1.4)
    txt(360, 422, "Oleg Bulichev", "Serif-B", 18, IVORY, "l")
    c.showPage()

# ============================================================================
# 02 — Motivation : one big idea + skeleton spectrum
# ============================================================================

def s_motivation():
    bg()
    header("The problem", "No single cipher fits a whole mission", 2)

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
    txt(480, 204, "balance them at runtime, not at design time.",
        "Serif-I", 19, BROWN, "c")
    c.showPage()

# ============================================================================
# 03 — Contributions : three big pillars
# ============================================================================

def s_contrib():
    bg()
    header("This thesis", "Design it formally — then measure it", 3)

    cols = [
        ("01", "MODEL", "Swarm graph + adaptation function",
         "F : S(t) → P", BROWN),
        ("02", "PROTOTYPE", "Pairwise testbed, four modes",
         "incl. adaptive switching", BALANCED_C),
        ("03", "EVIDENCE", "Measured, not just estimated",
         "228 benchmark runs", HEAVY_C),
    ]
    cw = 252; gap = 36; x0 = 66; top = 188
    for i, (n, t, desc, mono, ac) in enumerate(cols):
        x = x0 + i * (cw + gap)
        txt(x, top, n, "Serif-B", 44, TAN, "l")
        line(x, top + 64, x + cw, top + 64, LINE, 1.4)
        txt(x, top + 80, t, "Sans-B", 14, BROWN_DK, "l", tracking=2)
        para(x, top + 108, cw, desc, size=13.5, color=TEXT_MUT, leading=19)
        txt(x, top + 176, mono, "Mono-B", 12, ac, "l")

    txt(W/2, 452, "Novelty: a bounded formal model paired with an executable benchmark.",
        "Serif-I", 15, BROWN, "c")
    c.showPage()

# ============================================================================
# 04 — Formal model : skeleton graph -> F -> P
# ============================================================================

def s_model():
    bg()
    header("Formal model", "The swarm as a dynamic graph", 4)

    # left: skeleton graph
    txt(280, 176, "G ( V, E, t )", "Mono-B", 18, BROWN_DK, "c")
    txt(280, 202, "nodes = agents   ·   edges = live links", "Sans", 12, TEXT_MUT, "c")
    cxg, cyg = 280, 332
    nodes = [(cxg-132, cyg-74), (cxg-18, cyg-92), (cxg+96, cyg-62),
             (cxg+134, cyg+30), (cxg+24, cyg+84), (cxg-96, cyg+68), (cxg-6, cyg-4)]
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            if math.dist(nodes[i], nodes[j]) < 140:
                line(nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1], TAN, 1.4)
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
# 05 — Threat model : attacker vs guarantees, line icons
# ============================================================================

def s_threat():
    bg()
    header("Threat model", "What attackers do — what we guarantee", 5)

    kicker_label(120, 178, "the adversary can", HEAVY_C)
    adv = [(ic_eye, "Eavesdrop", "read traffic"),
           (ic_pen, "Tamper", "inject / modify"),
           (ic_key, "Compromise", "leak keys & memory")]
    for i, (ic, t, d) in enumerate(adv):
        y = 226 + i * 78
        circle(150, y, 26, stroke=LINE, fill=CARD, lw=1.4)
        ic(150, y, 30, HEAVY_C)
        txt(196, y - 14, t, "Serif-B", 17, BROWN_DK, "l")
        txt(196, y + 8, d, "Sans", 13, TEXT_MUT, "l")

    line(480, 196, 480, 452, LINE_SOFT, 1.2)

    kicker_label(540, 178, "the data plane guarantees", GOOD_C)
    gua = [(ic_lock, "Confidentiality", "AEAD, unique nonce"),
           (ic_shield, "Authenticity", "HMAC / hash token"),
           (ic_check, "Integrity & containment", "AEAD tag · epoch rekeying")]
    for i, (ic, t, d) in enumerate(gua):
        y = 226 + i * 78
        circle(570, y, 26, stroke=LINE, fill=CARD, lw=1.4)
        ic(570, y, 30, BROWN)
        txt(616, y - 14, t, "Serif-B", 17, BROWN_DK, "l")
        txt(616, y + 8, d, "Sans", 13, TEXT_MUT, "l")
    c.showPage()

# ============================================================================
# 06 — Building blocks : layered skeleton stack
# ============================================================================

def s_blocks():
    bg()
    header("Building blocks", "One hybrid stack — each primitive where it fits", 6)

    layers = [
        ("SESSION SETUP", "X25519  +  HKDF-SHA256",
         "ephemeral key exchange per epoch → forward secrecy", "periodic", BROWN_DK),
        ("PAYLOAD", "AES-GCM / ChaCha20-Poly1305",
         "AEAD confidentiality + integrity", "per message", BALANCED_C),
        ("RUNTIME AUTH", "HMAC-SHA256 / hash token",
         "lightweight origin & replay check", "per message", TAN),
    ]
    x, w = 110, 600
    top = 196; hh = 78; gap = 22
    for i, (cap, prim, desc, freq, ac) in enumerate(layers):
        y = top + i * (hh + gap)
        rrect(x, y, w, hh, stroke=LINE, fill=CARD, r=12)
        rect(x, y, 5, hh, fill=ac)
        txt(x + 26, y + 16, cap, "Sans-B", 10.5, BROWN, "l", tracking=1.8)
        txt(x + 26, y + 32, prim, "Mono-B", 18, BROWN_DK, "l")
        txt(x + 26, y + 58, desc, "Sans", 12.5, TEXT_MUT, "l")
        chip(x + w - 132, y + 25, 108, 28, freq, IVORY_2, BROWN, 10.5, "Sans-B", r=14)
        if i < 2:
            line(x + w/2, y + hh, x + w/2, y + hh + gap, TAN, 1.4)
            poly([(x + w/2 - 5, y + hh + gap - 7), (x + w/2 + 5, y + hh + gap - 7),
                  (x + w/2, y + hh + gap - 1)], fill=TAN)

    # side note
    txt(742, 240, "WHY HYBRID", "Sans-B", 10.5, BROWN, "l", tracking=1.6)
    para(742, 266, 152,
         "Costly asymmetric work stays <b>off</b> the per-packet path.",
         size=13, color=TEXT_MUT, leading=20)
    c.showPage()

# ============================================================================
# 07 — Profiles : three columns, hero crypto-work numbers
# ============================================================================

def s_profiles():
    bg()
    header("Profiles", "Three operating points", 7)

    profs = [
        ("HEAVY", HEAVY_C, IVORY, "AES-256-GCM", "+ HMAC-SHA256", "0.250", "max protection"),
        ("BALANCED", BALANCED_C, IVORY, "AES-192-GCM", "+ HMAC-SHA256", "0.250", "mixed conditions"),
        ("LIGHTWEIGHT", LIGHT_C, BROWN_DK, "ChaCha20-Poly1305", "+ hash token", "0.125", "efficiency first"),
    ]
    cw = 268; gap = 14; x0 = 66; top = 178; hh = 250
    for i, (name, ac, fg, p1, p2, val, tag) in enumerate(profs):
        x = x0 + i * (cw + gap)
        rrect(x, top, cw, hh, stroke=LINE, fill=CARD, r=14)
        rect(x, top, cw, 6, fill=ac)
        chip(x + 22, top + 26, 110, 26, name, ac, fg, 11, "Sans-B", r=13)
        txt(x + 24, top + 70, p1, "Mono-B", 14.5, BROWN_DK, "l")
        txt(x + 24, top + 92, p2, "Mono", 12.5, TEXT_MUT, "l")
        line(x + 24, top + 126, x + cw - 24, top + 126, LINE_SOFT, 1.2)
        txt(x + 24, top + 142, val, "Serif-B", 50, ac if ac != LIGHT_C else BROWN_DK, "l")
        txt(x + 150, top + 168, "MiB", "Sans", 13, TEXT_MUT, "l")
        txt(x + 24, top + 206, "crypto work / message", "Sans-B", 10.5, TEXT_MUT, "l", tracking=1)

    txt(W/2, 452, "Lightweight does half the per-message crypto work of the authenticated profiles.",
        "Serif-I", 15, BROWN, "c")
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
        txt(px, py + 20, name, "Mono-B", 12, BROWN_DK, "c")
    line(320, py, 580, py, TAN, 2)
    poly([(580, py - 5), (580, py + 5), (588, py)], fill=TAN)
    chip(398, py - 17, 104, 34, "gRPC", IVORY_2, BROWN, 12, "Mono-B", r=16)
    txt(450, py + 52, "two containers · encrypted data path", "Sans-I", 12, TEXT_MUT, "c")

    # hero constraint stats
    line(96, 300, 864, 300, LINE_SOFT, 1.2)
    stats = [("0.05", "CPU CORES"), ("128", "MiB RAM"),
             ("64", "KiB / MSG"), ("60", "SECONDS"), ("×3", "REPEATS")]
    n = len(stats); slot = 768 / n
    for i, (v, l) in enumerate(stats):
        cx = 96 + slot * i + slot/2
        txt(cx, 330, v, "Serif-B", 46, BROWN_DK, "c")
        txt(cx, 388, l, "Sans-B", 10.5, TEXT_MUT, "c", tracking=1.4)

    txt(W/2, 446, "Measured: latency · throughput · drops · switches · crypto work",
        "Sans", 13, TEXT_MUT, "c")
    c.showPage()

# ============================================================================
# 10 — Results I : crypto work bars + policy fit
# ============================================================================

def s_results1():
    bg()
    header("Results · I", "Adaptive spends protection where it is needed", 10)

    # LEFT: crypto work bars (frameless)
    txt(96, 186, "CRYPTO WORK / MESSAGE", "Sans-B", 10.5, BROWN, "l", tracking=1.6)
    txt(96, 202, "MiB · lower is cheaper", "Sans-I", 11, TEXT_MUT, "l")
    bars = [("Heavy", 0.250, HEAVY_C), ("Balanced", 0.250, BALANCED_C),
            ("Adaptive", 0.224, BROWN), ("Lightweight", 0.125, LIGHT_C)]
    base = 408; maxh = 150; bw = 66; gapb = 30; x0 = 110; amax = 0.27
    for i, (nm, v, col) in enumerate(bars):
        x = x0 + i * (bw + gapb)
        bh = maxh * v / amax
        rrect(x, base - bh, bw, bh, fill=col, r=4)
        txt(x + bw/2, base - bh - 20, f"{v:.3f}", "Serif-B", 15, BROWN_DK, "c")
        txt(x + bw/2, base + 8, nm, "Sans", 10.5, TEXT_MUT, "c")
    line(96, base, 470, base, LINE, 1.4)

    # RIGHT: policy fit stacked bars
    txt(540, 186, "POLICY FIT OVER THE 60-s SCHEDULE", "Sans-B", 10.5, BROWN, "l", tracking=1.4)
    txt(540, 202, "share of time at the right protection level", "Sans-I", 11, TEXT_MUT, "l")
    rows = [("Adaptive", 100, 0, 0), ("Always heavy", 40, 60, 0),
            ("Always balanced", 60, 0, 40), ("Always light", 20, 0, 80)]
    MATCH, OVER, UNDER = GOOD_C, TAN, HEAVY_C
    bx = 660; bw2 = 234; y = 230
    for nm, m, o, u in rows:
        txt(540, y + 5, nm, "Sans", 12, BROWN_DK, "l")
        xoff = bx
        for val, col in [(m, MATCH), (o, OVER), (u, UNDER)]:
            if val:
                rect(xoff, y, bw2 * val/100, 20, fill=col); xoff += bw2*val/100
        y += 40
    # legend
    lx = 660
    for nm, col in [("matched", MATCH), ("over", OVER), ("under", UNDER)]:
        rrect(lx, 396, 11, 11, fill=col, r=2)
        txt(lx + 16, 396, nm, "Sans", 10, TEXT_MUT, "l")
        lx += 30 + len(nm) * 6

    # hero takeaway — lead with the definitional (hard-to-contest) claim
    txt(540, 422, "100%", "Serif-B", 34, BROWN_DK, "l")
    txt(642, 418, "of the run at the right level", "Sans-B", 13, BROWN_DK, "l")
    txt(642, 440, "−26.7% tier-work vs. always-heavy", "Sans", 11.5, TEXT_MUT, "l")
    c.showPage()

# ============================================================================
# 11 — Results II : saturation curve + CPU bars
# ============================================================================

def s_results2():
    bg()
    header("Results · II", "Under a tight CPU cap, transport dominates", 11)

    # LEFT: delivered vs offered
    txt(96, 186, "DELIVERED vs OFFERED RATE", "Sans-B", 10.5, BROWN, "l", tracking=1.6)
    txt(96, 202, "0.05-core cap · msg/s", "Sans-I", 11, TEXT_MUT, "l")
    ax0, ay0, axw, axh = 130, 410, 330, 160
    line(ax0, ay0, ax0 + axw, ay0, BROWN_DK, 1.4)
    line(ax0, ay0, ax0, ay0 - axh, BROWN_DK, 1.4)
    def px(r): return ax0 + axw * r/300
    def py(v): return ay0 - axh * v/70
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
    for r in (25, 100, 200, 300):
        txt(px(r), ay0 + 8, str(r), "Sans", 9, TEXT_MUT, "c")

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

    txt(540, 392, "It's CPU-bound,", "Serif-B", 20, BROWN_DK, "l")
    txt(540, 416, "not a crypto-design limit.", "Serif-I", 18, BROWN, "l")
    txt(96, 452, "Near saturation the whole pipeline converges — the profile gap shows in crypto work, not latency.",
        "Sans-I", 12.5, TEXT_MUT, "l")
    c.showPage()

# ============================================================================
# 12 — Conclusion
# ============================================================================

def s_conclusion():
    bg(BROWN_DK)
    rect(66, 50, 4, 58, fill=TAN)
    txt(84, 54, "CONCLUSION", "Sans-B", 11, TAN, "l", tracking=1.6)
    txt(83, 72, "Adaptive crypto — measured, not just proposed", "Serif-B", 27, IVORY, "l")

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
        ("Pairwise, not a swarm",
         "two peers on the measured path; multi-hop & churn are out of scope"),
        ("Host, not hardware",
         "Docker + gRPC containers — no embedded radios or microcontrollers"),
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
         "Every claim is scoped to a constrained pairwise prototype — "
         "<b>validated, not extrapolated</b>.",
         size=14, color=BROWN, font="Sans-I", align=TA_CENTER)
    c.showPage()

# ----------------------------------------------------------------------------
for fn in (s_title, s_motivation, s_contrib, s_model, s_threat, s_blocks,
           s_profiles, s_logic, s_setup, s_results1, s_results2, s_conclusion,
           s_limitations):
    fn()
c.save()
print("wrote", OUT)
