// Digital rain with the words set inside it: glyphs falling everywhere, brighter where they cross the
// letters of CLOUDLAB WORKS, so the mark is made of the running code rather than laid over it. Drawn here,
// no film artwork used. Static single frame when the visitor prefers reduced motion.
(function () {
  var cv = document.getElementById("matrix");
  if (!cv || !cv.getContext) return;
  var W = cv.width, H = cv.height, ctx = cv.getContext("2d");
  var GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789Z:・=*+-<>¦|";
  var cell = 22, cols = Math.floor(W / cell), rows = Math.floor(H / cell);
  var drops = [], speed = [];
  for (var i = 0; i < cols; i++) { drops[i] = Math.floor(Math.random() * rows); speed[i] = 0.5 + Math.random() * 0.9; }

  // the word, as a mask: one letter row across the middle, the small line above it
  var mask = document.createElement("canvas"); mask.width = W; mask.height = H;
  var m = mask.getContext("2d");
  m.fillStyle = "#fff"; m.textAlign = "center"; m.textBaseline = "middle";
  m.font = "900 " + Math.floor(W * 0.19) + "px 'Courier New', Courier, monospace";
  m.fillText("CLOUDLAB", W / 2, H * 0.43);
  m.fillText("WORKS", W / 2, H * 0.57);
  var md = m.getImageData(0, 0, W, H).data;
  m.globalCompositeOperation = "source-in"; m.fillStyle = "#39ff14"; m.fillRect(0, 0, W, H); m.globalCompositeOperation = "source-over";
  function inWord(x, y) { var px = Math.min(W - 1, Math.max(0, x | 0)), py = Math.min(H - 1, Math.max(0, y | 0)); return md[(py * W + px) * 4 + 3] > 40; }
  // cells whose centre falls inside a letter: these stay lit so the word reads at every moment
  var wcell = 11, wordCells = [];
  for (var c = 0; c < Math.floor(W / wcell); c++) for (var r = 0; r < Math.floor(H / wcell); r++) if (inWord(c * wcell + wcell / 2, r * wcell + wcell / 2)) wordCells.push([c * wcell, r * wcell]);
  var wordFont = "bold " + (wcell - 1) + "px 'Courier New', Courier, monospace";
  var rainFont = "bold " + (cell - 4) + "px 'Courier New', Courier, monospace";

  ctx.fillStyle = "#000"; ctx.fillRect(0, 0, W, H);
  ctx.font = rainFont;
  ctx.textBaseline = "top";
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function frame() {
    ctx.fillStyle = "rgba(0,0,0,0.09)"; ctx.fillRect(0, 0, W, H);
    for (var i = 0; i < cols; i++) {
      var x = i * cell, y = Math.floor(drops[i]) * cell;
      var ch = GLYPHS.charAt(Math.floor(Math.random() * GLYPHS.length));
      var hot = inWord(x + cell / 2, y + cell / 2);
      ctx.shadowBlur = hot ? 14 : 0; ctx.shadowColor = "#7dff9a";
      ctx.fillStyle = hot ? "#e8ffe8" : (Math.random() < 0.08 ? "#b6ffc6" : "#1fbf4f");
      ctx.fillText(ch, x + 2, y + 2);
      drops[i] += speed[i];
      if (drops[i] * cell > H && Math.random() > 0.975) drops[i] = 0;
    }
    // the word: a faint solid glow under it, then most of its fine cells re-lit each frame, so it
    // reads at every moment and is still made of code
    ctx.globalAlpha = 0.10; ctx.shadowBlur = 24; ctx.shadowColor = "#39ff14"; ctx.drawImage(mask, 0, 0); ctx.globalAlpha = 1;
    ctx.font = wordFont; ctx.shadowBlur = 6;
    for (var w = 0; w < wordCells.length; w++) {
      if (Math.random() < 0.7) { ctx.fillStyle = Math.random() < 0.12 ? "#f2fff2" : "#8cf59c"; ctx.fillText(GLYPHS.charAt(Math.floor(Math.random() * GLYPHS.length)), wordCells[w][0] + 1, wordCells[w][1] + 1); }
    }
    ctx.font = rainFont; ctx.shadowBlur = 0;
  }
  if (reduced) { for (var k = 0; k < 90; k++) frame(); return; }
  var running = true;
  document.addEventListener("visibilitychange", function () { running = !document.hidden; });
  (function loop() { if (running) frame(); setTimeout(function () { requestAnimationFrame(loop); }, 55); })();
})();
