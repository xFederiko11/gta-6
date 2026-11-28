"""Consent-first interactive maps: standard guides, vehicle guides, and trophies.

Official embed permissions:
  Vice Map: https://vice-map.com/embed (credit REQUIRED; marker= optional)
  GTA6.city: https://gta6.city/embed (keep brand/CC-BY 4.0 attribution)
No coordinates are generated, scraped or inferred from a textual landmark.
The map runs inside the reader's browser only after they explicitly press
'Carica mappa'; the provider may or may not have a selected named marker.
"""
from __future__ import annotations
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

BASE="https://xfederiko11.github.io/gta-6/"
PRIMARY="https://vice-map.com/embed/map"
SECONDARY="https://gta6.city/embed/map"
PRIMARY_FULL="https://vice-map.com/map"
SECONDARY_FULL="https://gta6.city/"
SCHEMA="gta6-interactive-maps-v1"
VERSION="2026-11-28"
PROVIDERS=(
    {"id":"vice","name":"Vice Map","embed":PRIMARY,"full":PRIMARY_FULL,
     "terms":"https://vice-map.com/embed","marker_query":True},
    {"id":"city","name":"GTA6.city","embed":SECONDARY,"full":SECONDARY_FULL,
     "terms":"https://gta6.city/embed","marker_query":False}
)
ID=re.compile(r"[a-z0-9-]{3,100}")
SAFE_PATH=re.compile(r"(?:[a-z0-9-]+/)+")
SOURCE_PRECISION={"category","described","no-fixed-location"}
# Source-described locations only: a provider search is never an exact pin.
VEHICLE_MAP_ARTICLES={
 "guide-e-tutorial/key-cloner/":{
   "title":"Hathaway Apartments, Ocean Beach",
   "point":{"name":"Hathaway Apartments","where":"Ocean Beach, Vice Beach · parcheggio della missione Clonin’ Keys, Makin’ GS","precision":"described"},
   "source":"https://www.gtabase.com/gta-6/missions/steal-the-zorrusso-for-randy",
   "source_label":"GTABase — luogo della missione e schermate originali"},
 "garage-gratuiti/domestic-timbers/":{
   "title":"Domestic Timbers, Balsero",
   "point":{"name":"Domestic Timbers","where":"Balsero, Vice City · garage indicato da Randy dopo Delivery Day","precision":"described"},
   "source":"https://www.gtabase.com/gta-6/properties/domestic-timbers",
   "source_label":"GTABase — scheda del garage con foto e mappa"},
}
REGISTRY_SCHEMA="gta6-verified-external-map-references-v1"
EXTERNAL_ALLOWED={
 "jasons-safehouse":"https://gtamap.io/?m=jasons-safehouse",
 "permit-keys":"https://gtamap.io/?m=permit-keys",
 "starlet-motel":"https://gtamap.io/gta-6-map/starlet-motel/",
 "key-lento":"https://gtamap.io/gta-6-map/key-lento/",
 "hamlet-area":"https://gtamap.io/?m=hamlet",
 "belpoint-area":"https://gtamap.io/?m=belpoint",
 "port-gellhorn-garages":"https://gtamap.io/gta-6-map/port-gellhorn/",
}
KINDS={"community-marker-permalink","community-region-permalink","location-detail-permalink"}



def e(value): return escape(str(value),quote=True)


def article_paths(guides,trophies):
    g={x["canonical_path"]:x["id"] for x in guides}
    t={"trofei/"+x["slug"]+"/" for x in trophies}
    if len(g)!=12 or len(t)!=55 or any(not SAFE_PATH.fullmatch(k) for k in [*g,*t]):
        raise ValueError("Exactly 12 guides and 55 trophy routes required")
    if set(g)&t: raise ValueError("Guide/trophy canonical overlap")
    return g,t


