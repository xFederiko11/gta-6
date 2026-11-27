/* MAGAZINE_TAG_ARCHIVES_V1: local filtering, sorting and pagination. All links remain usable without JS. */
(()=>{'use strict';
const root=document.querySelector('[data-tag-archive]');
if(!root)return;
const grid=root.querySelector('[data-tag-grid]'),category=document.querySelector('[data-tag-category]'),sort=document.querySelector('[data-tag-sort]'),status=document.querySelector('[data-tag-count]'),pager=root.querySelector('[data-tag-pager]');
if(!grid||!category||!sort||!status||!pager)return;
const cards=[...grid.querySelectorAll('[data-tag-archive-card]')],size=25;
let page=1;
const parseDate=el=>{const n=Date.parse(el.dataset.published||'');return Number.isFinite(n)?n:0};
const story=el=>{const n=Number.parseInt(el.dataset.storyOrder||'',10);return Number.isInteger(n)?n:999};
function update(){
 const visible=cards.filter(el=>!category.value||el.dataset.group===category.value);
 const mode=sort.value;
 visible.sort((a,b)=>{
  if(mode==='title')return (a.querySelector('.archive-title')?.textContent||'').localeCompare(b.querySelector('.archive-title')?.textContent||'','it');
  if(mode==='story'&&story(a)!==story(b))return story(a)-story(b);
  return parseDate(b)-parseDate(a);
 });
 const pages=Math.max(1,Math.ceil(visible.length/size));page=Math.min(page,pages);
 const first=(page-1)*size,shown=visible.slice(first,first+size),selected=new Set(shown);
 for(const el of cards)el.hidden=!selected.has(el);
 for(const el of shown)grid.append(el);
 status.textContent=visible.length?'Articoli '+(first+1)+'–'+(first+shown.length)+' di '+visible.length:'Nessun articolo trovato.';
 pager.replaceChildren();pager.hidden=pages<=1;
 function button(n,label){const b=document.createElement('button');b.type='button';b.textContent=label;if(n===page)b.setAttribute('aria-current','page');b.addEventListener('click',()=>{page=n;update();status.setAttribute('tabindex','-1');status.focus()});return b}
 if(page>1)pager.append(button(page-1,'← Indietro'));
 for(let n=1;n<=pages;n++)pager.append(button(n,String(n)));
 if(page<pages)pager.append(button(page+1,'Avanti →'));
}
category.addEventListener('change',()=>{page=1;update()});
sort.addEventListener('change',()=>{page=1;update()});
update();
})();