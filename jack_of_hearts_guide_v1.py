"""Source-backed Jack of Hearts route article; YouTube remains opt-in only."""
from __future__ import annotations

from collections import defaultdict
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json

GUIDE_PATH="guide-e-tutorial/jack-of-hearts-36-cards/"
VIDEO_ID="LTbw8B0DQHA"
REGIONS=("mariana","vice-dale","leonard","kelly","lummox")
REGION_NAMES={"mariana":"Mariana County","vice-dale":"Vice-Dale County","leonard":"Leonard County","kelly":"Kelly County","lummox":"Lummox County"}
VIDEO_RECORDS={"pt-12":"jack-hearts-video-card-3","pt-32":"jack-hearts-video-card-13"}
EXPECTED_MOMENTS={"pt-12":577,"pt-32":1183}


def _e(value):
    return escape(str(value),quote=True)


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(routes,video,registry):
    if routes.get("schema")!="gta6-region-routes-v8":
        raise ValueError("Unexpected collectible route catalog")
    cards=[p for p in routes.get("points",[]) if p.get("card_set")=="jack-of-hearts"]
    if (len(cards)!=36 or {p.get("card_number") for p in cards}!=set(range(1,37))
            or {p.get("source_order") for p in cards}!=set(range(1,37))):
        raise ValueError("Jack of Hearts article requires all 36 distinct menu cards")
    if any(p.get("source")!="jack" or p.get("confidence")!="described" or p.get("region") not in REGIONS for p in cards):
        raise ValueError("Jack of Hearts point lacks a documented source description")
    if any(any(k in p for k in ("lat","lng","coordinates","duration_minutes","distance_km")) for p in cards):
        raise ValueError("The article cannot invent GPS or travel measures")
    source=urlsplit(routes.get("sources",{}).get("jack",""))
    if source.scheme!="https" or source.hostname!="www.powerpyx.com":
        raise ValueError("Jack of Hearts route source is not allowlisted")
    if video.get("youtube_id")!=VIDEO_ID or set(video.get("moments",{}))!=set(EXPECTED_MOMENTS):
        raise ValueError("Jack of Hearts video chapter catalog changed")
    for point,seconds in EXPECTED_MOMENTS.items():
        if video["moments"][point].get("at")!=seconds:
            raise ValueError("Unreviewed Jack of Hearts video timestamp")
    if urlsplit(video.get("source_url","")).hostname not in {"www.youtube.com","youtube.com"}:
        raise ValueError("Untrusted video source")
    media={x.get("id"):x for x in registry.get("items",[])}
    for point,ident in VIDEO_RECORDS.items():
        item=media.get(ident)
        if (not item or item.get("article_path")!=GUIDE_PATH or item.get("point_id")!=point
                or item.get("timestamp")!=EXPECTED_MOMENTS[point]
                or item.get("rights_status")!="youtube_platform_embed_only"
                or "site_opt_in_embed" not in item.get("allowed_channels",[])
                or "site_external_link" not in item.get("allowed_channels",[])
                or not any("Non scaricare" in x for x in item.get("restrictions",[]))):
            raise ValueError("Missing scoped YouTube player record for "+point)
    return sorted(cards,key=lambda p:p["source_order"])


def _video(moment,point,video):
    seconds=moment["at"]
    stamp=f"{seconds//60}:{seconds%60:02d}"
    source=video["source_url"]+"&t="+str(seconds)+"s"
    special=(" L'etichetta pubblica «Malena - Deep Red» non è stata verificata come equivalente "
             "a «Malena (Rosso)»: usa il video solo per confronto, non come conferma del luogo."
             if point=="pt-32" else
             " Il capitolo è un riferimento dichiarato dal creator, non una verifica indipendente del percorso.")
    return (
        '<div class="v-step-video" data-step-video-id="'+_e(video["youtube_id"])+'" data-step-video-seconds="'+str(seconds)+'">'
        '<button type="button" class="v-step-video-open" data-step-video-open hidden aria-label="Apri il capitolo video '+stamp+'">'
        '<span class="v-step-video-play" aria-hidden="true">▶</span><span><strong>Video di confronto</strong>'
        '<small>GTA Series Videos · capitolo '+_e(stamp)+' · si carica solo dopo il clic</small></span></button>'
        '<div class="v-step-video-slot" data-step-video-slot aria-live="polite"></div>'
        '<p class="v-step-video-note">Player YouTube opt-in; nessuna miniatura o fotogramma copiato.'
        +_e(special)+' <a href="'+_e(source)+'" target="_blank" rel="noopener noreferrer">Fonte video al minuto '+_e(stamp)+' ↗</a></p></div>'
    )


