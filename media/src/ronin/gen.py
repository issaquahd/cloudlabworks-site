#!/Users/rebl/.local/share/imgtools/bin/python
"""The Ronin set: samurai and masterless swordsmen as digital rain. Twenty-five scenes.

Same hand as the Matrix set and the same two-stage method: paint a light map (a 3:4 canvas of
greys where the green channel is brightness and the red channel marks the one warm thing), then
read it cell by cell and turn every cell into a katakana or digit whose brightness is the light
under it. Nothing is traced from a photograph or a film still; every figure is drawn here in
code from a seed.

Where the Matrix set is architecture, this set is people. The primitives below add what a body
needs: a stance, a hakama that widens at the hem, shoulders that carry a kataginu, a topknot, a
blade at rest or drawn. A figure has to survive being reduced to 10 px glyph cells, so the
silhouette does the work and detail below about 12 px is wasted.

Run: gen.py [outdir]  -> ronin-NN.png + set.json
"""
import os, sys, json, math, random
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
sys.path.insert(0, os.path.join(HERE, "..", "matrix"))
import gen as mx                      # primitives + the glyph renderer, one source of truth

W, H = mx.W, mx.H
D = ImageDraw.Draw


# ---------- figure primitives (green = light, red = the warm accent) ----------
def _p(im, pts, v, red=0):
    D(im).polygon([(int(x), int(y)) for x, y in pts], fill=(red, v, 0))


# The city set fills its frame with architecture; a figure study does not, so the people have
# to be big or the canvas reads as empty. First pass at h=300 left a 1200x1600 frame almost
# entirely black around a small silhouette. Everything is scaled here rather than at each of the
# twenty-five call sites.
FIG = 1.85

def figure(im, cx, base, h, v=190, lean=0.0, arms="rest", seed=0, hat=False, kneel=False):
    """A standing swordsman. h is head-to-heel in pixels; everything is proportioned off it."""
    rnd = random.Random(seed)
    h = h * FIG
    u = h / 8.0                                   # one head-height
    dx = lean * u
    if kneel:
        base_y = base
        _p(im, [(cx - u * 1.5, base_y), (cx + u * 1.5, base_y),
                (cx + u * 1.1, base_y - u * 1.4), (cx - u * 1.1, base_y - u * 1.4)], v)
        hip = base_y - u * 1.4
    else:
        # hakama: wide at the hem, the shape that reads even at ten pixels
        _p(im, [(cx - u * 1.55, base), (cx - u * 0.35, base),
                (cx - u * 0.3, base - u * 3.0), (cx - u * 1.0, base - u * 3.0)], v)
        _p(im, [(cx + u * 0.35, base), (cx + u * 1.55, base),
                (cx + u * 1.0, base - u * 3.0), (cx + u * 0.3, base - u * 3.0)], v)
        hip = base - u * 2.9
    # torso, narrowing to the shoulders
    _p(im, [(cx - u * 1.0 + dx * .3, hip), (cx + u * 1.0 + dx * .3, hip),
            (cx + u * 1.15 + dx, hip - u * 2.3), (cx - u * 1.15 + dx, hip - u * 2.3)], v)
    sh = hip - u * 2.3
    # kataginu: the stiff winged shoulders
    _p(im, [(cx - u * 1.9 + dx, sh + u * .15), (cx + u * 1.9 + dx, sh + u * .15),
            (cx + u * 1.1 + dx, sh - u * .5), (cx - u * 1.1 + dx, sh - u * .5)], min(255, v + 25))
    # head and topknot
    hx, hy = cx + dx * 1.15, sh - u * 1.05
    D(im).ellipse([hx - u * .52, hy - u * .62, hx + u * .52, hy + u * .62], fill=(0, min(255, v + 15), 0))
    if hat:
        _p(im, [(hx - u * 1.5, hy - u * .15), (hx + u * 1.5, hy - u * .15), (hx, hy - u * 1.25)],
           min(255, v + 30))
    else:
        _p(im, [(hx - u * .18, hy - u * .6), (hx + u * .18, hy - u * .6),
                (hx + u * .30, hy - u * 1.15), (hx - u * .30, hy - u * 1.15)], min(255, v + 20))
    # arms and blade
    if arms == "draw":
        sword(im, cx + u * 1.4 + dx, sh + u * .3, -28, u * 4.4, min(255, v + 50))
        _p(im, [(cx + u * 1.0 + dx, sh), (cx + u * 1.8 + dx, sh + u * .5),
                (cx + u * 1.5 + dx, sh + u * .9), (cx + u * .8 + dx, sh + u * .5)], v)
    elif arms == "high":
        sword(im, cx + u * .6 + dx, sh - u * .9, -78, u * 4.8, min(255, v + 50))
        _p(im, [(cx + u * .7 + dx, sh), (cx + u * 1.3 + dx, sh - u * 1.0),
                (cx + u * .9 + dx, sh - u * 1.2), (cx + u * .3 + dx, sh - u * .2)], v)
    elif arms == "rest":
        sword(im, cx - u * 1.2 + dx, hip - u * .3, 14, u * 3.6, min(255, v + 30))
    return dict(head=(hx, hy), shoulder=sh, hip=hip, u=u)


