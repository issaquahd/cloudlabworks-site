// Fetches public GitHub contribution calendars at build time and writes data/github.json.
// No token needed (public HTML endpoint). Run before build.mjs; the site itself makes no
// runtime requests to GitHub. Usage: node fetch-github.mjs [user ...]
import { writeFileSync, mkdirSync } from "node:fs";
const users = process.argv.slice(2).length ? process.argv.slice(2) : ["issaquahd", "CloudLabWorks"];
const out = {};
for (const user of users) {
  const res = await fetch(`https://github.com/users/${user}/contributions`, { headers: { "user-agent": "cloudlabworks-site build" } });
  if (!res.ok) throw new Error(`${user}: HTTP ${res.status}`);
  const html = await res.text();
  const tips = {};
  for (const m of html.matchAll(/<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)<\/tool-tip>/g)) tips[m[1]] = m[2];
  const days = [];
  for (const m of html.matchAll(/<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="([^"]+)"[^>]*data-level="(\d)"/g)) {
    const tip = tips[m[2]] || "";
    const n = /^(\d[\d,]*) contribution/.exec(tip);
    days.push({ date: m[1], level: +m[3], count: n ? +n[1].replace(/,/g, "") : 0 });
  }
  if (days.length < 300) throw new Error(`${user}: parsed only ${days.length} days — GitHub markup changed?`);
  days.sort((a, b) => (a.date < b.date ? -1 : 1));
  const total = days.reduce((s, d) => s + d.count, 0);
  out[user] = { fetched: new Date().toISOString().slice(0, 10), total, days };
  console.log(`${user}: ${days.length} days, ${total} contributions (${days[0].date} → ${days.at(-1).date})`);
}
mkdirSync(new URL("./data/", import.meta.url), { recursive: true });
writeFileSync(new URL("./data/github.json", import.meta.url), JSON.stringify(out));
