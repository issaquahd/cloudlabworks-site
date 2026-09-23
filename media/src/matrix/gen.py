#!/Users/rebl/.local/share/imgtools/bin/python
"""The Matrix set: Kyoto and Tokyo scenes as digital rain. Twenty to start.

Each scene is painted first as a light map (a 3:4 canvas of greys: sky, moon, hills, roofs, lit
windows, water) with a red channel marking the one warm thing (a torii, a lantern, a tower's
lights). The map is then read cell by cell and every cell becomes a katakana or digit whose
brightness is the light under it; rain columns fall through the frame with white heads. Nothing
is traced from a photograph; every shape is drawn here in code from a seed, so the set shares a
hand and no scene repeats. Run: gen.py [outdir]  → matrix-NN.png + set.json
"""
import os, sys, json, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
W, H = 1200, 1600           # light map, 3:4
CELL = 10                   # glyph cell → 120 × 160 glyphs
FONT = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
KATA = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789Z:・"

# ---------- light-map primitives (grey = light; red channel = the warm accent) ----------
def canvas(): return Image.new("RGB", (W, H), (0, 0, 0))
def sky(im, top=18, bottom=60, horizon=0.62):
    d = ImageDraw.Draw(im); hy = int(H * horizon)
    for y in range(hy):
        v = int(top + (bottom - top) * (y / hy)); d.line([(0, y), (W, y)], fill=(0, v, 0))
def moon(im, cx, cy, r, v=235):
    from PIL import ImageChops
    glow = Image.new("RGB", (W, H), (0, 0, 0)); ImageDraw.Draw(glow).ellipse([cx - r * 2.2, cy - r * 2.2, cx + r * 2.2, cy + r * 2.2], fill=(0, 70, 0))
    im.paste(ImageChops.add(im, glow.filter(ImageFilter.GaussianBlur(60))), (0, 0))
    ImageDraw.Draw(im).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, v, 0))
def hills(im, y0, amp, v, seed, n=6):
    rnd = random.Random(seed); d = ImageDraw.Draw(im)
    pts = [(0, H)]; x = 0
    while x <= W:
        pts.append((x, y0 + rnd.uniform(-amp, amp) * math.sin(x / rnd.uniform(90, 220) + rnd.random() * 3))); x += 40
    pts += [(W, H)]; d.polygon(pts, fill=(0, v, 0))
def ground(im, y0, v): ImageDraw.Draw(im).rectangle([0, y0, W, H], fill=(0, v, 0))
def water(im, y0, v=28):
    d = ImageDraw.Draw(im); d.rectangle([0, y0, W, H], fill=(0, v, 0))
    # reflection: the band above the water, flipped and dimmed, with ripple offsets
    band = im.crop((0, max(0, y0 - (H - y0)), W, y0)).transpose(Image.FLIP_TOP_BOTTOM).point(lambda p: int(p * 0.45))
    rip = Image.new("RGB", band.size); rnd = random.Random(y0)
    for y in range(band.height):
        off = int(6 * math.sin(y / 9.0) + rnd.uniform(-2, 2)); rip.paste(band.crop((0, y, W, y + 1)), (off, y))
    im.paste(rip, (0, y0))
def rect(im, x0, y0, x1, y1, v, red=0): ImageDraw.Draw(im).rectangle([x0, y0, x1, y1], fill=(red, v, 0))
def poly(im, pts, v, red=0): ImageDraw.Draw(im).polygon(pts, fill=(red, v, 0))
def windows(im, x0, y0, x1, y1, seed, pitch=(22, 30), lit=0.55, v=(120, 235), red=0):
    rnd = random.Random(seed); d = ImageDraw.Draw(im)
    for y in range(y0 + 10, y1 - 10, pitch[1]):
        for x in range(x0 + 8, x1 - 12, pitch[0]):
            if rnd.random() < lit: d.rectangle([x, y, x + pitch[0] - 12, y + pitch[1] - 16], fill=(red, rnd.randint(*v), 0))
def tower_block(im, x, w, top, v, seed, lit=0.5, red=0):
    rect(im, x, top, x + w, H, v); windows(im, x, top, x + w, int(H * 0.72), seed, lit=lit, red=red)