def sword(im, x, y, ang, length, v=225):
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    tw = max(2.0, length * 0.022)
    x2, y2 = x + c * length, y + s * length
    _p(im, [(x - s * tw, y + c * tw), (x + s * tw, y - c * tw),
            (x2 + s * tw * .5, y2 - c * tw * .5), (x2 - s * tw * .5, y2 + c * tw * .5)], v)
    # tsuba and grip, back down the other way
    gx, gy = x - c * length * .22, y - s * length * .22
    _p(im, [(gx - s * tw * 2.4, gy + c * tw * 2.4), (gx + s * tw * 2.4, gy - c * tw * 2.4),
            (x + s * tw * 1.2, y - c * tw * 1.2), (x - s * tw * 1.2, y + c * tw * 1.2)], max(0, v - 60))


def horse(im, cx, base, s=1.0, v=150):
    u = 34 * s
    _p(im, [(cx - u * 2.2, base - u * 1.6), (cx + u * 1.9, base - u * 1.7),
            (cx + u * 2.0, base - u * 2.6), (cx - u * 2.1, base - u * 2.5)], v)
    for k in (-1.8, -1.1, 1.1, 1.8):
        _p(im, [(cx + u * k - u * .16, base - u * 1.6), (cx + u * k + u * .16, base - u * 1.6),
                (cx + u * k + u * .22, base), (cx + u * k - u * .22, base)], v)
    _p(im, [(cx + u * 1.8, base - u * 2.5), (cx + u * 2.6, base - u * 3.5),
            (cx + u * 3.1, base - u * 3.3), (cx + u * 2.2, base - u * 2.3)], v)
    _p(im, [(cx - u * 2.1, base - u * 2.5), (cx - u * 2.9, base - u * 1.2),
            (cx - u * 2.5, base - u * 1.0), (cx - u * 1.9, base - u * 2.2)], max(0, v - 30))


def grave(im, cx, base, h=120, v=165):
    _p(im, [(cx - h * .16, base), (cx + h * .16, base),
            (cx + h * .16, base - h * .86), (cx, base - h), (cx - h * .16, base - h * .86)], v)


def fire(im, cx, cy, r=40, red=235, v=225):
    for i, k in enumerate((1.0, 0.66, 0.38)):
        _p(im, [(cx - r * k, cy), (cx + r * k, cy), (cx, cy - r * k * 2.2)],
           min(255, v + i * 12), red=red)


def flag(im, x, base, h=260, v=170, red=0):
    D(im).rectangle([x - 3, base - h, x + 3, base], fill=(0, v, 0))
    _p(im, [(x + 4, base - h), (x + 70, base - h + 14), (x + 70, base - h + 150), (x + 4, base - h + 130)],
       min(255, v + 30), red=red)


