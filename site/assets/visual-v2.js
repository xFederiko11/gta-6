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
  // A manually maintained, local-only collector checklist; NEVER PSN progression.
  document.querySelectorAll('[data-meditation-tracker]').forEach(tracker => {
    const KEY = 'gta6-meditations-v1';
    const boxes = Array.from(tracker.querySelectorAll('input[data-meditation-check]'));
    const keys = new Set(boxes.map(box => box.dataset.meditationCheck));
    if (boxes.length !== 18 || keys.size !== 18) return;
    const summary = tracker.querySelector('[data-meditation-summary]');
    const goal = tracker.querySelector('[data-meditation-100]');
    const house = tracker.querySelector('[data-meditation-house]');
    const progress = tracker.querySelector('[data-meditation-progress]');
    const unlock = tracker.querySelector('[data-meditation-unlock]');
    const save = tracker.querySelector('[data-meditation-save-status]');
    const reset = tracker.querySelector('[data-meditation-reset]');
    if (!summary || !goal || !house || !progress || !unlock || !save || !reset) return;
    let localAvailable = true;
    try {
      const old = JSON.parse(localStorage.getItem(KEY) || '[]');
      if (Array.isArray(old)) {
        const selected = new Set(old.filter(key => typeof key === 'string' && keys.has(key)));
        boxes.forEach(box => { box.checked = selected.has(box.dataset.meditationCheck); });
      }
    } catch (_) {
      localAvailable = false;
    }
    function update(persist) {
      const completed = boxes.filter(box => box.checked).map(box => box.dataset.meditationCheck);
      const done = completed.length;
      const beforeFinal = boxes.filter(box => box.dataset.meditationCheck !== 'ascent-mountain:final' && box.checked).length;
      summary.textContent = done + ' / 18';
      goal.textContent = Math.min(done, 15) + ' / 15';
      house.textContent = completed.includes('jasons-house:one') ? 'Completata' : 'Da fare';
      progress.value = done;
      unlock.textContent = beforeFinal === 17
        ? 'Le 17 sessioni precedenti risultano segnate nella checklist: verifica che il simbolo finale di Ascent Mountain sia disponibile nel gioco.'
        : 'Per sbloccare Ascent Mountain, completa tutte le altre 17 meditazioni nel gioco. Il conteggio del sito è soltanto un promemoria.';
      if (persist) {
        try {
          localStorage.setItem(KEY, JSON.stringify(completed));
          localAvailable = true;
        } catch (_) {
          localAvailable = false;
        }
      }
      save.textContent = localAvailable
        ? 'Progressi conservati solo in questo browser. Non sincronizzati con PS5, X o il nostro server.'
        : 'Salvataggio locale non disponibile: queste spunte potrebbero perdersi chiudendo la pagina.';
    }
    boxes.forEach(box => box.addEventListener('change', () => update(true)));
    reset.addEventListener('click', () => {
      if (!window.confirm('Azzera tutte le 18 spunte salvate in questo browser?')) return;
      boxes.forEach(box => { box.checked = false; });
      try {
        localStorage.removeItem(KEY);
        localAvailable = true;
      } catch (_) {
        localAvailable = false;
      }
      update(false);
    });
    update(false);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') document.querySelectorAll('.v-menu[open],.v-more[open]').forEach(menu => { menu.open = false; });
  });
})();
