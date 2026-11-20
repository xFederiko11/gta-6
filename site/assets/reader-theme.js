/* Adaptive default: dark on mobile, light on desktop. Explicit preference persists. */
(() => {
  'use strict';
  const key = 'gta6-theme-v1';
  const root = document.documentElement;
  const mobile = window.matchMedia('(max-width:760px)');
  const chooseDefault = () => mobile.matches ? 'dark' : 'light';
  const stored = () => { try { const value=localStorage.getItem(key); return value === 'dark' || value === 'light' ? value : null; } catch (_) { return null; } };
  const buttons = Array.from(document.querySelectorAll('[data-theme-choice]'));
  const meta = document.querySelector('meta[name="theme-color"]');
  function apply(value, save) {
    const theme = value === 'light' ? 'light' : 'dark';
    root.dataset.theme = theme;
    root.style.colorScheme = theme;
    if (meta) meta.content = theme === 'light' ? '#fcf8fc' : '#0c0b13';
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.themeChoice === theme)));
    if (save) { try { localStorage.setItem(key, theme); } catch (_) {} }
  }
  apply(stored() || chooseDefault(), false);
  buttons.forEach(button => button.addEventListener('click', () => apply(button.dataset.themeChoice, true)));
  window.addEventListener('storage', event => { if (event.key === key || event.key === null) apply(stored() || chooseDefault(), false); });
  mobile.addEventListener('change', () => { if (!stored()) apply(chooseDefault(),false); });
  window.addEventListener('pageshow', () => apply(stored() || chooseDefault(), false));
  const dialog = document.querySelector('[data-image-dialog]');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const photo = dialog.querySelector('img');
  const title = dialog.querySelector('[data-image-title]');
  const source = dialog.querySelector('[data-image-credit]');
  const viewport = dialog.querySelector('[data-image-viewport]');
  const zoom = dialog.querySelector('[data-image-zoom]');
  function resetZoom() { viewport.dataset.zoom = 'false'; zoom.setAttribute('aria-pressed', 'false'); zoom.textContent = 'Zoom 2x'; }
  document.querySelectorAll('a.v-image-link').forEach(link => link.addEventListener('click', event => {
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const image = link.querySelector('img');
    if (!image || image.dataset.unavailable !== undefined) return;
    event.preventDefault();
    photo.src = link.href;
    photo.alt = image.alt;
    title.textContent = image.alt;
    source.href = link.dataset.imageSource || link.href;
    source.textContent = 'Fonte originale';
    resetZoom();
    dialog.showModal();
  }));
  zoom.addEventListener('click', () => {
    const enlarged = viewport.dataset.zoom !== 'true';
    viewport.dataset.zoom = String(enlarged);
    zoom.setAttribute('aria-pressed', String(enlarged));
    zoom.textContent = enlarged ? 'Adatta allo schermo' : 'Zoom 2x';
  });
  dialog.querySelector('[data-image-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => { photo.removeAttribute('src'); resetZoom(); });
})();
