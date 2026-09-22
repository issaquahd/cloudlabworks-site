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
for n in hands-canvas pour-red-drips pour-multicolor fan-and-canvas glass-bowl glass-shelf raku-shelf kabuki-1 kabuki-2 revolutionnaire kimono-scroll pour-verdigris telephone-sunflowers; do
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
