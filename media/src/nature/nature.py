#!/usr/bin/env python3
"""Code as Nature, v0.1: the estate as a small living pod.

Three parts, named the way world.py names them:
  composition  what is alive (one organism per probe row in the published roster)
  dynamics     step(state, dt): Reynolds steering -- separation, alignment, cohesion
  appearance   render(state) -> SVG: flat shapes, 1200 x 900, earth tones plus one loud colour

The rules are Craig Reynolds' three, written out as plain lines you can read (Boids, SIGGRAPH
'87; The Nature of Code ch. 5). Nothing here is a physics engine and nothing is a neural
network yet -- neuroevolution is ch. 11 and a later rung.

THE POPULATION IS THE ESTATE, NOT A NUMBER I PICKED. One organism per row in
media/iam-state.json's roster. Today that is a very small pod, because the estate is small.
It grows when the estate grows, and that honesty is the point: the piece is not decorated
with extra creatures to look busier than the lab is.

Units: t in seconds of world time, lengths in pixels. Stdlib only.
"""
import math, random

W, H = 1200, 900

# earth tones first, then one loud colour placed against them (house rule, same as /world)
EARTH = dict(deep="#1a2c29", water="#2f4a45", mid="#4a6b63", light="#7d8a86",
             silt="#6b4f36", sand="#8a7357", foam="#f2ebdc", ink="#141414")
LOUD = "#e0472c"        # a sick organism, and nothing else


# ---------------------------------------------------------------- composition
def compose(roster, events, seed=11):
    """One organism per roster row. Seed places them; health comes from the feed."""
    rng = random.Random(seed)
    organisms = []
    for i, site in enumerate(roster):
        # a host with sub-checks carries them as extra, smaller organisms of the same body
        kids = list((site.get("checks") or {}).keys())
        organisms.append(dict(
            id=site["name"], kind="adult", ok=bool(site.get("ok", True)),
            pos=[rng.uniform(300, 900), rng.uniform(300, 600)],
            vel=[rng.uniform(-30, 30), rng.uniform(-30, 30)],
            size=26.0, phase=rng.uniform(0, math.tau),
        ))
        for k in kids:
            c = site["checks"][k]
            organisms.append(dict(
                id=f'{site["name"]}/{k}', kind="juvenile", ok=bool(c.get("ok", True)),
                pos=[rng.uniform(300, 900), rng.uniform(300, 600)],
                vel=[rng.uniform(-30, 30), rng.uniform(-30, 30)],
                size=15.0, phase=rng.uniform(0, math.tau),
            ))
    return dict(
        t=0.0, tick=0, seed=seed,
        organisms=organisms,
        blooms=[dict(at=e.get("at", ""), age=0.0) for e in events[:3]],
        palette="earth",
    )


# ---------------------------------------------------------------- dynamics
# Perception radii. Reynolds' defaults assume a crowd; this pod is the size of the estate.
# At a 150 px cohesion radius two organisms that drift apart are past each other's perception
# and NEVER reunite -- the run ends with the flock permanently dissolved, which is a lie about
# a healthy estate. The radius spans most of the tank so a small pod stays a pod.
SEP_R, ALI_R, COH_R = 80.0, 420.0, 420.0
MARGIN = 170.0          # steer away from the glass before reaching it
MAX_SPEED, MAX_FORCE = 78.0, 42.0


def _limit(v, m):
    n = math.hypot(*v)
    return [v[0] * m / n, v[1] * m / n] if n > m and n else v


def _steer(o, desired):
    """Reynolds: steering = desired - current, clamped. The one line the whole chapter is."""
    n = math.hypot(*desired)
    if not n:
        return [0.0, 0.0]
    desired = [desired[0] * MAX_SPEED / n, desired[1] * MAX_SPEED / n]
    return _limit([desired[0] - o["vel"][0], desired[1] - o["vel"][1]], MAX_FORCE)


