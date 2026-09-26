#!/usr/bin/env python3
"""Code as Bioacoustics, v0.1: what a call is, and where the pod goes next.

Fourth in the "Code as..." series (World, Music, Nature, this). Same three parts, named the
way world.py and nature.py name them:

  composition  what exists (synthesised call contours; an ensemble of forecast paths)
  dynamics     step(): an Ornstein-Uhlenbeck velocity process with direction blending
  appearance   render_*() -> SVG: flat shapes, 1200 x 900, earth tones plus one loud colour

WHAT IS REAL HERE AND WHAT IS NOT. Every number this file prints is program output -- the
synthesis parameters, the O-U constants, the ensemble spread, the false-positive count. None
of it is a whale. There is no recording in this repository, no fitted model, no field data.
The page carries two visual treatments and they are load-bearing:

  SOURCED       cards whose CONTENT traces to a published source, credited on the card
  ILLUSTRATIVE  cards that are this program's own synthesis, badge burned into the frame

The badge is drawn inside the SVG, not written in a caption, so it survives cropping and
reposting. Decided 2026-09-24 after the citation got specific enough to be mistaken for a
result: naming Lin's method is a credibility improvement AND a risk increase at the same time.

Credits, verified against the live sites 2026-09-24:
  HALLO, Simon Fraser University -- orca.research.sfu.ca -- binary classifier framed as
    source identification, models open-sourced, ecotype/pod work forthcoming.
  Lin (2023, SFU) -- the O-U velocity process with direction blending that `step()` below
    illustrates the SHAPE of. Not their parameters. Not their model.
  Ford's call-type catalogue -- the reason "discrete repertoire per pod" is a real idea and
    not one this page invented.
Not affiliated with any of them.

Units: t in seconds, lengths in pixels, frequency in Hz on a log axis. Stdlib only.
"""
import math, random

W, H = 1200, 900

# earth tones first, then one loud colour placed against them (house rule, /world and /nature)
EARTH = dict(deep="#16262b", water="#27424a", mid="#456a71", light="#7f918f",
             silt="#6b4f36", sand="#8a7357", foam="#f2ebdc", ink="#141414")
LOUD = "#e0472c"          # the synthetic marker, the false positive, and nothing else
SOURCED_EDGE = "#8a7357"  # sand: a card standing on a cited source
SYNTH_EDGE = LOUD         # loud: a card this program made up

FONT = "Helvetica,Arial,sans-serif"

# Two badges, not one. The Lin credit belongs on the cards that actually illustrate his
# method -- the forecast frames and the hazard overlay -- and nowhere else. Printing "based on
# Lin (2023)" under a synthesised call contour would be the exact error the badge exists to
# prevent: borrowing a real method's authority for a drawing that does not use it.
BADGE_FORECAST = ("ILLUSTRATIVE — concept only",
                  "Based on the idea in Lin (2023, SFU): an Ornstein-Uhlenbeck velocity process",
                  "with direction blending. Not HALLO's fitted model, not real whale data.")
BADGE_SYNTH = ("ILLUSTRATIVE — concept only",
               "Synthesised by this program from a fixed seed. Not a recording, not a",
               "measurement, not real whale data.")


# ---------------------------------------------------------------- composition
def call_contour(seed, n=220, dur=1.6):
    """One synthesised pulsed-call contour: (t, Hz) pairs.

    A real catalogued call type is defined by the SHAPE of its frequency contour over time --
    that much is Ford's catalogue and is why call types are discrete at all. The shape here is
    this program's: three segments (onset sweep, held plateau with a wobble, terminal drop),
    parameters drawn from `seed`. It is a cartoon of the right kind of object.
    """
    rng = random.Random(seed)
    f0 = rng.uniform(600, 1100)          # onset
    f1 = f0 * rng.uniform(1.25, 2.10)    # plateau
    f2 = f1 * rng.uniform(0.42, 0.72)    # terminal drop
    wob_hz = rng.uniform(3.0, 9.0)       # plateau wobble rate
    wob_amp = rng.uniform(0.02, 0.07)    # as a fraction of f1
    a, b = rng.uniform(0.14, 0.26), rng.uniform(0.60, 0.76)   # segment boundaries, fraction
    pts = []
    for i in range(n + 1):
        u = i / n
        t = u * dur
        if u < a:
            f = f0 + (f1 - f0) * (u / a) ** 0.6
        elif u < b:
            v = (u - a) / (b - a)
            f = f1 * (1.0 + wob_amp * math.sin(v * math.tau * wob_hz * dur))
        else:
            v = (u - b) / (1.0 - b)
            f = f1 + (f2 - f1) * v ** 1.4
        pts.append((t, f))
    return dict(seed=seed, dur_s=dur, f_onset=f0, f_plateau=f1, f_terminal=f2,
                wobble_hz=wob_hz, wobble_frac=wob_amp, points=pts)


