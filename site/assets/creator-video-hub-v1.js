/* Curated creator videos: click-to-load official player, no third-party assets
   or misleading publisher thumbnails before consent. */
(() => {
  'use strict';
  const cards = Array.from(document.querySelectorAll('[data-cv-video-id][data-cv-start]'));
  if (!cards.length) return;
  let active = null;
  for (const card of cards) {
    const id = card.dataset.cvVideoId;
    const start = card.dataset.cvStart;
    const trigger = card.querySelector('[data-cv-load]');
    const slot = card.querySelector('[data-cv-slot]');
    const poster = card.querySelector('.cv-poster');
    const playArt = card.querySelector('.cv-big-play');
    if (!/^[A-Za-z0-9_-]{11}$/.test(id) || !/^(0|[1-9][0-9]{0,4})$/.test(start) ||
        Number(start) > 21600 || !trigger || !slot || !poster) continue;
    const firstLabel = trigger.textContent;
    let currentSeconds = Number(start);
    function close() {
      slot.replaceChildren();
      if (playArt) playArt.hidden = false;
      trigger.hidden = false;
      trigger.textContent = firstLabel;
      trigger.setAttribute('aria-expanded', 'false');
      card.removeAttribute('data-cv-playing');
      if (active === close) active = null;
    }
    function open(seconds) {
      if (active && active !== close) active();
      currentSeconds = seconds;
      const frame = document.createElement('iframe');
      frame.src = 'https://www.youtube-nocookie.com/embed/' + id +
                  '?start=' + encodeURIComponent(String(seconds)) + '&rel=0&autoplay=1';
      frame.title = 'Player YouTube ufficiale: ' + card.querySelector('h2').textContent;
      frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      frame.allowFullscreen = true;
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.loading = 'eager';
      slot.replaceChildren(frame);
      if (playArt) playArt.hidden = true;
      trigger.hidden = false;
      trigger.textContent = '■ Chiudi il video';
      trigger.setAttribute('aria-expanded','true');
      card.setAttribute('data-cv-playing','true');
      active = close;
    }
    trigger.hidden = false;
    trigger.setAttribute('aria-expanded','false');
    trigger.addEventListener('click', () => {
      if (active === close) close();
      else open(currentSeconds);
    });
    for (const chapter of card.querySelectorAll('[data-cv-seek]')) {
      const value = chapter.dataset.cvSeek;
      if (!/^(0|[1-9][0-9]{0,4})$/.test(value) || Number(value)>21600) {
        chapter.disabled = true;
        continue;
      }
      chapter.addEventListener('click', () => open(Number(value)));
    }
    // Native page navigation unloads the player; no cookies or site state
    // are written by this widget, and no provider script is added globally.
  }
  const bar = document.querySelector('[data-cv-filters]');
  if (!bar) return;
  const buttons = Array.from(bar.querySelectorAll('[data-cv-filter]'));
  const empty = document.querySelector('[data-cv-empty]');
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const filter = button.dataset.cvFilter;
      if (!['all','auto','garage','collezionabili','soldi','extra'].includes(filter)) return;
      let found = 0;
      for (const card of cards) {
        const show = filter === 'all' || card.dataset.cvCategory === filter;
        card.hidden = !show;
        if (!show && active && card.hasAttribute('data-cv-playing')) active();
        if (show) found += 1;
      }
      buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      if (empty) empty.hidden = found !== 0;
    });
  });
})();
