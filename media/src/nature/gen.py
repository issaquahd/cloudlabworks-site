#!/usr/bin/env python3
"""Seed the pod from the published roster, step it, write three frames. Run: python3 gen.py

Reads media/iam-state.json -- the SAME file the /live page polls -- so the organisms are the
estate, not a fixture. Writes nature-01-t0.svg, nature-02-mid.svg, nature-03-end.svg,
set.json (name, title, text per frame) and state.json (roster, composition, final state).
Prints the run numbers; the page quotes those, never typed values.
"""
import copy, json, os
import nature

HERE = os.path.dirname(os.path.abspath(__file__))
FEED = os.path.normpath(os.path.join(HERE, "..", "..", "iam-state.json"))
SEED, TICKS, DT = 1, 240, 0.08      # 240 ticks of 80 ms: 19.2 s of world time, long enough
                                     # for the pod to find each other from a scattered start
FRAMES = {0: ("nature-01-t0", "Frame 1, tick 0"),
          TICKS // 2: ("nature-02-mid", "Frame 2, mid run"),
          TICKS: ("nature-03-end", "Frame 3, end of run")}


def snapshot(state):
    return dict(tick=state["tick"], t_s=round(state["t"], 3),
                cohesion_px=round(nature.cohesion_px(state), 1),
                organisms=[dict(id=o["id"], kind=o["kind"], ok=o["ok"],
                                x=round(o["pos"][0], 1), y=round(o["pos"][1], 1),
                                speed=round((o["vel"][0] ** 2 + o["vel"][1] ** 2) ** 0.5, 1))
                           for o in state["organisms"]])


def check(state):
    """Assert the invariants per tick, not per published frame. The /world orca wrapped at
    tick 59 of 60 and the teleport sat between frames 2 and 3 for a week."""
    for o in state["organisms"]:
        assert o["size"] - 0.5 <= o["pos"][0] <= nature.W - o["size"] + 0.5, f'{o["id"]} left the tank in x'
        assert o["size"] - 0.5 <= o["pos"][1] <= nature.H - o["size"] + 0.5, f'{o["id"]} left the tank in y'
        assert (o["vel"][0] ** 2 + o["vel"][1] ** 2) ** 0.5 <= nature.MAX_SPEED + 1e-6, f'{o["id"]} exceeded MAX_SPEED'


def main():
    feed = json.load(open(FEED))
    roster = feed.get("sites") or []
    if not roster:
        raise SystemExit(f"{FEED} has no 'sites' roster -- run ops/iam/publish.sh first")
    events = [e for e in feed.get("events", []) if e.get("kind") == "deploy"]

    state = nature.compose(roster, events, seed=SEED)
    first = copy.deepcopy(state)
    frames, shots = [], [snapshot(state)]

    if 0 in FRAMES:
        name, title = FRAMES[0]
        open(os.path.join(HERE, name + ".svg"), "w").write(nature.render(state, title))
        frames.append((name, title, 0))

    for i in range(1, TICKS + 1):
        nature.step(state, DT)
        check(state)
        if i in FRAMES:
            name, title = FRAMES[i]
            open(os.path.join(HERE, name + ".svg"), "w").write(nature.render(state, title))
            frames.append((name, title, i))
            shots.append(snapshot(state))

    start_coh = shots[0]["cohesion_px"]
    end_coh = shots[-1]["cohesion_px"]
    live = sum(1 for o in state["organisms"] if o["ok"])
    sick = len(state["organisms"]) - live

    # state.json / set.json shapes match media/src/world so build.mjs and tools/build-art.sh
    # read them the same way: set.json is a flat array of frame cards, state.json carries the
    # composition, a frames map keyed by tick, and final_state.
    by_tick = {str(s["tick"]): s for s in shots}
    json.dump(dict(seed=SEED, ticks=TICKS, dt_s=DT,
                   feed_generated=feed.get("generated"), feed_state=feed.get("state"),
                   roster=roster, composition=first["organisms"],
                   frames=by_tick, final_state=shots[-1]),
              open(os.path.join(HERE, "state.json"), "w"), indent=2)

    def caption(tick):
        s = by_tick[str(tick)]
        live_n = sum(1 for o in s["organisms"] if o["ok"])
        sick_n = len(s["organisms"]) - live_n
        together = ("scattered" if s["cohesion_px"] > 120 else
                    "closing" if s["cohesion_px"] > 60 else "together")
        return (f't = {s["t_s"]:.1f} s, tick {tick} of {TICKS}. '
                f'{live_n} answering, {sick_n} not. '
                f'Mean distance from the healthy centroid {s["cohesion_px"]:.1f} px: {together}.')

    json.dump([dict(name=n, title=t, tick=k, text=caption(k)) for n, t, k in frames],
              open(os.path.join(HERE, "set.json"), "w"), indent=2)

    print(f"seed={SEED} ticks={TICKS} dt={DT}s ({TICKS*DT:.1f}s of world time)")
    print(f"population={len(state['organisms'])} ({live} answering, {sick} not) from {len(roster)} roster rows")
    print(f"cohesion {start_coh} px -> {end_coh} px")
    print(f"feed generated {feed.get('generated')}, state {feed.get('state')}")


if __name__ == "__main__":
    main()
