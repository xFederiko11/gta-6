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
    verified=sum(x["status"]==VERIFIED for x in rows)
    cards=[]
    for car in rows:
        slug=car["slug"]
        target=base+PATH+slug+"/"
        terms=e(" ".join(str(car[k]) for k in ("name","area","kind","category")).casefold())
        cards.append(
            f'<article class="vc-card" data-vc-card data-vc-slug="{e(slug)}" '
            f'data-vc-owner="{e(car["kind"])}" data-vc-status="{e(car["status"])}" '
            f'data-vc-terms="{terms}">'
            f'<div class="vc-card-top"><span class="vc-tag">{e(car["kind"])} · '
            f'{e(car["category"])}</span><small class="vc-confidence">'
            f'{e(car["status"])}</small></div>'
            f'<h2><a href="{e(target)}">{e(car["name"])}</a></h2>'
            f'<p><strong>Zona:</strong> {e(car["area"])}</p>'
            f'<p class="vc-hint">{e(car["where"])}</p>'
            f'<div class="vc-card-end"><a class="vc-read" href="{e(target)}">'
            f'Dove e come trovarla →</a><button type="button" data-vc-found="{e(slug)}" '
            f'aria-pressed="false" aria-label="Segna {e(car["name"])} come trovata">'
            f'□ Da trovare</button></div></article>'
        )
    return "".join([
        '<section class="vc-hero"><span class="vc-eyebrow">GTA VI · ENCICLOPEDIA VEICOLI</span>',
        '<h1>Trova un veicolo in GTA VI</h1>',
        '<p>Cerca il modello, leggi il punto di ricerca e segui i passaggi per ottenerlo. ',
        'Ogni auto ha una scheda separata con fonte, prerequisiti e risultato da verificare. ',
        'Le posizioni riportate sono <strong>zone documentate, non spawn garantiti</strong>.</p>',
        f'<div class="vc-summary"><strong>{len(rows)} schede</strong>'
        f'<span>{verified} verificate · {len(rows)-verified} da approfondire</span></div>',
        '</section><section class="vc-index" data-vc-finder aria-label="Catalogo veicoli">',
        '<div class="vc-toolbar">',
        '<label for="vc-search">Cerca modello o zona<input id="vc-search" type="search" ',
        'data-vc-search placeholder="Es. Futo, Hellion, Vice Beach" autocomplete="off"></label>',
        '<label for="vc-owner">Tipo<select id="vc-owner" data-vc-filter-owner>',
        '<option value="Tutti">Tutti</option><option value="Moses">Moses</option>',
        '<option value="Randy">Randy</option></select></label>',
        '<label for="vc-confidence">Verifica<select id="vc-confidence" data-vc-filter-status>',
        '<option value="Tutte">Tutte</option><option value="Verificata">Verificata</option>',
        '<option value="In verifica">In verifica</option>',
        '<option value="Community">Community</option></select></label>',
        '<label class="vc-todo" for="vc-todo"><input id="vc-todo" data-vc-todo type="checkbox">',
        'Nascondi già trovate</label></div>',
        f'<p class="vc-count" role="status" data-vc-count aria-live="polite">'
        f'{len(rows)} veicoli nella raccolta</p><div class="vc-grid">',
        "".join(cards),
        '</div><p class="vc-empty" data-vc-empty hidden>Nessuna scheda con questi filtri.</p>',
        '</section><section class="vc-method"><h2>Come funzionano i dati</h2>',
        '<p><strong>Verificata</strong>: modello documentato e istruzioni basate su walkthrough ',
        'o mappe di riferimento; non assicura che lo spawn sia sempre disponibile. ',
        '<strong>In verifica</strong>: modello indicato nella lista ma senza posizione ',
        'specifica confermata. <strong>Community</strong>: fonti discordanti, non ',
        'utilizzare come requisito del trofeo senza controllare nel gioco.</p>',
        '<p><strong>Conservare un veicolo:</strong> prenderlo o consegnarlo non equivale ',
        f'a registrarlo come personale. Consulta la <a href="{e(base+"salvare-auto/")}">'
        'guida sulla registrazione</a> ',
        f'e <a href="{e(base+"guide-e-tutorial/scansionare-veicoli/")}">'
        'controlla i tracker con WAiNK</a> prima di partire.</p>',
        '<p class="vc-lead">Segnalazione X da verificare: ',
        f'<a href="{e(doc["origin_lead"]["url"])}" target="_blank" rel="noopener noreferrer">'
        'post di @murciaconlimon ↗</a>. Il suo contenuto non è ancora leggibile da ',
        'fonti verificabili: non attribuiamo a quel post auto di altre raccolte.</p>',
        '<p class="vc-privacy">La checklist “Trovata” resta soltanto in questo browser; ',
        'non viene inviata a X, GitHub o a un server.</p></section>'
    ])

def social_text(car,base):
    if car["status"]!=VERIFIED:return None
    path=base+PATH+car["slug"]+"/"
    desc=("Vicino a "+car["area"] if car["area"]!="Da verificare" else "Cerca gli indizi nel gioco")
    text="🚘 GTA VI | "+car["name"]+"\n"+desc+".\nPassaggi, requisiti e fonti in italiano:\n"+path+"\n#GTAVI"
    # URLs will count differently on X; stay well below 280 chars.
    if len(text)>250:raise ValueError("Long social draft")
    return text

