#!/bin/sh
# build-brand-kit — assemble media/cloudlabworks-brand-kit.zip from the CURRENT marks.
#
# Why this exists: the previous kit was hand-assembled on 09-20 and went stale the next day,
# when the ringed emblem (the official logo) was drawn. A script means the kit is rebuilt from
# source rather than remembered.
#
# Swag is the target, so this is not just a copy of the website's favicons:
#   - vector first (SVG), because print shops re-scale and a 1024 px PNG is only ~3.4 in @300dpi
#   - print-resolution PNGs at 4096 px (~13.6 in @300dpi) with transparency
#   - a one-colour silhouette of the emblem for embroidery and single-screen printing
# Everything is generated from the SVG sources; nothing here is a screenshot.
#
# Usage: tools/build-brand-kit.sh       (writes media/cloudlabworks-brand-kit.zip)
set -eu
DIR="$(cd "$(dirname "$0")/.." && pwd)"
MEDIA="$DIR/media"
SRC="$MEDIA/src"
OUT="$(mktemp -d)"
KIT="$OUT/cloudlabworks-brand-kit"
trap 'rm -rf "$OUT"' EXIT

# Pillow + numpy live in the imgtools venv on this box, not in the system python3.
PY_BIN=""
for c in "$HOME/.local/share/imgtools/bin/python" python3; do
  command -v "$c" >/dev/null 2>&1 || [ -x "$c" ] || continue
  "$c" -c "import PIL, numpy" >/dev/null 2>&1 && { PY_BIN="$c"; break; }
done
[ -n "$PY_BIN" ] || { echo "need a python with Pillow + numpy"; exit 1; }

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "need Google Chrome (renders SVG textPath; librsvg does not)"; exit 1; }



mkdir -p "$KIT/vector" "$KIT/emblem" "$KIT/icon" "$KIT/orca" "$KIT/pattern" "$KIT/print"

say() { printf '  %s\n' "$1"; }

# ---- vector: what a print shop actually wants -------------------------------------------
say "vector"
cp "$MEDIA/cloudlabworks-emblem.svg"  "$KIT/vector/"
cp "$MEDIA/cloudlabworks-icon.svg"    "$KIT/vector/"
cp "$SRC/waku-orca.svg"               "$KIT/vector/"
cp "$SRC/waku-orca-plain.svg"         "$KIT/vector/"
cp "$MEDIA/salish-pattern.svg" "$KIT/vector/"
cp "$MEDIA/wrench-cross.svg" "$KIT/vector/"

# ---- the homepage banner, saved as an actual asset ---------------------------------------
# There is no banner file in the repo: the header lockup is assembled in HTML from the emblem
# SVG, the wrench-cross SVG and LIVE TEXT for "CLOUDLAB WORKS" and the tagline. That is fine
# for a web page and useless for a vendor, who needs one image. Rendered here from the site's
# own _style.css so the spacing and weight match the header rather than being re-guessed.
#
# Chrome headless defaults to dark mode, and _style.css redefines --ink inside a
# prefers-color-scheme:dark block, so the wordmark comes out near-white and invisible on
# light ground unless the variables are pinned. Both inks are produced on purpose: dark for
# light garments, light for dark garments.
say "homepage banner lockup"
mkdir -p "$KIT/banner"
lockup() {  # lockup <ink> <muted> <tagline|""> <out>
  cat > "$OUT/lockup.html" <<EOF
<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="file://$DIR/site/_style.css">
<style>
  :root{--ink:$1;--muted:$2}
  html,body{margin:0;padding:0;background:transparent}
  #wrap{display:inline-block;padding:48px 64px}
  .brand{text-decoration:none}
</style>
<div id="wrap"><a class="brand" href="/"><img class="mark"
 src="file://$MEDIA/cloudlabworks-emblem.svg" width="128" height="128"><span><span
 class="brand-name">CLOUDLAB WORKS<img class="wx" src="file://$MEDIA/wrench-cross.svg"
 width="44" height="44"></span>${3:+<small>$3</small>}</span></a></div>
EOF
  "$CHROME" --headless --disable-gpu --hide-scrollbars \
    --default-background-color=00000000 --window-size=2400,600 --force-device-scale-factor=6 \
    --screenshot="$OUT/raw.png" "file://$OUT/lockup.html" >/dev/null 2>&1
  "$PY_BIN" - "$OUT/raw.png" "$4" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGBA")
bb = im.split()[3].getbbox()          # trim to ink, vendors want no dead margin
im.crop(bb).save(sys.argv[2])
print(f"    {sys.argv[2].split('/')[-1]} {im.crop(bb).size}")
PY
}
TAG="$(grep -o '<small>[^<]*</small>' "$DIR/site/_head.html" | head -1 | sed 's/<[^>]*>//g')"
lockup "#0f172a" "#64748b" "$TAG" "$KIT/banner/cloudlabworks-banner-dark-ink.png"
lockup "#e2e8f0" "#94a3b8" "$TAG" "$KIT/banner/cloudlabworks-banner-light-ink.png"
lockup "#0f172a" "#64748b" ""     "$KIT/banner/cloudlabworks-banner-dark-ink-notagline.png"
lockup "#e2e8f0" "#94a3b8" ""     "$KIT/banner/cloudlabworks-banner-light-ink-notagline.png"

