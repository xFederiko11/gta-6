/* GTA VI Italia: official YouTube embed loaded ONLY after an explicit click.
   A plain sourced timestamp link remains usable without JavaScript. */
(() => {
  'use strict';
  let opened = null;
  const widgets = document.querySelectorAll('.v-step-video[data-step-video-id]');
  for (const root of widgets) {
    const id = root.dataset.stepVideoId || '';
    const stamp = root.dataset.stepVideoSeconds || '';
    const button = root.querySelector('[data-step-video-open]');
    const slot = root.querySelector('[data-step-video-slot]');
    if (!/^[A-Za-z0-9_-]{11}$/.test(id) || !/^(0|[1-9][0-9]{0,4})$/.test(stamp)
        || Number(stamp) > 21600 || !button || !slot) continue;
    const caption = button.querySelector('strong');
    const originalCaption = caption ? caption.textContent : '';
    function close() {
      slot.replaceChildren();
      button.setAttribute('aria-expanded', 'false');
      root.removeAttribute('data-step-video-active');
      if (caption) caption.textContent = originalCaption;
      if (opened === close) opened = null;
    }
    button.hidden = false;
    button.setAttribute('aria-expanded', 'false');
    button.addEventListener('click', () => {
      if (opened === close) {
        close();
        return;
      }
      if (opened) opened();
      const frame = document.createElement('iframe');
      frame.setAttribute('title', 'Video esterno di GTA VI: momento della guida');
      frame.setAttribute('loading', 'eager');
      frame.setAttribute('allowfullscreen', '');
      frame.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
      frame.setAttribute('allow', 'accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share');
      frame.src = 'https://www.youtube-nocookie.com/embed/' + id
        + '?start=' + encodeURIComponent(stamp) + '&rel=0';
      slot.replaceChildren(frame);
      button.setAttribute('aria-expanded', 'true');
      root.setAttribute('data-step-video-active', 'true');
      if (caption) caption.textContent = 'Chiudi il video';
      opened = close;
    });
  }
})();