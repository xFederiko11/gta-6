"""Sourced regional collectible circuits for GTA VI PS5. Never fabricate GPS pins.

157 described POIs grouped by neighborhood (editorial grouping, not measured route).
Only published source URLs are linked and no gameplay screenshots are claimed.
"""
from __future__ import annotations
from collections import Counter
from html import escape
from urllib.parse import urlsplit, urlencode
from collectible_photo_evidence_v1 import validate as validate_photo_evidence, render as render_photo_evidence
from collectible_video_refs_v1 import render as render_collectible_video
import re

BASE="https://xfederiko11.github.io/gta-6/"
PATH="collezionabili/percorsi/"
REGION_ORDER=("kelly","vice-city","vice-dale","vice-beach","mariana","leonard","lummox")
TYPES={"playlist":"Playlist","cards":"Carte","waink":"Scansioni WAiNK","underwater":"Immersioni","stunt":"Salti acrobatici","vehicles":"Veicoli WAiNK","reading":"Libri e letture","magazines":"Riviste e fumetti","kenton":"Tesori Kenton (non 33 scoperte)"}
ALLOWED={"www.powerpyx.com","www.pushsquare.com","www.gtabase.com"}


def e(value):
    return escape(str(value),quote=True)


def validate_routes(data):
    if data.get("schema")!="gta6-region-routes-v8":
        raise ValueError("Unexpected region route schema")
    if data.get("checked")!="2026-11-21":
        raise ValueError("Missing review date")
    if not isinstance(data.get("sources"),dict) or len(data["sources"])<12:
        raise ValueError("Source registry is incomplete")
    for link in data["sources"].values():
        target=urlsplit(link)
        if target.scheme!="https" or target.hostname not in ALLOWED or target.username or target.password or target.port not in (None,443):
            raise ValueError("Unapproved external URL")
    regions=data.get("regions",[])
    if len(regions)!=7 or {x.get("id") for x in regions}!=set(REGION_ORDER):
        raise ValueError("Missing regional group")
    for group in regions:
        if not 3<=len(group.get("name",""))<=90 or not 40<=len(group.get("description",""))<=260:
            raise ValueError("Missing regional instructions")
        if not 20<=len(group.get("warning",""))<=220:
            raise ValueError("Regional caveat missing")
    items=data.get("points",[])
    if len(items)!=157 or len({x.get("id") for x in items})!=157:
        raise ValueError("Expected exactly 157 individually documented stops")
    counts=Counter(x["type"] for x in items)
    if counts!={"playlist":5,"cards":57,"waink":38,"underwater":6,"stunt":24,"vehicles":3,"reading":2,"magazines":20,"kenton":2}:
        raise ValueError("Unreviewed waypoint distribution")
    for n,item in enumerate(items,1):
        if item.get("id")!="pt-"+str(n).zfill(2):
            raise ValueError("Unexpected waypoint numbering")
        if item.get("region") not in REGION_ORDER or item.get("type") not in TYPES:
            raise ValueError("Unknown region or collectible type")
        if item.get("source") not in data["sources"]:
            raise ValueError("Missing direct source")
        if item.get("confidence")!="described":
            raise ValueError("Unsupported proof precision")
        for prop,low,high in (("name",5 if item.get("type")=="magazines" else 9,110),("place",10,210),("hint",24,330)):
            value=item.get(prop,"")
            if not isinstance(value,str) or not low<=len(value)<=high:
                raise ValueError("Incomplete waypoint: "+item["id"]+" "+prop)
        if any(k in item for k in ("lat","lng","long","coordinates","duration_minutes","distance_km")):
            raise ValueError("No coordinates, timing or distances can be invented")
        if item.get("missable"):
            if item.get("region")!="kelly" or item.get("name") not in ("Vicki — Delights Dancers","Victor Maravilla — Los Santos Corkers"):
                raise ValueError("Unverified missable warning")
            if "Capitolo 2" not in item.get("when",""):
                raise ValueError("Missing missable timing")
    if {x["name"] for x in items if x.get("missable")}!={"Vicki — Delights Dancers","Victor Maravilla — Los Santos Corkers"}:
        raise ValueError("Both source-backed missable cards required")
    jack=[item for item in items if item.get("card_set")=="jack-of-hearts"]
    if (len(jack)!=36 or {item.get("card_number") for item in jack}!=set(range(1,37))
            or {item.get("source_order") for item in jack}!=set(range(1,37))
            or any(type(item.get("card_number")) is not int or type(item.get("source_order")) is not int
                   or item.get("source")!="jack" or item.get("type")!="cards" for item in jack)):
        raise ValueError("Jack of Hearts needs 36 distinct sourced menu cards and source positions")
    if any(item.get("source")=="jack" and item not in jack for item in items):
        raise ValueError("Jack of Hearts card metadata missing")
    if {item["id"]:item["card_number"] for item in jack if item["id"] in {"pt-12","pt-32"}}!={"pt-12":3,"pt-32":13}:
        raise ValueError("Existing Jack of Hearts checklist IDs must remain stable")
    water=data.get("underwater",{})
    if water.get("required")!=33 or water.get("known_in_atlas")!=6:
        raise ValueError("Underwater count incorrectly claims full coverage")
    if data.get("cards",{}).get("required_sets")!=15 or data.get("cards",{}).get("total_sets")!=18:
        raise ValueError("Card 100 percent threshold mismatch")
    if data.get("waink",{}).get("required")!=100 or data["waink"].get("known_in_atlas")!=38 or data.get("cards",{}).get("known_in_atlas")!=57:
        raise ValueError("Wrong WAiNK target")
    magazine=data.get("magazines",{})
    if [magazine.get(x) for x in ("total_titles","documented_titles","combined_total_with_book_swaps","required_for_100_percent","location_limited_copies")]!=[27,20,34,30,9]:
        raise ValueError("Magazine 100% threshold and location-limited copies mismatch")
    if len([p for p in items if p["type"]=="magazines" and p.get("location_limited")])!=9:
        raise ValueError("Nine editorially verified chapter-limited magazine COPIES required")
    for item in items:
        if item["type"]=="magazines":
            if item["source"]!="magazines":
                raise ValueError("Magazine must be traced to official guide source registry")
            if item.get("location_limited"):
                if item.get("before_chapter") not in (1,2,3) or "copie alternative" not in item.get("location_note",""):
                    raise ValueError("Magazine warning must refer to lost copy, not a broken platinum")
            elif "before_chapter" in item or "location_note" in item:
                raise ValueError("A permanent magazine should not be flagged as limited")
        if item["type"]=="kenton":
            if item.get("counts_underwater") is not False or item["source"]!="under":
                raise ValueError("Treasure-only dive must not be counted among 33 discoveries")
        elif "counts_underwater" in item:
            raise ValueError("Only treasure-only dives may explicitly carry underwater exclusion")
    if data.get("kenton",{}).get("treasure_only")!=2 or data["kenton"].get("counts_underwater") is not False:
        raise ValueError("Kenton treasure-only count cannot inflate 6/33 underwater discoveries")
    stunts=data.get("stunts",{})
    if [stunts.get(x) for x in ("total","needed","under_bridges","stunt_jumps","knife_flights","base_jumps")]!=[397,300,202,130,40,25]:
        raise ValueError("Stunt subtype counts changed")
    if sum(n for _,n in stunts.get("jump_by_region",[]))!=130 or stunts.get("known_in_atlas")!=24:
        raise ValueError("Stunt Jump county breakdown wrong")
    return True


