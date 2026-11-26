/* X-first public discussions. No GitHub account, API fetch or comment database. */
(() => {
  "use strict";
  // Genuine Buffer sent-post links, no X API credentials in the browser.
  const BRIDGE="https://raw.githubusercontent.com/xFederiko11/federiko-gta-playstation-bot/main/data/x-permalinks-v1.json";
  const cleanUrl=(value)=>{
    if(typeof value!=="string")return null;
    try{
      const u=new URL(value);
      if(u.protocol!=="https:"||u.hostname!=="xfederiko11.github.io"||
         !u.pathname.startsWith("/gta-6/")||!u.pathname.endsWith("/")||
         u.search||u.hash||u.username||u.password)return null;
      return u.href;
    }catch(_){return null;}
  };
  const cleanX=(value)=>{
    if(typeof value!=="string"||/[\x00-\x20]/.test(value))return null;
    try{
      const u=new URL(value);
      if(u.protocol!=="https:"||u.hostname!=="x.com"||
         u.search||u.hash||u.username||u.password)return null;
      const m=u.pathname.match(/^\/xFederiko11\/status\/([0-9]{8,25})\/?$/i);
      return m ? "https://x.com/xFederiko11/status/"+m[1] : null;
    }catch(_){return null;}
  };
  const make=(tag,cls,value)=>{
    const node=document.createElement(tag);
    if(cls)node.className=cls;
    if(value!==undefined)node.textContent=value;
    return node;
  };
  const verifiedPosts=(value)=>{
    if(!value||value.schema!=="verified-buffer-x-permalinks-v1"||
       !Array.isArray(value.posts))return [];
    const used=new Set(),items=[];
    for(const p of value.posts.slice(0,200)){
      if(!p||p.verified_by!=="Buffer sent Post.externalLink on verified @xFederiko11 channel")continue;
      const article=cleanUrl(p.article_url),link=cleanX(p.x_url);
      if(!article||!link||used.has(link)||typeof p.excerpt!=="string"||
         p.excerpt.trim().length<12||typeof p.sent_at!=="string"||
         !Number.isFinite(Date.parse(p.sent_at)))continue;
      used.add(link);
      items.push({article,x_url:link,excerpt:p.excerpt.trim().slice(0,440),
                  sent_at:p.sent_at});
    }
    return items.sort((a,b)=>Date.parse(b.sent_at)-Date.parse(a.sent_at));
  };
  const addLink=(parent,label,url)=>{
    const a=make("a","",label);
    a.href=url;a.target="_blank";a.rel="noopener noreferrer";
    // The optional Umami script is only present after the owner opts in.
    // Classify only these known destinations, not any user's content.
    if(document.getElementById("growth-analytics-v1")){
      if(/^https:\/\/x\.com\/xFederiko11\/status\/[0-9]+$/.test(url))
        a.dataset.umamiEvent="x-post-open";
      else if(/^https:\/\/x\.com\/intent\/tweet\?in_reply_to=[0-9]+$/.test(url))
        a.dataset.umamiEvent="x-reply-intent";
    }
    parent.append(a);
  };
  function connectArticle(section,posts){
    const article=cleanUrl(section.dataset.xArticleUrl);
    if(!article)return;
    const matched=posts.filter(p=>p.article===article).slice(0,3);
    if(!matched.length)return;
    const lead=matched[0],primary=section.querySelector("[data-x-primary-action]");
    if(primary){
      primary.href="https://x.com/intent/tweet?in_reply_to="+lead.x_url.split("/").pop();
      primary.textContent="💬 Rispondi al post su X";
      // SSR fallback is an X contact intent. When a verified real post
      // arrives, reclassify the same CTA: otherwise analytics silently
      // misattributes genuine replies as contact-intent clicks.
      if(document.getElementById("growth-analytics-v1"))
        primary.dataset.umamiEvent="x-reply-intent";
    }
    const note=section.querySelector("[data-x-reply-note]");
    if(note)note.textContent="Post pubblicato e permalink X recuperato dalle ricevute Buffer. "
      +"Commenti e reazioni sono gestiti direttamente su X; non servono account GitHub.";
    const prev=section.previousElementSibling;
    if(prev&&prev.classList.contains("social-x-excerpt"))prev.hidden=true;
    const stack=make("div","social-x-matches");
    const h=make("h3","","𝕏 Post X collegati a questa guida");
    stack.append(h);
    matched.forEach(p=>{
      const card=make("article","social-x-match");
      const quote=make("blockquote","",p.excerpt);
      const actions=make("div","social-x-match-actions");
      addLink(actions,"Apri il post originale ↗",p.x_url);
      addLink(actions,"Rispondi su X ↗",
        "https://x.com/intent/tweet?in_reply_to="+p.x_url.split("/").pop());
      card.append(quote,actions);stack.append(card);
    });
    const controls=section.querySelector(".social-discussion-cta");
    if(controls)section.insertBefore(stack,controls);
  }
  function renderHome(posts){
    if(!posts.length)return;
    document.querySelectorAll("[data-x-live-grid]").forEach(grid=>{
    const cards=[];
    for(const p of posts.slice(0,4)){
      const card=make("article","social-comment-card");
      card.append(make("span","","𝕏 @xFederiko11"));
      card.append(make("p","",p.excerpt.slice(0,210)));
      addLink(card,"Leggi e rispondi su X ↗",p.x_url);
      cards.push(card);
    }
    grid.replaceChildren(...cards);
    });
  }
  async function syncVerifiedLinks(){
    try{
      const response=await fetch(BRIDGE,{method:"GET",mode:"cors",cache:"no-store",
                                        referrerPolicy:"no-referrer"});
      if(!response.ok)return;
      const data=await response.json(),posts=verifiedPosts(data);
      document.querySelectorAll("[data-x-article-url]").forEach(s=>connectArticle(s,posts));
      renderHome(posts);
    }catch(_){/* preserve safe server-rendered fallback */ }
  }
  if(document.querySelector("[data-x-article-url]")||document.querySelector("[data-x-live-grid]")){
    syncVerifiedLinks();
  }
  document.querySelectorAll("[data-x-timeline-load]").forEach(timeline=>{
    const panel=timeline.closest(".sb-x-panel")||document;
    const slot=panel.querySelector("[data-x-timeline-slot]");
    if(!slot)return;
    timeline.addEventListener("click",()=>{
      timeline.disabled=true;
      const link=document.createElement("a");
      link.href="https://x.com/xFederiko11";
      link.className="twitter-timeline";
      link.textContent="Ultimi post pubblici di Federiko su X";
      link.dataset.height="420";
      link.dataset.chrome="noheader nofooter";
      link.dataset.theme=document.documentElement.dataset.theme==="light"?"light":"dark";
      slot.append(link);
      const warn=()=>{
        const notice=document.createElement("p");
        notice.className="social-empty";
        notice.textContent="Il feed incorporato non è disponibile: apri il profilo dal link.";
        slot.append(notice);
      };
      const source="https://platform.twitter.com/widgets.js";
      const existing=document.querySelector('script[src="'+source+'"]');
      if(window.twttr&&window.twttr.widgets){
        try{window.twttr.widgets.load(slot)}catch(_){warn()}
      }else if(existing){
        existing.addEventListener("load",()=>{try{window.twttr?.widgets?.load(slot)}catch(_){warn()}},{once:true});
        existing.addEventListener("error",warn,{once:true});
      }else{
        const script=document.createElement("script");
        script.async=true;
        script.src=source;
        script.onerror=warn;
        document.head.append(script);
      }
      timeline.hidden=true;
    },{once:true});
  });
})();