def contour_distance(c1, c2):
    """Mean absolute difference in octaves between two contours, resampled to a common grid.

    This is the whole idea behind "which call type is this" reduced to one honest number: two
    calls are the same type when their contours sit on top of each other. A real classifier
    does far more than this and HALLO's is a neural one; this is the arithmetic underneath the
    intuition, printed so the page can quote it instead of asserting it.
    """
    n = min(len(c1["points"]), len(c2["points"]))
    tot = 0.0
    for i in range(n):
        f1 = max(1e-6, c1["points"][i][1])
        f2 = max(1e-6, c2["points"][i][1])
        tot += abs(math.log2(f1 / f2))
    return tot / n


def compose_repertoire(seed=7, groups=3, types=4):
    """A groups x types occupancy matrix: which synthesised type each synthesised group uses.

    The real claim -- resident pods hold overlapping but distinct repertoires, which is what
    makes acoustic source identification possible at all -- is Ford's and is credited on the
    card. The matrix is this program's, seeded and printed.
    """
    rng = random.Random(seed)
    labels = [f"group-{chr(ord('A') + g)}" for g in range(groups)]
    names = [f"type-{t + 1}" for t in range(types)]
    # Constructed, not sampled. A uniform draw kept producing an almost-full grid, which says
    # "everyone uses everything" -- the opposite of the claim the card is making. So the shape
    # is built: one type every group shares, one type a single group holds, the rest drawn.
    # It is synthesised either way; this way it is synthesised to be legible.
    grid = [[False] * types for _ in range(groups)]
    shared_t, unique_t = 0, types - 1
    for g in range(groups):
        grid[g][shared_t] = True
    grid[rng.randrange(groups)][unique_t] = True
    for g in range(groups):
        for t in range(types):
            if t not in (shared_t, unique_t):
                grid[g][t] = rng.random() < 0.55
    shared = sum(1 for t in range(types) if all(grid[g][t] for g in range(groups)))
    unique = sum(1 for t in range(types) if sum(grid[g][t] for g in range(groups)) == 1)
    return dict(seed=seed, labels=labels, names=names, grid=grid, shared=shared, unique=unique)


# ---------------------------------------------------------------- dynamics
# Ornstein-Uhlenbeck on VELOCITY, not position: the animal keeps its momentum and is pulled
# back toward a preferred speed and heading, which is why O-U is the family Lin (2023) works
# in. Direction blending: the pull target is a blend of where it is already going and where
# the channel wants it to go. Discretised Euler-Maruyama.
THETA = 0.55       # 1/s, mean reversion rate on velocity
SIGMA = 14.0       # px/s^1.5, volatility
MU_SPEED = 42.0    # px/s, preferred cruise
W_PERSIST = 0.72   # weight on the current heading in the blend
W_PREFER = 0.28    # weight on the preferred channel heading


def compose_paths(n_paths=24, seed=3, start=(230.0, 560.0), heading_deg=-12.0):
    rng = random.Random(seed)
    h = math.radians(heading_deg)
    return dict(
        t=0.0, tick=0, seed=seed, n_paths=n_paths,
        prefer=h,
        paths=[dict(
            pos=[start[0], start[1]],
            vel=[math.cos(h) * MU_SPEED, math.sin(h) * MU_SPEED],
            trail=[(start[0], start[1])],
            rng=random.Random(rng.randrange(1 << 30)),
        ) for _ in range(n_paths)],
    )


