/**
 * home.js — homepage-only behavior: "On this day" highlighting.
 * The match itself is computed at build time (see index.njk data);
 * this script just gives the section a gentle entrance when the
 * visitor jumps to it via the hero link.
 */

const link = document.getElementById('otd-link');
const section = document.getElementById('on-this-day');

if (link && section) {
  link.addEventListener('click', () => {
    section.classList.add('visible');
  });
}
