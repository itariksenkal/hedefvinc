/* HEDEF VİNÇ — site etkileşimleri */
(function () {
  "use strict";

  /* Kayan başlıkta gölge */
  var header = document.querySelector(".header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* Mobil menü */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".nav");
  var overlay = document.querySelector(".nav-overlay");
  function closeNav() {
    if (!nav) return;
    nav.classList.remove("is-open");
    if (toggle) {
      toggle.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    }
    if (overlay) overlay.classList.remove("is-visible");
    document.body.style.overflow = "";
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (overlay) overlay.classList.toggle("is-visible", open);
      document.body.style.overflow = open ? "hidden" : "";
    });
  }
  if (overlay) overlay.addEventListener("click", closeNav);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeNav();
  });

  /* Hizmetler açılır menüsü */
  document.querySelectorAll(".nav__drop").forEach(function (drop) {
    var btn = drop.querySelector("button");
    if (!btn) return;
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = drop.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  document.addEventListener("click", function (e) {
    document.querySelectorAll(".nav__drop.is-open").forEach(function (drop) {
      if (!drop.contains(e.target)) {
        drop.classList.remove("is-open");
        var btn = drop.querySelector("button");
        if (btn) btn.setAttribute("aria-expanded", "false");
      }
    });
  });

  /* SSS akordiyonu */
  document.querySelectorAll(".faq-item__q").forEach(function (q) {
    q.addEventListener("click", function () {
      var item = q.closest(".faq-item");
      var answer = item.querySelector(".faq-item__a");
      var isOpen = item.classList.contains("is-open");

      document.querySelectorAll(".faq-item.is-open").forEach(function (other) {
        if (other !== item) {
          other.classList.remove("is-open");
          var a = other.querySelector(".faq-item__a");
          if (a) a.style.maxHeight = "0px";
          var ob = other.querySelector(".faq-item__q");
          if (ob) ob.setAttribute("aria-expanded", "false");
        }
      });

      item.classList.toggle("is-open", !isOpen);
      q.setAttribute("aria-expanded", !isOpen ? "true" : "false");
      if (answer) {
        answer.style.maxHeight = !isOpen ? answer.scrollHeight + "px" : "0px";
      }
    });
  });

  /* Sayaç animasyonu (istatistik bandı) */
  function animateCount(el) {
    var target = parseInt(el.getAttribute("data-count"), 10);
    if (isNaN(target)) return;
    var suffix = el.getAttribute("data-suffix") || "";
    var dur = 1200;
    var start = null;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ("IntersectionObserver" in window) {
    var statIo = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCount(entry.target);
            statIo.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    document.querySelectorAll("[data-count]").forEach(function (el) {
      statIo.observe(el);
    });
  } else {
    document.querySelectorAll("[data-count]").forEach(function (el) {
      el.textContent = el.getAttribute("data-count") + (el.getAttribute("data-suffix") || "");
    });
  }

  /* Görünürlük animasyonu */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    document.querySelectorAll(".reveal").forEach(function (el) {
      io.observe(el);
    });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) {
      el.classList.add("is-visible");
    });
  }
})();