def step(state, dt):
    """One Euler-Maruyama step of the O-U velocity process with direction blending."""
    for p in state["paths"]:
        vx, vy = p["vel"]
        speed = math.hypot(vx, vy)
        # --- direction blending: target heading is current heading blended with preferred ---
        cur = math.atan2(vy, vx) if speed > 1e-9 else state["prefer"]
        tx = W_PERSIST * math.cos(cur) + W_PREFER * math.cos(state["prefer"])
        ty = W_PERSIST * math.sin(cur) + W_PREFER * math.sin(state["prefer"])
        tn = math.hypot(tx, ty) or 1.0
        mux, muy = (tx / tn) * MU_SPEED, (ty / tn) * MU_SPEED
        # --- O-U on velocity: pull toward mu, plus a Wiener increment ---
        rt = math.sqrt(dt)
        vx += THETA * (mux - vx) * dt + SIGMA * rt * p["rng"].gauss(0.0, 1.0)
        vy += THETA * (muy - vy) * dt + SIGMA * rt * p["rng"].gauss(0.0, 1.0)
        p["vel"] = [vx, vy]
        p["pos"][0] += vx * dt
        p["pos"][1] += vy * dt
        # the frame is a channel, not a torus: reflect, so nothing teleports between frames
        # (the /world orca wrapped at tick 59 of 60 and hid the jump in the gap)
        for k, hi in ((0, W), (1, H)):
            if p["pos"][k] < 40:
                p["pos"][k] = 40.0; p["vel"][k] = abs(p["vel"][k])
            elif p["pos"][k] > hi - 40:
                p["pos"][k] = hi - 40.0; p["vel"][k] = -abs(p["vel"][k])
        p["trail"].append((p["pos"][0], p["pos"][1]))
    state["t"] += dt
    state["tick"] += 1
    return state


def spread_px(state):
    """Mean distance of the ensemble from its own centroid: the forecast's honest error bar."""
    ps = state["paths"]
    cx = sum(p["pos"][0] for p in ps) / len(ps)
    cy = sum(p["pos"][1] for p in ps) / len(ps)
    return sum(math.hypot(p["pos"][0] - cx, p["pos"][1] - cy) for p in ps) / len(ps)


def centroid(state):
    ps = state["paths"]
    return (sum(p["pos"][0] for p in ps) / len(ps), sum(p["pos"][1] for p in ps) / len(ps))


# ---------------------------------------------------------------- the naive rule
def naive_detector(seed=5, n=160, threshold=0.62):
    """A deliberately bad detector: "loud in band => whale". Counts what it gets wrong.

    This is the card that replaced the toy classifier. A confusion matrix reads as a RESULT no
    matter what the caption says -- visual grammar beats caption text -- so the page shows the
    failure instead of the score: the same rule, fired on a synthetic boat, lighting up.
    """
    rng = random.Random(seed)
    events, tp = [], 0
    for i in range(n):
        kind = rng.choices(["call", "boat", "quiet"], weights=[0.28, 0.22, 0.50])[0]
        if kind == "call":
            energy = rng.uniform(0.55, 0.95)
        elif kind == "boat":
            energy = rng.uniform(0.50, 0.90)     # a boat is loud in band too. that is the point.
        else:
            energy = rng.uniform(0.02, 0.35)
        fired = energy >= threshold
        events.append(dict(i=i, kind=kind, energy=energy, fired=fired))
        if fired and kind == "call":
            tp += 1
    fp = sum(1 for e in events if e["fired"] and e["kind"] != "call")
    fn = sum(1 for e in events if not e["fired"] and e["kind"] == "call")
    return dict(seed=seed, n=n, threshold=threshold, events=events,
                true_positive=tp, false_positive=fp, false_negative=fn,
                boat_fires=sum(1 for e in events if e["fired"] and e["kind"] == "boat"))


# ---------------------------------------------------------------- appearance
def _open(bg_top=None, bg_bot=None):
    top = bg_top or EARTH["mid"]
    bot = bg_bot or EARTH["deep"]
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/>'
            f'</linearGradient></defs>',
            f'<rect width="{W}" height="{H}" fill="url(#bg)"/>']


def _frame(out, sourced):
    """The two treatments, drawn as the outermost thing so blurring the text still tells them
    apart: a solid sand edge for a card standing on a cited source, a loud dashed edge for a
    card this program synthesised."""
    if sourced:
        out.append(f'<rect x="10" y="10" width="{W-20}" height="{H-20}" fill="none" '
                   f'stroke="{SOURCED_EDGE}" stroke-width="10"/>')
    else:
        out.append(f'<rect x="10" y="10" width="{W-20}" height="{H-20}" fill="none" '
                   f'stroke="{SYNTH_EDGE}" stroke-width="10" stroke-dasharray="26 14"/>')


