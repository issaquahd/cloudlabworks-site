// IaC Live Music — a browser copy of the lab's instrument (ops/iam/drone.rb) plus a visualizer.
// Self-hosted, no third-party requests. State comes from /media/iam-state.json; recordings from /media/iam-feed.json.
(function () {
  "use strict";
  var STATE_URL = "/media/iam-state.json", FEED_URL = "/media/iam-feed.json";
  var hudState = document.getElementById("hud-state"), hudSince = document.getElementById("hud-since"), hud = document.getElementById("hud");
  var nowEl = document.getElementById("now"), playBtn = document.getElementById("play");
  var lab = { state: "ok", since: null, events: [], seen: 0 };
  var ac = null, master = null, analyser = null, playing = false, stepTimer = null, padTimer = null, source = "lab";
  var fmt = function (iso) { try { return new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }); } catch (e) { return iso || ""; } };

  // --- state feed --------------------------------------------------------------------------------
  function applyState(s) {
    var prev = lab.state;
    lab.state = s.state === "fault" ? "fault" : "ok";
    lab.since = s.since || null; lab.events = s.events || [];
    hudState.textContent = lab.state === "ok" ? "every site answering" : "fault — " + (s.down || []).join(", ");
    hudSince.textContent = lab.since ? "· since " + fmt(lab.since) : "";
    hud.className = "hud" + (lab.state === "fault" ? " fault" : "");
    var latest = lab.events.length ? lab.events[0] : null;
    if (playing && latest && latest.at && latest.at !== lab.seen) { lab.seen = latest.at; if (latest.kind === "deploy") deployFigure(); }
    else if (latest && !lab.seen) lab.seen = latest.at;
    if (playing && prev !== lab.state) nowEl.textContent = lab.state === "ok" ? "Back to E major." : "Something is down. E minor until it recovers.";
  }
  function pollState() {
    fetch(STATE_URL, { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).then(function (s) {
      if (s) applyState(s); else { hudState.textContent = "state unavailable"; }
    }).catch(function () { hudState.textContent = "state unavailable"; });
  }
  pollState(); setInterval(pollState, 30000);

  // --- instrument ---------------------------------------------------------------------------------
  var NOTE = { e2: 82.41, e4: 329.63, g4: 392.0, gs4: 415.3, b4: 493.88, e5: 659.26, g5: 783.99, gs5: 830.61, b5: 987.77, e6: 1318.5 };
  var ARP_OK = ["e4", "gs4", "b4", "e5", "gs5", "b4", "e5", "gs4"], ARP_FAULT = ["e4", "g4", "b4", "e5", "g5", "b4", "e5", "g4"];
  function ensureAudio() {
    if (ac) return;
    ac = new (window.AudioContext || window.webkitAudioContext)();
    master = ac.createGain(); master.gain.value = 0.6;
    var delay = ac.createDelay(1.0); delay.delayTime.value = 0.375; var fb = ac.createGain(); fb.gain.value = 0.32; var wet = ac.createGain(); wet.gain.value = 0.35;
    var lp = ac.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 3200;
    master.connect(lp); lp.connect(delay); delay.connect(fb); fb.connect(delay); delay.connect(wet);
    analyser = ac.createAnalyser(); analyser.fftSize = 1024; analyser.smoothingTimeConstant = 0.82;
    lp.connect(analyser); wet.connect(analyser); analyser.connect(ac.destination);
  }
  function pluck(freq, amp, rel, t) {
    var o = ac.createOscillator(), g = ac.createGain(), f = ac.createBiquadFilter();
    o.type = "triangle"; o.frequency.value = freq; f.type = "lowpass"; f.frequency.setValueAtTime(freq * 6, t); f.frequency.exponentialRampToValueAtTime(freq * 1.5, t + rel);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(amp, t + 0.008); g.gain.exponentialRampToValueAtTime(0.0001, t + rel);
    o.connect(f); f.connect(g); g.connect(master); o.start(t); o.stop(t + rel + 0.05);
  }
  function pad(freq, amp, att, rel, t) {
    var g = ac.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(amp, t + att); g.gain.exponentialRampToValueAtTime(0.0001, t + att + rel);
    [0, 3, -3].forEach(function (cents) { var o = ac.createOscillator(); o.type = "sine"; o.frequency.value = freq * Math.pow(2, cents / 1200); o.connect(g); o.start(t); o.stop(t + att + rel + 0.1); });
    g.connect(master);
  }
  function bell(freq, amp, rel, t) {
    var g = ac.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(amp, t + 0.005); g.gain.exponentialRampToValueAtTime(0.0001, t + rel);
    [1, 2.76, 5.4].forEach(function (r, i) { var o = ac.createOscillator(); o.type = "sine"; o.frequency.value = freq * r; var pg = ac.createGain(); pg.gain.value = [1, 0.35, 0.12][i]; o.connect(pg); pg.connect(g); o.start(t); o.stop(t + rel + 0.05); });
    g.connect(master);
  }
  var step = 0;
  function arpTick() {
    var ok = lab.state === "ok", notes = ok ? ARP_OK : ARP_FAULT, dur = ok ? 0.5 : 0.75, i = step % 8, t = ac.currentTime + 0.05;
    if (ok || i % 2 === 0) pluck(NOTE[notes[i]], ok ? 0.28 : 0.22, ok ? 0.9 : 1.4, t);
    if (!ok && i === 0) pad(NOTE.e2, 0.12, 0.5, 2.5, t);
    step++; stepTimer = setTimeout(arpTick, dur * 1000);
  }
  function airTick() {
    var ok = lab.state === "ok", t = ac.currentTime + 0.05;
    pad(NOTE[ok ? "b4" : "g4"], 0.07, 3, 5, t); if (!ok || Math.random() > 0.33) pad(NOTE[ok ? "e5" : "e4"], 0.05, 4, 6, t);
    padTimer = setTimeout(airTick, 8000);
  }
  function deployFigure() {
    if (!ac) return; var t = ac.currentTime + 0.05;
    [["e5", 0], ["gs5", 0.2], ["b5", 0.4], ["e6", 0.6]].forEach(function (n) { bell(NOTE[n[0]], 0.18, n[1] === 0.6 ? 1.6 : 1.2, t + n[1]); });
    nowEl.textContent = "A deploy just landed in the lab."; breach();
  }
  function start() {
    ensureAudio(); if (ac.state === "suspended") ac.resume();
    playing = true; source = "lab"; step = 0; arpTick(); airTick(); draw();
    playBtn.textContent = "Stop"; nowEl.textContent = lab.state === "ok" ? "Playing: E major, every site answering." : "Playing: E minor, something is down.";
  }
  function stop() { playing = false; clearTimeout(stepTimer); clearTimeout(padTimer); playBtn.textContent = "Play the lab"; nowEl.textContent = "Stopped."; }
  playBtn.addEventListener("click", function () { playing && source === "lab" ? stop() : start(); });

  // --- the Salish Sea (visualizer) --------------------------------------------------------------
  // One full-page canvas: dusk sky, the Olympics, four wave layers, and Waku. Swell follows the low
  // end, light on the water follows the highs, a deploy is a breach. Runs idle (slow) with no audio.
  var sea = document.getElementById("sea"), sc = sea.getContext("2d"), dpr = Math.min(window.devicePixelRatio || 1, 2);
  var W = 0, H = 0, t0 = performance.now(), raf = null, freq = null, wave = null;
  var ORCA = { body: new Path2D("M100 312 C160 200 280 150 380 170 C430 180 470 220 462 250 C450 300 380 330 300 336 C220 342 150 340 100 336 Z"),
               belly: new Path2D("M120 330 C220 300 340 296 452 262 C420 316 250 340 120 330 Z"),
               dorsal: new Path2D("M256 200 C248 150 238 108 226 72 C272 100 312 138 332 194 Z"),
               pect: new Path2D("M318 316 C300 342 306 374 338 382 C358 364 354 330 342 310 Z"),
               fluke: new Path2D("M106 320 C72 286 42 292 18 314 C48 316 68 320 88 324 C68 334 50 348 30 372 C60 362 86 350 108 334 Z") };
  var orca = { x: 0.12, dir: 1, phase: 0.9, breach: 0, speed: 0.022 }; // x in screen widths, phase drives the dive cycle
  function resize() { W = sea.clientWidth; H = sea.clientHeight; sea.width = W * dpr; sea.height = H * dpr; sc.setTransform(dpr, 0, 0, dpr, 0, 0); }
  window.addEventListener("resize", resize); resize();
  function band(a, b) { if (!freq) return 0; var s = 0, n = 0; for (var i = a; i < b && i < freq.length; i++) { s += freq[i]; n++; } return n ? s / n / 255 : 0; }
  function drawOrca(x, y, scale, tilt, alpha) {
    sc.save(); sc.translate(x, y); sc.rotate(tilt); sc.scale(scale * (orca.dir), scale); sc.translate(-280, -300); sc.globalAlpha = alpha;
    sc.fillStyle = "#0b1220"; sc.fill(ORCA.fluke); sc.fill(ORCA.body); sc.fill(ORCA.dorsal);
    sc.fillStyle = "#f8fafc"; sc.globalAlpha = alpha * 0.9; sc.fill(ORCA.belly);
    sc.fillStyle = "#0b1220"; sc.globalAlpha = alpha; sc.fill(ORCA.pect);
    sc.restore();
  }
  function frame(now) {
    raf = requestAnimationFrame(frame);
    var t = (now - t0) / 1000, ok = lab.state === "ok", live = !!analyser && (playing || source === "rec");
    if (live) { freq = freq || new Uint8Array(analyser.frequencyBinCount); analyser.getByteFrequencyData(freq); }
    var low = live ? band(2, 12) : 0.12 + 0.05 * Math.sin(t * 0.5), high = live ? band(60, 200) : 0.05;
    var horizon = H * 0.46;
    // sky — dusk over the Sound; storm when something is down
    var sky = sc.createLinearGradient(0, 0, 0, horizon);
    if (ok) { sky.addColorStop(0, "#0b1220"); sky.addColorStop(0.55, "#1e3a4c"); sky.addColorStop(1, "#c2703a"); }
    else { sky.addColorStop(0, "#0b1220"); sky.addColorStop(0.6, "#27212b"); sky.addColorStop(1, "#7f1d1d"); }
    sc.fillStyle = sky; sc.fillRect(0, 0, W, horizon + 2);
    // the Olympics — two ridges
    sc.fillStyle = ok ? "#12283a" : "#1a1a22"; ridge(horizon, 0.11, 0.0011, 7, 0); sc.fillStyle = ok ? "#0d1c2a" : "#101018"; ridge(horizon, 0.07, 0.0019, 13, 40);
    // sea — four wave layers, amplitude from the low end
    var layers = [[0.02, 0.018, 0.9, ok ? "#134e4a" : "#2a1f28"], [0.05, 0.012, 0.6, ok ? "#0f766e" : "#3b1f28"], [0.09, 0.009, 0.45, ok ? "#115e59" : "#331b22"], [0.13, 0.007, 0.35, ok ? "#0b3b3a" : "#241419"]];
    for (var L = 0; L < layers.length; L++) {
      var yb = horizon + (H - horizon) * layers[L][0], amp = (6 + low * 34) * (1 - L * 0.15), k = layers[L][1], sp = layers[L][2];
      sc.beginPath(); sc.moveTo(0, H);
      for (var x = 0; x <= W; x += 6) sc.lineTo(x, yb + Math.sin(x * k + t * sp + L) * amp + Math.sin(x * k * 2.3 - t * sp * 1.7) * amp * 0.35);
      sc.lineTo(W, H); sc.closePath(); sc.fillStyle = layers[L][3]; sc.fill();
    }
    // light on the water — highs
    var g = sc.createLinearGradient(0, horizon, 0, H); g.addColorStop(0, "rgba(255,200,140," + (0.10 + high * 0.5) + ")"); g.addColorStop(1, "rgba(255,200,140,0)");
    sc.fillStyle = g; sc.fillRect(W * 0.55 - 60, horizon, 120 + high * 300, H - horizon);
    // Waku — cruises, dives, surfaces; breaches on deploy
    orca.phase += 0.004 + low * 0.01; orca.x += orca.speed * orca.dir / 60;
    if (orca.x > 1.25) orca.dir = -1; if (orca.x < -0.25) orca.dir = 1;
    var surf = Math.sin(orca.phase);                          // -1 deep … 1 surfaced
    var yO = horizon + (H - horizon) * 0.07 + (1 - surf) * 46 - orca.breach * 90;
    var tilt = (orca.dir * -Math.cos(orca.phase) * 0.25) - orca.breach * orca.dir * 0.7;
    var alpha = Math.max(0.15, Math.min(1, 0.55 + surf * 0.45 + orca.breach));
    if (orca.breach > 0) orca.breach = Math.max(0, orca.breach - 0.012);
    drawOrca(orca.x * W, yO, 0.36 + (surf + 1) * 0.05, tilt, alpha);
    if (surf > 0.85 || orca.breach > 0.5) { sc.fillStyle = "rgba(248,250,252,.7)"; for (var d = 0; d < 6; d++) sc.beginPath(), sc.arc(orca.x * W + (Math.random() - 0.5) * 120, yO - 30 - Math.random() * 40 * (1 + orca.breach), 2 + Math.random() * 3, 0, 6.28), sc.fill(); }
    // foam line at the horizon layer
    sc.strokeStyle = "rgba(248,250,252," + (0.08 + high * 0.3) + ")"; sc.lineWidth = 1; sc.beginPath();
    for (var x2 = 0; x2 <= W; x2 += 6) { var y2 = horizon + (H - horizon) * 0.02 + Math.sin(x2 * 0.018 + t * 0.9) * (6 + low * 34); x2 ? sc.lineTo(x2, y2) : sc.moveTo(x2, y2); }
    sc.stroke();
  }
  function ridge(horizon, hFrac, k, seed, off) { sc.beginPath(); sc.moveTo(0, horizon); for (var x = 0; x <= W; x += 8) sc.lineTo(x, horizon - H * hFrac * (0.55 + 0.45 * Math.abs(Math.sin(x * k + seed) * Math.sin(x * k * 2.7 + seed))) + off * 0.2); sc.lineTo(W, horizon); sc.closePath(); sc.fill(); }
  function draw() { if (!raf) raf = requestAnimationFrame(frame); }
  function breach() { orca.breach = 1; }
  draw();

  // --- recordings ----------------------------------------------------------------------------------
  var list = document.getElementById("episodes");
  fetch(FEED_URL, { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : { episodes: [] }; }).then(function (f) {
    list.innerHTML = "";
    if (!f.episodes || !f.episodes.length) { list.innerHTML = "<li><span class=\"ev\">No recordings published yet.</span></li>"; return; }
    f.episodes.forEach(function (e) {
      var li = document.createElement("li"), t = document.createElement("time"), d = document.createElement("div"), ev = document.createElement("span"), a = document.createElement("audio");
      t.dateTime = e.date; t.textContent = e.date + (e.seconds ? " · " + Math.round(e.seconds) + " s" : "");
      ev.className = "ev"; ev.textContent = (e.events || []).map(function (x) { return x.replace(/^\d{6}-/, ""); }).join(" · ") || "lab";
      a.controls = true; a.preload = "none"; a.src = "/media/" + e.m4a;
      a.addEventListener("play", function () { ensureAudio(); if (ac.state === "suspended") ac.resume(); if (playing) stop(); source = "rec"; if (!a._node) { a._node = ac.createMediaElementSource(a); a._node.connect(analyser); } draw(); nowEl.textContent = "Playing the lab's own recording from " + e.date + "."; });
      d.appendChild(ev); d.appendChild(a); li.appendChild(t); li.appendChild(d); list.appendChild(li);
    });
  }).catch(function () { list.innerHTML = "<li><span class=\"ev\">Recordings unavailable.</span></li>"; });
})();
