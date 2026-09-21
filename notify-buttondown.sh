#!/usr/bin/env bash
# Post → email. Every published post in posts/*.md that is not yet listed in .buttondown-sent is
# sent once to the Buttondown list (username CloudLabWorks) as a full-text email, then its slug is
# recorded. Runs from deploy.sh after a successful Worker upload; safe to re-run; never re-sends.
#   bash notify-buttondown.sh            send what is unsent
#   bash notify-buttondown.sh --dry-run  list what would be sent
# Key: Bitwarden item "ButtonDown API" (the API key is in its notes; older name "ButtonDown RSS Email"), unlocked with the
# master password stored in the login Keychain (service bitwarden-waku-master, account waku).
# The key is never printed and never lands in git.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
SENT="$DIR/.buttondown-sent"
SITE=https://cloudlabworks.dev
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
touch "$SENT"

# Published posts as slug<TAB>file (same rules as build.mjs: slug from frontmatter or filename; drafts skipped).
list_posts() {
  python3 - "$DIR/posts" <<'EOF'
import os, re, sys
d = sys.argv[1]
for f in sorted(os.listdir(d)):
    if not f.endswith(".md"): continue
    src = open(os.path.join(d, f), encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n?", src, re.S)
    meta = {}
    if m:
        for line in m.group(1).split("\n"):
            k = line.find(":")
            if k > 0: meta[line[:k].strip()] = line[k+1:].strip().strip("\"'")
    if meta.get("draft") == "true": continue
    slug = meta.get("slug") or re.sub(r"\.md$", "", re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f))
    print(f"{slug}\t{f}")
EOF
}

UNSENT=$(list_posts | while IFS=$'\t' read -r slug f; do grep -qx "$slug" "$SENT" || printf '%s\t%s\n' "$slug" "$f"; done)
if [ -z "$UNSENT" ]; then echo "buttondown: nothing new to send"; exit 0; fi
echo "buttondown: unsent:"; printf '%s\n' "$UNSENT" | cut -f1 | sed 's/^/  /'
[ "$DRY" = 1 ] && exit 0

export BW_MASTER_PASSWORD="$(security find-generic-password -a waku -s bitwarden-waku-master -w 2>/dev/null)"
export BW_SESSION="$(bw unlock --passwordenv BW_MASTER_PASSWORD --raw 2>/dev/null)"
unset BW_MASTER_PASSWORD
KEY="$(bw get notes "ButtonDown API" 2>/dev/null | tr -d '[:space:]')"
[ ${#KEY} -ge 20 ] || KEY="$(bw get notes "ButtonDown RSS Email" 2>/dev/null | tr -d '[:space:]')"
unset BW_SESSION
[ ${#KEY} -ge 20 ] || { echo "buttondown: FAIL no API key from Bitwarden"; exit 1; }

printf '%s\n' "$UNSENT" | while IFS=$'\t' read -r slug f; do
  # Body: summary, link to the post, the post itself (markdown; Buttondown renders it), sign-off.
  BODY_JSON=$(python3 - "$DIR/posts/$f" "$slug" "$SITE" <<'EOF'
import json, re, sys
src = open(sys.argv[1], encoding="utf-8").read()
m = re.match(r"^---\n(.*?)\n---\n?(.*)$", src, re.S)
meta, body = {}, src
if m:
    for line in m.group(1).split("\n"):
        k = line.find(":")
        if k > 0: meta[line[:k].strip()] = line[k+1:].strip().strip("\"'")
    body = m.group(2)
url = f"{sys.argv[3]}/{meta.get('section') or 'blog'}/{sys.argv[2]}"
# relative image/link paths on the site become absolute in mail
body = re.sub(r"\]\((/[^)\s]*)\)", lambda mm: f"]({sys.argv[3]}{mm.group(1)})", body)
text = (f"*{meta.get('summary','')}*\n\n" if meta.get("summary") else "") + f"Read on the site: {url}\n\n---\n\n" + body.strip() + \
       f"\n\n---\n\n{meta.get('by','Alex Alvord')}, Cloud Lab Works · Duvall, Washington\n"
print(json.dumps({"subject": meta.get("title", sys.argv[2]), "slug": sys.argv[2], "canonical_url": url,
                  "description": meta.get("summary", ""), "body": text, "status": "about_to_send"}))
EOF
)
  CODE=$(curl -s -o /tmp/bd-send.json -w '%{http_code}' --max-time 40 -X POST https://api.buttondown.com/v1/emails \
    -H "Authorization: Token $KEY" -H 'Content-Type: application/json' -H 'X-Buttondown-Live-Dangerously: true' -d "$BODY_JSON")
  case "$CODE" in
    2*) echo "$slug" >> "$SENT"; echo "buttondown: sent $slug ($CODE)";;
    *)  echo "buttondown: FAIL $slug ($CODE) $(head -c 300 /tmp/bd-send.json)";;
  esac
  rm -f /tmp/bd-send.json
done
unset KEY

# Record what went out so a redeploy never re-sends. Pushed from here because the deploy child runs this.
if ! git -C "$DIR" diff --quiet -- .buttondown-sent; then
  git -C "$DIR" add .buttondown-sent && git -C "$DIR" commit -qm "buttondown: record sent posts" && git -C "$DIR" push -q && echo "buttondown: sent-list committed"
fi
