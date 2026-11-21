/* Local-only planning checklist. No PSN calls, account data or network requests. */
(() => {
  "use strict";
  const root = document.querySelector("[data-platinum-roadmap]");
  if (!root) return;
  const KEY = "gta6-italia:platinum-roadmap:v1";
  const TROPHIES_KEY = "gta6-italia:trophies:v1";
  const checks = [...root.querySelectorAll("input[data-roadmap-check]")];
  const valid = new Set(checks.map(box => box.dataset.roadmapCheck));
  const read = (key) => {
    try {
      const values = JSON.parse(window.localStorage.getItem(key) || "[]");
      return new Set(Array.isArray(values) ? values.filter(v => typeof v === "string") : []);
    } catch (_) { return new Set(); }
  };
  const selected = new Set([...read(KEY)].filter(key => valid.has(key)));
  const progress = root.querySelector("[data-roadmap-progress]");
  const counter = root.querySelector("[data-roadmap-count]");
  const storage = root.querySelector("[data-roadmap-storage]");
  const render = () => {
    checks.forEach(box => { box.checked = selected.has(box.dataset.roadmapCheck); });
    counter.textContent = selected.size + " / " + checks.length + " attività segnate";
    progress.value = selected.size;
    progress.setAttribute("aria-valuetext", selected.size + " su " + checks.length + " attività");
    root.querySelectorAll("[data-roadmap-phase]").forEach(phase => {
      const boxes = [...phase.querySelectorAll("input[data-roadmap-check]")];
      const done = boxes.filter(box => selected.has(box.dataset.roadmapCheck)).length;
      phase.querySelector("[data-phase-count]").textContent = done + " / " + boxes.length;
      phase.dataset.completed = done === boxes.length ? "true" : "false";
    });
    const earned = read(TROPHIES_KEY);
    root.querySelectorAll("[data-roadmap-trophy]").forEach(link => {
      const yes = earned.has(link.dataset.roadmapTrophy);
      link.dataset.earned = yes ? "true" : "false";
      const status = link.querySelector("[data-roadmap-trophy-status]");
      if (status) status.textContent = yes ? "segnato come ottenuto" : "da verificare su PS5";
    });
  };
  root.addEventListener("change", event => {
    const box = event.target;
    if (!(box instanceof HTMLInputElement) || !box.matches("input[data-roadmap-check]")) return;
    if (box.checked) selected.add(box.dataset.roadmapCheck);
    else selected.delete(box.dataset.roadmapCheck);
    try {
      window.localStorage.setItem(KEY, JSON.stringify([...selected]));
      storage.textContent = "Progressi salvati solo nel browser corrente. Non sincronizzati con PSN.";
    } catch (_) {
      storage.textContent = "Salvataggio nel browser non disponibile; le spunte restano in questa pagina.";
    }
    render();
  });
  window.addEventListener("storage", () => {
    selected.clear();
    for (const key of read(KEY)) if (valid.has(key)) selected.add(key);
    render();
  });
  window.addEventListener("gta6-italia:trophy-progress-changed", render);
  window.addEventListener("pageshow", render);
  render();
})();
