/* One shuffled pass through the curated pool, without immediate repeats. */
function createHeroDeck(length, random = Math.random) {
  let bag = [];
  let last = -1;
  return () => {
    if (!bag.length) {
      bag = Array.from({ length }, (_, i) => i);
      for (let i = bag.length - 1; i > 0; i--) {
        const j = Math.floor(random() * (i + 1));
        [bag[i], bag[j]] = [bag[j], bag[i]];
      }
      if (bag.length > 1 && bag[bag.length - 1] === last) [bag[0], bag[bag.length - 1]] = [bag[bag.length - 1], bag[0]];
    }
    last = bag.pop();
    return last;
  };
}

if (typeof module !== 'undefined' && module.exports) module.exports = { createHeroDeck };

if (typeof document !== 'undefined') (() => {
  const hero = document.querySelector('[data-hero-slideshow]');
  if (!hero) return;
  const payload = document.querySelector('#hero-slides');
  let slides;
  try { slides = JSON.parse(payload.textContent); } catch (_) { return; }
  if (!Array.isArray(slides) || slides.length < 2) return;
  const first = hero.querySelector('.ci-hero-image');
  const spare = first.cloneNode(false);
  spare.removeAttribute('src');
  spare.removeAttribute('srcset');
  spare.removeAttribute('fetchpriority');
  spare.loading = 'eager';
  spare.dataset.heroActive = 'false';
  spare.setAttribute('aria-hidden', 'true');
  hero.insertBefore(spare, first);
  const frames = [first, spare];
  const nextInDeck = createHeroDeck(slides.length);
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const controls = hero.querySelector('[data-hero-controls]');
  const caption = hero.querySelector('[data-hero-caption]');
  const count = hero.querySelector('[data-hero-count]');
  const toggle = hero.querySelector('[data-hero-toggle]');
  const prev = hero.querySelector('[data-hero-prev]');
  const next = hero.querySelector('[data-hero-next]');
  const history = [];
  let position = -1;
  let active = 0;
  let busy = false;
  let paused = reducedMotion.matches;
  let hovered = false;
  let focused = false;
  let rotationRequested = false;
  let inView = true;
  let timer;
  let prefetched = null;
  const interval = 8000;

  function canPlay() {
    return !paused && ((!hovered && !focused) || rotationRequested) && !document.hidden && inView;
  }
  function schedule() {
    clearTimeout(timer);
    if (canPlay()) timer = setTimeout(() => go(1), interval);
    hero.dataset.heroPlaying = String(canPlay());
  }
  function updateToggle() {
    toggle.textContent = paused ? 'Riprendi' : 'Pausa';
    toggle.setAttribute('aria-pressed', String(paused));
    toggle.setAttribute('aria-label', paused ? 'Avvia la presentazione' : 'Metti in pausa la presentazione');
  }
  function upcoming() {
    if (position + 1 >= history.length) history.push(nextInDeck());
    return history[position + 1];
  }
  function preload() {
    // Only one upcoming photograph is prefetched, never the whole collection.
    const index = upcoming();
    prefetched = new Image();
    prefetched.decoding = 'async';
    prefetched.src = slides[index].src;
  }
  async function show(index) {
    const incoming = frames[1 - active];
    const outgoing = frames[active];
    const slide = slides[index];
    busy = true;
    prev.disabled = next.disabled = true;
    try {
      incoming.alt = slide.alt;
      incoming.sizes = '(max-width: 700px) 1300px, 100vw';
      incoming.srcset = slide.srcset;
      incoming.src = slide.src;
      incoming.style.setProperty('--hero-position', slide.position);
      await incoming.decode();
      outgoing.dataset.heroActive = 'false';
      outgoing.setAttribute('aria-hidden', 'true');
      incoming.dataset.heroActive = 'true';
      incoming.removeAttribute('aria-hidden');
      active = 1 - active;
      hero.dataset.heroIndex = String(index);
      hero.dataset.heroName = slide.name;
      caption.textContent = slide.label;
      count.textContent = `${index + 1} / ${slides.length}`;
      // Keep at most two complete passes for the manual Back control.
      if (history.length > slides.length * 2 && position > slides.length) {
        history.splice(0, slides.length);
        position -= slides.length;
      }
      preload();
    } catch (_) {
      // Keep the last loaded photograph visible if a download fails.
    } finally {
      busy = false;
      prev.disabled = position <= 0;
      next.disabled = false;
      schedule();
    }
  }
  async function go(direction) {
    if (busy) return;
    clearTimeout(timer);
    if (direction < 0 && position > 0) position--;
    else { upcoming(); position++; }
    await show(history[position]);
  }
  prev.addEventListener('click', () => go(-1));
  next.addEventListener('click', () => go(1));
  toggle.addEventListener('click', () => {
    paused = !paused;
    rotationRequested = !paused;
    updateToggle(); schedule();
  });
  hero.addEventListener('mouseenter', () => { hovered = true; rotationRequested = false; schedule(); });
  hero.addEventListener('mouseleave', () => { hovered = false; schedule(); });
  hero.addEventListener('focusin', event => {
    focused = true;
    if (event.target !== toggle) rotationRequested = false;
    schedule();
  });
  hero.addEventListener('focusout', event => {
    focused = hero.contains(event.relatedTarget);
    schedule();
  });
  document.addEventListener('visibilitychange', schedule);
  reducedMotion.addEventListener('change', () => {
    if (reducedMotion.matches) paused = true;
    updateToggle(); schedule();
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      inView = entries[0].isIntersecting;
      schedule();
    }, { threshold: 0.15 }).observe(hero);
  }
  controls.hidden = false;
  updateToggle();
  go(1);
})();