def _badge(out, badge=None):
    """The ILLUSTRATIVE badge, burned into the frame so it survives a crop or a repost.

    Kept left of x=780: the watermarker stamps its own plate into the bottom-right corner and
    anything drawn under it is lost. A disclaimer you cannot read is not a disclaimer.
    """
    badge = badge or BADGE_SYNTH
    x, y, bw, bh = 34, H - 150, 726, 116
    out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{EARTH["ink"]}" '
               f'opacity="0.82" stroke="{LOUD}" stroke-width="3"/>')
    out.append(f'<text x="{x+18}" y="{y+34}" font-family="{FONT}" font-size="22" '
               f'font-weight="bold" fill="{LOUD}" letter-spacing="1.5">{badge[0]}</text>')
    for i, line in enumerate(badge[1:]):
        out.append(f'<text x="{x+18}" y="{y+62+i*26}" font-family="{FONT}" font-size="18" '
                   f'fill="{EARTH["foam"]}" opacity="0.92">{line}</text>')


def _credit(out, lines):
    """The SOURCED credit strip. Same corner rule as the badge: it stops short of the plate."""
    if isinstance(lines, str):
        lines = [lines]
    bh = 40 + 26 * len(lines)
    y = H - 60 - bh
    out.append(f'<rect x="34" y="{y}" width="726" height="{bh}" fill="{EARTH["ink"]}" '
               f'opacity="0.78" stroke="{SOURCED_EDGE}" stroke-width="3"/>')
    for i, line in enumerate(lines):
        out.append(f'<text x="52" y="{y+34+i*26}" font-family="{FONT}" font-size="19" '
                   f'fill="{EARTH["foam"]}" opacity="0.95">{line}</text>')


def _title(out, title, sub=""):
    out.append(f'<text x="40" y="70" font-family="{FONT}" font-size="34" font-weight="bold" '
               f'fill="{EARTH["foam"]}">{title}</text>')
    if sub:
        out.append(f'<text x="40" y="104" font-family="{FONT}" font-size="21" '
                   f'fill="{EARTH["foam"]}" opacity="0.75">{sub}</text>')


def _close(out):
    out.append('</svg>')
    return "\n".join(out)


def _hz_to_y(f, top=150, bot=H - 190, lo=300.0, hi=3000.0):
    u = (math.log2(max(lo, min(hi, f)) / lo)) / math.log2(hi / lo)
    return bot - u * (bot - top)


def render_contour(c, title, sub=""):
    out = _open()
    _title(out, title, sub)
    x0, x1 = 90, W - 70
    for f in (300, 600, 1200, 2400):
        y = _hz_to_y(f)
        out.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{EARTH["light"]}" '
                   f'stroke-width="1" opacity="0.35"/>')
        out.append(f'<text x="{x0-12}" y="{y+6:.1f}" text-anchor="end" font-family="{FONT}" '
                   f'font-size="17" fill="{EARTH["foam"]}" opacity="0.7">{f} Hz</text>')
    pts = " ".join(f'{x0 + (t / c["dur_s"]) * (x1 - x0):.1f},{_hz_to_y(f):.1f}'
                   for t, f in c["points"])
    out.append(f'<polyline points="{pts}" fill="none" stroke="{EARTH["foam"]}" stroke-width="5" '
               f'stroke-linejoin="round" stroke-linecap="round"/>')
    out.append(f'<text x="{x1}" y="{H-176}" text-anchor="end" font-family="{FONT}" font-size="18" '
               f'fill="{EARTH["foam"]}" opacity="0.7">{c["dur_s"]:.1f} s</text>')
    _badge(out)
    _frame(out, sourced=False)
    return _close(out)


def render_family(cs, title, sub=""):
    out = _open()
    _title(out, title, sub)
    cols, cw = len(cs), (W - 120) / len(cs)
    for i, c in enumerate(cs):
        cx0 = 60 + i * cw
        out.append(f'<rect x="{cx0+8:.1f}" y="150" width="{cw-16:.1f}" height="{H-340}" '
                   f'fill="{EARTH["deep"]}" opacity="0.45"/>')
        pts = " ".join(f'{cx0 + 18 + (t / c["dur_s"]) * (cw - 36):.1f},'
                       f'{_hz_to_y(f, top=180, bot=H - 210):.1f}' for t, f in c["points"])
        out.append(f'<polyline points="{pts}" fill="none" stroke="{EARTH["foam"]}" '
                   f'stroke-width="4" stroke-linejoin="round"/>')
        out.append(f'<text x="{cx0 + cw/2:.1f}" y="{H-170}" text-anchor="middle" '
                   f'font-family="{FONT}" font-size="20" fill="{EARTH["foam"]}" '
                   f'opacity="0.85">type-{i+1}</text>')
    _badge(out)
    _frame(out, sourced=False)
    return _close(out)


