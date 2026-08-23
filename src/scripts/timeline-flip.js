/**
 * timeline-flip.js — the flip-book timeline.
 *
 * Spec (build prompt §7), implemented here:
 * - one mission per "page", sequential chronological position
 * - search (fuzzy, via scripts/search.js + Fuse.js) triggers an animated
 *   jump from the current page to the target page
 * - HARD CAP: total animation ≤ 1.8 s regardless of jump distance.
 *   Phases: 2-3 real flips → blurred riffle → 2-3 real flips, blended on
 *   one easing curve instead of hard cuts.
 * - sound: synthesized WebAudio page turns (no asset to load — satisfies
 *   the "load audio only when opened" rule by construction). Pitch varies
 *   per flip; the riffle phase uses one continuous batched noise swell,
 *   then discrete flips again at landing. Mute toggle persists in
 *   localStorage. Sound only initializes after a user gesture.
 * - accessibility: prefers-reduced-motion jumps instantly; visible
 *   "Skip animation" control during any animation; everything operable
 *   by keyboard (←/→/Home/End, / focuses search, ↑↓+Enter on results).
 * - narrow viewports (<900 px) degrade to instant jumps by design.
 */

import { createSearchIndex, fuzzySearch } from './search.js';

const DATA_EL = document.getElementById('missions-data');
const book = document.getElementById('book');
const currentSheet = document.getElementById('current-sheet');
const flipper = document.getElementById('page-flipper');
const frontFace = document.getElementById('flip-front');
const backFace = document.getElementById('flip-back');
const counterEl = document.getElementById('flip-counter');
const progressBar = document.getElementById('flip-progress-bar');
const ctxEra = document.getElementById('ctx-era');
const ctxCount = document.getElementById('ctx-count');
const ctxLink = document.getElementById('ctx-link');
const openLink = document.getElementById('open-mission-link');
const btnPrev = document.getElementById('btn-prev');
const btnNext = document.getElementById('btn-next');
const btnFirst = document.getElementById('btn-first');
const btnLast = document.getElementById('btn-last');
const muteBtn = document.getElementById('mute-toggle');
const skipBtn = document.getElementById('skip-anim');
const searchInput = document.getElementById('flip-search-input');
const resultsEl = document.getElementById('search-results');

if (!DATA_EL || !book) {
  throw new Error('[timeline-flip] required DOM nodes missing');
}

const missions = JSON.parse(DATA_EL.textContent);
const N = missions.length;
const index = createSearchIndex(missions);

const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const narrow = matchMedia('(max-width: 900px)');
const MAX_DURATION = 1750; // ms — inside the spec's 1.2–1.8 s cap

let currentIndex = 0;
let animating = false;
let skipRequested = false;

/* ================= rendering ================= */

/** Escape text for safe innerHTML use. */
function esc(value) {
  const div = document.createElement('div');
  div.textContent = value ?? '';
  return div.innerHTML;
}

/** Status → CSS modifier class. */
function statusClass(status) {
  return 'status-' + String(status).toLowerCase().replace(/\s+/g, '-');
}

/**
 * Render a mission into a .mission-sheet element's HTML.
 * @param {Object} m - Mission record.
 */
function sheetHTML(m) {
  const photo = m.media && m.media.thumb
    ? `<img src="/${esc(m.media.thumb)}" alt="" loading="lazy">`
    : `<div class="card-placeholder" style="height:100%">
         <span>${esc(m.name.charAt(0))}</span>
       </div>`;
  return `
    <div class="sheet-photo">
      ${photo}
      <span class="sheet-year">${esc(m.year)}</span>
    </div>
    <h3 class="sheet-name">${esc(m.name)}</h3>
    <p class="sheet-facts">
      <span>${esc(m.lead_partner)}</span>
      <span>target <b>${esc(m.target)}</b></span>
      <span class="status-badge ${statusClass(m.status)}">${esc(m.status)}</span>
    </p>
    <p class="sheet-outcome">${esc(m.outcome)}</p>`;
}