def roof(im, cx, y, half, rise, v, curl=0.35):
    # a temple roof: a shallow curve, eaves lifting at the ends
    pts = [(cx - half, y)] + [(cx - half + i * (2 * half) / 24, y - rise * (1 - abs(i - 12) / 12) ** 0.7 + curl * rise * (abs(i - 12) / 12) ** 3) for i in range(25)] + [(cx + half, y), (cx + half * 0.82, y + rise * 0.55), (cx - half * 0.82, y + rise * 0.55)]
    poly(im, pts, v)
def pagoda(im, cx, base_y, tiers, width, v=150, roof_v=200):
    y = base_y; w = width
    for t in range(tiers):
        rect(im, cx - w * 0.36, y - 70, cx + w * 0.36, y, v)
        roof(im, cx, y - 70, w * 0.55, 34, roof_v)
        y -= 110; w *= 0.86
    poly(im, [(cx - 8, y - 40), (cx + 8, y - 40), (cx + 3, y - 150), (cx - 3, y - 150)], roof_v)
def torii(im, cx, base_y, scale=1.0, red=200, v=110):
    s = scale; d = ImageDraw.Draw(im)
    d.rectangle([cx - 90 * s, base_y - 220 * s, cx - 74 * s, base_y], fill=(red, v, 0)); d.rectangle([cx + 74 * s, base_y - 220 * s, cx + 90 * s, base_y], fill=(red, v, 0))
    poly(im, [(cx - 130 * s, base_y - 236 * s), (cx + 130 * s, base_y - 236 * s), (cx + 136 * s, base_y - 216 * s), (cx - 136 * s, base_y - 216 * s)], v, red)
    d.rectangle([cx - 104 * s, base_y - 186 * s, cx + 104 * s, base_y - 174 * s], fill=(red, v, 0))
def lantern(im, cx, cy, r=22, red=230, v=200):
    d = ImageDraw.Draw(im); d.ellipse([cx - r, cy - r * 1.3, cx + r, cy + r * 1.3], fill=(red, v, 0)); d.line([(cx, cy - r * 1.3 - 30), (cx, cy - r * 1.3)], fill=(0, 90, 0), width=3)
def bamboo(im, x, top, v, seed):
    rnd = random.Random(seed); d = ImageDraw.Draw(im); w = rnd.randint(10, 18)
    d.rectangle([x, top, x + w, H], fill=(0, v, 0))
    for y in range(top + rnd.randint(40, 120), H, rnd.randint(110, 170)): d.rectangle([x - 2, y, x + w + 2, y + 6], fill=(0, min(255, v + 60), 0))
def tree(im, cx, base, r, v, seed, blossom=False):
    rnd = random.Random(seed); d = ImageDraw.Draw(im)
    d.rectangle([cx - 6, base - r, cx + 6, base], fill=(0, 60, 0))
    for _ in range(9):
        ox, oy, rr = rnd.uniform(-r * 0.8, r * 0.8), rnd.uniform(-r * 1.6, -r * 0.4), rnd.uniform(r * 0.4, r * 0.8)
        d.ellipse([cx + ox - rr, base + oy - rr, cx + ox + rr, base + oy + rr], fill=(55 if blossom else 0, v, 0))
def bridge_arc(im, x0, x1, y, rise, v=170, thick=22):
    d = ImageDraw.Draw(im); pts = [(x0 + (x1 - x0) * i / 40, y - rise * math.sin(math.pi * i / 40)) for i in range(41)]
    d.line(pts, fill=(0, v, 0), width=thick)
    for i in range(0, 41, 5): d.line([(pts[i][0], pts[i][1] - 40), pts[i]], fill=(0, v, 0), width=6)
def rain_lines(im, seed, n=900, v=40):
    rnd = random.Random(seed); d = ImageDraw.Draw(im)
    for _ in range(n):
        x = rnd.randint(0, W); y = rnd.randint(0, H); l = rnd.randint(20, 70); d.line([(x, y), (x - 6, y + l)], fill=(0, v, 0), width=1)