def validate(guides,trophies,locations,collectibles):
    g,t=article_paths(guides,trophies)
    if set(g.values())!=set(locations.get("guides",{})) or len(locations["guides"])!=12:
        raise ValueError("No invented/missing guide location data")
    count=0
    for path,ident in g.items():
        for point in locations["guides"][ident]:
            if point.get("precision") not in SOURCE_PRECISION:
                raise ValueError("Unknown precision")
            if not isinstance(point.get("name"),str) or not 3<=len(point["name"])<=110:
                raise ValueError("Invalid map search name")
            if point.get("precision")=="no-fixed-location" and point.get("kind")=="map-category":
                raise ValueError("Cannot promise a marker for an abstract mechanic")
            count+=1
    if count!=19:
        raise ValueError("Expected exactly 19 verified text/map references")
    points=collectibles.get("points",[])
    if len(points)!=157 or len({x["id"] for x in points})!=157:
        raise ValueError("Current catalog 157 must have unique IDs")
    if any(not isinstance(x.get("name"),str) or not 3<=len(x["name"])<=110 for x in points):
        raise ValueError("Cannot look up unknown collectible names")
    for provider in PROVIDERS:
        for key in ("embed","full","terms"):
            u=urlsplit(provider[key])
            if u.scheme!="https" or u.username or u.password or u.query or u.fragment or u.port not in (None,443):
                raise ValueError("Untrusted map provider URL")
    return {"schema":SCHEMA,"reviewed":VERSION,"guide_articles":len(g),
            "trophy_articles":len(t),"collectible_pages":1,"directory_pages":1,
            "garage_guide_articles_with_map":2,
            "additional_vehicle_guide_articles_with_map":1,
            "articles_with_map":len(g)+len(t)+1+len(VEHICLE_MAP_ARTICLES),
            "pages_with_interactive_map":len(g)+len(t)+3+len(VEHICLE_MAP_ARTICLES),
            "guide_location_descriptions":count,
            "collectible_descriptions":len(points),
            "exact_gameplay_coordinate_pairs_verified":0,
            "named_place_search_is_exact_pin":False,
            "external_maps_loaded_automatically":False,
            "providers":[{"name":x["name"],"embed":x["embed"],"terms":x["terms"]} for x in PROVIDERS],
            "source":"https://vice-map.com/embed ; https://gta6.city/embed",
            "policy":"User-activated third-party iframe. Named search only; a label is not a proven marker or coordinate. Unofficial fan-made maps. Embedded maps are externally hosted and must keep original attribution. No paid APIs, map rehosting, PSN tracking or follower assertions."}


def _point(title,subtitle,precision):
    return {"name":title,"where":subtitle,"precision":precision}


def render_vehicle_map(path):
    """Compact native disclosure keeps the first numbered action in reach."""
    item=VEHICLE_MAP_ARTICLES[path]
    ident=path.rstrip("/").rsplit("/",1)[-1]
    return ('<details class="v-map-spoiler" data-vehicle-map-disclosure>'
            '<summary>Posizione e mappa: '+e(item["title"])+'</summary>'
            '<p>Luogo descritto dalla fonte: <a href="'+e(item["source"])+
            '" target="_blank" rel="noopener noreferrer">'+e(item["source_label"])+
            ' ↗</a>. Segui il segnale della missione nella tua partita.</p>'+
            render(item["title"],[item["point"]],id_suffix=ident,page_label="tutorial")+
            '</details>')


def guide_points(guide,locations,meditations):
    rows=[]
    for item in locations["guides"][guide["id"]]:
        rows.append(_point(item["name"],item["where"],item["precision"]))
    if guide["id"]=="meditazione-capitolo-1":
        for item in meditations["spots"]:
            rows.append(_point(item["name"],item["region"]+" · "+item["landmark"],"described"))
    return rows[:23]


def trophy_points(number,route,collectibles):
    """Only source-backed suggestions: chapter tasks have no inferred pin."""
    group=route.get("group")
    if number==28:
        return [_point("Jason’s House","Key Lento · potenziale attività di meditazione mancabile nel Capitolo 1","described")]
    if group=="collezionabili":
        samples=[x for x in collectibles["points"] if x.get("missable")]
        return [_point(x["name"],x["place"],"described") for x in samples[:2]]
    return []


def collectible_points(collectibles):
    items=[x for x in collectibles["points"] if x.get("missable") or x.get("location_limited")]
    items.extend(
        next((x for x in collectibles["points"] if x.get("type")==typ),None)
        for typ in ("waink","stunt","underwater","magazines","vehicles")
    )
    # No exact map markers: these are source-described examples only.
    unique=[];seen=set()
    for item in items:
        if item is not None and item["id"] not in seen:
            unique.append(_point(item["name"],item["place"],"described"))
            seen.add(item["id"])
    return unique[:12]


