# Code as World, third run: Beach Cairn (the MuJoCo scene)

Status: spec only, nothing built. This is the scene `/world` has been pointing at since v0.1:
"the one MuJoCo is reserved for, something that has to fall, bounce or stack." Same coastline
as the first world (Salish Sea), same house rule (earth tones, one loud colour), same three-part
split (composition, dynamics, appearance) — but for the first time, dynamics is a solver, not a
script, because a stacked, off-centre stone is exactly the thing a script can't fake: whether it
holds is a real equilibrium question, not a formula you get to write down in advance.

## Why this scene and not another

Every world so far cheats on purpose, by design, stated on the page: the canoe floats because
`buoyancy="floats"` says so; the petals fall on a closed-form curve; nothing touches anything
else and has to hold itself up. A stack of irregular stones is the smallest scene where that
stops being true — contact, friction, gravity and torque all at once, and the honest answer
("does it hold") is not knowable by writing the rule, only by running the physics. It also
closes a loop the site has been carrying since the first commit instead of opening a new one.

## Composition

**Entities** (`compose(seed)`  builds an MJCF model, not a Python dict list this time — the
state now lives in MuJoCo's `mjData`, read back into a small snapshot dict per frame):

| id | what | geometry | approx size | mass |
|---|---|---|---|---|
| `ground` | beach sand, static | plane | — | — |
| `stone-0` (base) | largest, sits on sand | ellipsoid, semi-axes randomized per seed within a range | ~0.34 x 0.26 x 0.22 m | granite density 2700 kg/m³ × volume |
| `stone-1` | mid | ellipsoid | ~0.26 x 0.20 x 0.17 m | ″ |
| `stone-2` | mid, the one likeliest to be the tip point | ellipsoid | ~0.20 x 0.15 x 0.13 m | ″ |
| `stone-3` (top, loud) | smallest, the one loud colour | ellipsoid | ~0.13 x 0.10 x 0.09 m | ″ |
| `shake` | the ground's own slide joint, driven by a scripted position, not simulated — this is the wave | 1-DOF slide (x) | — | — |

Four stones, not more: legible on a 1200x900 canvas at the scale the other worlds use, and
already enough contacts (3 stone-to-stone, 1 stone-to-sand) to make the question real. Each
stone is a MuJoCo ellipsoid with a free joint (6 DOF: it can fall, tip, slide, roll — nothing is
constrained to a plane; this is a real 3D stack, just rendered from one fixed camera angle, same
as the other two worlds render one fixed camera angle onto a flat scene). Ellipsoid, not a
loaded mesh: irregular enough to make balance nontrivial, simple enough that contact geometry
stays a closed-form primitive-primitive problem MuJoCo solves natively, no convex-hull import
step to get wrong.

**Seeded per stone, at compose time**, same discipline as the other two worlds — only placement
noise is randomized, never the physics constants:
- each stone's three semi-axis lengths, `rng.uniform` within a band around the nominal size in
  the table (±15%)
- each stone's placement error on top of its nominal stack position: lateral offset
  `rng.uniform(-0.03, 0.03)` m in x and y, tilt `rng.uniform(-6, 6)` degrees about a random
  horizontal axis — this is the "how well was it actually balanced" the run is testing
- stones start at rest, touching but with zero initial velocity; the first several ticks are the
  settle, not the disturbance

## Dynamics — the part that is finally a solver

`step()` is `mujoco.mj_step(model, data)`, called in a loop; nothing here is a rule I wrote, it
is MuJoCo integrating Newton's laws against the contact constraints. What I do write:

- **Integrator:** `implicitfast`, MuJoCo's recommended default for stacked-contact stability at
  a workable timestep.
- **Timestep:** `dt = 0.002 s` (500 Hz), because contact-rich stacks need a small step to stay
  stable; **this world's `t` is in seconds, not hours** — a different clock than the other two
  worlds, stated plainly on the page, not hidden.
- **Contact:** `friction = "0.9 0.9 0.005"` (high tangential friction, stone-on-stone and
  stone-on-sand, low torsional/rolling), `condim = 4`, `solref`/`solimp` left at MuJoCo defaults
  (soft-but-stiff enough that stones don't visibly interpenetrate at this timestep). Restitution
  effectively zero — stone does not bounce, it either holds or it slides/tips and settles.
- **Gravity:** `-9.81 m/s²`, unmodified — the one constant every other world's water and sun
  numbers already respect (Salish Sea's tide is real M2 physics too, just scripted instead of
  solved).
- **The wave, i.e. the disturbance:** the `shake` slide joint's position is driven directly (a
  `mjtNum` array written into `data.qpos` before each `mj_step`, not a force — this is the one
  place the scene still scripts an input, same as it's fair for an earthquake table to be
  scripted while the building's response is not): a chop riding on a tide, borrowing the Salish
  Sea world's own numbers for continuity rather than inventing new ones —
  `x(t) = 0.004*sin(2*pi*t/4.0) + 0.012*sin(2*pi*t/(12.42*3600)) * min(1, t/8)` in metres: a
  4-second-period wind-chop term at 4 mm amplitude (a plausible small beach wave's horizontal
  surge) plus the real M2 tidal period (12.42 h) at 12 mm amplitude ramped in over the first 8 s
  so the stack isn't hit with a step function at t = 0. The tide term barely moves inside a
  20 s run (it is there for continuity with world 1, not for effect); the chop term is what
  actually tests the stack.
- **Run length:** 20 s of simulated time, 10,000 steps at dt = 0.002 s. First ~3 s is settle
  (disturbance ramping in), remaining ~17 s is the test.
- **Outcome, computed not scripted:** after the run, compare each stone's final centre-of-mass
  height and tilt to its position at t = 3 s (end of settle). A stone that has dropped more than
  half its own height, or tipped past 45°, is recorded as fallen. The frame set and the caption
  report whichever happened — a collapsed cairn is a valid, honestly-reported result, not a bug
  to hide (Article IV: verified failure beats plausible success).

## Appearance — same flat-shape house style, new data source

`render(state)` stays an SVG-shapes function, same 1200x900 canvas, same earth palette, same one
loud colour (the top stone) — visually a sibling of the other two worlds, not a departure. What
changes is where the numbers come from: instead of a hand-written formula, each stone's `(x, z)`
position and its rotation angle in the camera plane come straight out of `mjData.xpos` /
`mjData.xmat` for that body, read after every `mj_step`, projected onto a single fixed
side-on camera (orthographic: drop the world y-axis, i.e. depth, exactly like the Salish Sea
world already renders one fixed view of a 3D-feeling shoreline). No 3D renderer, no lighting
model, no `mujoco.Renderer` / EGL or OSMesa dependency: MuJoCo is used purely as a physics
integrator here, and the picture is drawn by the same flat-shape code path as the other two
worlds. This keeps the whole pipeline headless and dependency-light — `pip install mujoco` is a
pure-Python-plus-native-binary package with no GPU or windowing requirement when you never call
its own renderer.

Draw order: sand (moss/earth-tone beach), the water line behind it reusing the Salish Sea
palette at low tide, then the four stones back-to-front by current world-y (depth) so a stone
that has tipped forward or sideways draws in the right order, each stone an ellipse (its
semi-axes projected through its current rotation) shaded by its `palette` (earth for the base
three, the loud colour for the top stone, unless it has fallen and rolled off the stack, in
which case it's drawn wherever physics put it — the loud colour doesn't get to cheat either).

## Frames and captions

Same convention as the other two worlds: three frames from one run — t = 0 (placed, before the
disturbance ramps in), t ≈ settle end (t = 3 s, the "as-built" baseline the outcome is measured
against), t = 20 s (the result). Caption numbers are `gen.py`'s own measurements: each stone's
drop (m) and tilt (deg) from its t = 3 s baseline, and the plain-language verdict per stone
("held" / "slid Ncm" / "fell"). No adjectives that aren't backed by one of those numbers.

## Determinism

Same house rule as the other worlds: fixed seed → same model → same result, every time. MuJoCo's
own integration is deterministic for a fixed model, fixed initial state and fixed timestep (no
multi-threaded contact solve non-determinism at this scale); `gen.py` will assert this by running
the sim twice from the same seed and diffing the final `qpos` array before writing frames — if
that assertion ever fails, that's a build failure, not a shrug.

## Seed selection — stated up front, not cherry-picked after the fact

The plan is to enumerate seeds 0–19, run the physics for each (headless, no rendering, ~1–2 s of
wall time per run), and record which held and which fell, before choosing which seed ships. The
one that ships is disclosed in `README.md` along with how many of the 20 held, so "this stack
holds" reads as one honestly-selected outcome from a stated population, not a result quietly
re-rolled until it looked good. A seed that collapses is an equally acceptable ship if the
collapse itself is the more interesting frame set — Article IV again: the honest picture, not
the flattering one.

## File layout (once built)

```
media/src/world-stones/
  stones.py     # build_model(seed) -> MJCF XML string; step(model, data, t, dt); render(state)
  gen.py        # seed sweep + the assertion above + writes 3 frames, set.json, state.json
  README.md     # written after the build, same shape as world/README.md and world-kyoto/README.md
```

`build.mjs` gets a third `WORLD_STONES` block in `worldPage()`, `world.html` gets a third
`<h2 id="stones">` section, `tools/build-art.sh` gets a third watermark loop — all three follow
the exact pattern the Kyoto addition just used, no new plumbing invented.

## Build-order checklist (not started; this document is the spec, not the build)

1. `pip install mujoco` (Apache-2.0, no license server, arm64 wheel exists) — pure dependency
   add, reversible, no network calls at runtime once installed.
2. `stones.py`: `build_model(seed)` — string-template the MJCF (ground plane, 4 ellipsoid
   bodies with free joints, the `shake` slide joint, friction/contact settings above).
3. `gen.py`: seed sweep 0–19 headless, print hold/fall per seed, pick and record the shipped
   seed and the reasoning, run the determinism check, render three frames.
4. `render()` in `stones.py`: reuse `poly()`/palette conventions from `world.py`/`kyoto.py`.
5. Wire `build.mjs`, `world.html`, `build-art.sh`; watermark; build; commit; deploy; verify live.