def render(data,curated_refs=(),photo_evidence=None):
    validate_routes(data)
    if photo_evidence is not None:
        validate_photo_evidence(photo_evidence,data)
    regions={x["id"]:x for x in data["regions"]}
    counts=Counter(x["type"] for x in data["points"])
    output=[
        '<section class="cr-root" data-collectible-routes>',
        '<header class="cr-hero"><span class="eyebrow">⌖ GTA VI ITALIA · PS5 / PS5 PRO</span>',
        '<h1>Percorsi collezionabili GTA 6: regioni e checkpoint</h1>',
        '<p><strong>157 posizioni documentate in sette aree</strong>,',
        ' raggruppate per vicinanza editoriale. Non sono tracciati GPS né',
        ' 157 pin di una mappa verificata; ogni checkpoint rimanda alla',
        ' fonte originale con screenshot e indicazioni dettagliate.</p>',
        '<div class="cr-stats" role="group" aria-label="Copertura percorsi">',
        '<div><strong>157</strong><small>checkpoint documentati</small></div>',
        '<div><strong>7</strong><small>aree di raccolta</small></div>',
        '<div><strong>6/33</strong><small>siti subacquei verificati qui</small></div>',
        '<div><strong>2</strong><small>carte potenzialmente mancabili</small></div>',
        '</div><nav class="cr-shortcuts" aria-label="Scorciatoie collezionabili">',
        '<a class="v-button" href="#cr-pt-26">Prima: carte mancabili →</a>',
        '<a class="v-button secondary" href="'+BASE+'trofei/100-percento/">Checklist 100% →</a>',
        '<a class="v-button secondary" href="'+BASE+'screenshot-ps5/invia/">Invia screenshot PS5 →</a>',
        '<a class="v-button secondary" href="https://x.com/intent/follow?screen_name=xFederiko11" target="_blank" rel="noopener noreferrer" data-cr-follow>Segui X per nuove posizioni ↗</a>',
        '</nav></header>',
        '<aside class="cr-alert" role="note"><strong>⚠️ Prima di lasciare il Capitolo 2:</strong>',
        ' recupera Vicki nel bagno dell’ufficio e Victor Maravilla nella cucina dello Starlet Motel',
        ' a Gellhorn. Le fonti riportano che questi luoghi non sono più accessibili',
        ' dopo il Capitolo 2. La perdita delle carte può compromettere le relative collezioni,',
        ' anche se per il 100% bastano 15 set completi su 18.</aside>',
        '<aside class="cr-alert" role="note"><strong>⚠️ Copie di riviste legate ai capitoli:</strong>',
        ' cinque copie nella casa di Jason (Capitolo 1), due allo Starlet Motel (Capitolo 2),',
        ' due nell’appartamento Bayside (Capitolo 3) possono diventare irraggiungibili.',
        ' <strong>Attenzione:</strong> PowerPyx segnala copie alternative degli stessi titoli:',
        ' perdere una specifica copia non rende automaticamente impossibile il 100%.',
        ' Sono necessari 30 su 34 titoli fra riviste e Book Swaps.</aside>',
        '<nav class="cr-priority-links" aria-label="Oggetti da controllare prima di avanzare nella storia">',
        '<strong>Controlla prima i mancabili:</strong> ',
        '<a href="#cr-pt-102">Capitolo 1 · riviste</a> ',
        '<a href="#cr-pt-26">Capitolo 2 · Vicki</a> ',
        '<a href="#cr-pt-66">Capitolo 2 · Victor</a> ',
        '<a href="#cr-pt-108">Capitolo 2 · riviste</a> ',
        '<a href="#cr-pt-111">Capitolo 3 · riviste</a></nav>',
        '<section class="cr-controls" aria-label="Filtri dei percorsi">',
        '<label class="cr-search">Cerca oggetto o luogo',
        '<input type="search" data-cr-query placeholder="Es. Vicki, Key Lento, poster" autocomplete="off"></label>',
        '<div class="cr-filter-group" aria-label="Raccolta completa documentata">'
        '<button type="button" data-cr-jack aria-pressed="false" hidden>Jack of Hearts · 36 posizioni documentate</button></div>',
        '<p class="cr-note-count">Jack of Hearts: tutti i 36 numeri del menu sono descritti qui. '
        'Il numero della carta nel menu è distinto dall’ordine del percorso. '
        'Capitolo minimo non documentato per l’intera raccolta: verifica gli accessi nella tua partita. '
        'Premi Tutti per tornare agli altri oggetti; le spunte indicano soltanto ciò che hai segnato tu.</p>',
        '<p><a href="'+BASE+'guide-e-tutorial/jack-of-hearts-36-cards/">Guida dedicata Jack of Hearts: 36 carte, numeri menu e indizi dei luoghi →</a></p>',
        '<div class="cr-filter-group" aria-label="Tipo di collezionabile">',
        '<button type="button" data-cr-filter="all" aria-pressed="true">Tutti · 157</button>'
    ]
    for typ,name in TYPES.items():
        output.append('<button type="button" data-cr-filter="'+e(typ)+'" aria-pressed="false">'+e(name)+' · '+str(counts[typ])+'</button>')
    output.extend([
        '</div><div class="cr-progress-wrap"><strong data-cr-progress>0 / 157 checkpoint segnati</strong>',
        '<progress max="157" value="0" data-cr-bar aria-label="Checkpoint segnati"></progress>',
        '<small data-cr-storage>Spunte private in questo browser, non collegate al PSN.</small></div>',
        '<p data-cr-visible role="status" aria-live="polite">157 checkpoint mostrati</p></section>',
        '<section class="cr-status" aria-label="Limiti del tracciamento"><h2>Ottimizzazione senza mappe inventate</h2>',
        '<p>Per una run orientata al Platino, <strong>Kelly County prima del cambio capitolo</strong>,',
        ' poi le aree urbane di Vice City e le immersioni in Mariana County quando',
        ' hai barca ed equipaggiamento. Questo ordine è una proposta basata sulle',
        ' posizioni documentate, non un itinerario calcolato con tempi o chilometri.</p>',
        '<p><strong>Prima area utile:</strong> il circuito di Key Lento riunisce curiosità WAiNK,',
        ' carte, veicoli da scansionare e due letture. I veicoli sono conteggiati come',
        ' categoria separata e non vanno scambiati per le scansioni di luoghi WAiNK.',
        ' <a href="'+e(data["sources"]["key_lento"])+'" target="_blank" rel="noopener noreferrer">',
        'Apri la guida fotografica Key Lento ↗</a>.</p>',
        '<p><strong>Nuove letture:</strong> 20 riviste e fumetti con luoghi descritti da PowerPyx.',
        ' Le riviste Style non contano nella categoria 30/34; i due tesori Kenton',
        ' aggiunti a Belpoint Strait e Bobcat Dive Site NON contano nel 6/33',
        ' delle Underwater Discoveries. <a href="'+e(data["sources"]["magazines"])+'"',
        ' target="_blank" rel="noopener noreferrer">Leggi i dettagli originali ↗</a>.</p>',
        '<p><strong>Copertura parziale:</strong> queste 57 carte sono una selezione delle 480',
        ' e queste 38 scansioni una selezione dei punti WAiNK.',
        ' Per le immersioni, sei luoghi su 33 sono documentati qui: mancano',
        ' ancora 27 posizioni. Anche i 24 salti qui documentati non coprono i 130 totali. Usa la checklist di gioco per il vero 100%.</p>',
        '<p><a href="'+e(data["sources"]["allmap"])+'" target="_blank" rel="noopener noreferrer">',
        'Apri mappa generale GTABase ↗</a> · ',
        '<a href="'+e(data["sources"]["cardmap"])+'" target="_blank" rel="noopener noreferrer">',
        'Filtro carte GTABase ↗</a>. Questi link esterni mostrano categorie,',
        ' non sono link diretti a un pin per ogni checkpoint.</p></section>',
    ])
    for region in REGION_ORDER:
        reg=regions[region]
        area=[x for x in data["points"] if x["region"]==region]
        output.extend([
            '<section class="cr-region" data-cr-region="'+e(region)+'" id="cr-'+e(region)+'">',
            '<header class="cr-region-head"><span class="cr-area-number">'+str(REGION_ORDER.index(region)+1).zfill(2)+'</span>',
            '<div><span class="eyebrow">'+e(reg["subtitle"])+'</span>',
            '<h2>'+e(reg["name"])+'</h2>',
            '<p>'+e(reg["description"])+'</p>',
            '<small>Nota: '+e(reg["warning"])+'</small></div>',
            '<strong class="cr-region-count" data-cr-region-count>0/'+str(len(area))+'</strong></header>',
            '<ol class="cr-steps">'
        ])
        for idx,item in enumerate(area,1):
            warning=(('<div class="cr-missable-warning"><strong>Potenzialmente mancabile:',
                      ' entro il Capitolo 2.</strong> Verifica con salvataggio manuale',
                      ' prima di avanzare.</div>') if item.get("missable") else ())
            if warning:
                warning=''.join(warning)
            else:
                warning=''
            limited=('<div class="cr-limited-copy"><strong>Copia legata al Capitolo '+
                     str(item["before_chapter"])+'</strong>. '+e(item["location_note"])+'</div>'
                     if item.get("location_limited") else '')
            if item["type"]=="kenton":
                limited+='<p class="cr-note-count">Solo tesori Kenton: non incrementa il contatore delle 33 scoperte subacquee.</p>'
            tweet=("@xFederiko11 #GTA6Italia FOTO PS5 originale "+item["id"]+
                   " | "+item["name"][:65]+
                   ". Sono autore e autorizzo volontariamente il riuso gratuito su GTA VI Italia con credito. Allego personalmente la foto.")
            if len(tweet)>270:
                raise ValueError("Oversize social screenshot request")
            intent="https://x.com/intent/tweet?"+urlencode({"text":tweet})
            curated=next((ref for ref in curated_refs if item["id"] in ref["checkpoint_ids"]),None)
            contextual_link=(
                '<p class="cr-direct-map"><a data-cr-curated-link '
                'data-umami-event="game-map-curated-link-open-intent" href="'+e(curated["url"])+
                '" target="_blank" rel="noopener noreferrer">📍 '+e(curated["label"])+
                ' ↗</a><small>Riferimento esterno a un edificio o zona, '
                'NON pin della posizione esatta dell’oggetto</small></p>'
                if curated else '')
            output.append(
                '<li class="cr-step" id="cr-'+e(item["id"])+'" data-cr-step="'+e(item["id"])+'" data-cr-type="'+e(item["type"])+'" '
                'data-cr-set="'+e(item.get("card_set",""))+'" data-cr-search="'+e(item["name"]+" "+item["place"]+" "+item["hint"])+'" '
                 'data-cr-deadline="'+str(item.get("before_chapter",2 if item.get("missable") else 99))+'">'
                '<div class="cr-step-head"><span>'+str(idx).zfill(2)+'</span>'
                '<div><strong>'+e(item["name"])+'</strong>'
                '<small>'+e(TYPES[item["type"]])+(' · Card '+str(item['card_number'])+' nel menu' if item.get('card_set')=='jack-of-hearts' else '')+' · zona descritta</small></div>'
                '<label class="cr-check"><input type="checkbox" data-cr-done="'+e(item["id"])+'" '
                'aria-label="Segna '+e(item["name"])+' come trovato"><span>Fatto</span></label></div>'
                +warning+limited+
                '<p class="cr-instruction-where"><strong>1 · VAI QUI</strong> '+e(item["place"])+'</p>'
                '<p class="cr-instruction-do"><strong>2 · FAI QUESTO</strong> '+e(item["hint"])+'</p>'+
                (render_photo_evidence(item,photo_evidence,data) if photo_evidence is not None else '')+
                '<details class="cr-step-extra"><summary>📷 Foto, mappa e fonti (facoltativi)</summary>'
                +contextual_link+
                render_collectible_video(item)+
                '<a href="'+e(data["sources"][item["source"]])+'" target="_blank" rel="noopener noreferrer">'
                'Fonte originale e immagini ↗</a> · '
                '<button type="button" class="cr-map-find" data-vim-map-search="'+e(item["name"])+'" '
                'aria-label="Cerca '+e(item["name"])+' nella mappa esterna">🗺️ Cerca nella mappa (nome) ↗</button> · '
                '<a data-cr-photo-intent="'+e(item["id"])+'" href="'+e(intent)+'" '
                'target="_blank" rel="noopener noreferrer">📷 Proponi tua foto PS5 via X ↗</a>'
                '</details></li>'
            )
        output.extend(['</ol></section>'])
    stunts=data["stunts"]
    output.extend([
        '<section class="cr-remaining" id="radio-segrete"><h2>Due radio segrete: 5 poster</h2>',
        '<p>Scansiona i poster con WAiNK: tieni premuto ↑, inquadra il poster e tieni premuto R1. Apri le schede qui sotto per posizione e foto originali.</p>',
        '<ol><li><a href="#cr-pt-09">The Vault</a>: basta il poster del locale. Cerca The Vault nell’elenco Radio.</li>',
        '<li>The Sniper of La Perle: <a href="#cr-pt-01">Aunt Zola</a>, <a href="#cr-pt-02">TWA Ponya</a>, <a href="#cr-pt-03">Drip Drops</a>, <a href="#cr-pt-07">Jack of Hearts</a>. L’ultimo locale richiede avanzamento nel Capitolo 3 secondo GTABase. Cerca la playlist sotto On Demand dopo tutti e quattro i poster.</li></ol>',
        '<p>Controlla Progressi → Collezioni → Esplorazione → Playlist uniche: servono 2 su 2 per il 100%. ',
        '<a href="'+e(data["sources"]["playlist"])+'" target="_blank" rel="noopener noreferrer">Posizioni PowerPyx ↗</a> · ',
        '<a href="'+e(data["sources"]["playlist_gtabase"])+'" target="_blank" rel="noopener noreferrer">Conferma e sblocco GTABase ↗</a>.</p></section>',
        '<section class="cr-remaining"><h2>Acrobazie, veicoli e le categorie non mappate qui</h2>',
        '<p>Per il 100% servono <strong>300 su 397 acrobazie</strong>: 202 sottoponti,',
        ' 130 salti, 40 voli radenti e 25 salti BASE. Non esiste in questo atlante',
        ' una lista di 300 singoli pin verificati, quindi non presentiamo 300',
        ' checkpoint come raccolti. I sottoponti sono spesso più rapidi da tentare,',
        ' ma dipende dal mezzo e dalle condizioni di volo.</p>',
        '<p>Salti acrobatici documentati per contea: ',
        ' · '.join(e(x)+': '+str(n) for x,n in stunts["jump_by_region"])+'. ',
        '<a href="'+e(data["sources"]["stuntall"])+'" target="_blank" rel="noopener noreferrer">',
        'Apri la fonte per i requisiti e i contatori ↗</a>.</p>',
        '<h3>Sottoponti: come registrarli</h3>',
        '<p>PowerPyx elenca 202 passaggi sotto i ponti. Usa un aereo o un elicottero, allineati all’apertura e attraversala in volo senza toccare acqua o struttura. Controlla Progressi → Attività → Acrobazie e il nome del ponte sulla mappa. ',
        '<a href="'+e(data["sources"]["bridges"])+'" target="_blank" rel="noopener noreferrer">Elenco per contea e schermate originali ↗</a>.</p>',
        '<p>WAiNK: 100 scansioni necessarie per il 100%, ma i murales AHOL',
        ' e 1010 hanno sezioni proprie e non valgono per questo contatore.',
        ' <a href="'+e(data["sources"]["waink"])+'" target="_blank" rel="noopener noreferrer">',
        'Approfondisci WAiNK ↗</a>.</p>',
        '<h3>No Flusher Tags</h3><p>Segui i messaggi di Cal, cerca le marcature a terra e scansionale con WAiNK. PowerPyx (26 novembre) elenca 15 tag a Vice-Dale; Push Square documenta due punti su Shore Dr già presenti qui. Verifica il totale in Progressi → Collezioni → WAiNK, perché gli elenchi sono ancora in aggiornamento. ',
        '<a href="'+e(data["sources"]["noflusher_all"])+'" target="_blank" rel="noopener noreferrer">Repertorio delle 15 marcature ↗</a> · ',
        '<a href="'+e(data["sources"]["noflusher"])+'" target="_blank" rel="noopener noreferrer">Due luoghi descritti da Push Square ↗</a>.</p>',
        '<p>Scoperte subacquee: necessari 33 siti su 33, qui ancora solo sei',
        ' posizioni verificabili. Belpoint Strait e Bobcat Dive Site sono',
        ' siti con tesori Kenton, ma non incrementano il contatore 33/33. ',
        '<a href="'+e(data["sources"]["under"])+'" target="_blank" rel="noopener noreferrer">',
        'Consulta la guida subacquea originale ↗</a>.</p></section>',
        '<p class="cr-footer-note">Fonti riesaminate il 21 novembre 2026.',
        ' Nessuna coordinata inventata, nessuna mappa ingannevole.',
        ' Le spunte sono promemoria locali e non sbloccano trofei PSN.</p>',
        '</section>'
    ])
    return ''.join(output)
