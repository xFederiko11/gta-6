/* GTA VI Italia: manual, local-only trophy progress and filters. */
(() => {
  "use strict";
  const root = document.querySelector("[data-trophy-atlas]");
  if (!root) return;
  const KEY = "gta6-italia:trophies:v1";
  const cards = [...root.querySelectorAll("[data-atlas-card]")];
  const inputs = [...root.querySelectorAll("input[data-atlas-trophy]")];
  const allowed = new Set(inputs.map(input => input.dataset.atlasTrophy));
  const count = root.querySelector("[data-atlas-counter]");
  const bar = root.querySelector("[data-atlas-progress]");
  const status = root.querySelector("[data-atlas-results]");
  const empty = root.querySelector("[data-atlas-empty]");
  const notice = root.querySelector("[data-atlas-storage]");
  const search = root.querySelector("[data-atlas-search]");
  const filters = [...root.querySelectorAll("[data-atlas-filter]")];
  let active = "all";
  function read() {
    try {
      const values = JSON.parse(window.localStorage.getItem(KEY) || "[]");
      return new Set(Array.isArray(values)
        ? values.filter(v => typeof v === "string" && allowed.has(v)) : []);
    } catch (_) { return new Set(); }
  }
  let earned = read();
  function normalize(s) {
    return (s || "").toLocaleLowerCase("it-IT").normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }
  function render() {
    let visible = 0;
    const query = normalize(search.value.trim());
    for (const card of cards) {
      const show = (active === "all" || card.dataset.group === active) &&
        (!query || normalize(card.dataset.search).includes(query));
      card.hidden = !show;
      if (show) visible++;
      const input = card.querySelector("input[data-atlas-trophy]");
      if (input) {
        const done = earned.has(input.dataset.atlasTrophy);
        input.checked = done;
        card.dataset.earned = done ? "true" : "false";
      }
    }
    count.textContent = earned.size + " / " + cards.length + " trofei segnati";
    bar.value = earned.size;
    bar.setAttribute("aria-valuetext", earned.size + " su " + cards.length + " trofei segnati");
    status.textContent = visible + " trofei mostrati su " + cards.length;
    empty.hidden = visible > 0;
    for (const button of filters) {
      button.setAttribute("aria-pressed", button.dataset.atlasFilter === active ? "true" : "false");
    }
  }
  root.addEventListener("change", event => {
    const input = event.target;
    if (!(input instanceof HTMLInputElement) || !input.matches("[data-atlas-trophy]")) return;
    const n = input.dataset.atlasTrophy;
    if (!allowed.has(n)) return;
    if (input.checked) earned.add(n); else earned.delete(n);
    try {
      window.localStorage.setItem(KEY, JSON.stringify([...earned]));
      notice.textContent = "Salvato solo in questo browser. Non modifica i trofei PSN.";
    } catch (_) {
      notice.textContent = "Impossibile salvare nel browser; le spunte restano in questa sessione.";
    }
    render();
    window.dispatchEvent(new Event("gta6-italia:trophy-progress-changed"));
  });
  search.addEventListener("input", render);
  for (const button of filters) button.addEventListener("click", () => {
    active = button.dataset.atlasFilter;
    render();
  });
  window.addEventListener("pageshow", () => { earned = read(); render(); });
  window.addEventListener("storage", event => {
    if (event.key === KEY) { earned = read(); render(); }
  });
  render();
})();
