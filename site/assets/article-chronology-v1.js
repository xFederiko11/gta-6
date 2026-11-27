/* Local-only archive filter. No network, no storage; full list without JS. */
(()=>{'use strict';
const root=document.querySelector('[data-chronology-root]');
const controls=root?.querySelector('[data-chronology-filters]');
if(!controls)return;
const search=controls.querySelector('[data-chronology-search]');
const category=controls.querySelector('[data-chronology-filter]');
const reset=controls.querySelector('[data-chronology-reset]');
const count=root.querySelector('[data-chronology-count]');
const undated=root.querySelector('[data-chronology-undated-section]');
const cards=[...root.querySelectorAll('[data-chronology-path]')];
const norm=v=>v.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('it-IT')
 .replace(/\b(?:gta\s*vi|grand\s+theft\s+auto\s+vi|grand\s+theft\s+auto\s+6)\b/g,'gta 6')
 .replace(/[^\p{L}\p{N}]+/gu,' ').trim();
const index=cards.map(card=>({card,text:norm(card.textContent)}));
function update(){
 const terms=norm(search.value).split(/\s+/).filter(Boolean);
 let n=0;
 for(const {card,text} of index){
  const matches=(!category.value||card.dataset.chronologyCategory===category.value)&&terms.every(t=>text.includes(t));
  card.hidden=!matches;if(matches)n++;
 }
 if(undated)undated.hidden=!undated.querySelector('[data-chronology-path]:not([hidden])');
 count.textContent=n===0?'Nessun articolo trovato: prova un’altra parola o Mostra tutti.':n+(n===1?' articolo trovato':' articoli trovati');
}
controls.hidden=false;
search.addEventListener('input',update);category.addEventListener('change',update);
reset.addEventListener('click',()=>{search.value='';category.value='';update();search.focus();});
update();
})();
