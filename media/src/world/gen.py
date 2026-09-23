#!/usr/bin/env python3
"""Seed the world, step it, write three frames. Run: python3 gen.py

Writes world-01-t0.svg, world-02-mid.svg, world-03-end.svg, set.json (name, title, text per
frame) and state.json (the composition, then the final state). Prints the run numbers; the
page quotes those, not typed values.
"""
import copy, json, os
import world

HERE = os.path.dirname(os.path.abspath(__file__))
SEED, TICKS, DT = 7, 180, 0.05        # 180 ticks of 3 minutes: nine hours, which runs past the
                                      # 6.21 h tide turn so the current reverses inside the run
FRAMES = {0: ("world-01-t0", "Frame 1, tick 0"), TICKS // 2: ("world-02-mid", "Frame 2, mid run"), TICKS: ("world-03-end", "Frame 3, end of run")}


def snapshot(state):
    return dict(tick=state["tick"], t_h=round(state["t"], 3), tide_m=round(state["tide_m"], 3),
                water_y=round(state["water_y"], 1), sun_angle_deg=round(state["sun_angle_deg"], 2),
                canoe_x=round(world.get(state, "canoe")["pos"][0], 1), canoe_drift_px=round(world.get(state, "canoe")["drift_px"], 1),
                orca_x=round(world.get(state, "orca")["pos"][0], 1), orca_depth_m=round(world.get(state, "orca")["depth_m"], 2),
                orca_surfaced=world.get(state, "orca")["surfaced"], heron_x=round(world.get(state, "heron")["pos"][0], 1))


def check(state, prev_orca_x):
    """Per-tick invariants. Checked on every tick, not on the three published frames:
    a discontinuity between samples is invisible to a frame-by-frame look, which is how
    the orca's modular wrap sat between frames 2 and 3 on the live page for a week.

    1. the heron's feet stay above the water line (it is standing on a rock, not wading)
    2. the orca moves at most its swim speed per tick (a wrap or a teleport fails here)
    """
    heron, orca = world.get(state, "heron"), world.get(state, "orca")
    clearance = state["water_y"] - heron["pos"][1]
    if clearance < 0:
        raise SystemExit(f"INVARIANT: heron underwater at tick {state['tick']}, "
                         f"clearance {clearance:.1f} px. Raise the rock or lower the tide.")
    step_px = abs(orca["pos"][0] - prev_orca_x)
    if step_px > orca["swim_px_per_h"] * state["dt"] + 1e-6:
        raise SystemExit(f"INVARIANT: orca moved {step_px:.1f} px in one tick at "
                         f"tick {state['tick']}, above its swim speed. That is a teleport.")
    return clearance


def main():
    state = world.compose(SEED)
    composition = copy.deepcopy(state["entities"])   # the world as composed, before any tick
    snaps, pieces = {}, []
    min_clearance, prev_orca_x = float("inf"), world.get(state, "orca")["pos"][0]
    for tick in range(TICKS + 1):
        if tick:
            world.step(state, DT)
            min_clearance = min(min_clearance, check(state, prev_orca_x))
            prev_orca_x = world.get(state, "orca")["pos"][0]
        if tick in FRAMES:
            name, title = FRAMES[tick]
            open(os.path.join(HERE, f"{name}.svg"), "w").write(world.render(state))
            snaps[tick] = snapshot(state)
            pieces.append(dict(name=name, title=title, tick=tick))
    first = snaps[0]
    for p in pieces:
        s = snaps[p["tick"]]
        if p["tick"] == 0:
            p["text"] = (f"t = {s['t_h']:.1f} h, tick {s['tick']} of {TICKS}. Low water: tide {s['tide_m']:+.2f} m, sun on the horizon at {s['sun_angle_deg']:.1f} degrees, "
                         f"the canoe at x = {s['canoe_x']:.0f} px before any drift, the orca surfaced, the heron on the rock.")
        else:
            orca = "is surfaced" if s["orca_surfaced"] else "is %.1f m down" % s["orca_depth_m"]
            p["text"] = (f"t = {s['t_h']:.1f} h, tick {s['tick']} of {TICKS}. The tide rose {s['tide_m'] - first['tide_m']:.2f} m to {s['tide_m']:+.2f} m, the sun reached {s['sun_angle_deg']:.1f} degrees, "
                         f"the canoe drifted {s['canoe_drift_px']:.0f} px east on the flood, the orca {orca}, the heron has not moved.")
    json.dump(pieces, open(os.path.join(HERE, "set.json"), "w"), indent=0, ensure_ascii=False)
    json.dump(dict(seed=SEED, ticks=TICKS, dt_h=DT, composition=composition, frames=snaps, final_state=snapshot(state)),
              open(os.path.join(HERE, "state.json"), "w"), indent=2)
    print(f"seed {SEED}, {TICKS} ticks, dt {DT} h, run {TICKS * DT:.2f} h")
    for tick, s in snaps.items():
        print(f"tick {tick:3d}: t {s['t_h']:.2f} h  tide {s['tide_m']:+.3f} m  water_y {s['water_y']:.1f}  sun {s['sun_angle_deg']:.2f} deg  canoe x {s['canoe_x']:.1f} (drift {s['canoe_drift_px']:+.1f} px)  orca x {s['orca_x']:.1f} depth {s['orca_depth_m']:.2f} m surfaced={s['orca_surfaced']}  heron x {s['heron_x']:.1f}")
    print(f"final: tide {state['tide_m']:+.3f} m (rose {state['tide_m'] - first['tide_m']:.3f} m), sun {state['sun_angle_deg']:.2f} deg, canoe drift {world.get(state, 'canoe')['drift_px']:+.1f} px")
    print(f"invariants: {TICKS} ticks checked, tightest heron clearance {min_clearance:.1f} px above the water line")


if __name__ == "__main__":
    main()
