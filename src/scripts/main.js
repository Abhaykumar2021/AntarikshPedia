/**
 * main.js — shared page behavior for every AntarikshPedia page.
 * Sidebar toggle + reveal-on-scroll; each page loads its own feature scripts.
 * The site is dark-only (light theme removed 2026-08-24).
 */

const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---- sidebar toggle ---- */
const menuBtn = document.getElementById('menu-btn');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebar-overlay');
const closeBtn = document.getElementById('sidebar-close');
const sidebarInput = document.getElementById('global-search-input');

function openSidebar() {
  sidebar.classList.add('is-open');
  sidebar.setAttribute('aria-hidden', 'false');
  overlay.classList.add('is-open');
  overlay.setAttribute('aria-hidden', 'false');
  menuBtn.setAttribute('aria-expanded', 'true');
  menuBtn.setAttribute('aria-label', 'Close menu');
  document.body.classList.add('sidebar-open');
  if (sidebarInput) sidebarInput.focus();
}

function closeSidebar() {
  sidebar.classList.remove('is-open');
  sidebar.setAttribute('aria-hidden', 'true');
  overlay.classList.remove('is-open');
  overlay.setAttribute('aria-hidden', 'true');
  menuBtn.setAttribute('aria-expanded', 'false');
  menuBtn.setAttribute('aria-label', 'Open menu');
  document.body.classList.remove('sidebar-open');
  menuBtn.focus();
}

if (menuBtn && sidebar && overlay) {
  menuBtn.addEventListener('click', () => {
    const open = menuBtn.getAttribute('aria-expanded') === 'true';
    open ? closeSidebar() : openSidebar();
  });

  if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
  overlay.addEventListener('click', closeSidebar);

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && sidebar.classList.contains('is-open')) {
      closeSidebar();
    }
  });

  /* Cmd+K or Ctrl+K to open sidebar and focus search */
  document.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      if (!sidebar.classList.contains('is-open')) openSidebar();
      if (sidebarInput) sidebarInput.focus();
    }
  });
}

/* ---- scroll-reveal ---- */
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
