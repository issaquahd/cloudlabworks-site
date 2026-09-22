// Code as Music — a browser copy of the lab's instrument (ops/iam/drone.rb) plus a visualizer.
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
  // The photo is the sea. This canvas is a light layer over it (mix-blend-mode: screen): shimmer on the
  // water follows the highs, slow swell lines follow the lows, a deploy sends rings across the water.
  var sea = document.getElementById("sea"), sc = sea.getContext("2d"), dim = document.getElementById("dim"), dpr = Math.min(window.devicePixelRatio || 1, 2);
  var W = 0, H = 0, t0 = performance.now(), raf = null, freq = null, rings = [];
  function resize() { W = sea.clientWidth; H = sea.clientHeight; sea.width = W * dpr; sea.height = H * dpr; sc.setTransform(dpr, 0, 0, dpr, 0, 0); }
  window.addEventListener("resize", resize); resize();
  function band(a, b) { if (!freq) return 0; var s = 0, n = 0; for (var i = a; i < b && i < freq.length; i++) { s += freq[i]; n++; } return n ? s / n / 255 : 0; }
  function frame(now) {
    raf = requestAnimationFrame(frame);
    var t = (now - t0) / 1000, ok = lab.state === "ok", live = !!analyser && (playing || source === "rec");
    if (live) { freq = freq || new Uint8Array(analyser.frequencyBinCount); analyser.getByteFrequencyData(freq); }
    var low = live ? band(2, 12) : 0.10 + 0.04 * Math.sin(t * 0.4), high = live ? band(60, 200) : 0.04;
    dim.className = ok ? "" : "fault";
    drawScope(live, ok);
    sc.clearRect(0, 0, W, H);
    var water = H * 0.45;                                             // the water starts roughly mid-frame in the photo
    // swell — three translucent bands drifting across the lower half, amplitude from the low end
    for (var L = 0; L < 3; L++) {
      var yb = water + (H - water) * (0.25 + L * 0.25), amp = (4 + low * 26) * (1 - L * 0.2), k = 0.012 - L * 0.002, sp = 0.5 + L * 0.2;
      sc.beginPath();
      for (var x = 0; x <= W; x += 8) { var y = yb + Math.sin(x * k + t * sp + L * 2) * amp + Math.sin(x * k * 2.1 - t * sp * 1.6) * amp * 0.4; x ? sc.lineTo(x, y) : sc.moveTo(x, y); }
      sc.strokeStyle = ok ? "rgba(153,246,228," + (0.10 + low * 0.35) + ")" : "rgba(252,165,165," + (0.10 + low * 0.35) + ")"; sc.lineWidth = 1.5 + low * 3; sc.stroke();
    }
    // shimmer — a soft glow on the water that breathes with the highs
    var g = sc.createRadialGradient(W * 0.62, water + (H - water) * 0.35, 10, W * 0.62, water + (H - water) * 0.35, W * 0.35 + high * W * 0.4);
    g.addColorStop(0, ok ? "rgba(255,214,170," + (0.12 + high * 0.6) + ")" : "rgba(255,170,170," + (0.10 + high * 0.5) + ")"); g.addColorStop(1, "rgba(0,0,0,0)");
    sc.fillStyle = g; sc.fillRect(0, water, W, H - water);
    // sparkle — points of light on the water, more with the highs
    var n = 6 + Math.floor(high * 60); sc.fillStyle = "rgba(255,255,255," + (0.25 + high * 0.5) + ")";
    for (var i = 0; i < n; i++) { var px = (Math.sin(i * 12.9898 + Math.floor(t * 2)) * 43758.5453) % 1; px = Math.abs(px); var py = Math.abs((Math.sin(i * 78.233 + Math.floor(t * 2)) * 12345.678) % 1); sc.fillRect(px * W, water + py * (H - water), 2, 1); }
    // rings — a deploy sends them across the water from where the dorsal fin is in the photo
    for (var r = rings.length - 1; r >= 0; r--) { var R = rings[r]; R.a += 2.6; R.life -= 0.006; if (R.life <= 0) { rings.splice(r, 1); continue; }
      sc.beginPath(); sc.ellipse(W * 0.78, water + (H - water) * 0.1, R.a, R.a * 0.28, 0, 0, 6.283); sc.strokeStyle = "rgba(226,232,240," + (R.life * 0.6) + ")"; sc.lineWidth = 2; sc.stroke(); }
  }
  // --- the sound graph (next to the play button): spectrum bars coloured by pitch, the waveform drawn over them
  var scope = document.getElementById("scope"), gc = scope ? scope.getContext("2d") : null, wave = null;
  function drawScope(live, ok) {
    if (!gc) return;
    var w = scope.width, h = scope.height;
    gc.clearRect(0, 0, w, h);
    var bars = 64, top = Math.min(freq ? freq.length : 512, 360);        // ~0 to 7.7 kHz at 44.1k / fftSize 1024
    for (var b = 0; b < bars; b++) {
      var i0 = Math.floor(Math.pow(b / bars, 1.6) * top), i1 = Math.max(i0 + 1, Math.floor(Math.pow((b + 1) / bars, 1.6) * top)), v = 0;
      if (live && freq) { for (var i = i0; i < i1; i++) v = Math.max(v, freq[i]); v /= 255; }
      else v = 0.04 + 0.03 * Math.sin(b * 0.5 + performance.now() / 900);
      var hue = ok ? 38 + (b / bars) * 140 : 350 + (b / bars) * 30;        // amber -> teal when ok; reds when down
      var bw = w / bars, bh = Math.max(2, v * (h - 24));
      gc.fillStyle = "hsla(" + hue + ",85%," + (48 + v * 22) + "%," + (0.35 + v * 0.6) + ")";
      gc.fillRect(b * bw + 1, h - 12 - bh, bw - 2, bh);
    }
    if (live && analyser) {
      wave = wave || new Uint8Array(analyser.fftSize); analyser.getByteTimeDomainData(wave);
      gc.beginPath();
      for (var x = 0; x < w; x++) { var s = wave[Math.floor(x / w * wave.length)] / 128 - 1; var y = h * 0.42 + s * h * 0.36; x ? gc.lineTo(x, y) : gc.moveTo(x, y); }
      gc.strokeStyle = ok ? "rgba(248,250,252,.85)" : "rgba(254,202,202,.85)"; gc.lineWidth = 1.6; gc.stroke();
    } else {
      gc.beginPath(); gc.moveTo(0, h * 0.42); gc.lineTo(w, h * 0.42); gc.strokeStyle = "rgba(226,232,240,.25)"; gc.lineWidth = 1; gc.stroke();
    }
  }
  function draw() { if (!raf) raf = requestAnimationFrame(frame); }
  function breach() { rings.push({ a: 6, life: 1 }); setTimeout(function () { rings.push({ a: 6, life: 1 }); }, 350); setTimeout(function () { rings.push({ a: 6, life: 1 }); }, 700); }
  draw();

  // --- recordings ----------------------------------------------------------------------------------
  var list = document.getElementById("episodes");
  fetch(FEED_URL, { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : { episodes: [] }; }).then(function (f) {
    list.innerHTML = "";
    if (!f.episodes || !f.episodes.length) { list.innerHTML = "<li><span class=\"ev\">No recordings published yet.</span></li>"; return; }
    f.episodes.forEach(function (e) {
      var li = document.createElement("li"), t = document.createElement("time"), d = document.createElement("div"), ev = document.createElement("span"), a = document.createElement("audio");
      t.dateTime = e.date; t.textContent = e.date + (e.seconds ? " · " + Math.round(e.seconds) + " s" : "");
      ev.className = "ev"; ev.textContent = (e.title ? e.title + " · " : "") + ((e.events || []).map(function (x) { return x.replace(/^\d{6}-/, ""); }).join(" · ") || "lab");
      if (e.art) { var im = document.createElement("img"); im.className = "art"; im.draggable = false; im.src = "/media/" + e.art; im.alt = "Art drawn from this recording: " + e.date; im.loading = "lazy"; d.appendChild(im); }
      if (e.haiku && e.haiku.length) { var hk = document.createElement("p"); hk.className = "haiku"; e.haiku.forEach(function (ln, i) { if (i) hk.appendChild(document.createElement("br")); hk.appendChild(document.createTextNode(ln)); }); d.appendChild(hk); }
      a.controls = true; a.preload = "none"; a.src = "/media/" + e.m4a;
      a.addEventListener("play", function () { ensureAudio(); if (ac.state === "suspended") ac.resume(); if (playing) stop(); source = "rec"; if (!a._node) { a._node = ac.createMediaElementSource(a); a._node.connect(analyser); } draw(); nowEl.textContent = "Playing the lab's own recording from " + e.date + "."; });
      d.appendChild(ev); d.appendChild(a); li.appendChild(t); li.appendChild(d); list.appendChild(li);
    });
  }).catch(function () { list.innerHTML = "<li><span class=\"ev\">Recordings unavailable.</span></li>"; });
})();
