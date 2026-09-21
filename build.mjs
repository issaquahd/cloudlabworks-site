// Builds src/worker.js from site/*.html and posts/*.md. No runtime dependencies.
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
const r = (p) => readFileSync(new URL(`./site/${p}`, import.meta.url), "utf8");
const style = r("_style.css").trim(), head = r("_head.html").trim(), foot = r("_foot.html").trim();
// Site-wide head: the Waku orca as favicon / touch icon, and the share card for pages that carry no og:image of their own.
const ICONS = `<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="icon" href="/media/cloudlabworks-icon.svg" type="image/svg+xml">
<link rel="icon" href="/media/cloudlabworks-icon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#0b1220">
<meta name="application-name" content="CloudLab Works">
<meta name="apple-mobile-web-app-title" content="CloudLab Works">`;
const OG_IMAGE = `<meta property="og:image" content="https://cloudlabworks.dev/media/waku-orca-og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">`;
const fill = (html) => html.replace("<style>{{STYLE}}</style>", ICONS + "\n" + (html.includes('property="og:image"') ? "" : OG_IMAGE + "\n") + "<style>" + style + "</style>").replace("{{HEAD}}", head).replace("{{FOOT}}", foot);
// Feed autodiscovery on every page, not only the blog: a reader pointed at cloudlabworks.dev finds the feed.
const FEED_LINK = `<link rel="alternate" type="application/rss+xml" title="Invisible Wires: Agentic Cloud" href="/blog/feed.xml">`;
const page = (f) => fill(r(f).replace("</head>", `${FEED_LINK}\n</head>`));

// ---------- blog: Invisible Wires: Agentic Cloud ----------
const BLOG = { key: "blog", title: "Invisible Wires: Agentic Cloud", h1: "Invisible Wires", sub: "Agentic Cloud", path: "/blog", desc: "Notes from a home lab on agentic operations, hybrid multicloud, and the wires nobody sees. By Alex Alvord and Waku." };
// A second, dedicated section: Nutanix. Posts opt in with `section: nutanix` in frontmatter; they get their own index, feed and URLs.
const NUTANIX = { key: "nutanix", title: "Nutanix: Invisible Wires: Agentic Cloud", h1: "Nutanix: Invisible Wires", sub: "Agentic Cloud · NC2 on AWS, Azure, Google Cloud", path: "/nutanix", desc: "Field notes on Nutanix: NC2 on AWS, Azure, Google Cloud, hybrid multicloud design, and what works in real customer environments. Written by Alex Alvord in a personal capacity, opinions are his own, not Nutanix's; everything here is public information.", disclaimer: "Personal blog. Alex works at Nutanix; the opinions here are his own and nothing here is Nutanix confidential: every fact is public or his own field experience." };
const SECTIONS = { blog: BLOG, nutanix: NUTANIX };
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
    const section = SECTIONS[meta.section || "blog"];
    if (!section) throw new Error(`posts/${f}: unknown section ${meta.section}`);
    // `also: nutanix` lists a post in a second section's index and feed; its URL stays under the primary section.
    const also = (meta.also || "").split(/[,\s]+/).filter(Boolean).map((k) => { if (!SECTIONS[k]) throw new Error(`posts/${f}: unknown section ${k}`); return SECTIONS[k]; });
    return { slug, date, sort: `${date}T${meta.time || "00:00"}`, title: meta.title, summary: meta.summary || "", by: meta.by || "Alex Alvord", html: markdown(body), section, moved: meta.moved_from || "", origin: meta.origin || "", draft: meta.draft === "true", also };
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

// Provenance is visible where the reader is: the by-line names the author, and a repost says where it first ran.
const originName = (u) => /linkedin\.com/.test(u) ? "LinkedIn" : /medium\.com/.test(u) ? "Medium" : new URL(u).hostname.replace(/^www\./, "");
const origin = (p) => p.origin ? ` · first published on <a href="${p.origin}" rel="noopener">${originName(p.origin)}</a>` : "";
const postItem = (p) => `    <li><time datetime="${p.date}">${fmtDate(p.date)}</time><b><a href="${p.section.path}/${p.slug}">${esc(p.title)}</a></b><span>${esc(p.summary)}</span><span class="by">By ${esc(p.by)}${origin(p)}</span></li>`;
const emptyItem = (sec) => `    <li><b>First post is on its way.</b><span><a href="${sec.path}/feed.xml">Subscribe to the feed</a> and it will find you.</span></li>`;
const drafts = posts.filter((p) => p.draft);
posts = posts.filter((p) => !p.draft);
const inSection = (sec) => posts.filter((p) => p.section === sec || p.also.includes(sec));

