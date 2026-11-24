/* Progressive enhancement: all images are available without JS; show 24 at once with JS. */
(() => {
  'use strict';
  const root=document.querySelector('[data-rockstar-gallery]');
  if(!root)return;
  const all=Array.from(root.querySelectorAll('[data-rg-card]'));
  const search=root.querySelector('[data-rg-search]');
  const filter=root.querySelector('[data-rg-filter]');
  const counter=root.querySelector('[data-rg-counter]');
  const empty=root.querySelector('[data-rg-empty]');
  const more=root.querySelector('[data-rg-more]');
  const STEP=24;
  let shown=STEP;
  function update(){
    const term=search.value.trim().toLocaleLowerCase('it-IT');
    const group=filter.value;
    let matching=0,visible=0;
    for(const card of all){
      const ok=(group==='Tutte'||card.dataset.rgGroup===group)&&
        card.dataset.rgSearch.includes(term);
      if(ok)matching++;
      if(ok&&matching<=shown){card.hidden=false;visible++;}else card.hidden=true;
    }
    empty.hidden=matching!==0;
    more.hidden=matching<=shown;
    counter.textContent=matching+' immagini trovate · '+visible+' mostrate';
  }
  search.addEventListener('input',()=>{shown=STEP;update();});
  filter.addEventListener('change',()=>{shown=STEP;update();});
  more.addEventListener('click',()=>{shown+=STEP;update();});
  update();
})();