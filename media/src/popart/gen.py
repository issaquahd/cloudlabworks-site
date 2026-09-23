#!/usr/bin/env python3
"""Waku, pop art: four pieces, Japanese pop-art register (Warhol repetition, Ben-day dots,
ukiyo-e wave and rising-sun motifs, a kanji stamp), built from Waku's own orca silhouette
(the same shape as media/src/agents/agent-waku.svg, recolored). Hand-written SVG, 1024
square except the tetraptych (2048 square), no raster model. Run: python3 gen.py
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
INK = "#141414"


def orca(body, face, fin, eye, cx=512, cy=470, scale=1.0, outline=None):
    """The Waku silhouette (head, dorsal fin, face patch, eye patches, eyes, tail), flat-colored."""
    ol = f' stroke="{outline}" stroke-width="{10/scale:.1f}"' if outline else ""
    g = [f'<g transform="translate({cx} {cy}) scale({scale}) translate(-512 -470)">']
    g.append(f'<path d="M420 700 q92 -60 184 0 q30 100 -92 130 q-122 -30 -92 -130z" fill="{body}"{ol}/>')
    g.append(f'<path d="M470 760 q42 -30 84 0 q0 60 -42 62 q-42 -2 -42 -62z" fill="{face}"/>')
    g.append(f'<path d="M600 780 q60 -20 80 20 q-30 6 -50 -4 q-6 24 -30 26z" fill="{body}"{ol}/>')
    g.append(f'<circle cx="512" cy="470" r="250" fill="{body}"{ol}/>')
    g.append(f'<path d="M512 240 q-40 -110 -20 -160 q70 60 80 160z" fill="{fin}"{ol}/>')
    g.append(f'<path d="M300 520 q60 190 212 190 q152 0 212 -190 q-60 -60 -212 -60 q-152 0 -212 60z" fill="{face}"/>')
    g.append(f'<ellipse cx="392" cy="360" rx="56" ry="70" fill="{face}" transform="rotate(-20 392 360)"/>')
    g.append(f'<ellipse cx="632" cy="360" rx="56" ry="70" fill="{face}" transform="rotate(20 632 360)"/>')
    for x in (402, 622):
        g.append(f'<ellipse cx="{x}" cy="470" rx="62" ry="71" fill="{face}" stroke="{eye[1]}" stroke-width="8"/>')
        g.append(f'<ellipse cx="{x+6}" cy="478" rx="38" ry="48" fill="{eye[0]}"/>')
        g.append(f'<ellipse cx="{x+6}" cy="488" rx="26" ry="31" fill="{eye[1]}"/>')
        g.append(f'<circle cx="{x-10}" cy="454" r="16" fill="{face}"/>')
    g.append("</g>")
    return "".join(g)


def bendot(id_, color, gap=26, r=5, opacity=.85):
    return (f'<pattern id="{id_}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
            f'<circle cx="{gap/2}" cy="{gap/2}" r="{r}" fill="{color}" opacity="{opacity}"/></pattern>')


def kanji_stamp(x, y, glyph, ring, ink, r=70):
    return (f'<g transform="translate({x} {y})"><circle r="{r}" fill="{ring}"/>'
            f'<text x="0" y="{r*0.34:.0f}" text-anchor="middle" font-family="Hiragino Mincho ProN, Noto Serif JP, serif" '
            f'font-size="{r*1.15:.0f}" fill="{ink}">{glyph}</text></g>')


def rays(cx, cy, r1, r2, n, color, opacity=.9):
    import math
    out = []
    for i in range(n):
        a0 = i * 2 * 3.14159265 / n
        a1 = a0 + 3.14159265 / n
        x0, y0 = cx + r1 * math.cos(a0), cy + r1 * math.sin(a0)
        x1, y1 = cx + r2 * math.cos(a0), cy + r2 * math.sin(a0)
        x2, y2 = cx + r2 * math.cos(a1), cy + r2 * math.sin(a1)
        x3, y3 = cx + r1 * math.cos(a1), cy + r1 * math.sin(a1)
        if i % 2 == 0:
            out.append(f'<path d="M{x0:.0f} {y0:.0f} L{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f} L{x3:.0f} {y3:.0f} Z" fill="{color}" opacity="{opacity}"/>')
    return "".join(out)


PIECES = []
def piece(name, title, text):
    def deco(f): PIECES.append(dict(name=name, title=title, text=text, draw=f)); return f
    return deco


@piece("tetraptych", "Waku, four ways",
       "The same orca, four flat palettes, one grid: a straight Warhol repetition, Ben-day "
       "dots standing in for the print screen he never actually ran through.")
def _():
    W = 2048
    quad = W // 2
    palettes = [
        ("#e0472c", "#f4e8c8", "#141414", ("#f2c879", "#141414")),   # red, cream ground, gold eye
        ("#0e7c86", "#f4e8c8", "#141414", ("#e0472c", "#141414")),   # teal, red eye
        ("#141414", "#f2c879", "#f4e8c8", ("#0e7c86", "#f4e8c8")),   # black body, gold face
        ("#c93b8f", "#f4e8c8", "#141414", ("#f2c879", "#141414")),   # magenta
    ]
    grounds = ["#f4e8c8", "#e0472c", "#0e7c86", "#c93b8f"]
    s = [f'<defs>{bendot("bd0", "#141414", 22, 3.4, .18)}{bendot("bd1", "#f4e8c8", 22, 3.4, .22)}</defs>']
    for i, (body, face, fin, eye) in enumerate(palettes):
        cx0, cy0 = (i % 2) * quad, (i // 2) * quad
        gnd = grounds[i]
        s.append(f'<rect x="{cx0}" y="{cy0}" width="{quad}" height="{quad}" fill="{gnd}"/>')
        s.append(f'<rect x="{cx0}" y="{cy0}" width="{quad}" height="{quad}" fill="url(#{"bd0" if gnd != "#141414" else "bd1"})"/>')
        s.append(orca(body, face, fin, eye, cx=cx0 + quad / 2, cy=cy0 + quad / 2 + 40, scale=quad / 1024 * 1.05))
    s.append(f'<rect x="{quad-4}" y="0" width="8" height="{W}" fill="#f4e8c8"/><rect x="0" y="{quad-4}" width="{W}" height="8" fill="#f4e8c8"/>')
    return W, "".join(s)


@piece("rising-sun", "Waku, rising sun",
       "Red and white, radiating: the flag-field treatment, not the flag itself. Kanji stamp "
       "reads \u6ce2, nami \u2014 wave, the thing Waku is named for.")
def _():
    W = 1024
    s = [f'<defs>{bendot("bd2", "#e0472c", 20, 3, .5)}</defs>']
    s.append(f'<rect width="{W}" height="{W}" fill="#f4e8c8"/>')
    s.append(rays(512, 470, 40, 620, 24, "#e0472c", .85))
    s.append(f'<circle cx="512" cy="470" r="620" fill="url(#bd2)"/>')
    s.append(f'<circle cx="512" cy="470" r="300" fill="#e0472c"/>')
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#f2c879", "#141414"), scale=1.15))
    s.append(kanji_stamp(880, 860, "\u6ce2", "#e0472c", "#f4e8c8"))
    return W, "".join(s)


@piece("great-wave", "Waku, the great wave",
       "A hand-drawn homage, not a reproduction: Hokusai's silhouette, simplified to three "
       "flat shapes, indigo and gold, Waku riding the crest instead of a fishing boat.")
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#dce7e4"/>']
    # background swell, three simplified wave bands (homage silhouette, not a copy of the print)
    s.append('<path d="M0 620 q180 -90 340 -20 q160 68 340 -10 q170 -78 344 0 v420 h-1024z" fill="#123a52"/>')
    s.append('<path d="M0 700 q200 -60 400 0 q200 60 400 0 q120 -40 224 -10 v330 h-1024z" fill="#1a4f70" opacity=".9"/>')
    # the great claw-wave, front and left, simplified
    s.append('<path d="M40 560 q40 -220 260 -260 q-90 40 -90 140 q140 -70 220 10 q-150 10 -170 90 '
              'q120 -30 150 40 q-110 10 -130 60 q70 0 80 40 q-160 10 -320 -40 q-90 -30 0 -80z" fill="#0e2e42" stroke="#f4e8c8" stroke-width="6"/>')
    s.append('<path d="M120 480 q30 -60 90 -70 q-10 30 10 50 q-60 10 -60 40z" fill="#f4e8c8"/>')  # foam fleck
    s.append(f'<circle cx="820" cy="200" r="90" fill="#e0472c" opacity=".92"/>')  # sun, Fuji-print style
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#e0472c", "#141414"), cx=690, cy=430, scale=.85))
    s.append(kanji_stamp(120, 890, "\u9be8", "#f4e8c8", "#123a52", r=60))  # 鯨-ish stand-in glyph kept simple
    return W, "".join(s)


@piece("kabuki", "Waku, kabuki paint",
       "Kumadori face-paint stripes borrowed for the mask, not the man: red courage-lines on "
       "black, magenta ground, the Ben-day dot standing in for woodblock grain.")
def _():
    W = 1024
    s = [f'<defs>{bendot("bd3", "#141414", 18, 2.6, .35)}</defs>']
    s.append(f'<rect width="{W}" height="{W}" fill="#c93b8f"/><rect width="{W}" height="{W}" fill="url(#bd3)"/>')
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#e0472c", "#141414"), scale=1.2, outline="#f4e8c8"))
    # kumadori: bold red courage-lines sweeping up from the eyes, black brow-line above, over the white face patch
    s.append('<path d="M300 460 q212 -170 424 0" fill="none" stroke="#e0472c" stroke-width="34" stroke-linecap="round"/>')
    s.append('<path d="M300 460 q212 -170 424 0" fill="none" stroke="#141414" stroke-width="8" stroke-linecap="round" opacity=".5"/>')
    s.append('<path d="M330 560 q182 90 364 0" fill="none" stroke="#e0472c" stroke-width="26" stroke-linecap="round"/>')
    s.append('<path d="M360 630 q152 46 304 0" fill="none" stroke="#141414" stroke-width="14" stroke-linecap="round"/>')
    s.append(kanji_stamp(900, 900, "\u83ef", "#141414", "#f4e8c8", r=64))
    return W, "".join(s)


def seigaiha(id_, r, color, bg, opacity=.9):
    """Wave-scale (seigaiha) field: nested arcs in a tiling rect. Simplified to four nested
    rings per tile rather than the full traditional hand-drawn overlap."""
    arcs = "".join(
        f'<path d="M0 {r:.0f} A{rr:.0f} {rr:.0f} 0 0 1 {2*r:.0f} {r:.0f}" fill="none" '
        f'stroke="{color}" stroke-width="{max(2, r*0.05):.0f}" opacity="{opacity}"/>'
        for rr in (r * .95, r * .7, r * .45, r * .2))
    return (f'<pattern id="{id_}" width="{2*r:.0f}" height="{r:.0f}" patternUnits="userSpaceOnUse">'
            f'<rect width="{2*r:.0f}" height="{r:.0f}" fill="{bg}"/>{arcs}</pattern>')


def asanoha(id_, s, color, bg, opacity=.8):
    """Hemp-leaf (asanoha) field, simplified to one six-line star per tile rather than the
    full interlocking hexagram weave."""
    import math
    cx, cy = s / 2, s * .433
    lines = []
    for i in range(6):
        a = i * math.pi / 3
        x, y = cx + s * .5 * math.cos(a), cy + s * .5 * math.sin(a)
        lines.append(f'<line x1="{cx:.0f}" y1="{cy:.0f}" x2="{x:.0f}" y2="{y:.0f}" '
                     f'stroke="{color}" stroke-width="{max(1, s*.03):.0f}" opacity="{opacity}"/>')
    return (f'<pattern id="{id_}" width="{s:.0f}" height="{s*.866:.0f}" patternUnits="userSpaceOnUse">'
            f'<rect width="{s:.0f}" height="{s*.866:.0f}" fill="{bg}"/>{"".join(lines)}</pattern>')


def ichimatsu(id_, s, c1, c2):
    """Two-tone checkerboard (ichimatsu) field."""
    return (f'<pattern id="{id_}" width="{2*s}" height="{2*s}" patternUnits="userSpaceOnUse">'
            f'<rect width="{2*s}" height="{2*s}" fill="{c1}"/>'
            f'<rect width="{s}" height="{s}" fill="{c2}"/>'
            f'<rect x="{s}" y="{s}" width="{s}" height="{s}" fill="{c2}"/></pattern>')


def dotscreen(id_, color, gap, r, ox=0, oy=0, opacity=.9):
    """One plate of a halftone/newsprint dot screen; offset (ox, oy) lets several plates
    register like offset comic-print color separations."""
    return (f'<pattern id="{id_}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse" '
            f'patternTransform="translate({ox} {oy})">'
            f'<circle cx="{gap/2}" cy="{gap/2}" r="{r}" fill="{color}" opacity="{opacity}"/></pattern>')


def sakura(x, y, r, color, center, rot=0):
    """One simplified five-petal blossom (petals as rotated ellipses, not notched)."""
    g = [f'<g transform="translate({x} {y}) rotate({rot})">']
    for i in range(5):
        g.append(f'<ellipse cx="0" cy="{-r*.6:.0f}" rx="{r*.42:.0f}" ry="{r*.62:.0f}" '
                 f'fill="{color}" transform="rotate({i*72})"/>')
    g.append(f'<circle r="{r*.22:.0f}" fill="{center}"/></g>')
    return "".join(g)


@piece("nine-up", "Waku, nine ways",
       "A 3x3 grid instead of the tetraptych's 2x2: the same Warhol repetition pushed one "
       "step further, nine flat hues cycling warm to cool, newsprint dot screen under each cell.")
def _():
    W = 1536
    cell = W // 3
    hues = ["#e0472c", "#d9a441", "#f2c879", "#0e7c86", "#123a52", "#1f4e8c",
            "#c93b8f", "#6a3b6e", "#141414"]
    grounds = ["#f4e8c8", "#141414"]
    s = [f'<defs>{dotscreen("bd_nu", "#141414", 20, 3, opacity=.16)}</defs>']
    for i, body in enumerate(hues):
        cx0, cy0 = (i % 3) * cell, (i // 3) * cell
        gnd = grounds[i % 2]
        face = "#f4e8c8" if body != "#141414" else "#f2c879"
        s.append(f'<rect x="{cx0}" y="{cy0}" width="{cell}" height="{cell}" fill="{gnd}"/>')
        s.append(f'<rect x="{cx0}" y="{cy0}" width="{cell}" height="{cell}" fill="url(#bd_nu)"/>')
        s.append(orca(body, face, "#141414", ("#f2c879", "#141414"),
                       cx=cx0 + cell / 2, cy=cy0 + cell / 2 + 30, scale=cell / 1024 * 1.05))
    for k in (1, 2):
        s.append(f'<rect x="{cell*k-3}" y="0" width="6" height="{W}" fill="#f4e8c8"/>')
        s.append(f'<rect x="0" y="{cell*k-3}" width="{W}" height="6" fill="#f4e8c8"/>')
    return W, "".join(s)


@piece("strip-four", "Waku, four in a row",
       "A 1x4 strip of vertical bands, not a square grid: four duotone panels, cream line "
       "holding each apart, the repetition read left to right instead of in a block.")
def _():
    W = 2048
    cell = W // 4
    palettes = [("#e0472c", "#f4e8c8"), ("#0e7c86", "#f4e8c8"), ("#d9a441", "#141414"), ("#6a3b6e", "#f4e8c8")]
    s = []
    for i, (gnd, body) in enumerate(palettes):
        cx0 = i * cell
        s.append(f'<rect x="{cx0}" y="0" width="{cell}" height="{W}" fill="{gnd}"/>')
        face = "#141414" if body == "#d9a441" else "#f4e8c8"
        s.append(orca(body, face, body, ("#f2c879", "#141414"), cx=cx0 + cell / 2, cy=W / 2 + 40, scale=cell / 1024 * 1.5))
        if i:
            s.append(f'<rect x="{cx0-3}" y="0" width="6" height="{W}" fill="#f4e8c8"/>')
    return W, "".join(s)


@piece("sixpack", "Waku, six up",
       "A 2x3 grid, six panels: a pastel half-step away from the tetraptych's primaries, "
       "checkerboard ground standing in for the print screen this time instead of dots.")
def _():
    W = 1536
    cols, rows = 2, 3
    cw, ch = W // cols, W // rows
    hues = [("#f2a6c7", "#141414"), ("#a8d8d0", "#141414"), ("#f2c879", "#141414"),
            ("#c9a8e0", "#141414"), ("#a8c4e0", "#141414"), ("#e0472c", "#f4e8c8")]
    s = [f'<defs>{ichimatsu("ic_six", 16, "#f4e8c8", "#ece0c0")}</defs>']
    for i, (body, fin) in enumerate(hues):
        cx0, cy0 = (i % cols) * cw, (i // cols) * ch
        s.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" fill="url(#ic_six)"/>')
        s.append(orca(body, "#f4e8c8", fin, ("#141414", "#f4e8c8"),
                       cx=cx0 + cw / 2, cy=cy0 + ch / 2 + 20, scale=min(cw, ch) / 1024 * 1.1))
    for k in range(1, cols):
        s.append(f'<rect x="{cw*k-3}" y="0" width="6" height="{W}" fill="#141414"/>')
    for k in range(1, rows):
        s.append(f'<rect x="0" y="{ch*k-3}" width="{W}" height="6" fill="#141414"/>')
    return W, "".join(s)


@piece("diptych", "Waku, two ways",
       "One canvas split down the middle, day against night: the smallest repetition grid in "
       "the set, a single hard edge instead of a ruled line between panels.")
def _():
    W = 1024
    s = [f'<rect width="{W//2}" height="{W}" fill="#f2c879"/>',
         f'<rect x="{W//2}" width="{W//2}" height="{W}" fill="#16213e"/>']
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#e0472c", "#141414"), cx=W*.27, cy=W/2+30, scale=.95))
    s.append(orca("#f4e8c8", "#16213e", "#f4e8c8", ("#f2c879", "#141414"), cx=W*.73, cy=W/2+30, scale=.95, outline="#141414"))
    return W, "".join(s)


@piece("tri-panel", "Waku, three ways",
       "A vertical triptych, dawn to dusk: three flat sky tones in sequence rather than a "
       "gradient doing the work, the orca held identically in each panel.")
def _():
    W = 1536
    cw = W // 3
    skies = ["#f2c879", "#e0472c", "#123a52"]
    bodies = [("#141414", "#f4e8c8"), ("#141414", "#f4e8c8"), ("#c9d2d8", "#141414")]
    s = []
    for i, sky in enumerate(skies):
        cx0 = i * cw
        s.append(f'<rect x="{cx0}" y="0" width="{cw}" height="{W}" fill="{sky}"/>')
        body, face = bodies[i]
        s.append(orca(body, face, body, ("#f2c879", "#141414"), cx=cx0 + cw / 2, cy=W / 2 + 40, scale=cw / 1024 * 1.4))
        if i:
            s.append(f'<rect x="{cx0-3}" y="0" width="6" height="{W}" fill="#141414"/>')
    return W, "".join(s)


@piece("pod-formation", "Waku, the pod",
       "Not a grid: one large orca and four small ones in loose formation, the Warhol "
       "repetition broken into a scatter instead of a block, Ben-day dots for water texture."
       )
def _():
    W = 1024
    s = [f'<defs>{bendot("bd_pod", "#0e7c86", 24, 3.4, .3)}</defs>']
    s.append(f'<rect width="{W}" height="{W}" fill="#dce7e4"/><rect width="{W}" height="{W}" fill="url(#bd_pod)"/>')
    small = [(210, 260, .32, 140), (830, 230, .3, -160), (170, 780, .28, 40), (860, 800, .26, -30)]
    for cx0, cy0, sc, rot in small:
        s.append(f'<g transform="rotate({rot} {cx0} {cy0})">' + orca("#123a52", "#f4e8c8", "#123a52", ("#f2c879", "#141414"), cx=cx0, cy=cy0, scale=sc) + '</g>')
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#e0472c", "#141414"), cx=512, cy=520, scale=1.05))
    return W, "".join(s)


@piece("seigaiha-field", "Waku, wave scales",
       "Seigaiha, the nested-arc wave-scale field, behind the orca instead of a plain ground: "
       "four rings per tile, a simplification of the traditional hand-overlapped version.")
def _():
    W = 1024
    s = [f'<defs>{seigaiha("sg1", 64, "#123a52", "#dce7e4", .9)}</defs>']
    s.append(f'<rect width="{W}" height="{W}" fill="url(#sg1)"/>')
    s.append(orca("#e0472c", "#f4e8c8", "#141414", ("#f2c879", "#141414"), scale=1.1, outline="#141414"))
    return W, "".join(s)


@piece("asanoha-field", "Waku, hemp leaf",
       "Asanoha, the hemp-leaf geometric field, worn thin behind the orca: one six-line star "
       "repeated per tile, a simplification of the full interlocking lattice, indigo on gold.")
def _():
    W = 1024
    s = [f'<defs>{asanoha("an1", 90, "#123a52", "#f2c879", .7)}</defs>']
    s.append(f'<rect width="{W}" height="{W}" fill="url(#an1)"/>')
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#e0472c", "#141414"), scale=1.1, outline="#f4e8c8"))
    return W, "".join(s)


@piece("ichimatsu-field", "Waku, checkerboard",
       "Ichimatsu, the two-tone checkerboard, full bleed: the orca in flat red on top of the "
       "field instead of inside a panel of it, the field doing the pop-art repetition instead of a grid of orcas.")
def _():
    W = 1024
    s = [f'<defs>{ichimatsu("ic1", 64, "#141414", "#f4e8c8")}</defs>']
    s.append(f'<rect width="{W}" height="{W}" fill="url(#ic1)"/>')
    s.append(orca("#e0472c", "#f4e8c8", "#e0472c", ("#f2c879", "#141414"), scale=1.15, outline="#141414"))
    return W, "".join(s)


@piece("newsprint", "Waku, newsprint",
       "A halftone dot screen in three offset plates, cyan, magenta, black, like a misregistered "
       "comic print: bolder and coarser than the Ben-day dots used elsewhere in the set.")
def _():
    W = 1024
    s = [f'<defs>{dotscreen("ns_c", "#0e7c86", 30, 9, 0, 0, .55)}'
         f'{dotscreen("ns_m", "#c93b8f", 30, 9, 10, 8, .55)}'
         f'{dotscreen("ns_k", "#141414", 30, 9, -8, 12, .55)}</defs>']
    s.append(f'<rect width="{W}" height="{W}" fill="#f4e8c8"/>')
    s.append(f'<rect width="{W}" height="{W}" fill="url(#ns_c)"/><rect width="{W}" height="{W}" fill="url(#ns_m)"/><rect width="{W}" height="{W}" fill="url(#ns_k)"/>')
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#c93b8f", "#141414"), scale=1.1, outline="#f4e8c8"))
    return W, "".join(s)


@piece("red-fuji", "Waku, red Fuji",
       "A homage to Hokusai's Red Fuji, not a copy: the mountain reduced to one flat red "
       "triangle and a white snow-cap wedge, Waku breaching where the print has only sky.")
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#f2c879"/>']
    s.append('<path d="M120 880 L512 300 L904 880 Z" fill="#e0472c"/>')
    s.append('<path d="M420 470 L512 300 L604 470 Q512 430 420 470 Z" fill="#f4e8c8"/>')
    s.append('<path d="M0 860 h1024 v164 h-1024z" fill="#123a52"/>')
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#f2c879", "#141414"), cx=512, cy=760, scale=.8))
    s.append(kanji_stamp(900, 900, "海", "#141414", "#f4e8c8", r=60))
    return W, "".join(s)


@piece("evening-rain", "Waku, evening rain",
       "A homage to Hiroshige's rain-streak woodblocks, simplified to a field of straight "
       "diagonal lines over a dark indigo ground, the orca surfacing through them."
       )
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#1a4f70"/>']
    for i in range(-4, 30):
        x = i * 42
        s.append(f'<line x1="{x}" y1="-40" x2="{x-220}" y2="{W+40}" stroke="#f4e8c8" stroke-width="3" opacity=".28"/>')
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#e0472c", "#141414"), scale=1.1, outline="#f4e8c8"))
    s.append('<path d="M0 900 q260 -40 512 0 q260 40 512 0 v124 h-1024z" fill="#0e2e42"/>')
    return W, "".join(s)


@piece("villain-paint", "Waku, blue paint",
       "A second kumadori palette: blue and indigo stripes, the color kabuki convention reads "
       "as menace rather than the red courage-lines used for the hero role in the first piece.")
def _():
    W = 1024
    s = [f'<defs>{bendot("bd_vp", "#f4e8c8", 18, 2.6, .25)}</defs>']
    s.append(f'<rect width="{W}" height="{W}" fill="#123a52"/><rect width="{W}" height="{W}" fill="url(#bd_vp)"/>')
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#1f4e8c", "#141414"), scale=1.2, outline="#f4e8c8"))
    s.append('<path d="M300 460 q212 -170 424 0" fill="none" stroke="#1f4e8c" stroke-width="34" stroke-linecap="round"/>')
    s.append('<path d="M330 560 q182 90 364 0" fill="none" stroke="#1f4e8c" stroke-width="26" stroke-linecap="round"/>')
    s.append('<path d="M360 630 q152 46 304 0" fill="none" stroke="#f4e8c8" stroke-width="14" stroke-linecap="round"/>')
    s.append(kanji_stamp(900, 900, "海", "#1f4e8c", "#f4e8c8", r=64))
    return W, "".join(s)


@piece("sorrow-lines", "Waku, sorrow lines",
       "A third kumadori palette: purple, downward-sweeping lines instead of the upward "
       "courage-lines, the convention for grief or nobility rather than heroism or menace.")
def _():
    W = 1024
    s = [f'<defs>{bendot("bd_sl", "#141414", 18, 2.6, .3)}</defs>']
    s.append(f'<rect width="{W}" height="{W}" fill="#c9a8e0"/><rect width="{W}" height="{W}" fill="url(#bd_sl)"/>')
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#6a3b6e", "#141414"), scale=1.2, outline="#f4e8c8"))
    s.append('<path d="M300 420 q212 170 424 0" fill="none" stroke="#6a3b6e" stroke-width="30" stroke-linecap="round"/>')
    s.append('<path d="M340 540 q172 120 344 0" fill="none" stroke="#6a3b6e" stroke-width="20" stroke-linecap="round"/>')
    s.append(kanji_stamp(900, 900, "深", "#6a3b6e", "#f4e8c8", r=64))
    return W, "".join(s)


@piece("sakura-shower", "Waku, cherry blossom",
       "A sakura shower: simplified five-petal blossoms scattered at three sizes over the "
       "orca, the petals rendered as plain ellipses rather than the notched botanical form.")
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#f4e8c8"/>']
    s.append(orca("#141414", "#f2a6c7", "#141414", ("#c93b8f", "#141414"), scale=1.1, outline=None))
    spots = [(120, 140, 46, 10), (860, 120, 40, -20), (200, 860, 34, 50), (900, 800, 44, 0),
             (60, 500, 30, 80), (960, 480, 32, -50), (500, 80, 36, 20), (480, 940, 30, -10),
             (300, 250, 22, 15), (740, 260, 24, -30), (260, 720, 20, 60), (760, 700, 22, -70)]
    for x, y, r, rot in spots:
        s.append(sakura(x, y, r, "#f2a6c7", "#e0472c", rot))
    return W, "".join(s)


@piece("indigo-sun", "Waku, indigo sun",
       "The rising-sun composition again, split-complementary this time: indigo field and "
       "gold rays instead of red and white, the same radiating field-treatment logic."
       )
def _():
    W = 1024
    s = [f'<defs>{bendot("bd_is", "#123a52", 20, 3, .5)}</defs>']
    s.append(f'<rect width="{W}" height="{W}" fill="#f4e8c8"/>')
    s.append(rays(512, 470, 40, 620, 24, "#123a52", .85))
    s.append(f'<circle cx="512" cy="470" r="620" fill="url(#bd_is)"/>')
    s.append(f'<circle cx="512" cy="470" r="300" fill="#123a52"/>')
    s.append(orca("#f2c879", "#f4e8c8", "#f2c879", ("#e0472c", "#141414"), scale=1.15, outline="#141414"))
    s.append(kanji_stamp(880, 860, "海", "#123a52", "#f4e8c8"))
    return W, "".join(s)


@piece("gold-leaf", "Waku, gold leaf",
       "Mostly negative space: one flat gold disc, an ink outline of the orca and nothing "
       "else, the minimal end of the register against the busiest pieces in the set.")
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#f4e8c8"/>']
    s.append(f'<circle cx="512" cy="440" r="330" fill="#f2c879"/>')
    s.append(orca("none", "none", "none", ("#141414", "#141414"), scale=1.1, outline="#141414"))
    return W, "".join(s)


@piece("gold-tide", "Waku, gold tide",
       "A sibling to the gold-leaf piece with one shape added: a single flat indigo wave under "
       "the same ink-line orca, on a gold ground instead of cream."
       )
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#f2c879"/>']
    s.append('<path d="M0 640 q220 -80 400 0 q220 80 440 -10 q100 -20 184 0 v394 h-1024z" fill="#123a52"/>')
    s.append(orca("none", "none", "none", ("#141414", "#141414"), scale=1.1, outline="#141414"))
    return W, "".join(s)


@piece("umi-stamp", "Waku, umi",
       "The kanji stamp enlarged from a corner seal to the whole ground: 海, umi, sea, "
       "filling the field the orca sits on instead of marking a signature in the corner.")
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#0e7c86"/>']
    s.append(f'<text x="512" y="700" text-anchor="middle" font-family="Hiragino Mincho ProN, Noto Serif JP, serif" '
              f'font-size="820" fill="#0a5760" opacity=".55">海</text>')
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#f2c879", "#141414"), scale=1.1, outline="#f4e8c8"))
    return W, "".join(s)


@piece("deep-stamp", "Waku, deep",
       "The same enlarged-glyph treatment as the umi piece, a different word: 深, "
       "deep, dark navy ground standing for the water the orca is under rather than on."
       )
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#16213e"/>']
    s.append(f'<text x="512" y="700" text-anchor="middle" font-family="Hiragino Mincho ProN, Noto Serif JP, serif" '
              f'font-size="820" fill="#0f1830" opacity=".6">深</text>')
    s.append(orca("#c9d2d8", "#16213e", "#c9d2d8", ("#f2c879", "#141414"), scale=1.1, outline="#f4e8c8"))
    return W, "".join(s)


@piece("noren", "Waku, noren",
       "A shop-curtain (noren) treatment: two panels hung from a header bar with a slit "
       "between them, the orca's head passing through the gap as if walking under it.")
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#dce7e4"/>']
    s.append('<rect x="0" y="70" width="1024" height="46" fill="#141414"/>')
    # two flush, straight-edged curtain panels hanging from the header bar, a narrow slit
    # between them for the orca to look through, a small hem-notch at each inner bottom
    # corner instead of tapered torii-style legs
    s.append('<rect x="20" y="116" width="452" height="620" fill="#e0472c"/>')
    s.append('<rect x="552" y="116" width="452" height="620" fill="#e0472c"/>')
    s.append('<path d="M432 696 h40 v40z" fill="#dce7e4"/>')
    s.append('<path d="M592 696 h-40 v40z" fill="#dce7e4"/>')
    s.append(kanji_stamp(246, 400, "波", "#f4e8c8", "#e0472c", r=68))
    s.append(kanji_stamp(778, 400, "海", "#f4e8c8", "#e0472c", r=68))
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#f2c879", "#141414"), cy=560, scale=.9))
    return W, "".join(s)


@piece("inverse-wave", "Waku, the wave, inverted",
       "A literal color inversion of the great wave piece: gold ground, indigo where the "
       "foam was, a straight negative read of the same three flat shapes."
       )
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#f2c879"/>']
    s.append('<path d="M0 620 q180 -90 340 -20 q160 68 340 -10 q170 -78 344 0 v420 h-1024z" fill="#e8c473" opacity=".9"/>')
    s.append('<path d="M0 700 q200 -60 400 0 q200 60 400 0 q120 -40 224 -10 v330 h-1024z" fill="#f0d68f" opacity=".9"/>')
    s.append('<path d="M40 560 q40 -220 260 -260 q-90 40 -90 140 q140 -70 220 10 q-150 10 -170 90 '
              'q120 -30 150 40 q-110 10 -130 60 q70 0 80 40 q-160 10 -320 -40 q-90 -30 0 -80z" fill="#fff6de" stroke="#123a52" stroke-width="6"/>')
    s.append(f'<circle cx="820" cy="200" r="90" fill="#123a52" opacity=".92"/>')
    s.append(orca("#f4e8c8", "#123a52", "#f4e8c8", ("#123a52", "#f4e8c8"), cx=690, cy=430, scale=.85, outline="#123a52"))
    s.append(kanji_stamp(120, 890, "鯨", "#123a52", "#f4e8c8", r=60))
    return W, "".join(s)


@piece("inverse-kabuki", "Waku, kabuki paint, inverted",
       "A literal color inversion of the kabuki piece: cream ground, black courage-lines, "
       "the magenta pushed down to the eye patches instead of filling the field."
       )
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#f4e8c8"/>']
    s.append(orca("#c93b8f", "#141414", "#c93b8f", ("#f4e8c8", "#c93b8f"), scale=1.2, outline="#141414"))
    s.append('<path d="M300 460 q212 -170 424 0" fill="none" stroke="#141414" stroke-width="34" stroke-linecap="round"/>')
    s.append('<path d="M330 560 q182 90 364 0" fill="none" stroke="#141414" stroke-width="26" stroke-linecap="round"/>')
    s.append('<path d="M360 630 q152 46 304 0" fill="none" stroke="#c93b8f" stroke-width="14" stroke-linecap="round"/>')
    s.append(kanji_stamp(900, 900, "華", "#f4e8c8", "#141414", r=64))
    return W, "".join(s)


@piece("moonlit", "Waku, moonlit",
       "The rising-sun field at night: a pale moon instead of a red sun, moonbeam wedges "
       "confined to the upper half instead of a full radiating circle, silver-grey orca."
       )
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#16213e"/>']
    s.append(rays(512, 200, 40, 460, 16, "#3c4a58", .8))
    s.append(f'<circle cx="512" cy="200" r="140" fill="#f0e6a8"/>')
    s.append(orca("#c9d2d8", "#16213e", "#c9d2d8", ("#f0e6a8", "#141414"), cy=560, scale=1.05, outline="#0f1830"))
    return W, "".join(s)


@piece("rough-water", "Waku, rough water",
       "An original storm composition, not a print homage: bold black wave-crests on indigo, "
       "high contrast, the orca breaching through rather than riding a named crest."
       )
def _():
    W = 1024
    s = [f'<rect width="{W}" height="{W}" fill="#1a4f70"/>']
    s.append('<path d="M0 300 q160 -60 320 0 q160 60 320 -10 q160 -50 384 10 v724 h-1024z" fill="#0e2e42"/>')
    s.append('<path d="M0 420 q200 -40 400 10 q200 50 400 -10 q120 -30 224 0 v604 h-1024z" fill="#141414"/>')
    s.append('<path d="M0 380 q100 -60 200 -10" fill="none" stroke="#f4e8c8" stroke-width="10" stroke-linecap="round" opacity=".8"/>')
    s.append('<path d="M600 340 q100 -50 200 0" fill="none" stroke="#f4e8c8" stroke-width="10" stroke-linecap="round" opacity=".8"/>')
    s.append(orca("#e0472c", "#f4e8c8", "#e0472c", ("#f2c879", "#141414"), cy=430, scale=1.15, outline="#f4e8c8"))
    return W, "".join(s)


@piece("horizon-bands", "Waku, horizon bands",
       "A leaping pose against flat horizon bands instead of a sky gradient: five discrete "
       "warm tones stacked like a Rothko field standing in for a sunset."
       )
def _():
    W = 1024
    bands = ["#f2c879", "#e8a25c", "#e0472c", "#c93b8f", "#6a3b6e"]
    h = W // len(bands)
    s = []
    for i, c in enumerate(bands):
        s.append(f'<rect x="0" y="{i*h}" width="{W}" height="{h+2}" fill="{c}"/>')
    s.append(orca("#141414", "#f4e8c8", "#141414", ("#f2c879", "#141414"), scale=1.15, outline="#f4e8c8"))
    return W, "".join(s)


def main():
    out = []
    for p in PIECES:
        size, body = p["draw"]()
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">{body}</svg>'
        open(os.path.join(HERE, f'popart-{p["name"]}.svg'), "w").write(svg)
        out.append({"name": p["name"], "title": p["title"], "text": p["text"]})
        print(p["name"])
    json.dump(out, open(os.path.join(HERE, "set.json"), "w"), indent=0, ensure_ascii=False)


if __name__ == "__main__":
    main()
