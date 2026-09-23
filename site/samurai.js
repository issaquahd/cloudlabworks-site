// Samurai Duel v0.1 -- vintage-cabinet canvas toy. No dependencies, no build step.
(() => {
  const cv = document.getElementById("dojo");
  if (!cv) return;
  const ctx = cv.getContext("2d");
  const W = cv.width, H = cv.height;
  const hitsAEl = document.getElementById("hitsA");
  const hitsBEl = document.getElementById("hitsB");
  const parriesEl = document.getElementById("parries");
  const boutsEl = document.getElementById("bouts");

  const rand = (a, b) => a + Math.random() * (b - a);
  const GROUND = H * 0.78;

  class Samurai {
    constructor(x, facing, armor, sash) {
      this.baseX = x;
      this.x = x;
      this.facing = facing; // 1 = faces right, -1 = faces left
      this.armor = armor;
      this.sash = sash;
      this.state = "idle"; // idle, windup, strike, recover, hit, win
      this.t = 0;
      this.lunge = 0;
      this.flash = 0;
    }
    attack() {
      if (this.state !== "idle") return false;
      this.state = "windup";
      this.t = 0;
      return true;
    }
    getBlade() {
      // returns {x1,y1,x2,y2} of the sword tip reach in world space, only meaningful mid-strike
      const shoulderY = GROUND - 74;
      const reach = 46 + this.lunge * 34;
      const tipX = this.x + this.facing * reach;
      return { x: tipX, y: shoulderY - 6 };
    }
    update() {
      this.t++;
      this.flash = Math.max(0, this.flash - 1);
      if (this.state === "windup") {
        this.lunge = Math.min(0.4, this.t / 10);
        if (this.t > 9) { this.state = "strike"; this.t = 0; }
      } else if (this.state === "strike") {
        this.lunge = 0.4 + Math.min(0.6, this.t / 5);
        this.x = this.baseX + this.facing * 10 * Math.min(1, this.t / 6);
        if (this.t > 6) { this.state = "recover"; this.t = 0; }
      } else if (this.state === "recover") {
        this.lunge = Math.max(0, 1 - this.t / 10);
        this.x += (this.baseX - this.x) * 0.3;
        if (this.t > 12) { this.state = "idle"; this.t = 0; this.lunge = 0; this.x = this.baseX; }
      } else if (this.state === "hit") {
        this.flash = 8;
        if (this.t > 20) { this.state = "idle"; this.t = 0; }
      } else if (this.state === "win") {
        // holds pose
      } else {
        this.lunge = Math.max(0, this.lunge - 0.05);
      }
    }
    isSwinging() {
      return this.state === "windup" || this.state === "strike";
    }
    isVulnerable() {
      // open to a hit: not mid-swing, not already reeling, not already resolved this exchange
      return this.state === "idle" || this.state === "recover";
    }
    draw(ctx) {
      ctx.save();
      ctx.translate(this.x, GROUND);
      const f = this.facing;
      // shadow
      ctx.fillStyle = "rgba(0,0,0,.35)";
      ctx.beginPath();
      ctx.ellipse(0, 4, 26, 6, 0, 0, Math.PI * 2);
      ctx.fill();
      const bob = this.state === "hit" ? -Math.sin(this.t * 0.6) * 4 : 0;
      const lean = this.lunge * f * 10;
      ctx.translate(lean, bob);
      // robe (flat triangle-ish shape)
      ctx.fillStyle = this.flash % 16 < 8 && this.state === "hit" ? "#e0472c" : this.armor;
      ctx.beginPath();
      ctx.moveTo(-16, 0);
      ctx.lineTo(16, 0);
      ctx.lineTo(9, -70);
      ctx.lineTo(-9, -70);
      ctx.closePath();
      ctx.fill();
      // sash
      ctx.fillStyle = this.sash;
      ctx.fillRect(-9, -44, 18, 8);
      // head
      ctx.fillStyle = "#e9cba3";
      ctx.beginPath();
      ctx.arc(0, -82, 11, 0, Math.PI * 2);
      ctx.fill();
      // topknot
      ctx.fillStyle = "#1a1310";
      ctx.beginPath();
      ctx.arc(0, -90, 8, Math.PI, 0);
      ctx.fill();
      ctx.fillRect(-2, -100, 4, 8);
      // arm + sword
      const shoulderY = -70;
      const swingA = this.isSwinging() ? -0.9 + this.lunge * 1.4 : -0.15;
      ctx.save();
      ctx.translate(f * 6, shoulderY);
      ctx.rotate(f * swingA);
      ctx.strokeStyle = "#2a2420";
      ctx.lineWidth = 5;
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(f * 10, 14); ctx.stroke();
      // blade
      const bladeLen = 46 + this.lunge * 30;
      ctx.strokeStyle = this.isSwinging() ? "#f2f2f2" : "#c9c9c9";
      ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(f * 10, 14); ctx.lineTo(f * (10 + bladeLen * 0.9), 14 - bladeLen); ctx.stroke();
      ctx.restore();
      ctx.restore();
    }
  }

  const left = new Samurai(W * 0.32, 1, "#8a2f22", "#f2c879");
  const right = new Samurai(W * 0.68, -1, "#22344a", "#d8b98a");

  let hitsA = 0, hitsB = 0, parries = 0, bouts = 0;
  let clashSpark = null; // {x,y,life}
  let cooldown = 0;
  let resolvedThisExchange = false;
  let aiTimer = rand(50, 110);

  function resetBout() {
    hitsA = 0; hitsB = 0;
    hitsAEl.textContent = "0"; hitsBEl.textContent = "0";
    left.state = "idle"; right.state = "idle";
  }

  function resolveExchange() {
    if (resolvedThisExchange) return;
    const aSwing = left.isSwinging();
    const bSwing = right.isSwinging();
    if (aSwing && bSwing) {
      // both swinging at once: clash
      parries++; parriesEl.textContent = parries;
      clashSpark = { x: (left.x + right.x) / 2, y: GROUND - 76, life: 14 };
      left.state = "recover"; left.t = 0;
      right.state = "recover"; right.t = 0;
      resolvedThisExchange = true;
    } else if (aSwing && right.isVulnerable() && left.state === "strike") {
      hitsA++; hitsAEl.textContent = hitsA;
      right.state = "hit"; right.t = 0;
      resolvedThisExchange = true;
      if (hitsA >= 3) { bouts++; boutsEl.textContent = bouts; left.state = "win"; setTimeout(resetBout, 900); }
    } else if (bSwing && left.isVulnerable() && right.state === "strike") {
      hitsB++; hitsBEl.textContent = hitsB;
      left.state = "hit"; left.t = 0;
      resolvedThisExchange = true;
      if (hitsB >= 3) { right.state = "win"; setTimeout(resetBout, 900); }
    }
  }

  cv.addEventListener("pointerdown", () => {
    if (left.attack()) resolvedThisExchange = false;
  });

  function aiAttack() {
    if (right.attack()) resolvedThisExchange = false;
  }

  function drawFloor() {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, "#3a332c");
    g.addColorStop(1, "#171310");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "#4a4038";
    ctx.fillRect(0, GROUND, W, H - GROUND);
    ctx.strokeStyle = "rgba(255,255,255,.05)";
    for (let x = 0; x < W; x += 60) {
      ctx.beginPath(); ctx.moveTo(x, GROUND); ctx.lineTo(x, H); ctx.stroke();
    }
  }

  function loop() {
    drawFloor();
    left.update();
    right.update();
    if (left.state === "strike" || right.state === "strike") resolveExchange();
    if (left.state === "idle" && right.state === "idle") resolvedThisExchange = false;

    left.draw(ctx);
    right.draw(ctx);

    if (clashSpark) {
      const s = clashSpark;
      s.life--;
      ctx.save();
      ctx.translate(s.x, s.y);
      ctx.strokeStyle = `rgba(255,230,150,${s.life / 14})`;
      ctx.lineWidth = 2;
      for (let i = 0; i < 6; i++) {
        const a = (i / 6) * Math.PI * 2 + s.life * 0.3;
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(Math.cos(a) * (18 - s.life), Math.sin(a) * (18 - s.life));
        ctx.stroke();
      }
      ctx.restore();
      if (s.life <= 0) clashSpark = null;
    }

    aiTimer--;
    if (aiTimer <= 0 && right.state === "idle") {
      aiAttack();
      aiTimer = rand(60, 130);
    }

    requestAnimationFrame(loop);
  }
  loop();
})();
