/* GTA 6 Italia: small, privacy-respecting interactions. No account APIs. */
(() => {
  "use strict";
  const MEDALS_KEY = "gta6-italia:shootist-medals:v1";
  const TROPHY_KEY = "gta6-italia:trophies:v1";
  function read(key) {
    try {
      const value = JSON.parse(window.localStorage.getItem(key) || "[]");
      return new Set(Array.isArray(value) ? value.filter(x => typeof x === "string") : []);
    } catch (_) { return new Set(); }
  }
  function save(key, values) {
    try { window.localStorage.setItem(key, JSON.stringify([...values])); return true; }
    catch (_) { return false; }
  }
  document.querySelectorAll("[data-medal-tracker]").forEach(root => {
    const boxes = [...root.querySelectorAll('input[data-medal-id]')];
    const allowed = new Set(boxes.map(x => x.dataset.medalId));
    const stored = read(MEDALS_KEY);
    const completed = new Set([...stored].filter(x => allowed.has(x)));
    const counter = root.querySelector("[data-medal-count]");
    const bar = root.querySelector("[data-medal-progress]");
    const feedback = root.querySelector("[data-medal-feedback]");
    function render() {
      for (const box of boxes) box.checked = completed.has(box.dataset.medalId);
      counter.textContent = completed.size + " / " + boxes.length;
      bar.value = completed.size;
      const percent = boxes.length ? Math.round(completed.size / boxes.length * 100) : 0;
      bar.setAttribute("aria-valuetext", completed.size + " medaglie Oro su " + boxes.length + ", " + percent + "%");
      if (completed.size === boxes.length) {
        feedback.textContent = "🎉 Checklist completa! Verifica lo sblocco del trofeo sul tuo account PS5.";
      }
    }
    root.addEventListener("change", event => {
      const target = event.target;
      if (!(target instanceof HTMLInputElement) || !target.matches("[data-medal-id]")) return;
      if (target.checked) completed.add(target.dataset.medalId);
      else completed.delete(target.dataset.medalId);
      const persisted = save(MEDALS_KEY, completed);
      render();
      if (completed.size !== boxes.length) {
        feedback.textContent = persisted
          ? "Progressi salvati solo in questo browser."
          : "Impossibile salvare in questo browser; i cambiamenti rimangono visibili finché la pagina è aperta.";
      }
    });
    root.querySelector("[data-medal-reset]")?.addEventListener("click", () => {
      if (!window.confirm("Vuoi azzerare le 42 caselle di questa checklist?")) return;
      completed.clear();
      const persisted = save(MEDALS_KEY, completed);
      render();
      feedback.textContent = persisted ? "Checklist azzerata." : "Checklist azzerata solo per questa sessione.";
    });
    render();
  });

  document.querySelectorAll("[data-trophy-done]").forEach(button => {
    const key = button.dataset.trophyDone;
    const completed = read(TROPHY_KEY);
    function render() {
      const marked = completed.has(key);
      button.setAttribute("aria-pressed", marked ? "true" : "false");
      button.textContent = marked ? "✓ Trofeo segnato come ottenuto" : "○ Segna trofeo ottenuto";
    }
    button.addEventListener("click", () => {
      if (completed.has(key)) completed.delete(key);
      else completed.add(key);
      const persisted = save(TROPHY_KEY, completed);
      render();
      const note = button.parentElement?.querySelector("[data-trophy-status]");
      if (note) note.textContent = persisted
        ? "Solo in questo browser. Non modifica i trofei PSN."
        : "Il browser non consente di salvare la selezione.";
    });
    render();
  });

  // Personal PSN-free overview. Re-read on browser Back (bfcache) and tab changes.
  document.querySelectorAll("[data-trophy-index-progress]").forEach(root => {
    const cards = [...document.querySelectorAll("[data-trophy-number]")];
    const known = new Set(cards.map(card => card.dataset.trophyNumber));
    const count = root.querySelector("[data-trophy-total]");
    const bar = root.querySelector("[data-trophy-index-bar]");
    function render() {
      const done = read(TROPHY_KEY);
      let marked = 0;
      for (const card of cards) {
        const finished = known.has(card.dataset.trophyNumber) && done.has(card.dataset.trophyNumber);
        card.dataset.completed = finished ? "true" : "false";
        if (finished) marked++;
      }
      count.textContent = marked + " / " + cards.length + " trofei segnati";
      bar.value = marked;
      bar.setAttribute("aria-valuetext", marked + " trofei segnati su " + cards.length);
    }
    window.addEventListener("pageshow", render);
    window.addEventListener("storage", render);
    render();
  });

  // Official Rockstar video only, loaded after an explicit user interaction.
  document.querySelectorAll("button[data-video-id]").forEach(button => {
    button.addEventListener("click", () => {
      const id = button.dataset.videoId || "";
      const second = Number(button.dataset.videoStart || "0");
      if (!/^[a-zA-Z0-9_-]{11}$/.test(id) || id !== "tJbzMqJGH4k" ||
          !Number.isInteger(second) || second < 0 || second > 3600) return;
      const iframe = document.createElement("iframe");
      iframe.title = "GTA VI: An Extended Look — anteprima ufficiale Rockstar, poligono";
      iframe.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&start=" + second + "&rel=0";
      iframe.loading = "lazy";
      iframe.referrerPolicy = "strict-origin-when-cross-origin";
      iframe.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share";
      iframe.allowFullscreen = true;
      iframe.className = "video-frame";
      const parent = button.closest("[data-video-slot]");
      if (parent) parent.replaceChildren(iframe);
    }, { once: true });
  });
})();
