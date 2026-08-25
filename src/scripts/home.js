/**
 * home.js — homepage-only behavior.
 * 1. "On this day" entrance when jumped to via the hero link.
 * 2. Evolution timeline: the lineage spine grows as the section
 *    scrolls through the viewport (reduced-motion → always full).
 */

const link = document.getElementById('otd-link');
const section = document.getElementById('on-this-day');

if (link && section) {
  link.addEventListener('click', () => {
    section.classList.add('visible');
  });
}

const evolution = document.getElementById('evolution');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

if (evolution && !reducedMotion) {
  let ticking = false;

  function updateGrowth() {
    ticking = false;
    const rect = evolution.getBoundingClientRect();
    const vh = window.innerHeight;
    // 0 when the top of the timeline reaches 80% of the viewport,
    // 1 when its bottom reaches 35% — reads as the line being "drawn"
    const start = vh * 0.8;
    const end = vh * 0.35;
    const progress = (start - rect.top) / (rect.height + start - end);
    const clamped = Math.min(1, Math.max(0, progress));
    evolution.style.setProperty('--growth', clamped.toFixed(4));
  }

  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(updateGrowth);
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  updateGrowth();
}
