"""Code as World, Kyoto: one temple-garden scene as executable code.

Same three-part split as media/src/world/world.py (composition, dynamics, appearance),
same house rule (earth tones first, one loud colour against them), same discipline: every
rule in step() is a line you can read, nothing here is a solver. Units: t in hours, pixels
on the page; PX_PER_H converts a px/h rate into a per-tick delta via dt. Stdlib only.
"""
import math, random

W, H = 1200, 900
GROUND_Y = 780          # pond surface / garden ground line petals fall to and recycle from

EARTH = dict(sky="#e9dfc9", dawn="#e8c194", sun="#d9a441", cloud="#f2ecdd",
             hill="#8c7f68", pine="#57654a", wall="#8f8574", roof="#3f4a44",
             moss="#7c8a5e", water="#4f6b5a", deep="#2c3f37", bloom="#e7c7bd",
             koi="#c47a3a", koi_patch="#f2ebdc", stone="#7a6a56", flame="#e8a23a", ink="#2a1f14")
LOUD = "#c1432a"        # the torii gate


# ---------------------------------------------------------------- composition
def compose(seed=11):
    """The entities of the world. The seed places the koi's start, the petals' spawn points,
    phase and per-petal fall cycle, and the clouds; everything else is fixed."""
    rng = random.Random(seed)
    entities = [
        dict(id="sun", kind="sun", pos=[80, 420], size=40,
             arc=dict(cx=600, cy=420, rx=520, ry=330), day_length_h=7.0, angle_deg=0.0, palette="earth"),
        dict(id="hill", kind="land", pos=[0, 300], size=[1200, 260],
             shape=[[0, 560], [0, 420], [180, 370], [420, 340], [650, 365], [900, 335], [1200, 400], [1200, 560]],
             palette="earth"),
        dict(id="pond", kind="water", pos=[140, 560], size=[840, 220], palette="earth",
             ripple_amp=0.0),
        dict(id="cherry", kind="tree", pos=[260, 560], size=[220, 180],
             canopy=dict(cx=260, cy=430, rx=150, ry=95), trunk_w=16, palette="earth"),
        dict(id="torii", kind="torii", pos=[800, 560], size=[150, 240], palette="loud"),
        dict(id="lantern", kind="lantern", pos=[1090, 560], size=[42, 92], lit=False, palette="earth"),
        dict(id="koi", kind="koi", pos=[rng.uniform(400, 600), 700], size=[74, 24],
             swim=dict(amp_px=230, period_h=2.6, center_x=560, base_y=700), palette="earth"),
    ]
    for i in range(3):
        entities.append(dict(id=f"pine-{i}", kind="pine",
                             pos=[110 + i * 470 + rng.uniform(-30, 30), 400 + rng.uniform(-15, 15)],
                             size=[60 + rng.uniform(-8, 8), 90 + rng.uniform(-10, 10)], palette="earth"))
    for i in range(2):
        entities.append(dict(id=f"cloud-{i}", kind="cloud",
                             pos=[rng.uniform(120, 1080), rng.uniform(80, 220)],
                             size=[rng.uniform(150, 240), rng.uniform(24, 38)], palette="earth"))
    fall_speed = 130.0     # px/h
    for i in range(12):
        spawn = [rng.uniform(175, 370), rng.uniform(390, 445)]
        cycle_h = (GROUND_Y - spawn[1]) / fall_speed
        entities.append(dict(id=f"petal-{i}", kind="petal", pos=list(spawn), spawn=spawn, size=[11, 7],
                             fall_speed_px_h=fall_speed, drift_speed_px_h=22.0,
                             flutter_amp_px=15.0, flutter_period_h=0.5,
                             phase=rng.uniform(0, 2 * math.pi), t0_h=rng.uniform(0, cycle_h), cycle_h=cycle_h,
                             palette="earth"))
    return dict(seed=seed, tick=0, t=0.0, dt=None, sun_angle_deg=0.0, lantern_lit=False, ripple_amp=0.0, entities=entities)


def get(state, id_):
    return next(e for e in state["entities"] if e["id"] == id_)


