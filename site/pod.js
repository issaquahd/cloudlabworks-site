// Waku's Pod v0.1 -- vintage-cabinet canvas toy. Feed the pod salmon; drag anyone by hand.
(() => {
  const cv = document.getElementById("stage");
  if (!cv) return;
  const ctx = cv.getContext("2d");
  const W = cv.width, H = cv.height;
  const fedEl = document.getElementById("fed");
  const countEl = document.getElementById("count");

  const rand = (a, b) => a + Math.random() * (b - a);

  // Waku and four of the pod (media/src/agents/gen.py, family.py): body color, dorsal-fin height
  // (0 = none, like Porpoise/Dolphin's low fin), face-patch color, size.
  const POD = [
    { name: "Waku", body: "#1f2a33", patch: "#fff", fin: 1.0, len: 46 },
    { name: "Minke", body: "#3f6e8f", patch: "#e8e0cc", fin: 0.4, len: 28 },
    { name: "Humpback", body: "#454545", patch: "#8a8a8a", fin: 0.25, len: 50 },
    { name: "Porpoise", body: "#6b6b6b", patch: "#d9d9d9", fin: 0.35, len: 30 },
    { name: "Dolphin", body: "#4a6b7a", patch: "#cfe0e2", fin: 0.5, len: 34 },
  ];

  class Pod {
    constructor(spec, i) {
      Object.assign(this, spec);
      this.x = rand(60, W - 60);
      this.y = rand(60, H - 60);
      this.a = rand(0, Math.PI * 2);
      this.speed = rand(0.4, 0.8);
      this.wag = rand(0, Math.PI * 2);
      this.turnBias = rand(-0.015, 0.015);
      this.wanderT = 0;
      this.dragged = false;
    }
    steerTo(tx, ty) {
      let diff = Math.atan2(ty - this.y, tx - this.x) - this.a;
      while (diff > Math.PI) diff -= Math.PI * 2;
      while (diff < -Math.PI) diff += Math.PI * 2;
      this.a += diff * 0.05;
    }
    update(food) {
      if (this.dragged) { this.wag += 0.25; return; }
      let nearest = null, nd = Infinity;
      for (const f of food) { const d = Math.hypot(f.x - this.x, f.y - this.y); if (d < nd) { nd = d; nearest = f; } }
      if (nearest && nd < 280) {
        this.steerTo(nearest.x, nearest.y);
        this.speed += (1.0 - this.speed) * 0.02;
        if (nd < 16) nearest.eaten = true;
      } else {
        this.wanderT -= 1;
        if (this.wanderT <= 0) { this.a += rand(-0.5, 0.5); this.wanderT = rand(50, 130); }
        this.a += this.turnBias;
        this.speed += (0.45 - this.speed) * 0.02;
      }
      const m = this.len + 10;
      if (this.x < m) this.steerTo(W / 2, this.y);
      if (this.x > W - m) this.steerTo(W / 2, this.y);
      if (this.y < m) this.steerTo(this.x, H / 2);
      if (this.y > H - m) this.steerTo(this.x, H / 2);
      this.wag += 0.18 + this.speed * 0.12;
      this.x += Math.cos(this.a) * this.speed;
      this.y += Math.sin(this.a) * this.speed;
    }
    draw(ctx) {
      const wag = Math.sin(this.wag) * 0.3;
      const l = this.len;
      ctx.save();
      ctx.translate(this.x, this.y);
      ctx.rotate(this.a);
      // body
      ctx.fillStyle = this.body;
      ctx.beginPath(); ctx.ellipse(0, 0, l * 0.52, l * 0.24, 0, 0, Math.PI * 2); ctx.fill();
      // pale belly/face patch, an orca-family tell
      ctx.fillStyle = this.patch;
      ctx.beginPath(); ctx.ellipse(l * 0.05, l * 0.09, l * 0.3, l * 0.11, 0, 0, Math.PI * 2); ctx.fill();
      // tail, wagging
      ctx.save(); ctx.translate(-l * 0.5, 0); ctx.rotate(wag);
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-l * 0.3, -l * 0.22); ctx.lineTo(-l * 0.3, l * 0.22); ctx.closePath();
      ctx.fillStyle = this.body; ctx.fill(); ctx.restore();
      // dorsal fin, height varies by species
      if (this.fin > 0) {
        ctx.beginPath();
        ctx.moveTo(-l * 0.02, -l * 0.2);
        ctx.lineTo(l * 0.06, -l * 0.2 - l * this.fin * 0.55);
        ctx.lineTo(l * 0.16, -l * 0.18);
        ctx.closePath();
        ctx.fillStyle = this.body; ctx.fill();
      }
      ctx.restore();
    }
  }

  const pod = POD.map((s, i) => new Pod(s, i));
  const food = [];
  const ripples = [];
  let fed = 0;
  let held = null;

  function toCanvasXY(evt) {
    const r = cv.getBoundingClientRect();
    const p = evt.touches ? evt.touches[0] : evt;
    return { x: (p.clientX - r.left) * (W / r.width), y: (p.clientY - r.top) * (H / r.height) };
  }
  function nearestPod(x, y) {
    let best = null, bd = 40;
    for (const k of pod) { const d = Math.hypot(k.x - x, k.y - y); if (d < bd) { bd = d; best = k; } }
    return best;
  }

  cv.addEventListener("pointerdown", (e) => {
    const { x, y } = toCanvasXY(e);
    const k = nearestPod(x, y);
    if (k) { held = k; k.dragged = true; }
    else { food.push({ x, y, eaten: false, life: 900 }); ripples.push({ x, y, r: 2, a: 0.5 }); }
  });
  cv.addEventListener("pointermove", (e) => {
    if (!held) return;
    const { x, y } = toCanvasXY(e);
    held.a = Math.atan2(y - held.y, x - held.x);
    held.x = x; held.y = y;
  });
  ["pointerup", "pointerleave", "pointercancel"].forEach((ev) =>
    cv.addEventListener(ev, () => { if (held) { held.dragged = false; held = null; } })
  );

  function drawSea() {
    const g = ctx.createRadialGradient(W / 2, H / 2, 40, W / 2, H / 2, W * 0.7);
    g.addColorStop(0, "#0e4a5c"); g.addColorStop(1, "#062430");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  function drawSalmon(x, y) {
    ctx.save(); ctx.translate(x, y);
    ctx.fillStyle = "#e0824a";
    ctx.beginPath(); ctx.ellipse(0, 0, 7, 3, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#c96a3a";
    ctx.beginPath(); ctx.moveTo(-6, 0); ctx.lineTo(-11, -3); ctx.lineTo(-11, 3); ctx.closePath(); ctx.fill();
    ctx.restore();
  }

  function loop() {
    drawSea();
    for (let i = ripples.length - 1; i >= 0; i--) {
      const r = ripples[i]; r.r += 1.1; r.a -= 0.011;
      if (r.a <= 0) { ripples.splice(i, 1); continue; }
      ctx.strokeStyle = `rgba(180,220,230,${r.a})`; ctx.lineWidth = 1.4;
      ctx.beginPath(); ctx.arc(r.x, r.y, r.r, 0, Math.PI * 2); ctx.stroke();
    }
    for (let i = food.length - 1; i >= 0; i--) {
      const f = food[i]; f.life--;
      if (f.eaten || f.life <= 0) { if (f.eaten) { fed++; fedEl.textContent = fed; } food.splice(i, 1); continue; }
      drawSalmon(f.x, f.y);
    }
    for (const k of pod) k.update(food);
    for (const k of pod) k.draw(ctx);
    countEl.textContent = pod.length;
    requestAnimationFrame(loop);
  }
  loop();
})();
