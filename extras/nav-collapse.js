/**
 * Desktop sidebar collapse for Material's nested nav.
 *
 * Background: Material only collapses nested nav sections on mobile by
 * default. On desktop, the section's <nav class="md-nav"> is always
 * visible, regardless of the toggling checkbox state — so clicking the
 * chapter title appears to do nothing.
 *
 * Fix:
 *   1. Inject CSS to hide the nested <nav> when its checkbox is unchecked.
 *   2. Default-collapse every section except the one containing the active
 *      page (so non-current chapters start folded).
 *   3. Bind a click handler on each section's <label> that toggles the
 *      checkbox ourselves. The native <label for> indirection occasionally
 *      gets swallowed by parent <li> event handling, so we don't rely on
 *      it for the toggle.
 *
 * Re-runs on every Material page swap (navigation.instant) via document$.
 */
(function () {
  "use strict";

  function ensureStyle() {
    if (document.getElementById("nav-collapse-style")) return;
    var s = document.createElement("style");
    s.id = "nav-collapse-style";
    // General-sibling selector: when the checkbox is unchecked, hide the
    // sub-nav that follows it. Desktop only — Material handles mobile.
    s.textContent = [
      "@media screen and (min-width: 960px) {",
      "  .md-sidebar--primary .md-nav__item--nested > .md-toggle:not(:checked) ~ .md-nav {",
      "    display: none !important;",
      "  }",
      "}",
    ].join("\n");
    document.head.appendChild(s);
  }

  function applyDefaultState() {
    var sections = document.querySelectorAll(
      ".md-sidebar--primary .md-nav__item--nested"
    );
    if (!sections.length) return;

    // Find which section contains the currently-active link. Material sets
    // .md-nav__link--active on the <a> of the current page; we walk up the
    // DOM to find its enclosing nested section. This is more reliable than
    // checking section.classList.contains('--active'), which Material 9.x
    // doesn't always set on the parent <li>.
    // NOTE: For non-default languages, lang-switcher.js rewrites the sidebar
    // link hrefs client-side, which means Material's initial active-link
    // detection (done at render time on the original hrefs) misses. So
    // on translated editions, nothing reports as active. To handle both
    // cases we default-expand everything — readers can collapse to declutter.
    var activeSection = null;
    var activeLink = document.querySelector(
      ".md-sidebar--primary a.md-nav__link--active"
    );
    if (activeLink) {
      var node = activeLink;
      while (node && node !== document) {
        if (node.classList && node.classList.contains("md-nav__item--nested")) {
          activeSection = node;
          break;
        }
        node = node.parentElement;
      }
    }

    sections.forEach(function (section) {
      var checkbox = section.querySelector(":scope > .md-toggle");
      var label = section.querySelector(":scope > label.md-nav__link");
      if (!checkbox) return;
      // Don't re-set state on every SPA swap if user has already toggled;
      // only initialise the first time we see this section.
      if (section.dataset.navInit === "1") return;
      section.dataset.navInit = "1";

      var isActive = (section === activeSection) ||
                     section.classList.contains("md-nav__item--active");
      // If no section reports as active (common on translated editions where
      // Material's active detection missed), default-expand this section so
      // its sub-items remain reachable.
      if (!activeSection) isActive = true;
      checkbox.checked = !!isActive;
      // NOTE: We do NOT bind our own click handler on the <label>. The native
      // <label for="..."> mechanism already toggles the checkbox on click,
      // and adding our own handler caused double-toggle bugs.
    });
  }

  function init() {
    ensureStyle();
    applyDefaultState();
  }

  document.addEventListener("DOMContentLoaded", init);
  if (window.document$) window.document$.subscribe(init);
})();
