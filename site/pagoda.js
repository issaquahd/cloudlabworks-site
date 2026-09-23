// Pagoda Flight v0.1 -- vintage-cabinet canvas toy. A crane threads gaps between pagoda tiers.
(() => {
  const cv = document.getElementById("stage");
  if (!cv) return;
  const ctx = cv.getContext("2d");
  const W = cv.width, H = cv.height;
  const scoreEl = document.getElementById("score");
  const bestEl = document.getElementById("best");
  const BEST_KEY = "pagoda-flight-best";
  let best = Number(localStorage.getItem(BEST_KEY) || 0);
  bestEl.textContent = best;

  const GRAV = 0.42, FLAP = -7.2, GAP = 150, TOWER_W = 74, SPEED = 2.6;

  let bird, towers, score, alive, started, wing;

  function reset() {
    bird = { x: 160, y: H / 2, vy: 0 };
    towers = [];
    let x = W + 80;
    for (let i = 0; i < 5; i++) { towers.push(spawnTower(x)); x += 240; }
    score = 0; alive = true; started = false; wing = 0;
    scoreEl.textContent = 0;
  }
  function spawnTower(x) {
    const gapY = 90 + Math.random() * (H - 180 - GAP);
    return { x, gapY, passed: false };
  }

  function flap() {
    if (!alive) { reset(); return; }
    started = true;
    bird.vy = FLAP;
  }
  cv.addEventListener("pointerdown", flap);
  window.addEventListener("keydown", (e) => { if (e.code === "Space") { e.preventDefault(); flap(); } });

  function drawSky() {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, "#3a1f4a"); g.addColorStop(0.55, "#7a3b5a"); g.addColorStop(1, "#e0824a");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    // sun
    ctx.fillStyle = "#f2c879"; ctx.beginPath(); ctx.arc(W - 130, 120, 60, 0, Math.PI * 2); ctx.fill();
    // distant hill silhouette
    ctx.fillStyle = "rgba(20,10,25,.55)";
    ctx.beginPath(); ctx.moveTo(0, H - 60);
    for (let x = 0; x <= W; x += 40) ctx.lineTo(x, H - 60 - Math.sin(x * 0.01) * 18 - 20);
    ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.closePath(); ctx.fill();
  }

  function pagodaTier(cx, y, w, h, roofColor, bodyColor) {
    ctx.fillStyle = bodyColor;
    ctx.fillRect(cx - w * 0.36, y, w * 0.72, h);
    ctx.fillStyle = roofColor;
    ctx.beginPath();
    ctx.moveTo(cx - w / 2, y);
    ctx.quadraticCurveTo(cx - w * 0.28, y - h * 0.42, cx, y - h * 0.18);
    ctx.quadraticCurveTo(cx + w * 0.28, y - h * 0.42, cx + w / 2, y);
    ctx.closePath(); ctx.fill();
  }

  function drawTower(t) {
    const roof = "#8a2e2e", body = "#3d2418", roof2 = "#a83b3b";
    // top stack, tiers shrinking upward, from gap to top
    let y = t.gapY;
    let w = TOWER_W;
    let i = 0;
    while (y > -40) {
      pagodaTier(t.x + TOWER_W / 2, y, w, 34, i % 2 ? roof : roof2, body);
      y -= 40; w *= 0.94; i++;
    }
    // finial
    ctx.fillStyle = "#f2c879";
    ctx.fillRect(t.x + TOWER_W / 2 - 3, y - 26, 6, 26);
    ctx.beginPath(); ctx.arc(t.x + TOWER_W / 2, y - 26, 8, 0, Math.PI * 2); ctx.fill();
    // bottom stack, from gap+GAP to floor
    y = t.gapY + GAP;
    w = TOWER_W;
    i = 0;
    while (y < H + 20) {
      pagodaTier(t.x + TOWER_W / 2, y + 34, w, 34, i % 2 ? roof : roof2, body);
      y += 40; w *= 0.985; i++;
    }
  }

  function drawBird() {
    const a = Math.max(-0.6, Math.min(0.9, bird.vy / 10));
    ctx.save();
    ctx.translate(bird.x, bird.y);
    ctx.rotate(a * 0.5);
    ctx.fillStyle = "#f4f1e8";
    ctx.beginPath(); ctx.ellipse(0, 0, 22, 14, 0, 0, Math.PI * 2); ctx.fill();
    // wing, flapping
    const wa = Math.sin(wing) * 0.7 - 0.2;
    ctx.save(); ctx.translate(-2, -2); ctx.rotate(wa);
    ctx.fillStyle = "#1f2a33";
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.quadraticCurveTo(-6, -18, -26, -10); ctx.quadraticCurveTo(-10, 4, 0, 4); ctx.closePath(); ctx.fill();
    ctx.restore();
    // head/neck
    ctx.fillStyle = "#f4f1e8";
    ctx.beginPath(); ctx.ellipse(20, -10, 9, 8, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#d94a3d";
    ctx.beginPath(); ctx.moveTo(27, -12); ctx.lineTo(40, -8); ctx.lineTo(27, -6); ctx.closePath(); ctx.fill();
    ctx.fillStyle = "#141414";
    ctx.beginPath(); ctx.arc(22, -12, 1.6, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  function loop() {
    drawSky();
    towers.forEach(drawTower);
    drawBird();
    if (started && alive) {
      bird.vy += GRAV;
      bird.y += bird.vy;
      wing += 0.35 + Math.abs(bird.vy) * 0.03;
      towers.forEach((t) => {
        t.x -= SPEED;
        if (!t.passed && t.x + TOWER_W < bird.x - 20) { t.passed = true; score++; scoreEl.textContent = score; }
        const inX = bird.x + 18 > t.x && bird.x - 18 < t.x + TOWER_W;
        if (inX && (bird.y - 14 < t.gapY || bird.y + 14 > t.gapY + GAP)) alive = false;
      });
      if (towers.length && towers[0].x < -TOWER_W) { towers.shift(); towers.push(spawnTower(towers[towers.length - 1].x + 240)); }
      if (bird.y - 14 < 0 || bird.y + 14 > H) alive = false;
      if (!alive && score > best) { best = score; localStorage.setItem(BEST_KEY, best); bestEl.textContent = best; }
    } else {
      wing += 0.12;
    }
    if (!alive && started) {
      ctx.fillStyle = "rgba(20,10,25,.55)"; ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "#f4e8c8"; ctx.textAlign = "center"; ctx.font = "bold 34px system-ui, sans-serif";
      ctx.fillText("Click to try again", W / 2, H / 2);
    }
    requestAnimationFrame(loop);
  }
  reset();
  loop();
})();
