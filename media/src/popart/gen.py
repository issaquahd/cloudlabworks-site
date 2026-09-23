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
