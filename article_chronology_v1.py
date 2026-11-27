"""Public editorial chronology, independent from the photo-gated X feed."""
from datetime import date
from html import escape
from pathlib import Path
import json,re
from vehicle_progression_guides_v1 import ARTICLES as VEHICLE_PROGRESSION
from garage_guides_v1 import STORY_ROWS,STORY
from strip_club_guide_v1 import PATH as STRIP_CLUB_PATH, PUBLISHED as STRIP_CLUB_PUBLISHED
GLITCH="guide-e-tutorial/glitch-prima-persona-ps5/"
EXTRA=[
 ("guide-e-tutorial/strip-club-gta-6/","GTA 6: dove sono i tre strip club e come raggiungerli","Missioni"),
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
    rows += [(p,t,c,dates.get(p) or (STRIP_CLUB_PUBLISHED if p==STRIP_CLUB_PATH else None)) for p,t,c in EXTRA]
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
# Every article belongs to exactly one parent and one child. Keep the legacy
# inventory labels above for source contracts, but expose this shared taxonomy.
PAGE_SIZE=25
BASE="https://xfederiko11.github.io/gta-6/"
INDEX="articoli/"
CATALOG="articoli/catalogo.json"
GROUPS={
 "guide":("Guide e missioni","pink",{"missioni":"Missioni e attività","spostamenti":"Spostamenti e vita quotidiana"}),
 "soldi":("Soldi ed economia","orange",{"bottini":"Denaro e bottini","vendita":"Vendita di veicoli"}),
 "veicoli":("Veicoli e garage","cyan",{"garage":"Garage e proprietà","registrazione":"Registrazione e chiavi","scanner":"WAiNK e scanner","richieste":"Richieste di Moses e Randy","posizioni":"Posizioni dei veicoli"}),
 "platino":("Trofei e completamento","violet",{"roadmap":"Roadmap e checklist","trofei":"Singoli trofei","collezionabili":"Collezionabili e mappe","sfide":"Sfide e medaglie","animali":"Animali e fauna","meditazione":"Meditazione"}),
 "trucchi":("Trucchi e codici","orange",{"codici":"Codici PS5"}),
 "glitch":("Glitch ed exploit","pink",{"ps5":"Glitch PS5"}),
 "news":("News e approfondimenti","pink",{"patch":"Patch e aggiornamenti","foto":"Approfondimenti e immagini"}),
 "hdr":("Tecnica e HDR","violet",{"lg":"LG OLED","samsung":"Samsung OLED","sony":"Sony OLED","philips":"Philips OLED","panasonic":"Panasonic OLED","altri":"Altri modelli OLED"}),
}

def taxonomy(row):
    p,_,c,_=row
    if c=="Glitch":return "glitch","ps5"
    if c=="Trucchi":return "trucchi","codici"
    if c=="News e patch":return "news","patch"
    if c=="Approfondimenti":return "news","foto"
    if c=="HDR OLED":
        brand=p.split("/")[1].split("-")[0]
        return "hdr",brand if brand in GROUPS["hdr"][2] else "altri"
    if p=="guide-e-tutorial/vendere-veicoli/":return "soldi","vendita"
    if p.startswith("guide-e-tutorial/soldi-"):return "soldi","bottini"
    if p.startswith("garage-gratuiti/") or p=="veicoli/pfister-vanessas-growler/":return "veicoli","garage"
    if p in ("salvare-auto/","guide-e-tutorial/key-cloner/"):return "veicoli","registrazione"
    if p=="guide-e-tutorial/scansionare-veicoli/":return "veicoli","scanner"
    if p in ("guide-e-tutorial/veicoli-per-moses/","guide-e-tutorial/sportive-randy-posizioni/"):return "veicoli","richieste"
    if p.startswith("veicoli/"):return "veicoli","posizioni"
    if p.startswith("trofei/trofeo-") and p!="trofei/trofei-difficili/":return "platino","trofei"
    if p=="guide-e-tutorial/studiare-animali/":return "platino","animali"
    if p=="guide-e-tutorial/meditazione-capitolo-1/":return "platino","meditazione"
    if p in ("guide-e-tutorial/70-sfide-100-percento/","guide-e-tutorial/poligoni-concentrazione/","trofei/medaglie-oro/"):return "platino","sfide"
    if p.startswith("collezionabili/"):return "platino","collezionabili"
    if p.startswith("trofei/"):return "platino","roadmap"
    if c=="Garage":return "veicoli","garage"
    if c=="Veicoli":return "veicoli","posizioni"
    if c=="Collezionabili":return "platino","collezionabili"
    if c=="Trofei":return "platino","sfide"
    if p=="guide-e-tutorial/viaggio-rapido-taxi/":return "guide","spostamenti"
    return "guide","missioni"

def category_path(group="",sub=""):
    if not group:return INDEX
    if group not in GROUPS or (sub and sub not in GROUPS[group][2]):raise ValueError("Unknown category")
    return INDEX+"categoria/"+group+"/"+(sub+"/" if sub else "")

def page_path(group="",sub="",page=1):
    if page<1:raise ValueError("Invalid archive page")
    return category_path(group,sub)+("pagina/"+str(page)+"/" if page>1 else "")

def scoped(rows,group="",sub=""):
    return [r for r in rows if (not group or taxonomy(r)[0]==group) and (not sub or taxonomy(r)[1]==sub)]

def tree(rows=None):
    rows=inventory() if rows is None else rows
    result=[]
    for g,(label,color,children) in GROUPS.items():
        group_rows=scoped(rows,g)
        if not group_rows:continue
        result.append({"id":g,"label":label,"color":color,"count":len(group_rows),
                       "path":category_path(g),"children":[{"id":s,"label":name,"count":len(found),"path":category_path(g,s)}
                         for s,name in children.items() if (found:=scoped(group_rows,g,s))]})
    return result

def total_pages(rows):
    return max(1,(len(rows)+PAGE_SIZE-1)//PAGE_SIZE)

def specs(rows=None):
    rows=inventory() if rows is None else rows
    scopes=[("","",rows)]
    for g in tree(rows):
        scopes.append((g["id"],"",scoped(rows,g["id"])))
        scopes.extend((g["id"],s["id"],scoped(rows,g["id"],s["id"])) for s in g["children"])
    for group,sub,selected in scopes:
        for page in range(1,total_pages(selected)+1):
            # Small, overlapping discovery lists remain useful to readers;
            # don't index collections of only one or two already indexed pages.
            # A child with the exact same article set as its parent remains
            # navigable, but does not compete for indexing with that parent.
            distinct=not sub or len(selected)<len(scoped(rows,group))
            yield group,sub,page,page_path(group,sub,page),len(selected)>=3 and distinct,selected

def label_for(group="",sub=""):
    if not group:return "Tutti gli articoli"
    return GROUPS[group][2][sub] if sub else GROUPS[group][0]

def record(row):
    p,t,c,d=row;g,s=taxonomy(row)
    secret=c=="Trofei" and t.startswith("Trofeo segreto n.")
    kind=("Fonte ufficiale" if c=="News e patch" else "Community · da verificare" if c=="Glitch"
          else "Non testato direttamente" if c=="Trucchi" else "Trofeo segreto" if secret else
          "Scheda tecnica" if c=="HDR OLED" else "Scheda veicolo" if p.startswith("veicoli/") else
          "Approfondimento" if c=="Approfondimenti" else "Guida")
    return {"path":p,"title":t,"category":c,"group":g,"sub":s,"group_label":GROUPS[g][0],
            "sub_label":GROUPS[g][2][s],"color":GROUPS[g][1],"published":d,"badge":kind,
            "summary":"Dettagli e requisiti nella guida. Possibili spoiler." if secret else "",
            "secret":secret,"image":"","credit":""}

def esc(v):return escape(str(v),quote=True)

def card(item,url):
    p=item["path"];title=item["title"];published=item["published"]
    stamp=('<time datetime="'+esc(published)+'">'+date.fromisoformat(published).strftime("%d/%m/%Y")+'</time>') if published else '<span>Data non documentata</span>'
    if item["image"]:
        media=('<img src="'+esc(url(item["image"]))+'" width="480" height="252" loading="lazy" decoding="async" alt="">'
               '<span class="archive-credit">'+esc(item["credit"])+'</span>')
    else:
        # No poster pretending to be a screenshot. The actual headline and
        # category are sufficient until a relevant cleared photo is available.
        media=""
    return ('<a class="ed-home-card chronology-card" data-chronology-path="'+esc(p)+'" data-chronology-category="'+esc(item["category"])+'" data-group="'+esc(item["group"])+'" data-sub="'+esc(item["sub"])+'" data-color="'+esc(item["color"])+'" href="'+esc(url(p))+'">'+
            ('<span class="archive-media">'+media+'</span>' if media else '')+'<span class="archive-copy"><span class="archive-meta"><span class="archive-category">'+esc(item["group_label"])+'</span><span>'+esc(item["sub_label"])+'</span>'+stamp+'</span>'
            '<strong class="archive-title">'+esc(title)+'</strong><span class="archive-summary">'+esc(item["summary"])+'</span>'
            '<span class="archive-bottom"><span class="archive-badge">'+esc(item["badge"])+'</span><span class="archive-cta">Leggi →</span></span></span></a>')

def entry(row,url):
    return card(record(row),url)

def category_nav(url,rows,group="",sub="",compact=False):
    groups=tree(rows)
    if compact:
        return '<details class="archive-bottom-categories"><summary>Esplora per categoria</summary><div class="archive-taxonomy">'+''.join(
            '<section><a href="'+url(g["path"])+'">'+esc(g["label"])+' <span>'+str(g["count"])+'</span></a><div>'+''.join(
                '<a href="'+url(s["path"])+'">'+esc(s["label"])+' <span>'+str(s["count"])+'</span></a>' for s in g["children"])+'</div></section>' for g in groups)+'</div></details>'
    main='<nav class="archive-group-nav" aria-label="Categorie articoli"><a href="'+url(INDEX)+'"'+(' aria-current="page"' if not group else '')+'>Tutti</a>'+''.join(
        '<a href="'+url(g["path"])+'" data-color="'+g["color"]+'"'+(' aria-current="page"' if g["id"]==group and not sub else '')+(' data-current-group="true"' if g["id"]==group else '')+'>'+esc(g["label"])+' <span>'+str(g["count"])+'</span></a>' for g in groups)+'</nav>'
    if group:
        children=next(g["children"] for g in groups if g["id"]==group)
        main+='<nav class="archive-sub-nav" aria-label="Sottocategorie"><a href="'+url(category_path(group))+'"'+(' aria-current="page"' if not sub else '')+'>Tutta la categoria</a>'+''.join(
            '<a href="'+url(s["path"])+'"'+(' aria-current="page"' if s["id"]==sub else '')+'>'+esc(s["label"])+' <span>'+str(s["count"])+'</span></a>' for s in children)+'</nav>'
    return main

def pager(url,rows,group="",sub="",page=1):
    n=total_pages(rows)
    def link(i,text,cls=""):
        return '<a href="'+url(page_path(group,sub,i))+'"'+(' aria-current="page"' if page==i else '')+(' class="'+cls+'"' if cls else '')+'>'+text+'</a>'
    return '<nav class="archive-pagination" data-archive-pager aria-label="Pagine articoli">'+(link(page-1,"← Indietro","archive-prev") if page>1 else '')+''.join(link(i,str(i)) for i in range(1,n+1))+(link(page+1,"Avanti →","archive-next") if page<n else '')+'</nav>'

def filters(rows,group,sub):
    groups=tree(rows)
    opts='<option value="">Tutte</option>'+''.join('<option value="'+g["id"]+'"'+(' selected' if g["id"]==group else '')+'>'+esc(g["label"])+'</option>' for g in groups)
    subs='<option value="">Tutte</option>'+''.join('<option value="'+s["id"]+'"'+(' selected' if s["id"]==sub else '')+'>'+esc(s["label"])+'</option>' for g in groups if g["id"]==group for s in g["children"])
    return ('<div class="ed-filters chronology-filters" data-chronology-filters hidden><label>Cerca in tutto il catalogo<input type="search" data-chronology-search placeholder="Titolo, veicolo, trofeo…"></label>'
            '<label>Categoria<select data-chronology-filter>'+opts+'</select></label><label>Sottocategoria<select data-chronology-subfilter>'+subs+'</select></label>'
            '<button type="button" data-chronology-reset>Ripristina</button></div>')

def render(url,archive=False,group="",sub="",page=1):
    rows=inventory();selected=scoped(rows,group,sub)
    start=(page-1)*PAGE_SIZE;shown=selected[start:start+PAGE_SIZE]
    heading=label_for(group,sub) if archive and group else "Ultimi articoli"
    out=('<section class="focus-content ed-home" id="ultimi-articoli" data-chronology-root data-archive-page="'+str(page)+'" data-archive-group="'+group+'" data-archive-sub="'+sub+'" data-catalog-url="'+url(CATALOG)+'" aria-labelledby="chronology-title">'
         '<div class="archive-heading"><div><span class="archive-kicker">GTA VI ITALIA / MAGAZINE</span><h2 id="chronology-title">'+esc(heading)+'</h2><p>Dal più recente al meno recente per data di pubblicazione.</p></div><span class="archive-total">'+str(len(selected))+' articoli</span></div>')
    if archive:out+=category_nav(url,rows,group,sub)+filters(rows,group,sub)
    out+='<p data-chronology-count role="status" aria-live="polite">Articoli '+str(start+1)+'–'+str(start+len(shown))+' di '+str(len(selected))+'</p>'
    out+='<div class="archive-grid" data-chronology-dated>'+''.join(entry(r,url) for r in shown)+'</div>'
    out+=pager(url,selected,group,sub,page)+category_nav(url,rows,group,sub,compact=True)
    return out+'</section>'

# Editorial intent, not keyword-volume claims. The archive is a discovery
# collection, not a replacement for the canonical answer or existing guide hub.
ARCHIVE_TOPICS={
 "":("Articoli GTA 6: guide, news e aggiornamenti","Scopri le guide italiane di GTA VI, le novità, i veicoli, i trofei e le configurazioni PS5. Sfoglia gli articoli per data o categoria."),
 "guide":("Guide GTA 6: missioni e attività","Trova guide per missioni, attività e spostamenti in GTA VI. Le procedure legittime sono separate da trucchi e glitch."),
 "soldi":("Soldi GTA 6: bottini e vendita veicoli","Consulta le guide per trovare denaro, recuperare bottini e vendere veicoli in GTA VI, con requisiti e avvisi sui limiti."),
 "veicoli":("Auto GTA 6: veicoli, garage e registrazione","Esplora le guide su come salvare e registrare le auto, trovare i veicoli, sbloccare i garage e usare WAiNK in GTA VI."),
 "platino":("Platino GTA 6: trofei e completamento","Sfoglia le guide ai trofei, alle checklist, alle sfide e ai collezionabili di GTA VI su PS5, con attenzione agli spoiler."),
 "trucchi":("Trucchi GTA 6: archivio codici PS5","Consulta le schede dei codici PS5 per GTA VI e le condizioni di utilizzo. I trucchi sono separati dalle strategie legittime."),
 "glitch":("Glitch GTA 6: archivio exploit PS5","Consulta i glitch documentati per PS5, separati dalle guide legittime. Controlla lo stato della verifica e delle patch."),
 "news":("News GTA 6: patch e approfondimenti","Scopri gli aggiornamenti di GTA VI, le patch e gli approfondimenti editoriali con fonti e date di pubblicazione."),
 "hdr":("HDR GTA 6: archivio TV OLED e PS5","Trova schede HDR per TV OLED, organizzate per marca e modello, con impostazioni PS5 e limiti di verifica."),
}
SUB_TOPICS={
 ("guide","missioni"):("Missioni GTA 6: guide e attività","Consulta le guide alle missioni e alle attività di GTA VI, con requisiti, passaggi e fonti."),
 ("guide","spostamenti"):("Spostamenti GTA 6: taxi e vita quotidiana","Trova le guide agli spostamenti e alle attività quotidiane in GTA VI, con indicazioni pratiche."),
 ("soldi","bottini"):("Soldi GTA 6: dove trovare denaro e bottini","Consulta le guide ai luoghi in cui trovare denaro e bottini, con prerequisiti e precauzioni."),
 ("soldi","vendita"):("GTA 6: archivio guide alla vendita di veicoli","Trova le guide che spiegano quando e come vendere veicoli in GTA VI e quali condizioni controllare."),
 ("veicoli","garage"):("Garage GTA 6: proprietà e sblocchi","Trova guide ai garage di GTA VI, ai requisiti di sblocco, alle proprietà e ai codici documentati."),
 ("veicoli","registrazione"):("GTA 6: guide per salvare auto e chiavi","Trova le procedure per salvare e registrare un'auto in GTA VI e sbloccare Key Cloner. Apri la guida specifica per tutti i passaggi."),
 ("veicoli","scanner"):("WAiNK GTA 6: guide allo scanner veicoli","Consulta le guide per scansionare i veicoli con WAiNK e riconoscere i tracker in GTA VI."),
 ("veicoli","richieste"):("GTA 6: richieste auto di Moses e Randy","Esplora le guide dedicate alle richieste di veicoli di Moses e Randy, con posizioni e prerequisiti documentati."),
 ("veicoli","posizioni"):("Veicoli GTA 6: posizioni e modelli","Sfoglia le schede dei veicoli con posizioni e condizioni documentate. Consulta la singola scheda per i dettagli."),
 ("platino","roadmap"):("GTA 6: roadmap platino e checklist 100%","Consulta i percorsi al platino e al completamento al 100%, con requisiti e avvertenze sugli spoiler."),
 ("platino","trofei"):("Trofei GTA 6: archivio delle singole guide","Trova le guide ai singoli trofei PS5. I titoli e le anteprime dei trofei segreti restano protetti dagli spoiler."),
 ("platino","collezionabili"):("Collezionabili GTA 6: percorsi e mappe","Sfoglia le guide ai collezionabili e i percorsi documentati, con riferimenti alle mappe."),
 ("platino","sfide"):("Sfide GTA 6: medaglie e completamento","Consulta le guide alle sfide, ai poligoni e alle medaglie rilevanti per il completamento."),
 ("platino","animali"):("Animali GTA 6: guide alla fauna","Consulta le guide allo studio della fauna di GTA VI e ai requisiti per il completamento."),
 ("platino","meditazione"):("Meditazioni GTA 6: archivio delle guide","Trova le guide alle meditazioni con luoghi, condizioni e checklist."),
 ("trucchi","codici"):("GTA 6: schede dei codici PS5","Sfoglia le schede dei codici per PS5, con fonti e avvisi sulle limitazioni."),
 ("glitch","ps5"):("GTA 6: guide ai glitch PS5","Consulta le anomalie documentate, lo stato della verifica e le avvertenze per i trofei."),
 ("news","patch"):("Patch GTA 6: archivio aggiornamenti","Trova le schede delle patch e delle correzioni di GTA VI con riferimenti alle comunicazioni ufficiali."),
 ("news","foto"):("GTA 6: approfondimenti e immagini ufficiali","Sfoglia gli approfondimenti editoriali su ambientazioni e veicoli, con immagini attribuite."),
}
def archive_metadata(group="",sub="",page=1):
    if sub and group=="hdr":
        label=label_for(group,sub)
        title="HDR GTA 6: "+label+" e PS5"
        desc="Consulta le schede HDR di "+label+" per GTA VI e PS5, con modelli, impostazioni e limiti di verifica."
    elif sub:
        title,desc=SUB_TOPICS[(group,sub)]
    else:
        title,desc=ARCHIVE_TOPICS[group]
    if page>1:
        title+=" – pagina "+str(page)
        desc+=" Pagina "+str(page)+"."
    return title,desc

ARCHIVE_ROUTES={
 "veicoli":(("salvare-auto/","Come salvare e registrare un’auto"),("garage-gratuiti/","Sbloccare i garage gratuiti"),("guide-e-tutorial/scansionare-veicoli/","Scansionare i veicoli con WAiNK")),
 "soldi":(("soldi-facili/","Guide ai soldi facili"),("guide-e-tutorial/soldi-facili-capitolo-1/","Bottini nel Capitolo 1"),("guide-e-tutorial/vendere-veicoli/","Vendere veicoli")),
 "platino":(("trofei/roadmap-platino/","Roadmap del platino"),("trofei/100-percento/","Checklist del 100%"),("collezionabili/percorsi/","Percorsi dei collezionabili")),
 "guide":(("guide-e-tutorial/","Tutte le guide operative"),("video-tutorial/","Video tutorial"),("mappe-guide/","Mappe delle guide")),
 "hdr":(("hdr-oled/","Cerca il tuo modello OLED"),),
 "news":(("patch/","Tutte le patch"),("immagini-ufficiali/","Galleria ufficiale")),
 "trucchi":(("trucchi/","Catalogo codici PS5"),),
 "glitch":(("glitch/","Glitch e stato delle patch"),),
}
def archive_routes(url,group,sub,page):
    if not group or page!=1:return ""
    routes=ARCHIVE_ROUTES[group]
    # Keep the curated links outside the 25 chronological article cards.
    return '<nav class="archive-sub-nav archive-topic-links" aria-label="Percorsi consigliati"><strong>Vai direttamente a:</strong>'+''.join('<a href="'+url(path)+'">'+esc(label)+' →</a>' for path,label in routes)+'</nav>'

def archive_pages(write,layout,url,crumbs):
    paths=[]
    for g,s,n,p,indexable,rows in specs():
        label=label_for(g,s)
        heading="Articoli GTA VI" if not g else label+" · GTA VI"
        if n>1:heading+=" — pagina "+str(n)
        seo_title,desc=archive_metadata(g,s,n)
        crumbs_parts=[("Articoli",INDEX)]
        if g:crumbs_parts.append((GROUPS[g][0],category_path(g)))
        if s:crumbs_parts.append((label,category_path(g,s)))
        if n>1:crumbs_parts.append(("Pagina "+str(n),p))
        body=crumbs(crumbs_parts)+'<section class="ed-intro archive-intro"><h1>'+esc(heading)+'</h1><p>'+esc(desc)+'</p></section>'+archive_routes(url,g,s,n)+render(url,True,g,s,n)
        schema={"@context":"https://schema.org","@type":"CollectionPage","name":heading,"url":url(p),"inLanguage":"it-IT",
                "mainEntity":{"@type":"ItemList","numberOfItems":len(rows[(n-1)*PAGE_SIZE:n*PAGE_SIZE]),"itemListElement":[{"@type":"ListItem","position":(n-1)*PAGE_SIZE+i,"url":url(row[0])} for i,row in enumerate(rows[(n-1)*PAGE_SIZE:n*PAGE_SIZE],1)]}}
        write(p+"index.html",layout(seo_title,desc,p,body,"articles",robots="index,follow" if indexable else "noindex,follow",structured=schema))
        if indexable:paths.append(p)
    return paths

def glitch_page(url):
    return '<section class="ed-intro"><h1>Glitch GTA 6 su PS5</h1><p>Solo exploit e anomalie, separati dalle strategie previste dal gioco. Controlla la patch indicata da ogni guida: nessuna garanzia per i trofei.</p></section><section class="ed-home" data-glitch-index><div class="archive-grid">'+''.join(entry(r,url) for r in inventory() if r[2]=="Glitch")+'</div></section>'

def decorate(root=Path("_site")):
    """Use only metadata and existing cover files from the built public pages.
    Listings prioritize real cleared gameplay. Do not use illustrated
    placeholder cards or extend legacy promotional media to new placements.
    Hidden trophies never expose covers
    or requirements. The X feed remains byte-identical."""
    from html.parser import HTMLParser
    class Meta(HTMLParser):
        def __init__(self):
            super().__init__();self.values={};self.canon=[]
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if tag=="meta":
                key=a.get("name") or a.get("property")
                if key:self.values[key]=a.get("content","")
            if tag=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href"))
    feed=root/"articoli/feed.json";before=feed.read_bytes()
    records={}
    for row in inventory():
        item=record(row);p=item["path"];parser=Meta()
        parser.feed((root/p/"index.html").read_text(encoding="utf-8"))
        assert parser.canon==[BASE+p],p
        if not item["secret"]:
            desc=" ".join(parser.values.get("description","").split())
            if len(desc)>190:desc=desc[:187].rsplit(" ",1)[0]+"…"
            item["summary"]=desc or "Consulta requisiti, indicazioni e fonti nella scheda."
            kind=parser.values.get("gta6:cover-kind")
            image=parser.values.get("og:image","")
            if kind=="approved_gameplay":
                assert image.startswith(BASE+"assets/social-cards/"),p
                rel=image.removeprefix(BASE)
                assert re.fullmatch(r"assets/social-cards/[0-9a-f]{16}\.jpg",rel),rel
                assert (root/rel).is_file(),rel
                item["image"]=rel
                item["credit"]="Screenshot autorizzato · crediti nella guida"
        records[p]=item
    pattern=re.compile(r'<a class="ed-home-card chronology-card" data-chronology-path="([^"]+)"[^>]*>.*?</a>',re.S)
    for f in [root/"index.html",root/"glitch/index.html",*(root/p/"index.html" for _,_,_,p,_,_ in specs())]:
        html=f.read_text(encoding="utf-8")
        changed=pattern.sub(lambda m:card(records[m.group(1)],lambda p:BASE+p),html)
        assert pattern.search(changed),str(f)
        f.write_text(changed,encoding="utf-8")
    (root/CATALOG).write_text(json.dumps({"schema":"gta6-public-archive-v2","page_size":PAGE_SIZE,"groups":tree(),"items":list(records.values())},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    assert before==feed.read_bytes()
    print("MAGAZINE_ARCHIVE_BUILT",len(records),"articles",len(list(specs())),"collection pages",sum(bool(x["image"]) for x in records.values()),"approved gameplay covers in listings")

if __name__=="__main__":
    decorate()
