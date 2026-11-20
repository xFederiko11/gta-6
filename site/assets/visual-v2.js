/* Local-only preferences. No publication APIs, credentials or tracking. */
(() => {
  'use strict';
  const key = 'gta6-spoilers-v2';
  const switches = Array.from(document.querySelectorAll('[data-spoiler-choice]'));
  const spoilers = Array.from(document.querySelectorAll('details[data-spoiler]'));
  const label = document.querySelector('[data-spoiler-label]');
  let preference = 'hide';
  try { preference = localStorage.getItem(key) === 'show' ? 'show' : 'hide'; } catch (_) {}
  function apply(value, save) {
    preference = value === 'show' ? 'show' : 'hide';
    spoilers.forEach(panel => { panel.open = preference === 'show'; });
    switches.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.spoilerChoice === preference)));
    if (label) label.textContent = preference === 'show' ? 'Spoiler visibili' : 'Spoiler nascosti';
    if (save) { try { localStorage.setItem(key, preference); } catch (_) {} }
  }
  switches.forEach(button => button.addEventListener('click', () => apply(button.dataset.spoilerChoice, true)));
  apply(preference, false);
  window.addEventListener('storage', event => { if (event.key === key) apply(event.newValue, false); });
  document.querySelectorAll('[data-guide-directory]').forEach(directory => {
    const input = directory.querySelector('[data-guide-search]');
    const buttons = Array.from(directory.querySelectorAll('[data-guide-filter]'));
    const cards = Array.from(directory.querySelectorAll('[data-guide-searchable]'));
    const result = directory.querySelector('[data-guide-result]');
    let active = 'all';
    const normalize = value => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('it-IT');
    function render() {
      const words = normalize(input ? input.value.trim() : '').split(/\s+/).filter(Boolean);
      let count = 0;
      cards.forEach(card => {
        const match = (active === 'all' || card.dataset.category === active) && words.every(word => normalize(card.dataset.guideSearchable).includes(word));
        card.hidden = !match;
        count += match ? 1 : 0;
      });
      if (result) result.textContent = count ? count + (count === 1 ? ' guida disponibile' : ' guide disponibili') : 'Nessuna guida trovata. Prova un altro termine o scegli Tutte.';
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.guideFilter === active)));
    }
    if (input) input.addEventListener('input', render);
    buttons.forEach(button => button.addEventListener('click', () => { active = button.dataset.guideFilter; render(); }));
    render();
  });
  document.querySelectorAll('img[data-visual-image]').forEach(image => {
    function fallback() {
      image.dataset.unavailable = 'true';
      image.alt = 'Immagine non disponibile. Le istruzioni e il collegamento alla fonte restano consultabili.';
      const link = image.closest('a');
      if (link && link.dataset.imageSource) {
        link.href = link.dataset.imageSource;
        const badge = link.querySelector('.v-image-label');
        if (badge) badge.textContent = 'Apri la fonte';
      }
    }
    image.addEventListener('error', fallback);
    if (image.complete && image.naturalWidth === 0) fallback();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') document.querySelectorAll('.v-menu[open],.v-more[open]').forEach(menu => { menu.open = false; });
  });
})();