# ---- print-resolution renders, transparent ----------------------------------------------
# Rendered by headless Chrome, NOT rsvg-convert. The emblem sets CLOUDLAB/WORKS on a
# <textPath>, which rsvg silently drops: it produces the ring and the wrench cross with no
# lettering at all. That failure is invisible unless you look at the output, which is exactly
# how a titleless logo reaches a print shop. Chrome renders textPath correctly.
say "print renders (4096 px, headless Chrome)"
render() {  # render <svg> <px> <out>
  cat > "$OUT/wrap.html" <<EOF
<!doctype html><meta charset="utf-8">
<style>html,body{margin:0;padding:0;background:transparent}
img{width:${2}px;height:${2}px;display:block}</style>
<img src="file://$1">
EOF
  "$CHROME" --headless --disable-gpu --hide-scrollbars \
    --default-background-color=00000000 --window-size="$2,$2" \
    --screenshot="$3" "file://$OUT/wrap.html" >/dev/null 2>&1
}
render "$MEDIA/cloudlabworks-emblem.svg" 4096 "$KIT/print/cloudlabworks-emblem-4096.png"
render "$MEDIA/cloudlabworks-icon.svg"   4096 "$KIT/print/cloudlabworks-icon-4096.png"
render "$SRC/waku-orca.svg"              4096 "$KIT/print/waku-orca-4096.png"

# ---- one-colour emblem for embroidery / single-screen ------------------------------------
# Threshold on INK, not on alpha. The emblem has an opaque disc behind it, so an alpha
# silhouette is a filled circle and nothing else -- useless to an embroiderer. Thresholding
# luminance keeps the orca, the ring and the lettering as one ink on a knocked-out ground.
say "one-colour silhouette"
"$PY_BIN" - "$KIT/print/cloudlabworks-emblem-4096.png" "$KIT/print" <<'PY'
import sys
from PIL import Image
import numpy as np
src, outdir = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGBA")
rgba = np.asarray(im).astype(float)
alpha = rgba[..., 3]
# composite over white so the light ground reads as paper, then take the dark parts as ink
comp = rgba[..., :3] * (alpha[..., None] / 255.0) + 255.0 * (1 - alpha[..., None] / 255.0)
lum = comp.mean(axis=2)
ink = (lum < 150) & (alpha > 32)
for name, colour in (("black", (0, 0, 0)), ("white", (255, 255, 255))):
    out = np.zeros(rgba.shape, np.uint8)
    out[..., 0], out[..., 1], out[..., 2] = colour
    out[..., 3] = (ink * 255).astype(np.uint8)
    Image.fromarray(out).resize((2048, 2048), Image.LANCZOS) \
        .save(f"{outdir}/cloudlabworks-emblem-1color-{name}-2048.png")
