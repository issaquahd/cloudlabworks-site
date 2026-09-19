// Local preview of the built worker (Node ≥ 18). node serve.mjs → http://127.0.0.1:8787
import { createServer } from "node:http";
const w = (await import("./src/worker.js")).default;
// Local stand-in for the send_email binding: prints the raw message instead of sending.
const ENV = { INQUIRY_TO: "local-test@example.invalid", INQUIRY: { send: async (m) => console.log("--- would send ---\n" + m.raw) } };
createServer(async (req, res) => {
  const chunks = []; for await (const c of req) chunks.push(c);
  const init = { method: req.method, headers: req.headers, body: chunks.length ? Buffer.concat(chunks) : undefined };
  const r = await w.fetch(new Request(`http://${req.headers.host}${req.url}`, init), ENV);
  res.writeHead(r.status, Object.fromEntries(r.headers));
  res.end(await r.text());
}).listen(8787, "127.0.0.1", () => console.log("http://127.0.0.1:8787"));
