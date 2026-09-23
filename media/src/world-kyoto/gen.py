#!/usr/bin/env python3
"""Seed the Kyoto world, step it, write three frames. Run: python3 gen.py

Writes kyoto-01-t0.svg, kyoto-02-mid.svg, kyoto-03-end.svg, set.json (name, title, text per
frame) and state.json (the composition, then the final state). Prints the run numbers; the
page quotes those, not typed values.
"""
import copy, json, os
import kyoto

HERE = os.path.dirname(os.path.abspath(__file__))
SEED, TICKS, DT = 11, 140, 0.05        # 140 ticks of 3 minutes: 7 hours, sunrise to dusk
FRAMES = {0: ("kyoto-01-t0", "Frame 1, tick 0"), TICKS // 2: ("kyoto-02-mid", "Frame 2, mid run"), TICKS: ("kyoto-03-end", "Frame 3, end of run")}


def snapshot(state):
    koi = kyoto.get(state, "koi")
    return dict(tick=state["tick"], t_h=round(state["t"], 3), sun_angle_deg=round(state["sun_angle_deg"], 2),
                lantern_lit=state["lantern_lit"], koi_x=round(koi["pos"][0], 1), koi_y=round(koi["pos"][1], 1),
                ripple_amp=round(state["ripple_amp"], 2))


def main():
    state = kyoto.compose(SEED)
    composition = copy.deepcopy(state["entities"])   # the world as composed, before any tick
    snaps, pieces = {}, []
    for tick in range(TICKS + 1):
        if tick:
            kyoto.step(state, DT)
        if tick in FRAMES:
            name, title = FRAMES[tick]
            open(os.path.join(HERE, f"{name}.svg"), "w").write(kyoto.render(state))
            snaps[tick] = snapshot(state)
            pieces.append(dict(name=name, title=title, tick=tick))
    first = snaps[0]
    for p in pieces:
        s = snaps[p["tick"]]
        lit = "lit" if s["lantern_lit"] else "unlit"
        if p["tick"] == 0:
            p["text"] = (f"t = {s['t_h']:.1f} h, tick {s['tick']} of {TICKS}. Sun at {s['sun_angle_deg']:.1f} degrees on the arc, "
                         f"the lantern {lit}, the koi at x = {s['koi_x']:.0f} px, ripple {s['ripple_amp']:.1f} px.")
        else:
            p["text"] = (f"t = {s['t_h']:.1f} h, tick {s['tick']} of {TICKS}. Sun reached {s['sun_angle_deg']:.1f} degrees "
                         f"(from {first['sun_angle_deg']:.1f}), the lantern is {lit}, the koi at x = {s['koi_x']:.0f} px, ripple {s['ripple_amp']:.1f} px.")
    json.dump(pieces, open(os.path.join(HERE, "set.json"), "w"), indent=0, ensure_ascii=False)
    json.dump(dict(seed=SEED, ticks=TICKS, dt_h=DT, composition=composition, frames=snaps, final_state=snapshot(state)),
              open(os.path.join(HERE, "state.json"), "w"), indent=2)
    print(f"seed {SEED}, {TICKS} ticks, dt {DT} h, run {TICKS * DT:.2f} h")
    for tick, s in snaps.items():
        print(f"tick {tick:3d}: t {s['t_h']:.2f} h  sun {s['sun_angle_deg']:.2f} deg  lantern {'lit' if s['lantern_lit'] else 'unlit'}  koi x {s['koi_x']:.1f} y {s['koi_y']:.1f}  ripple {s['ripple_amp']:.2f} px")


if __name__ == "__main__":
    main()
