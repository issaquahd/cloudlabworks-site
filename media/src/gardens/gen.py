#!/usr/bin/env python3
"""The garden set: thirty Japanese garden scenes, generated. Portrait 900x1200, flat woodblock layering:
sky, sun or moon, mountain bands in haze, a structure (pagoda, torii, pergola with wisteria, tea house,
stone lantern), a bridge over water, trees built from blossom clusters, rocks, koi, reflections, petals.
Every scene is composed from one seed; the palette (sunset, day, dusk, night, blossom) is the seed's too.
Style references were three garden illustrations Alex sent on 2026-09-21, read and trashed the same
turn; nothing here is traced or copied. Run: python3 gen.py  → garden-NN.svg + set.json
"""
import json, math, os, random
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 900, 1200

PALETTES = {
    "sunset": dict(sky=("#f7a072", "#e8636f", "#6b3a6e"), sun="#fff2c8", far="#c9737f", mid="#8f4b63", near="#4a2f4a", water=("#2f6f7a", "#1f4f5c"), foliage=["#e0455a", "#f27f8f", "#f5a4b6", "#8c2f45"], green="#3f6e4a", ground="#5c3d4a", wood="#b83b2f", stone="#6f6a72", path="#d9c4a5"),
    "day":    dict(sky=("#dff1f7", "#bfe0ee", "#8fbfd6"), sun="#fff7d6", far="#9fbfcf", mid="#6f9a8f", near="#3e6b58", water=("#5fa7b3", "#2f7a86"), foliage=["#f3a7c2", "#f7c6d8", "#e57ea0", "#c74b7a"], green="#4f8a55", ground="#6b7d5a", wood="#b83b2f", stone="#7d8288", path="#e3d5b8"),
    "dusk":   dict(sky=("#f1c6d6", "#c98bb4", "#5f4a8a"), sun="#fdf2d0", far="#8f6f9f", mid="#5f4f7f", near="#3a2f56", water=("#3f5f8f", "#26406a"), foliage=["#b57bd6", "#c9a0e6", "#8e5bb8", "#e493c3"], green="#3f6a5a", ground="#4a4260", wood="#a8522f", stone="#5f5b6f", path="#d3c2c8"),
    "night":  dict(sky=("#1c2a4d", "#122040", "#0a1430"), sun="#f3efd8", far="#2b3d66", mid="#1f2f52", near="#141f3c", water=("#1f3d5c", "#132a44"), foliage=["#d84a6a", "#e88aa0", "#a83358", "#f0b0c0"], green="#2f5a48", ground="#1f2b40", wood="#a83a2a", stone="#4a5060", path="#8e93a8"),
    "blossom": dict(sky=("#fde6ec", "#f8c9d6", "#e9a6bd"), sun="#fffaf0", far="#d9a6bb", mid="#a97a98", near="#6e5470", water=("#79b6c4", "#3f8a9a"), foliage=["#f4a6c0", "#f9cddb", "#ee86ab", "#d95c8d"], green="#5a8f5f", ground="#7a6b6f", wood="#c24a34", stone="#7c7a86", path="#efe0cc"),
}
STRUCTURES = ["pagoda", "torii", "pergola", "teahouse", "lantern"]

