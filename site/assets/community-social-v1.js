/* X-first public discussions. No GitHub account, API fetch or comment database. */
(() => {
  "use strict";
  const timeline=document.querySelector("[data-x-timeline-load]");
  const slot=document.querySelector("[data-x-timeline-slot]");
  if(timeline && slot) timeline.addEventListener("click",() => {
    timeline.disabled=true;
    timeline.textContent="Apertura dei post X…";
    const link=document.createElement("a");
    link.href="https://x.com/xFederiko11";
    link.className="twitter-timeline";
    link.textContent="Ultimi post pubblici di Federiko su X";
    link.dataset.height="550";
    link.dataset.chrome="noheader nofooter";
    link.dataset.theme=document.documentElement.dataset.theme==="dark"?"dark":"light";
    slot.append(link);
    const script=document.createElement("script");
    script.async=true;
    script.src="https://platform.twitter.com/widgets.js";
    script.onerror=()=>{
      const notice=document.createElement("p");
      notice.className="social-empty";
      notice.textContent="Il browser non consente di incorporare X: apri il profilo dal link.";
      slot.append(notice);
    };
    document.head.append(script);
    timeline.hidden=true;
  },{once:true});
})();