# ---------------------------------------------------------------- dynamics
def step(state, dt):
    """Advance the world by dt hours. Every rule is explicit; nothing is solved."""
    state["tick"] += 1
    state["dt"] = dt
    t = state["t"] = state["tick"] * dt
    sun, pond, koi, lantern = get(state, "sun"), get(state, "pond"), get(state, "koi"), get(state, "lantern")

    # sun: an arc from the left horizon at sunrise (t = 0) to the right horizon at sunset,
    # same shape as the Salish Sea world's sun, a shorter day (one autumn afternoon into dusk)
    sun["angle_deg"] = state["sun_angle_deg"] = min(180.0, 180.0 * t / sun["day_length_h"])
    a = math.radians(sun["angle_deg"])
    sun["pos"] = [sun["arc"]["cx"] - sun["arc"]["rx"] * math.cos(a), sun["arc"]["cy"] - sun["arc"]["ry"] * math.sin(a)]

    # lantern: lights itself once the sun has dropped past dusk threshold, not before
    lantern["lit"] = state["lantern_lit"] = sun["angle_deg"] >= 150.0

    # koi: swims a sinusoidal lane across the pond, a small vertical bob riding the same period;
    # the ripple it leaves is a pure function of how fast it is crossing the centre of the lane
    sw = koi["swim"]
    koi["pos"][0] = sw["center_x"] + sw["amp_px"] * math.sin(2 * math.pi * t / sw["period_h"])
    koi["pos"][1] = sw["base_y"] + 7 * math.sin(4 * math.pi * t / sw["period_h"])
    pond["ripple_amp"] = state["ripple_amp"] = 13.0 * abs(math.cos(2 * math.pi * t / sw["period_h"]))

    # petals: each is a pure function of elapsed time since its own last spawn (t + t0, modulo its
    # own fall cycle) - a steady fall, a steady eastward drift, a flutter riding on top of both
    for e in state["entities"]:
        if e["kind"] != "petal":
            continue
        local_t = (t + e["t0_h"]) % e["cycle_h"]
        e["pos"][1] = e["spawn"][1] + e["fall_speed_px_h"] * local_t
        e["pos"][0] = (e["spawn"][0] + e["drift_speed_px_h"] * local_t
                       + e["flutter_amp_px"] * math.sin(2 * math.pi * local_t / e["flutter_period_h"] + e["phase"]))
    return state


# ---------------------------------------------------------------- appearance
def poly(points, fill):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" fill="{fill}"/>'