def groups_h(rep, ch=110):
    return len(rep["labels"]) * ch


def render_repertoire(rep, title, sub="", credit=""):
    out = _open()
    _title(out, title, sub)
    x0, y0 = 300, 200
    cw, ch = 180, 110
    for t, name in enumerate(rep["names"]):
        out.append(f'<text x="{x0 + t*cw + cw/2}" y="{y0-22}" text-anchor="middle" '
                   f'font-family="{FONT}" font-size="21" fill="{EARTH["foam"]}" opacity="0.8">{name}</text>')
    for g, label in enumerate(rep["labels"]):
        out.append(f'<text x="{x0-28}" y="{y0 + g*ch + ch/2 + 8}" text-anchor="end" '
                   f'font-family="{FONT}" font-size="21" fill="{EARTH["foam"]}" opacity="0.8">{label}</text>')
        for t in range(len(rep["names"])):
            on = rep["grid"][g][t]
            x, y = x0 + t * cw, y0 + g * ch
            out.append(f'<rect x="{x+6}" y="{y+6}" width="{cw-12}" height="{ch-12}" '
                       f'fill="{EARTH["foam"] if on else EARTH["deep"]}" '
                       f'opacity="{0.9 if on else 0.4}" stroke="{EARTH["light"]}" stroke-width="2"/>')
    out.append(f'<text x="40" y="{y0 + groups_h(rep) + 76}" font-family="{FONT}" font-size="22" '
               f'fill="{EARTH["foam"]}" opacity="0.9">'
               f'{rep["shared"]} type(s) shared by every group, {rep["unique"]} held by one only</text>')
    if credit:
        _credit(out, credit)
        _frame(out, sourced=True)
    else:
        _badge(out)
        _frame(out, sourced=False)
    return _close(out)


def render_match(c1, c2, d, title, sub=""):
    out = _open()
    _title(out, title, sub)
    x0, x1 = 90, W - 70
    for c, col, wdt in ((c1, EARTH["foam"], 5), (c2, LOUD, 4)):
        pts = " ".join(f'{x0 + (t / c["dur_s"]) * (x1 - x0):.1f},{_hz_to_y(f):.1f}'
                       for t, f in c["points"])
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{wdt}" '
                   f'stroke-linejoin="round"/>')
    out.append(f'<text x="40" y="{H-172}" font-family="{FONT}" font-size="24" '
               f'fill="{EARTH["foam"]}">mean separation {d:.3f} octaves</text>')
    _badge(out)
    _frame(out, sourced=False)
    return _close(out)


def render_paths(state, title, sub="", hazard=None):
    out = _open()
    _title(out, title, sub)
    cx, cy = centroid(state)
    sp = spread_px(state)
    # the ensemble spread, drawn as the thing it is: an error bar, not a prediction
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{sp:.1f}" fill="{EARTH["foam"]}" '
               f'opacity="0.12" stroke="{EARTH["foam"]}" stroke-width="2" stroke-dasharray="8 8"/>')
    if hazard:
        hx, hy, hr = hazard
        out.append(f'<circle cx="{hx}" cy="{hy}" r="{hr}" fill="{LOUD}" opacity="0.14" '
                   f'stroke="{LOUD}" stroke-width="3"/>')
        out.append(f'<rect x="{hx-238:.0f}" y="{hy-hr-46:.0f}" width="476" height="34" '
                   f'fill="{EARTH["ink"]}" opacity="0.7"/>')
        out.append(f'<text x="{hx}" y="{hy-hr-22}" text-anchor="middle" font-family="{FONT}" '
                   f'font-size="20" fill="{LOUD}">hazard band — abstract, not a place</text>')
    for p in state["paths"]:
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in p["trail"][::2])
        inside = hazard and math.hypot(p["pos"][0] - hazard[0], p["pos"][1] - hazard[1]) <= hazard[2]
        col = LOUD if inside else EARTH["foam"]
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2" '
                   f'opacity="{0.85 if inside else 0.45}"/>')
        out.append(f'<circle cx="{p["pos"][0]:.1f}" cy="{p["pos"][1]:.1f}" r="5" fill="{col}" '
                   f'opacity="0.9"/>')
    out.append(f'<text x="40" y="{H-172}" font-family="{FONT}" '
               f'font-size="21" fill="{EARTH["foam"]}" opacity="0.9">'
               f't = {state["t"]:.1f} s, {state["n_paths"]} paths, spread {sp:.1f} px</text>')
    _badge(out, BADGE_FORECAST)
    _frame(out, sourced=False)
    return _close(out)


