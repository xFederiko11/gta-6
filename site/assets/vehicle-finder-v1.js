/* Private checklist and on-demand video: no network until the video is opened. */
(()=>{'use strict';
  for(const button of document.querySelectorAll('[data-vc-load-video]')){
    button.addEventListener('click',()=>{
      const seconds=Number(button.dataset.vcStartSeconds);
      if(!Number.isInteger(seconds)||seconds<10||seconds>900)return;
      const slot=button.parentElement.querySelector('[data-vc-video-slot]');
      if(!slot||slot.querySelector('iframe'))return;
      const frame=document.createElement('iframe');
      frame.src='https://www.youtube-nocookie.com/embed/UyxxY0A_kow?start='+seconds+'&rel=0';
      frame.title='Gameplay originale IGN GTA VI, dal momento del veicolo selezionato';
      frame.loading='lazy';
      frame.referrerPolicy='strict-origin-when-cross-origin';
      frame.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';
      frame.setAttribute('allowfullscreen','');
      slot.appendChild(frame);
      button.hidden=true;
    });
  }
  const root=document.querySelector('[data-vc-finder]');
  if(!root)return;
  const cards=[...root.querySelectorAll('[data-vc-card]')];
  const search=root.querySelector('[data-vc-search]');
  const owner=root.querySelector('[data-vc-filter-owner]');
  const status=root.querySelector('[data-vc-filter-status]');
  const todo=root.querySelector('[data-vc-todo]');
  const more=root.querySelector('[data-vc-more]');
  const count=root.querySelector('[data-vc-count]');
  const empty=root.querySelector('[data-vc-empty]');
  const KEY='botx-vehicle-finder-found-v1';
  const STEP=12;
  let shown=STEP,found={};
  try{const raw=JSON.parse(localStorage.getItem(KEY)||'{}');
      if(raw&&typeof raw==='object'&&!Array.isArray(raw))found=raw;}catch(_e){found={};}
  function write(){try{localStorage.setItem(KEY,JSON.stringify(found));}catch(_e){}}
  function view(){
    const term=search.value.trim().toLocaleLowerCase('it-IT');
    let matching=0,visible=0;
    for(const card of cards){
      const slug=card.dataset.vcSlug;
      const isFound=found[slug]===true;
      const button=card.querySelector('[data-vc-found]');
      button.setAttribute('aria-pressed',String(isFound));
      button.textContent=isFound?'✓ Trovata':'□ Da trovare';
      const ok=card.dataset.vcTerms.includes(term)&&
        (owner.value==='Tutti'||card.dataset.vcOwner===owner.value)&&
        (status.value==='Tutte'||card.dataset.vcStatus===status.value)&&
        (!todo.checked||!isFound);
      if(ok)matching++;
      const show=ok&&matching<=shown;
      card.hidden=!show;
      if(show)visible++;
    }
    count.textContent=visible+' di '+matching+' schede trovate';
    empty.hidden=matching!==0;
    more.hidden=matching<=shown;
  }
  for(const input of [search,owner,status,todo])
    input.addEventListener(input===search?'input':'change',()=>{
      shown=STEP;view();
    });
  more.addEventListener('click',()=>{shown+=STEP;view();});
  root.addEventListener('click',(event)=>{
    const button=event.target.closest('[data-vc-found]');
    if(!button||!root.contains(button))return;
    const slug=button.dataset.vcFound;
    found[slug]=found[slug]!==true;write();view();
  });
  view();
})();