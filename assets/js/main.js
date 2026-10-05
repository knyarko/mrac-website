(function () {
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("primary-nav");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Transparent header over the home hero turns solid once the page scrolls or the menu opens.
  function updateHeader() {
    if (!header || !header.classList.contains("overlay")) return;
    var open = nav && nav.classList.contains("open");
    header.classList.toggle("solid", open || window.scrollY > 40);
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
      updateHeader();
    });
    nav.addEventListener("click", function (ev) {
      if (ev.target.tagName === "A") {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        updateHeader();
      }
    });
  }

  // Scroll-reveal band: the photo drifts slower than the page, so it appears to be uncovered.
  var bands = Array.prototype.slice.call(document.querySelectorAll(".photo-band"));
  function updateBands() {
    if (reduceMotion) return;
    var vh = window.innerHeight;
    bands.forEach(function (band) {
      var r = band.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      var progress = (r.top + r.height / 2 - vh / 2) / (vh / 2 + r.height / 2); // -1..1
      band.querySelector(".band-img").style.transform = "translate3d(0," + (progress * 12).toFixed(2) + "%,0)";
    });
  }

  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      updateHeader();
      updateBands();
      ticking = false;
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  updateHeader();
  updateBands();

  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  // Highlight the nav item for the section in view (home page) or the current page.
  var links = Array.prototype.slice.call(document.querySelectorAll(".primary-nav a"));
  var page = location.pathname.split("/").pop() || "index.html";
  var sections = ["home", "key-areas", "members"]
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean);

  function setActive(href) {
    links.forEach(function (a) {
      a.classList.toggle("active", a.getAttribute("href").split("/").pop() === href);
    });
  }

  if (sections.length && "IntersectionObserver" in window) {
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) setActive("index.html#" + en.target.id);
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    sections.forEach(function (s) { obs.observe(s); });
  } else {
    var match = links.filter(function (a) {
      return a.getAttribute("href").split("/").pop().split("#")[0] === page;
    })[0];
    if (match) setActive(match.getAttribute("href").split("/").pop());
  }
})();