def hexmix(a, b, t):
    a = tuple(int(a[i:i+2], 16) for i in (1, 3, 5)); b = tuple(int(b[i:i+2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

class Scene:
    def __init__(self, seed):
        self.r = random.Random(seed); self.seed = seed; self.parts = []; self.defs = []
        self.pal = PALETTES[self.r.choice(list(PALETTES))]
        self.palname = [k for k, v in PALETTES.items() if v is self.pal][0]
        self.structure = self.r.choice(STRUCTURES)
        self.horizon = self.r.randint(520, 640)     # where water begins
        self.moon = self.palname == "night" or (self.palname == "dusk" and self.r.random() < 0.5)
        self.features = []

    def add(self, s): self.parts.append(s)

    # ---- sky, light, mountains ----
    def sky(self):
        a, b, c = self.pal["sky"]
        self.defs.append(f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/><stop offset=".55" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></linearGradient>')
        self.add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
        if self.palname == "night":
            for _ in range(70):
                x, y = self.r.uniform(0, W), self.r.uniform(0, self.horizon * 0.7)
                self.add(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{self.r.uniform(.8, 2):.1f}" fill="#fff" opacity="{self.r.uniform(.3, .9):.2f}"/>')
        cx, cy, rr = self.r.randint(260, 640), self.r.randint(150, 330), self.r.randint(70, 120)
        self.sunpos = (cx, cy, rr)
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{rr * 1.6:.0f}" fill="{self.pal["sun"]}" opacity=".18"/>')
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="{self.pal["sun"]}"/>')
        if self.moon:
            self.add(f'<circle cx="{cx + rr * .35:.0f}" cy="{cy - rr * .25:.0f}" r="{rr * .82:.0f}" fill="{self.pal["sky"][1]}"/>' if self.r.random() < .5 else "")
        # soft cloud bands
        for _ in range(self.r.randint(2, 5)):
            y = self.r.randint(90, self.horizon - 220); w = self.r.randint(180, 520); x = self.r.randint(-60, W - 100)
            self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{self.r.randint(10, 22)}" rx="12" fill="#fff" opacity="{self.r.uniform(.12, .3):.2f}"/>')

    def mountains(self):
        for band, col in ((0, self.pal["far"]), (1, self.pal["mid"]), (2, self.pal["near"])):
            base = self.horizon - 40 + band * 20
            pts = [(-20, base)]; x = -20
            while x < W + 40:
                peak = base - self.r.randint(90 + band * 40, 200 + band * 70)
                x2 = x + self.r.randint(120, 260)
                pts.append(((x + x2) / 2, peak)); x = x2
            pts.append((x, base)); pts.append((W + 40, base)); pts.append((W + 40, H)); pts.append((-20, H))
            d = "M" + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts) + "Z"
            self.add(f'<path d="{d}" fill="{col}" opacity="{.75 + band * .12:.2f}"/>')
        self.add(f'<rect x="0" y="{self.horizon - 60}" width="{W}" height="80" fill="{self.pal["sky"][2]}" opacity=".35"/>')  # haze

    # ---- ground, water, path ----
    def ground(self):
        hz = self.horizon
        self.defs.append(f'<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{self.pal["water"][0]}"/><stop offset="1" stop-color="{self.pal["water"][1]}"/></linearGradient>')
        # banks: left and right ground masses with a pond between them
        self.add(f'<rect x="0" y="{hz}" width="{W}" height="{H - hz}" fill="{self.pal["ground"]}"/>')
        self.add(f'<path d="M{self.r.randint(60, 180)} {hz + 60} C {W * .3:.0f} {hz + 40}, {W * .6:.0f} {hz + 30}, {W - self.r.randint(60, 180)} {hz + 60} C {W + 60} {hz + 300}, {W - 40} {H - 100}, {W * .6:.0f} {H + 20} L {W * .35:.0f} {H + 20} C {-60} {H - 120}, {-20} {hz + 260}, {self.r.randint(60, 180)} {hz + 60} Z" fill="url(#water)"/>')
        # ripple lines
        for _ in range(28):
            y = self.r.randint(hz + 90, H - 40); x = self.r.randint(120, W - 260); w = self.r.randint(40, 180)
            self.add(f'<path d="M{x} {y} q{w / 2:.0f} -6 {w} 0" fill="none" stroke="#fff" stroke-width="2" opacity="{self.r.uniform(.15, .4):.2f}" stroke-linecap="round"/>')
        # a stone path on the left bank
        for i in range(6):
            x, y = 60 + i * 34 + self.r.randint(-8, 8), hz + 120 + i * 90
            self.add(f'<ellipse cx="{x}" cy="{y}" rx="{self.r.randint(22, 34)}" ry="{self.r.randint(10, 16)}" fill="{self.pal["path"]}" opacity=".9"/>')

    # ---- flora ----
    def blossom_tree(self, x, y, size, colours, lean=0.0):
        trunk = self.pal["near"] if self.palname != "night" else "#0d1428"
        # trunk and three branches
        self.add(f'<path d="M{x} {y} q{lean * 20:.0f} -{size * .5:.0f} {lean * 40 + 10:.0f} -{size * 1.1:.0f} M{x + lean * 20:.0f} {y - size * .55:.0f} q-{size * .4:.0f} -{size * .25:.0f} -{size * .7:.0f} -{size * .6:.0f} M{x + lean * 20:.0f} {y - size * .55:.0f} q{size * .45:.0f} -{size * .25:.0f} {size * .75:.0f} -{size * .55:.0f}" fill="none" stroke="{trunk}" stroke-width="{max(6, size * .08):.0f}" stroke-linecap="round"/>')
        cx, cy = x + lean * 30, y - size * 1.0
        for _ in range(int(size * 1.6)):
            a = self.r.uniform(0, math.tau); d = self.r.uniform(0, 1) ** .6 * size * .95
            px, py = cx + math.cos(a) * d * 1.15, cy + math.sin(a) * d * .75
            self.add(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="{self.r.uniform(size * .05, size * .13):.0f}" fill="{self.r.choice(colours)}" opacity="{self.r.uniform(.75, 1):.2f}"/>')

    def pine(self, x, y, size):
        trunk = "#2b1d1a"
        self.add(f'<path d="M{x} {y} q{size * .1:.0f} -{size * .6:.0f} -{size * .1:.0f} -{size * 1.2:.0f}" fill="none" stroke="{trunk}" stroke-width="{max(5, size * .07):.0f}" stroke-linecap="round"/>')
        for i in range(4):
            yy = y - size * (.45 + i * .25); w = size * (.9 - i * .18)
            self.add(f'<path d="M{x - w / 2:.0f} {yy:.0f} q{w / 2:.0f} -{size * .22:.0f} {w:.0f} 0 q-{w / 2:.0f} {size * .12:.0f} -{w:.0f} 0Z" fill="{self.pal["green"]}"/>')

    def wisteria(self, x, y, length, n):
        cols = ["#b58fd8", "#9a6fc4", "#d3b3ec", "#7f55ad"]
        for i in range(n):
            xx = x + i * (length / max(n - 1, 1)); L = self.r.randint(120, 240)
            for k in range(0, L, 9):
                r = 7 * (1 - k / L) + 3
                self.add(f'<circle cx="{xx + math.sin(k / 18) * 5:.0f}" cy="{y + k}" r="{r:.1f}" fill="{self.r.choice(cols)}"/>')

    # ---- structures ----
    def pagoda(self, x, base, w, tiers):
        red, dark = self.pal["wood"], "#3a1f1f"
        h = w * .42
        for t in range(tiers):
            ww = w * (1 - t * .13); y = base - t * h
            self.add(f'<rect x="{x - ww * .3:.0f}" y="{y - h * .6:.0f}" width="{ww * .6:.0f}" height="{h * .6:.0f}" fill="{red}"/>')
            self.add(f'<rect x="{x - ww * .3:.0f}" y="{y - h * .6:.0f}" width="{ww * .6:.0f}" height="{h * .12:.0f}" fill="{dark}" opacity=".5"/>')
            # eave: a wide dark roof with upturned corners, thick enough to read as a roof
            self.add(f'<path d="M{x - ww / 2 - 10:.0f} {y - h * .5:.0f} q10 -18 24 -22 L{x - ww * .2:.0f} {y - h * .98:.0f} L{x + ww * .2:.0f} {y - h * .98:.0f} L{x + ww / 2 - 14:.0f} {y - h * .72:.0f} q14 4 24 22 L{x + ww * .3:.0f} {y - h * .62:.0f} L{x - ww * .3:.0f} {y - h * .62:.0f}Z" fill="{dark}"/>')
            self.add(f'<path d="M{x - ww / 2 - 10:.0f} {y - h * .5:.0f} L{x + ww / 2 + 10:.0f} {y - h * .5:.0f}" stroke="{dark}" stroke-width="6" stroke-linecap="round"/>')
        top = base - tiers * h - h * .5
        self.add(f'<path d="M{x} {top - 60} v60" stroke="{dark}" stroke-width="6"/><circle cx="{x}" cy="{top - 62}" r="9" fill="{dark}"/>')

    def torii(self, x, base, w):
        red = self.pal["wood"]; h = w * 1.1
        self.add(f'<rect x="{x - w * .38:.0f}" y="{base - h:.0f}" width="{w * .07:.0f}" height="{h:.0f}" fill="{red}"/><rect x="{x + w * .31:.0f}" y="{base - h:.0f}" width="{w * .07:.0f}" height="{h:.0f}" fill="{red}"/>')
        self.add(f'<path d="M{x - w * .55:.0f} {base - h - w * .04:.0f} q{w * .55:.0f} -{w * .12:.0f} {w * 1.1:.0f} 0 v{w * .08:.0f} q-{w * .55:.0f} -{w * .1:.0f} -{w * 1.1:.0f} 0Z" fill="{red}"/>')
        self.add(f'<rect x="{x - w * .45:.0f}" y="{base - h + w * .18:.0f}" width="{w * .9:.0f}" height="{w * .07:.0f}" fill="{red}"/>')
        self.add(f'<rect x="{x - w * .04:.0f}" y="{base - h + w * .08:.0f}" width="{w * .08:.0f}" height="{w * .1:.0f}" fill="#2a1a1a"/>')

    def pergola(self, x, base, w):
        wood = "#6f4a2e"
        for i in range(3):
            xx = x - w / 2 + i * w / 2
            self.add(f'<rect x="{xx - 8:.0f}" y="{base - 420}" width="16" height="420" fill="{wood}"/>')
        self.add(f'<rect x="{x - w / 2 - 30:.0f}" y="{base - 430}" width="{w + 60:.0f}" height="14" fill="{wood}"/>')
        for i in range(9):
            self.add(f'<rect x="{x - w / 2 - 20 + i * (w + 40) / 8:.0f}" y="{base - 445}" width="8" height="30" fill="{wood}"/>')
        self.wisteria(x - w / 2 - 10, base - 420, w + 20, 11)

    def teahouse(self, x, base, w):
        wall, roof = "#e9dcc3", "#3a2a2a"; h = w * .5
        self.add(f'<rect x="{x - w / 2:.0f}" y="{base - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{wall}"/>')
        for i in range(4):
            self.add(f'<rect x="{x - w / 2 + 14 + i * (w - 28) / 4:.0f}" y="{base - h + 16:.0f}" width="{(w - 28) / 4 - 10:.0f}" height="{h - 30:.0f}" fill="none" stroke="#5a4636" stroke-width="3"/>')
        self.add(f'<path d="M{x - w * .62:.0f} {base - h + 4:.0f} Q{x:.0f} {base - h - w * .34:.0f} {x + w * .62:.0f} {base - h + 4:.0f}Z" fill="{roof}"/>')

    def lantern(self, x, base, s):
        st = self.pal["stone"]
        self.add(f'<rect x="{x - s * .12:.0f}" y="{base - s * .9:.0f}" width="{s * .24:.0f}" height="{s * .9:.0f}" fill="{st}"/>')
        self.add(f'<rect x="{x - s * .3:.0f}" y="{base - s * 1.25:.0f}" width="{s * .6:.0f}" height="{s * .35:.0f}" rx="4" fill="{st}"/>')
        self.add(f'<rect x="{x - s * .12:.0f}" y="{base - s * 1.2:.0f}" width="{s * .24:.0f}" height="{s * .25:.0f}" fill="#ffe9a8" opacity=".9"/>')
        self.add(f'<path d="M{x - s * .45:.0f} {base - s * 1.25:.0f} Q{x:.0f} {base - s * 1.6:.0f} {x + s * .45:.0f} {base - s * 1.25:.0f}Z" fill="{st}"/>')
        self.add(f'<ellipse cx="{x}" cy="{base:.0f}" rx="{s * .32:.0f}" ry="{s * .08:.0f}" fill="{st}"/>')

    def bridge(self, y, x1, x2, red=True):
        col = self.pal["wood"] if red else "#7a5a3a"; rail = "#3a2222" if red else "#5a4030"
        mid = (x1 + x2) / 2; rise = (x2 - x1) * .28
        self.add(f'<path d="M{x1} {y} Q{mid:.0f} {y - rise:.0f} {x2} {y} v26 Q{mid:.0f} {y - rise + 26:.0f} {x1} {y + 26}Z" fill="{col}"/>')
        self.add(f'<path d="M{x1} {y - 44} Q{mid:.0f} {y - rise - 44:.0f} {x2} {y - 44}" fill="none" stroke="{rail}" stroke-width="7"/>')
        for i in range(9):
            t = i / 8; xx = x1 + (x2 - x1) * t; yy = (1 - t) ** 2 * y + 2 * (1 - t) * t * (y - rise) + t * t * y
            self.add(f'<rect x="{xx - 3:.0f}" y="{yy - 46:.0f}" width="6" height="46" fill="{rail}"/>')
        self.add(f'<path d="M{x1} {y + 26} Q{mid:.0f} {y + rise + 26:.0f} {x2} {y + 26}" fill="{col}" opacity=".35"/>')  # reflection

    def rocks(self, n):
        for _ in range(n):  # on the banks, at the water's edge, never floating mid-pond
            left = self.r.random() < .5
            x = self.r.randint(30, 200) if left else self.r.randint(W - 200, W - 30); y = self.r.randint(self.horizon + 120, H - 40)
            self.add(f'<ellipse cx="{x}" cy="{y}" rx="{self.r.randint(18, 48)}" ry="{self.r.randint(12, 26)}" fill="{self.pal["stone"]}"/>')
            self.add(f'<ellipse cx="{x - 6}" cy="{y - 6}" rx="{self.r.randint(8, 18)}" ry="{self.r.randint(5, 9)}" fill="#fff" opacity=".15"/>')

    def koi(self, n):
        for _ in range(n):
            x, y = self.r.randint(220, W - 260), self.r.randint(self.horizon + 200, H - 60); a = self.r.uniform(-40, 40)
            self.add(f'<g transform="rotate({a:.0f} {x} {y})"><ellipse cx="{x}" cy="{y}" rx="26" ry="9" fill="#f2f2ee"/><ellipse cx="{x + 6}" cy="{y}" rx="12" ry="8" fill="#e8622a"/><path d="M{x - 26} {y} l-12 -7 v14z" fill="#f2f2ee"/></g>')

    def petals(self, n):
        cols = self.pal["foliage"]
        for _ in range(n):
            x, y = self.r.randint(0, W), self.r.randint(0, H)
            self.add(f'<ellipse cx="{x}" cy="{y}" rx="5" ry="3" fill="{self.r.choice(cols)}" opacity=".8" transform="rotate({self.r.randint(0, 180)} {x} {y})"/>')

    def compose(self):
        self.sky(); self.mountains(); self.ground()
        hz = self.horizon; r = self.r
        # structure on the far bank, behind the bridge
        sx = r.randint(230, 670); f = []
        if self.structure == "pagoda": t = r.randint(3, 5); self.pagoda(sx, hz + 20, r.randint(220, 300), t); f.append(f"a {t}-tier pagoda")
        elif self.structure == "torii": self.torii(sx, hz + 24, r.randint(180, 260)); f.append("a torii")
        elif self.structure == "pergola": self.pergola(sx, hz + 30, r.randint(300, 420)); f.append("a wisteria pergola")
        elif self.structure == "teahouse": self.teahouse(sx, hz + 24, r.randint(220, 320)); f.append("a tea house")
        else: self.lantern(sx, hz + 40, r.randint(90, 130)); f.append("a stone lantern")
        # far trees along the horizon
        for _ in range(r.randint(3, 6)):
            x = r.randint(30, W - 30); kind = r.random()
            if kind < .6: self.blossom_tree(x, hz + r.randint(10, 40), r.randint(60, 110), self.pal["foliage"], lean=r.uniform(-.6, .6))
            else: self.pine(x, hz + r.randint(10, 40), r.randint(70, 120))
        # bridge across the pond
        by = hz + r.randint(150, 230); bx1 = r.randint(120, 220); bx2 = W - r.randint(120, 220)
        red = r.random() < .65; self.bridge(by, bx1, bx2, red); f.append("a red bridge" if red else "a wooden bridge")
        self.rocks(r.randint(5, 9))
        if r.random() < .8: k = r.randint(3, 8); self.koi(k); f.append(f"{k} koi")
        # near trees on both banks, big
        big = self.pal["foliage"]
        self.blossom_tree(r.randint(40, 140), hz + r.randint(380, 520), r.randint(150, 230), big, lean=r.uniform(.2, .8))
        self.blossom_tree(W - r.randint(40, 140), hz + r.randint(320, 520), r.randint(140, 220), big, lean=r.uniform(-.8, -.2))
        if r.random() < .5: self.pine(r.randint(600, 860), hz + r.randint(120, 200), r.randint(120, 170)); f.append("a pine")
        if self.structure != "pergola" and r.random() < .35: self.wisteria(r.randint(80, 300), 0, r.randint(200, 420), r.randint(5, 9)); f.append("wisteria")
        self.petals(r.randint(30, 90))
        self.features = f

    def svg(self):
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{"".join(self.defs)}</defs>{"".join(self.parts)}</svg>'

TITLES = {"sunset": "at sunset", "day": "in the afternoon", "dusk": "at dusk", "night": "under the moon", "blossom": "in blossom"}
NAMES = ["Kiyomizu", "Ryōan", "Kenroku", "Kōraku", "Kairaku", "Ginkaku", "Tōfuku", "Heian", "Arashiyama", "Shinjuku", "Rikugi", "Hama-rikyū", "Byōdō", "Daigo", "Nanzen", "Tenryū", "Eikan", "Saihō", "Kinkaku", "Sankei", "Shukkei", "Ritsurin", "Kōko", "Jōju", "Mōtsū", "Kōdai", "Shōren", "Hōkoku", "Ninna", "Tōji"]

def main():
    out = []
    for i in range(30):
        s = Scene(1000 + i * 7919); s.compose()
        name = f"garden-{i + 1:02d}"; open(os.path.join(HERE, name + ".svg"), "w").write(s.svg())
        feats = s.features; text = f"{NAMES[i]} {TITLES[s.palname]}: " + ", ".join(feats[:-1]) + (" and " if len(feats) > 1 else "") + feats[-1] + ". Composed from one seed; the palette is the seed's choice too."
        out.append({"name": name, "title": f"{NAMES[i]}, {TITLES[s.palname]}", "text": text, "palette": s.palname, "structure": s.structure})
        print(name, s.palname, s.structure, feats)
    json.dump(out, open(os.path.join(HERE, "set.json"), "w"), indent=0, ensure_ascii=False)

if __name__ == "__main__": main()
