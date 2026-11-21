/* External GTA VI map embeds. Explicit human click, fixed HTTPS allowlist,
   no synthetic GPS, no auto-publish, no cookies/local storage from OUR script. */
(() => {
  "use strict";
  const SOURCES = Object.freeze({
    vice: { embed: "https://vice-map.com/embed/map", full: "https://vice-map.com/map", name: "Vice Map" },
    city: { embed: "https://gta6.city/embed/map", full: "https://gta6.city/", name: "GTA6.city" }
  });
  function metric(name) {
    // Counts an interaction only. Never implies map location, follower or PSN progress.
    const umami=window.umami;
    if(umami && typeof umami.track==="function") {
      try { umami.track(name); } catch (_) { /* Analytics is optional. */ }
    }
  }
  const instances=[...document.querySelectorAll("[data-vi-map]")];
  for(const root of instances) {
    const load=root.querySelector("[data-vim-load]");
    const wrap=root.querySelector("[data-vim-frame]");
    const status=root.querySelector("[data-vim-status]");
    const full=root.querySelector("[data-vim-full]");
    const tabs=[...root.querySelectorAll("[data-vim-provider]")];
    let provider="vice",frame=null,requestedName=null;
    if(!load || !wrap || !status || !full || tabs.length!==2) continue;
    function message(text) { status.textContent=text; }
    function createFrame() {
      if(frame) return;
      frame=document.createElement("iframe");
      frame.className="vim-iframe";
      frame.title="Mappa interattiva non ufficiale di GTA VI: zoom e navigazione";
      frame.setAttribute("loading","lazy");
      frame.setAttribute("referrerpolicy","strict-origin-when-cross-origin");
      frame.setAttribute("sandbox","allow-scripts allow-same-origin allow-forms allow-popups");
      frame.setAttribute("allowfullscreen","");
      wrap.replaceChildren(frame);
    }
    function view(name) {
      createFrame();
      let url=SOURCES[provider].embed;
      if(name && provider==="vice") url+="?marker="+encodeURIComponent(name);
      // If a third-party map refuses embedding, the full-screen link always remains.
      frame.src=url;
      load.textContent="↻ Ricarica la mappa";
      full.href=SOURCES[provider].full;
      full.textContent="Apri "+SOURCES[provider].name+" a schermo intero ↗";
      message(name && provider==="vice"
        ? "Ricerca nominale di «"+name+"» richiesta a Vice Map. Se non esiste un marker, usa ricerca e zoom manuali. Nessuna posizione esatta verificata."
        : "Mappa di "+SOURCES[provider].name+" richiesta. Usa zoom e trascinamento; l'embed potrebbe essere bloccato dal provider.");
    }
    function pick(name) {
      requestedName=name;
      if(provider!=="vice") {
        provider="vice";
        for(const tab of tabs)tab.setAttribute("aria-pressed",String(tab.dataset.vimProvider===provider));
      }
      view(name);
      root.scrollIntoView({behavior:"smooth",block:"start"});
      metric("game-map-named-search-intent");
    }
    load.addEventListener("click",()=>{view(requestedName);metric("game-map-load-intent");});
    for(const tab of tabs) {
      tab.addEventListener("click",()=>{
        const which=tab.dataset.vimProvider;
        if(!(which in SOURCES))return;
        provider=which;
        requestedName=null;
        for(const other of tabs)other.setAttribute("aria-pressed",String(other===tab));
        full.href=SOURCES[provider].full;
        full.textContent="Apri "+SOURCES[provider].name+" a schermo intero ↗";
        if(frame)view(null);
        else message(SOURCES[provider].name+" selezionato. Premi «Carica mappa interattiva» per aprirlo.");
        metric("game-map-provider-switch-intent");
      });
    }
    for(const btn of root.querySelectorAll("[data-vim-seek]")) {
      btn.addEventListener("click",()=>{
        const name=(btn.dataset.vimSeek||"").trim();
        if(name.length>1 && name.length<120)pick(name);
      });
    }
    // Checkpoint buttons outside this panel can request a nominal marker.
    document.querySelectorAll("[data-vim-map-search]").forEach(btn=>{
      btn.addEventListener("click",()=>{
        const name=(btn.dataset.vimMapSearch||"").trim();
        if(name.length>1 && name.length<120)pick(name);
      });
    });
  }
})();