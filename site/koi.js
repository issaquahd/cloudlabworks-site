// Koi Pond v0.1 -- vintage-cabinet canvas toy. No dependencies, no build step.
(() => {
  const cv = document.getElementById("pond");
  if (!cv) return;
  const ctx = cv.getContext("2d");
  const W = cv.width, H = cv.height;
  const fedEl = document.getElementById("fed");
  const countEl = document.getElementById("count");

  const COLORS = [
    { body: "#f4f1e8", spot: "#e0472c" },
    { body: "#e8e0cc", spot: "#1a1a1a" },
    { body: "#f4f1e8", spot: "#e0472c", spot2: "#1a1a1a" },
    { body: "#f5c451", spot: null },
    { body: "#e0472c", spot: "#f4f1e8" },
    { body: "#c9c9c9", spot: "#3a3a3a" },
  ];

  const rand = (a, b) => a + Math.random() * (b - a);

  class Koi {
    constructor(i) {
      this.x = rand(60, W - 60);
      this.y = rand(60, H - 60);
      this.a = rand(0, Math.PI * 2);
      this.speed = rand(0.4, 0.9);
      this.len = rand(28, 40);
      this.wag = rand(0, Math.PI * 2);
      this.turnBias = rand(-0.02, 0.02);
      this.wanderT = 0;
      this.dragged = false;
      this.c = COLORS[i % COLORS.length];
    }
    steerTo(tx, ty) {
      const dx = tx - this.x, dy = ty - this.y;
      let diff = Math.atan2(dy, dx) - this.a;
      while (diff > Math.PI) diff -= Math.PI * 2;
      while (diff < -Math.PI) diff += Math.PI * 2;
      this.a += diff * 0.06;
    }
    update(pellets) {
      if (this.dragged) { this.wag += 0.3; return; }
      let nearest = null, nd = Infinity;
      for (const p of pellets) {
        const d = Math.hypot(p.x - this.x, p.y - this.y);
        if (d < nd) { nd = d; nearest = p; }
      }
      if (nearest && nd < 260) {
        this.steerTo(nearest.x, nearest.y);
        this.speed += (1.1 - this.speed) * 0.02;
        if (nd < 14) nearest.eaten = true;
      } else {
        this.wanderT -= 1;
        if (this.wanderT <= 0) { this.a += rand(-0.6, 0.6); this.wanderT = rand(40, 120); }
        this.a += this.turnBias;
        this.speed += (0.5 - this.speed) * 0.02;
      }
      const m = 44;
      if (this.x < m) this.steerTo(W / 2, this.y);
      if (this.x > W - m) this.steerTo(W / 2, this.y);
      if (this.y < m) this.steerTo(this.x, H / 2);
      if (this.y > H - m) this.steerTo(this.x, H / 2);
      this.wag += 0.25 + this.speed * 0.15;
      this.x += Math.cos(this.a) * this.speed;
      this.y += Math.sin(this.a) * this.speed;
    }
    draw(ctx) {
      const wag = Math.sin(this.wag) * 0.35;
      ctx.save();
      ctx.translate(this.x, this.y);
      ctx.rotate(this.a);
      const l = this.len;
      ctx.fillStyle = this.c.body;
      ctx.beginPath();
      ctx.ellipse(0, 0, l * 0.5, l * 0.22, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.save();
      ctx.translate(-l * 0.48, 0);
      ctx.rotate(wag);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(-l * 0.32, -l * 0.2);
      ctx.lineTo(-l * 0.32, l * 0.2);
      ctx.closePath();
      ctx.fillStyle = this.c.body;
      ctx.fill();
      ctx.restore();
      if (this.c.spot) { ctx.fillStyle = this.c.spot; ctx.beginPath(); ctx.ellipse(l * 0.06, -l * 0.02, l * 0.14, l * 0.1, 0.3, 0, Math.PI * 2); ctx.fill(); }
      if (this.c.spot2) { ctx.fillStyle = this.c.spot2; ctx.beginPath(); ctx.ellipse(-l * 0.12, l * 0.03, l * 0.1, l * 0.07, -0.2, 0, Math.PI * 2); ctx.fill(); }
      ctx.restore();
    }
  }

  const koi = Array.from({ length: 6 }, (_, i) => new Koi(i));
  const pellets = [];
  const ripples = [];
  let fed = 0;
  let held = null;

  function toCanvasXY(evt) {
    const r = cv.getBoundingClientRect();
    const p = evt.touches ? evt.touches[0] : evt;
    return { x: (p.clientX - r.left) * (W / r.width), y: (p.clientY - r.top) * (H / r.height) };
  }
  function nearestKoi(x, y) {
    let best = null, bd = 32;
    for (const k of koi) { const d = Math.hypot(k.x - x, k.y - y); if (d < bd) { bd = d; best = k; } }
    return best;
  }

  cv.addEventListener("pointerdown", (e) => {
    const { x, y } = toCanvasXY(e);
    const k = nearestKoi(x, y);
    if (k) { held = k; k.dragged = true; }
    else { pellets.push({ x, y, eaten: false, life: 900 }); ripples.push({ x, y, r: 2, a: 0.5 }); }
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

  function drawPond() {
    const g = ctx.createRadialGradient(W / 2, H / 2, 40, W / 2, H / 2, W * 0.7);
    g.addColorStop(0, "#124a5c");
    g.addColorStop(1, "#082530");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  }

  function loop() {
    drawPond();
    for (let i = ripples.length - 1; i >= 0; i--) {
      const r = ripples[i];
      r.r += 1.2; r.a -= 0.012;
      if (r.a <= 0) { ripples.splice(i, 1); continue; }
      ctx.strokeStyle = `rgba(180,220,230,${r.a})`;
      ctx.lineWidth = 1.4;
      ctx.beginPath(); ctx.arc(r.x, r.y, r.r, 0, Math.PI * 2); ctx.stroke();
    }
    for (let i = pellets.length - 1; i >= 0; i--) {
      const p = pellets[i];
      p.life--;
      if (p.eaten || p.life <= 0) { if (p.eaten) { fed++; fedEl.textContent = fed; } pellets.splice(i, 1); continue; }
      ctx.fillStyle = "#c9a24a";
      ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, Math.PI * 2); ctx.fill();
    }
    for (const k of koi) k.update(pellets);
    for (const k of koi) k.draw(ctx);
    countEl.textContent = koi.length;
    requestAnimationFrame(loop);
  }
  loop();
})();