def step(state, dt):
    """Separation, alignment, cohesion. A sick organism does not align or cohere: it keeps
    separation only, so a fault reads as the pod coming apart rather than as a red dot."""
    orgs = state["organisms"]
    for o in orgs:
        sep = [0.0, 0.0]; ali = [0.0, 0.0]; coh = [0.0, 0.0]
        n_sep = n_ali = n_coh = 0
        for p in orgs:
            if p is o:
                continue
            dx, dy = p["pos"][0] - o["pos"][0], p["pos"][1] - o["pos"][1]
            d = math.hypot(dx, dy) or 1e-6
            if d < SEP_R:
                sep[0] -= dx / d / d; sep[1] -= dy / d / d; n_sep += 1
            if d < ALI_R and p["ok"]:
                ali[0] += p["vel"][0]; ali[1] += p["vel"][1]; n_ali += 1
            if d < COH_R and p["ok"]:
                coh[0] += p["pos"][0]; coh[1] += p["pos"][1]; n_coh += 1

        acc = [0.0, 0.0]
        if n_sep:
            s = _steer(o, sep)
            acc[0] += s[0] * 1.6; acc[1] += s[1] * 1.6          # separation always applies
        if o["ok"]:
            if n_ali:
                a = _steer(o, [ali[0] / n_ali, ali[1] / n_ali])
                acc[0] += a[0] * 1.0; acc[1] += a[1] * 1.0
            if n_coh:
                c = _steer(o, [coh[0] / n_coh - o["pos"][0], coh[1] / n_coh - o["pos"][1]])
                acc[0] += c[0] * 0.9; acc[1] += c[1] * 0.9
        else:
            # sick: drifts, slows, sinks a little. No alignment, no cohesion.
            acc[1] += 9.0
            o["vel"][0] *= 0.995; o["vel"][1] *= 0.995

        # Boundary avoidance. Without it a pod of two parks against a wall: cohesion pulls
        # each toward the other and nothing pushes either off the edge, so the run ends with
        # both sitting on the silt. Reynolds steers away from the margin before reaching it.
        if o["ok"]:
            want = [0.0, 0.0]
            if o["pos"][0] < MARGIN:          want[0] = MAX_SPEED
            elif o["pos"][0] > W - MARGIN:    want[0] = -MAX_SPEED
            if o["pos"][1] < MARGIN:          want[1] = MAX_SPEED
            elif o["pos"][1] > H - MARGIN:    want[1] = -MAX_SPEED
            if want[0] or want[1]:
                b = _steer(o, want)
                acc[0] += b[0] * 2.2; acc[1] += b[1] * 2.2

        o["vel"] = _limit([o["vel"][0] + acc[0] * dt, o["vel"][1] + acc[1] * dt], MAX_SPEED)
        o["pos"][0] += o["vel"][0] * dt
        o["pos"][1] += o["vel"][1] * dt
        o["phase"] += dt * 2.2

        # the frame is a tank, not a torus: reflect, so nothing teleports between frames
        # (the /world orca taught us that a modular wrap hides the discontinuity in the gap)
        for k, hi in ((0, W), (1, H)):
            if o["pos"][k] < o["size"]:
                o["pos"][k] = o["size"]; o["vel"][k] = abs(o["vel"][k])
            elif o["pos"][k] > hi - o["size"]:
                o["pos"][k] = hi - o["size"]; o["vel"][k] = -abs(o["vel"][k])

    for b in state["blooms"]:
        b["age"] += dt
    state["t"] += dt
    state["tick"] += 1
    return state


def cohesion_px(state):
    """Mean distance from the healthy centroid: the number the page quotes for 'together'."""
    live = [o for o in state["organisms"] if o["ok"]]
    if len(live) < 2:
        return 0.0
    cx = sum(o["pos"][0] for o in live) / len(live)
    cy = sum(o["pos"][1] for o in live) / len(live)
    return sum(math.hypot(o["pos"][0] - cx, o["pos"][1] - cy) for o in live) / len(live)


# ---------------------------------------------------------------- appearance
def _body(o):
    a = math.atan2(o["vel"][1], o["vel"][0])
    s = o["size"]
    fill = LOUD if not o["ok"] else EARTH["ink"]
    belly = EARTH["foam"] if o["ok"] else EARTH["sand"]
    tail = math.sin(o["phase"]) * s * 0.32
    return (
        f'<g transform="translate({o["pos"][0]:.1f},{o["pos"][1]:.1f}) '
        f'rotate({math.degrees(a):.1f})" opacity="{0.95 if o["ok"] else 0.6:.2f}">'
        f'<ellipse rx="{s:.1f}" ry="{s*0.44:.1f}" fill="{fill}"/>'
        f'<ellipse cx="{-s*0.1:.1f}" cy="{s*0.16:.1f}" rx="{s*0.62:.1f}" ry="{s*0.17:.1f}" fill="{belly}"/>'
        f'<path d="M{-s:.1f},0 L{-s*1.5:.1f},{tail-s*0.3:.1f} L{-s*1.5:.1f},{tail+s*0.3:.1f} Z" fill="{fill}"/>'
        f'<circle cx="{s*0.55:.1f}" cy="{-s*0.1:.1f}" r="{max(1.4, s*0.09):.1f}" fill="{EARTH["foam"]}"/>'
        f'</g>')


def render(state, title=""):
    live = sum(1 for o in state["organisms"] if o["ok"])
    sick = len(state["organisms"]) - live
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
    out.append(f'<defs><linearGradient id="col" x1="0" y1="0" x2="0" y2="1">'
               f'<stop offset="0" stop-color="{EARTH["mid"]}"/>'
               f'<stop offset="1" stop-color="{EARTH["deep"]}"/></linearGradient></defs>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#col)"/>')
    # silt floor, drawn from the same seed so the ground is part of the composition
    rng = random.Random(state["seed"])
    pts = " ".join(f"{x},{H-60-rng.uniform(0,44):.0f}" for x in range(0, W + 1, 60))
    out.append(f'<polyline points="0,{H} {pts} {W},{H}" fill="{EARTH["silt"]}" opacity="0.75"/>')
    # a bloom per recent deploy event, expanding and fading
    for b in state["blooms"]:
        r = 40 + b["age"] * 46
        op = max(0.0, 0.5 - b["age"] * 0.1)
        if op > 0.01:
            out.append(f'<circle cx="{W*0.5:.0f}" cy="{H*0.42:.0f}" r="{r:.0f}" fill="none" '
                       f'stroke="{EARTH["foam"]}" stroke-width="2" opacity="{op:.2f}"/>')
    for o in state["organisms"]:
        out.append(_body(o))
    out.append(f'<text x="28" y="{H-28}" font-family="Helvetica,Arial,sans-serif" font-size="22" '
               f'fill="{EARTH["foam"]}" opacity="0.8">{title}</text>')
    out.append(f'<text x="{W-28}" y="{H-28}" text-anchor="end" font-family="Helvetica,Arial,sans-serif" '
               f'font-size="22" fill="{EARTH["foam"]}" opacity="0.6">'
               f'{live} answering, {sick} not</text>')
    out.append('</svg>')
    return "\n".join(out)
