// Hamburger drawer: the checkbox does open/close without script; this adds Escape, Enter/Space on the
// labels, and moves focus into the drawer so the keyboard works the same as the pointer.
(function () {
  var t = document.getElementById("menu-t"), menu = document.getElementById("menu"); if (!t || !menu) return;
  var btn = document.querySelector(".menu-btn");
  function set(open) { t.checked = open; document.documentElement.classList.toggle("menu-open", open); if (open) { var a = menu.querySelector("a"); if (a) a.focus(); } else if (btn) btn.focus(); }
  t.addEventListener("change", function () { set(t.checked); });
  document.querySelectorAll('label[for="menu-t"]').forEach(function (l) {
    l.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); set(!t.checked); } });
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && t.checked) set(false); });
  menu.addEventListener("click", function (e) { if (e.target.closest("a")) set(false); });
})();

// Footer status: the lab's own health probe, published as /media/iam-state.json by the deploy and the nightly
// tools (state ok|fault, down[], generated). Green when ok and fresh, red on a fault, amber when the file is
// older than a day (the probe stopped), grey when it cannot be read at all. This script is loaded from the header,
// before the footer is parsed, so the probe waits for DOMContentLoaded.
(function probe() {
  if (document.readyState === "loading") return document.addEventListener("DOMContentLoaded", probe);
  var el = document.getElementById("lab-status"); if (!el) return;
  var set = function (state, text) { el.setAttribute("data-state", state); el.lastChild.nodeValue = text; };
  fetch("/media/iam-state.json", { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).then(function (s) {
    if (!s || !s.state) return set("unknown", "Status unknown");
    var age = (Date.now() - Date.parse(s.generated || 0)) / 36e5;
    var when = s.generated ? new Date(s.generated).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "";
    if (s.state !== "ok") return set("fault", "Fault" + (s.down && s.down.length ? " (" + s.down.join(", ") + ")" : "") + (when ? " · " + when : ""));
    if (age > 24) return set("stale", "Live, unverified since " + when);
    set("ok", "Live" + (when ? " · " + when : ""));
  }).catch(function () { set("unknown", "Status unknown"); });
})();