def render(state):
    """The state as flat shapes. Draw order is depth order: sky, sun, clouds, hill, pines, pond,
    koi and its ripples, torii on the far bank, cherry tree and lantern on the near bank, petals
    falling over all of it."""
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
    sun = get(state, "sun")
    low_sun = sun["angle_deg"] >= 150.0 or sun["angle_deg"] <= 12.0
    s.append(f'<rect width="{W}" height="{H}" fill="{EARTH["dawn"] if low_sun else EARTH["sky"]}"/>')
    s.append(f'<circle cx="{sun["pos"][0]:.1f}" cy="{sun["pos"][1]:.1f}" r="{sun["size"]}" fill="{EARTH["sun"]}"/>')
    for e in state["entities"]:
        if e["kind"] == "cloud":
            s.append(f'<ellipse cx="{e["pos"][0]:.1f}" cy="{e["pos"][1]:.1f}" rx="{e["size"][0] / 2:.1f}" ry="{e["size"][1] / 2:.1f}" fill="{EARTH["cloud"]}"/>')
    s.append(poly(get(state, "hill")["shape"], EARTH["hill"]))
    for e in state["entities"]:
        if e["kind"] == "pine":
            px, py, pw, ph = e["pos"][0], e["pos"][1], e["size"][0], e["size"][1]
            s.append(poly([[px, py - ph], [px - pw / 2, py], [px + pw / 2, py]], EARTH["pine"]))
    # ground: moss under everything, the pond cut into it
    s.append(f'<rect x="0" y="{GROUND_Y - 220:.1f}" width="{W}" height="{H - GROUND_Y + 220:.1f}" fill="{EARTH["moss"]}"/>')
    pond = get(state, "pond")
    px, py, pw, ph = pond["pos"][0], pond["pos"][1], pond["size"][0], pond["size"][1]
    s.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="18" fill="{EARTH["water"]}"/>')
    s.append(f'<rect x="{px:.1f}" y="{py + ph * 0.55:.1f}" width="{pw:.1f}" height="{ph * 0.45:.1f}" rx="14" fill="{EARTH["deep"]}"/>')
    koi = get(state, "koi")
    kx, ky = koi["pos"]
    ramp = pond["ripple_amp"]
    for i, r in enumerate((1, 2, 3)):
        s.append(f'<ellipse cx="{kx:.1f}" cy="{ky:.1f}" rx="{28 + r * (10 + ramp):.1f}" ry="{9 + r * (3 + ramp * 0.3):.1f}" fill="none" stroke="{EARTH["cloud"]}" stroke-width="1.4" opacity="{0.30 - i * 0.08:.2f}"/>')
    kw, kh = koi["size"]
    s.append(f'<path d="M{kx - kw / 2:.1f} {ky:.1f} q{kw * 0.15:.1f} -{kh / 2:.1f} {kw * 0.6:.1f} -{kh * 0.3:.1f} q{kw * 0.25:.1f} {kh * 0.15:.1f} {kw * 0.4:.1f} {kh * 0.3:.1f} q-{kw * 0.15:.1f} {kh / 2:.1f} -{kw * 0.6:.1f} {kh * 0.3:.1f} q-{kw * 0.25:.1f} -{kh * 0.15:.1f} -{kw * 0.4:.1f} -{kh * 0.3:.1f}z" fill="{EARTH["koi"]}"/>')
    s.append(f'<path d="M{kx - kw / 2:.1f} {ky:.1f} l-16 -8 l0 16z" fill="{EARTH["koi"]}"/>')
    s.append(f'<ellipse cx="{kx + kw * 0.12:.1f}" cy="{ky - kh * 0.18:.1f}" rx="{kw * 0.14:.1f}" ry="{kh * 0.16:.1f}" fill="{EARTH["koi_patch"]}"/>')
    # torii on the far bank: two pillars, two beams, the loud colour against everything above
    tx, ty, tw, th = *get(state, "torii")["pos"], *get(state, "torii")["size"]
    s.append(f'<rect x="{tx - tw / 2:.1f}" y="{ty - th:.1f}" width="16" height="{th:.1f}" fill="{LOUD}"/>')
    s.append(f'<rect x="{tx + tw / 2 - 16:.1f}" y="{ty - th:.1f}" width="16" height="{th:.1f}" fill="{LOUD}"/>')
    s.append(f'<rect x="{tx - tw / 2 - 18:.1f}" y="{ty - th:.1f}" width="{tw + 36:.1f}" height="16" fill="{EARTH["ink"]}"/>')
    s.append(f'<rect x="{tx - tw / 2 - 26:.1f}" y="{ty - th - 22:.1f}" width="{tw + 52:.1f}" height="20" rx="4" fill="{LOUD}"/>')
    s.append(f'<rect x="{tx - tw / 2 + 4:.1f}" y="{ty - th + 34:.1f}" width="{tw - 8:.1f}" height="12" fill="{LOUD}"/>')
    # cherry tree on the near bank: trunk, canopy, then its own falling petals draw last, over all
    tree = get(state, "cherry")
    cy_c = tree["canopy"]
    s.append(f'<rect x="{tree["pos"][0] - tree["trunk_w"] / 2:.1f}" y="{cy_c["cy"] + 10:.1f}" width="{tree["trunk_w"]}" height="{tree["pos"][1] - cy_c["cy"] - 10:.1f}" fill="{EARTH["wall"]}"/>')
    s.append(f'<ellipse cx="{cy_c["cx"]:.1f}" cy="{cy_c["cy"]:.1f}" rx="{cy_c["rx"]:.1f}" ry="{cy_c["ry"]:.1f}" fill="{EARTH["bloom"]}"/>')
    # stone lantern on the near bank: base, shaft, roof cap, a flame once the sun is down
    lx, ly, lw, lh = *get(state, "lantern")["pos"], *get(state, "lantern")["size"]
    s.append(f'<rect x="{lx - lw / 2:.1f}" y="{ly - lh * 0.35:.1f}" width="{lw:.1f}" height="{lh * 0.35:.1f}" fill="{EARTH["stone"]}"/>')
    s.append(f'<rect x="{lx - lw * 0.28:.1f}" y="{ly - lh * 0.68:.1f}" width="{lw * 0.56:.1f}" height="{lh * 0.33:.1f}" fill="{EARTH["stone"]}"/>')
    s.append(f'<polygon points="{lx - lw * 0.6:.1f},{ly - lh * 0.68:.1f} {lx:.1f},{ly - lh:.1f} {lx + lw * 0.6:.1f},{ly - lh * 0.68:.1f}" fill="{EARTH["roof"]}"/>')
    if get(state, "lantern")["lit"]:
        s.append(f'<circle cx="{lx:.1f}" cy="{ly - lh * 0.5:.1f}" r="{lw * 0.55:.1f}" fill="{EARTH["flame"]}" opacity="0.22"/>')
        s.append(f'<ellipse cx="{lx:.1f}" cy="{ly - lh * 0.5:.1f}" rx="6" ry="9" fill="{EARTH["flame"]}"/>')
    for e in state["entities"]:
        if e["kind"] == "petal":
            x, y = e["pos"]
            s.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{e["size"][0]:.1f}" ry="{e["size"][1]:.1f}" fill="{EARTH["bloom"]}" transform="rotate(30 {x:.1f} {y:.1f})"/>')
    s.append("</svg>")
    return "\n".join(s)