def render_families(title, sub="", credit=""):
    """The three sound families. The claim is textbook bioacoustics, so this card is SOURCED;
    the drawings are schematic and say so."""
    out = _open()
    _title(out, title, sub)
    rows = [("clicks", "echolocation: short, broadband, in trains", "click"),
            ("whistles", "tonal, continuous, narrowband", "whistle"),
            ("pulsed calls", "rapid pulse trains heard as tone; the catalogued types", "pulsed")]
    y = 190
    for name, desc, kind in rows:
        out.append(f'<rect x="40" y="{y}" width="{W-80}" height="170" fill="{EARTH["deep"]}" '
                   f'opacity="0.42"/>')
        out.append(f'<text x="70" y="{y+46}" font-family="{FONT}" font-size="27" '
                   f'font-weight="bold" fill="{EARTH["foam"]}">{name}</text>')
        out.append(f'<text x="70" y="{y+78}" font-family="{FONT}" font-size="20" '
                   f'fill="{EARTH["foam"]}" opacity="0.78">{desc}</text>')
        bx, by, bw2 = 640, y + 100, W - 720
        if kind == "click":
            for i in range(26):
                x = bx + i * (bw2 / 26)
                out.append(f'<line x1="{x:.1f}" y1="{by-44}" x2="{x:.1f}" y2="{by+16}" '
                           f'stroke="{EARTH["foam"]}" stroke-width="3" opacity="0.9"/>')
        elif kind == "whistle":
            pts = " ".join(f'{bx + i*(bw2/60):.1f},{by - 22 - 20*math.sin(i/60*math.tau*1.1):.1f}'
                           for i in range(61))
            out.append(f'<polyline points="{pts}" fill="none" stroke="{EARTH["foam"]}" stroke-width="4"/>')
        else:
            for i in range(60):
                x = bx + i * (bw2 / 60)
                h2 = 30 + 16 * math.sin(i / 60 * math.tau * 2.0)
                out.append(f'<line x1="{x:.1f}" y1="{by-h2:.1f}" x2="{x:.1f}" y2="{by+8:.1f}" '
                           f'stroke="{EARTH["foam"]}" stroke-width="2" opacity="0.85"/>')
        y += 190
    _credit(out, credit)
    _frame(out, sourced=True)
    return _close(out)


def render_false_positive(det, title, sub=""):
    out = _open()
    _title(out, title, sub)
    x0, x1, base = 70, W - 70, H - 230
    top = 170
    thr_y = base - det["threshold"] * (base - top)
    for e in det["events"]:
        x = x0 + (e["i"] / det["n"]) * (x1 - x0)
        h2 = e["energy"] * (base - top)
        col = (LOUD if e["fired"] and e["kind"] != "call"
               else EARTH["foam"] if e["fired"] else EARTH["light"])
        out.append(f'<line x1="{x:.1f}" y1="{base}" x2="{x:.1f}" y2="{base-h2:.1f}" '
                   f'stroke="{col}" stroke-width="5" opacity="{0.95 if e["fired"] else 0.45}"/>')
    out.append(f'<line x1="{x0}" y1="{thr_y:.1f}" x2="{x1}" y2="{thr_y:.1f}" '
               f'stroke="{EARTH["sand"]}" stroke-width="3" stroke-dasharray="12 8"/>')
    out.append(f'<text x="{x0}" y="{thr_y-12:.1f}" font-family="{FONT}" '
               f'font-size="19" fill="{EARTH["sand"]}">threshold {det["threshold"]:.2f}</text>')
    out.append(f'<text x="40" y="{H-172}" font-family="{FONT}" font-size="23" '
               f'fill="{EARTH["foam"]}">'
               f'{det["true_positive"]} calls caught, {det["false_positive"]} false alarms '
               f'({det["boat_fires"]} of them boats), {det["false_negative"]} calls missed</text>')
    _badge(out)
    _frame(out, sourced=False)
    return _close(out)