/**
 * Paint the current mission onto both static faces of the book.
 * @param {number} i - Mission index.
 */
function renderCurrent(i) {
  const m = missions[i];
  if (!m) return;

  currentSheet.innerHTML = sheetHTML(m);
  frontFace.firstElementChild.innerHTML = sheetHTML(missions[(i + 1) % N]);
  backFace.firstElementChild.innerHTML = sheetHTML(m);

  counterEl.textContent = `${i + 1} / ${N}`;
  progressBar.style.width = `${((i + 1) / N) * 100}%`;

  // left context page
  const eraMissions = missions.filter(x => x.era === m.era);
  ctxEra.textContent = m.era.split(':')[0];
  ctxCount.textContent =
    eraMissions.indexOf(m) + 1 + '/' + eraMissions.length;
  ctxLink.href = `/missions/${m.id}/`;
  ctxLink.textContent = m.name;

  openLink.href = `/missions/${m.id}/`;
  btnPrev.disabled = i === 0;
  btnNext.disabled = i === N - 1;
  document.title = `${m.name} (${m.year}) — AntarikshPedia Timeline`;
}

/* ================= sound ================= */

const sound = (() => {
  let ctx = null;
  let muted = localStorage.getItem('ap-muted') === '1';

  function ensureCtx() {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume();
  }

  /** One short paper-flip: filtered noise burst, pitch-varied. */
  function flip(pitch = 1) {
    if (muted) return;
    ensureCtx();
    const dur = 0.09;
    const buffer = ctx.createBuffer(1, ctx.sampleRate * dur, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < data.length; i++) {
      data[i] = (Math.random() * 2 - 1) * (1 - i / data.length);
    }
    const src = ctx.createBufferSource();
    src.buffer = data;
    src.playbackRate.value = pitch;
    const filter = ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = 900 + Math.random() * 700 * pitch;
    filter.Q.value = 0.8;
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.16, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
    src.connect(filter).connect(gain).connect(ctx.destination);
    src.start();
  }

  /**
   * Continuous riffle: one longer noise swell with fast amplitude
   * flutter — reads as many pages without firing N samples.
   */
  function riffle(durationMs) {
    if (muted) return;
    ensureCtx();
    const dur = durationMs / 1000;
    const buffer = ctx.createBuffer(1, ctx.sampleRate * dur, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    const flutterRate = 34; // pseudo-page rate per second
    for (let i = 0; i < data.length; i++) {
      const t = i / ctx.sampleRate;
      const flutter = 0.5 + 0.5 * Math.sin(2 * Math.PI * flutterRate * t);
      data[i] = (Math.random() * 2 - 1) * flutter * 0.5;
    }
    const src = ctx.createBufferSource();
    src.buffer = data;
    src.playbackRate.value = 1.4;
    const filter = ctx.createBiquadFilter();
    filter.type = 'highpass';
    filter.frequency.value = 800;
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.0001, ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.12, ctx.currentTime + dur * 0.15);
    gain.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + dur);
    src.connect(filter).connect(gain).connect(ctx.destination);
    src.start();
  }

  function setMuted(next) {
    muted = next;
    localStorage.setItem('ap-muted', muted ? '1' : '0');
  }
  function isMuted() {
    return muted;
  }

  return { flip, riffle, setMuted, isMuted };
})();

function paintMuteButton() {
  muteBtn.textContent = sound.isMuted() ? 'Sound off' : 'Sound on';
  muteBtn.setAttribute('aria-pressed', String(!sound.isMuted()));
}
paintMuteButton();

muteBtn.addEventListener('click', () => {
  sound.setMuted(!sound.isMuted());
  paintMuteButton();
});

/* ================= the jump animation ================= */

/**
 * easeInOutQuint — slow-fast-slow; blends real flips and the riffle
 * into one continuous motion per the spec's easing requirement.
 */
