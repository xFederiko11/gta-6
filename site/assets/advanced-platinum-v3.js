/* Local-only editable GTA VI 100% and collectible card checklist; no PSN API. */
(() => {
  "use strict";
  const root = document.querySelector("[data-advanced-platinum-100]");
  if (!root) return;
  const STORAGE = "gta6-italia:100-completion:v3";
  const CARDS = "gta6-italia:card-sets:v3";
  const metrics = [...root.querySelectorAll("[data-ap-metric]")];
  const sets = [...root.querySelectorAll("input[data-ap-card]")];
  const maxValue = input => Number(input.getAttribute("max"));
  function getRecord(key, fallback, valid) {
    try {
      const parsed = JSON.parse(window.localStorage.getItem(key) || "null");
      return valid(parsed) ? parsed : fallback;
    } catch (_) { return fallback; }
  }
  const readMetrics = () => getRecord(STORAGE, {}, v => Boolean(v) && typeof v === "object" && !Array.isArray(v));
  const readCards = () => getRecord(CARDS, [], Array.isArray);
  let counts = readMetrics();
  let doneCards = new Set(readCards().filter(x => typeof x === "string"));
  const counter = root.querySelector("[data-ap-done-count]");
  const overall = root.querySelector("[data-ap-overall-progress]");
  const cardCounter = root.querySelector("[data-ap-card-count]");
  const cardProgress = root.querySelector("[data-ap-card-progress]");
  const cardDetails = root.querySelector("[data-ap-card-details]");
  const status = root.querySelector("[data-ap-storage]");
  function clamp(val, max) {
    const n = Number(val);
    return Number.isFinite(n) ? Math.max(0, Math.min(max, Math.floor(n))) : 0;
  }
  function render() {
    let reached = 0;
    for (const metric of metrics) {
      const input = metric.querySelector("input[data-ap-input]");
      const goal = Number(metric.dataset.apTarget);
      const value = clamp(counts[input.dataset.apInput], maxValue(input));
      input.value = String(value);
      const success = value >= goal;
      if (success) reached++;
      metric.dataset.complete = success ? "true" : "false";
      metric.querySelector("[data-ap-metric-status]").textContent = success ? "Raggiunto" : "Da fare";
      metric.querySelector("[data-ap-bar]").value = Math.min(value, goal);
      metric.querySelector("[data-ap-ratio]").textContent = value.toLocaleString("it-IT") + " / " + goal.toLocaleString("it-IT");
    }
    counter.textContent = reached + " / " + metrics.length + " categorie raggiunte";
    overall.value = reached;
    let completedSets = 0;
    for (const box of sets) {
      const yes = doneCards.has(box.dataset.apCard);
      box.checked = yes;
      if (yes) completedSets++;
    }
    cardCounter.textContent = completedSets + " / " + sets.length + " set completati";
    cardProgress.value = Math.min(completedSets, 15);
    cardDetails.textContent = completedSets >= 15 ? "Target 100% (15 set) spuntato manualmente; verifica in gioco."
      : completedSets >= 3 ? "Trofeo da 3 set: obiettivo segnato. Mancano " + (15-completedSets) + " set al 100%."
      : "Primo trofeo: 3 set · Mancano " + (3-completedSets) + " set al primo traguardo.";
  }
  root.addEventListener("change", event => {
    const target = event.target;
    if (!(target instanceof HTMLInputElement)) return;
    if (target.matches("input[data-ap-input]")) {
      const key = target.dataset.apInput;
      const val = clamp(target.value, maxValue(target));
      counts[key] = val;
      try {
        window.localStorage.setItem(STORAGE, JSON.stringify(counts));
        status.textContent = "Progresso salvato solo su questo dispositivo; nessun accesso a PSN.";
      } catch (_) {
        status.textContent = "Salvataggio non disponibile; i dati restano nella pagina aperta.";
      }
    } else if (target.matches("input[data-ap-card]")) {
      const id = target.dataset.apCard;
      if (target.checked) doneCards.add(id); else doneCards.delete(id);
      try {
        window.localStorage.setItem(CARDS, JSON.stringify([...doneCards]));
        status.textContent = "Set salvati solo su questo dispositivo; conferma sempre il menu PS5.";
      } catch (_) {
        status.textContent = "Salvataggio non disponibile; le spunte restano nella pagina aperta.";
      }
    } else return;
    render();
  });
  window.addEventListener("pageshow", () => {
    counts = readMetrics();
    doneCards = new Set(readCards().filter(x => typeof x === "string"));
    render();
  });
  window.addEventListener("storage", evt => {
    if (evt.key !== STORAGE && evt.key !== CARDS) return;
    counts = readMetrics();
    doneCards = new Set(readCards().filter(x => typeof x === "string"));
    render();
  });
  render();
})();
