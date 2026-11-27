"""Public editorial chronology, independent from the photo-gated X feed."""
from datetime import date
from html import escape
from pathlib import Path
import json,re
from vehicle_progression_guides_v1 import ARTICLES as VEHICLE_PROGRESSION
from garage_guides_v1 import STORY_ROWS,STORY
GLITCH="guide-e-tutorial/glitch-prima-persona-ps5/"
EXTRA=[
 ("garage-gratuiti/","Garage gratuiti GTA 6: tutti gli sblocchi","Garage"),
 ("garage-gratuiti/southside-storage/","Southside Storage: 5 murales e codice 1010","Garage"),
 ("garage-gratuiti/domestic-timbers/","Domestic Timbers: garage e Raul’s Tempesta","Garage"),
 ("garage-gratuiti/garage-storia/","Garage gratuiti della storia","Garage"),
]
EXTRA += [
 ("guide-e-tutorial/veicoli-per-moses/","Le sei auto per Moses: posizioni e ricompense","Missioni"),
 ("trofei/roadmap-platino/","Roadmap Platino GTA 6","Trofei"),
 ("trofei/100-percento/","Checklist completamento al 100%","Collezionabili"),
 ("trofei/trofei-difficili/","Trofei difficili: requisiti e strategie","Trofei"),
 ("trofei/medaglie-oro/","Trofei Oro e medaglie Oro","Trofei"),
 ("collezionabili/percorsi/","Percorsi collezionabili per regione","Collezionabili"),
]
EXTRA += [(STORY+ident+"/",name+" Garage: come sbloccarlo","Garage") for ident,name,*_ in STORY_ROWS]
CATEGORIES=("News e patch","Guide legittime","Missioni","Veicoli","Garage","Trofei","Collezionabili","Trucchi","Glitch","HDR OLED","Approfondimenti")
GUIDE_CATEGORIES={"Soldi":"Guide legittime","Collezionabili":"Collezionabili","Platino":"Trofei","Trofei":"Trofei","Movimento":"Guide legittime","Garage":"Garage","Auto speciali":"Missioni","Glitch":"Glitch"}
def read(path):return json.loads(Path(path).read_text(encoding="utf-8"))
def ordered(rows):
    seen=set()
    for path,title,category,published in rows:
        if path in seen or not re.fullmatch(r"(?:[a-z0-9-]+/)+",path):raise ValueError("Invalid/duplicate article "+path)
        seen.add(path)
        if category not in CATEGORIES:raise ValueError("Unknown editorial category: "+category)
        if published:date.fromisoformat(published)
    return sorted(rows,key=lambda r:(not r[3],-date.fromisoformat(r[3]).toordinal() if r[3] else 0,r[0]))
def inventory():
    dates=read("data/publication_dates_v1.json")["published"]
    rows=[(a["path"],a["title"],"Approfondimenti",a["published"]) for a in read("data/articles.json")["articles"]]
    rows += [("patch/"+p["date"]+"/","GTA VI: patch del "+p["date"],"News e patch",p["published"]) for p in read("data/patches_v1.json")["records"]]
    for filename in ("data/guide.json","data/visual_guides.json"):
        for g in read(filename)["guides"]:
            path=g.get("canonical_path") or "guide-e-tutorial/"+g["id"]+"/"
            rows.append((path,g["title"],GUIDE_CATEGORIES.get(g["tag"],"Guide legittime"),dates.get(path)))
    rows += [(p,t,c,dates.get(p)) for p,t,c in EXTRA]
    rows += [(p,t,"Guide legittime",dates.get(p)) for p,t,_ in VEHICLE_PROGRESSION]
    for car in read("data/vehicle_catalog_v1.json")["items"]:
        if car["status"]!="Verificata":continue # noindex research cards do not belong in the reviewed archive
        p="veicoli/"+car["slug"]+"/"
        rows.append((p,car["name"]+": dove trovarla","Garage" if car["slug"]=="pfister-vanessas-growler" else "Veicoli",dates.get(p)))
    for t in read("data/trofei.json")["trophies"]:
        p="trofei/"+t["slug"]+"/"
        title=("Trofeo segreto n. "+str(t["number"])) if t["hidden"] else "Trofeo "+t["name_it"]
        rows.append((p,title,"Trofei",dates.get(p)))
    for t in read("data/trucchi.json")["cheats"]:
        p="trucchi/"+t["slug"]+"/"
        rows.append((p,t["title"]+": codice PS5","Trucchi",dates.get(p)))
    for tv in read("data/hdr_oled.json")["families"]:
        p="hdr-oled/"+tv["slug"]+"/"
        rows.append((p,"HDR PS5: "+tv["brand"]+" "+tv["series"],"HDR OLED",dates.get(p)))
    if not set(dates)<= {r[0] for r in rows}:raise ValueError("Unknown publication path")
    return ordered(rows)
def entry(row,url):
    path,title,category,published=row
    stamp=(' · <time datetime="'+published+'">'+date.fromisoformat(published).strftime("%d/%m/%Y")+'</time>') if published else ''
    return '<a class="ed-home-card chronology-card" data-chronology-path="'+escape(path,quote=True)+'" data-chronology-category="'+escape(category,quote=True)+'" href="'+url(path)+'"><span><small>'+escape(category)+stamp+'</small><strong>'+escape(title)+'</strong></span></a>'
def render(url,archive=False):
    rows=inventory();dated=[r for r in rows if r[3]];undated=[r for r in rows if not r[3]]
    out='<section class="focus-content ed-home" id="ultimi-articoli" data-chronology-root aria-labelledby="chronology-title"><h2 id="chronology-title">Ultimi articoli</h2><p>Dal più recente al meno recente per data di pubblicazione, non di aggiornamento.</p><div data-chronology-dated>'+''.join(entry(r,url) for r in (dated if archive else dated[:12]))+'</div>'
    if archive:
        filters=('<div class="ed-filters chronology-filters" data-chronology-filters hidden><label>Cerca un articolo<input type="search" data-chronology-search placeholder="Es. Cheetah, trofeo, HDR"></label><label>Categoria<select data-chronology-filter><option value="">Tutte</option>'+''.join('<option>'+escape(c)+'</option>' for c in CATEGORIES)+'</select></label><button type="button" data-chronology-reset>Mostra tutti</button></div><p data-chronology-count role="status" aria-live="polite"></p>')
        out=out.replace('<div data-chronology-dated>',filters+'<div data-chronology-dated>',1)
        if undated:
            out+='<section data-chronology-undated-section><h2 data-chronology-undated-title>Archivio senza data certa</h2><p>Prima pubblicazione non documentata: nessuna data inventata.</p><div data-chronology-undated>'+''.join(entry(r,url) for r in undated)+'</div></section>'
    else:
        out+='<p><a href="'+url("articoli/")+'">Tutti gli articoli: ricerca e categorie →</a> · <a href="'+url("glitch/")+'">Solo glitch</a></p>'
    return out+'</section>'
def glitch_page(url):
    return '<section class="ed-intro"><h1>Glitch GTA 6 su PS5</h1><p>Solo exploit e anomalie, separati dalle strategie previste dal gioco. Controlla la patch indicata da ogni guida: nessuna garanzia per i trofei.</p></section><section class="ed-home" data-glitch-index>'+''.join(entry(r,url) for r in inventory() if r[2]=="Glitch")+'</section>'
