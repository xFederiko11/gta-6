/* MAGAZINE_QUICK_SEARCH_V1: local suggestions, no query telemetry or external API. */
(()=>{'use strict';
const panels=[...document.querySelectorAll('[data-magazine-search]')];
if(!panels.length)return;
const first=panels[0].querySelector('[data-search-form]');
const archive=new URL(first.action,document.baseURI);
if(archive.origin!==location.origin)return;
const base=new URL('../',archive),endpoint=new URL('catalogo.json',archive);
const norm=v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('it-IT').replace(/\b(?:gta\s*(?:vi|6)|grand\s+theft\s+auto\s+vi|grand\s+theft\s+auto\s+6)\b/g,'gta 6').replace(/[^\p{L}\p{N}]+/gu,' ').trim();
let pending;
function catalog(){
 if(!pending)pending=fetch(endpoint,{credentials:'same-origin',cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('catalog');return r.json()}).then(d=>{
  if(d.schema!=='gta6-public-archive-v2'||!Array.isArray(d.items))throw Error('schema');
  return d.items.filter(x=>x&&!x.secret&&typeof x.title==='string'&&/^(?:[a-z0-9-]+\/)+$/.test(x.path)).map(x=>({item:x,title:norm(x.title),text:norm([x.title,x.summary,x.group_label,x.sub_label,(x.tags||[]).flatMap(t=>[t.label,...(t.aliases||[])]).join(' ')].join(' '))}));
 }).catch(e=>{pending=null;throw e});
 return pending;
}
for(const panel of panels){
 const field=panel.querySelector('[data-search-input]'),box=panel.querySelector('[data-search-results]'),status=panel.querySelector('[data-search-status]');
 let sequence=0;
 function close(){sequence++;box.hidden=true;status.textContent='Cerca per titolo, veicolo, missione o trofeo.'}
 async function update(){
  const id=++sequence,query=norm(field.value),terms=query.split(/\s+/).filter(Boolean);
  box.replaceChildren();box.hidden=true;
  if(query.length<2){status.textContent='Cerca per titolo, veicolo, missione o trofeo.';return}
  status.textContent='Ricerca…';
  try{
   const items=await catalog();if(id!==sequence)return;
   const found=items.filter(x=>terms.every(t=>x.text.includes(t))).map(x=>({x,score:(x.title===query?1000:0)+(x.title.includes(query)?100:0)+terms.filter(t=>x.title.includes(t)).length*10})).sort((a,b)=>b.score-a.score);
   status.textContent=found.length?found.length+' articoli trovati · Invio per tutti i risultati':'Nessun articolo trovato.';
   for(const {x} of found.slice(0,6)){
    const a=document.createElement('a'),strong=document.createElement('strong'),small=document.createElement('small');
    a.href=new URL(x.item.path,base).href;strong.textContent=x.item.title;small.textContent=[(x.item.tags||[]).slice(0,2).map(t=>t.label).join(' · '),x.item.sub_label||x.item.group_label||'Articolo'].filter(Boolean).join(' · ');a.append(strong,small);box.append(a);
   }
   box.hidden=!box.childElementCount;
  }catch(_){if(id===sequence)status.textContent='Suggerimenti non disponibili. Apri l’archivio per continuare.'}
 }
 field.addEventListener('input',update);
 field.addEventListener('focus',()=>{if(norm(field.value).length>=2)update()});
 panel.addEventListener('keydown',e=>{
  if(e.key==='Escape'){e.preventDefault();field.focus();close()}
  else if(e.key==='ArrowDown'&&e.target===field&&!box.hidden&&box.firstElementChild){e.preventDefault();box.firstElementChild.focus()}
  else if((e.key==='ArrowDown'||e.key==='ArrowUp')&&box.contains(document.activeElement)){
   e.preventDefault();const links=[...box.children],i=links.indexOf(document.activeElement),n=i+(e.key==='ArrowDown'?1:-1);if(n<0)field.focus();else if(n<links.length)links[n].focus();
  }
 });
 panel.addEventListener('focusout',e=>{if(!panel.contains(e.relatedTarget))close()});
}
})();