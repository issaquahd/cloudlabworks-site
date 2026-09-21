# cloudlabworks.dev

Source for [cloudlabworks.dev](https://cloudlabworks.dev) — Cloud Lab Works LLC.

Landing page for Cloud Lab Works LLC. Pages `/`, `/work`, `/inquire`, `/privacy`, `/terms`, plus the blog **Invisible Wires: Agentic Cloud** at `/blog` (posts, `/blog/<slug>`, `/blog/feed.xml`), one Cloudflare
Worker, zero external requests (inline CSS, system fonts, no analytics).

- Edit `site/*.html` and `site/_style.css`; `node build.mjs` regenerates `src/worker.js`.
- Deploy: `npx wrangler deploy` (custom domains in `wrangler.jsonc`), or upload `src/worker.js`
  via the API (`deploy.sh`, passes `keep_assets`). Local check: `node serve.mjs` → http://127.0.0.1:8787.
- Media: files in `media/` are served at `/media/<name>` as Workers Static Assets (free, no R2).
  `deploy-assets.sh` uploads them and redeploys the Worker; run it whenever `media/` changes.
  Video: H.264 + AAC, `-movflags +faststart`, poster JPEG alongside.

## Inquiry form (`/inquire`)

`site/inquire.html` is rendered at runtime (values echoed back on a validation error). A POST
validates (name, email, category from `CATEGORIES` in `build.mjs`; honeypot + 3-second timing
check), builds a plain-text RFC 5322 message and sends it through the Worker's `send_email`
binding `INQUIRY` to the var `INQUIRY_TO`, with `Reply-To` set to the visitor. `INQUIRY_TO`
must be a **verified Email Routing destination address** (sends to those are free on every
plan); an unverified address fails at send time. Both scripts pass the binding and the var on
every upload because the API replaces bindings wholesale — a deploy without them turns the form
into a 503. `node serve.mjs` prints the message instead of sending.

## Blog posts

Drop a Markdown file in `posts/` named `YYYY-MM-DD-slug.md`:

```
---
title: The post title
date: 2026-09-18
time: 09:00             # optional, orders same-day posts
by: Alex Alvord            # or "Waku", or "Alex Alvord and Waku"
summary: One sentence shown in the index, home page, and RSS.
draft: false               # true keeps it out of the build
---

Body in Markdown: headings (##), paragraphs, lists, **bold**, *italic*, `code`,
fenced code blocks, > quotes, [links](https://example.com), ---.
```

Then `node build.mjs` and deploy. The newest three posts appear on the home page.

## GitHub contribution graphs

`/work` shows the contribution calendars for `@issaquahd` and `@CloudLabWorks` as inline SVG.
`node fetch-github.mjs` pulls the public calendars into `data/github.json` (no token, no
runtime requests from the site); `node build.mjs` renders them. Re-run the fetch before a
deploy to refresh the numbers.
