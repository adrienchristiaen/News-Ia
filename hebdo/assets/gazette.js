// Bascule Lumos / Nox. Sans JavaScript, le site suit le thème du système.
(function () {
  var root = document.documentElement;
  var media = window.matchMedia("(prefers-color-scheme: dark)");
  function sombre() {
    var t = root.dataset.theme;
    return t ? t === "dark" : media.matches;
  }
  function maj() {
    // Libellé fixe, état porté par aria-pressed : « Mode nuit (Nox), activé ».
    document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
      b.hidden = false;
      b.setAttribute("aria-pressed", String(sombre()));
    });
    // La barre du navigateur mobile suit le thème choisi.
    var fond = getComputedStyle(root).getPropertyValue("--papier").trim();
    document.querySelectorAll('meta[name="theme-color"]').forEach(function (m) {
      if (fond) m.setAttribute("content", fond);
    });
  }
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest("[data-theme-toggle]");
    if (!b) return;
    var t = sombre() ? "light" : "dark";
    root.dataset.theme = t;
    try { localStorage.setItem("gazette-theme", t); } catch (_) {}
    maj();
  });
  media.addEventListener("change", maj);
  maj();
})();
