// Digital rain with the word set inside it: glyphs falling everywhere, brighter where they cross the
// letters of MATRIX, so the mark is made of the running code rather than laid over it. Drawn here,
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
  m.font = "900 " + Math.floor(W * 0.235) + "px 'Courier New', Courier, monospace";
  m.fillText("MATRIX", W / 2, H * 0.50);
  m.font = "700 " + Math.floor(W * 0.062) + "px 'Courier New', Courier, monospace";
  m.fillText("THE", W / 2, H * 0.34);
  var md = m.getImageData(0, 0, W, H).data;
  function inWord(x, y) { var px = Math.min(W - 1, Math.max(0, x | 0)), py = Math.min(H - 1, Math.max(0, y | 0)); return md[(py * W + px) * 4 + 3] > 40; }

  ctx.fillStyle = "#000"; ctx.fillRect(0, 0, W, H);
  ctx.font = "bold " + (cell - 4) + "px 'Courier New', Courier, monospace";
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
      // keep the word legible between drops: a dim glyph on every cell inside the letters, sometimes
      if (Math.random() < 0.12) {
        var yy = Math.floor(Math.random() * rows) * cell;
        if (inWord(x + cell / 2, yy + cell / 2)) { ctx.shadowBlur = 6; ctx.fillStyle = "#5fe37f"; ctx.fillText(GLYPHS.charAt(Math.floor(Math.random() * GLYPHS.length)), x + 2, yy + 2); }
      }
      drops[i] += speed[i];
      if (drops[i] * cell > H && Math.random() > 0.975) drops[i] = 0;
    }
    ctx.shadowBlur = 0;
  }
  if (reduced) { for (var k = 0; k < 90; k++) frame(); return; }
  var running = true;
  document.addEventListener("visibilitychange", function () { running = !document.hidden; });
  (function loop() { if (running) frame(); setTimeout(function () { requestAnimationFrame(loop); }, 55); })();
})();
