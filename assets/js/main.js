/* Hedef Vinç · menü, telefonda katlanan bölümler, blog süzgeci. Sayfa JS olmadan da eksiksiz çalışır. */
(function () {
  "use strict";
  var btn = document.querySelector(".hdr__menu");
  var nav = document.getElementById("menu");
  if (btn && nav) {
    var kapat = function () { nav.classList.remove("acik"); btn.setAttribute("aria-expanded", "false"); };
    btn.addEventListener("click", function () {
      var acik = nav.classList.toggle("acik");
      btn.setAttribute("aria-expanded", acik ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") kapat(); });
  }

  /* Telefonda uzun ikincil bölümler, içindekiler ve alt bölüm grupları kapalı başlar */
  if (window.matchMedia && window.matchMedia("(max-width: 859.98px)").matches) {
    document.querySelectorAll("details.katla").forEach(function (d) { d.open = false; });
  }

  /* Yatay kaydırılan galeride ekran dışındaki fotoğraflar, şerit görününce yüklensin */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (girdiler) {
      girdiler.forEach(function (g) {
        if (!g.isIntersecting) return;
        g.target.querySelectorAll('img[loading="lazy"]').forEach(function (i) { i.loading = "eager"; });
        io.unobserve(g.target);
      });
    }, { rootMargin: "300px 0px" });
    document.querySelectorAll(".galeri").forEach(function (g) { io.observe(g); });
  }

  /* Blog: kategori çipleri */
  var cipler = document.querySelectorAll(".cip[data-kat]");
  if (cipler.length) {
    var kartlar = document.querySelectorAll(".kart[data-kat]");
    cipler.forEach(function (c) {
      c.addEventListener("click", function () {
        var k = c.getAttribute("data-kat");
        cipler.forEach(function (x) { x.setAttribute("aria-pressed", x === c ? "true" : "false"); });
        kartlar.forEach(function (kart) { kart.hidden = !(k === "*" || kart.getAttribute("data-kat") === k); });
      });
    });
    document.querySelector(".cipler").hidden = false;
  }
})();
