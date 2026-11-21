"""Sourced location / screenshot coverage panels for the 11 GTA VI guides.

No invented map coordinates or rehosted video. Photo counts use the same
verified, locally optimized evidence logic as the existing screenshot hub.
"""
from __future__ import annotations

from html import escape
from urllib.parse import urlsplit
import re

from photo_request_hub_v1 import screenshot_count

BASE="https://xfederiko11.github.io/gta-6/"
HUB_PATH="mappe-guide/"
HOSTS={"www.gtabase.com","www.powerpyx.com","insider-gaming.com",
       "www.videogameschronicle.com"}
KINDS={"map-category","source-guide"}
PRECISION={"category","described","no-fixed-location"}


def e(value):
    return escape(str(value), quote=True)


def validate(guides, locations, meditations):
    ids={g["id"] for g in guides}
    if locations.get("schema")!="gta6-verified-location-references-v2":
        raise ValueError("Unsupported location reference schema")
    items=locations.get("guides",{})
    if ids!=set(items) or len(ids)!=11:
        raise ValueError("Location atlas must cover exactly all published guides")
    for ident,entries in items.items():
        if not isinstance(entries,list) or not 1<=len(entries)<=12:
            raise ValueError("Guide locations must have documented entries")
        for item in entries:
            if item.get("kind") not in KINDS or item.get("precision") not in PRECISION:
                raise ValueError("Unknown map reference kind or precision")
            for key in ("name","where","note"):
                content=item.get(key)
                if not isinstance(content,str) or len(content)<12 and key!="name" or len(content)>340:
                    raise ValueError("Invalid map reference description")
            target=urlsplit(item.get("url",""))
            if (target.scheme!="https" or target.hostname not in HOSTS
                or target.username or target.password or target.port not in (None,443)
                or target.fragment):
                raise ValueError("Map source must be a supported direct HTTPS URL")
            if item["kind"]=="map-category" and target.hostname!="www.gtabase.com":
                raise ValueError("Map category requires GTABase")
            if item["precision"]=="category" and item["kind"]!="map-category":
                raise ValueError("Category precision requires a map link")
    if meditations.get("total_locations")!=10 or len(meditations.get("spots",[]))!=10:
        raise ValueError("Ten meditation places required")
    return True


def entry_html(item):
    kind="Mappa filtrata esterna" if item["kind"]=="map-category" else "Fonte con descrizione del luogo"
    precision={"category":"Categoria, non un pin esatto",
               "described":"Orientamento testuale, non coordinate",
               "no-fixed-location":"Non è previsto un punto fisso"}[item["precision"]]
    return ('<li class="g-loc-item"><div class="g-loc-icon" aria-hidden="true">⌖</div>'
            '<div><strong>'+e(item["name"])+'</strong><p>'+e(item["where"])+'</p>'
            '<small>'+e(precision)+' · '+e(item["note"])+'</small>'
            '<a href="'+e(item["url"])+'" target="_blank" rel="noopener noreferrer">'
            +e(kind)+' ↗</a></div></li>')


def meditate_landmarks(meditations):
    rows=[]
    for n,spot in enumerate(meditations["spots"],1):
        label="⚠️ Capitolo 1" if spot.get("phase")=="chapter1" else (
            "🏁 Ultima tappa" if spot.get("phase")=="final" else
            "Jason + Lucia")
        rows.append(
            '<li><span class="g-loc-number">'+str(n).zfill(2)+'</span>'
            '<div><strong>'+e(spot["name"])+'</strong>'
            '<p>'+e(spot["region"])+' · '+e(spot["landmark"])+'</p>'
            '<small>'+e(label)+'</small></div></li>')
    return ('<div class="g-meditation-map"><h3>10 punti di orientamento per 18 sessioni</h3>'
            '<p>Landmark descritti nelle guide PowerPyx e Push Square: '
            'non sono pin geolocalizzati. Per spuntare le singole sessioni '
            '<a href="#meditazioni-checklist">usa la checklist dedicata ↓</a>.</p>'
            '<ol>'+''.join(rows)+'</ol></div>')


def render_guide(g, data, meditations):
    records=data["guides"].get(g["id"],[])
    if not records: raise ValueError("No map references for guide")
    inner=('<p>I collegamenti rimandano a <strong>mappe filtrate di terzi</strong> o '
           'a <strong>fonti descrittive</strong>. Non sono screenshot di gioco '
           'acquisiti dal nostro sito e non fingono di indicare coordinate precise.</p>'
           '<ul class="g-loc-list">'+''.join(entry_html(x) for x in records)+'</ul>')
    if g["id"]=="meditazione-capitolo-1":
        inner+=meditate_landmarks(meditations)
    if g.get("spoiler"):
        inner=('<details class="g-loc-spoiler"><summary>Apri luoghi e riferimenti '
               '(contiene spoiler)</summary>'+inner+'</details>')
    return ('<section class="g-location-panel" id="luoghi-mappe">'
            '<span class="v-kicker">⌖ LOCALIZZAZIONE E FONTI</span>'
            '<h2>Dove andare: luoghi e mappe</h2>'+inner+'</section>')


