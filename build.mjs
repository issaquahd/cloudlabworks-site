// Builds src/worker.js from site/*.html and posts/*.md. No runtime dependencies.
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
const r = (p) => readFileSync(new URL(`./site/${p}`, import.meta.url), "utf8");
const style = r("_style.css").trim(), head = r("_head.html").trim(), foot = r("_foot.html").trim();
const fill = (html) => html.replace("{{STYLE}}", style).replace("{{HEAD}}", head).replace("{{FOOT}}", foot);
const page = (f) => fill(r(f));

// ---------- blog: Invisible Wires — Agentic Cloud ----------
const BLOG = { title: "Invisible Wires — Agentic Cloud", path: "/blog", desc: "Notes from a home lab on agentic operations, hybrid multicloud, and the wires nobody sees. By Alex Alvord and Waku." };
const SITE = "https://cloudlabworks.dev";
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// Minimal Markdown: headings, paragraphs, lists, fenced code, blockquotes, hr, images (own line → figure), links, bold, italic, inline code.
function inline(s) {
  const codes = [];
  s = s.replace(/`([^`]+)`/g, (_, c) => { codes.push(`<code>${esc(c)}</code>`); return `\u0000${codes.length - 1}\u0000`; });
  s = esc(s)
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, t, u) => `<a href="${u}"${/^https?:/.test(u) ? ' rel="noopener"' : ""}>${t}</a>`)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*\w])\*([^*\n]+)\*(?!\w)/g, "$1<em>$2</em>");
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => codes[+i]);
}
function markdown(src) {
  const lines = src.replace(/\r/g, "").split("\n"), out = [];
  let i = 0;
  const para = [];
  const flush = () => { if (para.length) { out.push(`<p>${inline(para.join(" "))}</p>`); para.length = 0; } };
  while (i < lines.length) {
    const l = lines[i];
    if (/^```/.test(l)) { flush(); const lang = l.slice(3).trim(); const buf = []; i++; while (i < lines.length && !/^```/.test(lines[i])) buf.push(lines[i++]); i++; out.push(`<pre><code${lang ? ` class="lang-${esc(lang)}"` : ""}>${esc(buf.join("\n"))}</code></pre>`); continue; }
    const h = /^(#{1,4})\s+(.*)$/.exec(l);
    if (h) { flush(); const n = Math.max(2, h[1].length); out.push(`<h${n}>${inline(h[2])}</h${n}>`); i++; continue; }
    if (/^(-{3,}|\*{3,})\s*$/.test(l)) { flush(); out.push("<hr>"); i++; continue; }
    const im = /^!\[([^\]]*)\]\(([^)\s]+)\)\s*$/.exec(l);
    if (im) { flush(); const cap = im[1] ? `<figcaption>${inline(im[1])}</figcaption>` : ""; out.push(`<figure><img src="${im[2]}" alt="${esc(im[1])}" loading="lazy" decoding="async">${cap}</figure>`); i++; continue; }
    if (/^>\s?/.test(l)) { flush(); const buf = []; while (i < lines.length && /^>\s?/.test(lines[i])) buf.push(lines[i++].replace(/^>\s?/, "")); out.push(`<blockquote>${markdown(buf.join("\n"))}</blockquote>`); continue; }
    if (/^\s*[-*]\s+/.test(l)) { flush(); const buf = []; while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) buf.push(`<li>${inline(lines[i++].replace(/^\s*[-*]\s+/, ""))}</li>`); out.push(`<ul>${buf.join("")}</ul>`); continue; }
    if (/^\s*\d+\.\s+/.test(l)) { flush(); const buf = []; while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) buf.push(`<li>${inline(lines[i++].replace(/^\s*\d+\.\s+/, ""))}</li>`); out.push(`<ol>${buf.join("")}</ol>`); continue; }
    if (/^\s*$/.test(l)) { flush(); i++; continue; }
    para.push(l.trim()); i++;
  }
  flush();
  return out.join("\n");
}
function frontmatter(src) {
  const m = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/.exec(src);
  if (!m) return [{}, src];
  const meta = {};
  for (const line of m[1].split("\n")) { const k = line.indexOf(":"); if (k > 0) meta[line.slice(0, k).trim()] = line.slice(k + 1).trim().replace(/^["']|["']$/g, ""); }
  return [meta, m[2]];
}
const fmtDate = (d) => new Date(d + "T12:00:00Z").toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });

const postsDir = new URL("./posts/", import.meta.url);
let posts = [];
try {
  posts = readdirSync(postsDir).filter((f) => f.endsWith(".md")).map((f) => {
    const [meta, body] = frontmatter(readFileSync(new URL(f, postsDir), "utf8"));
    const slug = meta.slug || f.replace(/^\d{4}-\d{2}-\d{2}-/, "").replace(/\.md$/, "");
    const date = meta.date || f.slice(0, 10);
    if (!meta.title) throw new Error(`posts/${f}: missing title`);
    if (meta.draft === "true") return null;
    return { slug, date, sort: `${date}T${meta.time || "00:00"}`, title: meta.title, summary: meta.summary || "", by: meta.by || "Alex Alvord", html: markdown(body) };
  }).filter(Boolean).sort((a, b) => (a.sort === b.sort ? 0 : a.sort < b.sort ? 1 : -1));
} catch (e) { if (e.code !== "ENOENT") throw e; }

const shell = ({ title, desc, path, body, cls = "post", noindex = false, extraHead = "" }) => fill(`<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
${noindex ? '<meta name="robots" content="noindex">' : ""}
<link rel="canonical" href="${SITE}${path}">
<link rel="alternate" type="application/rss+xml" title="${esc(BLOG.title)}" href="${BLOG.path}/feed.xml">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${SITE}${path}">
${extraHead}
<style>{{STYLE}}</style>
</head>
<body>
{{HEAD}}
<main class="${cls}">
${body}
</main>
{{FOOT}}
</body>
</html>
`);

const postItem = (p) => `    <li><time datetime="${p.date}">${fmtDate(p.date)}</time><b><a href="${BLOG.path}/${p.slug}">${esc(p.title)}</a></b><span>${esc(p.summary)}</span></li>`;
const emptyItem = `    <li><b>First post is on its way.</b><span><a href="${BLOG.path}/feed.xml">Subscribe to the feed</a> and it will find you.</span></li>`;

const blogIndex = shell({
  title: `${BLOG.title} — Cloud Lab Works`, desc: BLOG.desc, path: BLOG.path, cls: "blog",
  body: `  <h1>Invisible Wires<small>Agentic Cloud</small></h1>
  <p class="lede">${esc(BLOG.desc)}</p>
  <p class="tag"><a href="${BLOG.path}/feed.xml">RSS feed</a></p>
  <ul class="plain posts">
${posts.length ? posts.map(postItem).join("\n") : emptyItem}
  </ul>`,
});
const postPages = Object.fromEntries(posts.map((p) => [`${BLOG.path}/${p.slug}`, shell({
  title: `${p.title} — ${BLOG.title}`, desc: p.summary || BLOG.desc, path: `${BLOG.path}/${p.slug}`,
  extraHead: `<meta property="og:type" content="article"><meta property="article:published_time" content="${p.date}">`,
  body: `  <p class="tag crumb"><a href="${BLOG.path}">Invisible Wires — Agentic Cloud</a></p>
  <h1>${esc(p.title)}</h1>
  <p class="meta"><time datetime="${p.date}">${fmtDate(p.date)}</time> · ${esc(p.by)}</p>
  <article>
${p.html}
  </article>
  <p class="tag back"><a href="${BLOG.path}">← All posts</a></p>`,
})]));
const feed = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>${esc(BLOG.title)}</title>
<link>${SITE}${BLOG.path}</link>
<atom:link href="${SITE}${BLOG.path}/feed.xml" rel="self" type="application/rss+xml"/>
<description>${esc(BLOG.desc)}</description>
<language>en-us</language>
${posts.map((p) => `<item>
<title>${esc(p.title)}</title>
<link>${SITE}${BLOG.path}/${p.slug}</link>
<guid isPermaLink="true">${SITE}${BLOG.path}/${p.slug}</guid>
<pubDate>${new Date(p.date + "T12:00:00Z").toUTCString()}</pubDate>
<description>${esc(p.summary)}</description>
</item>`).join("\n")}
</channel>
</rss>
`;

// ---------- GitHub contribution graphs (data/github.json from fetch-github.mjs; no runtime requests) ----------
let gh = {};
try { gh = JSON.parse(readFileSync(new URL("./data/github.json", import.meta.url), "utf8")); } catch (e) { if (e.code !== "ENOENT") throw e; }
const GH_PEOPLE = { issaquahd: "Alex Alvord", CloudLabWorks: "Alex Alvord" };
function githubGraph(user) {
  const d = gh[user]; if (!d) return "";
  const C = 10, G = 2, S = C + G, PAD_T = 14, PAD_L = 0;
  const first = new Date(d.days[0].date + "T00:00:00Z");
  const startDow = first.getUTCDay();
  const cells = [], months = []; let lastMonth = -1;
  d.days.forEach((day, i) => {
    const idx = i + startDow, col = Math.floor(idx / 7), row = idx % 7;
    const dt = new Date(day.date + "T00:00:00Z");
    if (row === 0 && dt.getUTCMonth() !== lastMonth) { lastMonth = dt.getUTCMonth(); if (dt.getUTCDate() <= 7 || months.length === 0) months.push({ col, label: dt.toLocaleDateString("en-US", { month: "short", timeZone: "UTC" }) }); }
    const label = `${day.count === 0 ? "No contributions" : day.count === 1 ? "1 contribution" : `${day.count} contributions`} on ${dt.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" })}`;
    cells.push(`<rect class="l${day.level}" x="${PAD_L + col * S}" y="${PAD_T + row * S}" width="${C}" height="${C}" rx="2"${day.count ? `><title>${label}</title></rect` : "/"}>`);
  });
  const cols = Math.ceil((d.days.length + startDow) / 7), w = PAD_L + cols * S, h = PAD_T + 7 * S;
  const mlabels = months.filter((m, i, a) => i === 0 || m.col - a[i - 1].col >= 3).map((m) => `<text x="${PAD_L + m.col * S}" y="9">${m.label}</text>`).join("");
  const total = d.total.toLocaleString("en-US");
  return `    <li class="gh"><b><a href="https://github.com/${user}" rel="noopener">@${user}</a> — ${esc(GH_PEOPLE[user] || user)}</b><span>${total} contribution${d.total === 1 ? "" : "s"} in the last year · as of ${d.fetched}</span>
      <svg class="gh-graph" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" role="img" aria-label="GitHub contribution calendar for ${user}: ${total} contributions in the last year">${mlabels}${cells.join("")}</svg></li>`;
}
const GITHUB = Object.keys(GH_PEOPLE).map(githubGraph).join("\n");

// Home page: latest three posts.
const home = page("index.html").replace("{{LATEST}}", posts.length ? posts.slice(0, 3).map(postItem).join("\n") : emptyItem).replace("{{GITHUB}}", GITHUB);

// Inquiry form (/inquire): rendered at runtime from this template so it can echo values back on a validation error.
const INQUIRE = page("inquire.html");
const CATEGORIES = ["Architecture review", "Cloud and AI infrastructure design", "Technical content", "Speaking and interviews", "Mentoring", "Meet at an event", "Something else"];

const pages = { "/": home, "/work": page("work.html").replace("{{GITHUB}}", GITHUB), [BLOG.path]: blogIndex, ...postPages, "/notes": page("notes.html"), "/privacy": page("privacy.html"), "/terms": page("terms.html") };
const files = { [`${BLOG.path}/feed.xml`]: { body: feed, type: "application/rss+xml; charset=utf-8" } };

const worker = `// Generated by build.mjs — do not edit. Source: site/*.html, posts/*.md
const PAGES = ${JSON.stringify(pages)};
const FILES = ${JSON.stringify(files)};
const INQUIRE = ${JSON.stringify(INQUIRE)};
const CATEGORIES = ${JSON.stringify(CATEGORIES)};
const INQUIRY_FROM = "inquiry@cloudlabworks.dev";
// Recipient: the Worker var INQUIRY_TO (must be a verified Email Routing destination address in this account); the From address is on the zone.
const HEADERS = {
  "content-type": "text/html; charset=utf-8",
  "cache-control": "public, max-age=300",
  "strict-transport-security": "max-age=31536000; includeSubDomains; preload",
  "x-content-type-options": "nosniff",
  "referrer-policy": "strict-origin-when-cross-origin",
  "content-security-policy": "default-src 'none'; style-src 'unsafe-inline'; img-src 'self'; media-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
};
const NOSTORE = { ...HEADERS, "cache-control": "no-store" };
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const b64 = (s) => btoa(String.fromCharCode(...new TextEncoder().encode(s)));
const hdr = (s) => (/^[\\x20-\\x7e]*$/.test(s) ? s : "=?utf-8?B?" + b64(s) + "?=");
function inquireForm({ values = {}, notice = "", err = false } = {}) {
  const v = (k) => esc(values[k] || "");
  const opts = ['<option value="" disabled' + (values.category ? "" : " selected") + ">Choose one</option>", ...CATEGORIES.map((c) => '<option value="' + esc(c) + '"' + (values.category === c ? " selected" : "") + ">" + esc(c) + "</option>")].join("\\n");
  return INQUIRE.replace("{{NOTICE}}", notice ? '<p class="notice' + (err ? " err" : "") + '">' + esc(notice) + "</p>" : "")
    .replace("{{OPTIONS}}", opts).replace("{{V_NAME}}", v("name")).replace("{{V_EMAIL}}", v("email")).replace("{{V_PHONE}}", v("phone"))
    .replace("{{V_COMPANY}}", v("company")).replace("{{V_CONTEXT}}", v("context")).replace("{{T}}", String(Date.now()));
}
async function inquire(request, env) {
  const ct = request.headers.get("content-type") || "";
  if (!ct.startsWith("application/x-www-form-urlencoded") && !ct.startsWith("multipart/form-data")) return new Response("Unsupported media type", { status: 415 });
  const form = await request.formData();
  const f = (k, max) => (form.get(k) || "").toString().trim().slice(0, max);
  const values = { name: f("name", 120), email: f("email", 200), phone: f("phone", 40), company: f("company", 120), category: f("category", 60), context: f("context", 4000) };
  const bad = (msg) => new Response(inquireForm({ values, notice: msg, err: true }), { status: 400, headers: NOSTORE });
  if (f("website", 10)) return new Response(inquireForm({ notice: "Thanks — your inquiry is on its way." }), { headers: NOSTORE });
  const t = Number(f("t", 20));
  if (!t || Date.now() - t < 3000) return bad("That was quick. Please take a second look and send again.");
  if (!values.name) return bad("Name is required.");
  if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(values.email)) return bad("A valid email address is required so Alex can reply.");
  if (!CATEGORIES.includes(values.category)) return bad("Choose what you are inquiring about.");
  const lines = ["Inquiry from cloudlabworks.dev/inquire", "", "Name:     " + values.name, "Email:    " + values.email, "Phone:    " + (values.phone || "—"), "Company:  " + (values.company || "—"), "Category: " + values.category, "", "Context:", values.context || "—", "", "— Received " + new Date().toISOString() + " · IP " + (request.headers.get("cf-connecting-ip") || "?") + " · " + (request.headers.get("cf-ipcountry") || "")];
  const body = lines.join("\\r\\n");
  const raw = ["From: " + hdr("Cloud Lab Works inquiry") + " <" + INQUIRY_FROM + ">", "To: " + env.INQUIRY_TO, "Reply-To: " + hdr(values.name) + " <" + values.email + ">", "Subject: " + hdr("[cloudlabworks.dev] " + values.category + " — " + values.name), "Date: " + new Date().toUTCString(), "Message-ID: <" + crypto.randomUUID() + "@cloudlabworks.dev>", "MIME-Version: 1.0", "Content-Type: text/plain; charset=utf-8", "Content-Transfer-Encoding: base64", "", b64(body).replace(/.{76}/g, "$&\\r\\n")].join("\\r\\n");
  if (!env.INQUIRY || !env.INQUIRY_TO) return new Response(inquireForm({ values, notice: "The form is not wired up yet. Email alex@cloudlabworks.dev directly.", err: true }), { status: 503, headers: NOSTORE });
  try {
    const EmailMessage = await import("cloudflare:email").then((m) => m.EmailMessage, () => class { constructor(from, to, raw) { Object.assign(this, { from, to, raw }); } }); // fallback only for serve.mjs
    await env.INQUIRY.send(new EmailMessage(INQUIRY_FROM, env.INQUIRY_TO, raw));
  } catch (e) {
    return new Response(inquireForm({ values, notice: "Sending failed on our side (" + (e && e.message ? e.message : "unknown error") + "). Email alex@cloudlabworks.dev directly.", err: true }), { status: 502, headers: NOSTORE });
  }
  return new Response(inquireForm({ notice: "Thanks, " + values.name + " — your inquiry is on its way to Alex." }), { headers: NOSTORE });
}
// /media/*: Static Assets ignore Range (200, full body). WebKit needs 206 byte ranges to seek — and to
// seek back to 0 for <video loop> — so serve the asset through the ASSETS binding and slice it here.
async function media(request, env) {
  if (request.method !== "GET" && request.method !== "HEAD") return new Response("Method not allowed", { status: 405, headers: { allow: "GET, HEAD" } });
  const res = await env.ASSETS.fetch(new Request(request.url, { method: "GET" }));
  if (!res.ok || res.status === 206) return res;
  const h = new Headers(res.headers);
  h.set("accept-ranges", "bytes");
  const m = /^bytes=(\\d*)-(\\d*)$/.exec(request.headers.get("range") || "");
  if (!m) return new Response(request.method === "HEAD" ? null : res.body, { status: 200, headers: h });
  const buf = await res.arrayBuffer();
  const size = buf.byteLength;
  let start = m[1] === "" ? Math.max(0, size - Number(m[2])) : Number(m[1]);
  let end = m[1] !== "" && m[2] !== "" ? Math.min(Number(m[2]), size - 1) : size - 1;
  if (m[1] === "" && m[2] === "" || start >= size || start > end) return new Response(null, { status: 416, headers: { "content-range": "bytes */" + size } });
  h.set("content-range", "bytes " + start + "-" + end + "/" + size);
  h.set("content-length", String(end - start + 1));
  return new Response(request.method === "HEAD" ? null : buf.slice(start, end + 1), { status: 206, headers: h });
}
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname.startsWith("www.")) {
      url.hostname = url.hostname.slice(4);
      return Response.redirect(url.toString(), 301);
    }
    let path = url.pathname.replace(/\\/+$/, "") || "/";
    if (path.startsWith("/media/") && env.ASSETS) return media(request, env);
    if (path === "/inquire" || path === "/inquire.html") {
      if (request.method === "POST") return inquire(request, env);
      if (request.method !== "GET" && request.method !== "HEAD") return new Response("Method not allowed", { status: 405, headers: { allow: "GET, HEAD, POST" } });
      // Prefill from the query string (event "Request to meet" links): category must be a known option, context is trimmed and capped.
      const q = url.searchParams, pre = {};
      if (CATEGORIES.includes(q.get("category") || "")) pre.category = q.get("category");
      if (q.get("context")) pre.context = q.get("context").trim().slice(0, 4000);
      return new Response(inquireForm({ values: pre }), { headers: NOSTORE });
    }
    const file = FILES[path];
    if (file) return new Response(file.body, { headers: { ...HEADERS, "content-type": file.type } });
    if (path.endsWith(".html")) path = path.slice(0, -5) || "/";
    if (path === "/index") path = "/";
    if (path === "/robots.txt") return new Response("User-agent: *\\nAllow: /\\n", { headers: { "content-type": "text/plain" } });
    const body = PAGES[path];
    if (!body) return new Response("Not found", { status: 404, headers: { "content-type": "text/plain" } });
    return new Response(body, { headers: HEADERS });
  },
};
`;
writeFileSync(new URL("./src/worker.js", import.meta.url), worker);
console.log("built src/worker.js:", ["/inquire", ...Object.keys(pages), ...Object.keys(files)].map((k) => `${k} ${(k === "/inquire" ? INQUIRE : pages[k] || files[k].body).length}B`).join(", "));
