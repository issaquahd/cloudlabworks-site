# cloudlabworks.dev

Landing page for Cloud Lab Works LLC. Three pages (`/`, `/privacy`, `/terms`), one Cloudflare
Worker, zero external requests (inline CSS, system fonts, no analytics).

- Edit `site/*.html` and `site/_style.css`; `node build.mjs` regenerates `src/worker.js`.
- Deploy: `npx wrangler deploy` (custom domains in `wrangler.jsonc`), or upload `src/worker.js`
  via the API. Local check: `node serve.mjs` → http://127.0.0.1:8787.