const sectionIndex = (sec) => shell({
  title: `${sec.title} · CloudLab Works`, desc: sec.desc, path: sec.path, cls: "blog",
  body: `  <h1>${esc(sec.h1)}<small>${esc(sec.sub)}</small></h1>
  <p class="lede">${esc(sec.desc)}</p>
  ${sec.disclaimer ? `<p class="tag">${esc(sec.disclaimer)}</p>\n  ` : ""}<p class="tag"><a href="${sec.path}/feed.xml">RSS feed</a> · <a href="/subscribe">Subscribe by email</a></p>
  <ul class="plain posts">
${inSection(sec).length ? inSection(sec).map(postItem).join("\n") : emptyItem(sec)}
  </ul>`,
});
const postPages = Object.fromEntries([...posts, ...drafts].map((p) => [`${p.section.path}/${p.slug}`, shell({
  title: `${p.draft ? "DRAFT: " : ""}${p.title} · ${p.section.title}`, desc: p.summary || p.section.desc, path: `${p.section.path}/${p.slug}`, noindex: p.draft,
  extraHead: `<meta property="og:type" content="article"><meta property="article:published_time" content="${p.date}">`,
  body: `  ${p.draft ? `<p class="tag draft">Draft: unlisted preview. Not in the index, the feed, or the mail; search engines are told to ignore it.</p>\n  ` : ""}<p class="tag crumb"><a href="${p.section.path}">${esc(p.section.title)}</a></p>
  <h1>${esc(p.title)}</h1>
  <p class="meta"><time datetime="${p.date}">${fmtDate(p.date)}</time> · By ${esc(p.by)}${origin(p)}</p>
  <article>
${p.html}
  </article>
  ${p.section.disclaimer ? `<p class="tag">${esc(p.section.disclaimer)}</p>\n  ` : ""}<p class="tag back"><a href="${p.section.path}">← All posts</a></p>`,
})]));
// Old URLs of posts that moved between sections (frontmatter `moved_from: /blog/<slug>`) → 301.
const REDIRECTS = Object.fromEntries(posts.filter((p) => p.moved).map((p) => [p.moved, `${p.section.path}/${p.slug}`]));
const sectionFeed = (sec) => `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>${esc(sec.title)}</title>
<link>${SITE}${sec.path}</link>
<atom:link href="${SITE}${sec.path}/feed.xml" rel="self" type="application/rss+xml"/>
<description>${esc(sec.desc)}</description>
<language>en-us</language>
${inSection(sec).map((p) => `<item>
<title>${esc(p.title)}</title>
<link>${SITE}${sec.path}/${p.slug}</link>
<guid isPermaLink="true">${SITE}${sec.path}/${p.slug}</guid>
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
  return `    <li class="gh"><b><a href="https://github.com/${user}" rel="noopener">@${user}</a>, ${esc(GH_PEOPLE[user] || user)}</b><span>${total} contribution${d.total === 1 ? "" : "s"} in the last year · as of ${d.fetched}</span>
      <svg class="gh-graph" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" role="img" aria-label="GitHub contribution calendar for ${user}: ${total} contributions in the last year">${mlabels}${cells.join("")}</svg></li>`;
}
const GITHUB = Object.keys(GH_PEOPLE).map(githubGraph).join("\n");

// Home page: latest three posts.
const home = page("index.html").replace("{{LATEST}}", inSection(BLOG).length ? inSection(BLOG).slice(0, 3).map(postItem).join("\n") : emptyItem(BLOG)).replace("{{GITHUB}}", GITHUB);

// Inquiry form (/inquire): rendered at runtime from this template so it can echo values back on a validation error.
const INQUIRE = page("inquire.html");
const CATEGORIES = ["Cloud & AI triage", "Startup advisor", "Agentic art", "Original art", "Board position", "Community give-back", "Collaborate on a project", "Writing", "Speaking and interviews", "Mentoring", "Meet at an event", "Something else"];

