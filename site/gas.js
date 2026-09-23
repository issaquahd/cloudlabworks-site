// Hitodama Chase v0.1 -- vintage-cabinet canvas toy. No dependencies, no build step.
(() => {
  const cv = document.getElementById("village");
  if (!cv) return;
  const ctx = cv.getContext("2d");
  const W = cv.width, H = cv.height;
  const caughtEl = document.getElementById("caught");
  const escapedEl = document.getElementById("escaped");
  const countEl = document.getElementById("villagerCount");

  const rand = (a, b) => a + Math.random() * (b - a);
  const GROUND = H * 0.82;

  class Villager {
    constructor(i) {
      this.x = rand(60, W - 60);
      this.y = GROUND + rand(-6, 6);
      this.homeY = this.y;
      this.a = 0;
      this.speed = rand(1.1, 1.6);
      this.dragged = false;
      this.robe = ["#7a4a2c", "#3a5a4a", "#5a3a5a", "#4a4a6a", "#6a5a3a"][i % 5];
      this.legPhase = rand(0, Math.PI * 2);
    }
    steerTo(tx, ty) {
      const dx = tx - this.x, dy = ty - this.y;
      let diff = Math.atan2(dy, dx) - this.a;
      while (diff > Math.PI) diff -= Math.PI * 2;
      while (diff < -Math.PI) diff += Math.PI * 2;
      this.a += diff * 0.15;
    }
    update(orbs) {
      if (this.dragged) { this.y = Math.min(this.y, GROUND + 10); this.legPhase += 0.3; return; }
      let nearest = null, nd = Infinity;
      for (const o of orbs) {
        if (o.caught) continue;
        const d = Math.hypot(o.x - this.x, o.y - this.y);
        if (d < nd) { nd = d; nearest = o; }
      }
      if (nearest && nd < 320) {
        this.steerTo(nearest.x, nearest.y);
        if (nd < 22) nearest.caught = true;
      } else {
        this.a += Math.sin(Date.now() * 0.0003 + this.homeY) * 0.02;
      }
      this.x += Math.cos(this.a) * this.speed;
      this.y = this.homeY + Math.sin(this.a) * 4;
      this.x = Math.max(20, Math.min(W - 20, this.x));
      this.legPhase += this.speed * 0.15;
    }
    draw(ctx) {
      ctx.save();
      ctx.translate(this.x, this.y);
      ctx.fillStyle = "rgba(0,0,0,.3)";
      ctx.beginPath(); ctx.ellipse(0, 20, 12, 3, 0, 0, Math.PI * 2); ctx.fill();
      const legSwing = Math.sin(this.legPhase) * 5;
      ctx.strokeStyle = "#201610";
      ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(-3, 8); ctx.lineTo(-3 + legSwing, 19); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(3, 8); ctx.lineTo(3 - legSwing, 19); ctx.stroke();
      ctx.fillStyle = this.robe;
      ctx.beginPath();
      ctx.moveTo(-9, 8); ctx.lineTo(9, 8); ctx.lineTo(6, -18); ctx.lineTo(-6, -18);
      ctx.closePath(); ctx.fill();
      ctx.fillStyle = "#e9cba3";
      ctx.beginPath(); ctx.arc(0, -24, 6, 0, Math.PI * 2); ctx.fill();
      // conical hat
      ctx.fillStyle = "#c9a86a";
      ctx.beginPath();
      ctx.moveTo(0, -34); ctx.lineTo(11, -22); ctx.lineTo(-11, -22);
      ctx.closePath(); ctx.fill();
      // lantern/net arm reaching toward facing direction
      const fx = Math.cos(this.a) * 12, fy = Math.sin(this.a) * 4;
      ctx.strokeStyle = "#201610";
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(4, -6); ctx.lineTo(4 + fx, -6 + fy); ctx.stroke();
      ctx.fillStyle = "rgba(200,220,180,.7)";
      ctx.beginPath(); ctx.arc(4 + fx, -6 + fy, 4, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }
  }

  class Hitodama {
    constructor() {
      this.x = rand(40, W - 40);
      this.y = GROUND + rand(0, 20);
      this.vy = -rand(0.35, 0.7);
      this.drift = rand(-0.3, 0.3);
      this.wobble = rand(0, Math.PI * 2);
      this.life = rand(500, 800);
      this.caught = false;
    }
    update() {
      this.wobble += 0.06;
      this.x += this.drift + Math.sin(this.wobble) * 0.4;
      this.y += this.vy;
      this.life--;
    }
    draw(ctx) {
      const flicker = 0.7 + Math.sin(this.wobble * 3) * 0.3;
      ctx.save();
      ctx.globalAlpha = Math.min(1, this.life / 80) * flicker;
      const g = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, 16);
      g.addColorStop(0, "#eafff0");
      g.addColorStop(0.4, "#8fd6c9");
      g.addColorStop(1, "rgba(80,150,140,0)");
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(this.x, this.y, 16, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#f4fff9";
      ctx.beginPath(); ctx.arc(this.x, this.y, 4, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }
  }

  const villagers = Array.from({ length: 5 }, (_, i) => new Villager(i));
  const orbs = [];
  let caught = 0, escaped = 0;
  let spawnTimer = 0;
  let held = null;

  function toCanvasXY(evt) {
    const r = cv.getBoundingClientRect();
    const p = evt.touches ? evt.touches[0] : evt;
    return { x: (p.clientX - r.left) * (W / r.width), y: (p.clientY - r.top) * (H / r.height) };
  }
  function nearestVillager(x, y) {
    let best = null, bd = 36;
    for (const v of villagers) { const d = Math.hypot(v.x - x, v.y - y); if (d < bd) { bd = d; best = v; } }
    return best;
  }
  function nearestIdleVillager(x, y) {
    let best = null, bd = Infinity;
    for (const v of villagers) { if (v.dragged) continue; const d = Math.hypot(v.x - x, v.y - y); if (d < bd) { bd = d; best = v; } }
    return best;
  }

  cv.addEventListener("pointerdown", (e) => {
    const { x, y } = toCanvasXY(e);
    const v = nearestVillager(x, y);
    if (v) { held = v; v.dragged = true; }
    else { const nv = nearestIdleVillager(x, y); if (nv) nv.steerTo(x, y); }
  });
  cv.addEventListener("pointermove", (e) => {
    if (!held) return;
    const { x, y } = toCanvasXY(e);
    held.a = Math.atan2(y - held.y, x - held.x);
    held.x = x; held.y = Math.min(y, GROUND + 12);
  });
  ["pointerup", "pointerleave", "pointercancel"].forEach((ev) =>
    cv.addEventListener(ev, () => { if (held) { held.dragged = false; held.homeY = held.y; held = null; } })
  );

  function drawNight() {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, "#0a0f1c");
    g.addColorStop(0.7, "#111d2c");
    g.addColorStop(1, "#1a2a30");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "#1c2a24";
    ctx.fillRect(0, GROUND + 14, W, H - GROUND - 14);
    // moon
    ctx.fillStyle = "#e9edd8";
    ctx.beginPath(); ctx.arc(W - 60, 56, 22, 0, Math.PI * 2); ctx.fill();
    // rooflines silhouette
    ctx.fillStyle = "#050a12";
    ctx.beginPath();
    ctx.moveTo(0, GROUND + 14);
    ctx.lineTo(40, GROUND - 30); ctx.lineTo(80, GROUND + 14);
    ctx.lineTo(120, GROUND - 44); ctx.lineTo(170, GROUND + 14);
    ctx.lineTo(520, GROUND + 14);
    ctx.lineTo(560, GROUND - 36); ctx.lineTo(610, GROUND + 14);
    ctx.lineTo(W, GROUND + 14);
    ctx.lineTo(W, GROUND + 30); ctx.lineTo(0, GROUND + 30);
    ctx.closePath(); ctx.fill();
  }

  function loop() {
    drawNight();

    spawnTimer--;
    if (spawnTimer <= 0 && orbs.length < 6) {
      orbs.push(new Hitodama());
      spawnTimer = rand(70, 160);
    }

    for (let i = orbs.length - 1; i >= 0; i--) {
      const o = orbs[i];
      o.update();
      if (o.caught) { caught++; caughtEl.textContent = caught; orbs.splice(i, 1); continue; }
      if (o.life <= 0 || o.y < -20) { escaped++; escapedEl.textContent = escaped; orbs.splice(i, 1); continue; }
    }
    for (const o of orbs) o.draw(ctx);

    for (const v of villagers) v.update(orbs);
    villagers.sort((a, b) => a.y - b.y);
    for (const v of villagers) v.draw(ctx);
    countEl.textContent = villagers.length;

    requestAnimationFrame(loop);
  }
  loop();
})();
