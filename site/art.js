// /art: fill the nightly card's haiku from the published feed (no third-party requests).
(function () {
  var el = document.getElementById("haiku-latest"); if (!el) return;
  fetch("/media/iam-feed.json", { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).then(function (f) {
    var e = f && f.episodes && f.episodes[0]; if (!e || !e.haiku) return;
    e.haiku.forEach(function (ln, i) { if (i) el.appendChild(document.createElement("br")); el.appendChild(document.createTextNode(ln)); });
    var d = document.createElement("small"); d.textContent = " " + e.date; d.style.opacity = ".7"; el.appendChild(d);
  }).catch(function () {});
})();
