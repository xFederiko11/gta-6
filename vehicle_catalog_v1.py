"""GTA VI vehicles: source-checked location finder and individual articles.

Only externally documented zones, never invented pin coordinates, spawn
guarantees, car images, player earnings or duplicate SEO articles. A missing
position produces a clearly labeled noindex research card.
"""
from __future__ import annotations
from html import escape
from pathlib import Path
from urllib.parse import quote, urlsplit
import json
import re

PATH="veicoli/"
CATALOG=Path("data/vehicle_catalog_v1.json")
VERIFIED="Verificata"
STATUSES={VERIFIED,"In verifica","Community"}
KINDS={"Moses","Randy"}
FIELDS={"name","slug","kind","category","area","where","visual","unlock","steps","check",
        "status","source_url","additional_source","spoiler","note"}
SOURCE_DOMAINS={"www.powerpyx.com","www.gtabase.com","gta6gps.com"}

def e(v):return escape(str(v),quote=True)
def href_safe(value):
    raw=str(value or "")
    p=urlsplit(raw)
    if (p.scheme!="https" or p.username or p.password or p.port not in (None,443)
            or p.hostname not in SOURCE_DOMAINS or p.fragment or not p.path.startswith("/")):
        raise ValueError("Source outside reviewed domains: "+raw)
    return raw

def load(path=CATALOG):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate(doc):
    if doc.get("schema")!="botx-vehicle-catalog-v1" or not isinstance(doc.get("items"),list):
        raise ValueError("Invalid vehicle catalog")
    if len(doc["items"])<20:
        raise ValueError("Missing source-confirmed model inventory")
    seen=set()
    for car in doc["items"]:
        if not FIELDS.issubset(car):
            raise ValueError("Missing fields in vehicle article")
        slug=car["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",slug) or slug in seen:
            raise ValueError("Unsafe or duplicated vehicle slug")
        seen.add(slug)
        if (car["status"] not in STATUSES or car["kind"] not in KINDS
                or not 5<=len(car["name"])<=65 or not 3<=len(car["where"])<=195):
            raise ValueError("Unreviewed vehicle classification")
        steps=car["steps"]
        if (not isinstance(steps,list) or not 3<=len(steps)<=6 or any(
                not isinstance(v,str) or not 19<=len(v)<=220 for v in steps)):
            raise ValueError("Every article needs individual, actionable steps")
        if not 12<=len(car["check"])<=250 or not 15<=len(car["note"])<=330:
            raise ValueError("Unclear player confirmation")
        href_safe(car["source_url"])
        href_safe(car["additional_source"])
        if car.get("video_url"):
            v=urlsplit(car["video_url"])
            if (v.scheme!="https" or v.hostname!="www.youtube.com"
                    or not v.path=="/watch" or not v.query.startswith("v=UyxxY0A_kow&t=")):
                raise ValueError("Unverified video embed or unsupported source")
        if car.get("reward") and (car["kind"]!="Moses" or car["status"]!=VERIFIED):
            raise ValueError("Payment cannot be claimed on unverified records")
        if car["status"]!="Verificata" and car.get("reward"):
            raise ValueError("No rewards for uncertain models")
    if any(car["name"] in str(doc.get("origin_lead",{}).get("status","")) for car in doc["items"]):
        raise ValueError("Unverified social post cannot claim vehicle identity")
    return doc