print(f"    ink coverage {ink.mean()*100:.1f}% of canvas")
PY

# ---- web-size raster sets, copied as-is --------------------------------------------------
say "raster sets"
for f in "$MEDIA"/cloudlabworks-emblem-*.png; do [ -f "$f" ] && cp "$f" "$KIT/emblem/"; done
for f in "$MEDIA"/cloudlabworks-icon-*.png;   do [ -f "$f" ] && cp "$f" "$KIT/icon/";   done
for f in "$MEDIA"/cloudlabworks-ios-*.png;    do [ -f "$f" ] && cp "$f" "$KIT/icon/";   done
for f in "$MEDIA"/waku-orca-*.png;            do [ -f "$f" ] && cp "$f" "$KIT/orca/";   done
# two .ico files exist and they are NOT the same: favicon.ico is the small site one,
# cloudlabworks.ico is the large multi-resolution build. Both ship.
cp "$MEDIA/favicon.ico" "$MEDIA/cloudlabworks.ico" "$KIT/icon/"
cp "$MEDIA/cloudlabworks-avatar-1024.png" "$KIT/orca/"
cp "$MEDIA/cloudlabworks-banner-salish.jpg" "$KIT/pattern/"

# ---- README ------------------------------------------------------------------------------
cat > "$KIT/README.txt" <<'TXT'
CloudLab Works — brand kit
Cloud Lab Works LLC. Generated by tools/build-brand-kit.sh; do not hand-edit this folder.

THE MARK
  The official logo is the ringed emblem: the orca badge inside a white band, CLOUDLAB
  arched above, WORKS arched below, wrench cross at the foot. That is vector/cloudlabworks-emblem.svg.
  The plain orca circle (icon / waku-orca) is a secondary mark and an avatar, not the logo.

WHAT TO SEND A PRINTER
  vector/   SVG. Send this when the vendor can take it.
            WARNING: the emblem's CLOUDLAB / WORKS lettering is LIVE TEXT on an SVG
            <textPath>, set in Futura / Avenir Next. A renderer without textPath support
            drops the lettering entirely (librsvg does exactly this), and a machine without
            those fonts will substitute one. If the vendor's proof comes back with no title,
            or with the title in the wrong face, send print/ instead.
  print/    4096 px PNG, transparent, ~13.6 inches at 300 dpi. Use when SVG is refused.
  banner/   THE HOMEPAGE LOCKUP, saved as an image. The site header has no banner file:
            it is built in HTML from two SVGs plus live text, so this is rendered from the
            site's own stylesheet. dark-ink for light garments, light-ink for dark ones,
            and -notagline variants, which are usually what you want on a hat or a pocket.
            ~10 in wide at 300 dpi.
  print/cloudlabworks-emblem-1color-*.png
            Single-ink silhouette for embroidery and one-screen printing. Use these rather
            than letting a vendor redraw the mark themselves.

BRAND NAME
  Written "CloudLab Works" (one word, capital L) in copy. The legal entity is
  "Cloud Lab Works LLC" and is used where the LLC is named.

COLOUR
  Natural tones with one vibrant colour set against them. The teal variants are the accent;
  do not introduce new accent colours.

OTHER FOLDERS
  emblem/  icon/  orca/   web-sized PNG sets and favicon, as used on cloudlabworks.dev
  pattern/ Coast Salish border band, drawn for this site. Decorative, not a logo.

The artwork is the property of Cloud Lab Works LLC.
TXT

# ---- zip ---------------------------------------------------------------------------------
( cd "$OUT" && zip -qr cloudlabworks-brand-kit.zip cloudlabworks-brand-kit )
mv "$OUT/cloudlabworks-brand-kit.zip" "$MEDIA/cloudlabworks-brand-kit.zip"
echo "wrote media/cloudlabworks-brand-kit.zip ($(du -h "$MEDIA/cloudlabworks-brand-kit.zip" | cut -f1))"
unzip -l "$MEDIA/cloudlabworks-brand-kit.zip" | tail -1
