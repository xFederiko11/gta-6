/* Progressively enhance the crawlable, 25-item magazine archive.
   No private data, external requests, cookies, or invented dates. */
(()=>{'use strict';
const root=document.querySelector('[data-chronology-root]');
const controls=root?.querySelector('[data-chronology-filters]');
if(!controls)return;
const search=controls.querySelector('[data-chronology-search]'),group=controls.querySelector('[data-chronology-filter]'),sub=controls.querySelector('[data-chronology-subfilter]'),reset=controls.querySelector('[data-chronology-reset]');
const count=root.querySelector('[data-chronology-count]'),grid=root.querySelector('[data-chronology-dated]'),pager=root.querySelector('[data-archive-pager]');
const staticCards=[...grid.children].map(el=>el.cloneNode(true)),staticPager=pager.cloneNode(true),staticCount=count.textContent;
const initial={group:root.dataset.archiveGroup||'',sub:root.dataset.archiveSub||'',page:Number(root.dataset.archivePage)||1};
const endpoint=new URL(root.dataset.catalogUrl,document.baseURI),base=new URL('../',endpoint);
if(endpoint.origin!==location.origin)return;
const norm=v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('it-IT')
 .replace(/\b(?:gta\s*(?:vi|6)|grand\s+theft\s+auto\s+vi|grand\s+theft\s+auto\s+6)\b/g,'gta 6')
 .replace(/[^\p{L}\p{N}]+/gu,' ').trim();
function node(tag,cls='',text=''){const el=document.createElement(tag);if(cls)el.className=cls;if(text)el.textContent=text;return el}
function linkPath(path){if(!/^(?:[a-z0-9-]+\/)+$/.test(path))throw new Error('Invalid article path');return new URL(path,base).href}
let catalog,items,groups,pageSize=25,page=initial.page;
function card(item){
 const a=node('a','ed-home-card chronology-card');
 a.href=linkPath(item.path);a.dataset.chronologyPath=item.path;a.dataset.chronologyCategory=item.category;
 a.dataset.group=item.group;a.dataset.sub=item.sub;a.dataset.color=item.color;
 const media=node('span','archive-media');
 if(item.image&&/^assets\/(?:archive-thumbs\/[a-f0-9]{16}\.webp|social-cards\/[a-f0-9]{16}\.jpg)$/.test(item.image)){
  const img=node('img');img.src=new URL(item.image,base).href;img.width=480;img.height=252;img.loading='lazy';img.decoding='async';img.alt='';
  media.append(img,node('span','archive-credit',item.credit));
 }
 const copy=node('span','archive-copy'),meta=node('span','archive-meta');
 meta.append(node('span','archive-category',item.group_label),node('span','',item.sub_label));
 if(item.published&&/^\d{4}-\d{2}-\d{2}$/.test(item.published)){
  const date=node('time','',item.published.split('-').reverse().join('/'));date.dateTime=item.published;meta.append(date);
 }else meta.append(node('span','','Data non documentata'));
 const bottom=node('span','archive-bottom');
 bottom.append(node('span','archive-badge',item.badge),node('span','archive-cta','Leggi →'));
 copy.append(meta,node('strong','archive-title',item.title),node('span','archive-summary',item.summary),bottom);
 if(media.childElementCount)a.append(media);
 a.append(copy);return a;
}
function options(selected=''){
 const children=groups.find(g=>g.id===group.value)?.children||[];
 sub.replaceChildren(new Option('Tutte',''),...children.map(c=>new Option(c.label+' ('+c.count+')',c.id)));
 sub.value=children.some(c=>c.id===selected)?selected:'';
 sub.disabled=!group.value||!children.length;
}
function pathFor(n){return 'articoli/'+(group.value?'categoria/'+group.value+'/'+(sub.value?sub.value+'/':''):'')+(n>1?'pagina/'+n+'/':'')}
function restore(){
 grid.replaceChildren(...staticCards.map(el=>el.cloneNode(true)));
 pager.replaceChildren(...[...staticPager.children].map(el=>el.cloneNode(true)));
 pager.hidden=staticPager.hidden;count.textContent=staticCount;
}
function update(keepPage=false){
 if(!keepPage)page=1;
 const terms=norm(search.value).split(/\s+/).filter(Boolean);
 if(!terms.length&&group.value===initial.group&&sub.value===initial.sub&&page===initial.page){restore();return}
 const results=items.filter(x=>(!group.value||x.item.group===group.value)&&(!sub.value||x.item.sub===sub.value)&&terms.every(t=>x.text.includes(t)));
 const pages=Math.max(1,Math.ceil(results.length/pageSize));page=Math.min(page,pages);
 const first=(page-1)*pageSize,visible=results.slice(first,first+pageSize);
 grid.replaceChildren(...visible.map(x=>card(x.item)));
 count.textContent=results.length?'Articoli '+(first+1)+'–'+(first+visible.length)+' di '+results.length:'Nessun articolo trovato: prova un’altra parola o ripristina.';
 pager.replaceChildren();pager.hidden=!results.length;
 function button(n,label,cls=''){
  if(!terms.length){const a=node('a',cls,label);a.href=linkPath(pathFor(n));if(n===page)a.setAttribute('aria-current','page');return a}
  const b=node('button',cls,label);b.type='button';
  if(n===page)b.setAttribute('aria-current','page');
  b.addEventListener('click',()=>{page=n;update(true);count.scrollIntoView({block:'start'});count.setAttribute('tabindex','-1');count.focus({preventScroll:true});});
  return b;
 }
 if(page>1)pager.append(button(page-1,'← Indietro','archive-prev'));
 for(let n=1;n<=pages;n++)pager.append(button(n,String(n)));
 if(page<pages)pager.append(button(page+1,'Avanti →','archive-next'));
}
fetch(endpoint,{credentials:'same-origin',cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error('Catalog unavailable');return r.json()}).then(data=>{
 if(data.schema!=='gta6-public-archive-v2'||data.page_size!==25||!Array.isArray(data.items)||!Array.isArray(data.groups))throw new Error('Invalid catalog');
 catalog=data;groups=catalog.groups;pageSize=catalog.page_size;
 items=catalog.items.map(item=>({item,text:norm([item.title,item.summary,item.group_label,item.sub_label,item.badge,(item.tags||[]).flatMap(tag=>[tag.label,...(tag.aliases||[])]).join(' ')].join(' '))}));
 group.value=initial.group;options(initial.sub);
 controls.hidden=false;
 const query=new URLSearchParams(location.search).get('q');
 if(query&&query.trim()){
  search.value=query.trim().slice(0,100);
  update();
 }
 search.addEventListener('input',()=>update());group.addEventListener('change',()=>{options();update()});sub.addEventListener('change',()=>update());
 reset.addEventListener('click',()=>{search.value='';group.value=initial.group;options(initial.sub);page=initial.page;restore();const url=new URL(location.href);if(url.searchParams.has('q')){url.searchParams.delete('q');history.replaceState(null,'',url.href)}search.focus()});
}).catch(()=>{ /* Static category links and numbered pages still work. */ });
})();