#!/usr/bin/env bash
# Render /diagrams: media/src/diagrams/diagrams.py writes the .txt/.mmd sources and set.json; this turns
# each into a watermarked JPEG in media/ (dg-wm-art-<name>.jpg, dg-wm-<name>-ascii.jpg, dg-wm-<name>-mermaid.jpg).
# ASCII → PNG with text2img.py (Menlo on cream); Mermaid → PNG with mermaid-cli in the installed Chrome.
set -u
DIR="$(cd "$(dirname "$0")/.." && pwd)"; SRC="$DIR/media/src/diagrams"; M="$DIR/media"; WM="$DIR/tools/watermark.py"
python3 "$SRC/diagrams.py" || exit 1
PUP="$SRC/puppeteer.json"
[ -f "$PUP" ] || printf '{"executablePath":"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome","args":["--no-sandbox"]}' > "$PUP"
TMP="$(mktemp -d)"
render() { # render PNG OUT-NAME [width]
  local png="$1" out="$M/$2" w="${3:-1600}"
  "$WM" "$png" "$out" --width "$w" >/dev/null && echo "$2"
}
for n in $(python3 -c "import json;print(' '.join(x['name'] for x in json.load(open('$SRC/set.json'))['art']))"); do
  "$DIR/tools/text2img.py" "$SRC/art-$n.txt" "$TMP/art-$n.png" >/dev/null && render "$TMP/art-$n.png" "dg-wm-art-$n.jpg" 1400
done
for n in $(python3 -c "import json;print(' '.join(x['name'] for x in json.load(open('$SRC/set.json'))['blueprints']))"); do
  "$DIR/tools/text2img.py" "$SRC/bp-$n.txt" "$TMP/bp-$n-ascii.png" >/dev/null && render "$TMP/bp-$n-ascii.png" "dg-wm-$n-ascii.jpg" 1600
  npx -y @mermaid-js/mermaid-cli -i "$SRC/bp-$n.mmd" -o "$TMP/bp-$n-mermaid.png" -p "$PUP" -b '#f1e3c3' -w 1400 -s 2 >/dev/null 2>&1 \
    && "$DIR/tools/pad.py" "$TMP/bp-$n-mermaid.png" 80 80 200 80 \
    && render "$TMP/bp-$n-mermaid.png" "dg-wm-$n-mermaid.jpg" 1600 || echo "FAIL mermaid $n"
done
rm -rf "$TMP"