def index_body(doc,base):
    validate(doc)
    rows=doc["items"]
    totals={label:sum(car["status"]==label for car in rows) for label in STATUSES}
    items=[]
    for car in rows:
        slug=car["slug"]
        target=base+PATH+slug+"/"
        items.append(
            '<article class="vc-card" data-vc-card data-vc-slug="'+e(slug)+'" '
            'data-vc-owner="'+e(car["kind"])+'" data-vc-status="'+e(car["status"])+'" '
            'data-vc-search="'+e((car["name"]+" "+car["area"]+" "+car["kind"]+" "+car["category"]).casefold())+'">'
            '<div class="vc-card-top"><span class="vc-tag">'+e(car["kind"])+' · '+e(car["category"])+'</span>'
            '<small class="vc-confidence">'+e(car["status"])+'</small></div>'
            '<h2><a href="'+e(target)+'">'+e(car["name"])+'</a></h2>'
            '<p><strong>Zona:</strong> '+e(car["area"])+'</p>'
            '<p class="vc-hint">'+e(car["where"])+'</p>'
            '<div class="vc-card-end"><a class="vc-read" href="'+e(target)+'">'
            'Dove e come trovarla →</a><button type="button" data-vc-found="'+e(slug)+'" '
            'aria-pressed="false" aria-label="Segna '+e(car["name"])+' come trovata">'
            '□ Da trovare</button></div></article>'
        )
    return (
        '<section class="vc-hero"><span class="vc-eyebrow">GTA VI · ENCICLOPEDIA VEICOLI</span>'
        '<h1>Trova un veicolo in GTA VI</h1>'
        '<p>Cerca il modello, leggi il punto di ricerca e segui i passaggi per ottenerlo. '
        'Ogni auto ha una scheda separata con fonte, prerequisiti e risultato da verificare. '
        'Le posizioni riportate sono <strong>zone documentate, non spawn garantiti</strong>.</p>'
        '<div class="vc-summary"><strong>'+str(len(rows))+' schede</strong>'
        '<span>'+str(totals[VERIFIED])+' verificate · '
        +str(totals["In verifica"]+totals["Community"])+' da approfondire</span></div>'
        '</section><section class="vc-index" data-vc-finder aria-label="Catalogo veicoli">'
        '<div class="vc-toolbar">'
        '<label for="vc-search">Cerca modello o zona<input id="vc-search" type="search" '
        'data-vc-search placeholder="Es. Futo, Hellion, Vice Beach" autocomplete="off"></label>'
        '<label for="vc-owner">Tipo<select id="vc-owner" data-vc-owner>'
        '<option value="Tutti">Tutti</option><option value="Moses">Moses</option>'
        '<option value="Randy">Randy</option></select></label>'
        '<label for="vc-confidence">Verifica<select id="vc-confidence" data-vc-status>'
        '<option value="Tutte">Tutte</option><option value="Verificata">Verificata</option>'
        '<option value="In verifica">In verifica</option>'
        '<option value="Community">Community</option></select></label>'
        '<label class="vc-todo" for="vc-todo"><input id="vc-todo" data-vc-todo type="checkbox">'
        'Nascondi già trovate</label></div>'
        '<p class="vc-count" role="status" data-vc-count aria-live="polite">'
        +str(len(rows))+' veicoli nella raccolta</p><div class="vc-grid">'
        +''.join(items)+'</div><p class="vc-empty" data-vc-empty hidden>'
        'Nessuna scheda con questi filtri.</p></section>'
        '<section class="vc-method"><h2>Come funzionano i dati</h2>'
        '<p><strong>Verificata</strong>: modello documentato e istruzioni basate su walkthrough '
        'o mappe di riferimento; non assicura che lo spawn sia sempre disponibile. '
        '<strong>In verifica</strong>: modello indicato nella lista ma senza posizione '
        'specifica confermata. <strong>Community</strong>: fonti discordanti, non '
        'utilizzare come requisito del trofeo senza controllare nel gioco.</p>'
        '<p><strong>Conservare un veicolo:</strong> prenderlo o consegnarlo non equivale '
        'a registrarlo come personale. Consulta la '
        '<a href="'+e(base+'salvare-auto/')+'">guida sulla registrazione</a> '
        'e <a href="'+e(base+'guide-e-tutorial/scansionare-veicoli/')+'">'
        'controlla i tracker con WAiNK</a> prima di partire.</p>'
        '<p class="vc-lead">Segnalazione X da verificare: '
        '<a href="'+e(doc["origin_lead"]["url"])+'" target="_blank" rel="noopener noreferrer">'
        'post di @murciaconlimon ↗</a>. Il suo contenuto non è ancora leggibile da '
        'fonti verificabili: non attribuiamo a quel post auto di altre raccolte.</p>'
        '<p class="vc-privacy">La checklist “Trovata” resta soltanto in questo browser; '
        'non viene inviata a X, GitHub o a un server.</p></section>'
    )

def social_text(car,base):
    if car["status"]!=VERIFIED:return None
    path=base+PATH+car["slug"]+"/"
    desc=("Vicino a "+car["area"] if car["area"]!="Da verificare" else "Cerca gli indizi nel gioco")
    text="🚘 GTA VI | "+car["name"]+"\n"+desc+".\nPassaggi, requisiti e fonti in italiano:\n"+path+"\n#GTAVI"
    # URLs will count differently on X; stay well below 280 chars.
    if len(text)>250:raise ValueError("Long social draft")
    return text

