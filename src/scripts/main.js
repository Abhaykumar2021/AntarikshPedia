/**
 * main.js — shared page behavior for every AntarikshPedia page.
 * Reveal-on-scroll only; each page loads its own feature scripts.
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

/* ---------- theme toggle (light/dark) ---------- */

const themeButton = document.getElementById('theme-toggle');
const themeIcon = themeButton?.querySelector('.theme-icon');

function paintThemeButton() {
  const light = document.documentElement.dataset.theme === 'light';
  if (themeIcon) themeIcon.textContent = light ? '☾' : '☀';
  themeButton?.setAttribute(
    'aria-label',
    light ? 'Switch to dark theme' : 'Switch to light theme'
  );
}

themeButton?.addEventListener('click', () => {
  const next =
    document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
  document.documentElement.dataset.theme = next;
  try {
    localStorage.setItem('ap-theme', next);
  } catch { /* private mode: session-only */ }
  paintThemeButton();
});

paintThemeButton();