const pages = { "/": home, "/work": page("work.html").replace("{{GITHUB}}", GITHUB), [BLOG.path]: sectionIndex(BLOG), [NUTANIX.path]: sectionIndex(NUTANIX), ...postPages, "/notes": page("notes.html"), "/privacy": page("privacy.html"), "/terms": page("terms.html"), "/card": page("card.html"), "/live": page("live.html"), "/orcas": page("orcas.html"), "/art": page("art.html"), "/diagrams": page("diagrams.html"), "/asr": page("asr.html"), "/certifications": page("certifications.html"), "/subscribe": page("subscribe.html"), "/resume": page("resume.html") };
// /card is the NFC business-card landing page; the tag on the card carries only this URL.
const VCARD = ["BEGIN:VCARD", "VERSION:3.0", "N:Alvord;Alex;;;", "FN:Alex Alvord", "ORG:Cloud Lab Works LLC", "TITLE:Principal Architect", "EMAIL;TYPE=INTERNET,WORK:alex@cloudlabworks.dev", "URL:https://cloudlabworks.dev", "URL;TYPE=LinkedIn:https://www.linkedin.com/in/alexalvord/", "ADR;TYPE=WORK:;;;Duvall;WA;;USA", "NOTE:Hybrid multicloud and AI infrastructure. A working lab, open to collaboration on projects. cloudlabworks.dev", "END:VCARD"].join("\r\n") + "\r\n";
// Scripts, self-hosted (CSP script-src 'self'): /live.js = the browser instrument + visualizer; /art.js = the nightly haiku on /art; /menu.js = keyboard handling for the hamburger drawer.
const LIVE_JS = readFileSync(new URL("./site/live.js", import.meta.url), "utf8");
const ART_JS = readFileSync(new URL("./site/art.js", import.meta.url), "utf8");
const MENU_JS = readFileSync(new URL("./site/menu.js", import.meta.url), "utf8");
const files = { [`${BLOG.path}/feed.xml`]: { body: sectionFeed(BLOG), type: "application/rss+xml; charset=utf-8" }, [`${NUTANIX.path}/feed.xml`]: { body: sectionFeed(NUTANIX), type: "application/rss+xml; charset=utf-8" }, "/alex-alvord.vcf": { body: VCARD, type: "text/vcard; charset=utf-8" }, "/live.js": { body: LIVE_JS, type: "text/javascript; charset=utf-8" }, "/art.js": { body: ART_JS, type: "text/javascript; charset=utf-8" }, "/menu.js": { body: MENU_JS, type: "text/javascript; charset=utf-8" }, "/site.webmanifest": { body: JSON.stringify({ name: "CloudLab Works", short_name: "CloudLab Works", description: "Cloud and AI infrastructure, designed to be run.", start_url: "/", display: "standalone", background_color: "#0b1220", theme_color: "#0b1220", icons: [{ src: "/media/cloudlabworks-icon-192.png", sizes: "192x192", type: "image/png" }, { src: "/media/cloudlabworks-icon-512.png", sizes: "512x512", type: "image/png" }, { src: "/media/cloudlabworks-icon-maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" }] }), type: "application/manifest+json; charset=utf-8" } };
// Root-level icon names that browsers, crawlers and link unfurlers request without reading the page.
const ICON_ALIASES = { "/favicon.ico": "/media/favicon.ico", "/favicon.svg": "/media/cloudlabworks-icon.svg", "/favicon.png": "/media/cloudlabworks-icon-32.png", "/apple-touch-icon.png": "/media/cloudlabworks-icon-180.png", "/apple-touch-icon-precomposed.png": "/media/cloudlabworks-icon-180.png" };