function easeInOutQuint(t) {
  return t < 0.5 ? 16 * t ** 5 : 1 - Math.pow(-2 * t + 2, 5) / 2;
}

let skipHandler = null;

/**
 * Animate a jump from currentIndex to targetIndex.
 *
 * @param {number} targetIndex - Destination page (0-based).
 */
async function jumpTo(targetIndex) {
  targetIndex = Math.max(0, Math.min(N - 1, targetIndex));
  const distance = Math.abs(targetIndex - currentIndex);

  // instant cases: reduced motion, tiny distance, narrow viewport
  if (reducedMotion || narrow.matches || distance === 0) {
    currentIndex = targetIndex;
    renderCurrent(currentIndex);
    return;
  }
  if (animating) return;

  animating = true;
  skipRequested = false;
  skipBtn.classList.add('active');

  const direction = targetIndex > currentIndex ? 1 : -1;
  const start = performance.now();

  // phase sizing: lead flips + riffle + land flips share the time budget
  const leadFlips = Math.min(3, distance);
  const landFlips = Math.min(3, distance);
  const riffleSpan = distance - leadFlips - landFlips; // virtual pages

  const tRiffleStart = 0.18;          // normalized phase boundaries
  const tRiffleEnd = 0.82;

  // continuous riffle sound starts here; discrete flips fire at edges
  setTimeout(() => {
    if (!skipRequested && riffleSpan > 0) {
      sound.riffle(MAX_DURATION * (tRiffleEnd - tRiffleStart));
    } else if (distance > 0) {
      sound.flip(1);
    }
  }, 60);

  await new Promise(resolve => {
    function frame(now) {
      if (skipRequested) return resolve();
      const elapsed = now - start;
      const t = Math.min(elapsed / MAX_DURATION, 1);
      const eased = easeInOutQuint(t);

      // which virtual page are we "on"?
      const virtualPos = eased * distance;

      // rotateY: full 180° sweep during lead/land phases, rapid shallow
      // oscillation + blur during the riffle window
      let angle;
      let riffle = false;
      const tn = t; // normalized time
      if (tn > tRiffleStart && tn < tRiffleEnd && riffleSpan > 0) {
        riffle = true;
        // fast shallow oscillations convey fanning
        angle = -35 * Math.sin(virtualPos * 2.6) - 12;
        flipper.classList.add('riffle');
      } else {
        flipper.classList.remove('riffle');
        // progress within the current real flip cycle
        const cycle = leadFlips + landFlips;
        const phase = (virtualPos / distance) * cycle;
        angle = -180 * (phase % 1);
        if (direction === -1) angle *= -1;
      }

      flipper.style.transform = `rotateY(${angle}deg)`;
      flipper.style.opacity = riffle ? '0.9' : '1';

      // swap the visible page content at each real-flip boundary so the
      // sheet under the flipping page keeps changing
      const shownIndex = Math.round(
        currentIndex + direction * virtualPos
      );
      const clampedShown = Math.max(0, Math.min(N - 1, shownIndex));
      if (clampedShown !== lastShown && !riffle) {
        lastShown = clampedShown;
        frontFace.firstElementChild.innerHTML =
          sheetHTML(missions[Math.min(N - 1, clampedShown + direction)] ||
            missions[clampedShown]);
        backFace.firstElementChild.innerHTML =
          sheetHTML(missions[clampedShown]);
        sound.flip(0.9 + Math.random() * 0.3);
      }

      if (t < 1) {
        requestAnimationFrame(frame);
      } else {
        resolve();
      }
    }

    let lastShown = currentIndex;
    requestAnimationFrame(frame);
  });

  flipper.classList.remove('riffle');
  flipper.style.transform = 'rotateY(0deg)';
  currentIndex = targetIndex;
  renderCurrent(currentIndex);

  skipBtn.classList.remove('active');
  animating = false;
}

skipBtn.addEventListener('click', () => {
  skipRequested = true;
});

/* ================= controls & keyboard ================= */

