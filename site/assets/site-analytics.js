/* GTA 6 Italia: anonymous link engagement, loaded only when opt-in config is set.
   No cookies, localStorage, URL query strings, search terms or PSN data.
   Page views are tracked by GoatCounter itself; this script adds aggregate click events.
   This file never sends a request unless there is a configured endpoint and permission.
*/
(() => {
  "use strict";
  const ownScript = document.currentScript;
  const endpoint = ownScript?.dataset.analyticsEndpoint || "";
  if (!/^https:\/\/[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.goatcounter\.com\/count$/.test(endpoint)) return;
  if (window.location.hostname !== "xfederiko11.github.io") return;
  if (!window.location.pathname.startsWith("/gta-6/")) return;

  // Explicitly avoid loading the external analytics library for privacy signals.
  if (navigator.globalPrivacyControl === true || navigator.doNotTrack === "1" ||
      window.doNotTrack === "1" || navigator.msDoNotTrack === "1") return;

  const prefix = "/gta-6/";
  const destHosts = Object.freeze({
    "x.com": "social-x",
    "twitter.com": "social-x",
    "youtube.com": "youtube",
    "www.youtube.com": "youtube",
    "youtu.be": "youtube",
    "www.powerpyx.com": "powerpyx",
    "powerpyx.com": "powerpyx",
    "www.gtabase.com": "gtabase",
    "gtabase.com": "gtabase",
    "gta.wiki": "gta-wiki",
    "gta.fandom.com": "gta-fandom",
    "www.rockstargames.com": "rockstar",
    "rockstargames.com": "rockstar",
    "www.playstation.com": "playstation",
    "playstation.com": "playstation",
    "www.reddit.com": "reddit",
    "reddit.com": "reddit",
    "github.com": "github",
  });
  function sitePath(path) {
    if (!path.startsWith(prefix)) return null;
    const raw = path.slice(prefix.length).replace(/\/index\.html$/, "/").replace(/\/$/, "");
    if (raw.length > 110 || !/^[a-zA-Z0-9/_-]*$/.test(raw)) return null;
    return raw || "home";
  }
  function targetName(rawUrl) {
    let u;
    try { u = new URL(rawUrl, location.href); } catch (_) { return null; }
    if (u.protocol !== "https:") return null;
    if (u.origin === location.origin) {
      const dest = sitePath(u.pathname);
      return dest ? "site-" + dest : null;
    }
    // Never send full external URLs or visitor-supplied queries to analytics.
    const group = destHosts[u.hostname.toLowerCase()];
    if (!group) return null;
    if (group === "social-x" && !u.pathname.startsWith("/xFederiko11")) return null;
    return "external-" + group;
  }
  function placement(anchor) {
    if (anchor.closest(".mainnav")) return "main-menu";
    if (anchor.closest(".discovery-rail")) return "recommended";
    if (anchor.closest(".community-card")) return "discovery-source";
    if (anchor.closest(".guide-sidebar,.sidebox")) return "sidebar";
    if (anchor.closest(".source-details")) return "source-details";
    if (anchor.closest(".footer")) return "footer";
    if (anchor.closest(".hero")) return "home-hero";
    return "content";
  }
  function send(category, target) {
    const from = sitePath(location.pathname);
    if (!from || !window.goatcounter || typeof window.goatcounter.count !== "function") return;
    const name = "click:" + category + ":" + from + ":" + target;
    if (name.length > 240) return;
    try {
      window.goatcounter.count({
        path: name,
        title: "GTA VI | " + category + " | " + from + " → " + target,
        event: true,
        no_session: true
      });
    } catch (_) { /* Analytics must never interfere with the site. */ }
  }
  document.addEventListener("click", event => {
    if (!(event.target instanceof Element)) return;
    const anchor = event.target.closest("a[href]");
    if (anchor) {
      const to = targetName(anchor.href);
      if (to) send(placement(anchor), to);
      return;
    }
    const button = event.target.closest("button");
    if (!button) return;
    let action;
    if (button.hasAttribute("data-guide-copy")) action = "copy-guide-steps";
    else if (button.hasAttribute("data-hdr-copy")) action = "copy-hdr-values";
    else if (button.hasAttribute("data-copy-sequence")) action = "copy-cheat-sequence";
    else if (button.hasAttribute("data-community-video-id")) action = "play-source-video";
    else if (button.hasAttribute("data-video-id")) action = "play-official-video";
    if (action) send("interaction", action);
  }, {passive: true});

  const provider = document.createElement("script");
  provider.async = true;
  provider.src = "https://gc.zgo.at/count.js";
  provider.dataset.goatcounter = endpoint;
  document.head.appendChild(provider);
})();
