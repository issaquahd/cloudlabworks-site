#!/usr/bin/env bash
# Deploy cloudlabworks-site Worker + custom domains + Email Routing forward.
# Runs on the OpenClaw gateway host; CLOUDFLARE_API_TOKEN_CLOUDLABWORKS is an
# opaque sentinel substituted by the egress proxy on api.cloudflare.com.
# Never prints the credential. Idempotent: safe to re-run.
set -u
API=https://api.cloudflare.com/client/v4
ZONE=37ae17c6461c5cdc908dd564c361888e
SCRIPT=cloudlabworks-site
# Email Routing (step 4) is one-time setup, done 2026-09-18. Opt in with FWD_TO=<mailbox>; a plain redeploy skips it.
FWD_TO="${FWD_TO:-}"
FWD_ADDR=alex@cloudlabworks.dev
DIR="$(cd "$(dirname "$0")" && pwd)"
AUTH="Authorization: Bearer ${CLOUDFLARE_API_TOKEN_CLOUDLABWORKS:-}"
J='Content-Type: application/json'

say() { printf '%s\n' "$*"; }
cf() { curl -s --max-time 40 -H "$AUTH" "$@"; }
ok() { python3 -c 'import sys,json;d=json.load(sys.stdin);print("ok" if d.get("success") else "FAIL "+json.dumps(d.get("errors"))[:300])'; }

say "== 1. account"
ACCT=$(cf "$API/accounts?per_page=5" | python3 -c 'import sys,json;d=json.load(sys.stdin);r=d.get("result") or [];print(r[0]["id"] if r else "")')
[ -n "$ACCT" ] || { say "FAIL: no account visible to this credential"; exit 1; }
say "account ${ACCT:0:8}…"

say "== 2. worker upload ($SCRIPT)"
# Bindings are replaced wholesale on every upload: the /inquire form needs the send_email binding
# INQUIRY and the var INQUIRY_TO (a verified Email Routing destination; alex@ verified 2026-09-19) on each deploy.
INQUIRY_TO="${INQUIRY_TO:-alex@cloudlabworks.dev}"
META="{\"main_module\":\"worker.js\",\"compatibility_date\":\"2026-09-01\",\"keep_assets\":true,\"bindings\":[{\"type\":\"assets\",\"name\":\"ASSETS\"},{\"type\":\"send_email\",\"name\":\"INQUIRY\"},{\"type\":\"plain_text\",\"name\":\"INQUIRY_TO\",\"text\":\"$INQUIRY_TO\"}]}"
UPLOAD=$(cf -X PUT "$API/accounts/$ACCT/workers/scripts/$SCRIPT" \
  -F "metadata=$META;type=application/json" \
  -F "worker.js=@$DIR/src/worker.js;type=application/javascript+module" | ok); say "$UPLOAD"

say "== 3. custom domains"
for H in cloudlabworks.dev www.cloudlabworks.dev; do
  printf '%s: ' "$H"
  cf -X PUT "$API/accounts/$ACCT/workers/domains" -H "$J" \
    -d "{\"zone_id\":\"$ZONE\",\"hostname\":\"$H\",\"service\":\"$SCRIPT\",\"environment\":\"production\"}" | ok
done

if [ -n "$FWD_TO" ]; then
say "== 4. email routing (forward $FWD_ADDR -> $FWD_TO)"
# 4a. remove the null-MX and SPF -all records so Cloudflare's MX/SPF can take their place
cf "$API/zones/$ZONE/dns_records?per_page=100" | python3 -c '
import sys,json
for r in json.load(sys.stdin).get("result",[]):
    if (r["type"]=="MX" and r["content"]==".") or (r["type"]=="TXT" and r["name"]=="cloudlabworks.dev" and r["content"].strip("\"")=="v=spf1 -all"):
        print(r["id"], r["type"], r["content"])' | while read -r ID T C; do
  printf 'delete %s %s: ' "$T" "$C"; cf -X DELETE "$API/zones/$ZONE/dns_records/$ID" | ok
done
printf 'enable: ';      cf -X POST "$API/zones/$ZONE/email/routing/enable" -H "$J" -d '{}' | ok
# apex MX/SPF/DKIM records are written by /enable; POST /email/routing/dns is for subdomains only (error 2007 otherwise)
printf 'destination: '; cf -X POST "$API/accounts/$ACCT/email/routing/addresses" -H "$J" -d "{\"email\":\"$FWD_TO\"}" | ok
printf 'rule: ';        cf -X POST "$API/zones/$ZONE/email/routing/rules" -H "$J" \
  -d "{\"name\":\"alex forward\",\"enabled\":true,\"matchers\":[{\"type\":\"literal\",\"field\":\"to\",\"value\":\"$FWD_ADDR\"}],\"actions\":[{\"type\":\"forward\",\"value\":[\"$FWD_TO\"]}]}" | ok
else
say "== 4. email routing: skipped (set FWD_TO to run)"
fi

say "== 5. verify"
sleep 20
for U in https://cloudlabworks.dev/ https://cloudlabworks.dev/privacy https://www.cloudlabworks.dev/; do
  printf '%s -> ' "$U"; curl -s -o /dev/null --max-time 20 -w '%{http_code} %{redirect_url}\n' "$U"
done
say "MX:"; dig +short MX cloudlabworks.dev @ashton.ns.cloudflare.com
say "TXT:"; dig +short TXT cloudlabworks.dev @ashton.ns.cloudflare.com
say "routing status:"; cf "$API/zones/$ZONE/email/routing" | python3 -c 'import sys,json;r=json.load(sys.stdin).get("result",{});print(r.get("status"),r.get("enabled"))'

# Infrastructure as Music: the deploy phrase + cue when the worker upload was accepted. Keyed on the API result, not on a
# curl to the public site — from the gateway exec sandbox that curl is a proxy artifact (hosts outside the token's allowlist). Never fails the deploy.
[ "$UPLOAD" = ok ] && { sh /Users/rebl/.openclaw/workspace/ops/iam/play.sh deploy; sh /Users/rebl/.openclaw/workspace/ops/iam/play.sh deploy-cue; } || true