def article_body(car,base,all_cars):
    validate({"schema":"botx-vehicle-catalog-v1","items":all_cars,"origin_lead":{"status":""}})
    canonical=base+PATH+car["slug"]+"/"
    intro=('Nel punto indicato cerca il modello, verifica tracker e requisiti con WAiNK. '
           'Una consegna a Moses o Randy non implica che il veicolo diventi di tua proprietà.')
    lines=[]
    for i,step in enumerate(car["steps"],1):
        lines.append('<li><span aria-hidden="true">'+str(i).zfill(2)+'</span><p>'+e(step)+'</p></li>')
    source_host="PowerPyx" if "powerpyx.com" in car["source_url"] else "GTABase"
    source2="GTABase" if "gtabase.com" in car["additional_source"] else "PowerPyx"
    related=[x for x in all_cars if x["slug"]!=car["slug"] and x["kind"]==car["kind"]][:4]
    check_label="Stato: "+car["status"]
    text=social_text(car,base)
    share=('<section class="vc-social" aria-labelledby="vc-social-title"><h2 id="vc-social-title">'
           'Post originale per X (bozza)</h2><p>Da pubblicare soltanto con una '
           'foto pertinente utilizzabile e dopo controllo editoriale. '
           'Nessun invio automatico da questa pagina.</p>'
           '<blockquote>'+e(text).replace("\n","<span class=\"vc-line-break\"></span>")+'</blockquote>'
           '<a href="https://x.com/intent/tweet?text='+quote(text,safe="")+'" target="_blank" '
           'rel="noopener noreferrer">Apri la bozza su X ↗</a></section>') if text else (
           '<p class="vc-social-pending">Post X non disponibile: dati da verificare '
           'prima della promozione.</p>')
    video=('<p class="vc-video"><a href="'+e(car["video_url"])+'" target="_blank" '
           'rel="noopener noreferrer">▶ Guarda il modello nel video IGN dal '
           +e(car["video_stamp"])+' ↗</a> · Link al player del canale originale, '
           'nessuno screenshot copiato.</p>') if car.get("video_url") else ''
    caution=(
        'Regalo finale di Moses: contiene uno spoiler.'
        if car.get("spoiler") else
        'La zona di ricerca può cambiare con il progresso di storia e i controlli delle missioni.'
    )
    return (
        '<nav class="vc-crumb" aria-label="Percorso"><a href="'+e(base+PATH)+'">'
        'Tutti i veicoli</a><span aria-hidden="true"> › </span>'
        +e(car["name"])+'</nav>'
        '<article class="vc-article" data-vc-detail="'+e(car["slug"])+'">'
        '<section class="vc-article-hero"><span class="vc-eyebrow">'
        +e(car["kind"]+" · "+car["category"])+'</span>'
        '<h1>'+e(car["name"])+': dove trovarla in GTA VI</h1>'
        '<p>'+e(intro)+'</p>'
        '<span class="vc-confidence">'+e(check_label)+'</span></section>'
        '<section class="vc-facts" aria-label="Risposta immediata"><h2>Dove, quando, cosa ottenere</h2>'
        '<dl><div><dt>Zona</dt><dd>'+e(car["area"])+'</dd></div>'
        '<div><dt>Dove cercare</dt><dd>'+e(car["where"])+'</dd></div>'
        '<div><dt>Quando</dt><dd>'+e(car["unlock"])+'</dd></div>'
        +('<div><dt>Pagamento base</dt><dd>'+e(car["reward"])+' (bonus condizioni variabile)</dd></div>' if car.get("reward") else '')
        '</dl><p class="vc-safety"><strong>Attenzione:</strong> '+e(caution)+'</p></section>'
        '<section class="vc-instructions" id="procedura"><h2>Come ottenerla: '
        +str(len(car["steps"]))+' passaggi</h2><ol>'+''.join(lines)+'</ol>'
        '<p class="vc-check"><strong>✓ Controllo finale:</strong> '
        +e(car["check"])+'</p></section>'
        '<section class="vc-context"><h2>Come riconoscerla e conservarla</h2>'
        '<p><strong>Indizio visivo:</strong> '+e(car["visual"])+'</p>'
        '<p>'+e(car.get("tracker") or "Scansiona con WAiNK prima di tentare il furto.")+'</p>'
        '<p>'+e(car["note"])+'</p>'
        '<p>Vuoi tenerla invece di consegnarla? Verifica prima '
        '<a href="'+e(base+'salvare-auto/')+'">come registrare un’auto personale</a>. '
        'Controlla tracker, garage e limiti nel gioco: non tutte le auto '
        'si possono registrare nello stesso momento della storia.</p>'
        '</section><section class="vc-source"><h2>Fonti e posizione sulla mappa</h2>'
        '<p>I punti geografici sono quelli descritti dagli autori delle guide; '
        'non abbiamo inventato coordinate o screenshot di gioco.</p>'
        '<a href="'+e(car["source_url"])+'" target="_blank" rel="noopener noreferrer">'
        'Fonte della procedura: '+source_host+' ↗</a>'
        '<a href="'+e(car["additional_source"])+'" target="_blank" rel="noopener noreferrer">'
        'Verifica o mappa: '+source2+' ↗</a>'
        +video+'</section>'+share+
        '<nav class="vc-related" aria-label="Altri veicoli da cercare"><h2>Altre schede</h2>'
        +''.join('<a href="'+e(base+PATH+x["slug"]+"/")+'">'+e(x["name"])+' →</a>' for x in related)
        +'</nav></article>'
    )

def pages(doc,base):
    validate(doc)
    for car in doc["items"]:
        yield car,PATH+car["slug"]+"/",article_body(car,base,doc["items"])
