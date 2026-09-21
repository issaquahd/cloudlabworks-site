#!/usr/bin/env bash
# Export /resume to media/alex-alvord-resume.pdf with the print watermark baked in (headless Chrome).
# Run after build.mjs; deploy-assets.sh then uploads it. Idempotent.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
node build.mjs >/dev/null
(node serve.mjs >/tmp/serve-resume.log 2>&1 &) ; sleep 2
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$DIR/media/alex-alvord-resume.pdf" "http://127.0.0.1:8787/resume" >/dev/null 2>&1
pkill -f "node serve.mjs" >/dev/null 2>&1 || true
[ -s media/alex-alvord-resume.pdf ] && echo "resume pdf: $(wc -c < media/alex-alvord-resume.pdf | tr -d ' ') bytes, $(python3 -c "import re,sys; print(len(re.findall(rb'/Type\s*/Page[^s]', open('media/alex-alvord-resume.pdf','rb').read())))") pages" || { echo "FAIL: pdf not written"; exit 1; }
