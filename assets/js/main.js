(function () {
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("primary-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    nav.addEventListener("click", function (ev) {
      if (ev.target.tagName === "A") {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  // Highlight the nav item for the section currently in view (home page only).
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
