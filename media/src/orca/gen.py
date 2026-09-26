#!/usr/bin/env python3
"""Render the /orca set, then write what the page is allowed to quote. Run: python3 gen.py

Ten cards: 4 call catalogue, 4 forecast, 2 bioacoustics. Writes orca-01..orca-10 .svg,
set.json (name, title, group, treatment, text per card) and state.json (every parameter and
every measured number). build.mjs reads only those two files, so the page cannot state a
number this program did not produce -- same contract as media/src/world and media/src/nature.

Two cards carry the SOURCED treatment (a solid sand edge, a credit strip): the repertoire
matrix and the three-sound-families card, both of which rest on published work that is named
on the card. The other eight carry the ILLUSTRATIVE badge burned into the frame. Blur the
text on any card and the edge still tells you which kind it is -- that is the test.
"""
import json, os
import orca

HERE = os.path.dirname(os.path.abspath(__file__))
TICKS, DT = 300, 0.1          # 30 s of world time
FRAMES = {0: "orca-05-forecast-t0", TICKS // 2: "orca-06-forecast-mid", TICKS: "orca-07-forecast-end"}
HAZARD = (860.0, 360.0, 150.0)   # abstract band, deliberately not a map of anywhere

FORD = ["Repertoire structure after Ford's catalogue of resident killer whale",
        "call types. This matrix is synthesised. Not affiliated with SFU or HALLO."]
FAMILIES = ["Standard bioacoustic taxonomy; the source-identification framing is",
            "HALLO's (orca.research.sfu.ca). Drawings schematic. Not affiliated."]


def write(name, svg):
    open(os.path.join(HERE, name + ".svg"), "w").write(svg)


def main():
    cards, state = [], {}

    # ---------------------------------------------------------- call catalogue (4)
    c1 = orca.call_contour(seed=101)
    c2 = orca.call_contour(seed=102)
    c3 = orca.call_contour(seed=103)
    c4 = orca.call_contour(seed=104)
    fam = [c1, c2, c3, c4]

    write("orca-01-call-contour", orca.render_contour(
        c1, "One call, drawn as a contour",
        "frequency over time on a log axis — the shape is what a call type is"))
    cards.append(dict(
        name="orca-01-call-contour", title="One call, drawn as a contour",
        group="Call catalogue", treatment="illustrative",
        text=(f'Onset {c1["f_onset"]:.0f} Hz, plateau {c1["f_plateau"]:.0f} Hz with a '
              f'{c1["wobble_hz"]:.1f} Hz wobble at {c1["wobble_frac"]*100:.1f}% depth, terminal '
              f'{c1["f_terminal"]:.0f} Hz, over {c1["dur_s"]:.1f} s. Synthesised from seed '
              f'{c1["seed"]}; a real catalogued type is defined by a shape like this one, '
              f'not by this one.')))

    write("orca-02-call-family", orca.render_family(
        fam, "Four types, side by side",
        "discrete, because the shapes do not blend into each other"))
    spans = [abs(c["f_plateau"] - c["f_terminal"]) for c in fam]
    cards.append(dict(
        name="orca-02-call-family", title="Four types, side by side",
        group="Call catalogue", treatment="illustrative",
        text=(f'Four contours from seeds {fam[0]["seed"]}–{fam[-1]["seed"]}. Plateau-to-terminal '
              f'drop ranges {min(spans):.0f}–{max(spans):.0f} Hz across the set. Discreteness is '
              f'the claim worth keeping: types are countable, which is what makes acoustic '
              f'identification possible at all.')))

    rep = orca.compose_repertoire(seed=7)
    write("orca-03-repertoire", orca.render_repertoire(
        rep, "Who uses which type", "overlapping but distinct repertoires", credit=FORD))
    cards.append(dict(
        name="orca-03-repertoire", title="Who uses which type",
        group="Call catalogue", treatment="sourced",
        text=(f'{len(rep["labels"])} groups × {len(rep["names"])} types, seed {rep["seed"]}: '
              f'{rep["shared"]} type(s) used by every group, {rep["unique"]} held by exactly one. '
              f'The idea that pods hold overlapping-but-distinct repertoires is Ford’s and is '
              f'credited on the card; this particular matrix is program output.')))

    d = orca.contour_distance(c1, c2)
    d_self = orca.contour_distance(c1, c1)
    write("orca-04-call-match", orca.render_match(
        c1, c2, d, "Same type, or not?",
        "mean separation in octaves — the arithmetic under the intuition"))
    cards.append(dict(
        name="orca-04-call-match", title="Same type, or not?",
        group="Call catalogue", treatment="illustrative",
        text=(f'Contour 101 against contour 102: {d:.3f} octaves mean separation, against '
              f'{d_self:.3f} for a contour matched with itself. A real classifier does far more '
              f'than this — HALLO’s is a neural one — but this is the quantity the intuition '
              f'is reaching for.')))

    state["calls"] = dict(
        contours={f'seed-{c["seed"]}': {k: v for k, v in c.items() if k != "points"} for c in fam},
        distance_101_102_octaves=round(d, 4), distance_self_octaves=round(d_self, 4),
        repertoire=dict(seed=rep["seed"], labels=rep["labels"], names=rep["names"],
                        grid=rep["grid"], shared=rep["shared"], unique=rep["unique"]))

    # ---------------------------------------------------------- forecast (4)
    st = orca.compose_paths(n_paths=24, seed=3)
    shots = {}

    def shot(s):
        cx, cy = orca.centroid(s)
        return dict(tick=s["tick"], t_s=round(s["t"], 2), spread_px=round(orca.spread_px(s), 1),
                    centroid=[round(cx, 1), round(cy, 1)],
                    in_hazard=sum(1 for p in s["paths"]
                                  if ((p["pos"][0] - HAZARD[0]) ** 2 +
                                      (p["pos"][1] - HAZARD[1]) ** 2) ** 0.5 <= HAZARD[2]))

    def check(s):
        for p in s["paths"]:
            assert 39.5 <= p["pos"][0] <= orca.W - 39.5, "a path left the channel in x"
            assert 39.5 <= p["pos"][1] <= orca.H - 39.5, "a path left the channel in y"

    shots[0] = shot(st)
    write(FRAMES[0], orca.render_paths(
        st, "Tick 0: everything starts in one place",
        "24 paths, identical initial condition"))
    for i in range(1, TICKS + 1):
        orca.step(st, DT)
        check(st)
        if i in FRAMES:
            shots[i] = shot(st)
            sub = ("the O-U pull holds the heading; the noise spreads the ensemble"
                   if i < TICKS else "the spread IS the forecast")
            write(FRAMES[i], orca.render_paths(
                st, f"Tick {i}: {'mid run' if i < TICKS else 'end of run'}", sub))

    for i, name in FRAMES.items():
        s = shots[i]
        cards.append(dict(
            name=name, title=("Tick 0: everything starts in one place" if i == 0
                              else f"Tick {i}: {'mid run' if i < TICKS else 'end of run'}"),
            group="Forecast", treatment="illustrative",
            text=(f't = {s["t_s"]:.1f} s, tick {i} of {TICKS}. Ensemble spread '
                  f'{s["spread_px"]:.1f} px around a centroid at '
                  f'({s["centroid"][0]:.0f}, {s["centroid"][1]:.0f}). '
                  f'θ = {orca.THETA}, σ = {orca.SIGMA}, preferred cruise '
                  f'{orca.MU_SPEED} px/s, heading blend {orca.W_PERSIST}/{orca.W_PREFER}.')))

    write("orca-08-ship-strike", orca.render_paths(
        st, "The same ensemble, against a hazard band",
        "why anyone forecasts a whale in the first place", hazard=HAZARD))
    final = shot(st)
    cards.append(dict(
        name="orca-08-ship-strike", title="The same ensemble, against a hazard band",
        group="Forecast", treatment="illustrative",
        text=(f'{final["in_hazard"]} of {st["n_paths"]} paths end inside the band at t = '
              f'{final["t_s"]:.1f} s. The band is a circle on an empty field on purpose: it is '
              f'not a channel, not a shipping lane, not a map of anywhere. The output of a real '
              f'system is a probability over a real place, and this is not one.')))

    state["forecast"] = dict(
        theta=orca.THETA, sigma=orca.SIGMA, mu_speed=orca.MU_SPEED,
        w_persist=orca.W_PERSIST, w_prefer=orca.W_PREFER,
        seed=st["seed"], n_paths=st["n_paths"], ticks=TICKS, dt_s=DT,
        hazard=dict(x=HAZARD[0], y=HAZARD[1], r=HAZARD[2]),
        frames={str(k): v for k, v in shots.items()}, final_state=final)

    # ---------------------------------------------------------- bioacoustics (2)
    write("orca-09-sound-families", orca.render_families(
        "Three families of sound", "clicks, whistles, pulsed calls", credit=FAMILIES))
    cards.append(dict(
        name="orca-09-sound-families", title="Three families of sound",
        group="Bioacoustics", treatment="sourced",
        text=('Clicks for echolocation, whistles for tonal contact, pulsed calls for the '
              'catalogued repertoire. Standard taxonomy, credited on the card; the drawings '
              'are schematic, and the source-identification framing is HALLO’s. '
              'Not affiliated with SFU or HALLO.')))

    det = orca.naive_detector(seed=5)
    write("orca-10-false-positive", orca.render_false_positive(
        det, "The rule that looked fine", "loud in band ⇒ whale"))
    cards.append(dict(
        name="orca-10-false-positive", title="The rule that looked fine",
        group="Bioacoustics", treatment="illustrative",
        text=(f'{det["n"]} synthetic events at threshold {det["threshold"]:.2f}: '
              f'{det["true_positive"]} calls caught, {det["false_positive"]} false alarms of which '
              f'{det["boat_fires"]} are boats, {det["false_negative"]} calls missed. A boat is loud '
              f'in band too. This is the card that replaced a confusion matrix, because a matrix '
              f'reads as a result no matter what the caption underneath it says.')))

    state["detector"] = {k: v for k, v in det.items() if k != "events"}

    # ---------------------------------------------------------- write the contract
    state["badges"] = dict(forecast=list(orca.BADGE_FORECAST), synthetic=list(orca.BADGE_SYNTH))
    state["credits"] = dict(ford=" ".join(FORD), families=" ".join(FAMILIES))
    state["counts"] = dict(total=len(cards),
                           call_catalogue=sum(1 for c in cards if c["group"] == "Call catalogue"),
                           forecast=sum(1 for c in cards if c["group"] == "Forecast"),
                           bioacoustics=sum(1 for c in cards if c["group"] == "Bioacoustics"),
                           sourced=sum(1 for c in cards if c["treatment"] == "sourced"),
                           illustrative=sum(1 for c in cards if c["treatment"] == "illustrative"))

    assert state["counts"]["total"] == 10, state["counts"]
    assert state["counts"]["call_catalogue"] == 4 and state["counts"]["forecast"] == 4 \
        and state["counts"]["bioacoustics"] == 2, state["counts"]

    json.dump(cards, open(os.path.join(HERE, "set.json"), "w"), indent=2)
    json.dump(state, open(os.path.join(HERE, "state.json"), "w"), indent=2)

    print(f'{state["counts"]["total"]} cards: {state["counts"]["call_catalogue"]} call catalogue, '
          f'{state["counts"]["forecast"]} forecast, {state["counts"]["bioacoustics"]} bioacoustics')
    print(f'{state["counts"]["sourced"]} sourced, {state["counts"]["illustrative"]} illustrative')
    print(f'forecast: seed={st["seed"]} {st["n_paths"]} paths, {TICKS} ticks x {DT}s '
          f'({TICKS*DT:.0f}s), spread {shots[0]["spread_px"]} -> {final["spread_px"]} px, '
          f'{final["in_hazard"]} in the band')
    print(f'calls: 101 vs 102 = {d:.3f} octaves, self = {d_self:.3f}')
    print(f'detector: {det["true_positive"]} TP, {det["false_positive"]} FP '
          f'({det["boat_fires"]} boats), {det["false_negative"]} FN')


if __name__ == "__main__":
    main()
