/* GTA VI Italia: per-guide checklist and copy, all local-only, no trackers or PSN API. */
(() => {
  "use strict";
  const PREFIX = "gta6-italia:guide-steps:v1:";
  function stored(key) {
    try {
      const rows = JSON.parse(window.localStorage.getItem(key) || "[]");
      return new Set(Array.isArray(rows) ? rows.filter(x => typeof x === "string") : []);
    } catch (_) { return new Set(); }
  }
  function persist(key, rows) {
    try {
      window.localStorage.setItem(key, JSON.stringify([...rows]));
      return true;
    } catch (_) { return false; }
  }
  document.querySelectorAll("[data-guide-steps]").forEach(root => {
    const id = root.dataset.guideSteps || "";
    if (!/^[a-z0-9-]{1,90}$/.test(id)) return;
    const version = root.dataset.guideVersion || "initial";
    if (!/^[a-f0-9]{12}$/.test(version)) return;
    const key = PREFIX + id + ":" + version;
    const boxes = [...root.querySelectorAll("input[data-guide-step]")];
    const allowed = new Set(boxes.map(x => x.dataset.guideStep));
    let checked = new Set([...stored(key)].filter(x => allowed.has(x)));
    const count = root.querySelector("[data-guide-count]");
    const progress = root.querySelector(".guide-steps-progress");
    const note = root.querySelector("[data-guide-feedback]");
    function render() {
      for (const box of boxes) box.checked = checked.has(box.dataset.guideStep);
      if (count) count.textContent = checked.size + " / " + boxes.length;
      if (progress) {
        progress.value = checked.size;
        progress.setAttribute("aria-valuetext",
          checked.size + " passaggi segnati su " + boxes.length);
      }
    }
    root.addEventListener("change", e => {
      const box = e.target;
      if (!(box instanceof HTMLInputElement) || !box.matches("[data-guide-step]")) return;
      if (box.checked) checked.add(box.dataset.guideStep);
      else checked.delete(box.dataset.guideStep);
      const ok = persist(key, checked);
      render();
      if (note) {
        note.textContent = !ok
          ? "Il browser non consente il salvataggio: le spunte rimangono solo finché questa pagina è aperta."
          : checked.size === boxes.length
            ? "✓ Checklist completata. Verifica il risultato direttamente in GTA VI; non modifica i trofei PSN."
            : "Progressi salvati soltanto su questo dispositivo. Nessun collegamento PSN.";
      }
    });
    root.querySelector("[data-guide-copy]")?.addEventListener("click", async () => {
      const steps = [...root.querySelectorAll(".guide-step-text")]
        .map((x, index) => (index + 1) + ". " + x.textContent.trim());
      if (!steps.length || !navigator.clipboard || !navigator.clipboard.writeText) {
        if (note) note.textContent = "Copia non disponibile in questo browser. Puoi selezionare il testo dei passaggi.";
        return;
      }
      try {
        await navigator.clipboard.writeText(steps.join("\n"));
        if (note) note.textContent = "Passaggi copiati. Nessun dato inviato ad altri servizi.";
      } catch (_) {
        if (note) note.textContent = "Copia non autorizzata dal browser. Puoi selezionare i passaggi manualmente.";
      }
    });
    window.addEventListener("storage", event => {
      if (event.key === key) {
        checked = new Set([...stored(key)].filter(x => allowed.has(x)));
        render();
      }
    });
    window.addEventListener("pageshow", render);
    render();
  });
})();
