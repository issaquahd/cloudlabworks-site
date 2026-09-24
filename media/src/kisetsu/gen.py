#!/usr/bin/env python3
"""Kisetsu (季節), the seasons set: thirty pieces of Japanese pop art, hand-written SVG.

Same register as media/src/popart: flat colour, heavy ink outline, Ben-day dots, a kanji
stamp, no raster model and no traced photograph. Every leaf, petal and animal below is built
from maths in this file, so the set shares a hand.

Three subjects, which are the three seasons that matter in this vocabulary:
  autumn  twelve Japanese maple cultivars, each a real named Acer with its real colour
  spring  ten flowering cherries, real varieties, from the early Kawazu to the autumn-blooming
          Jugatsu
  winter  eight steam-pool scenes with Japanese macaques

ON THE WINTER SCENES, stated plainly rather than buried: Japanese macaques (Macaca fuscata)
live on Honshu, Shikoku, Kyushu and Yakushima. They are ABSENT FROM HOKKAIDO. Their northern
limit is the Shimokita Peninsula in northern Honshu, and the famous hot-spring troop is at
Jigokudani in NAGANO, central Honshu. The brief asked for Hokkaido; the captions say Nagano
and Shimokita because a public page under a real name should not invent a range map. Hokkaido
gets its own steam without monkeys, at Noboribetsu, which is real.

Palette rule, inherited from the rest of the art section: earth tones first, then one loud
colour set against them.

Run: python3 gen.py  ->  kisetsu-<name>.svg + set.json
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
W = 1024
INK = "#141414"
PAPER = "#f4e8c8"


# ---------- pop-art furniture ----------
def bendot(id_, color, gap=26, r=5, opacity=.85):
    return (f'<pattern id="{id_}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
            f'<circle cx="{gap/2}" cy="{gap/2}" r="{r}" fill="{color}" opacity="{opacity}"/></pattern>')


def stamp(x, y, glyph, ring, ink=PAPER, r=62):
    return (f'<g transform="translate({x} {y})"><circle r="{r}" fill="{ring}"/>'
            f'<text x="0" y="{r*0.34:.0f}" text-anchor="middle" '
            f'font-family="Hiragino Mincho ProN, Noto Serif JP, serif" '
            f'font-size="{r*1.1:.0f}" fill="{ink}">{glyph}</text></g>')


def rays(cx, cy, r1, r2, n, color, opacity=.85):
    out = []
    for i in range(0, n, 2):
        a0 = i * 2 * math.pi / n; a1 = a0 + math.pi / n
        pts = [(cx + r1 * math.cos(a0), cy + r1 * math.sin(a0)),
               (cx + r2 * math.cos(a0), cy + r2 * math.sin(a0)),
               (cx + r2 * math.cos(a1), cy + r2 * math.sin(a1)),
               (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1))]
        d = " ".join(f"{x:.0f} {y:.0f}" for x, y in pts)
        out.append(f'<path d="M{d} Z" fill="{color}" opacity="{opacity}"/>')
    return "".join(out)


# ---------- botany ----------
def maple_leaf(cx, cy, r, rot=0, fill="#c0392b", outline=INK, lobes=5, w=1.0):
    """A palmate Acer leaf.

    First attempt walked a single radius around the leaf with jitter and produced a convex
    star: no sinuses, so it read as an asterisk rather than a maple. A palmatum leaf is
    SEPARATE slender lobes joined near the centre, so the shape has to go all the way OUT to
    the tip and all the way BACK IN to a deep sinus between each pair. The sinus depth is what
    makes it a maple; the serration on the way out is detail nobody sees at thumbnail size.
    """
    span = math.pi * 1.62
    sinus = r * 0.20                         # how far back in between lobes: the whole trick
    pts = []
    for i in range(lobes):
        a = -math.pi / 2 - span / 2 + span * i / (lobes - 1)
        half = (0.34 if i in (0, lobes - 1) else 0.30) * span / (lobes - 1) * w
        # out along one edge, serrated
        for t in (0.30, 0.52, 0.72, 0.88):
            e = a - half * (1 - t) ** 0.65
            rr = r * t * (1.06 if int(t * 10) % 2 else 0.96)
            pts.append((cx + rr * math.cos(e), cy + rr * math.sin(e)))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))          # the tip
        for t in (0.88, 0.72, 0.52, 0.30):
            e = a + half * (1 - t) ** 0.65
            rr = r * t * (1.06 if int(t * 10) % 2 else 0.96)
            pts.append((cx + rr * math.cos(e), cy + rr * math.sin(e)))
        if i < lobes - 1:                                                 # the sinus
            am = a + span / (lobes - 1) / 2
            pts.append((cx + sinus * math.cos(am), cy + sinus * math.sin(am)))
    d = " ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    sw = max(2.0, r * 0.05)
    g = [f'<g transform="rotate({rot} {cx} {cy})">']
    g.append(f'<path d="M{cx:.0f} {cy:.0f} L{cx:.0f} {cy + r*0.80:.0f}" stroke="{outline}" '
             f'stroke-width="{r*0.06:.1f}" fill="none" stroke-linecap="round"/>')
    g.append(f'<path d="M{d} Z" fill="{fill}" stroke="{outline}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>')
    for i in range(lobes):                                                # veins to each tip
        a = -math.pi / 2 - span / 2 + span * i / (lobes - 1)
        g.append(f'<line x1="{cx:.0f}" y1="{cy:.0f}" x2="{cx + r*0.82*math.cos(a):.0f}" '
                 f'y2="{cy + r*0.82*math.sin(a):.0f}" stroke="{outline}" stroke-width="{max(1.2, r*0.018):.1f}" opacity=".45"/>')
    g.append("</g>")
    return "".join(g)


def sakura(cx, cy, r, fill="#f6c7d4", heart="#e0472c", outline=INK, petals=5):
    """Five notched petals and a stamen crown."""
    g = []
    for i in range(petals):
        a = -math.pi / 2 + i * 2 * math.pi / petals
        px, py = cx + r * 0.62 * math.cos(a), cy + r * 0.62 * math.sin(a)
        nx, ny = cx + r * 1.02 * math.cos(a), cy + r * 1.02 * math.sin(a)
        lx, ly = cx + r * 0.72 * math.cos(a - 0.52), cy + r * 0.72 * math.sin(a - 0.52)
        rx, ry = cx + r * 0.72 * math.cos(a + 0.52), cy + r * 0.72 * math.sin(a + 0.52)
        notch = (cx + r * 0.86 * math.cos(a), cy + r * 0.86 * math.sin(a))
        g.append(f'<path d="M{cx:.0f} {cy:.0f} Q{lx:.0f} {ly:.0f} {nx:.0f} {ny:.0f} '
                 f'Q{notch[0]:.0f} {notch[1]:.0f} {px:.0f} {py:.0f} '
                 f'Q{rx:.0f} {ry:.0f} {cx:.0f} {cy:.0f} Z" '
                 f'fill="{fill}" stroke="{outline}" stroke-width="{max(1.6, r*0.05):.1f}" stroke-linejoin="round"/>')
    for i in range(7):
        a = i * 2 * math.pi / 7
        g.append(f'<line x1="{cx:.0f}" y1="{cy:.0f}" x2="{cx + r*0.42*math.cos(a):.0f}" '
                 f'y2="{cy + r*0.42*math.sin(a):.0f}" stroke="{heart}" stroke-width="{max(1.4, r*0.045):.1f}" stroke-linecap="round"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.12:.1f}" fill="{heart}"/>')
    return "".join(g)


def branch(x0, y0, x1, y1, w0, color=INK):
    return (f'<path d="M{x0:.0f} {y0:.0f} Q{(x0+x1)/2:.0f} {(y0+y1)/2 - abs(x1-x0)*0.22:.0f} {x1:.0f} {y1:.0f}" '
            f'stroke="{color}" stroke-width="{w0}" fill="none" stroke-linecap="round"/>')


def macaque(cx, cy, s=1.0, fur="#8a6244", face="#e0472c", outline=INK, submerged=True):
    """A sitting Japanese macaque, shoulders up if submerged. Built to read small and flat."""
    g = []
    r = 46 * s
    if not submerged:
        g.append(f'<ellipse cx="{cx}" cy="{cy + r*1.5:.0f}" rx="{r*1.15:.0f}" ry="{r*1.25:.0f}" '
                 f'fill="{fur}" stroke="{outline}" stroke-width="{4*s:.1f}"/>')
    else:
        g.append(f'<path d="M{cx - r*1.15:.0f} {cy + r*1.1:.0f} q{r*1.15:.0f} {-r*0.7:.0f} {r*2.3:.0f} 0 Z" '
                 f'fill="{fur}" stroke="{outline}" stroke-width="{4*s:.1f}"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.0f}" fill="{fur}" stroke="{outline}" stroke-width="{4.5*s:.1f}"/>')
    for k in (-1, 1):
        g.append(f'<circle cx="{cx + k*r*0.98:.0f}" cy="{cy - r*0.05:.0f}" r="{r*0.3:.0f}" '
                 f'fill="{fur}" stroke="{outline}" stroke-width="{3.5*s:.1f}"/>')
    g.append(f'<ellipse cx="{cx}" cy="{cy + r*0.16:.0f}" rx="{r*0.66:.0f}" ry="{r*0.7:.0f}" '
             f'fill="{face}" stroke="{outline}" stroke-width="{3.5*s:.1f}"/>')
    for k in (-1, 1):
        g.append(f'<ellipse cx="{cx + k*r*0.26:.0f}" cy="{cy + r*0.02:.0f}" rx="{r*0.1:.0f}" ry="{r*0.13:.0f}" fill="{outline}"/>')
    g.append(f'<path d="M{cx - r*0.2:.0f} {cy + r*0.52:.0f} q{r*0.2:.0f} {r*0.16:.0f} {r*0.4:.0f} 0" '
             f'stroke="{outline}" stroke-width="{3*s:.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(g)


def steam(x, y, w, h, color=PAPER, opacity=.55, n=3):
    out = []
    for i in range(n):
        xx = x + i * w / n
        out.append(f'<path d="M{xx:.0f} {y:.0f} q{w*0.16:.0f} {-h*0.3:.0f} 0 {-h*0.55:.0f} '
                   f'q{-w*0.16:.0f} {-h*0.3:.0f} {w*0.05:.0f} {-h*0.45:.0f}" '
                   f'stroke="{color}" stroke-width="{max(6, w*0.05):.0f}" fill="none" '
                   f'opacity="{opacity}" stroke-linecap="round"/>')
    return "".join(out)


def pool(y, color="#4a6b63", rim="#6b4f36"):
    return (f'<path d="M0 {y} Q{W*0.25:.0f} {y-26} {W*0.5:.0f} {y} T{W} {y} L{W} {W} L0 {W} Z" fill="{color}"/>'
            f'<path d="M0 {y} Q{W*0.25:.0f} {y-26} {W*0.5:.0f} {y} T{W} {y}" stroke="{rim}" stroke-width="9" fill="none"/>')


def snowfall(seed, n=90, color=PAPER):
    import random
    rnd = random.Random(seed)
    return "".join(f'<circle cx="{rnd.randrange(W)}" cy="{rnd.randrange(W)}" r="{rnd.choice((3,4,6))}" '
                   f'fill="{color}" opacity="{rnd.choice((.5,.7,.9))}"/>' for _ in range(n))


# ---------- registry ----------
PIECES = []
def piece(name, season, title, text):
    def deco(f): PIECES.append(dict(name=name, season=season, title=title, text=text, draw=f)); return f
    return deco


def plate(bg, body, stampglyph=None, stampring="#e0472c", dots=None):
    """One 1024 square: ground colour, optional Ben-day field, art, optional stamp."""
    s = [f'<rect width="{W}" height="{W}" fill="{bg}"/>']
    if dots:
        s.append(f'<defs>{bendot("bd", dots[0], dots[1], dots[2])}</defs>')
        s.append(f'<rect width="{W}" height="{W}" fill="url(#bd)"/>')
    s.append(body)
    if stampglyph:
        s.append(stamp(W - 108, W - 108, stampglyph, stampring))
    return W, "".join(s)


# ---------- autumn: twelve Acer cultivars, real names and real colour ----------
MAPLES = [
    ("sango-kaku", "Sango-kaku", "珊瑚閣", "#e0472c", "#f2c879", "Coral-bark maple. The winter twigs are the point: the leaves go butter-yellow and fall, and the bare branch turns coral."),
    ("bloodgood", "Bloodgood", "血紅", "#7d1f1f", "#c9a227", "The one everyone plants. Deep burgundy all summer, then scarlet; upright and reliable, which is why it is everywhere."),
    ("osakazuki", "Osakazuki", "大盃", "#c0392b", "#e8dcc4", "Green until it is not. Osakazuki holds plain green through summer and then turns the most violent crimson of any palmatum."),
    ("seiryu", "Seiryu", "青龍", "#4f7a45", "#c9a227", "The only upright laceleaf. Dissected foliage that stays green through the heat and finishes gold with a red edge."),
    ("shishigashira", "Shishigashira", "獅子頭", "#3f6e3a", "#d9a441", "Lion's mane. Crinkled leaves crowded on short internodes, so the whole tree reads as texture before it reads as colour."),
    ("katsura", "Katsura", "桂", "#e08a2c", "#7d8a86", "Spring, not autumn, is its season: new leaves open apricot-orange, fade to green, and come back gold in October."),
    ("beni-kawa", "Beni-kawa", "紅川", "#d4452a", "#f2ebdc", "Red-bark, the redder sibling of Sango-kaku. Same trick, harder colour, and the bark brightens as the temperature drops."),
    ("aconitifolium", "Aconitifolium", "羽団扇", "#b03030", "#6b4f36", "Fernleaf full-moon maple, an Acer japonicum rather than a palmatum. Deeply cut fans that turn every shade of red at once."),
    ("orange-dream", "Orange Dream", "橙夢", "#e08a2c", "#4f7a45", "Opens orange-yellow in spring with a red margin, greens in summer, golds in autumn. Three trees in one year."),
    ("crimson-queen", "Crimson Queen", "紅妃", "#8e2b2b", "#c9a227", "Weeping dissectum. Holds its dark red through summer heat better than most laceleaf forms, which is the whole selling point."),
    ("viridis", "Viridis", "緑滝", "#5b8a4a", "#e0472c", "The green weeping laceleaf. A mound of dissected foliage that goes gold and orange, the counterweight to Crimson Queen."),
    ("higasayama", "Higasayama", "日傘山", "#c9a227", "#e0472c", "Variegated: cream margins on green, flushed pink as the leaf opens. Closest thing in the genus to a printed pattern."),
]

for _i, (_n, _t, _k, _c1, _c2, _tx) in enumerate(MAPLES):
    def _mk(c1=_c1, c2=_c2, k=_k, i=_i):
        def draw():
            body = [rays(W * 0.5, W * 0.42, 60, 900, 24, c2, .22)]
            # one big specimen leaf, then a Warhol-ish row of small repeats
            for j, (lx, ly, lr, rot) in enumerate(((512, 430, 300, 0),)):
                body.append(maple_leaf(lx, ly, lr, rot, c1, INK, lobes=7 if i % 3 == 0 else 5))
            for j in range(5):
                body.append(maple_leaf(108 + j * 168, 872, 72, (j - 2) * 14,   # ends clear of the stamp
                                       c1 if j % 2 == 0 else c2, INK, lobes=5))
            return plate("#e8dcc4", "".join(body), k, c1, dots=(c2, 30, 4))
        return draw
    piece(_n, "Autumn", f"{_t}", _tx)(_mk())


# ---------- spring: ten flowering cherries ----------
CHERRIES = [
    ("somei-yoshino", "Somei-yoshino", "染井吉野", "#f6d7de", "The clone. Nearly every famous avenue in Japan is one genetically identical tree, which is why a city blooms on the same day."),
    ("yamazakura", "Yamazakura", "山桜", "#f2c9cf", "The wild hill cherry: flowers and copper-red young leaves open together, so the tree is never pure white the way Somei-yoshino is."),
    ("shidarezakura", "Shidarezakura", "枝垂桜", "#f0b8c8", "Weeping. The branches carry the flowers down rather than up, and the oldest specimens are propped on timber frames."),
    ("kanzan", "Kanzan", "関山", "#e88aa4", "Double, deep pink, thirty petals or more per flower. Blooms late, after the single whites have gone over."),
    ("ukon", "Ukon", "鬱金", "#dcd7a0", "The yellow-green cherry. Pale chartreuse petals that pink at the base as they age, which reads as a printing error and is not."),
    ("jugatsuzakura", "Jugatsuzakura", "十月桜", "#f6dde3", "Blooms twice: a scatter in October and a fuller show in spring. The autumn flowering is sparse on purpose, not a failure."),
    ("kawazu", "Kawazu-zakura", "河津桜", "#e8749a", "The early one. Deep pink and open in February while everything else is bare, which makes it look impatient."),
    ("fugenzo", "Fugenzo", "普賢象", "#eeaec2", "Named for two leaf-like pistils in the centre said to resemble Fugen's elephant. Double, pink, very late."),
    ("ichiyo", "Ichiyo", "一葉", "#f3c2d2", "Pale double pink with a single leaf-like pistil, hence the name. Opens after Somei-yoshino and holds longer."),
    ("omoigawa", "Omoigawa", "思川", "#f0a8bd", "A modern selection from Tochigi, semi-double and soft pink, and one of the few named cherries younger than the cars under it."),
]

for _i, (_n, _t, _k, _c, _tx) in enumerate(CHERRIES):
    def _mk(c=_c, k=_k, i=_i):
        def draw():
            body = [f'<rect width="{W}" height="{W}" fill="#1a2c29"/>' if i % 3 == 2 else "",
                    rays(W * 0.5, W * 0.5, 40, 820, 20, "#f2ebdc", .12)]
            body.append(branch(-20, 780, 1044, 300 if i % 2 else 520, 26))
            body.append(branch(-20, 940, 700, 640, 16))
            rnd_seed = i * 13 + 7
            import random
            rnd = random.Random(rnd_seed)
            for _ in range(26):
                x = rnd.randrange(40, W - 40); y = rnd.randrange(120, 820)
                body.append(sakura(x, y, rnd.choice((46, 58, 72)), c, "#e0472c"))
            body.append(sakura(300, 300, 150, c, "#e0472c"))
            bg = "#1a2c29" if i % 3 == 2 else "#e8dcc4"
            return plate(bg, "".join(body), k, "#e0472c", dots=("#c9a227", 34, 3) if i % 3 != 2 else None)
        return draw
    piece(_n, "Spring", f"{_t}", _tx)(_mk())


# ---------- winter: eight steam pools ----------
ONSEN = [
    ("jigokudani-troop", "Jigokudani, the troop", "地獄谷", "Nagano", True, 5,
     "Jigokudani Monkey Park, Nagano. The troop that learned to bathe, reportedly from one young female in the early 1960s; the behaviour spread by imitation and is now a tradition."),
    ("jigokudani-one", "Jigokudani, one in the pool", "湯", "Nagano", True, 1,
     "One macaque, shoulders under. Steam is the only white in the frame and the face is the only loud colour."),
    ("jigokudani-snow", "Snow on the shoulders", "雪", "Nagano", True, 3,
     "Snow settles on a wet head and does not melt, because the body below the waterline is warm and the head is not."),
    ("shimokita-limit", "Shimokita, the northern limit", "下北", "Aomori", False, 4,
     "The Shimokita Peninsula in Aomori: the northernmost wild non-human primates on earth, a metre of snow for months, and no hot pool laid on."),
    ("mother-infant", "Mother and infant", "親子", "Nagano", True, 2,
     "An infant rides high and dry. Grooming and bathing are both social, and the pool is a place where rank gets negotiated quietly."),
    ("noboribetsu", "Noboribetsu, Hokkaido", "登別", "Hokkaido", False, 0,
     "Hokkaido steam, drawn honestly: Noboribetsu's own Jigokudani, sulphur vents and no monkeys, because macaques do not live on Hokkaido at all."),
    ("yudanaka-night", "Yudanaka, after dark", "夜湯", "Nagano", True, 3,
     "The valley after the park closes. Lantern light on water, steam going straight up because there is no wind in a gorge."),
    ("thaw", "First thaw", "雪解", "Nagano", True, 2,
     "The end of the set and the end of the season: less steam, more rock, and the troop beginning to sit on the edge rather than in it."),
]

for _i, (_n, _t, _k, _place, _mk_monkeys, _count, _tx) in enumerate(ONSEN):
    def _mkf(k=_k, monkeys=_mk_monkeys, count=_count, i=_i, place=_place):
        def draw():
            night = place == "Nagano" and i in (6,)
            bg = "#16232b" if night else "#dfe6e3"
            body = [f'<rect width="{W}" height="{W}" fill="{bg}"/>']
            body.append(rays(W * 0.5, 180, 40, 760, 18, "#f2c879" if night else "#f2ebdc", .16))
            # rock shelf
            body.append(f'<path d="M0 620 L180 560 L360 600 L540 540 L760 590 L1024 545 L1024 760 L0 760 Z" '
                        f'fill="{"#2f3a36" if night else "#8a7357"}"/>')
            body.append(pool(700, "#2a4a52" if night else "#4a6b63", "#6b4f36"))
            for j in range(count):
                x = 180 + j * (700 // max(1, count)) + (40 if j % 2 else 0)
                body.append(macaque(x, 690 - (26 if j % 2 else 0), 1.0 + (j % 3) * .12,
                                    "#8a6244", "#e0472c", submerged=monkeys))
            body.append(steam(90, 660, 900, 520, "#f2ebdc", .5 if not night else .35, n=6))
            if place == "Hokkaido":
                # no macaques here on purpose, so the vents have to carry the frame instead
                for vx, vr in ((250, 70), (430, 110), (640, 84), (830, 120)):
                    body.append(f'<path d="M{vx-vr} 600 q{vr} -{vr*1.9:.0f} {vr*2} 0 z" fill="#d9a441" opacity=".75"/>')
                    body.append(steam(vx - vr//2, 596, vr*1.6, 460, "#f2ebdc", .6, n=2))
                body.append(f'<path d="M0 596 L200 548 L470 586 L700 536 L1024 580 L1024 640 L0 640 Z" fill="#6b4f36"/>')
            body.append(snowfall(i * 5 + 3, 110 if place != "Hokkaido" else 60))
            return plate(bg, "".join(body), k, "#e0472c")
        return draw
    piece(_n, "Winter", f"{_t}", _tx)(_mkf())


def main():
    out = []
    for p in PIECES:
        size, body = p["draw"]()
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
               f'width="{size}" height="{size}">{body}</svg>')
        open(os.path.join(HERE, f'kisetsu-{p["name"]}.svg'), "w").write(svg)
        out.append({"name": f'kisetsu-{p["name"]}', "season": p["season"], "title": p["title"], "text": p["text"]})
        print(f'{p["season"]:7} {p["name"]}')
    json.dump(out, open(os.path.join(HERE, "set.json"), "w"), indent=1, ensure_ascii=False)
    print(len(PIECES), "pieces")


if __name__ == "__main__":
    main()
