/* Local-only preferences. No publication APIs, credentials or tracking. */
(() => {
  'use strict';
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
      if (image.dataset.unavailable === 'true') return;
      image.dataset.unavailable = 'true';
      const label = image.alt || 'Schermata della guida';
      const link = image.closest('a');
      if (link && link.dataset.imageSource) {
        link.href = link.dataset.imageSource;
        link.setAttribute('aria-label', 'Apri la fonte originale: ' + label);
        const badge = link.querySelector('.v-image-label');
        if (badge) badge.textContent = 'Apri la fonte';
      }
      const replacement = document.createElement('div');
      replacement.className = 'v-missing-media';
      replacement.setAttribute('role', 'img');
      replacement.setAttribute('aria-label', 'Immagine non disponibile: ' + label);
      replacement.dataset.mediaMissing = image.dataset.visualImage || 'unknown';
      const symbol = document.createElement('span');
      symbol.className = 'v-missing-icon';
      symbol.setAttribute('aria-hidden', 'true');
      symbol.textContent = '▧';
      const heading = document.createElement('strong');
      heading.textContent = 'Immagine non disponibile';
      const help = document.createElement('small');
      help.textContent = 'Consulta la fonte originale indicata nella guida.';
      replacement.append(symbol, heading, help);
      image.replaceWith(replacement);
    }
    image.addEventListener('error', fallback);
    if (image.complete && image.naturalWidth === 0) fallback();
  });
  // No third-party requests until a reader chooses to play the original video.
  document.querySelectorAll('[data-load-youtube]').forEach(button => {
    button.addEventListener('click', () => {
      const shell = button.closest('[data-youtube-id][data-youtube-start]');
      if (!shell) return;
      const id = shell.dataset.youtubeId;
      const seconds = Number(shell.dataset.youtubeStart);
      if (!/^[a-zA-Z0-9_-]{11}$/.test(id) ||
          !Number.isInteger(seconds) || seconds < 0 || seconds > 100000) return;
      const holder = shell.querySelector('[data-youtube-holder]');
      if (!holder || holder.querySelector('iframe')) return;
      const frame = document.createElement('iframe');
      frame.title = 'Video gameplay YouTube originale';
      frame.src = 'https://www.youtube-nocookie.com/embed/' + id +
                  '?start=' + seconds + '&rel=0&autoplay=1';
      frame.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share';
      frame.allowFullscreen = true;
      frame.loading = 'lazy';
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.setAttribute('data-original-video-player', '');
      holder.replaceChildren(frame);
    }, {once: true});
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') document.querySelectorAll('.v-menu[open],.v-more[open]').forEach(menu => { menu.open = false; });
  });
})();