def render(url):
    routes=_load("data/collectible_routes_v4.json")
    video=_load("data/collectible_video_refs_v1.json")
    registry=_load("data/editorial_media_registry_v1.json")
    cards=validate(routes,video,registry)
    grouped=defaultdict(list)
    for card in cards:
        grouped[card["region"]].append(card)
    output=[
        '<section class="v-jack-card-route" id="jack-of-hearts-route" aria-labelledby="jack-of-hearts-title">',
        '<span class="v-kicker">36 CARTE · 5 REGIONI</span>',
        '<h2 id="jack-of-hearts-title">Dove trovare le 36 carte Jack of Hearts</h2>',
        '<p>Ogni tappa distingue l’ordine del percorso dal numero della carta nel menu Progressi. '
        'Le descrizioni sono basate sulla fonte originale e sull’atlante interno: non sono coordinate '
        'GPS né prove PS5 raccolte dal nostro team.</p>',
        '<p><a href="'+_e(url("collezionabili/percorsi/"))+'">Apri l’atlante regionale con checklist locale →</a> · '
        '<a href="'+_e(url("video-tutorial/"))+'">Apri l’hub dei video opt-in →</a></p>',
        '<nav class="jack-region-nav" aria-label="Vai alla contea">'
    ]
    for region in REGIONS:
        if grouped.get(region):
            output.append('<a href="#jack-region-'+region+'">'+_e(REGION_NAMES[region])+' · '+str(len(grouped[region]))+'</a>')
    output.append('</nav>')
    for region in REGIONS:
        section=grouped.get(region,[])
        if not section:
            continue
        output.append('<section class="jack-region" id="jack-region-'+region+'"><h3>'+_e(REGION_NAMES[region])+'</h3><ol>')
        for point in section:
            order=point["source_order"]
            number=point["card_number"]
            output.append(
                '<li class="jack-card-item" id="jack-card-'+str(order)+'" data-source-order="'+str(order)+'" '
                'data-menu-card="'+str(number)+'"><h4>Tappa '+str(order)+' · carta menu #'+str(number)+': '+_e(point["name"])+'</h4>'
                '<p class="jack-card-place"><strong>Landmark:</strong> '+_e(point["place"])+'</p>'
                '<p>'+_e(point["hint"])+'</p>'
                '<a href="'+_e(url("collezionabili/percorsi/")+"#cr-"+point["id"])+'">Apri il checkpoint nell’atlante →</a>'
            )
            moment=video.get("moments",{}).get(point["id"])
            if moment:
                output.append(_video(moment,point["id"],video))
            output.append('</li>')
        output.append('</ol></section>')
    output.extend([
        '<p class="jack-route-source">Fonte del percorso e dei landmark: '
        '<a href="'+_e(routes["sources"]["jack"])+'" target="_blank" rel="noopener noreferrer">PowerPyx · tutte le 36 carte Jack of Hearts ↗</a>. '
        'La fonte ordina le tappe per prossimità, non per il numero del menu.</p>',
        '<p class="jack-route-limit">Il video GTA Series Videos offre due etichette di capitolo pubbliche; '
        'la riproduzione e le corrispondenze con i luoghi non sono state verificate autonomamente.</p>',
        '</section>'
    ])
    return "".join(output)
