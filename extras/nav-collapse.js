/**
 * Desktop sidebar collapse for Material's chapter sections.
 *
 * Background: with `navigation.sections` + `navigation.indexes`, each
 * chapter renders as
 *
 *   <li class="md-nav__item--section md-nav__item--nested">
 *     <input class="md-toggle" id="__nav_N">
 *     <div class="md-nav__link md-nav__container">
 *       <a href="…/chapterN/">chapter title</a>   ← navigates
 *       <label for="__nav_N">chevron</label>      ← toggles
 *     </div>
 *     <nav class="md-nav">…配套实验…</nav>
 *   </li>
 *
 * Material only honours the checkbox on mobile; on desktop the section
 * subtree is always visible and the chevron is hidden. We inject CSS so
 * that on desktop, too, the subtree follows the checkbox and the chevron
 * is visible/clickable. Material checks the active chapter's checkbox at
 * render time, so the default state (active chapter open, rest closed)
 * comes for free.
 *
 * One case needs JS: on pages Material doesn't consider "active" — the
 * translated editions (sidebar links are rewritten client-side by
 * lang-switcher.js) and the per-experiment pages, which aren't in the
 * nav — no checkbox is checked. There we match the current URL against
 * each section's chapter number and open the matching section.
 *
 * Re-runs on every Material page swap (navigation.instant) via document$.
 */
(function () {
  "use strict";

  function ensureStyle() {
    if (document.getElementById("nav-collapse-style")) return;
    var s = document.createElement("style");
    s.id = "nav-collapse-style";
    s.textContent = [
      "@media screen and (min-width: 76.25em) {",
      // Collapse the subtree when the checkbox is unchecked (Material
      // keeps section subtrees always-visible on desktop by default).
      "  .md-sidebar--primary .md-nav__item--nested > .md-toggle:not(:checked) ~ .md-nav {",
      "    display: none !important;",
      "  }",
      // Material hides the section chevron on desktop; bring it back and
      // make it clickable.
      "  .md-sidebar--primary .md-nav__item--nested > .md-nav__container > label.md-nav__link {",
      "    display: flex;",
      "    align-items: center;",
      "    cursor: pointer;",
      "    pointer-events: auto !important;",
      "    margin: 0;",
      // 4px top padding centres the 1.2rem icon on the title's FIRST line
      // (6px link padding + ~1.3 line-height): the container aligns
      // flex-start (book-theme.css) so wrapped two-line titles don't pull
      // the chevron down between the lines.
      "    padding: 4px 0.2rem 0 0.4rem;",
      "  }",
      // Material's own stylesheet already rotates the chevron's ::after
      // by 90° when the checkbox is checked — no extra transform here.
      "  .md-sidebar--primary .md-nav__item--nested > .md-nav__container > label.md-nav__link .md-nav__icon {",
      "    display: block;",
      "  }",
      "}",
    ].join("\n");
    document.head.appendChild(s);
  }

  function applyDefaultState() {
    var sidebar = document.querySelector(".md-sidebar--primary");
    if (!sidebar) return;

    // Material already checked a section's checkbox? Then its render-time
    // active detection worked — nothing to fix up.
    if (sidebar.querySelector(".md-nav__item--nested > .md-toggle:checked")) return;

    // Otherwise (translated edition or a page outside the nav), derive the
    // chapter from the URL and open the matching section.
    var m = location.pathname.match(/chapter(\d+)/);
    if (!m) return;
    var wanted = m[1];
    var sections = sidebar.querySelectorAll(".md-nav__item--nested");
    for (var i = 0; i < sections.length; i++) {
      var link = sections[i].querySelector(":scope > .md-nav__container > a.md-nav__link");
      var checkbox = sections[i].querySelector(":scope > .md-toggle");
      if (!link || !checkbox) continue;
      var lm = (link.getAttribute("href") || "").match(/chapter(\d+)/);
      if (lm && lm[1] === wanted) {
        checkbox.checked = true;
        break;
      }
    }
  }

  function init() {
    ensureStyle();
    applyDefaultState();
  }

  document.addEventListener("DOMContentLoaded", init);
  if (window.document$) window.document$.subscribe(init);
})();
