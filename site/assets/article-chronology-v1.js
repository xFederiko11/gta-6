/* Local-only archive filter. No network, no storage; full list without JS. */
(()=>{'use strict';
const root=document.querySelector('[data-chronology-root]');
const controls=root?.querySelector('[data-chronology-filters]');
if(!controls)return;
const search=controls.querySelector('[data-chronology-search]');
const category=controls.querySelector('[data-chronology-filter]');
const count=root.querySelector('[data-chronology-count]');
const cards=[...root.querySelectorAll('[data-chronology-path]')];
const norm=v=>v.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('it-IT');
function update(){
 const terms=norm(search.value).trim().split(/\s+/).filter(Boolean);
 let n=0;
 for(const card of cards){
  const matches=(!category.value||card.dataset.chronologyCategory===category.value)&&terms.every(t=>norm(card.textContent).includes(t));
  card.hidden=!matches;if(matches)n++;
 }
 count.textContent=n+' articoli trovati';
}
controls.hidden=false;
search.addEventListener('input',update);category.addEventListener('change',update);update();
})();