const worker = `// Generated by build.mjs, do not edit. Source: site/*.html, posts/*.md
const PAGES = ${JSON.stringify(pages)};
const FILES = ${JSON.stringify(files)};
const ICON_ALIASES = ${JSON.stringify(ICON_ALIASES)};
const REDIRECTS = ${JSON.stringify(REDIRECTS)};
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
  "content-security-policy": "default-src 'none'; style-src 'unsafe-inline'; img-src 'self'; media-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self' https://buttondown.com; frame-ancestors 'none'",
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
  if (f("website", 10)) return new Response(inquireForm({ notice: "Thanks, your inquiry is on its way." }), { headers: NOSTORE });
  const t = Number(f("t", 20));
  if (!t || Date.now() - t < 3000) return bad("That was quick. Please take a second look and send again.");
  if (!values.name) return bad("Name is required.");
  if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(values.email)) return bad("A valid email address is required so Alex can reply.");
  if (!CATEGORIES.includes(values.category)) return bad("Choose what you are inquiring about.");
  const lines = ["Inquiry from cloudlabworks.dev/inquire", "", "Name:     " + values.name, "Email:    " + values.email, "Phone:    " + (values.phone || "-"), "Company:  " + (values.company || "-"), "Category: " + values.category, "", "Context:", values.context || ", ", "", ",  Received " + new Date().toISOString() + " · IP " + (request.headers.get("cf-connecting-ip") || "?") + " · " + (request.headers.get("cf-ipcountry") || "")];
  const body = lines.join("\\r\\n");
  const raw = ["From: " + hdr("CloudLab Works inquiry") + " <" + INQUIRY_FROM + ">", "To: " + env.INQUIRY_TO, "Reply-To: " + hdr(values.name) + " <" + values.email + ">", "Subject: " + hdr("[cloudlabworks.dev] " + values.category + ", " + values.name), "Date: " + new Date().toUTCString(), "Message-ID: <" + crypto.randomUUID() + "@cloudlabworks.dev>", "MIME-Version: 1.0", "Content-Type: text/plain; charset=utf-8", "Content-Transfer-Encoding: base64", "", b64(body).replace(/.{76}/g, "$&\\r\\n")].join("\\r\\n");
  if (!env.INQUIRY || !env.INQUIRY_TO) return new Response(inquireForm({ values, notice: "The form is not wired up yet. Email alex@cloudlabworks.dev directly.", err: true }), { status: 503, headers: NOSTORE });
  try {
    const EmailMessage = await import("cloudflare:email").then((m) => m.EmailMessage, () => class { constructor(from, to, raw) { Object.assign(this, { from, to, raw }); } }); // fallback only for serve.mjs
    await env.INQUIRY.send(new EmailMessage(INQUIRY_FROM, env.INQUIRY_TO, raw));
  } catch (e) {
    return new Response(inquireForm({ values, notice: "Sending failed on our side (" + (e && e.message ? e.message : "unknown error") + "). Email alex@cloudlabworks.dev directly.", err: true }), { status: 502, headers: NOSTORE });
  }
  return new Response(inquireForm({ notice: "Thanks, " + values.name + ", your inquiry is on its way to Alex." }), { headers: NOSTORE });
}
// /media/*: Static Assets ignore Range (200, full body). WebKit needs 206 byte ranges to seek, and to
// seek back to 0 for <video loop>, so serve the asset through the ASSETS binding and slice it here.
async function media(request, env) {
  if (request.method !== "GET" && request.method !== "HEAD") return new Response("Method not allowed", { status: 405, headers: { allow: "GET, HEAD" } });
  const res = await env.ASSETS.fetch(new Request(request.url, { method: "GET" }));
  if (!res.ok || res.status === 206) return res;
  const h = new Headers(res.headers);
  h.set("accept-ranges", "bytes");
  // Static Assets label the IaM feed files octet-stream; Safari refuses octet-stream audio, fetch().json() is fine either way.
  const ext = (new URL(request.url).pathname.match(/\\.([a-z0-9]+)$/) || [])[1];
  const mime = { json: "application/json; charset=utf-8", m4a: "audio/mp4", opus: "audio/ogg", mp3: "audio/mpeg", pdf: "application/pdf", zip: "application/zip", ico: "image/x-icon" }[ext];
  if (mime) h.set("content-type", mime);
  if (ext === "json") h.set("cache-control", "public, max-age=60");
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
    if (ICON_ALIASES[path] && env.ASSETS) return media(new Request(url.origin + ICON_ALIASES[path], request), env);
    if (REDIRECTS[path]) return Response.redirect(url.origin + REDIRECTS[path], 301);
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