def validate_curated_external_refs(registry,guides,trophies,collectibles):
    """Source-scoped external permalink evidence, NOT exact GTA VI coordinates."""
    if registry.get("schema")!=REGISTRY_SCHEMA:
        raise ValueError("Unreviewed external map registry")
    entries=registry.get("items")
    if not isinstance(entries,list) or len(entries)!=len(EXTERNAL_ALLOWED):
        raise ValueError("External map registry must be deliberately reviewed")
    guide_ids={x["id"] for x in guides}
    trophies_set={x["number"] for x in trophies}
    point_ids={x["id"] for x in collectibles["points"]}
    results=[]
    for row in entries:
        ident=row.get("id")
        if ident not in EXTERNAL_ALLOWED or row.get("url")!=EXTERNAL_ALLOWED[ident]:
            raise ValueError("Untrusted external map permalink")
        if row.get("kind") not in KINDS or row.get("in_game_coordinate_verified") is not False:
            raise ValueError("Community pin is not PS5-verified GPS")
        if any(not isinstance(row.get(key),str) or not 4<=len(row[key])<=180
               for key in ("place","label","source_page")):
            raise ValueError("Incomplete source reference")
        if not row["source_page"].startswith("https://gtamap.io/"):
            raise ValueError("Untrusted map reference origin")
        if not isinstance(row.get("guide_ids"),list) or not set(row["guide_ids"])<=guide_ids:
            raise ValueError("Unknown guide linked to map pin")
        if not isinstance(row.get("trophy_numbers"),list) or not set(row["trophy_numbers"])<=trophies_set:
            raise ValueError("Unknown trophy linked to map pin")
        if not isinstance(row.get("checkpoint_ids"),list) or not set(row["checkpoint_ids"])<=point_ids:
            raise ValueError("Unknown collectible linked to map pin")
        if row.get("kind")=="community-marker-permalink" and ident!="jasons-safehouse":
            raise ValueError("Only Jason's building has an indexed direct marker")
        results.append(row)
    if {x["id"] for x in results}!=set(EXTERNAL_ALLOWED):
        raise ValueError("Duplicate or missing community map links")
    required_scopes={
        "hamlet-area":("community-region-permalink","town-area",[],["soldi-facili-capitolo-1"]),
        "belpoint-area":("community-region-permalink","coastal-area",["pt-122"],[]),
        "port-gellhorn-garages":("location-detail-permalink","town-information",[],["registrare-auto-personale"])}
    for ident,(typ,scope,checkpoints,guideids) in required_scopes.items():
        row=next(x for x in results if x["id"]==ident)
        if (row["kind"]!=typ or row["scope"]!=scope or
            row["checkpoint_ids"]!=checkpoints or row["guide_ids"]!=guideids or
            row["trophy_numbers"]):
            raise ValueError("External region source cannot be promoted to an exact point")
    if sum(x["kind"]=="community-marker-permalink" for x in results)!=1:
        raise ValueError("Do not claim multiple direct map markers")
    if sum(x["kind"]=="community-region-permalink" for x in results)!=3:
        raise ValueError("Exactly three source-indexed area links, NOT item markers")
    if sum(x["kind"]=="location-detail-permalink" for x in results)!=3:
        raise ValueError("Exactly three informational town/building pages")
    return {"external_map_references_reviewed":len(results),
            "external_community_building_markers":1,
            "external_community_region_links":3,
            "external_location_detail_links":3,
            "exact_gameplay_coordinate_pairs_verified":0,
            "individual_collectible_pins_verified":0,
            "external_link_verification":"indexed_public_source_not_in_game_or_live_api",
            "warning":"A place/building marker is not a collectible-specific pin."}


def external_refs_for(registry,*,guide=None,trophy=None,checkpoints=None):
    checkpoint_set=set(checkpoints or ())
    matched=[]
    for row in registry["items"]:
        if (guide in row["guide_ids"] if guide is not None else False) or (
            trophy in row["trophy_numbers"] if trophy is not None else False) or (
            bool(checkpoint_set.intersection(row["checkpoint_ids"]))):
            matched.append(row)
    return matched


def render_curated_refs(refs):
    if not refs:return ""
    rows=[]
    for row in refs:
        if row["id"] not in EXTERNAL_ALLOWED or row["url"]!=EXTERNAL_ALLOWED[row["id"]]:
            raise ValueError("Unvalidated external map link")
        rows.append('<li><a data-vim-curated-link data-umami-event="game-map-curated-link-open-intent" href="'+
                    e(row["url"])+'" target="_blank" rel="noopener noreferrer">'+
                    e(row["label"])+' ↗</a><small>Fonte: GTA Map · '+
                    e({"community-marker-permalink":"marker esterno di un edificio",
                        "community-region-permalink":"area geografica esterna",
                        "location-detail-permalink":"scheda di località"}[row["kind"]])+
                    '. Nessuna coordinata del singolo oggetto confermata.</small></li>')
    return ('<aside class="vim-curated"><h3>📍 Riferimenti geografici con permalink</h3>'
            '<p>I collegamenti portano al luogo o alla zona sulla mappa della community: '
            'non sono pin esatti per carte, riviste o altri oggetti.</p><ul>'+
            ''.join(rows)+'</ul></aside>')


