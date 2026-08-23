/**
 * global-search.js — header search available on every page.
 *
 * Fuzzy-searches the mission record (Fuse.js) and links results straight
 * to mission pages. Keyboard: ↓/↑ to move, Enter to open, Esc to close.
 * On the timeline page the sidebar search still drives the flip-book;
 * this one always navigates.
 */

import { createSearchIndex, fuzzySearch } from './search.js';

const form = document.getElementById('global-search-form');
const input = document.getElementById('global-search-input');
const list = document.getElementById('global-results');

if (form && input && list) {
  const missions = JSON.parse(
    document.getElementById('all-missions').textContent
  );
  const index = createSearchIndex(missions);
  let active = -1;

  const close = () => {
    list.classList.remove('open');
    list.innerHTML = '';
    active = -1;
  };

  const paint = () => {
    [...list.querySelectorAll('.search-result')].forEach((el, i) =>
      el.setAttribute('aria-selected', String(i === active))
    );
  };

  input.addEventListener('input', () => {
    const hits = fuzzySearch(index, input.value, 7);
    list.innerHTML = '';
    active = -1;
    if (!hits.length) {
      close();
      return;
    }
    for (const m of hits) {
      const li = document.createElement('li');
      li.setAttribute('role', 'option');
      li.innerHTML =
        `<a class="search-result" href="/missions/${m.id}/">` +
        `${m.name}<span class="sr-year">${m.year}</span></a>`;
      list.appendChild(li);
    }
    list.classList.add('open');
  });

  input.addEventListener('keydown', event => {
    if (event.key === 'ArrowDown' && list.classList.contains('open')) {
      event.preventDefault();
      active = (active + 1) % list.children.length;
      paint();
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      active = (active - 1 + list.children.length) % list.children.length;
      paint();
    } else if (event.key === 'Enter') {
      const chosen = list.children[Math.max(active, 0)]?.querySelector('a');
      if (chosen) {
        event.preventDefault();
        window.location.href = chosen.href;
      }
    } else if (event.key === 'Escape') {
      close();
    }
  });

  form.addEventListener('submit', event => {
    event.preventDefault();
    const first = list.querySelector('a');
    if (first) window.location.href = first.href;
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('.header-search')) close();
  });
}
