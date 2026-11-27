/* MAGAZINE_TAG_ARCHIVES_V1: local filtering and sorting; no telemetry or network calls. */
(()=>{'use strict';
const root=document.querySelector('[data-tag-archive]');
if(!root)return;
const grid=root.querySelector('[data-tag-grid]'),category=document.querySelector('[data-tag-category]'),sort=document.querySelector('[data-tag-sort]'),status=document.querySelector('[data-tag-count]');
if(!grid||!category||!sort||!status)return;
const cards=[...grid.querySelectorAll('[data-tag-archive-card]')];
const parseDate=el=>{const s=el.dataset.published||'';const n=Date.parse(s);return Number.isFinite(n)?n:0};
const story=el=>{const n=Number.parseInt(el.dataset.storyOrder||'',10);return Number.isInteger(n)?n:999};
function update(){
 const visible=cards.filter(el=>!category.value||el.dataset.group===category.value);
 const mode=sort.value;
 visible.sort((a,b)=>{
  if(mode==='title')return (a.querySelector('.archive-title')?.textContent||'').localeCompare(b.querySelector('.archive-title')?.textContent||'','it');
  if(mode==='story'&&story(a)!==story(b))return story(a)-story(b);
  return parseDate(b)-parseDate(a);
 });
 for(const el of cards)el.hidden=!visible.includes(el);
 for(const el of visible)grid.append(el);
 status.textContent=visible.length+' '+(visible.length===1?'articolo':'articoli')+' mostrati';
}
category.addEventListener('change',update);
sort.addEventListener('change',update);
update();
})();