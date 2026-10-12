// Bascule Lumos / Nox. Sans JavaScript, le site suit le thème du système.
(function () {
  var root = document.documentElement;
  var media = window.matchMedia("(prefers-color-scheme: dark)");
  function sombre() {
    var t = root.dataset.theme;
    return t ? t === "dark" : media.matches;
  }
  function maj() {
    document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(sombre()));
      b.setAttribute("aria-label", sombre() ? "Passer en mode jour (Lumos)" : "Passer en mode nuit (Nox)");
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
