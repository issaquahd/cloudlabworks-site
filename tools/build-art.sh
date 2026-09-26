#!/usr/bin/env bash
# Render every piece on /art as a watermarked JPEG in media/ (flat, what deploy-assets.sh uploads).
# Sources live under media/src/ and are never uploaded; the site chrome files (orca mark, banner,
# pattern tile, share card, stickers) stay public because the pages need them, but /art shows the
# watermarked copy and links to no source. Idempotent: re-renders only when the source is newer.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"; WM="$DIR/tools/watermark.py"; M="$DIR/media"; S="$M/src"
render() { # render SRC OUT [width]
  local src="$1" out="$M/$2" w="${3:-1600}"
  [ -f "$src" ] || { echo "MISSING $src"; return 1; }
  if [ ! -f "$out" ] || [ "$src" -nt "$out" ] || [ "$WM" -nt "$out" ]; then "$WM" "$src" "$out" --width "$w"; else echo "$2 up to date"; fi
}
# Made here: photographs of the work as it hangs and sits (served originals moved to src/art/served/).
for n in hands-canvas pour-red-drips pour-multicolor fan-and-canvas glass-bowl glass-shelf raku-shelf kabuki-1 kabuki-2 revolutionnaire kimono-scroll pour-verdigris telephone-sunflowers waku-carving; do
  render "$S/art/served/art-$n.jpg" "art-wm-$n.jpg" 1200
done
# Waku art: the Salish Sea set.
for n in salmon raven-sun heron thunderbird-whale welcome-figure canoe; do
  render "$S/salish/salish-$n.svg" "art-wm-salish-$n.jpg" 1024
done
# Waku art: the Japanese set (badges drawn for the household portal; sources copied from alvordhouse-site/media/icons).
# gen.py writes set.json (title, text) and one SVG per motif; the five portal badges are hand files beside them.
for n in okio-ja otto-office takarak-travel osama-finance clw-ledger $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/japanese/set.json"))))'); do
  render "$S/japanese/$n.svg" "art-wm-jp-$n.jpg" 1024
done
# Waku art: the garden set (thirty generated scenes; gen.py writes set.json and garden-NN.svg).
for n in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/gardens/set.json"))))'); do
  render "$S/gardens/$n.svg" "art-wm-$n.jpg" 1200
done
# Waku art: friends and family (thirty-one more chibi characters; family.py writes the SVGs, headless Chrome the PNGs).
for n in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/agents/family.json"))))'); do
  render "$S/agents/family-$n.png" "art-wm-family-$n.jpg" 1024
done
# Waku art: the Matrix set (Kyoto and Tokyo scenes as digital rain; gen.py writes set.json and matrix-NN.png).
for n in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/matrix/set.json"))))'); do
  render "$S/matrix/$n.png" "art-wm-$n.jpg" 1200
done
# Waku art: the Ronin set (samurai and masterless swordsmen as digital rain; same renderer as the
# Matrix set, figures instead of architecture; gen.py writes set.json and ronin-NN.png).
for n in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/ronin/set.json"))))'); do
  render "$S/ronin/$n.png" "art-wm-$n.jpg" 1200
done
# Waku art: the agents set (six chibi characters; gen.py writes the SVGs, headless Chrome renders the PNGs because the captions are text).
for n in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/agents/set.json"))))'); do
  render "$S/agents/agent-$n.png" "art-wm-agent-$n.jpg" 1024
done
# Waku art: the site set.
render "$S/portrait/alex-three-ways.jpg" art-wm-alex-three-ways.jpg 1600
render "$M/waku-orca-pale.svg" art-wm-orca-mark.jpg 1024
render "$M/cloudlabworks-banner-salish.jpg" art-wm-salish-band.jpg 1600
render "$M/salish-pattern-alpha.svg" art-wm-watermark-tile.jpg 1024
render "$M/waku-orca-og.png" art-wm-share-card.jpg 1200
# Waku art: pop art (Japanese pop-art register: Warhol repetition, Ben-day dots, rising sun,
# ukiyo-e wave, kumadori face paint; gen.py writes set.json and popart-NAME.svg).
for n in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/popart/set.json"))))'); do
  render "$S/popart/popart-$n.svg" "art-wm-popart-$n.jpg" 1600
done
# Waku art: Kisetsu, the seasons set (30 pieces: twelve Acer cultivars, ten flowering cherries,
# eight steam pools; hand-written SVG in the same pop register as popart/). Names in set.json
# already carry the kisetsu- prefix.
for n in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/kisetsu/set.json"))))'); do
  render "$S/kisetsu/$n.svg" "art-wm-$n.jpg" 1600
done
# Code as World: one world as code, three frames from one seed (gen.py writes set.json, state.json and world-NN-*.svg).
for n in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/world/set.json"))))'); do
  render "$S/world/$n.svg" "art-wm-$n.jpg" 1200
done
# Code as World, Kyoto: the second world (gen.py writes set.json, state.json and kyoto-NN-*.svg).
for n in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/world-kyoto/set.json"))))'); do
  render "$S/world-kyoto/$n.svg" "art-wm-$n.jpg" 1200
done
# Code as Nature: the estate as a pod, Reynolds steering over the published roster
# (gen.py writes set.json, state.json and nature-NN-*.svg).
for n in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/nature/set.json"))))'); do
  render "$S/nature/$n.svg" "art-wm-$n.jpg" 1200
done
# Code as Bioacoustics: what a call is, and where the pod goes next (gen.py writes set.json,
# state.json and orca-NN-*.svg). Two treatments, both drawn INTO the SVG: a solid sand edge on
# the two SOURCED cards, a loud dashed edge plus the ILLUSTRATIVE badge on the other eight. The
# badge has to survive a crop and a repost, so it is rendered, never captioned.
for n in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open("'"$S"'/orca/set.json"))))'); do
  render "$S/orca/$n.svg" "art-wm-$n.jpg" 1200
done
