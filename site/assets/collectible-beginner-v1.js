/* GTA VI Italia: one real documented collectible at a time.
   Reuses the original LI and the existing local checklist. Never duplicates
   checkboxes, pins, coordinates, images or trophy/PSN completion claims. */
(() => {
  "use strict";
  const root=document.querySelector("[data-collectible-routes]");
  const wizard=root?.querySelector("[data-cr-wizard]");
  if (!root || !wizard) return;
  const points=[...root.querySelectorAll("[data-cr-step]")];
  const slot=wizard.querySelector("[data-cr-wizard-item]");
  if (points.length!==123 || !slot) return; // Don't hide the original list on bad data.
  const count=wizard.querySelector("[data-cr-wizard-count]");
  const help=wizard.querySelector("[data-cr-wizard-help]");
  const found=wizard.querySelector("[data-cr-wizard-found]");
  const skip=wizard.querySelector("[data-cr-wizard-skip]");
  const back=wizard.querySelector("[data-cr-wizard-back]");
  const toggle=wizard.querySelector("[data-cr-wizard-toggle]");
  const finished=wizard.querySelector("[data-cr-wizard-done]");
  const restart=wizard.querySelector("[data-cr-wizard-restart]");
  const note=wizard.querySelector("[data-cr-wizard-local]");
  const search=root.querySelector("[data-cr-query]");
  const allFilter=root.querySelector('[data-cr-filter="all"]');
  const sorted=[...points].sort((a,b)=>
    Number(a.dataset.crDeadline)-Number(b.dataset.crDeadline)
    || points.indexOf(a)-points.indexOf(b));
  const byId=new Map(sorted.map((item,index)=>[item.id,index]));
  const rawHash=location.hash.slice(1);
  let index=byId.has(rawHash) ? byId.get(rawHash)
    : Math.max(0,sorted.findIndex(p=>!p.querySelector("[data-cr-done]").checked));
  let guided=true;
  let ended=false;
  let active=null;
  let anchor=null;

  function restore(){
    if (active && anchor && anchor.parentNode) anchor.replaceWith(active);
    active=null;
    anchor=null;
  }
  function actualDone(){
    return points.filter(p=>p.querySelector("[data-cr-done]").checked).length;
  }
  function show(scroll=false){
    restore();
    root.dataset.crGuided=guided?"true":"false";
    wizard.hidden=false;
    const step=sorted[index];
    if (guided && !ended) {
      if (!step) return;
      // Move rather than clone: exactly 123 checkboxes and 123 IDs at all times.
      anchor=document.createComment("original collectible position");
      step.before(anchor);
      slot.appendChild(step);
      active=step;
      step.hidden=false;
      count.textContent="CHECKPOINT "+(index+1)+" DI "+sorted.length;
      const d=Number(step.dataset.crDeadline);
      help.textContent=d===1 ? "PRIORITÀ: copia del Capitolo 1. Verifica prima di avanzare."
        : d===2 ? "PRIORITÀ: contenuto legato al Capitolo 2."
        : d===3 ? "PRIORITÀ: copia del Capitolo 3."
        : "Cerca il luogo, esegui la raccolta, poi premi TROVATO.";
      back.disabled=index===0;
      found.hidden=false;
      skip.hidden=false;
      finished.hidden=true;
      note.textContent=actualDone()+" / 123 segnati qui. Non è il contatore del gioco.";
      toggle.textContent="Preferisci vedere tutti? Apri elenco, filtri e altre sezioni";
      if (scroll) wizard.scrollIntoView({block:"start",behavior:"auto"});
    } else {
      found.hidden=true;
      skip.hidden=true;
      back.disabled=true;
      if (ended && guided) {
        finished.hidden=false;
        count.textContent="FINE DEL PERCORSO DOCUMENTATO";
        help.textContent="La lista è parziale: controlla il progresso vero sul gioco.";
        note.textContent=actualDone()+" / 123 checkpoint segnati in questo browser.";
        toggle.textContent="Vedi tutti i checkpoint e la mappa";
      } else {
        finished.hidden=true;
        count.textContent="ELENCO COMPLETO · 123 CHECKPOINT";
        help.textContent="Usa ricerca, filtri e spunte. I percorsi sono descrizioni, non GPS.";
        toggle.textContent="← Torna a un solo checkpoint alla volta";
      }
      if (scroll) wizard.scrollIntoView({block:"start",behavior:"auto"});
    }
  }

  function advance(marked){
    if (!guided || ended) return;
    if (marked && active){
      const box=active.querySelector("input[data-cr-done]");
      if (box && !box.checked){
        box.checked=true;
        box.dispatchEvent(new Event("change",{bubbles:true}));
      }
    }
    if (index+1<sorted.length) {
      index++;
      history.replaceState(null,"","#"+sorted[index].id);
      show(true);
    } else {
      ended=true;
      history.replaceState(null,"","#cr-percorso-completato");
      show(true);
    }
  }

  found.addEventListener("click",()=>advance(true));
  skip.addEventListener("click",()=>advance(false));
  back.addEventListener("click",()=>{
    if (!guided || index===0) return;
    ended=false;
    index--;
    history.replaceState(null,"","#"+sorted[index].id);
    show(true);
  });
  toggle.addEventListener("click",()=>{
    guided=!guided;
    ended=false;
    if (guided){
      // The original search controls are always editable in full-list mode.
      search.value="";
      search.dispatchEvent(new Event("input",{bubbles:true}));
      allFilter.click();
      index=Math.max(0,sorted.findIndex(p=>!p.querySelector("[data-cr-done]").checked));
    } else {
      // Restore the moved real LI before exposing the original grouped list.
      restore();
      search.dispatchEvent(new Event("input",{bubbles:true}));
    }
    show(true);
  });
  restart.addEventListener("click",()=>{
    guided=true;
    ended=false;
    index=Math.max(0,sorted.findIndex(p=>!p.querySelector("[data-cr-done]").checked));
    history.replaceState(null,"","#"+sorted[index].id);
    show(true);
  });
  root.addEventListener("change",event=>{
    if (event.target.matches?.("input[data-cr-done]") && guided) {
      note.textContent=actualDone()+" / 123 segnati qui. Non è il contatore del gioco.";
    }
  });
  window.addEventListener("hashchange",()=>{
    const idx=byId.get(location.hash.slice(1));
    if (idx===undefined) return;
    guided=true;
    ended=false;
    index=idx;
    show(true);
  });
  // Location buttons still open the real map on user gesture, below the guide.
  root.addEventListener("click",event=>{
    if (!event.target.closest?.("[data-vim-map-search]")) return;
    const map=document.querySelector("details.cr-map-extra");
    if (map) map.open=true;
  });
  show(false);
})();