btnPrev.addEventListener('click', () => jumpTo(currentIndex - 1));
btnNext.addEventListener('click', () => jumpTo(currentIndex + 1));
btnFirst.addEventListener('click', () => jumpTo(0));
btnLast.addEventListener('click', () => jumpTo(N - 1));

// era quick-jumps
document.querySelectorAll('[data-era-index]').forEach(btn => {
  btn.addEventListener('click', () => {
    jumpTo(parseInt(btn.dataset.eraIndex, 10));
  });
});

// keyboard: global shortcuts
document.addEventListener('keydown', event => {
  const typing = event.target.closest('input, textarea, select');
  switch (event.key) {
    case 'ArrowLeft':
      if (!typing) { event.preventDefault(); jumpTo(currentIndex - 1); }
      break;
    case 'ArrowRight':
      if (!typing) { event.preventDefault(); jumpTo(currentIndex + 1); }
      break;
    case 'Home':
      if (!typing) { event.preventDefault(); jumpTo(0); }
      break;
    case 'End':
      if (!typing) { event.preventDefault(); jumpTo(N - 1); }
      break;
    case '/':
      if (!typing) {
        event.preventDefault();
        searchInput.focus();
      }
      break;
    case 'm':
    case 'M':
      if (!typing) {
        sound.setMuted(!sound.isMuted());
        paintMuteButton();
      }
      break;
    default:
      break;
  }
});

/* ================= fuzzy search UI ================= */

const state = { activeResult: -1, results: [] };

function closeResults() {
  resultsEl.classList.remove('open');
  resultsEl.innerHTML = '';
  state.results = [];
  state.activeResult = -1;
  searchInput.setAttribute('aria-expanded', 'false');
}

function paintResults() {
  [...resultsEl.querySelectorAll('.search-result')].forEach((el, i) => {
    el.setAttribute('aria-selected', String(i === state.activeResult));
  });
}

searchInput.addEventListener('input', () => {
  const hits = fuzzySearch(index, searchInput.value);
  state.results = hits;
  resultsEl.innerHTML = '';
  state.activeResult = -1;

  if (hits.length === 0) {
    closeResults();
    return;
  }

  hits.forEach(m => {
    const li = document.createElement('li');
    li.setAttribute('role', 'option');
    li.innerHTML = `
      <button type="button" class="search-result"
              data-id="${esc(m.id)}" data-index="${missions.indexOf(m)}">
        ${esc(m.name)}
        <span class="sr-year">${esc(m.year)}</span>
      </button>`;
    resultsEl.appendChild(li);
  });

  resultsEl.classList.add('open');
  searchInput.setAttribute('aria-expanded', 'true');
});

// user gesture: submitting a search triggers the animated jump (+sound)
resultsEl.addEventListener('click', event => {
  const button = event.target.closest('.search-result');
  if (!button) return;
  closeResults();
  searchInput.blur();
  jumpTo(parseInt(button.dataset.index, 10)).then(() =>
    console.log(`landed on mission ${currentIndex + 1}`)
  );
});

searchInput.addEventListener('keydown', event => {
  if (event.key === 'ArrowDown' && state.results.length) {
    event.preventDefault();
    state.activeResult =
      (state.activeResult + 1) % state.results.length;
    paintResults();
  } else if (event.key === 'ArrowUp' && state.results.length) {
    event.preventDefault();
    state.activeResult =
      (state.activeResult - 1 + state.results.length) % state.results.length;
    paintResults();
  } else if (event.key === 'Enter') {
    event.preventDefault();
    const chosen = state.results[state.activeResult] || state.results[0];
    if (chosen) {
      closeResults();
      searchInput.blur();
      jumpTo(missions.indexOf(chosen));
    }
  } else if (event.key === 'Escape') {
    closeResults();
  }
});

document.addEventListener('click', event => {
  if (!event.target.closest('.flip-search')) closeResults();
});

/* ================= boot ================= */

renderCurrent(currentIndex);
