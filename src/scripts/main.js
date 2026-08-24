/**
 * main.js — shared page behavior for every AntarikshPedia page.
 * Reveal-on-scroll only; each page loads its own feature scripts.
 * The site is dark-only (light theme removed 2026-08-24).
 */

const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

/** Add .visible to .reveal elements as they enter the viewport. */
function initReveals() {
  const els = document.querySelectorAll('.reveal');
  if (reducedMotion || !('IntersectionObserver' in window)) {
    els.forEach(el => el.classList.add('visible'));
    return;
  }
  const io = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    },
    // threshold 0: tall sections (whole era grids) must reveal as soon as
    // their first pixel enters, not after 12% is visible
    { threshold: 0, rootMargin: '0px 0px -40px 0px' }
  );
  els.forEach(el => io.observe(el));
}

initReveals();
