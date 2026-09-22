// Live Test Pipeline: reads /media/tests.json (current rows) and /media/tests-feed.json (transitions), both written by the
// lab's test poster and shipped on the asset path. Self-hosted, no third-party requests. Renders the home strip and /tests.
(function () {
  "use strict";
  var cur = document.getElementById("tests-rows"), feedEl = document.getElementById("tests-feed"), gen = document.getElementById("tests-generated");
  if (!cur && !feedEl) return;
  var LABEL = { pass: "Pass", fail: "Fail", wip: "In progress", planned: "Planned", finished: "Finished" };
  var when = function (iso) { try { return new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }); } catch (e) { return iso || ""; } };
  var el = function (tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  function row(t, compact) {
    var li = el("li", "trow " + t.status);
    var st = el("span", "st " + t.status, LABEL[t.status] || t.status);
    var name = el("b", null, t.name);
    var head = el("div", "head"); head.appendChild(st); head.appendChild(name);
    li.appendChild(head);
    if (!compact) li.appendChild(el("span", "check", t.check));
    var meta = el("small", "meta", (t.status === "fail" && t.runs > 1 ? "failing for " + t.runs + " runs · " : "") + "last run " + when(t.last_run) + (t.last_transition ? " · last change " + when(t.last_transition) : ""));
    li.appendChild(meta);
    if (t.status === "fail" && t.failure) li.appendChild(el("span", "fail", t.failure));
    return li;
  }
  if (cur) {
    var compact = cur.hasAttribute("data-compact");
    fetch("/media/tests.json", { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
      cur.innerHTML = "";
      if (!d || !d.tests || !d.tests.length) { cur.appendChild(el("li", "empty", "No tests published yet.")); return; }
      d.tests.forEach(function (t) { cur.appendChild(row(t, compact)); });
      if (gen) gen.textContent = "Updated " + when(d.generated) + ".";
    }).catch(function () { cur.innerHTML = ""; cur.appendChild(el("li", "empty", "Test data unavailable.")); });
  }
  if (feedEl) {
    fetch("/media/tests-feed.json", { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
      feedEl.innerHTML = "";
      if (!d || !d.items || !d.items.length) { feedEl.appendChild(el("li", "empty", "No transitions yet.")); return; }
      d.items.slice(0, 50).forEach(function (i) {
        var li = el("li", "titem " + i.to);
        li.appendChild(el("time", null, when(i.at)));
        var d2 = el("div"); d2.appendChild(el("b", null, i.name)); d2.appendChild(el("span", "arrow", (i.from ? LABEL[i.from] || i.from : "new") + " → " + (LABEL[i.to] || i.to)));
        if (i.note) d2.appendChild(el("small", "note", i.note));
        li.appendChild(d2); feedEl.appendChild(li);
      });
    }).catch(function () { feedEl.innerHTML = ""; feedEl.appendChild(el("li", "empty", "Feed unavailable.")); });
  }
})();
