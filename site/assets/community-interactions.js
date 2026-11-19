/* GTA VI Italia: private, accessible filters for attributed research headlines. */
(() => {
  "use strict";
  const search = document.getElementById("community-search");
  const cards = [...document.querySelectorAll(".community-card")];
  const count = document.getElementById("community-result-count");
  const empty = document.querySelector("[data-community-empty]");
  const sources = [...document.querySelectorAll("[data-community-filter-source]")];
  const statuses = [...document.querySelectorAll("[data-community-filter-status]")];
  if (search && count && sources.length && statuses.length) {
    let source = "all", status = "all";
    function paint() {
      const q = search.value.trim().toLocaleLowerCase("it-IT");
      let visible = 0;
      for (const card of cards) {
        const match = (!q || card.dataset.communitySearch.includes(q)) &&
          (source === "all" || card.dataset.communitySource === source) &&
          (status === "all" || card.dataset.communityStatus === status);
        card.hidden = !match;
        if (match) visible++;
      }
      count.textContent = visible + " segnalazioni trovate · contenuti non verificati";
      if (empty) empty.hidden = visible !== 0 || cards.length === 0;
    }
    search.addEventListener("input", paint);
    for (const button of sources) {
      button.addEventListener("click", () => {
        source = button.dataset.communityFilterSource;
        for (const b of sources) b.setAttribute("aria-pressed", String(b === button));
        paint();
      });
    }
    for (const button of statuses) {
      button.addEventListener("click", () => {
        status = button.dataset.communityFilterStatus;
        for (const b of statuses) b.setAttribute("aria-pressed", String(b === button));
        paint();
      });
    }
    paint();
  }
  // No iframe or thumbnail requests to YouTube until the visitor explicitly clicks.
  for (const button of document.querySelectorAll("button[data-community-video-id]")) {
    button.addEventListener("click", () => {
      const id = button.dataset.communityVideoId || "";
      if (!/^[a-zA-Z0-9_-]{11}$/.test(id)) return;
      const slot = button.closest("[data-community-video-slot]");
      if (!slot) return;
      const iframe = document.createElement("iframe");
      iframe.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
      iframe.title = "Video community GTA VI — fonte esterna, contenuto non verificato";
      iframe.loading = "lazy";
      iframe.referrerPolicy = "strict-origin-when-cross-origin";
      iframe.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share";
      iframe.allowFullscreen = true;
      iframe.className = "community-video-frame";
      slot.replaceChildren(iframe);
    }, {once: true});
  }
})();
