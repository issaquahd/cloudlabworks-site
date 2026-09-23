#!/usr/bin/env python3
"""Code as World, v0.1: one Salish Sea scene as executable code.

Three parts, named the way the Code-as-World paper names them:
  composition  what is in the world (entities, positions, sizes, a few physical numbers)
  dynamics     step(state, dt): the rules that move it, written out as plain code
  appearance   render(state) -> SVG: flat shapes, 1200 x 900, earth tones plus one loud colour

The dynamics are a script, not a solver: every rule is a line you can read. Nothing here is
MuJoCo or any physics engine. Units: t in hours, lengths in metres where the rule is physical,
pixels where it is only on the page; PX_PER_M converts between them. Stdlib only.
"""
import math, random

W, H = 1200, 900
PX_PER_M = 40          # one metre of tide or dive is forty pixels on the page
WATER_Y0 = 520         # water line at zero tide (mean water), pixels from the top

# earth tones first, then one loud colour placed against them (the house rule on /art)
EARTH = dict(sky="#e8dcc4", dawn="#e6c9a0", sun="#d9a441", cloud="#f2ebdc",
             far="#7a6a56", land="#6b4f36", rock="#8a7357", water="#4a6b63",
             deep="#2f4a45", under="#1a2c29", orca="#141414", patch="#f4e8c8", heron="#7d8a86", ink="#2a1f14")
LOUD = "#e0472c"       # the canoe


# ---------------------------------------------------------------- composition
def compose(seed=7):
    """The entities of the world. The seed places the clouds, the heron and the boats;
    everything else is fixed. Same seed, same world."""
    rng = random.Random(seed)
    water_y = WATER_Y0 + 1.6 * PX_PER_M        # low water at t = 0, so the line starts 64 px below mean
    entities = [
        dict(id="sun", kind="sun", pos=[80, 440], size=44,
             arc=dict(cx=600, cy=440, rx=520, ry=340), day_length_h=12.5,
             angle_deg=0.0, palette="earth"),
        dict(id="water", kind="water", pos=[0, WATER_Y0], size=[W, H - WATER_Y0],
             tide=dict(amplitude_m=1.6, period_h=12.42), tide_m=-1.6,
             current=dict(max_px_per_h=90.0), current_px_per_h=0.0, palette="earth"),
        dict(id="headland", kind="land", pos=[0, 380], size=[1200, 220],
             shape=[[0, 600], [0, 470], [140, 430], [330, 400], [520, 420], [640, 450], [700, 600]],
             palette="earth"),
        dict(id="island", kind="land", pos=[700, 440], size=[300, 180],
             shape=[[700, 620], [720, 500], [780, 460], [860, 440], [960, 470], [1000, 620]],
             palette="earth"),
        dict(id="canoe", kind="canoe", pos=[rng.uniform(220, 300), water_y], size=[130, 26],
             mass_kg=55.0, buoyancy="floats", drift_px=0.0, palette="loud"),
        dict(id="orca", kind="orca", pos=[rng.uniform(420, 520), water_y], size=[220, 70],
             mass_kg=4000.0, buoyancy="neutral", swim_px_per_h=110.0, heading=1,
             dive=dict(depth_m=4.0, cycle_h=0.45), depth_m=0.0, surfaced=True, palette="earth"),
        dict(id="heron", kind="heron", pos=[rng.uniform(850, 900), None], size=[34, 96],
             mass_kg=2.3, stands_on="island", palette="earth"),
    ]
    # the heron stands on the rock, so its feet are the island's surface at its own x,
    # not a number typed next to one
    island = next(e for e in entities if e["id"] == "island")
    heron = next(e for e in entities if e["id"] == "heron")
    heron["pos"][1] = surface_y(island["shape"], heron["pos"][0])
    for i in range(3):
        entities.append(dict(id=f"cloud-{i}", kind="cloud",
                             pos=[rng.uniform(100, 1100), rng.uniform(90, 260)],
                             size=[rng.uniform(140, 260), rng.uniform(26, 44)], palette="earth"))
    return dict(seed=seed, tick=0, t=0.0, dt=None, tide_m=-1.6, water_y=water_y, sun_angle_deg=0.0, entities=entities)


def get(state, id_):
    return next(e for e in state["entities"] if e["id"] == id_)


def surface_y(shape, x):
    """The top of a land polygon at a given x: the smallest y on any edge spanning x.
    Used so a standing bird rests on the rock rather than near it."""
    tops = []
    for (x0, y0), (x1, y1) in zip(shape, shape[1:]):
        if x0 == x1:
            continue
        lo, hi = (x0, x1) if x0 < x1 else (x1, x0)
        if lo <= x <= hi:
            tops.append(y0 + (x - x0) * (y1 - y0) / (x1 - x0))
    return min(tops) if tops else None


