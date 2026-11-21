/* X-only community contribution preparation, with explicit, voluntary consent. No upload or network call. */
(() => {
  "use strict";
  const root=document.querySelector("[data-photo-intake]");
  if (!root) return;
  const form=root.querySelector("[data-intake-form]");
  const guide=form.querySelector("[data-pi-guide]");
  const role=form.querySelector("[data-pi-role]");
  const platform=form.querySelector("[data-pi-platform]");
  const patch=form.querySelector("[data-pi-patch]");
  const credit=form.querySelector("[data-pi-credit]");
  const owner=form.querySelector("[data-pi-owner]");
  const rights=form.querySelector("[data-pi-rights]");
  const publicPost=form.querySelector("[data-pi-public]");
  const button=form.querySelector("[data-pi-submit]");
  const message=form.querySelector("[data-pi-status]");
  const fallback=form.querySelector("[data-pi-fallback]");
  const roles=[...form.querySelectorAll("template[data-pi-role-options] option")];
  const validGuides=new Set([...guide.options].map(option=>option.value));
  function fillRoles() {
    const previous=role.value;
    role.replaceChildren();
    roles.filter(item=>item.dataset.photoGuide===guide.value).forEach(item=>{
      role.add(new Option(item.textContent,item.value));
    });
    if ([...role.options].some(x=>x.value===previous)) role.value=previous;
  }
  const clean=s=>s.trim().replace(/[\r\n\t<>]/g," ").replace(/\s{2,}/g," ");
  const text=()=>{
    const patchValue=clean(patch.value);
    const creditValue=clean(credit.value);
    const version=patchValue? " patch:"+patchValue:"";
    return "@xFederiko11 #GTA6Italia FOTO "+
      guide.value+" step:"+role.value+"/5 "+platform.value+version+
      " Credito:"+creditValue+
      ". Sono autore e autorizzo GTA VI Italia a ripubblicare questa mia foto sul sito e sui social con credito. Allego screenshot originale.";
  };
  function ready() {
    return validGuides.has(guide.value) &&
      [...role.options].some(x=>x.value===role.value) &&
      ["PS5","PS5 Pro"].includes(platform.value) &&
      Boolean(clean(credit.value)) && credit.value.length<=24 &&
      patch.value.length<=18 && owner.checked && rights.checked && publicPost.checked &&
      text().length<=280;
  }
  function update() {
    const yes=ready();
    button.disabled=!yes;
    fallback.hidden=true;
    message.textContent=!(owner.checked && rights.checked && publicPost.checked)
      ? "Conferma le tre dichiarazioni prima di preparare il post."
      : !clean(credit.value)
        ? "Inserisci un credito pubblico per attribuire la foto."
        : text().length>280
          ? "Il messaggio X supera 280 caratteri: abbrevia credito o versione."
          : "Bozza pronta. Foto da allegare e pubblicare manualmente su X.";
  }
  guide.addEventListener("change",()=>{fillRoles();update();});
  form.addEventListener("input",update);
  form.addEventListener("change",update);
  form.addEventListener("submit",event=>{
    event.preventDefault();
    if (!ready()) {update();return;}
    const link="https://x.com/intent/tweet?"+new URLSearchParams({text:text()}).toString();
    fallback.href=link;
    fallback.hidden=false;
    /* A real user gesture opens their X compose screen; no data is sent to our server. */
    const opened=window.open(link,"_blank","noopener,noreferrer");
    message.textContent=opened
      ? "Bozza aperta. Allega la foto e pubblica solo se desideri: nulla è stato inviato al sito."
      : "Se la bozza non si è aperta, premi il link qui sotto. Non abbiamo ricevuto la foto.";
  });
  fillRoles();
  update();
})();
