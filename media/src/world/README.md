# Code as World, v0.1

One Salish Sea scene represented as executable code, stepped through its own rules, rendered to three frames. Shown on https://cloudlabworks.dev/world.

## Run

    python3 gen.py

Writes `world-01-t0.svg`, `world-02-mid.svg`, `world-03-end.svg`, `set.json` (name, title, caption per frame) and `state.json` (the composition and the final state), and prints the run numbers (ticks, dt, tide, sun angle, canoe drift). Stdlib only. The seed is fixed in `gen.py`; the same seed produces the same world and the same frames. `tools/build-art.sh` at the repo root watermarks the SVGs into `media/art-wm-world-*.jpg`.

## The three parts (`world.py`)

- composition: `compose(seed)`, a list of entities (sun, water, two pieces of land, a canoe, an orca, a heron, three clouds), each with an id, kind, position, size, a few physical numbers where they mean something (mass, buoyancy, drift and swim speeds, tide amplitude and period), and a palette role (earth or loud).
- dynamics: `step(state, dt)`, the rules that move the world, written out as plain code: a sinusoidal tide on the water level, a sun arc, a current that follows the tide and drifts the canoe, an orca that swims and rides a dive cycle, a heron that stays put. No randomness outside the seed.
- appearance: `render(state)`, the state as flat SVG shapes, 1200 x 900, earth tones first and one loud colour (the canoe) against them.

## What this is not

The dynamics are a script, not a solver: every rule is a line you can read, and nothing is integrated, collided or constrained. MuJoCo stays in reserve for the one scene that actually needs a physics solver (something that has to fall, bounce or stack); this scene does not, so it does not get one.