def sign(im, x, y, w, h, v, seed, red=0):
    rect(im, x, y, x + w, y + h, v, red); rnd = random.Random(seed); d = ImageDraw.Draw(im)
    for i in range(rnd.randint(2, 5)): d.rectangle([x + 8, y + 8 + i * (h // 5), x + w - 8, y + 8 + i * (h // 5) + h // 9], fill=(0, 30, 0))
def stars(im, seed, n=140):
    rnd = random.Random(seed); d = ImageDraw.Draw(im)
    for _ in range(n): x, y = rnd.randint(0, W), rnd.randint(0, int(H * 0.5)); d.point((x, y), fill=(0, rnd.randint(120, 220), 0))

# ---------- scenes ----------
S = []
def scene(name, city, title, text):
    def deco(f): S.append((name, city, title, text, f)); return f
    return deco

@scene("kyoto-fushimi", "Kyoto", "Fushimi Inari, the tunnel", "The thousand gates of Fushimi Inari, receding uphill. The one warm thing in the frame is vermilion, repeated until it becomes a corridor.")
def _(im):
    sky(im, 6, 20, 0.45); ground(im, int(H * 0.45), 34)
    hz = int(H * 0.45)
    for i in range(16, -1, -1):
        t = i / 16; s_ = 0.3 + (1 - t) ** 1.6 * 2.2; base = hz + 90 + int((1 - t) ** 1.6 * (H - hz - 130))
        torii(im, W // 2, base, s_, red=200 + int(40 * (1 - t)), v=150 + int(90 * (1 - t)))
    poly(im, [(W // 2 - 40, hz + 80), (W // 2 + 40, hz + 80), (W // 2 + 200, H), (W // 2 - 200, H)], 80)

@scene("kyoto-kinkaku", "Kyoto", "Kinkaku-ji, on the pond", "The golden pavilion and its reflection: two storeys of light over a black pond, a pine leaning in from the left.")
def _(im):
    sky(im, 12, 40, 0.6); hills(im, int(H * 0.44), 60, 22, 2); stars(im, 2)
    cx = 640; base = int(H * 0.6)
    rect(im, cx - 220, base - 90, cx + 220, base, 90); roof(im, cx, base - 90, 260, 30, 130)
    rect(im, cx - 180, base - 190, cx + 180, base - 100, 225); windows(im, cx - 180, base - 190, cx + 180, base - 100, 3, pitch=(40, 40), lit=0.9, v=(40, 60))
    roof(im, cx, base - 190, 230, 34, 245); rect(im, cx - 140, base - 290, cx + 140, base - 200, 235); roof(im, cx, base - 290, 190, 36, 250)
    tree(im, 160, base, 120, 90, 3); water(im, base + 4)

@scene("kyoto-kiyomizu", "Kyoto", "Kiyomizu, the stage", "The wooden stage of Kiyomizu-dera on its lattice of pillars, the hillside falling away below, the city as a spill of small lights.")
def _(im):
    sky(im, 14, 50, 0.55); moon(im, 980, 220, 60); hills(im, int(H * 0.5), 80, 30, 5)
    base = int(H * 0.62); rect(im, 120, base - 30, 880, base, 160); roof(im, 500, base - 190, 420, 50, 190); rect(im, 180, base - 160, 820, base - 30, 120)
    windows(im, 180, base - 160, 820, base - 30, 6, pitch=(36, 44), lit=0.35, v=(200, 250))
    d = ImageDraw.Draw(im)
    for x in range(140, 880, 60):
        d.line([(x, base), (x - 20, H)], fill=(0, 140, 0), width=10)
        for y in range(base + 80, H, 120): d.line([(x - 30, y), (x + 30, y)], fill=(0, 120, 0), width=8)
    windows(im, 0, int(H * 0.72), W, H, 7, pitch=(50, 60), lit=0.15, v=(140, 220))

@scene("kyoto-arashiyama", "Kyoto", "Arashiyama, the bamboo", "The bamboo grove at Arashiyama: culms taller than the frame, the light coming down between them in bars.")
def _(im):
    sky(im, 6, 30, 0.35); rnd = random.Random(8)
    for x in sorted(rnd.sample(range(-20, W, 6), 60)): bamboo(im, x, rnd.randint(-100, 200), rnd.randint(90, 230), x)
    ground(im, int(H * 0.86), 40); rect(im, 460, int(H * 0.86), 740, H, 110)

@scene("kyoto-gion", "Kyoto", "Gion, the lantern lane", "A machiya street in Gion after dark: lattice fronts, tiled eaves, and a row of paper lanterns doing the work of the moon.")
def _(im):
    sky(im, 8, 24, 0.45); rect(im, 0, int(H * 0.7), W, H, 60)
    for i, x in enumerate(range(0, W, 200)):
        rect(im, x, int(H * 0.4) - i % 2 * 30, x + 190, int(H * 0.7), 45); roof(im, x + 95, int(H * 0.4) - i % 2 * 30, 105, 26, 170)
        windows(im, x, int(H * 0.45), x + 190, int(H * 0.7), 10 + i, pitch=(14, 60), lit=0.8, v=(150, 220))
        lantern(im, x + 95, int(H * 0.5) + 20, 24)
    for i in range(6): lantern(im, 120 + i * 190, int(H * 0.62), 16, red=200, v=180)

@scene("kyoto-togetsukyo", "Kyoto", "Togetsukyō, the moon bridge", "The long bridge at Arashiyama over the Katsura, the hills behind it, and the moon it is named for.")
def _(im):
    sky(im, 12, 44, 0.55); moon(im, 300, 240, 70); hills(im, int(H * 0.5), 90, 34, 11); hills(im, int(H * 0.56), 50, 26, 12)
    y = int(H * 0.64); ImageDraw.Draw(im).line([(0, y), (W, y)], fill=(0, 210, 0), width=34)
    for x in range(40, W, 90): rect(im, x - 12, y, x + 12, y + 80, 150)
    for x in range(20, W, 45): rect(im, x - 4, y - 60, x + 4, y - 17, 120)
    water(im, y + 72)

@scene("kyoto-toji", "Kyoto", "Tō-ji, five storeys", "The five-storey pagoda of Tō-ji, the tallest wooden tower in the country, drawn as five roofs and a spire against the moon.")
def _(im):
    sky(im, 10, 40, 0.65); moon(im, 860, 260, 90); stars(im, 13); ground(im, int(H * 0.7), 45)
    pagoda(im, 520, int(H * 0.7), 5, 420); tree(im, 1000, int(H * 0.7), 80, 70, 13)

@scene("kyoto-tetsugaku", "Kyoto", "The Philosopher's Path", "The canal walk in blossom season: cherry trees on both banks, petals in the water, a stone path that only goes one way.")
def _(im):
    sky(im, 30, 90, 0.5); hills(im, int(H * 0.46), 40, 30, 14)
    for i, x in enumerate(range(40, W, 230)): tree(im, x, int(H * 0.64) + (i % 2) * 30, 120 + (i % 3) * 30, 150 + (i % 2) * 60, 20 + i, blossom=True)
    poly(im, [(W // 2 - 60, int(H * 0.62)), (W // 2 + 60, int(H * 0.62)), (W // 2 + 320, H), (W // 2 - 320, H)], 36)
    poly(im, [(0, int(H * 0.66)), (W // 2 - 90, int(H * 0.62)), (W // 2 - 340, H), (0, H)], 100)

@scene("kyoto-ryoanji", "Kyoto", "Ryōan-ji, the fifteen stones", "The rock garden: raked gravel drawn as rows of glyphs, the stones as silences in it. You cannot see all fifteen from any one place, and you cannot here either.")
def _(im):
    ground(im, 0, 20); rect(im, 0, 0, W, int(H * 0.22), 70); rect(im, 0, int(H * 0.22), W, int(H * 0.25), 130)
    d = ImageDraw.Draw(im)
    for y in range(int(H * 0.27), H, 24): d.line([(0, y), (W, y)], fill=(0, 175, 0), width=5)
    rnd = random.Random(15)
    for gx, gy, r in [(300, 600, 70), (390, 640, 40), (820, 560, 55), (760, 1000, 48), (880, 1040, 30), (240, 1150, 60), (520, 1320, 44), (600, 1290, 26), (1000, 1300, 50), (150, 900, 34), (980, 780, 26), (430, 880, 30), (700, 1450, 40), (1040, 1480, 28), (330, 1500, 22)]:
        d.ellipse([gx - r, gy - r * 0.6, gx + r, gy + r * 0.6], fill=(0, 8, 0)); d.ellipse([gx - r * 1.5, gy - r, gx + r * 1.5, gy + r], outline=(0, 200, 0), width=3)

@scene("kyoto-yasaka", "Kyoto", "Yasaka, the pagoda street", "Hōkan-ji's pagoda at the top of the sloping street, the shop lanterns coming on, dusk doing the rest.")
def _(im):
    sky(im, 20, 70, 0.6); ground(im, int(H * 0.6), 50); poly(im, [(W * 0.3, int(H * 0.6)), (W * 0.7, int(H * 0.6)), (W, H), (0, H)], 80)
    pagoda(im, 600, int(H * 0.6), 5, 300)
    for x in (0, 1000): rect(im, x, int(H * 0.5), x + 200, H, 60); windows(im, x, int(H * 0.55), x + 200, H, 21 + x, pitch=(18, 50), lit=0.7, v=(90, 140))
    for i in range(5): lantern(im, 110 + i * 40 if i < 3 else 1040 + (i - 3) * 60, int(H * 0.66) + i * 30, 14)

@scene("tokyo-shibuya", "Tokyo", "Shibuya, the crossing", "The scramble from above: five screens, a thousand heads, every one of them a glyph for the two seconds the light is green.")
def _(im):
    sky(im, 6, 18, 0.3)
    for x, w, top in ((0, 260, 120), (280, 320, 40), (620, 220, 200), (860, 340, 80)): tower_block(im, x, w, top, 28, x, lit=0.6)
    for x, y, w, h, s in ((60, 260, 180, 120, 31), (300, 200, 240, 160, 32), (880, 240, 220, 140, 33), (640, 330, 150, 90, 34)): sign(im, x, y, w, h, 210, s, red=60 if s % 2 else 0)
    rect(im, 0, int(H * 0.62), W, H, 40); d = ImageDraw.Draw(im)
    for i in range(0, W, 70): d.line([(i, int(H * 0.62)), (i + 200, H)], fill=(0, 150, 0), width=8)
    rnd = random.Random(35)
    for _ in range(520): x, y = rnd.randint(0, W), rnd.randint(int(H * 0.64), H); d.ellipse([x - 10, y - 13, x + 10, y + 13], fill=(0, rnd.randint(200, 255), 0))

@scene("tokyo-tower", "Tokyo", "Tokyo Tower, lit", "The tower over Shiba, orange by night, the office blocks around it holding still while the rain moves.")
def _(im):
    sky(im, 8, 30, 0.7); rnd = random.Random(41)
    for x in range(0, W, 140): tower_block(im, x, 120, rnd.randint(int(H * 0.45), int(H * 0.62)), 35, x, lit=0.4)
    cx = 600; base = int(H * 0.78); rect(im, 0, base, W, H, 30)
    poly(im, [(cx - 200, base), (cx + 200, base), (cx + 40, 160), (cx - 40, 160)], 40, red=70)
    d = ImageDraw.Draw(im)
    for y in range(200, base, 50):
        hw = 40 + (y - 160) / (base - 160) * 160; hw2 = 40 + (y + 50 - 160) / (base - 160) * 160
        d.line([(cx - hw, y), (cx + hw, y)], fill=(240, 220, 0), width=7)
        d.line([(cx - hw, y), (cx + hw2, y + 50)], fill=(230, 180, 0), width=4); d.line([(cx + hw, y), (cx - hw2, y + 50)], fill=(230, 180, 0), width=4)
    d.line([(cx - 40, 160), (cx - 200, base)], fill=(240, 230, 0), width=9); d.line([(cx + 40, 160), (cx + 200, base)], fill=(240, 230, 0), width=9)
    rect(im, cx - 130, 690, cx + 130, 760, 250, red=210); rect(im, cx - 4, 60, cx + 4, 160, 240, red=230)

@scene("tokyo-skytree", "Tokyo", "Skytree, over the Sumida", "The tallest thing in the city as a needle of light, the river taking a copy of it and breaking it up.")
def _(im):
    sky(im, 8, 36, 0.62); moon(im, 260, 200, 50)
    for x in range(0, W, 110): tower_block(im, x, 96, random.Random(x).randint(int(H * 0.46), int(H * 0.6)), 40, x + 7, lit=0.4)
    cx = 800; base = int(H * 0.62)
    poly(im, [(cx - 60, base), (cx + 60, base), (cx + 14, 120), (cx - 14, 120)], 200); rect(im, cx - 3, 40, cx + 3, 120, 240)
    rect(im, cx - 70, 560, cx + 70, 600, 250); rect(im, cx - 50, 820, cx + 50, 850, 250)
    water(im, base + 2)

@scene("tokyo-yokocho", "Tokyo", "Omoide Yokochō", "The yakitori alley behind Shinjuku station: six feet wide, lanterns overhead, every stall a lit window with smoke where the rain should be.")
def _(im):
    sky(im, 6, 20, 0.3)
    for side in (0, 1):
        x0, x1 = (0, 380) if side == 0 else (820, W)
        rect(im, x0, 200, x1, H, 70); windows(im, x0, 300, x1, H, 51 + side, pitch=(30, 80), lit=0.85, v=(150, 250))
        for i in range(6): sign(im, x0 + 20 + (i % 2) * 150, 240 + i * 180, 130, 70, 220, 60 + i + side * 10, red=40)
    poly(im, [(380, H), (820, H), (640, 260), (560, 260)], 90)
    for i in range(7): lantern(im, 600 + (i % 2) * 40 - 20, 300 + i * 120, 18 - i, red=220)

@scene("tokyo-rainbow", "Tokyo", "Rainbow Bridge", "The suspension bridge across the bay from Odaiba, its cables as a lattice of glyphs, the bay black under it.")
def _(im):
    sky(im, 8, 30, 0.55); stars(im, 61)
    for x in range(0, W, 130): tower_block(im, x, 110, random.Random(x + 3).randint(int(H * 0.36), int(H * 0.5)), 35, x + 9, lit=0.3)
    y = int(H * 0.56); d = ImageDraw.Draw(im); d.line([(0, y), (W, y)], fill=(0, 230, 0), width=30)
    for px in (300, 900):
        rect(im, px - 16, y - 300, px + 16, y + 80, 200)
        for i in range(0, 300, 20): d.line([(px, y - 300 + i), (px + (600 if px == 300 else -600) * i / 300, y)], fill=(0, 170, 0), width=4)
    for x in range(0, W, 40): d.line([(x, y - 240 + 200 * abs(math.sin(x / 600 * math.pi)), ), (x, y)], fill=(0, 150, 0), width=4)
    water(im, y + 8)

@scene("tokyo-akihabara", "Tokyo", "Akihabara, the signs", "Electric Town: a wall of signage seven storeys high, each sign a block of glyphs at its own brightness.")
def _(im):
    sky(im, 6, 20, 0.2); rnd = random.Random(71)
    for x in (0, 420, 800):
        rect(im, x, 100, x + 380, H, 60)
        for i in range(7): sign(im, x + 20, 140 + i * 190, 340, 140, rnd.randint(150, 240), 72 + i + x, red=rnd.choice((0, 0, 50, 90)))
    rect(im, 0, int(H * 0.85), W, H, 40)

@scene("tokyo-kaminarimon", "Tokyo", "Kaminarimon, the lantern", "The thunder gate at Asakusa: one giant lantern, red, under a roof wide enough to hide the street behind it.")
def _(im):
    sky(im, 10, 36, 0.6); ground(im, int(H * 0.72), 50)
    rect(im, 200, 400, 240, int(H * 0.72), 120); rect(im, 960, 400, 1000, int(H * 0.72), 120)
    roof(im, 600, 400, 520, 70, 170); rect(im, 160, 400, 1040, 460, 130)
    d = ImageDraw.Draw(im); d.ellipse([400, 480, 800, 1000], fill=(230, 200, 0))
    for y in range(500, 1000, 40): d.line([(400, y), (800, y)], fill=(160, 120, 0), width=3)
    rect(im, 560, 1000, 640, 1060, 60)

@scene("tokyo-shinkansen", "Tokyo", "Shinkansen, the platform", "The nose of the train at the platform, the doors lit, the departure board as a grid of glyphs that only says the time.")
def _(im):
    sky(im, 6, 18, 0.4); rect(im, 0, 0, W, 300, 40)
    poly(im, [(80, 1300), (1120, 1300), (1120, 700), (900, 560), (300, 560), (80, 700)], 160)
    poly(im, [(300, 560), (900, 560), (760, 470), (440, 470)], 190)
    windows(im, 100, 720, 1100, 900, 81, pitch=(90, 190), lit=0.9, v=(210, 250))
    rect(im, 0, 1300, W, H, 90); sign(im, 380, 120, 440, 130, 200, 82)
    for x in range(120, W, 240): rect(im, x, 1310, x + 90, 1330, 220)

@scene("tokyo-station", "Tokyo", "Tokyo Station, the facade", "The Marunouchi side: two domes, three storeys of brick drawn as lit arches, the plaza empty for once.")
def _(im):
    sky(im, 10, 40, 0.55); moon(im, 1000, 180, 50)
    rect(im, 0, 620, W, 1200, 90); windows(im, 0, 660, W, 1180, 91, pitch=(60, 90), lit=0.75, v=(150, 230))
    d = ImageDraw.Draw(im)
    for cx in (220, 980): d.pieslice([cx - 150, 470, cx + 150, 770], 180, 360, fill=(0, 140, 0)); rect(im, cx - 160, 620, cx + 160, 1200, 110); windows(im, cx - 160, 660, cx + 160, 1180, 92 + cx, pitch=(50, 90), lit=0.8, v=(150, 230))
    rect(im, 0, 1200, W, H, 45)

@scene("tokyo-hanabi", "Tokyo", "Sumida, fireworks", "The river festival: one burst over the skyline, the whole city looking up, the water taking the copy.")
def _(im):
    sky(im, 6, 26, 0.6)
    for x in range(0, W, 100): tower_block(im, x, 86, random.Random(x + 5).randint(int(H * 0.44), int(H * 0.58)), 40, x + 11, lit=0.5)
    d = ImageDraw.Draw(im); cx, cy = 560, 380
    for a in range(0, 360, 8):
        r = 380; x1, y1 = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
        d.line([(cx, cy), (x1, y1)], fill=(150, 230, 0), width=5); d.ellipse([x1 - 12, y1 - 12, x1 + 12, y1 + 12], fill=(230, 250, 0))
        x2, y2 = cx + r * 0.55 * math.cos(math.radians(a + 4)), cy + r * 0.55 * math.sin(math.radians(a + 4)); d.ellipse([x2 - 7, y2 - 7, x2 + 7, y2 + 7], fill=(200, 240, 0))
    d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(255, 255, 0))
    water(im, int(H * 0.6))

@scene("kyoto-nijo", "Kyoto", "Nijō, the moat gate", "The castle's karamon gate across still water, its ridge gilded, the banks in blossom on both sides.")
def _(im):
    sky(im, 16, 50, 0.6); stars(im, 91); hills(im, int(H * 0.56), 40, 45, 90)
    base = int(H * 0.68)
    for i, x in enumerate((150, 330, 920, 1080)):
        tree(im, x, base + (i % 2) * 16, 120 + (i % 2) * 20, 235, 90 + i, blossom=True)
    rect(im, W // 2 - 230, base - 130, W // 2 + 230, base, 95); roof(im, W // 2, base - 130, 270, 40, 220)
    rect(im, W // 2 - 46, base - 88, W // 2 + 46, base, 32)
    rect(im, W // 2 - 46, base - 100, W // 2 + 46, base - 88, 235, red=210)
    water(im, base + 4, v=24)

@scene("fukuoka-hakata", "Fukuoka", "Hakata, the yatai row", "A line of yatai stalls by the canal, steam over each counter, Fukuoka Tower's diamond skin catching the little light there is.")
def _(im):
    sky(im, 8, 26, 0.4); cx, base = 940, int(H * 0.46)
    poly(im, [(cx - 130, base), (cx + 130, base), (cx + 26, 130), (cx - 26, 130)], 200)
    d = ImageDraw.Draw(im)
    for y in range(170, base, 46):
        hw = 30 + (y - 130) / (base - 130) * 100
        d.line([(cx - hw, y), (cx + hw, y)], fill=(0, 150, 0), width=4)
        d.line([(cx - hw, y), (cx + hw, y - 46)], fill=(0, 120, 0), width=2)
    rect(im, 0, int(H * 0.68), W, H, 45)
    rnd = random.Random(93)
    for i, x in enumerate(range(50, 820, 150)):
        rect(im, x, int(H * 0.68) - 90, x + 130, int(H * 0.68), 95)
        roof(im, x + 65, int(H * 0.68) - 90, 80, 20, 140)
        sign(im, x + 14, int(H * 0.68) - 46, 100, 34, 180, 94 + i)
        lantern(im, x + 65, int(H * 0.68) - 60, 15, red=200)
        for _ in range(4):
            sx = x + rnd.randint(20, 110); sy = int(H * 0.68) - rnd.randint(10, 30)
            d.line([(sx, sy), (sx - 4, sy - 40)], fill=(0, 70, 0), width=3)
    water(im, int(H * 0.86), v=22)

@scene("hokkaido-noboribetsu", "Hokkaido", "Noboribetsu, Jigokudani", "Hell Valley by night: steam standing over sulphur ground, an oni's red eyes on the ridge above the onsen roofs, snow keeping everything else quiet.")
def _(im):
    sky(im, 6, 22, 0.42); moon(im, 220, 190, 58)
    hills(im, int(H * 0.5), 70, 190, 200); hills(im, int(H * 0.58), 40, 140, 201)
    ground(im, int(H * 0.68), 210)
    d = ImageDraw.Draw(im); rnd = random.Random(202)
    for _ in range(9):
        x = rnd.randint(200, 980); y = int(H * 0.68) - rnd.randint(0, 30)
        for j in range(6):
            d.ellipse([x - 18 + j * 3, y - 26 - j * 20, x + 18 + j * 3, y - 8 - j * 20], outline=(0, 70 + j * 8, 0), width=3)
    ox, oy = 940, int(H * 0.56)
    poly(im, [(ox - 46, oy), (ox + 46, oy), (ox + 30, oy - 150), (ox - 30, oy - 150)], 40)
    poly(im, [(ox - 30, oy - 150), (ox - 10, oy - 210), (ox - 2, oy - 150)], 60, red=180)
    poly(im, [(ox + 30, oy - 150), (ox + 10, oy - 210), (ox + 2, oy - 150)], 60, red=180)
    d.ellipse([ox - 22, oy - 150, ox + 22, oy - 108], fill=(0, 70, 0))
    d.ellipse([ox - 14, oy - 138, ox - 4, oy - 128], fill=(230, 30, 0)); d.ellipse([ox + 4, oy - 138, ox + 14, oy - 128], fill=(230, 30, 0))
    base = int(H * 0.82)
    rect(im, 120, base - 70, 700, base, 130); roof(im, 410, base - 70, 300, 34, 175)
    windows(im, 160, base - 60, 660, base - 6, 203, pitch=(40, 40), lit=0.7, v=(160, 230))
    water(im, base + 6, v=30)
    for _ in range(60):
        x = rnd.randint(0, W); y = rnd.randint(0, int(H * 0.68))
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(0, 235, 0))


# ---------- the matrix render ----------
def matrix(lightmap, path, seed):
    rnd = random.Random(seed)
    cols, rows = W // CELL, H // CELL
    g = lightmap.resize((cols, rows), Image.LANCZOS); px = g.load()
    im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, CELL + 3)
    streaks = {x: (rnd.randint(0, rows - 1), rnd.randint(8, 22)) for x in rnd.sample(range(cols), cols // 4)}
    for y in range(rows):
        for x in range(cols):
            r, v, _ = px[x, y]; lum = max(0.0, (v / 255.0 - 0.05) / 0.95) ** 0.85; red = r / 255.0
            boost = 0.0; head = False
            if x in streaks:
                hy, ln = streaks[x]; dy = (hy - y) % rows
                if dy == 0: head = True
                elif dy < ln: boost = (1 - dy / ln) * 0.5
            lum = min(1.0, lum + boost)
            if not head and lum < 0.4 and rnd.random() > 0.12 + lum * 2.0: continue   # dark areas: sparse glyphs, density carries the tone
            if lum < 0.03 and not head: continue
            ch = rnd.choice(KATA)
            if head: col = (225, 255, 225)
            elif red > 0.3:
                col = (int(120 + 135 * lum), int(40 + 90 * lum), int(20 * lum))
            else:
                gch = int(50 + 205 * lum); rch = int(10 + 130 * max(0, lum - 0.6) / 0.4); bch = int(15 + 80 * max(0, lum - 0.75) / 0.25)
                col = (min(255, rch), min(255, gch), min(255, bch))
            d.text((x * CELL, y * CELL - 2), ch, font=font, fill=col)
    im.save(path, optimize=True)

if __name__ == "__main__":
    manifest = []
    for i, (name, city, title, text, f) in enumerate(S, 1):
        random.seed(i * 7919)
        im = canvas(); f(im)
        # a little rain in the light map itself, then a soft blur so glyph brightness varies smoothly
        rain_lines(im, i, n=500, v=30)
        im = im.filter(ImageFilter.GaussianBlur(0.8))
        matrix(im, os.path.join(OUT, f"matrix-{i:02d}.png"), i)
        manifest.append({"name": f"matrix-{i:02d}", "scene": name, "city": city, "title": title, "text": text})
        print(f"matrix-{i:02d} {city}: {title}")
    json.dump(manifest, open(os.path.join(OUT, "set.json"), "w"), indent=1, ensure_ascii=False)
    print(len(S), "scenes")
