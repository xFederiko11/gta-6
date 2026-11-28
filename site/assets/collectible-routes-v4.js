/* GTA VI Italia: user-controlled local checklist for sourced, partial collectibles. */
(() => {
  "use strict";
  const root=document.querySelector("[data-collectible-routes]");
  if (!root) return;
  const KEY="gta6-italia:collectible-routes:v4";
  const points=[...root.querySelectorAll("[data-cr-step]")];
  const regions=[...root.querySelectorAll("[data-cr-region]")];
  const known=new Set(points.map(p=>p.dataset.crStep));
  const query=root.querySelector("[data-cr-query]");
  const buttons=[...root.querySelectorAll("[data-cr-filter]")];
  const summary=root.querySelector("[data-cr-progress]");
  const progress=root.querySelector("[data-cr-bar]");
  const visible=root.querySelector("[data-cr-visible]");
  const notice=root.querySelector("[data-cr-storage]");
  let filter="all";
  let cardSet=null;
  const jack=root.querySelector("[data-cr-jack]");
  function read() {
    try {
      const parsed=JSON.parse(window.localStorage.getItem(KEY) || "[]");
      return new Set(Array.isArray(parsed)?parsed.filter(x=>typeof x==="string" && known.has(x)):[]);
    } catch (_) { return new Set(); }
  }
  let done=read();
  const norm=x=>(x||"").toLocaleLowerCase("it-IT").normalize("NFD").replace(/[\u0300-\u036f]/g,"");
  function draw() {
    const q=norm(query.value.trim());
    let shown=0;
    for (const point of points) {
      const matches=(filter==="all"||point.dataset.crType===filter) && (!cardSet||point.dataset.crSet===cardSet) && (!q||norm(point.dataset.crSearch).includes(q));
      point.hidden=!matches;
      if (matches) shown++;
      const checkbox=point.querySelector("input[data-cr-done]");
      const yes=done.has(point.dataset.crStep);
      checkbox.checked=yes;
      point.dataset.completed=yes?"true":"false";
    }
    for (const region of regions) {
      const all=[...region.querySelectorAll("[data-cr-step]")];
      const found=all.filter(x=>done.has(x.dataset.crStep)).length;
      const present=all.some(x=>!x.hidden);
      region.hidden=!present;
      region.querySelector("[data-cr-region-count]").textContent=found+"/"+all.length;
    }
    for (const button of buttons) button.setAttribute("aria-pressed",button.dataset.crFilter===filter?"true":"false");
    if (jack) jack.setAttribute("aria-pressed",String(cardSet==="jack-of-hearts"));
    summary.textContent=done.size+" / "+points.length+" checkpoint segnati";
    progress.value=done.size;
    progress.setAttribute("aria-valuetext",done.size+" di "+points.length+" checkpoint");
    visible.textContent=shown+" checkpoint mostrati su "+points.length;
  }
  root.addEventListener("change",event=>{
    const target=event.target;
    if (!(target instanceof HTMLInputElement) || !target.matches("input[data-cr-done]")) return;
    const id=target.dataset.crDone;
    if (!known.has(id)) return;
    if (target.checked) done.add(id); else done.delete(id);
    try {
      window.localStorage.setItem(KEY,JSON.stringify([...done]));
      notice.textContent="Progresso salvato soltanto su questo dispositivo, non su PSN.";
    } catch (_) {
      notice.textContent="Salvataggio locale non disponibile; le spunte restano in questa pagina.";
    }
    draw();
  });
  if (jack) {
    jack.hidden=false;
    jack.addEventListener("click",()=>{cardSet="jack-of-hearts";filter="all";query.value="";draw();});
  }
  query.addEventListener("input",draw);
  buttons.forEach(button=>button.addEventListener("click",()=>{
    cardSet=null;
    filter=button.dataset.crFilter;
    draw();
  }));
  window.addEventListener("pageshow",()=>{done=read();draw();});
  window.addEventListener("storage",event=>{if(event.key===KEY){done=read();draw();}});
  draw();
})();