def article_body(car,base,all_cars):
    validate({"schema":"botx-vehicle-catalog-v1","items":all_cars,
              "origin_lead":{"status":""}})
    title=car["name"]
    slug=car["slug"]
    intro=("Nel punto indicato cerca il modello, verifica tracker e requisiti con WAiNK. "
           "Una consegna a Moses o Randy non implica che il veicolo diventi di tua proprietà.")
    steps="".join(
        f'<li><span aria-hidden="true">{n:02d}</span><p>{e(step)}</p></li>'
        for n,step in enumerate(car["steps"],1)
    )
    original="PowerPyx" if "powerpyx.com" in car["source_url"] else "GTABase"
    second="GTABase" if "gtabase.com" in car["additional_source"] else "PowerPyx"
    related=[x for x in all_cars if x["slug"]!=slug and x["kind"]==car["kind"]][:4]
    related_html="".join(
        f'<a href="{e(base+PATH+x["slug"]+"/")}">{e(x["name"])} →</a>'
        for x in related
    )
    reward=(
        f'<div><dt>Pagamento base</dt><dd>{e(car["reward"])} '
        '(bonus condizioni variabile)</dd></div>'
        if car.get("reward") else ""
    )
    warning=("Regalo finale di Moses: contiene uno spoiler."
             if car.get("spoiler") else
             "La zona di ricerca può cambiare con il progresso di storia e i controlli delle missioni.")
    video=(
        f'<p class="vc-video"><a href="{e(car["video_url"])}" target="_blank" '
        f'rel="noopener noreferrer">▶ Guarda il modello nel video IGN dal '
        f'{e(car["video_stamp"])} ↗</a> · Link al player del canale originale, '
        'nessuno screenshot copiato.</p>'
        if car.get("video_url") else ""
    )
    draft=social_text(car,base)
    share=(
        '<section class="vc-social" aria-labelledby="vc-social-title">'
        '<h2 id="vc-social-title">Post originale per X (bozza)</h2>'
        '<p>Da pubblicare soltanto con una foto pertinente utilizzabile '
        'e dopo controllo editoriale. Nessun invio automatico da questa pagina.</p>'
        f'<blockquote>{e(draft).replace(chr(10),"<span class=vc-line-break></span>")}</blockquote>'
        f'<a href="https://x.com/intent/tweet?text={quote(draft,safe="")}" target="_blank" '
        'rel="noopener noreferrer">Apri la bozza su X ↗</a></section>'
        if draft else (
        '<p class="vc-social-pending">Post X non disponibile: dati da verificare '
        'prima della promozione.</p>')
    )
    parts=[
        f'<nav class="vc-crumb" aria-label="Percorso"><a href="{e(base+PATH)}">'
        f'Tutti i veicoli</a><span aria-hidden="true"> › </span>{e(title)}</nav>',
        f'<article class="vc-article" data-vc-detail="{e(slug)}">',
        f'<section class="vc-article-hero"><span class="vc-eyebrow">'
        f'{e(car["kind"])} · {e(car["category"])}</span>',
        f'<h1>{e(title)}: dove trovarla in GTA VI</h1>',
        f'<p>{e(intro)}</p><span class="vc-confidence">Stato: '
        f'{e(car["status"])}</span></section>',
        '<section class="vc-facts" aria-label="Risposta immediata">',
        '<h2>Dove, quando, cosa ottenere</h2><dl>',
        f'<div><dt>Zona</dt><dd>{e(car["area"])}</dd></div>',
        f'<div><dt>Dove cercare</dt><dd>{e(car["where"])}</dd></div>',
        f'<div><dt>Quando</dt><dd>{e(car["unlock"])}</dd></div>',
        reward,
        '</dl><p class="vc-safety"><strong>Attenzione:</strong> ',
        e(warning),'</p></section>',
        '<section class="vc-instructions" id="procedura">',
        f'<h2>Come ottenerla: {len(car["steps"])} passaggi</h2><ol>',
        steps,'</ol><p class="vc-check"><strong>✓ Controllo finale:</strong> ',
        e(car["check"]),'</p></section>',
        '<section class="vc-context"><h2>Come riconoscerla e conservarla</h2>',
        '<p><strong>Indizio visivo:</strong> ',e(car["visual"]),'</p>',
        '<p>',e(car.get("tracker") or "Scansiona con WAiNK prima di tentare il furto."),'</p>',
        '<p>',e(car["note"]),'</p>',
        '<p>Vuoi tenerla invece di consegnarla? Verifica prima ',
        f'<a href="{e(base+"salvare-auto/")}">come registrare un’auto personale</a>. ',
        'Controlla tracker, garage e limiti nel gioco: non tutte le auto ',
        'si possono registrare nello stesso momento della storia.</p></section>',
        '<section class="vc-source"><h2>Fonti e posizione sulla mappa</h2>',
        '<p>I punti geografici sono quelli descritti dagli autori delle guide; ',
        'non abbiamo inventato coordinate o screenshot di gioco.</p>',
        f'<a href="{e(car["source_url"])}" target="_blank" rel="noopener noreferrer">'
        f'Fonte della procedura: {original} ↗</a>',
        f'<a href="{e(car["additional_source"])}" target="_blank" rel="noopener noreferrer">'
        f'Verifica o mappa: {second} ↗</a>',
        video,'</section>',share,
        '<nav class="vc-related" aria-label="Altri veicoli da cercare">',
        '<h2>Altre schede</h2>',related_html,'</nav></article>'
    ]
    return "".join(parts)

def pages(doc,base):
    validate(doc)
    for car in doc["items"]:
        yield car,PATH+car["slug"]+"/",article_body(car,base,doc["items"])
