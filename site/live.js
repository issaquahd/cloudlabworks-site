// IaC Live Music — a browser copy of the lab's instrument (ops/iam/drone.rb) plus a visualizer.
// Self-hosted, no third-party requests. State comes from /media/iam-state.json; recordings from /media/iam-feed.json.
(function () {
  "use strict";
  var STATE_URL = "/media/iam-state.json", FEED_URL = "/media/iam-feed.json";
  var hudState = document.getElementById("hud-state"), hudSince = document.getElementById("hud-since"), hud = document.getElementById("hud");
  var nowEl = document.getElementById("now"), playBtn = document.getElementById("play"), canvas = document.getElementById("viz");
  var ctx2d = canvas.getContext("2d");
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
    nowEl.textContent = "A deploy just landed in the lab.";
  }
  function start() {
    ensureAudio(); if (ac.state === "suspended") ac.resume();
    playing = true; source = "lab"; step = 0; arpTick(); airTick(); draw();
    playBtn.textContent = "Stop"; nowEl.textContent = lab.state === "ok" ? "Playing: E major, every site answering." : "Playing: E minor, something is down.";
  }
  function stop() { playing = false; clearTimeout(stepTimer); clearTimeout(padTimer); playBtn.textContent = "Play the lab"; nowEl.textContent = "Stopped."; }
  playBtn.addEventListener("click", function () { playing && source === "lab" ? stop() : start(); });

  // --- visualizer ---------------------------------------------------------------------------------
  var raf = null, freq = null, wave = null;
  function draw() {
    if (raf) return;
    var W = canvas.width, H = canvas.height, ok;
    (function frame() {
      raf = requestAnimationFrame(frame);
      if (!analyser) return;
      freq = freq || new Uint8Array(analyser.frequencyBinCount); wave = wave || new Uint8Array(analyser.fftSize);
      analyser.getByteFrequencyData(freq); analyser.getByteTimeDomainData(wave); ok = lab.state === "ok";
      ctx2d.fillStyle = "rgba(11,18,32,0.28)"; ctx2d.fillRect(0, 0, W, H);
      var bars = 64, bw = W / bars;
      for (var i = 0; i < bars; i++) {
        var v = freq[Math.floor(i * 3.2)] / 255, h = v * v * (H - 40);
        ctx2d.fillStyle = ok ? "rgba(45,212,191," + (0.25 + v * 0.7) + ")" : "rgba(248,113,113," + (0.25 + v * 0.7) + ")";
        ctx2d.fillRect(i * bw + 2, H - h, bw - 4, h);
      }
      ctx2d.beginPath(); ctx2d.strokeStyle = ok ? "#e2e8f0" : "#fca5a5"; ctx2d.lineWidth = 1.5;
      for (var j = 0; j < wave.length; j += 4) { var x = j / wave.length * W, y = H * 0.42 + (wave[j] - 128) / 128 * H * 0.3; j ? ctx2d.lineTo(x, y) : ctx2d.moveTo(x, y); }
      ctx2d.stroke();
    })();
  }
  // idle frame so the stage is not black before play
  ctx2d.fillStyle = "#0b1220"; ctx2d.fillRect(0, 0, canvas.width, canvas.height);
  ctx2d.strokeStyle = "#1e293b"; ctx2d.beginPath(); ctx2d.moveTo(0, canvas.height * 0.42); ctx2d.lineTo(canvas.width, canvas.height * 0.42); ctx2d.stroke();

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
