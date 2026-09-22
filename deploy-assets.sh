#!/usr/bin/env bash
# Upload media/* as Workers Static Assets and redeploy src/worker.js with them attached.
# /media/* runs the Worker first (run_worker_first) so it can answer Range requests via the ASSETS
# binding — WebKit needs 206s to seek/loop video; everything else is served by the platform. Runs on the OpenClaw gateway host; the token is an opaque
# sentinel substituted by the egress proxy. Never prints the credential. Idempotent.
#
# Flow (developers.cloudflare.com/workers/static-assets/direct-upload):
#   1. POST assets-upload-session with a manifest {path: {hash, size}}  -> upload JWT + buckets
#   2. POST assets/upload?base64=true per bucket, Bearer = upload JWT   -> completion JWT
#   3. PUT the script with metadata.assets.jwt = completion JWT
# deploy.sh (no assets) passes keep_assets=true so a plain redeploy keeps what is uploaded here.
set -u
API=https://api.cloudflare.com/client/v4
SCRIPT=cloudlabworks-site
DIR="$(cd "$(dirname "$0")" && pwd)"
# src/worker.js is generated from site/*.html; always rebuild first or a text change ships stale (09-21 lesson).
(cd "$DIR" && node build.mjs >/dev/null) || { echo "build.mjs failed"; exit 1; }
AUTH="Authorization: Bearer ${CLOUDFLARE_API_TOKEN_CLOUDLABWORKS:-}"
J='Content-Type: application/json'
say() { printf '%s\n' "$*"; }
cf() { curl -s --max-time 120 -H "$AUTH" "$@"; }
hash_of() { shasum -a 256 "$1" | cut -c1-32; }
file_of() { for F in "$DIR"/media/*; do [ -f "$F" ] && [ "$(hash_of "$F")" = "$1" ] && { echo "$F"; return; }; done; }
mime() { case "$1" in *.mp4) echo video/mp4;; *.webm) echo video/webm;; *.jpg|*.jpeg) echo image/jpeg;; *.png) echo image/png;; *.svg) echo image/svg+xml;; *.gif) echo image/gif;; *.m4a) echo audio/mp4;; *.json) echo application/json;; *) echo application/octet-stream;; esac; }

say "== 1. account"
ACCT=$(cf "$API/accounts?per_page=5" | python3 -c 'import sys,json;d=json.load(sys.stdin);r=d.get("result") or [];print(r[0]["id"] if r else "")')
[ -n "$ACCT" ] || { say "FAIL: no account visible to this credential"; exit 1; }
say "account ${ACCT:0:8}…"

say "== 2. manifest (media/*)"
MANIFEST="{"; SEP=""
for F in "$DIR"/media/*; do
  [ -f "$F" ] || continue
  N=$(basename "$F"); H=$(hash_of "$F"); S=$(stat -f %z "$F")
  MANIFEST="$MANIFEST$SEP\"/media/$N\":{\"hash\":\"$H\",\"size\":$S}"; SEP=","
  say "/media/$N $S B $H"
done
MANIFEST="$MANIFEST}"
SESSION=$(cf -X POST "$API/accounts/$ACCT/workers/scripts/$SCRIPT/assets-upload-session" -H "$J" -d "{\"manifest\":$MANIFEST}")
python3 -c 'import sys,json;d=json.load(sys.stdin);print("session ok" if d.get("success") else "FAIL "+json.dumps(d.get("errors"))[:300])' <<<"$SESSION"
JWT=$(python3 -c 'import sys,json;print(json.load(sys.stdin)["result"].get("jwt",""))' <<<"$SESSION")
[ -n "$JWT" ] || { say "FAIL: no upload jwt"; exit 1; }
BUCKETS=$(python3 -c 'import sys,json;[print(" ".join(b)) for b in json.load(sys.stdin)["result"].get("buckets") or []]' <<<"$SESSION")

say "== 3. upload"
COMPLETION="$JWT"
if [ -z "$BUCKETS" ]; then say "nothing new to upload; session jwt is the completion jwt"; fi
while read -r BUCKET; do
  [ -n "$BUCKET" ] || continue
  ARGS=(); TMP=()
  for H in $BUCKET; do
    SRC=$(file_of "$H"); [ -n "$SRC" ] || { say "FAIL: no file for hash $H"; exit 1; }
    B64=$(mktemp); base64 -i "$SRC" | tr -d '\n' > "$B64"; TMP+=("$B64")
    ARGS+=(-F "$H=<$B64;type=$(mime "$SRC")")
  done
  RESP=$(curl -s --max-time 300 -X POST "$API/accounts/$ACCT/workers/assets/upload?base64=true" -H "Authorization: Bearer $JWT" "${ARGS[@]}")
  rm -f "${TMP[@]}"
  python3 -c 'import sys,json;d=json.load(sys.stdin);print("bucket ok" if d.get("success") else "FAIL "+json.dumps(d.get("errors"))[:300])' <<<"$RESP"
  C=$(python3 -c 'import sys,json;print((json.load(sys.stdin).get("result") or {}).get("jwt") or "")' <<<"$RESP")
  [ -n "$C" ] && COMPLETION="$C"
done <<<"$BUCKETS"

say "== 4. worker upload with assets"
# Bindings are replaced on every upload — carry the ASSETS binding (Range on /media/*), the /inquire email binding + recipient var (see deploy.sh).
INQUIRY_TO="${INQUIRY_TO:-alex@cloudlabworks.dev}"   # must be a verified Email Routing destination
cf -X PUT "$API/accounts/$ACCT/workers/scripts/$SCRIPT" \
  -F "metadata={\"main_module\":\"worker.js\",\"compatibility_date\":\"2026-09-01\",\"assets\":{\"jwt\":\"$COMPLETION\",\"config\":{\"not_found_handling\":\"none\",\"run_worker_first\":[\"/media/*\"]}},\"bindings\":[{\"type\":\"assets\",\"name\":\"ASSETS\"},{\"type\":\"send_email\",\"name\":\"INQUIRY\"},{\"type\":\"plain_text\",\"name\":\"INQUIRY_TO\",\"text\":\"$INQUIRY_TO\"}]};type=application/json" \
  -F "worker.js=@$DIR/src/worker.js;type=application/javascript+module" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("deploy ok" if d.get("success") else "FAIL "+json.dumps(d.get("errors"))[:300])' | tee /tmp/deploy-assets.result
# Infrastructure as Music: deploy phrase + cue when the upload was accepted. Never fails the deploy.
grep -q '^deploy ok$' /tmp/deploy-assets.result && { sh /Users/rebl/.openclaw/workspace/ops/iam/play.sh deploy; sh /Users/rebl/.openclaw/workspace/ops/iam/play.sh deploy-cue; } || true

say "== 5. verify"
sleep 15
for U in https://cloudlabworks.dev/ https://cloudlabworks.dev/media/cloud-magician.mp4 https://cloudlabworks.dev/media/cloud-magician-poster.jpg; do
  printf '%s -> ' "$U"; curl -s -o /dev/null --max-time 30 -w '%{http_code} %{content_type} %{size_download}B\n' "$U"
done