def blossom_fall(im, seed, n=180, v=120):
    rnd = random.Random(seed); d = D(im)
    for _ in range(n):
        x, y = rnd.randrange(W), rnd.randrange(H); r = rnd.randint(3, 7)
        d.ellipse([x, y, x + r, y + r * .7], fill=(90, v + rnd.randint(-25, 25), 0))


def snow(im, seed, n=700, v=150):
    rnd = random.Random(seed); d = D(im)
    for _ in range(n):
        x, y = rnd.randrange(W), rnd.randrange(H); r = rnd.randint(2, 5)
        d.ellipse([x, y, x + r, y + r], fill=(0, v + rnd.randint(-40, 40), 0))


# ---------- scenes ----------
S = []
def scene(name, era, title, text):
    def deco(f): S.append((name, era, title, text, f)); return f
    return deco


@scene("rain-bridge", "Ronin", "Ronin on the bridge, rain",
       "A masterless swordsman stops halfway across. The rain is already in the glyphs, so the "
       "weather and the medium are the same thing.")
def _(im):
    mx.sky(im, 8, 26, 0.5); mx.hills(im, int(H * .48), 70, 26, 3)
    mx.water(im, int(H * .72), 22); mx.bridge_arc(im, 120, W - 120, int(H * .70), 90, 150, 26)
    figure(im, W // 2, int(H * .66), 300, 200, arms="rest", seed=1, hat=True)
    mx.rain_lines(im, 11, n=1500, v=52)


@scene("iai-dawn", "Samurai", "Iai, first light",
       "The draw and the cut are one motion. The blade is the brightest thing in the frame "
       "because at this distance it is the only thing that moves.")
def _(im):
    mx.sky(im, 30, 95, 0.58); mx.moon(im, 300, 240, 44, 200)
    mx.ground(im, int(H * .72), 30); mx.hills(im, int(H * .58), 50, 44, 7)
    figure(im, 560, int(H * .72), 340, 205, arms="draw", seed=2)


@scene("beach-duel", "Ronin", "Two on the sand at dawn",
       "Ganryujima weather. Both figures are the same brightness, which is the only comment the "
       "set makes on who was right.")
def _(im):
    mx.sky(im, 40, 120, 0.55); mx.water(im, int(H * .55), 34); mx.ground(im, int(H * .78), 46)
    figure(im, 360, int(H * .80), 300, 195, arms="rest", seed=3)
    figure(im, 860, int(H * .80), 300, 195, lean=-0.25, arms="high", seed=4)


@scene("torii-sleep", "Ronin", "Asleep against the gate",
       "No lord, no barracks, no watch to stand. The vermilion of the torii is the warm thing; "
       "the man is not.")
def _(im):
    mx.sky(im, 6, 18, 0.45); mx.ground(im, int(H * .70), 26); mx.stars(im, 9)
    mx.torii(im, W // 2, int(H * .70), 2.6, red=210, v=150)
    figure(im, W // 2 - 190, int(H * .70), 200, 150, lean=0.9, arms="none", seed=5, kneel=True)


@scene("bamboo-walk", "Samurai", "Through the bamboo",
       "Vertical grain everywhere, and one vertical thing that is walking. The grove and the "
       "rain columns run the same direction on purpose.")
def _(im):
    mx.sky(im, 10, 34, 0.3); mx.ground(im, int(H * .78), 30)
    for i in range(22):
        mx.bamboo(im, 30 + i * 56, int(H * .06), 70 + (i * 37) % 60, i)
    figure(im, 600, int(H * .80), 330, 210, arms="rest", seed=6, hat=True)


@scene("seiza-audience", "Samurai", "Seiza, before the dais",
       "Kneeling, blade laid to the right where it cannot be drawn quickly. The posture is the "
       "message and the room is dark enough to make it the only one.")
def _(im):
    mx.sky(im, 4, 10, 0.2); mx.ground(im, int(H * .66), 22)
    mx.rect(im, 180, int(H * .30), W - 180, int(H * .66), 40)
    mx.lantern(im, 300, int(H * .40), 30); mx.lantern(im, W - 300, int(H * .40), 30)
    figure(im, W // 2, int(H * .74), 260, 175, arms="none", seed=7, kneel=True)


@scene("mountain-pass", "Ronin", "The pass, alone",
       "Small figure, large country. The hills carry most of the light and the man carries "
       "almost none, which is the correct ratio for the situation.")
def _(im):
    mx.sky(im, 16, 58, 0.5); mx.hills(im, int(H * .44), 120, 34, 11, n=8)
    mx.ground(im, int(H * .80), 26)
    figure(im, 780, int(H * .82), 190, 165, arms="rest", seed=8, hat=True)


@scene("yabusame", "Samurai", "Yabusame, the third target",
       "Mounted archery at a gallop. The horse is drawn flat and fast; the rider is a wedge.")
def _(im):
    mx.sky(im, 26, 80, 0.55); mx.ground(im, int(H * .68), 40); mx.hills(im, int(H * .55), 40, 30, 5)
    horse(im, 520, int(H * .76), 1.5 * FIG, 150)   # mount scales with the rider
    figure(im, 520, int(H * .62), 220, 195, lean=0.3, arms="high", seed=9)
    for x in (940, 1080):
        mx.rect(im, x, int(H * .56), x + 26, int(H * .70), 120, red=190)


@scene("snow-stand", "Ronin", "Standing in snow",
       "Snow in the light map and rain in the glyphs, two weathers in one frame. The figure is "
       "the only warm-edged shape and even that is cold.")
def _(im):
    mx.sky(im, 34, 70, 0.52); mx.ground(im, int(H * .70), 78); snow(im, 12, 900, 165)
    figure(im, 600, int(H * .74), 320, 150, arms="rest", seed=10, hat=True)


@scene("noodle-stall", "Ronin", "The stall at the roadside",
       "A paper lantern, a bowl, a sword laid across the knees. The one warm thing is the food.")
def _(im):
    mx.sky(im, 5, 16, 0.4); mx.ground(im, int(H * .72), 28)
    mx.rect(im, 380, int(H * .40), 900, int(H * .46), 90)
    mx.roof(im, 640, int(H * .40), 300, 44, 130)
    mx.lantern(im, 430, int(H * .50), 34, red=240, v=235)
    figure(im, 720, int(H * .78), 230, 160, arms="none", seed=13, kneel=True)


@scene("rice-field", "Ronin", "Duel in the paddy",
       "Flooded field, two men, no ground worth the name. The water takes the light and gives "
       "back two silhouettes.")
def _(im):
    mx.sky(im, 22, 74, 0.5); mx.water(im, int(H * .58), 40); mx.hills(im, int(H * .50), 44, 26, 4)
    figure(im, 430, int(H * .80), 290, 185, arms="high", seed=14)
    figure(im, 800, int(H * .80), 290, 185, lean=-0.2, arms="draw", seed=15)


@scene("river-ford", "Samurai", "The ford",
       "Crossing at the shallow place, blade held clear of the water. Everything below the knee "
       "is light with a current in it.")
def _(im):
    mx.sky(im, 18, 56, 0.48); mx.hills(im, int(H * .44), 60, 28, 6); mx.water(im, int(H * .64), 46)
    figure(im, 560, int(H * .84), 300, 190, arms="high", seed=16, hat=True)


@scene("seven-ridge", "Ronin", "Seven on the ridge",
       "Seven silhouettes on a skyline, unevenly spaced because a line of men never is.")
def _(im):
    mx.sky(im, 30, 96, 0.62); mx.hills(im, int(H * .58), 70, 30, 8)
    base = int(H * .66)
    for i, x in enumerate((180, 330, 455, 600, 745, 890, 1040)):
        figure(im, x, base + (i % 3) * 8, 210 + (i % 4) * 14, 40, arms="rest", seed=20 + i,
               hat=(i % 3 == 0))


@scene("temple-gate", "Samurai", "The gate at night",
       "A two-storey gate, a lantern under it, a man who has stopped just short of the light.")
def _(im):
    mx.sky(im, 4, 14, 0.42); mx.ground(im, int(H * .74), 24); mx.stars(im, 21)
    mx.rect(im, 300, int(H * .40), 980, int(H * .74), 60)
    mx.roof(im, 640, int(H * .40), 420, 60, 120); mx.roof(im, 640, int(H * .26), 330, 52, 100)
    mx.lantern(im, 640, int(H * .50), 40, red=235, v=245)
    figure(im, 640, int(H * .84), 250, 130, arms="rest", seed=22)


@scene("whetstone", "Ronin", "Sharpening, by the fire",
       "The only scene in the set where the blade is not a threat. It is a chore, and the fire "
       "is doing the talking.")
def _(im):
    mx.sky(im, 3, 9, 0.35); mx.ground(im, int(H * .68), 26)
    fire(im, 760, int(H * .70), 70)
    figure(im, 520, int(H * .74), 240, 170, arms="none", seed=23, kneel=True)
    sword(im, 560, int(H * .69), 2, 260, 215)


@scene("charge", "Samurai", "The charge",
       "Three riders abreast. At this size a horse is a wedge and a rider is a smaller wedge on "
       "top of it, and that is enough.")
def _(im):
    mx.sky(im, 24, 88, 0.52); mx.ground(im, int(H * .66), 44)
    for i, x in enumerate((280, 620, 960)):
        horse(im, x, int(H * .78) + i * 6, 1.3 * FIG, 140)
        figure(im, x, int(H * .64) + i * 6, 200, 190, lean=0.35, arms="high", seed=30 + i)
    flag(im, 1090, int(H * .70), 300, 170, red=200)


@scene("blossom", "Samurai", "Under the falling blossom",
       "The one scene that borrows the cliche on purpose. Petals are warm-channel, the man is "
       "not, and the contrast is the whole point.")
def _(im):
    mx.sky(im, 28, 78, 0.5); mx.ground(im, int(H * .74), 34)
    mx.tree(im, 300, int(H * .74), 240, 90, 4, blossom=True)
    mx.tree(im, 980, int(H * .74), 200, 80, 5, blossom=True)
    figure(im, 640, int(H * .78), 300, 185, arms="rest", seed=33)
    blossom_fall(im, 34, 220, 120)


@scene("burning-village", "Ronin", "Walking out of the village",
       "The warm channel is doing something it does nowhere else in the set: it is behind him, "
       "and he is not looking at it.")
def _(im):
    mx.sky(im, 10, 40, 0.5); mx.ground(im, int(H * .74), 30)
    for x, w in ((150, 200), (420, 240), (900, 220)):
        mx.rect(im, x, int(H * .52), x + w, int(H * .74), 70)
        mx.roof(im, x + w // 2, int(H * .52), w // 2 + 20, 40, 95)
        fire(im, x + w // 2, int(H * .52), 90)
    figure(im, 700, int(H * .84), 320, 175, arms="rest", seed=35, hat=True)


@scene("waterfall", "Samurai", "Under the fall",
       "Misogi: standing under cold water on purpose. The column of the fall and the column of "
       "the man are the same width, which is not an accident.")
def _(im):
    mx.sky(im, 8, 26, 0.3); mx.hills(im, int(H * .30), 40, 30, 9)
    mx.rect(im, 540, int(H * .18), 740, int(H * .70), 130)
    mx.water(im, int(H * .70), 44)
    figure(im, 640, int(H * .78), 260, 175, arms="none", seed=36)


@scene("castle-wall", "Samurai", "On the wall",
       "A sloped stone base, a white keep behind, one sentry. The keep has the light; the "
       "sentry has the job.")
def _(im):
    mx.sky(im, 14, 48, 0.5); mx.stars(im, 37); mx.moon(im, 950, 260, 54)
    mx.poly(im, [(80, H), (250, int(H * .56)), (W - 250, int(H * .56)), (W - 80, H)], 76)
    mx.pagoda(im, 640, int(H * .56), 4, 300, 150, 210)
    figure(im, 330, int(H * .56), 180, 120, arms="rest", seed=38)


@scene("teahouse-door", "Ronin", "In the doorway",
       "Framed by a doorway he has not decided to walk through. The frame is brighter than "
       "either side of it.")
def _(im):
    mx.sky(im, 4, 12, 0.3); mx.ground(im, int(H * .76), 22)
    mx.rect(im, 330, int(H * .26), 950, int(H * .76), 34)
    mx.rect(im, 470, int(H * .36), 810, int(H * .76), 105)
    mx.rect(im, 500, int(H * .39), 780, int(H * .76), 22)
    figure(im, 640, int(H * .76), 280, 150, arms="rest", seed=39)


@scene("fog-duel", "Ronin", "Fog, and someone else in it",
       "One figure resolved, one barely. The set's quietest frame: most of the glyphs here are "
       "carrying almost no light at all.")
def _(im):
    mx.sky(im, 20, 44, 0.6); mx.ground(im, int(H * .78), 28)
    figure(im, 430, int(H * .80), 300, 175, arms="rest", seed=40)
    figure(im, 900, int(H * .80), 290, 62, lean=-0.15, arms="rest", seed=41, hat=True)


@scene("lantern-forest", "Ronin", "Carrying the light",
       "A hand lantern in a cryptomeria wood. The warm circle travels with him and nothing else "
       "in the frame is lit at all.")
def _(im):
    mx.sky(im, 3, 10, 0.25); mx.ground(im, int(H * .78), 20)
    for i in range(9):
        mx.tree(im, 90 + i * 140, int(H * .78), 150 + (i * 29) % 70, 46, 50 + i)
    figure(im, 600, int(H * .82), 280, 140, arms="none", seed=44)
    mx.lantern(im, 720, int(H * .62), 40, red=240, v=250)


@scene("grave-marker", "Ronin", "At the marker",
       "Kneeling at a stone. The sword is on the ground, which in this set happens exactly "
       "twice and means the same thing both times.")
def _(im):
    mx.sky(im, 12, 38, 0.52); mx.hills(im, int(H * .48), 50, 26, 12); mx.ground(im, int(H * .74), 28)
    grave(im, 780, int(H * .74), 150, 175)
    figure(im, 560, int(H * .80), 240, 165, arms="none", seed=45, kneel=True)
    sword(im, 640, int(H * .77), 4, 220, 190)


@scene("into-the-rain", "Ronin", "Walking into it",
       "The last frame of the set, and the only one shot from behind. Everything ahead of him "
       "is rain, which here is also the material the picture is made of.")
def _(im):
    mx.sky(im, 10, 30, 0.55); mx.ground(im, int(H * .76), 24)
    mx.hills(im, int(H * .55), 60, 20, 13)
    figure(im, 640, int(H * .80), 330, 165, arms="rest", seed=48, hat=True)
    mx.rain_lines(im, 49, n=2200, v=58)


if __name__ == "__main__":
    manifest = []
    for i, (name, era, title, text, f) in enumerate(S, 1):
        random.seed(i * 6421)
        im = mx.canvas(); f(im)
        mx.rain_lines(im, i + 300, n=700, v=34)
        im = im.filter(ImageFilter.GaussianBlur(0.8))
        mx.matrix(im, os.path.join(OUT, f"ronin-{i:02d}.png"), i + 500)
        manifest.append({"name": f"ronin-{i:02d}", "scene": name, "city": era, "title": title, "text": text})
        print(f"ronin-{i:02d} {era}: {title}")
    json.dump(manifest, open(os.path.join(OUT, "set.json"), "w"), indent=1, ensure_ascii=False)
    print(len(S), "scenes")
