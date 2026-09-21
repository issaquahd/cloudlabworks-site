#!/usr/bin/env bash
# Publish a draft post: flip `draft: true` → published, build, commit, push, deploy (deploy.sh then
# mails the post to the Buttondown list via notify-buttondown.sh). Idempotent: a post that is
# already published just redeploys. Runs on the gateway host (needs the Cloudflare token sentinel
# that deploy.sh uses — so run it from an admitted API-lane session, never from a script payload).
#   bash publish-post.sh posts/2026-09-21-some-post.md
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
F="${1:?usage: publish-post.sh posts/<file>.md}"
case "$F" in /*) ;; *) F="$DIR/$F";; esac
[ -f "$F" ] || { echo "FAIL: $F not found"; exit 1; }
cd "$DIR"

if grep -q '^draft: true$' "$F"; then
  sed -i '' '/^draft: true$/d' "$F"
  echo "publish: draft flag removed from $(basename "$F")"
else
  echo "publish: $(basename "$F") already published; redeploying"
fi

node build.mjs >/dev/null || { echo "FAIL: build"; exit 1; }
SLUG=$(grep -m1 '^slug:' "$F" | sed 's/^slug: *//'); SEC=$(grep -m1 '^section:' "$F" | sed 's/^section: *//'); SEC=${SEC:-blog}
grep -q "\"/$SEC/$SLUG\"" src/worker.js || { echo "FAIL: /$SEC/$SLUG not in the build"; exit 1; }

if ! git diff --quiet -- "$F" src/worker.js; then
  git add "$F" src/worker.js && git commit -qm "Publish: $SLUG" && git push -q && echo "publish: committed and pushed $(git log -1 --format=%h)"
fi

bash "$DIR/deploy.sh"
echo "publish: URL https://cloudlabworks.dev/$SEC/$SLUG"
