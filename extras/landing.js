/* Landing-page enhancement for index.md: count-up animation on the hero
   stats (.lp-stat__num[data-target]). The markup already contains the real
   final numbers, so if this script never runs (or IntersectionObserver is
   unavailable) the correct values are simply shown without animation.
   No-op on every other page. */
(function () {
  function countUp(el) {
    var target = parseFloat(el.getAttribute('data-target'));
    if (isNaN(target)) return;
    var suffix = el.getAttribute('data-suffix') || '';
    var dur = 1100, startTs = null;
    function frame(ts) {
      if (startTs === null) startTs = ts;
      var p = Math.min((ts - startTs) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(frame);
      else el.textContent = target + suffix;
    }
    requestAnimationFrame(frame);
  }

  function init() {
    if (init.done) return;               // run once per page load
    var nums = [].slice.call(document.querySelectorAll('.lp-stat__num[data-target]'));
    if (!nums.length) return;
    init.done = true;
    var reduce = window.matchMedia &&
                 window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce || typeof IntersectionObserver === 'undefined') return; // keep static numbers
    nums.forEach(function (el) { el.textContent = '0'; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { countUp(e.target); io.unobserve(e.target); }
      });
    }, { threshold: 0.4 });
    var vh = window.innerHeight || document.documentElement.clientHeight;
    nums.forEach(function (el) {
      var top = el.getBoundingClientRect().top;
      if (top < vh) { countUp(el); } else { io.observe(el); }
    });
  }

  // Run now (DOM is ready by the time this end-of-body script executes) and
  // also on Material instant navigation, so it survives SPA-style page swaps.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  if (window.document$ && typeof window.document$.subscribe === 'function') {
    window.document$.subscribe(function () { init.done = false; init(); });
  }
})();
