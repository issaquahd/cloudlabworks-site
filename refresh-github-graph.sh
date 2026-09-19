#!/usr/bin/env bash
# Weekly refresh: re-fetch GitHub contribution data, rebuild, upload the Worker only.
# Does NOT touch DNS, custom domains, or Email Routing (deploy.sh steps 3-4) — those are
# one-time config, not part of a routine content refresh.
# Runs on the OpenClaw gateway host; CLOUDFLARE_API_TOKEN_CLOUDLABWORKS is an opaque
# sentinel substituted by the egress proxy on api.cloudflare.com. Never prints it.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

say() { printf '%s\n' "$*"; }
AUTH="Authorization: Bearer ${CLOUDFLARE_API_TOKEN_CLOUDLABWORKS:-}"
ok() { python3 -c 'import sys,json;d=json.load(sys.stdin);print("ok" if d.get("success") else "FAIL "+json.dumps(d.get("errors"))[:300])'; }

say "== 1. fetch github data"
node fetch-github.mjs issaquahd CloudLabWorks || { say "FAIL: fetch-github.mjs"; exit 1; }

say "== 2. build"
node build.mjs || { say "FAIL: build.mjs"; exit 1; }

if git diff --quiet -- data/github.json src/worker.js; then
  say "== 3. no change since last run, skipping upload+commit"
  exit 0
fi

say "== 3. account"
ACCT=$(curl -s --max-time 20 -H "$AUTH" "https://api.cloudflare.com/client/v4/accounts?per_page=5" | python3 -c 'import sys,json;d=json.load(sys.stdin);r=d.get("result") or [];print(r[0]["id"] if r else "")')
[ -n "$ACCT" ] || { say "FAIL: no account visible to this credential"; exit 1; }
say "account ${ACCT:0:8}…"

say "== 4. worker upload"
curl -s --max-time 40 -H "$AUTH" -X PUT "https://api.cloudflare.com/client/v4/accounts/$ACCT/workers/scripts/cloudlabworks-site" \
  -F 'metadata={"main_module":"worker.js","compatibility_date":"2026-09-01","keep_assets":true};type=application/json' \
  -F "worker.js=@$DIR/src/worker.js;type=application/javascript+module" | ok

say "== 5. commit"
git add data/github.json src/worker.js
git commit -q -m "data: weekly github graph refresh $(date -u +%Y-%m-%d)"
say "committed $(git rev-parse --short HEAD)"
