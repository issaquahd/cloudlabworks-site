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