# ---------------------------------------------------------------- dynamics
def step(state, dt):
    """Advance the world by dt hours. Every rule is explicit; nothing is solved."""
    state["tick"] += 1
    state["dt"] = dt
    t = state["t"] = state["tick"] * dt
    water, sun, canoe, orca = get(state, "water"), get(state, "sun"), get(state, "canoe"), get(state, "orca")

    # tide: a sinusoid on the water level, low water at t = 0, one M2 period of 12.42 hours
    tide = water["tide"]
    water["tide_m"] = state["tide_m"] = -tide["amplitude_m"] * math.cos(2 * math.pi * t / tide["period_h"])
    water["pos"][1] = state["water_y"] = WATER_Y0 - state["tide_m"] * PX_PER_M

    # sun: an arc from the left horizon at sunrise (t = 0) to the right horizon at sunset
    sun["angle_deg"] = state["sun_angle_deg"] = min(180.0, 180.0 * t / sun["day_length_h"])
    a = math.radians(sun["angle_deg"])
    sun["pos"] = [sun["arc"]["cx"] - sun["arc"]["rx"] * math.cos(a), sun["arc"]["cy"] - sun["arc"]["ry"] * math.sin(a)]

    # current: follows the tide, east on the flood, west on the ebb; the canoe drifts with it
    water["current_px_per_h"] = water["current"]["max_px_per_h"] * math.sin(2 * math.pi * t / tide["period_h"])
    canoe["pos"][0] += water["current_px_per_h"] * dt
    canoe["drift_px"] += water["current_px_per_h"] * dt
    canoe["pos"][1] = state["water_y"]          # it floats: the hull sits on whatever the water line is

    # orca: swims at a steady pace and turns at the frame edge rather than wrapping, because a
    # body that leaves one side and reappears at the other is not a persistent world;
    # neutrally buoyant, so depth is set by the breath cycle rather than by weight
    half = orca["size"][0] / 2
    x = orca["pos"][0] + orca["heading"] * orca["swim_px_per_h"] * dt
    if x > W - half:
        x, orca["heading"] = 2 * (W - half) - x, -1      # reflect off the east edge
    elif x < half:
        x, orca["heading"] = 2 * half - x, 1             # reflect off the west edge
    orca["pos"][0] = x
    orca["depth_m"] = orca["dive"]["depth_m"] * max(0.0, math.sin(2 * math.pi * t / orca["dive"]["cycle_h"]))
    orca["surfaced"] = orca["depth_m"] < 0.2
    orca["pos"][1] = state["water_y"] + orca["depth_m"] * PX_PER_M

    # heron: stays put. It is hunting, and the rock does not move.
    return state


# ---------------------------------------------------------------- appearance
def poly(points, fill):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" fill="{fill}"/>'


