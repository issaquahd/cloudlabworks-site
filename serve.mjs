// Local preview of the built worker (Node ≥ 18). node serve.mjs → http://127.0.0.1:8787
import { createServer } from "node:http";
const w = (await import("./src/worker.js")).default;
createServer(async (req, res) => {
  const r = await w.fetch(new Request(`http://${req.headers.host}${req.url}`));
  res.writeHead(r.status, Object.fromEntries(r.headers));
  res.end(await r.text());
}).listen(8787, "127.0.0.1", () => console.log("http://127.0.0.1:8787"));
