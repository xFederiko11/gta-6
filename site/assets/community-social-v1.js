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
      const date=new Date(p.sent_at);
      const parts=Object.fromEntries(new Intl.DateTimeFormat("it-IT",{timeZone:"Europe/Rome",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hourCycle:"h23"}).formatToParts(date).map(p=>[p.type,p.value]));
      const stamp=make("time","sb-post-time",parts.day+"/"+parts.month+"/"+parts.year+" · "+parts.hour+":"+parts.minute);
      stamp.dateTime=p.sent_at;
      stamp.title="Orario italiano";
      card.append(stamp);
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
  // Fetch the existing public receipt feed only when a discussion/rail is
  // near the viewport. Native links and server-rendered excerpts work offline.
  let receiptFetchStarted=false;
  function loadReceipts(){
    if(receiptFetchStarted)return;
    receiptFetchStarted=true;
    syncVerifiedLinks();
  }
  const receiptPanels=document.querySelectorAll("[data-x-article-url],[data-x-live-grid]");
  if(receiptPanels.length){
    if("IntersectionObserver" in window){
      const observer=new IntersectionObserver(entries=>{
        if(entries.some(e=>e.isIntersecting)){
          observer.disconnect();
          loadReceipts();
        }
      },{rootMargin:"200px"});
      receiptPanels.forEach(panel=>observer.observe(panel));
    }else loadReceipts();
  }
  document.querySelectorAll("[data-x-timeline-load]").forEach(timeline=>{
    const panel=timeline.closest(".sb-x-panel")||document;
    const slot=panel.querySelector("[data-x-timeline-slot]");
    const link=slot&&slot.querySelector("a.twitter-timeline");
    if(!slot||!link)return;
    let started=false;
    const warn=(script)=>{
      if(script)script.dataset.xFeedFailed="true";
      started=false;
      timeline.disabled=false;
      timeline.hidden=false;
      timeline.textContent="Riprova il feed X";
      const notice=make("p","social-empty","La timeline X non è disponibile. Puoi aprire il profilo dal collegamento qui sotto.");
      slot.append(notice);
    };
    const render=()=>{
      try{
        if(!window.twttr||!window.twttr.widgets)throw new Error("X widget unavailable");
        const rendered=window.twttr.widgets.load(slot);
        if(rendered&&typeof rendered.then==="function"){
          rendered.then(()=>{timeline.hidden=true;}).catch(()=>warn());
        }else timeline.hidden=true;
      }catch(_){warn();}
    };
    const load=()=>{
      if(started)return;
      started=true;
      timeline.disabled=true;
      timeline.textContent="Caricamento feed X…";
      link.dataset.theme=document.documentElement.dataset.theme==="light"?"light":"dark";
      slot.querySelectorAll(".social-empty").forEach(n=>n.remove());
      const source="https://platform.twitter.com/widgets.js";
      let existing=document.querySelector('script[src="'+source+'"]');
      if(existing&&existing.dataset.xFeedFailed==="true"){
        existing.remove();
        existing=null;
      }
      if(window.twttr&&window.twttr.widgets){
        render();
      }else if(existing){
        existing.addEventListener("load",render,{once:true});
        existing.addEventListener("error",()=>warn(existing),{once:true});
      }else{
        const script=document.createElement("script");
        script.async=true;
        script.src=source;
        script.onerror=()=>warn(script);
        document.head.append(script);
      }
    };
    timeline.addEventListener("click",load);
    if("IntersectionObserver" in window){
      const observer=new IntersectionObserver(entries=>{
        if(entries.some(e=>e.isIntersecting)){
          observer.disconnect();
          load();
        }
      },{rootMargin:"200px"});
      observer.observe(panel);
    }else load();
  });
})();
