/* Device-local discovery checklist; no account, analytics, API, or post actions. */
(()=>{'use strict';
 const root=document.querySelector('[data-vc-finder]');
 if(!root)return;
 const cards=[...root.querySelectorAll('[data-vc-card]')];
 const search=root.querySelector('[data-vc-search]');
 const owner=root.querySelector('[data-vc-filter-owner]');
 const status=root.querySelector('[data-vc-filter-status]');
 const todo=root.querySelector('[data-vc-todo]');
 const count=root.querySelector('[data-vc-count]');
 const empty=root.querySelector('[data-vc-empty]');
 const KEY='botx-vehicle-finder-found-v1';
 let found={};
 try{const raw=JSON.parse(localStorage.getItem(KEY)||'{}');if(raw&&typeof raw==='object'&&!Array.isArray(raw))found=raw;}catch(_e){found={};}
 function write(){try{localStorage.setItem(KEY,JSON.stringify(found));}catch(_e){}}
 function view(){
   const term=search.value.trim().toLocaleLowerCase('it-IT');
   let n=0;
   for(const card of cards){
     const slug=card.dataset.vcSlug;
     const isFound=found[slug]===true;
     const button=card.querySelector('[data-vc-found]');
     button.setAttribute('aria-pressed',String(isFound));
     button.textContent=isFound?'✓ Trovata':'□ Da trovare';
     const yes=card.dataset.vcTerms.includes(term)&&
       (owner.value==='Tutti'||card.dataset.vcOwner===owner.value)&&
       (status.value==='Tutte'||card.dataset.vcStatus===status.value)&&
       (!todo.checked||!isFound);
     card.hidden=!yes;
     if(yes)n++;
   }
   count.textContent=n+' di '+cards.length+' schede visibili';
   empty.hidden=n!==0;
 }
 for(const input of [search,owner,status,todo])
   input.addEventListener((input===search?'input':'change'),view);
 root.addEventListener('click',(event)=>{
   const button=event.target.closest('[data-vc-found]');
   if(!button||!root.contains(button))return;
   const slug=button.dataset.vcFound;
   found[slug]=found[slug]!==true;write();view();
 });
 view();
})();