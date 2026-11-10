/* Portfolio Yoan Rousselot : navigation, filtres, animations, visionneuse */
(function () {
  "use strict";
  document.documentElement.classList.add("js");

  /* En-tête : ombre au défilement */
  var header = document.querySelector(".site-header");
  function onScroll() { header && header.classList.toggle("scrolled", window.scrollY > 8); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Menu mobile */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".main-nav");
  function closeNav() {
    if (!toggle) return;
    toggle.setAttribute("aria-expanded", "false");
    nav.classList.remove("open");
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("open", open);
    });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) closeNav(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeNav(); });
  }

  /* Lien actif selon la section visible (page d'accueil) */
  var links = document.querySelectorAll("[data-nav]");
  if (document.body.classList.contains("home") && "IntersectionObserver" in window) {
    var map = {};
    links.forEach(function (a) { map[a.dataset.nav] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var id = en.target.id === "about" ? "profil" : en.target.id;
        links.forEach(function (a) { a.classList.toggle("active", a.dataset.nav === id); });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    document.querySelectorAll("main section[id]").forEach(function (s) { spy.observe(s); });
  }

  /* Apparition au défilement */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* Filtres du parcours */
  var filters = document.querySelectorAll(".filter");
  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var f = btn.dataset.filter;
      filters.forEach(function (b) {
        b.classList.toggle("active", b === btn);
        b.setAttribute("aria-pressed", String(b === btn));
      });
      document.querySelectorAll(".tl-item").forEach(function (it) {
        var show = f === "all" || it.dataset.kind === f;
        it.hidden = !show;
        if (show) it.querySelector(".reveal, .card") && it.classList.add("in");
      });
    });
  });

  /* Cartes du parcours entièrement cliquables */
  document.querySelectorAll(".tl-card.is-link").forEach(function (card) {
    var a = card.querySelector("a.btn");
    card.style.cursor = "pointer";
    card.addEventListener("click", function (e) {
      if (e.target.closest("a")) return;
      if (window.getSelection && String(window.getSelection())) return;
      a && a.click();
    });
  });

  /* Visionneuse d'images */
  var lb = document.getElementById("lightbox");
  var items = Array.prototype.slice.call(document.querySelectorAll(".g-open"));
  if (lb && items.length) {
    var img = lb.querySelector("img"), cap = lb.querySelector("figcaption"), idx = 0, lastFocus = null;
    var show = function (i) {
      idx = (i + items.length) % items.length;
      img.src = items[idx].dataset.src;
      img.alt = items[idx].dataset.caption;
      cap.textContent = items[idx].dataset.caption;
    };
    var open = function (i) {
      lastFocus = document.activeElement;
      show(i); lb.hidden = false; document.body.style.overflow = "hidden";
      lb.querySelector(".lb-close").focus();
    };
    var close = function () {
      lb.hidden = true; document.body.style.overflow = "";
      lastFocus && lastFocus.focus();
    };
    items.forEach(function (b, i) { b.addEventListener("click", function () { open(i); }); });
    lb.querySelector(".lb-close").addEventListener("click", close);
    lb.querySelector(".lb-prev").addEventListener("click", function () { show(idx - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function () { show(idx + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (lb.hidden) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(idx - 1);
      if (e.key === "ArrowRight") show(idx + 1);
    });
    if (items.length < 2) lb.querySelectorAll(".lb-nav").forEach(function (b) { b.hidden = true; });
  }
})();
