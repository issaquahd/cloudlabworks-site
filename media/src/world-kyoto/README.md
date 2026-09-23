# Code as World, Kyoto

The second world in the `/world` series: a temple-garden pond scene, cherry tree, torii gate
on the far bank, stone lantern, koi, one afternoon into dusk — represented as executable code
the same way the Salish Sea world is, and shown alongside it on https://cloudlabworks.dev/world.

## Run

    python3 gen.py

Writes `kyoto-01-t0.svg`, `kyoto-02-mid.svg`, `kyoto-03-end.svg`, `set.json` (name, title,
caption per frame) and `state.json` (the composition and the final state), and prints the run
numbers (ticks, dt, sun angle, lantern state, koi position, ripple). Stdlib only. The seed is
fixed in `gen.py`; the same seed produces the same world and the same frames.
`tools/build-art.sh` at the repo root watermarks the SVGs into `media/art-wm-kyoto-*.jpg`.

## The three parts (`kyoto.py`)

- **composition:** `compose(seed)` — a list of entities (sun, hill, pond, cherry tree, torii
  gate, stone lantern, koi, three pines, two clouds, twelve petals), each with an id, kind,
  position, size, and the numbers its own dynamics need (the koi's swim amplitude and period,
  each petal's fall speed, drift speed, flutter and its own fall cycle length), and a palette
  role (earth or loud — the torii is the one loud colour, same house rule as the Salish Sea
  world and `/art`).
- **dynamics:** `step(state, dt)` — a sun arc from sunrise to dusk over a shorter (7 h)
  afternoon; a stone lantern that lights itself once the sun passes a dusk threshold; a koi
  that swims a sinusoidal lane across the pond, its ripple a pure function of how fast it is
  crossing the lane's centre; twelve petals, each a pure function of elapsed time since its own
  last spawn (fall, eastward drift, flutter), recycling on its own fixed cycle. No randomness
  outside the seed, and no randomness at all inside `step` — every petal position at any tick
  is a closed-form function of `t`.
- **appearance:** `render(state)` — the state as flat SVG shapes, 1200 x 900, earth tones
  (moss, stone, pond water, pine, hillside, pale cherry bloom) first, the torii's vermilion the
  one loud colour against them.

## What this is not

Same discipline as the Salish Sea world: the dynamics are a script, not a solver — every rule
is a line you can read, nothing is integrated, collided or constrained. This is still not the
scene MuJoCo is reserved for; nothing here needs to fall, bounce, stack or collide with
anything else. The petals fall, but each one falls by a formula, not a physics step.