def render(state):
    """The state as flat shapes. Draw order is the depth order: sky, sun, clouds, far land,
    water, whatever is under the water, whatever floats, whatever stands on the rock."""
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
    wy = state["water_y"]
    sun = get(state, "sun")
    low_sun = math.sin(math.radians(sun["angle_deg"])) < 0.25
    s.append(f'<rect width="{W}" height="{H}" fill="{EARTH["dawn"] if low_sun else EARTH["sky"]}"/>')
    s.append(f'<circle cx="{sun["pos"][0]:.1f}" cy="{sun["pos"][1]:.1f}" r="{sun["size"]}" fill="{EARTH["sun"]}"/>')
    for e in state["entities"]:
        if e["kind"] == "cloud":
            s.append(f'<ellipse cx="{e["pos"][0]:.1f}" cy="{e["pos"][1]:.1f}" rx="{e["size"][0] / 2:.1f}" ry="{e["size"][1] / 2:.1f}" fill="{EARTH["cloud"]}"/>')
    s.append(poly(get(state, "headland")["shape"], EARTH["far"]))
    s.append(poly(get(state, "island")["shape"], EARTH["rock"]))
    # the water covers whatever the tide has reached
    s.append(f'<rect x="0" y="{wy:.1f}" width="{W}" height="{H - wy:.1f}" fill="{EARTH["water"]}"/>')
    s.append(f'<rect x="0" y="{wy + 120:.1f}" width="{W}" height="{H - wy - 120:.1f}" fill="{EARTH["deep"]}"/>')
    o = get(state, "orca")
    ox, ow, oh = o["pos"][0], o["size"][0], o["size"][1]
    if o["surfaced"]:
        # the back arches out of the water and the dorsal fin shows; the rest is under the line
        s.append(f'<path d="M{ox - ow / 2:.1f} {wy:.1f} q{ow / 2:.1f} -{oh * 0.6:.1f} {ow:.1f} 0z" fill="{EARTH["orca"]}"/>')
        s.append(f'<path d="M{ox - 14:.1f} {wy - oh * 0.28:.1f} q4 -{oh * 0.9:.1f} 30 -{oh * 0.95:.1f} q-2 {oh * 0.5:.1f} 6 {oh * 0.85:.1f}z" fill="{EARTH["orca"]}"/>')
        s.append(f'<ellipse cx="{ox + ow * 0.3:.1f}" cy="{wy - 4:.1f}" rx="{ow * 0.1:.1f}" ry="5" fill="{EARTH["patch"]}"/>')
    else:
        # a dark silhouette at depth, seen through the water
        oy = o["pos"][1]
        s.append(f'<ellipse cx="{ox:.1f}" cy="{oy:.1f}" rx="{ow / 2:.1f}" ry="{oh / 2:.1f}" fill="{EARTH["under"]}"/>')
        s.append(f'<path d="M{ox - 14:.1f} {oy - oh / 2:.1f} q4 -{oh * 0.9:.1f} 30 -{oh * 0.95:.1f} q-2 {oh * 0.5:.1f} 6 {oh * 0.85:.1f}z" fill="{EARTH["under"]}"/>')
        s.append(f'<path d="M{ox + ow / 2 - 10:.1f} {oy:.1f} l40 -18 l0 36z" fill="{EARTH["under"]}"/>')
    c = get(state, "canoe")
    cx, cw, ch = c["pos"][0], c["size"][0], c["size"][1]
    # the one loud colour: a flat hull on the water line, a paddler, a paddle
    s.append(f'<path d="M{cx - cw / 2:.1f} {wy - 6:.1f} q{cw / 2:.1f} {ch:.1f} {cw:.1f} 0 l-8 -10 q-{cw / 2 - 8:.1f} 14 -{cw - 16:.1f} 0z" fill="{LOUD}"/>')
    s.append(f'<circle cx="{cx + 6:.1f}" cy="{wy - 26:.1f}" r="8" fill="{EARTH["ink"]}"/>')
    s.append(f'<rect x="{cx - 2:.1f}" y="{wy - 20:.1f}" width="16" height="16" rx="3" fill="{EARTH["ink"]}"/>')
    s.append(f'<line x1="{cx + 14:.1f}" y1="{wy - 24:.1f}" x2="{cx + 44:.1f}" y2="{wy + 10:.1f}" stroke="{EARTH["ink"]}" stroke-width="4" stroke-linecap="round"/>')
    h = get(state, "heron")
    hx, hy, hw, hh = h["pos"][0], h["pos"][1], h["size"][0], h["size"][1]
    # a heron in five flat shapes: two legs, a body, a neck, a head with a beak
    s.append(f'<line x1="{hx - 5:.1f}" y1="{hy:.1f}" x2="{hx - 5:.1f}" y2="{hy - hh * 0.42:.1f}" stroke="{EARTH["heron"]}" stroke-width="3"/>')
    s.append(f'<line x1="{hx + 6:.1f}" y1="{hy:.1f}" x2="{hx + 4:.1f}" y2="{hy - hh * 0.42:.1f}" stroke="{EARTH["heron"]}" stroke-width="3"/>')
    s.append(f'<ellipse cx="{hx:.1f}" cy="{hy - hh * 0.55:.1f}" rx="{hw * 0.7:.1f}" ry="{hh * 0.16:.1f}" fill="{EARTH["heron"]}"/>')
    s.append(f'<path d="M{hx + hw * 0.4:.1f} {hy - hh * 0.6:.1f} q10 -{hh * 0.3:.1f} 2 -{hh * 0.42:.1f}" fill="none" stroke="{EARTH["heron"]}" stroke-width="5" stroke-linecap="round"/>')
    s.append(f'<ellipse cx="{hx + hw * 0.45:.1f}" cy="{hy - hh:.1f}" rx="9" ry="6" fill="{EARTH["heron"]}"/>')
    s.append(f'<path d="M{hx + hw * 0.45 + 8:.1f} {hy - hh - 2:.1f} l26 4 l-26 4z" fill="{EARTH["sun"]}"/>')
    s.append("</svg>")
    return "\n".join(s)
