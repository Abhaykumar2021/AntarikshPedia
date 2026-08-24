/**
 * vision.js — starfield canvas + count-up stats for the vision page.
 * Both effects honor prefers-reduced-motion.
 */

const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- starfield ---------- */

function initStars() {
  const canvas = document.getElementById('vision-stars');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  let stars = [];
  let raf = null;
  let running = false;

  function resize() {
    canvas.width = canvas.offsetWidth * dpr;
    canvas.height = canvas.offsetHeight * dpr;
    const count = Math.round(
      (canvas.width * canvas.height) / (9000 * dpr * dpr)
    );
    stars = Array.from({ length: count }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: (Math.random() * 1.1 + 0.3) * dpr,
      base: Math.random() * 0.45 + 0.2,
      amp: Math.random() * 0.35 + 0.1,
      speed: Math.random() * 0.0012 + 0.0004,
      phase: Math.random() * Math.PI * 2,
      drift: (Math.random() * 0.02 + 0.004) * dpr,
    }));
  }

  function draw(t) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const s of stars) {
      const alpha = reducedMotion
        ? s.base
        : s.base + Math.sin(t * s.speed + s.phase) * s.amp;
      ctx.globalAlpha = Math.max(0.05, alpha);
      ctx.fillStyle = '#e8ecf4';
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
      if (!reducedMotion) {
        s.x += s.drift;
        if (s.x > canvas.width + 2) s.x = -2;
      }
    }
    ctx.globalAlpha = 1;
  }

  function loop(t) {
    draw(t);
    raf = requestAnimationFrame(loop);
  }

  function start() {
    if (running || reducedMotion) return;
    running = true;
    raf = requestAnimationFrame(loop);
  }

  function stop() {
    running = false;
    if (raf) cancelAnimationFrame(raf);
    raf = null;
  }

  resize();
  draw(0);
  window.addEventListener('resize', () => {
    resize();
    draw(0);
  });

  const io = new IntersectionObserver(
    entries => (entries[0].isIntersecting ? start() : stop()),
    { threshold: 0 }
  );
  io.observe(canvas);
}

/* ---------- count-up stats ---------- */

function initCountUps() {
  const nums = document.querySelectorAll('.stat-num[data-count]');
  if (!nums.length) return;

  const easeOut = x => 1 - Math.pow(1 - x, 3);

  function animate(el) {
    const target = parseInt(el.dataset.count, 10);
    if (reducedMotion || !target) {
      el.textContent = target;
      return;
    }
    const dur = 1300;
    const t0 = performance.now();
    function tick(now) {
      const p = Math.min((now - t0) / dur, 1);
      el.textContent = Math.round(easeOut(p) * target);
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  const io = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animate(entry.target);
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.4 }
  );
  nums.forEach(el => io.observe(el));
}

initStars();
initCountUps();
