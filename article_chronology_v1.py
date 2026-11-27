"""Public editorial chronology, independent from the photo-gated X feed."""
from datetime import date
from html import escape
from pathlib import Path
import json,re
GLITCH="guide-e-tutorial/glitch-prima-persona-ps5/"
EXTRA=[
 ("garage-gratuiti/","Garage gratuiti GTA 6: tutti gli sblocchi","Garage"),
 ("garage-gratuiti/southside-storage/","Southside Storage: 5 murales e codice 1010","Garage"),
 ("garage-gratuiti/domestic-timbers/","Domestic Timbers: garage e Raul’s Tempesta","Garage"),
 ("garage-gratuiti/garage-storia/","Garage gratuiti della storia","Garage"),
]
def read(path):return json.loads(Path(path).read_text(encoding="utf-8"))
def ordered(rows):
    seen=set()
    for path,title,category,published in rows:
        if path in seen or not re.fullmatch(r"(?:[a-z0-9-]+/)+",path):raise ValueError("Invalid/duplicate article "+path)
        seen.add(path)
        if published:date.fromisoformat(published)
    return sorted(rows,key=lambda r:(not r[3],-date.fromisoformat(r[3]).toordinal() if r[3] else 0,r[0]))
def inventory():
    dates=read("data/publication_dates_v1.json")["published"]
    rows=[(a["path"],a["title"],"Approfondimenti",a["published"]) for a in read("data/articles.json")["articles"]]
    rows += [("patch/"+p["date"]+"/","GTA VI: patch del "+p["date"],"Patch",p["published"]) for p in read("data/patches_v1.json")["records"]]
    for filename in ("data/guide.json","data/visual_guides.json"):
        for g in read(filename)["guides"]:
            path=g.get("canonical_path") or "guide-e-tutorial/"+g["id"]+"/"
            rows.append((path,g["title"],"Glitch" if path==GLITCH else "Guide",dates.get(path)))
    rows += [(p,t,c,dates.get(p)) for p,t,c in EXTRA]
    if not set(dates)<= {r[0] for r in rows}:raise ValueError("Unknown publication path")
    return ordered(rows)
def entry(row,url):
    path,title,category,published=row
    stamp=(' · <time datetime="'+published+'">'+date.fromisoformat(published).strftime("%d/%m/%Y")+'</time>') if published else ''
    return '<a class="ed-home-card chronology-card" data-chronology-path="'+escape(path,quote=True)+'" data-chronology-category="'+escape(category,quote=True)+'" href="'+url(path)+'"><span><small>'+escape(category)+stamp+'</small><strong>'+escape(title)+'</strong></span></a>'
def render(url,archive=False):
    rows=inventory();dated=[r for r in rows if r[3]];undated=[r for r in rows if not r[3]]
    out='<section class="focus-content ed-home" id="ultimi-articoli" aria-labelledby="chronology-title"><h2 id="chronology-title">Ultimi articoli</h2><p>Dal più recente al meno recente per data di pubblicazione, non di aggiornamento.</p><div data-chronology-dated>'+''.join(entry(r,url) for r in (dated if archive else dated[:12]))+'</div>'
    if archive:
        out+='<h2>Archivio guide</h2><p>Prima pubblicazione non documentata: nessuna data inventata.</p><div data-chronology-undated>'+''.join(entry(r,url) for r in undated)+'</div>'
    else:
        out+='<p><a href="'+url("articoli/")+'">Tutti gli articoli e le guide →</a> · <a href="'+url("glitch/")+'">Solo glitch</a></p>'
    return out+'</section>'
def glitch_page(url):
    return '<section class="ed-intro"><h1>Glitch GTA 6 su PS5</h1><p>Solo exploit e anomalie, separati dalle strategie previste dal gioco. Controlla la patch indicata da ogni guida: nessuna garanzia per i trofei.</p></section><section class="ed-home" data-glitch-index>'+''.join(entry(r,url) for r in inventory() if r[2]=="Glitch")+'</section>'
