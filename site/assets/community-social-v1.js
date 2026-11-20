/* Public, read-only comments; posting always occurs on GitHub with user auth.
   X timeline is optional and never injects a tracking widget without a click. */
(() => {
  "use strict";
  const api="https://api.github.com/repos/xFederiko11/gta-6/issues/";
  function make(tag,className,text) {
    const el=document.createElement(tag);
    if (className) el.className=className;
    if (text!==undefined) el.textContent=text;
    return el;
  }
  function safeLink(url,issue) {
    try {
      const u=new URL(url);
      return u.protocol==="https:" && u.hostname==="github.com" &&
        u.pathname.startsWith("/xFederiko11/gta-6/issues/"+issue) ? u.href : null;
    } catch (_) { return null; }
  }
  async function fill(section) {
    const number=section.dataset.discussionIssue;
    if (!/^\d{1,10}$/.test(number)) return;
    const list=section.querySelector("[data-comments-list]");
    if (!list) return;
    try {
      const response=await fetch(api+number+"/comments?per_page=30",{
        headers:{"Accept":"application/vnd.github+json"},
        cache:"no-store",referrerPolicy:"no-referrer"
      });
      if (!response.ok) throw new Error("Commenti temporaneamente non disponibili");
      const rows=await response.json();
      if (!Array.isArray(rows))throw new Error("Formato inatteso");
      list.replaceChildren();
      const accepted=rows.filter(row => row && row.user &&
        row.user.type==="User" && row.body && safeLink(row.html_url,number));
      const counter=section.querySelector("[data-comment-count]");
      if(counter) counter.textContent=(rows.length>=30?"Almeno ":"")+rows.length+" commenti";
      if (!accepted.length) {
        list.append(make("p","social-empty","Non ci sono ancora commenti: puoi essere il primo."));
        return;
      }
      for (const c of accepted.slice(-20)) {
        const article=make("article","social-comment");
        const header=make("div","social-comment-meta");
        header.append(make("strong","", "@" + c.user.login.slice(0,40)));
        const dt=new Date(c.created_at);
        if (!Number.isNaN(+dt)) {
          const time=make("time","",dt.toLocaleDateString("it-IT"));
          time.dateTime=c.created_at;header.append(time);
        }
        const text=make("p","social-comment-body",c.body.slice(0,700));
        const footer=make("div","social-comment-footer");
        const link=make("a","","Rispondi / leggi su GitHub ↗");
        link.href=safeLink(c.html_url,number);
        link.target="_blank";link.rel="noopener noreferrer";
        footer.append(link);
        const count=Number(c.reactions?.["+1"]||0);
        if (Number.isInteger(count) && count>0) footer.append(make("span","","👍 "+count));
        article.append(header,text,footer);
        list.append(article);
      }
    } catch (_) {
      list.replaceChildren(make("p","social-empty",
        "I commenti non sono caricabili in questo momento. Puoi leggerli e partecipare su GitHub."));
    }
  }
  const sections=document.querySelectorAll("[data-discussion-issue]");
  if ("IntersectionObserver" in window) {
    const observer=new IntersectionObserver(entries => {
      for(const entry of entries) if(entry.isIntersecting) {
        observer.unobserve(entry.target);
        fill(entry.target);
      }
    },{rootMargin:"450px 0px"});
    sections.forEach(s=>observer.observe(s));
  } else sections.forEach(fill);

  const timeline=document.querySelector("[data-x-timeline-load]");
  const slot=document.querySelector("[data-x-timeline-slot]");
  if(timeline && slot) timeline.addEventListener("click",() => {
    timeline.disabled=true;
    timeline.textContent="Apertura dei post X…";
    const a=make("a","","Ultimi post pubblici di Federiko su X");
    a.href="https://x.com/xFederiko11";
    a.className="twitter-timeline";
    a.dataset.height="550";
    a.dataset.chrome="noheader nofooter";
    a.dataset.theme=document.documentElement.dataset.theme==="dark"?"dark":"light";
    slot.append(a);
    const script=document.createElement("script");
    script.async=true;script.src="https://platform.twitter.com/widgets.js";
    script.onerror=()=>{
      slot.append(make("p","social-empty","X non permette di visualizzare il feed nel browser: aprilo dal link."));
    };
    document.head.append(script);
    timeline.hidden=true;
  },{once:true});
})();