def render(title,points=(),*,id_suffix="article",page_label="articolo",curated_refs=()):
    if not ID.fullmatch(id_suffix):
        raise ValueError("Unsafe map id")
    if len(points)>23:
        raise ValueError("Cannot overload map with unreviewed markers")
    rows=[]
    for i,item in enumerate(points,1):
        name=item.get("name")
        where=item.get("where","")
        precision=item.get("precision")
        if precision not in SOURCE_PRECISION or not isinstance(name,str) or not 3<=len(name)<=110 or not isinstance(where,str) or len(where)>260:
            raise ValueError("Unreviewed map reference")
        if precision=="no-fixed-location":
            rows.append('<li class="vim-location vim-no-point"><strong>'+e(name)+
                        '</strong><span>Non ha una posizione fissa; consulta la procedura.</span></li>')
        else:
            rows.append('<li class="vim-location"><button type="button" data-vim-seek="'+e(name)+'" '
                        'aria-label="Cerca '+e(name)+' nella mappa esterna">'+
                        '<strong>'+str(i).zfill(2)+' · '+e(name)+'</strong>'
                        '<span>'+e(where)+'</span>'
                        '<small>Ricerca nominale del provider: non è un pin esatto verificato</small>'
                        '</button></li>')
    if not rows:
        rows=['<li class="vim-no-point">Nessun punto fisso verificato per questo '+e(page_label)+
              '. Puoi comunque esplorare liberamente Leonida, ma non esiste un marker ufficiale associato.</li>']
    return (
        '<section class="vim-root" data-vi-map data-map-context="'+e(id_suffix)+'" id="mappa-interattiva">'
        '<header class="vim-head"><span class="v-kicker">🗺️ MAPPA INTERATTIVA · LEONIDA</span>'
        '<h2>Esplora sulla mappa: '+e(title)+'</h2>'
        '<p>Trascina e ingrandisci la mappa di GTA VI. Le etichette qui sotto sono luoghi '
        'descritti nelle nostre fonti: la ricerca per nome <strong>non certifica '
        'la posizione esatta</strong>, né l’esistenza del pin presso il fornitore.</p></header>'
        '<div class="vim-tools"><div class="vim-provider-tabs" role="group" aria-label="Fornitore mappa">'
        '<button type="button" data-vim-provider="vice" aria-pressed="true">Vice Map</button>'
        '<button type="button" data-vim-provider="city" aria-pressed="false">GTA6.city</button>'
        '</div><button type="button" class="vim-load" data-vim-load aria-controls="vim-frame-'+e(id_suffix)+'">'
        '🗺️ Carica mappa interattiva</button></div>'
        '<p class="vim-status" data-vim-status role="status" aria-live="polite">'
        'Mappa esterna non caricata. Aprila solo se vuoi trasferire la visita a un altro sito.</p>'
        '<div id="vim-frame-'+e(id_suffix)+'" class="vim-frame" data-vim-frame>'
        '<div class="vim-placeholder"><span aria-hidden="true">⌖</span>'
        '<strong>Vice City e Leonida</strong><p>Zoom e trascinamento dopo il caricamento volontario.</p></div>'
        '</div><div class="vim-meta"><a data-vim-full href="'+PRIMARY_FULL+'" '
        'target="_blank" rel="noopener noreferrer">Apri Vice Map a schermo intero ↗</a>'
        '<span>Mappe non ufficiali; alcune posizioni e categorie sono stime della community.</span></div>'
        '<details class="vim-places" open><summary>Luoghi collegati a questa guida ('+str(len(points))+')</summary>'
        '<ol>'+''.join(rows)+'</ol></details>'+render_curated_refs(curated_refs)+
        '<p class="vim-credit">Mappa ospitata e mantenuta da <a href="https://vice-map.com/" '
        'target="_blank" rel="noopener noreferrer">Vice Map</a> o '
        '<a href="https://gta6.city/" target="_blank" rel="noopener noreferrer">GTA6.city</a>. '
        'Crediti originali preservati. GTA VI appartiene a Rockstar Games. '
        'La mappa non sincronizza salvataggi o trofei PSN.</p>'
        '<p class="vim-follow"><a data-vim-follow href="https://x.com/intent/follow?screen_name=xFederiko11" '
        'target="_blank" rel="noopener noreferrer">𝕏 Segui GTA VI Italia per nuovi percorsi verificati ↗</a></p>'
        '</section>'
    )


def as_json(data):
    if data.get("schema")!=SCHEMA or data.get("pages_with_interactive_map")!=71:
        raise ValueError("Cannot export invalid map rollout")
    return json.dumps(data,ensure_ascii=False,indent=2)+"\n"