def render_hub(guides, data, media, extras, get_local):
    cards=[]
    for g in sorted(guides,key=lambda x:(0 if x["id"]=="meditazione-capitolo-1" else 1,
          x["safe_title"].casefold())):
        local=screenshot_count(g,media,extras,get_local)
        links=''.join(entry_html(x) for x in data["guides"][g["id"]])
        # Curated authentic screenshots already downloaded by the normal build;
        # never use promotional art, remote hotlinks or unverifiable uploads.
        evidence=list(dict.fromkeys(
            [*g.get("step_media",{}).values(),
             *(x["key"] for x in extras.get(g["canonical_path"],{}).get("gallery",[]))]
        ))
        snapshots=[]
        for key in evidence:
            item=media.get(key)
            if not item or item.get("kind")!="screenshot":
                continue
            local_url=get_local(key)
            if not isinstance(local_url,str) or not local_url.startswith(BASE+"assets/visual/"):
                continue
            snapshots.append(
                '<figure><a href="'+e(local_url)+'" target="_blank" rel="noopener noreferrer">'
                '<img src="'+e(local_url)+'" alt="'+e(item["alt"])+'" loading="lazy" '
                'decoding="async" width="960" height="540" data-map-guide-screenshot="'+e(key)+'"></a>'
                '<figcaption>'+e(item["caption"])+' '
                '<a href="'+e(item["source"])+'" target="_blank" rel="noopener noreferrer">'
                +e(item["credit"])+' · fonte ↗</a></figcaption></figure>'
            )
            if len(snapshots)>=2: break
        previews=('<div class="g-map-preview">'+''.join(snapshots)+'</div>' if snapshots else
                  '<p class="g-map-preview-empty">📸 Screenshot del passaggio non ancora disponibile. '
                  'Nessun render viene sostituito a una prova di gameplay.</p>')
        if g.get("spoiler") and snapshots:
            previews=('<details class="g-map-photo-details"><summary>Apri screenshot '
                      '(possibili spoiler)</summary>'+previews+'</details>')
        cards.append(
            '<article class="g-map-card" data-location-guide="'+e(g["id"])+'" '
            'data-screenshot-count="'+str(local)+'">'
            '<span class="v-kicker">'+e(g["tag"])+' · '+str(local)+'/5 schermate gameplay</span>'
            '<h2>'+e(g["safe_title"])+'</h2>'
            '<p>'+e(g.get("location","Segui i riferimenti documentati nella guida."))+'</p>'
            +previews+
            '<details><summary>Apri i luoghi documentati ('+
            str(len(data["guides"][g["id"]]))+')</summary><ul class="g-loc-list">'+links+'</ul></details>'
            '<a class="g-map-guide" href="'+BASE+e(g["canonical_path"])+'#luoghi-mappe">'
            'Apri la guida con i riferimenti →</a></article>')
    return (
        '<section class="g-map-hub"><header class="g-map-hero">'
        '<span class="eyebrow">⌖ GTA VI ITALIA · MAPPE E POSIZIONI PS5</span>'
        '<h1>Mappe GTA 6: luoghi e screenshot delle guide</h1>'
        '<p>Trova l’area giusta prima di seguire una procedura. '
        'Ogni riferimento distingue <strong>categoria sulla mappa</strong>, '
        '<strong>descrizione della fonte</strong> e screenshot di gameplay '
        'disponibili sul sito. Non creiamo coordinate o spawn non verificati.</p>'
        '<p class="g-map-hub-caution"><strong>Importante:</strong> una mappa di '
        'categoria non significa che tutti i punti elencati abbiano pin precisi. '
        'I filmati, i render promozionali e le richieste della community non '
        'contano come screenshot autentici.</p>'
        '<nav class="g-map-links" aria-label="Guide e checklist">'
        '<a class="v-button" href="'+BASE+'screenshot-ps5/">Contribuisci con screenshot PS5 →</a>'
        '<a class="v-button secondary" href="'+BASE+'trofei/roadmap-platino/#guida-55-trofei">'
        'Roadmap di tutti i 55 trofei →</a><a class="v-button secondary" href="'+BASE+'collezionabili/percorsi/">Percorsi collezionabili per area →</a></nav>'
        '</header><div class="g-map-cards">'+''.join(cards)+'</div></section>'
    )
