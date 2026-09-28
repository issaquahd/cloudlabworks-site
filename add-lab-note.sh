#!/usr/bin/env bash
# Insert one dated Lab log entry at the top of /notes, rebuild, commit, push, deploy.
# Idempotent: a second run for the same date replaces that day's entry rather than stacking.
#   bash add-lab-note.sh 2026-09-27 "Two or three sentences of prose."
# Runs on the OpenClaw gateway host (deploy.sh needs the Cloudflare sentinel).
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
DATE="${1:?usage: add-lab-note.sh YYYY-MM-DD \"text\"}"
TEXT="${2:?usage: add-lab-note.sh YYYY-MM-DD \"text\"}"
F="$DIR/site/notes.html"
[ -f "$F" ] || { echo "FAIL: $F missing"; exit 1; }

case "$DATE" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;; *) echo "FAIL: bad date $DATE"; exit 1;; esac
PRETTY=$(date -j -f %Y-%m-%d "$DATE" "+%B %-d, %Y" 2>/dev/null) || { echo "FAIL: bad date $DATE"; exit 1; }

python3 - "$F" "$DATE" "$PRETTY" "$TEXT" <<'PY'
import html, re, sys
path, date, pretty, text = sys.argv[1:5]
s = open(path).read()
# Drop an existing Lab log entry for this date so re-runs replace instead of stacking.
s = re.sub(r'\n  <article class="note lab-log">\s*\n    <p class="meta"><time datetime="%s">.*?</article>\n' % re.escape(date),
           '\n', s, flags=re.S)
paras = "\n".join('      <p>%s</p>' % html.escape(p.strip())
                  for p in text.split("\n\n") if p.strip())
block = (
  '\n  <article class="note lab-log">\n'
  '    <p class="meta"><time datetime="%s">%s</time> · Lab log</p>\n'
  '%s\n'
  '    <p class="tag">Generated from the homelab\'s own daily record.</p>\n'
  '  </article>\n' % (date, pretty, paras)
)
i = s.find('  <article class="note">')
if i == -1:
    print("FAIL: no existing note block to anchor against"); sys.exit(1)
open(path, "w").write(s[:i] + block.lstrip('\n') + s[i:])
print("note: inserted %s" % date)
PY
[ $? -eq 0 ] || { echo "FAIL: insert"; exit 1; }

node build.mjs >/dev/null || { echo "FAIL: build"; exit 1; }
grep -q 'lab-log' src/worker.js || { echo "FAIL: entry not in build"; exit 1; }

if ! git diff --quiet -- site/notes.html src/worker.js; then
  git add site/notes.html src/worker.js
  git commit -qm "notes: lab log $DATE" && git push -q && echo "note: pushed $(git log -1 --format=%h)"
fi

bash "$DIR/deploy.sh" || { echo "FAIL: deploy"; exit 1; }
echo "note: live https://cloudlabworks.dev/notes"
