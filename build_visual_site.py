#!/usr/bin/env python3
"""Production visual layer. Retains every existing canonical URL and source data.
No generated gameplay imagery, invented popularity, account credentials or API calls.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlencode
import xml.etree.ElementTree as ET

import build_site as legacy
import site_info
import editorial_articles
import patch_archive_v1
import cinematic_site
import garage_guides_v1 as garage_guides
import vehicle_progression_guides_v1 as vehicle_progression
import article_chronology_v1 as chronology
from visual_guide_content import enrich
from operational_brief_v1 import validate as validate_operational_briefs, render as render_operational_brief
from waink_visual_v1 import intro as render_waink_intro, step as render_waink_step
from moses_vehicle_jobs_v1 import render as render_moses_jobs, validate as validate_moses_jobs, PATH as MOSES_JOBS_PATH
from community_social_v1 import home_rail
from meditation_tracker_v1 import render as render_meditation_tracker
from x_growth_dashboard_v1 import (render as render_growth_dashboard, read_report as growth_report,
                                   to_json as export_growth_report, PATH as GROWTH_PATH)
from photo_request_hub_v1 import render as render_photo_hub
from photo_coverage_v5 import audit as audit_photo_coverage, render as render_photo_coverage, json_report as export_photo_coverage, PATH as PHOTO_COVERAGE_PATH
from platinum_roadmap_v1 import render as render_platinum_roadmap, ROADMAP_PATH
from guide_step_references_v1 import render as render_step_evidence, validate as validate_step_evidence
from step_image_sources_v1 import load as load_step_photo_sources, validate as validate_step_photo_sources, render as render_step_photo_source
from first_car_steps_v1 import validate as validate_first_car, render as render_first_car
from creator_video_hub_v1 import load as load_creator_videos, records as reviewed_creator_videos, render as render_creator_videos, PATH as CREATOR_VIDEO_PATH
from chapter1_money_steps_v1 import validate as validate_money, render as render_money
from rockstar_gallery_v1 import render as render_rockstar_gallery, validate as validate_rockstar_gallery, PATH as ROCKSTAR_GALLERY_PATH
from vehicle_catalog_v1 import (load as load_vehicle_catalog, validate as validate_vehicles,
    index_body as render_vehicle_index, pages as vehicle_pages, PATH as VEHICLE_PATH)
from platinum_atlas_v2 import render as render_trophy_atlas, validate as validate_trophy_atlas
from advanced_platinum_v3 import (render_100 as render_advanced_100, render_hard as render_advanced_hard,
                                  validate as validate_advanced, COLLECTIBLE_PATH, HARD_PATH)
from photo_provenance_v3 import render as render_photo_provenance, validate as validate_provenance, PATH as PROVENANCE_PATH
from collectible_routes_v4 import render as render_collectible_routes, validate_routes, PATH as COLLECTIBLE_ROUTE_PATH
from collectible_photo_evidence_v1 import validate as validate_collectible_photos
from photo_intake_v4 import (render as render_photo_intake, validate_approved,
                              render_approved_for_guide, render_approved_for_step, approved_count, PATH as PHOTO_INTAKE_PATH)
from guide_location_atlas_v2 import (render_hub as render_map_hub, render_guide as render_guide_locations,
                                     validate as validate_map_references, HUB_PATH as MAP_HUB_PATH)
from interactive_article_maps_v1 import (render as render_interactive_map, validate as validate_interactive_maps,
                                         guide_points as interactive_guide_points, trophy_points as interactive_trophy_points,
                                         collectible_points as interactive_collectible_points,
                                         as_json as export_map_rollout,validate_curated_external_refs,
                                         external_refs_for)

e=legacy.e
url=legacy.url
BASE=legacy.BASE
OUT=legacy.OUT
ORIGINAL_LAYOUT=legacy.layout
ORIGINAL_SOURCES=site_info.sources_for
MEDIA=json.loads(Path('data/visual_media.json').read_text(encoding='utf-8'))['images']
PHOTO_STEP_REVIEW=json.loads(Path('data/tutorial_photo_review.json').read_text(encoding='utf-8'))
PHOTO_SOURCE_REFS=load_step_photo_sources()
if PHOTO_STEP_REVIEW.get('schema')!='gta6-tutorial-photo-review-v2':
    raise ValueError('Invalid audited step-photo schema')
VISUAL_REQUESTS=json.loads(Path('data/visual_requests.json').read_text(encoding='utf-8'))['guides']
VISUAL_EVIDENCE=json.loads(Path('data/guide_visual_refs.json').read_text(encoding='utf-8'))
STEP_EVIDENCE=json.loads(Path('data/guide_step_refs.json').read_text(encoding='utf-8'))
TROPHY_ROUTES=json.loads(Path('data/platinum_trophy_routes_v2.json').read_text(encoding='utf-8'))
LOCATION_REFS=json.loads(Path('data/guide_locations_v2.json').read_text(encoding='utf-8'))
MEDITATION_PLACES=json.loads(Path('data/meditation_checklist_v1.json').read_text(encoding='utf-8'))
EXTERNAL_MAP_REFS=json.loads(Path('data/map_external_permalinks_v1.json').read_text(encoding='utf-8'))
ADVANCED=json.loads(Path('data/advanced_platinum_v3.json').read_text(encoding='utf-8'))
PHOTO_REVIEW=json.loads(Path('data/photo_provenance_review_v3.json').read_text(encoding='utf-8'))
OPERATIONAL_BRIEFS=json.loads(Path('data/guide_operational_briefs_v1.json').read_text(encoding='utf-8'))
COLLECTIBLE_ROUTES=json.loads(Path('data/collectible_routes_v4.json').read_text(encoding='utf-8'))
COLLECTIBLE_PHOTOS=json.loads(Path('data/collectible_photo_evidence_v1.json').read_text(encoding='utf-8'))
APPROVED_PHOTOS=json.loads(Path('data/approved_screenshots_v4.json').read_text(encoding='utf-8'))
TROPHY_ITEMS=json.loads(Path('data/trofei.json').read_text(encoding='utf-8'))['trophies']
TROPHY_MAP_PATHS={'trofei/'+row['slug']+'/':row for row in TROPHY_ITEMS}
GUIDE_MAP_PATHS=set()
MAP_RENDER_PATHS=set(TROPHY_MAP_PATHS)|{MAP_HUB_PATH,COLLECTIBLE_ROUTE_PATH}
# Legacy manifest is link-only; never trust cached provider derivatives.
ASSET_VERSION=hashlib.sha256(b''.join(Path(p).read_bytes() for p in ('site/assets/visual-v2.css','site/assets/visual-v2.js'))).hexdigest()[:12]
DESIGN_VERSION='visual-v2-20261120'


def brand():
    return '<a class="v-brand" href="'+url()+'"><span class="v-mark" aria-hidden="true">VI</span><span><strong>GTA 6 / ITALIA</strong><small>Guide strategiche in italiano</small></span></a>'


def header(path):
    # Three editorial destinations: guide ≠ community report ≠ other tools.
    primary=[('Home',''),('Guide','guide-e-tutorial/'),('Trofei','trofei/'),('Scoperte','scoperte/')]
    secondary=[('Soldi facili','soldi-facili/'),('Cerca un veicolo','veicoli/'),
               ('Salvare auto','salvare-auto/'),('Glitch','glitch/'),('Garage gratuiti',garage_guides.PATH),('Collezionabili','collezionabili/percorsi/'),
               ('Mappe','mappe-guide/'),('HDR OLED','hdr-oled/'),('Video tutorial','video-tutorial/'),('Articoli','articoli/'),('Patch','patch/'),('Immagini ufficiali','immagini-ufficiali/'),('Fonti e metodo','fonti/')]
    def link(label,target):
        current=' aria-current="page"' if path==target else ''
        return f'<a href="{url(target)}"{current}>{e(label)}</a>'
    main=''.join(link(*item) for item in primary)
    more=''.join(link(*item) for item in secondary)
    x_link=('<a class="v-x-link" href="https://x.com/intent/follow?screen_name=xFederiko11" '
            'target="_blank" rel="me noopener noreferrer" aria-label="Segui Federiko su X">'
            '<span aria-hidden="true">𝕏</span><span>Segui</span></a>')
    return ('<header class="v-header" id="inizio"><div class="wrap v-header-inner">'+brand()+
            '<nav class="v-nav" aria-label="Navigazione principale">'+main+
            '<details class="v-more"><summary>Altro</summary><div>'+more+'</div></details></nav>'+
            x_link+
            '<details class="v-menu"><summary aria-label="Apri il menu">Menu ☰</summary><nav aria-label="Navigazione mobile">'+main+more+'</nav></details></div></header>'+
            (('<div class="v-spoilerbar"><div class="wrap v-spoiler-inner">'
              '<p><strong>⚠️ Attenzione spoiler:</strong> proseguendo potresti leggere dettagli '
              'di missioni, luoghi e ricompense.</p></div></div>') if path else ''))

def footer():
    links=[('Roadmap platino','trofei/roadmap-platino/'),('Checklist 100%','trofei/100-percento/'),('Percorsi collezionabili','collezionabili/percorsi/'),('Trofei difficili','trofei/trofei-difficili/'),('Invia foto','screenshot-ps5/invia/'),('Mappe e luoghi','mappe-guide/'),('Soldi facili','soldi-facili/'),('Auto speciali','auto-speciali/'),('Salvare le auto','salvare-auto/'),('Garage gratuiti',garage_guides.PATH),('Tutte le guide','guide-e-tutorial/'),('Patch GTA VI','patch/'),('Trofei','trofei/'),('HDR OLED','hdr-oled/'),('Foto della community','screenshot-ps5/'),('Immagini Rockstar','immagini-ufficiali/'),('Video dei creator','video-tutorial/'),('Fonti e metodo','fonti/'),('Privacy e visite','privacy/')]
    return ('<footer class="v-footer"><div class="wrap"><div class="v-footer-grid"><div>'+brand()+
            '<p>Guide indipendenti per PS5 e PS5 Pro. Sintesi originali, schermate attribuite e avvisi spoiler. Non affiliato a Rockstar Games.</p></div><nav class="v-footer-links" aria-label="Link utili">'+
            ''.join(f'<a href="{url(p)}">{e(t)}</a>' for t,p in links)+
            '</nav></div><div class="v-footer-note"><span>Le guide possono contenere spoiler. Le schermate appartengono ai rispettivi titolari.</span><a href="https://x.com/xFederiko11" target="_blank" rel="me noopener noreferrer">𝕏 @xFederiko11</a></div></div></footer><a class="v-top" href="#inizio" aria-label="Torna all’inizio">↑</a>')


def layout(title,desc,path,body,section=None,image=None,robots='index,follow',structured=None):
    # Trophy article bodies are generated by the legacy site builder.
    # Attach a real interactive viewer to each of the 55 individual trophy pages
    # without inventing a trophy-specific geographic marker.
    if path in TROPHY_MAP_PATHS:
        trophy=TROPHY_MAP_PATHS[path]
        number=trophy['number']
        route=TROPHY_ROUTES['records'][number-1]
        body+=render_interactive_map(trophy['name'] if 'name' in trophy else trophy['slug'],
              interactive_trophy_points(number,route,COLLECTIBLE_ROUTES),
              id_suffix='trofeo-'+str(number),page_label='trofeo',
              curated_refs=external_refs_for(EXTERNAL_MAP_REFS,trophy=number))
    if path in ('salvare-auto/','veicoli/','guide-e-tutorial/','auto-speciali/','guide-e-tutorial/sportive-randy-posizioni/',garage_guides.BUY,garage_guides.VANESSA,garage_guides.BOBCAT,garage_guides.COQUETTE):
        body+=garage_guides.banner(BASE+'/')
    page=ORIGINAL_LAYOUT(title,desc,path,body,section,image,robots,structured)
    page=re.sub(r'<header class="site-header">.*?</header>',lambda _:header(path),page,count=1,flags=re.S)
    page=re.sub(r'<footer class="footer">.*?</footer>',lambda _:footer(),page,count=1,flags=re.S)
    page=page.replace('<body>',f'<body data-design-version="{DESIGN_VERSION}">',1)
    page=page.replace('</head>',f'<link rel="stylesheet" href="{url("assets/visual-v2.css")}?v={ASSET_VERSION}"><meta name="color-scheme" content="light"></head>',1)
    page=page.replace('</body>',f'<script src="{url("assets/visual-v2.js")}?v={ASSET_VERSION}" defer></script></body>',1)
    if path in ('', CREATOR_VIDEO_PATH):
        css='creator-video-hub-v1.css'
        version=hashlib.sha256(Path('site/assets',css).read_bytes()).hexdigest()[:12]
        page=page.replace('</head>',f'<link rel="stylesheet" href="{url("assets/"+css)}?v={version}"></head>',1)
    if path == CREATOR_VIDEO_PATH:
        js='creator-video-hub-v1.js'
        version=hashlib.sha256(Path('site/assets',js).read_bytes()).hexdigest()[:12]
        page=page.replace('</body>',f'<script src="{url("assets/"+js)}?v={version}" defer></script></body>',1)
    if path == '' or path.startswith(('articoli/','media/rockstar/','patch/','glitch/')):
        css='editorial-articles.css'
        version=hashlib.sha256(Path('site/assets',css).read_bytes()).hexdigest()[:12]
        page=page.replace('</head>',f'<link rel="stylesheet" href="{url("assets/"+css)}?v={version}"></head>',1)
    if path=='articoli/':
        js='article-chronology-v1.js'
        digest=hashlib.sha256(Path('site/assets',js).read_bytes()).hexdigest()[:12]
        page=page.replace('</body>',f'<script src="{url("assets/"+js)}?v={digest}" defer></script></body>',1)
    if path == '':
        css='site-focus-v1.css'
        version=hashlib.sha256(Path('site/assets',css).read_bytes()).hexdigest()[:12]
        page=page.replace('</head>',
            f'<link rel="stylesheet" href="{url("assets/"+css)}?v={version}"></head>',1)
    if path == GROWTH_PATH:
        css='x-growth-dashboard-v1.css'
        version=hashlib.sha256(Path('site/assets',css).read_bytes()).hexdigest()[:12]
        page=page.replace('</head>',f'<link rel="stylesheet" href="{url("assets/"+css)}?v={version}"></head>',1)
    if path in MAP_RENDER_PATHS or path in GUIDE_MAP_PATHS:
        css,js='interactive-map-v1.css','interactive-map-v1.js'
        version=hashlib.sha256(Path('site/assets',css).read_bytes()+Path('site/assets',js).read_bytes()).hexdigest()[:12]
        page=page.replace('</head>',f'<link rel="stylesheet" href="{url("assets/"+css)}?v={version}"></head>',1)
        page=page.replace('</body>',f'<script src="{url("assets/"+js)}?v={version}" defer></script></body>',1)
    if path==VEHICLE_PATH or path.startswith((VEHICLE_PATH,garage_guides.PATH)) or path in (vehicle_progression.CLONER,vehicle_progression.SELL):
        css,js='vehicle-finder-v1.css','vehicle-finder-v1.js'
        version=hashlib.sha256(
            Path('site/assets',css).read_bytes()+Path('site/assets',js).read_bytes()).hexdigest()[:12]
        page=page.replace('</head>',
            f'<link rel="stylesheet" href="{url("assets/"+css)}?v={version}"></head>',1)
        page=page.replace('</body>',
            f'<script src="{url("assets/"+js)}?v={version}" defer></script></body>',1)
    if path==ROCKSTAR_GALLERY_PATH:
        css,js='rockstar-gallery-v1.css','rockstar-gallery-v1.js'
        version=hashlib.sha256(
            Path('site/assets',css).read_bytes()+Path('site/assets',js).read_bytes()).hexdigest()[:12]
        page=page.replace('</head>',
            f'<link rel="stylesheet" href="{url("assets/"+css)}?v={version}"></head>',1)
        page=page.replace('</body>',
            f'<script src="{url("assets/"+js)}?v={version}" defer></script></body>',1)
    if path == PHOTO_COVERAGE_PATH:
        css,js='photo-coverage-v5.css','photo-coverage-v5.js'
        version=hashlib.sha256(Path('site/assets',css).read_bytes()+Path('site/assets',js).read_bytes()).hexdigest()[:12]
        page=page.replace('</head>',f'<link rel="stylesheet" href="{url("assets/"+css)}?v={version}"></head>',1)
        page=page.replace('</body>',f'<script src="{url("assets/"+js)}?v={version}" defer></script></body>',1)
    if path in (COLLECTIBLE_ROUTE_PATH,PHOTO_INTAKE_PATH):
        css,js=('collectible-routes-v4.css','collectible-routes-v4.js') if path==COLLECTIBLE_ROUTE_PATH else ('photo-intake-v4.css','photo-intake-v4.js')
        version=hashlib.sha256(Path('site/assets',css).read_bytes()+Path('site/assets',js).read_bytes()).hexdigest()[:12]
        page=page.replace('</head>',
            f'<link rel="stylesheet" href="{url("assets/"+css)}?v={version}"></head>',1)
        page=page.replace('</body>',
            f'<script src="{url("assets/"+js)}?v={version}" defer></script></body>',1)
    if path in (COLLECTIBLE_PATH,HARD_PATH):
        version=hashlib.sha256(
            b''.join(Path('site/assets',name).read_bytes() for name in
                     ('advanced-platinum-v3.css','advanced-platinum-v3.js'))
        ).hexdigest()[:12]
        page=page.replace('</head>',
            f'<link rel="stylesheet" href="{url("assets/advanced-platinum-v3.css")}?v={version}"></head>',1)
        if path == COLLECTIBLE_PATH:
            page=page.replace('</body>',
                f'<script src="{url("assets/advanced-platinum-v3.js")}?v={version}" defer></script></body>',1)
    if path == ROADMAP_PATH:
        version=hashlib.sha256(
            b''.join(Path('site/assets',name).read_bytes() for name in
                     ('platinum-roadmap.css','platinum-roadmap.js',
                      'platinum-atlas-v2.css','platinum-atlas-v2.js'))
        ).hexdigest()[:12]
        page=page.replace('</head>',(
            f'<link rel="stylesheet" href="{url("assets/platinum-roadmap.css")}?v={version}">'
            f'<link rel="stylesheet" href="{url("assets/platinum-atlas-v2.css")}?v={version}"></head>'
        ),1)
        page=page.replace('</body>',(
            f'<script src="{url("assets/platinum-roadmap.js")}?v={version}" defer></script>'
            f'<script src="{url("assets/platinum-atlas-v2.js")}?v={version}" defer></script></body>'
        ),1)
    return page


def media_src(key,width=960):
    """Legacy source references are never rendered as locally cached images."""
    return None


def unavailable_media(key):
    record=MEDIA[key]
    kind='Mappa' if 'mapp' in record['alt'].lower() else 'Schermata'
    return (f'<div class="v-missing-media" role="img" data-media-missing="{e(key)}" '
            f'aria-label="{e(kind)} non disponibile: {e(record["alt"])}">'
            '<span class="v-missing-icon" aria-hidden="true">▧</span>'
            f'<strong>{kind} non disponibile</strong>'
            '<small>La fonte originale è disponibile in fondo a questo riquadro.</small></div>')


def image(key,*,eager=False):
    record=MEDIA[key]
    original=media_src(key)
    if not original:
        return unavailable_media(key)
    extra=' loading="eager" fetchpriority="high"' if eager else ' loading="lazy"'
    source_480=media_src(key,480)
    srcset=(f' srcset="{e(source_480)} 480w, {e(original)} 960w" '
            'sizes="(max-width: 600px) 92vw, (max-width: 900px) 48vw, 600px"') if source_480 else ''
    if record['kind'] not in {'screenshot','promotional'}:
        raise ValueError('Unknown media provenance class')
    return f'<img class="v-photo" data-visual-image="{e(key)}" data-visual-kind="{e(record["kind"])}" src="{e(original)}"{srcset} alt="{e(record["alt"])}" width="960" height="540" decoding="async"{extra}>'


def figure(key,caption_override=None):
    """Show the verified cached photo, with a small direct source link below it."""
    record=MEDIA[key]
    photo=media_src(key)
    caption=record['caption'] if caption_override is None else caption_override
    credit=('<figcaption class="v-caption v-photo-attribution">'
            '<span class="v-photo-caption">'+e(caption)+'</span>'
            '<small class="v-photo-origin"><a href="'+e(record['source'])+'" '
            'target="_blank" rel="noopener noreferrer">Fonte foto: '
            +e(record['credit'])+' ↗</a></small></figcaption>')
    if not photo:
        return '<figure class="v-unavailable-figure">'+unavailable_media(key)+credit+'</figure>'
    return ('<figure class="v-verified-figure"><a class="v-image-link" href="'+e(photo)+'" '
            'data-image-source="'+e(record["source"])+'" target="_blank" rel="noopener noreferrer" '
            'aria-label="Ingrandisci: '+e(record["alt"])+'">'+image(key)+
            '<span class="v-image-label">Ingrandisci ↗</span></a>'+credit+'</figure>')


def visual_contribution(g):
    """Five clear requests for authentic PS5 evidence, never fake screenshots.

    Every suggested X post is an optional manual compose intent. Neither a
    submitted image nor redistribution permission is inferred from opening it.
    Hidden details protect location/mission spoilers in the requests.
    """
    requested=VISUAL_REQUESTS.get(g['id'])
    if not isinstance(requested,list) or len(requested)!=5:
        raise ValueError('Incomplete five-role visual request: '+g['id'])
    if any(not isinstance(item,str) or not 8<=len(item)<=150 for item in requested):
        raise ValueError('Invalid visual request')
    path=g['canonical_path']
    if not re.fullmatch(r'(?:[a-z0-9-]+/)+',path):
        raise ValueError('Invalid contribution guide path')

    # Only real, locally available step screenshots count towards the goal.
    # Hero art and promotional imagery never establish a gameplay step.
    screenshots={
        key for key in g['step_media'].values()
        if key in MEDIA and MEDIA[key]['kind']=='screenshot' and media_src(key)
    }
    count=len(screenshots)+approved_count(APPROVED_PHOTOS,g['id'])
    original='@xFederiko11 Ho uno screenshot PS5 originale utile a questa guida GTA VI: '+url(path)+' #GTA6Italia'
    target='https://x.com/intent/tweet?'+urlencode({'text':original})
    if len(original)>280:
        raise ValueError('Generic photo contribution exceeds X text limit')

    photo_rows=[]
    for index,role in enumerate(requested,1):
        # The five editorial photo roles are not automatically assigned to
        # numbered steps: a position shot is not proof of a later result.
        message='@xFederiko11 Screenshot PS5 GTA VI: '+role+'\n'+url(path)+' #GTA6Italia'
        if len(message)>280:
            raise ValueError('Photo contribution exceeds X text limit')
        link='https://x.com/intent/tweet?'+urlencode({'text':message})
        photo_rows.append(
            '<li class="v-visual-request-row">'
            '<span class="v-visual-request-number" aria-hidden="true">'+str(index).zfill(2)+'</span>'
            '<span class="v-visual-request-title">'+e(role)+'</span>'
            '<a href="'+e(link)+'" target="_blank" rel="noopener noreferrer" '
            'data-visual-request-photo="'+str(index)+'" '
            'aria-label="Proponi su X uno screenshot per: '+e(role)+'">Proponi su X ↗</a>'
            '</li>'
        )
    return (
        '<aside id="contributi-foto" class="v-visual-help" '
        'data-visual-request-id="'+e(g['id'])+'" '
        'aria-label="Schermate di gameplay e contributi della community">'
        '<div class="v-visual-help-head"><div><span class="v-kicker">𝕏 COMMUNITY · SCHERMATE PS5</span>'
        '<h2>Aiutaci a documentare ogni passaggio</h2>'
        '<p class="v-visual-coverage" data-visual-screenshot-count="'+str(count)+'">'
        '<strong>'+str(count)+'/5 screenshot</strong> di gameplay visibili '
        'nella guida e nella galleria (obiettivo editoriale; promozioni escluse).</p>'
        '<p>Fotografie autentiche di mappe, menu, azioni e risultati: mai mappe o '
        'ricompense ricostruite. Nessun account GitHub necessario.</p></div>'
        '<a class="v-button secondary" href="'+e(target)+'" '
        'target="_blank" rel="noopener noreferrer" data-visual-send-x>'
        '𝕏 Proponi uno screenshot</a></div>'
        '<details class="v-visual-request-details"><summary>Quali cinque screenshot ci servono?</summary>'
        '<ol class="v-visual-request-list">'+''.join(photo_rows)+'</ol>'
        '<p>Premi Crea (Create) su PS5 e allega <strong>manualmente</strong> '
        'l’immagine al post che aprirai su X. Indica PS5/PS5 Pro, patch se nota '
        'e avvisa degli spoiler. Pubblica solo immagini che puoi condividere. '
        'Per ripubblicarle sul sito ti chiederemo un permesso esplicito; '
        'un tweet non concede automaticamente una licenza. Nessun invio '
        'automatico né promessa di essere pubblicati.</p></details>'
        '<p class="v-visual-follow"><a href="https://x.com/intent/follow?screen_name=xFederiko11" '
        'target="_blank" rel="noopener noreferrer" data-visual-follow-x>'
        '𝕏 Segui @xFederiko11 per aggiornamenti verificati di questa guida ↗</a></p></aside>'
    )


def walkthrough_visuals(g):
    """Source-linked genuine gameplay clips and maps. Player loads only on click.

    This section never claims that videos are verified by our own playback.
    The verified timestamps and linked positions refer to independent sources.
    Videos do not count toward five locally verified screenshots.
    """
    ident=g['id']
    vid=VISUAL_EVIDENCE.get('guides',{}).get(ident)
    maps=VISUAL_EVIDENCE.get('maps',{})
    selected=[ident]
    if ident=='registrare-auto-personale':
        selected.append('salvare-auto-garages')
    map_refs=[maps[key] for key in selected if key in maps]
    if not vid and not map_refs:return ''
    out='<section class="v-reference-hub" id="riferimenti-visivi"><span class="v-kicker">FONTI VISIVE</span><h2>Vedi il percorso nel gameplay</h2>'
    out+='<p class="v-reference-intro">Solo video reali e mappe di terzi: nessuna posizione o schermata ricostruita artificialmente.</p>'
    for mp in map_refs:
        target=mp['url']
        parsed=urlsplit(target)
        if parsed.scheme!='https' or parsed.hostname!='www.gtabase.com' or parsed.username or parsed.password or parsed.port not in (None,443):
            raise ValueError('Unverified map URL')
        out+=('<div class="v-map-reference"><span aria-hidden="true">▤</span><div>'
              '<strong>Mappa interattiva del luogo</strong>'
              '<p>'+e(mp['caution'])+'</p>'
              '<a href="'+e(target)+'" target="_blank" rel="noopener noreferrer">'
              +e(mp['label'])+' ↗</a></div></div>')
    if vid:
        video_id=vid.get('youtube_id','')
        start=vid.get('start_seconds')
        if not isinstance(video_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{11}',video_id):
            raise ValueError('Invalid YouTube video identifier')
        if type(start) is not int or not 0<=start<=100000:
            raise ValueError('Invalid YouTube timestamp')
        source=vid.get('context_source','')
        u=urlsplit(source)
        # The meditation timestamps are published by the video's own creator.
        # Allow only this exact reviewed first-party video URL; other existing
        # source allowlists remain unchanged.
        direct_creator_source = (ident=='meditazione-capitolo-1'
                                 and video_id=='WZ9EM_i_W38'
                                 and source=='https://www.youtube.com/watch?v=WZ9EM_i_W38')
        if not direct_creator_source and (u.scheme!='https' or u.hostname not in ('trari.com','www.trari.com','www.dexerto.com')):
            raise ValueError('Unknown external video reference provenance')
        open_url='https://www.youtube.com/watch?v='+video_id+'&t='+str(start)+'s'
        out+=('<details class="v-video-reference"><summary>▶ '+e(vid['title'])+
              ' (attenzione: filmato con possibili spoiler)</summary>'
              '<div class="v-video-copy"><strong>Gameplay: '+e(vid['creator'])+'</strong>'
              '<p>'+e(vid['why'])+'</p>'
              '<div class="v-video-shell" data-youtube-id="'+e(video_id)+
              '" data-youtube-start="'+str(start)+'">'
              '<div class="v-video-embed" data-youtube-holder>'
              '<span class="v-video-play-art" aria-hidden="true">▶</span>'
              '<button type="button" data-load-youtube>▶ Riproduci video originale</button>'
              '<small>Il player YouTube viene caricato solo dopo il clic.</small></div></div>'
              '<div class="v-video-links"><a href="'+e(open_url)+'" target="_blank" rel="noopener noreferrer">Apri su YouTube dal punto utile ↗</a>')
        chapters=vid.get('chapters',[])
        if not isinstance(chapters,list) or len(chapters)>(10 if direct_creator_source else 5):
            raise ValueError('Invalid chapter reference set')
        out+='<ul>'
        for ch in chapters:
            sec=ch.get('at')
            if type(sec) is not int or not 0<=sec<=100000:
                raise ValueError('Invalid chapter timestamp')
            target='https://www.youtube.com/watch?v='+video_id+'&t='+str(sec)+'s'
            out+='<li><a href="'+e(target)+'" target="_blank" rel="noopener noreferrer">'+e(ch['label'])+'</a></li>'
        out+='</ul><a href="'+e(source)+'" target="_blank" rel="noopener noreferrer">Fonte della cronologia ↗</a></div>'
        out+='<p class="v-ref-caveat">Il video è del creator indicato, non di Rockstar Games. Se l’embed è bloccato, usa il link YouTube originale. I minuti sono quelli indicati dalla fonte, non una verifica personale del filmato.</p>'
        out+='</div></details>'
    return out+'</section>'


def reading_time(g):
    count=len((' '.join(g['steps'])+' '+g['summary']+' '+g.get('benefit','')+' '+g.get('caution','')).split())
    return max(1,round(count/180))


def card(g):
    """Illustrated discovery card; promotional photography is labelled separately."""
    return (
        f'<article class="v-guide-card v-guide-card-plain" data-category="{e(g["category"])}" '
        f'data-guide-searchable="{e(g["safe_title"]+" "+g["tag"]+" "+g["summary"])}">'
        f'<a href="{url(g["canonical_path"])}">'
        +cinematic_site.card_image(g,url)+
        '<div class="v-card-copy">'
        f'<span class="v-tag">{e(g["tag"])} · GUIDA PRATICA</span>'
        f'<h3>{e(g["safe_title"])}</h3><p>{e(g["summary"])}</p>'
        f'<div class="v-card-meta"><span>{len(g["steps"])} passaggi</span>'
        '<b>Apri il tutorial →</b></div></div></a></article>'
    )



def section_head(kicker,title,desc='',href=None):
    tail=f'<a href="{url(href)}">Tutte le guide →</a>' if href else ''
    return '<div class="v-section-head"><div>'+f'<span class="v-kicker">{e(kicker)}</span><h2>{e(title)}</h2>'+ (f'<p>{e(desc)}</p>' if desc else '')+'</div>'+tail+'</div>'


def categories():
    items=[('€','Soldi facili','Dove cercare e cosa raccogliere','soldi-facili/'),('↗','Auto speciali','Zone, richieste e veicoli','auto-speciali/'),('⌂','Salvare le auto','Registrazione e garage','salvare-auto/'),('★','Trofei e platino','Requisiti e checklist','trofei/roadmap-platino/')]
    return '<nav class="v-categories" aria-label="Scegli il tuo obiettivo">'+''.join(f'<a class="v-category" href="{url(p)}"><span class="v-icon" aria-hidden="true">{e(icon)}</span><span><strong>{e(t)}</strong><small>{e(d)}</small></span><span class="v-arrow" aria-hidden="true">→</span></a>' for icon,t,d,p in items)+'</nav>'


def home(guides):
    """A photographic route into the existing guides, trophies and discoveries."""
    return cinematic_site.home(guides,url).replace('<section class="ci-section ci-shell" id="scegli">', '<section class="ci-section ci-shell" id="scegli">'+chronology.render(url),1)+(
        '<section class="cv-home-link" aria-labelledby="cv-home-title">'
        '<h2 id="cv-home-title">🎬 Video dei creator, istruzioni italiane</h2>'
        '<p>Quattro video originali selezionati per auto, soldi e tecniche GTA VI. '
        'Scegli il minuto utile e apri la guida passo per passo: non serve cercare nel filmato.</p>'
        '<a href="'+url(CREATOR_VIDEO_PATH)+'">Scopri i video tutorial selezionati →</a>'
        '</section>')


def directory(guides,kind='all'):
    config={
        'all':('Guide GTA 6: scegli cosa fare','Tutti i percorsi in italiano. Cerca un obiettivo, apri una guida e segui i passaggi.','guide-e-tutorial/'),
        'soldi':('Soldi facili, percorsi chiari.','Luoghi e bottino del Capitolo 1. Controlla i rischi prima di partire: niente promesse di guadagni infiniti.','soldi-facili/'),
        'auto':('Trova l’auto. Poi tienila.','Richieste, ricerca dei veicoli e garage: scegli il percorso giusto senza confondere consegna e conservazione.','auto-speciali/'),
    }
    title,desc,path=config[kind]
    selected=guides if kind=='all' else [g for g in guides if g['category']==kind or (kind=='auto' and g['category']=='garage')]
    body=legacy.crumbs([(title,path)])+f'<section class="v-directory-head"><span class="eyebrow">GTA 6 · GUIDE OPERATIVE</span><h1>{e(title)}</h1><p>{e(desc)}</p></section>'
    if kind=='all':
        body+=('<p class="v-guide-video-crosslink">🎬 Preferisci vedere il passaggio? '
               '<a href="'+url(CREATOR_VIDEO_PATH)+'">Vai ai video tutorial dei creator →</a></p>')
    if kind=='auto':
        body+=('<aside class="v-cash-safety"><strong>🚘 Cerchi un modello preciso?</strong>'
               '<p>Apri il <a href="'+url('veicoli/')+'">catalogo veicoli GTA VI</a>: '
               'posizioni documentate, passaggi per ottenerli, fonti e modelli in verifica.</p>'
               '</aside>')
    if kind=='soldi':
        body+=('<aside class="v-cash-safety" role="note"><strong>⚠️ Non farmare alla cieca nel Capitolo 1.</strong>'
               '<p>Prima di accumulare denaro, controlla un rischio importante per la progressione. '
               'Il bottino non sempre resterà disponibile dopo certe missioni. '
               f'<a href="{url("guide-e-tutorial/soldi-facili-capitolo-1/")}#avviso-capitolo-1">'
               'Leggi le precauzioni (spoiler leggero) →</a></p></aside>')
    body+='<section data-guide-directory aria-label="Catalogo delle guide"><div class="v-filterbar" id="cerca-guide"><label><span class="micro">Cerca per obiettivo</span><br><input type="search" data-guide-search placeholder="Es. soldi, auto, taxi…" aria-label="Cerca una guida"></label>'
    if kind=='all':
        body+='<div class="v-filters" role="group" aria-label="Filtra per obiettivo">'+''.join(f'<button type="button" data-guide-filter="{value}" aria-pressed="{str(value=="all").lower()}">{label}</button>' for value,label in [('all','Tutte'),('soldi','Soldi'),('auto','Auto'),('garage','Garage'),('inizio','Altre guide')])+'</div>'
    body+=f'</div><h2 class="v-directory-section-title">{e({"all":"Tutte le guide pratiche","soldi":"Guide per ottenere e conservare soldi","auto":"Guide per trovare e conservare veicoli"}[kind])}</h2><p class="v-result" data-guide-result role="status" aria-live="polite">{len(selected)} guide disponibili</p><div class="v-grid">'+''.join(card(g) for g in selected)+'</div></section>'
    if kind in ('all','auto','soldi'):
        body+=vehicle_progression.links(BASE+'/')
    if kind=='soldi':
        body+='<section class="v-section v-promo v-promo-no-media"><div><span class="eyebrow">PRIMA DI FARE SOLDI</span><h2>Non perdere il bottino nel passaggio al Capitolo 2</h2><p>Il normale Checking Account di BuckMe non protegge il denaro dalla perdita programmata a fine Capitolo 1. Quando disponibile, Family Savings può conservarne fino a 5.000 GTA$, ma il denaro trasferito non è prelevabile normalmente. Valuta gli acquisti utili e rimanda il farming pesante al Capitolo 2.</p><p class="v-caption">Leggi tutte le precauzioni nella <a href="'+url("guide-e-tutorial/soldi-facili-capitolo-1/")+'">guida al Capitolo 1</a>.</p></div></section>'
    return title,desc,path,body


def sources(g,media_keys):
    links=list(dict.fromkeys([g['source_url'],*g.get('extra_sources',[]),*[MEDIA[k]['source'] for k in media_keys]]))
    names={'powerpyx.com':'PowerPyx','pushsquare.com':'Push Square','insider-gaming.com':'Insider Gaming','gamesradar.com':'GamesRadar+','rockstargames.com':'Rockstar Games','gtabase.com':'GTABase','gta.tech4gamers.com':'Tech4Gamers'}
    body='<section class="v-sources" id="fonti"><h2>Fonti, immagini e verifica</h2><ul>'
    for source in links:
        host=urlsplit(source).hostname.removeprefix('www.')
        body+=f'<li><a href="{e(source)}" target="_blank" rel="noopener noreferrer">{e(names.get(host,host))} — apri il riferimento ↗</a></li>'
    body+='</ul><p>Testo sintetizzato e riorganizzato in italiano. Le schermate sono attribuite ai rispettivi editori e a Rockstar Games; le immagini promozionali sono dichiarate e non provano una posizione o un passaggio.</p>'
    body+='<p>Le indicazioni riportano le fonti, non test personali. Ricontrolla i prompt della tua patch. Nessuna certificazione automatica di compatibilità tra exploit e trofei.</p></section>'
    return body



def guide_seo_title(name):
    """Use complete original guide headings, shorten only the SEO suffix."""
    name=name.strip()
    for suffix in (" | Guida GTA 6 PS5", " | GTA 6 PS5", " | Guida PS5", ""):
        if len(name)+len(suffix)<=60:
            return name+suffix
    return name


def guide(g,guides):
    """Reader-first walkthrough: tutorial immediately after title and safeguards.

    All optional photos, maps, external media, editorial context and source
    details live *after* the action steps, in a closed native details panel.
    Never hide trophy-breaking prerequisites or invent gameplay evidence.
    """
    path=g['canonical_path']
    title=g['safe_title']
    count=len(g['steps'])
    if g['id']=='registrare-auto-personale':
        validate_first_car(g)
    if g['id']=='soldi-facili-capitolo-1':
        validate_money(g)
    body=legacy.crumbs([('Guide','guide-e-tutorial/'),(title,path)])
    body+=('<section class="v-intro v-guide-intro" aria-label="Introduzione alla guida">'
           '<span class="v-tag">'+e(g['tag'])+' · PS5 / PS5 Pro</span>'
           '<h1>'+e(title)+'</h1>'
           '<p>'+e(g['summary'])+'</p>'
           '<span class="v-guide-step-count">'+str(count)+' passaggi pratici</span>'
           '</section>')
    body+='<div class="v-guide-layout v-guide-single"><article class="v-guide-main">'
    if g['id']=='scansionare-veicoli':
        body+=render_waink_intro()
    body+=render_operational_brief(OPERATIONAL_BRIEFS,g)
    controls={
        'registrare-auto-personale':'↑ croce direzionale · R1 · △ (Triangolo) · levetta destra',
        'prima-persona-glitch-ps5':'OPTIONS · ↑ croce direzionale · ○ (Cerchio) · touchpad',
        'scansionare-veicoli':'↑ croce direzionale · WAiNK (segui i comandi a schermo)',
        'viaggio-rapido-taxi':'Telefono → Contatti → Paradise Taxi'
    }
    # WAiNK already states the requirements in its compact brief.
    if g['id']!='scansionare-veicoli':
        body+=('<details class="v-guide-prep">'
               '<summary>Prima di iniziare: requisiti e luogo di partenza</summary>'
               '<div class="v-guide-prep-content">'
               '<p><strong>Serve:</strong> '+e(g["requirements"])+'</p>'
               '<p><strong>Dove:</strong> '+e(g["location"])+'</p>'
               +('<p class="v-guide-controls"><strong>Comandi PS5:</strong> '+e(controls[g['id']])+'</p>' if g['id'] in controls else '')
               +'</div></details>')
    # Car registration is easy to confuse with owning garages or paying for
    # vehicle delivery. Make those story-gated differences visible up front.
    if g['id']=='registrare-auto-personale':
        body+=('<p class="v-guide-urgent car-story-warning" role="note">'
               '<strong>🚘 Prima registrazione gratuita:</strong> '
               'la prima registrazione da Moses è gratuita durante il Capitolo 2. '
               'Scooter Bros si sblocca quando concludi Moses e richiamare il veicolo '
               'prevede una tariffa mostrata nell’app. '
               'Il garage gratuito di Port Gellhorn e gli altri garage acquistabili '
               'si sbloccano dopo Daily Driver. '
               '<a href="https://www.gtabase.com/gta-6/articles/how-to-unlock-garages-in-gta-6" '
               'target="_blank" rel="noopener noreferrer">Fonte sblocchi garage ↗</a></p>')
        body+=('<aside class="v-guide-urgent" id="sblocchi-tracker" role="note">'
               '<strong>Quali auto puoi registrare?</strong>'
               '<p><strong>No Tracker:</strong> Moses, Capitolo 2.</p>'
               '<p><strong>Standard:</strong> Pay ’n’ Spray, dopo i primi incarichi del Capitolo 3.</p>'
               '<p><strong>Advanced:</strong> Pay ’n’ Spray, dopo Dale Mamba nella catena di Randy. '
               'Non occorre completare tutte le 16 consegne.</p>'
               '<a href="https://www.powerpyx.com/gta-6-how-to-register-advanced-tracker-cars/" target="_blank" rel="noopener noreferrer">Fonte PowerPyx, 25 novembre ↗</a></aside>')
    if g['id']=='sportive-randy-posizioni':
        body+=('<p class="v-guide-urgent" data-randy-completion="separate" role="note">'
               '<strong>🏆 Due obiettivi diversi:</strong> Dale Mamba sblocca la registrazione Advanced Tracker; '
               'per Domanda e offerta (Supply &amp; Demand) devi completare anche tutta la lista e il finale della serie. '
               'I nomi delle missioni successive sono negli approfondimenti.</p>')
    if g['id']=='scansionare-veicoli':
        body+=('<p class="v-guide-urgent waink-tracker-warning" role="note">'
               '<strong>🚘 Prima di rubare:</strong> '
               '<strong>No Tracker</strong> = nessun localizzatore. '
               '<strong>Standard</strong> e <strong>Advanced</strong>: rischio di segnalazione. '
               'Vedi il confronto illustrato al passo 4. '
               '<a href="https://www.powerpyx.com/gta-6-moses-take-a-vehicle-to-moses-walkthrough/" '
               'target="_blank" rel="noopener noreferrer">Verifica PowerPyx ↗</a></p>')
    # Critical trophy/save warnings must remain visible BEFORE the first step.
    if g['id']=='soldi-facili-capitolo-1':
        body+=('<p class="v-guide-urgent cash-critical-warning" role="note">'
               '<strong>⚠️ Non perdere i soldi:</strong> '
               'prima di Recalibration crea un salvataggio manuale separato. '
               'Con Tourist Trap il denaro ordinario non viene conservato '
               'nel Capitolo 2. Valuta Family Savings (massimo 5.000 GTA$, '
               'non normalmente prelevabili) prima di avanzare. '
               '<a href="https://www.powerpyx.com/gta-6-tourist-trap-take-up-mattias-offer-walkthrough/" target="_blank" rel="noopener noreferrer">Fonte del punto di non ritorno ↗</a>'
               '</p>')
    if g['id']=='soldi-2500-three-sheets-liquor':
        body+=('<p class="v-guide-urgent" role="note"><strong>⚠️ Non perdere i soldi:</strong> '
               'il denaro del Capitolo 1 può andare perso avanzando nella storia. '
               'Prima di accumularlo, crea un salvataggio manuale separato e leggi '
               'le precauzioni sotto il tutorial.</p>')
    if g['id']=='prima-persona-glitch-ps5':
        body+=('<p class="v-guide-urgent" data-glitch-patch-status="community" role="note">'
               '<strong>🟡 Community:</strong> segnalato funzionante anche dopo la patch del 23 novembre; non testato da noi. '
               '<strong>🏆 Trofei non verificati.</strong> '
               'Non usare il salvataggio principale del platino: crea prima '
               'un salvataggio di prova separato.</p>')
    if g['id']=='meditazione-capitolo-1':
        body+=('<p class="v-guide-urgent" role="note"><strong>🏆 Prima meditazione:</strong> '
               'se l’hai saltata, PowerPyx segnala la lezione alternativa Learn to Meditate Together '
               'dopo lo sblocco di entrambi i personaggi. Non ricominciare soltanto per questo.</p>')
    body+=('<section id="procedura" class="v-tutorial" aria-labelledby="titolo-procedura">'
           '<header class="v-tutorial-head">'
           '<span class="v-tutorial-start-here">'+str(count)+' PASSAGGI</span>'
           '<h2 id="titolo-procedura">Come fare, passo per passo</h2>'
           '<p>Segui le istruzioni nell’ordine indicato.</p>'
           '</header>')
    if g['spoiler']:
        body+=('<p class="v-spoiler-warning" role="note">'
               '<strong>⚠️ Spoiler:</strong> i prossimi passaggi mostrano missioni, luoghi o ricompense.'
               '</p>')
    body+='<ol class="v-steps">'
    used=[]
    step_evidence=[]
    for n,raw in enumerate(g['steps']):
        text=re.sub(r'^SPOILER(?: LUOGHI)?:\s*','',raw)
        heading=g['step_headings'][n] if n<len(g['step_headings']) else 'Segui il passaggio'
        body+=(
            f'<li class="v-step" id="passaggio-{n+1}">'
            '<div class="v-step-head">'
            f'<span class="v-step-n" aria-hidden="true">{n+1:02d}</span>'
            '<div>'
            f'<span class="v-step-kicker">PASSO {n+1} DI {count}</span>'
            f'<h3>{e(heading)}</h3><p>{e(text)}</p>'
            '</div></div>')
        if g['id']=='scansionare-veicoli':
            body+=render_waink_step(n)
        if g['id']=='registrare-auto-personale':
            body+=render_first_car(n)
        if g['id']=='soldi-facili-capitolo-1':
            body+=render_money(n)
        key=g['step_media'].get(n)
        approved=PHOTO_STEP_REVIEW['guide_step_approved'].get(g['id'],{}).get(str(n))
        if key and (not approved or approved['key']!=key):
            raise ValueError('Photo not approved for tutorial: '+g['id']+' step '+str(n+1))
        if approved and not key:
            raise ValueError('Approved tutorial photo not configured: '+g['id']+' step '+str(n+1))
        photo_shown=False
        if key:
            if key not in MEDIA or MEDIA[key]['kind']!='screenshot':
                raise ValueError('Non-gameplay image in a tutorial: '+str(key))
            if MEDIA[key]['source']!=approved['source']:
                raise ValueError('Photo source differs from audited record: '+key)
            if media_src(key):
                body+=('<div class="v-proof-media" data-visual-proof-image="'+e(key)+'">'
                       '<p class="v-proof-label">FOTO DEL PASSAGGIO</p>'
                       +figure(key)+'</div>')
                used.append(key)
                photo_shown=True
        context=PHOTO_STEP_REVIEW.get('context_approved',{}).get(g['id'],{}).get(str(n))
        if context:
            context_key=context['key']
            if context_key not in MEDIA or MEDIA[context_key]['kind']!='screenshot':
                raise ValueError('Unverified location photo: '+str(context_key))
            if media_src(context_key):
                body+=('<div class="v-proof-media v-location-reference" '
                       'data-visual-location-image="'+e(context_key)+'">'
                       '<p class="v-proof-label">FOTO DEL LUOGO · SOLO RIFERIMENTO</p>'
                       +figure(context_key,context['caption'])+'</div>')
                photo_shown=True
        # Only photos explicitly approved for this numbered instruction
        # appear here. A requested photo-role ID does not imply a step.
        community_photo=render_approved_for_step(g,APPROVED_PHOTOS,n)
        if community_photo:
            body+=community_photo
            photo_shown=True
        photo_ref=render_step_photo_source(PHOTO_SOURCE_REFS,g['id'],n)
        if photo_ref:
            if photo_shown:
                body+=('<details class="v-more-photo-sources"><summary>Altre foto e riferimenti '
                       'sul sito originale (facoltativo)</summary>'+photo_ref+'</details>')
            else:
                body+=photo_ref
        evidence=render_step_evidence(g,n,STEP_EVIDENCE,VISUAL_EVIDENCE)
        if evidence:
            if g['id'] in {'registrare-auto-personale','soldi-facili-capitolo-1','soldi-2500-three-sheets-liquor',
                           'scansionare-veicoli','prima-persona-glitch-ps5','meditazione-capitolo-1'}:
                # Map/video reference belongs beside its corresponding action.
                # They remain verified external links, never screenshots or fake pins.
                body+=evidence
            else:
                step_evidence.append((n+1,heading,evidence))
        checks=g.get('checks',[])
        if n<len(checks):
            body+=f'<p class="v-check"><strong>✓ Controllo:</strong> {e(checks[n])}</p>'
        body+='</li>'
    body+='</ol>'
    if g['id']=='meditazione-capitolo-1':
        # The in-game meditation checklist belongs to the actionable guide,
        # not to the references that follow after completion.
        body+=render_meditation_tracker()
    body+='<p class="v-tutorial-finish"><strong>FINE DEI PASSAGGI</strong> · Da qui in poi trovi soltanto informazioni aggiuntive.</p>'
    body+='</section>'
    # Readers can stop here: reference material is genuinely optional.
    body+=('<details class="v-guide-more" id="approfondimenti">'
           '<summary><span><strong>Approfondimenti e materiali extra</strong>'
           '<small>Non fanno parte del tutorial: mappe, video, fonti e note</small></span>'
           '<span class="v-more-chevron" aria-hidden="true">⌄</span></summary>'
           '<div class="v-guide-more-content">')
    if g['id']=='registrare-auto-personale':
        body+=('<p class="v-guide-next-moses"><strong>DOPO LA PRIMA AUTO:</strong> '
               '<a href="'+url(MOSES_JOBS_PATH)+'">6 veicoli da recuperare per Moses, con ricompense →</a>'
               '</p>')
        body+=('<section class="v-guide-ref-list" id="advanced-tracker-details" aria-labelledby="advanced-tracker-title">'
               '<h3 id="advanced-tracker-title">Registrare un’auto con Advanced Tracker (Capitolo 3)</h3>'
               '<p><strong>Verificata sulle fonti · spoiler leggero sulla progressione.</strong></p>'
               '<ol><li>Completa Clonin’ Keys, Makin’ Gs e avvia le richieste di Randy. '
               '<a href="'+url('guide-e-tutorial/sportive-randy-posizioni/')+'">Apri la guida Randy</a>.</li>'
               '<li>Consegna alcuni veicoli richiesti: secondo PowerPyx circa 5–7, non una soglia garantita.</li>'
               '<li>Quando compare Dale Mamba, completa la missione. '
               '<a href="https://www.powerpyx.com/gta-6-dale-mamba-steal-the-declasse-mamba-gt-walkthrough/" target="_blank" rel="noopener noreferrer">Procedura originale ↗</a>.</li>'
               '<li>Scansiona un veicolo con WAiNK. Al Pay ’n’ Spray controlla che Register sia disponibile, '
               'che ci sia uno slot libero e conferma il prezzo mostrato nel gioco.</li></ol>'
               '<p><strong>Controllo finale:</strong> verifica che il nuovo mezzo compaia in Scooter Bros. '
               'Non confondere il Key Cloner con il permesso di registrazione.</p>'
               '<p>Fonte: <a href="https://www.powerpyx.com/gta-6-how-to-register-advanced-tracker-cars/" target="_blank" rel="noopener noreferrer">PowerPyx, 25 novembre 2026 ↗</a>. '
               'Procedura non testata personalmente in gioco.</p></section>')
    if g['id']=='sportive-randy-posizioni':
        body+=('<section class="v-guide-ref-list" id="randy-trophy-finale" aria-labelledby="randy-finale-title">'
               '<h3 id="randy-finale-title">Domanda e offerta: come concludere la serie (spoiler)</h3>'
               '<ol><li>Termina Randy’s Wish List e Dale Mamba.</li>'
               '<li>Completa Mansion Thrax quando ricevi la nuova richiesta.</li>'
               '<li>Attendi il contatto di Randy e completa Delivery Day (Meet Randy) a Balsero.</li></ol>'
               '<p><strong>Controllo finale:</strong> cerca lo sblocco del trofeo Supply &amp; Demand dopo Delivery Day. '
               'Lo sblocco Advanced Tracker avviene prima, con Dale Mamba.</p>'
               '<p><a href="https://www.powerpyx.com/gta-6-mansion-thrax-steal-the-truffade-thrax-walkthrough/" target="_blank" rel="noopener noreferrer">Fonte Mansion Thrax ↗</a> · '
               '<a href="https://www.powerpyx.com/gta-6-delivery-day-meet-randy-walkthrough/" target="_blank" rel="noopener noreferrer">Fonte Delivery Day, 26 novembre ↗</a> · '
               '<a href="'+url('trofei/trofeo-26-domanda-e-offerta/')+'">Scheda trofeo</a></p></section>')
    if step_evidence:
        body+='<section class="v-guide-ref-list"><h3>Riferimenti per alcuni passaggi (facoltativi)</h3>'
        for number,heading,fragment in step_evidence:
            body+='<div class="v-guide-ref-entry"><strong>Passaggio '+str(number)+': '+e(heading)+'</strong>'+fragment+'</div>'
        body+='</section>'
    if g['id'] in {'soldi-facili-capitolo-1','soldi-2500-three-sheets-liquor'}:
        body+=('<aside class="v-missable-notice" role="note"><strong>🏆 Attività mancabili, ma non richieste per il platino.</strong>'
               '<p>Gli incarichi Get Shirley’s Rum e Steal the Scooter sono esclusivi del Capitolo 1. '
               'PowerPyx li indica come mancabili, ma non necessari per il 100% o per i trofei. '
               'Falli prima del finale del capitolo se vuoi vedere tutto; '
               'non serve ricominciare la partita soltanto per questi due incarichi.</p>'
               '<a href="https://www.powerpyx.com/gta-6-all-strangers-freaks-side-missions/" '
               'target="_blank" rel="noopener noreferrer">Verifica la lista PowerPyx ↗</a></aside>')
        body+=('<aside class="v-cash-safety" role="note"><strong>⚠️ Prima di farmare: una perdita possibile nel Capitolo 1.</strong>'
               '<details class="v-cash-details" id="avviso-capitolo-1">'
               '<summary>Mostra le precauzioni e il punto di non ritorno (spoiler leggero)</summary>'
               '<p>Secondo GTABase, Tech4Gamers e numerose testimonianze dei giocatori del 19–20 novembre, '
               'completando il Capitolo 1 si perdono i contanti, il saldo ordinario BuckMe, '
               'il denaro nascosto nella casa di Jason e i veicoli personali iniziali. '
               'La missione <strong>Tourist Trap</strong> è segnalata come punto di non ritorno: '
               '<strong>crea un salvataggio manuale separato PRIMA di Recalibration</strong>, '
               'perché il finale del capitolo potrebbe avviarsi subito dopo.</p>'
               '<p>Prima di Recalibration: considera '
               'fino a <strong>5.000 GTA$</strong> in Family Savings quando disponibile '
               '(non prelevabile normalmente), investi soltanto in equipaggiamento '
               'documentato come conservabile e rimanda i grandi bottini recuperabili '
               'al Capitolo 2. Non considerare il normale conto corrente un rifugio. '
               'La compatibilità con i trofei delle singole scelte non è certificata.</p>'
               '<p class="v-caption">Riscontri: '
               '<a href="https://www.gtabase.com/gta-6/articles/how-to-keep-your-money-safe-in-gta-6" target="_blank" rel="noopener noreferrer">GTABase</a>'
               ' · <a href="https://gta.tech4gamers.com/gta-6/guides/money-end-of-chapter-1/" target="_blank" rel="noopener noreferrer">Tech4Gamers</a>'
               ' · <a href="https://www.powerpyx.com/gta-6-tourist-trap-take-up-mattias-offer-walkthrough/" target="_blank" rel="noopener noreferrer">PowerPyx: punto di non ritorno</a>'
               ' · <a href="https://www.reddit.com/r/GTA6/comments/1y0sv2n/something_you_should_know_about_the_end_of/" target="_blank" rel="noopener noreferrer">Discussione r/GTA6</a>. '
               'Fonti indipendenti, non test diretti del nostro team.</p>'
               '</details><p class="v-photo-hub-guide-callout"><a href="'+url('screenshot-ps5/')+'">Vedi tutte le richieste fotografiche della community →</a></p></aside>')
    if g['id']=='prima-persona-glitch-ps5':
        body+=('<aside class="v-glitch-status" role="note"><strong>🟡 Community · segnalato funzionante dopo la patch del 23 novembre</strong>'
               '<p>Verifica fonti: 25 novembre 2026. PC Gamer ha provato il metodo al lancio. '
               'Il 23 novembre utenti PS5 e PS5 Pro hanno riferito di riuscire ancora ad attivarlo dopo l’aggiornamento. '
               'GamePro il 24 novembre riprende una testimonianza della community; GamesRadar indica che le note non menzionano il glitch. '
               'Versione riportata: 01.002.002. Non abbiamo provato personalmente questa versione; '
               'le segnalazioni non equivalgono a una conferma Rockstar.</p>'
               '<p><a href="https://www.reddit.com/r/GTA6/comments/1y3kl8l/can_anyone_confirm_if_the_first_person_camera/" target="_blank" rel="noopener noreferrer">Discussione post-patch del 23 novembre ↗</a> · '
               '<a href="https://www.gamepro.de/artikel/gta-6-update-01002002%2C3463626.html" target="_blank" rel="noopener noreferrer">GamePro del 24 novembre ↗</a> · '
               '<a href="https://www.gamesradar.com/games/grand-theft-auto/gta-6-update-gives-players-losing-progress-to-crashes-a-lifeline-and-it-looks-like-the-first-person-and-60fps-glitches-are-safe-for-now/" target="_blank" rel="noopener noreferrer">GamesRadar: stato dopo la patch ↗</a> · '
               '<a href="'+url('patch/2026-11-23/')+'">Riepilogo delle note ufficiali</a>.</p>'
               '<p><strong>⚠️ Trophy Status Uncertain.</strong> Non esistono prove specifiche '
               'di compatibilità con i trofei: se punti al platino, non provarlo sul salvataggio principale. '
               'È una tecnica single-player; fai un salvataggio manuale separato prima di iniziare.</p>'
               '<p><a href="https://www.pcgamer.com/games/grand-theft-auto/gta-6-is-playable-in-first-person-heres-how-to-activate-it/" '
               'target="_blank" rel="noopener noreferrer">Verifica indipendente PC Gamer ↗</a> '
               '· <a href="https://www.reddit.com/r/GTA6/comments/1y15kfv/" target="_blank" '
               'rel="noopener noreferrer">Segnalazione Reddit del 20 novembre ↗</a></p></aside>')
    if g.get('benefit'):
        body+='<p class="v-guide-extra-note"><strong>Da sapere:</strong> '+e(g['benefit'])+'</p>'
    body+=walkthrough_visuals(g)
    body+=render_guide_locations(g,LOCATION_REFS,MEDITATION_PLACES)
    interactive=render_interactive_map(g['safe_title'],
          interactive_guide_points(g,LOCATION_REFS,MEDITATION_PLACES),
          id_suffix=g['id'],page_label='guida',
          curated_refs=external_refs_for(EXTERNAL_MAP_REFS,guide=g['id']))
    if g.get('spoiler'):
        interactive=('<details class="v-map-spoiler"><summary>Mostra la mappa interattiva '
                     'e i luoghi di questa guida (spoiler)</summary>'+interactive+'</details>')
    body+=interactive
    body+=f'<aside class="v-notice"><strong>Prima di continuare</strong>{e(g.get("caution","Controlla il progresso in gioco."))}</aside>'
    if g['id']=='poligoni-concentrazione':
        body+=f'<p><a class="v-button secondary" href="{url("trofei/trofeo-17-cecchino/")}">Apri la checklist delle medaglie →</a></p>'
    body+=visual_contribution(g)
    body+=render_approved_for_guide(g,APPROVED_PHOTOS)
    body+=sources(g,used)
    body+='</div></details></article></div>'
    body+=f'<p class="v-guide-return"><a href="{url("guide-e-tutorial/")}">← Torna a tutte le guide</a></p>'
    description=g['seo_description']
    seo_title=guide_seo_title(title)
    structured=legacy.schema_article(seo_title,description,url(path),None)
    legacy.write(path+'index.html',layout(seo_title,description,path,body,'guide',None,structured=structured))



def validate(guides):
    seen=set()
    allowed={'powerpyx.com','www.powerpyx.com','insider-gaming.com','www.insider-gaming.com','www.pushsquare.com','www.gamesradar.com','www.gtabase.com','gtabase.com','gta.tech4gamers.com','www.videogameschronicle.com','www.pcgamer.com','www.dexerto.com','www.reddit.com','www.gamepro.de'}
    for g in guides:
        if g['id'] in seen or not re.fullmatch(r'[a-z0-9-]+',g['id']):
            raise ValueError('Duplicate or invalid guide id')
        seen.add(g['id'])
        if not re.fullmatch(r'(?:[a-z0-9-]+/)+',g['canonical_path']):
            raise ValueError('Invalid canonical path')
        for source in [g['source_url'],*g.get('extra_sources',[])]:
            parts=urlsplit(source)
            if parts.scheme!='https' or parts.hostname not in allowed or parts.username or parts.password:
                raise ValueError('Unapproved guide source')
        if not g['steps'] or g['hero_media'] not in MEDIA:
            raise ValueError('Incomplete guide')
    return True


def main():
    global GUIDE_MAP_PATHS, MAP_RENDER_PATHS
    cinematic_site.prepare()
    editorial_articles.prepare()
    records=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
    records+=json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides']
    guides=enrich(records)
    validate(guides)
    validate_operational_briefs(OPERATIONAL_BRIEFS,guides)
    validate_moses_jobs()
    for guide_id,items in PHOTO_STEP_REVIEW.get('context_approved',{}).items():
        candidate=next((g for g in guides if g['id']==guide_id),None)
        if candidate is None:
            raise ValueError('Photo context for unknown guide: '+guide_id)
        for index,item in items.items():
            if not index.isdigit() or int(index)>=len(candidate['steps']) or int(index)<0:
                raise ValueError('Location photo outside guide steps: '+guide_id)
            key=item.get('key')
            if (key not in MEDIA or MEDIA[key]['kind']!='screenshot'
                or item.get('role')!='riferimento-luogo'
                or not 40<=len(item.get('caption',''))<=230):
                raise ValueError('Location reference without verifiable role and caption: '+guide_id)
    validate_step_photo_sources(PHOTO_SOURCE_REFS,guides)
    validate_step_evidence(guides,STEP_EVIDENCE,VISUAL_EVIDENCE)
    validate_map_references(guides,LOCATION_REFS,MEDITATION_PLACES)
    trophies=json.loads(Path('data/trofei.json').read_text(encoding='utf-8'))['trophies']
    map_rollout=validate_interactive_maps(guides,trophies,LOCATION_REFS,COLLECTIBLE_ROUTES)
    map_rollout.update(validate_curated_external_refs(EXTERNAL_MAP_REFS,guides,trophies,COLLECTIBLE_ROUTES))
    GUIDE_MAP_PATHS={row['canonical_path'] for row in guides}
    MAP_RENDER_PATHS=set(TROPHY_MAP_PATHS)|GUIDE_MAP_PATHS|{MAP_HUB_PATH,COLLECTIBLE_ROUTE_PATH}
    validate_advanced(ADVANCED,trophies)
    validate_provenance(PHOTO_REVIEW,MEDIA,guides)
    rockstar_manifest=validate_rockstar_gallery()
    vehicle_catalog=validate_vehicles(load_vehicle_catalog())
    validate_routes(COLLECTIBLE_ROUTES)
    validate_collectible_photos(COLLECTIBLE_PHOTOS,COLLECTIBLE_ROUTES)
    validate_approved(APPROVED_PHOTOS,guides,VISUAL_REQUESTS)
    PHOTO_COVERAGE=audit_photo_coverage(guides,VISUAL_REQUESTS,APPROVED_PHOTOS,PHOTO_REVIEW)
    site_info.sources_for=lambda path: ORIGINAL_SOURCES(path)+('build_visual_site.py','moses_vehicle_jobs_v1.py','operational_brief_v1.py','data/guide_operational_briefs_v1.json','site/assets/operational-guide-v1.css','site/assets/site-focus-v1.css','collectible_routes_v4.py','data/collectible_routes_v4.json','data/collectible_photo_evidence_v1.json','collectible_photo_evidence_v1.py','site/assets/collectible-photo-v1.css','site/assets/collectible-beginner-v1.css','site/assets/collectible-beginner-v1.js','photo_intake_v4.py','data/approved_screenshots_v4.json','advanced_platinum_v3.py','data/advanced_platinum_v3.json','photo_provenance_v3.py','data/photo_provenance_review_v3.json','visual_guide_content.py','data/visual_guides.json','data/visual_media.json','data/visual_requests.json','data/guide_visual_refs.json','data/guide_step_refs.json','guide_step_references_v1.py','data/step_image_sources_v1.json','step_image_sources_v1.py','data/guide_locations_v2.json','guide_location_atlas_v2.py','data/map_external_permalinks_v1.json','interactive_article_maps_v1.py','site/assets/interactive-map-v1.css','site/assets/interactive-map-v1.js','data/guide_extras.json','photo_request_hub_v1.py','data/meditation_checklist_v1.json','meditation_tracker_v1.py','site/assets/visual-v2.css','site/assets/visual-v2.js','rockstar_gallery_v1.py','site/assets/rockstar/gta-vi/manifest.json','site/assets/rockstar-gallery-v1.css','site/assets/rockstar-gallery-v1.js','vehicle_catalog_v1.py','data/vehicle_catalog_v1.json','site/assets/vehicle-finder-v1.css','site/assets/vehicle-finder-v1.js') + (('platinum_roadmap_v1.py','platinum_atlas_v2.py','data/platinum_trophy_routes_v2.json','site/assets/platinum-roadmap.css','site/assets/platinum-roadmap.js','site/assets/platinum-atlas-v2.css','site/assets/platinum-atlas-v2.js') if path==ROADMAP_PATH else ()) + (('waink_visual_v1.py',)+tuple('site/assets/waink-guide/step-'+str(n)+'.svg' for n in range(1,6)) if path=='guide-e-tutorial/scansionare-veicoli/' else ())
    original_patch_sources=site_info.sources_for
    site_info.sources_for=lambda path: original_patch_sources(path)+(('patch_archive_v1.py','patch_observations_v1.py','data/patches_v1.json','site/assets/editorial-articles.css') if path.startswith('patch/') else ())
    original_garage_sources=site_info.sources_for
    site_info.sources_for=lambda path: original_garage_sources(path)+(('garage_guides_v1.py','site/assets/vehicle-finder-v1.css') if path.startswith(garage_guides.PATH) else ())
    site_info.last_modified_at.cache_clear()
    legacy.layout=layout
    from community_discovery_v2 import render as community_render
    legacy.render_community_page=community_render
    legacy.main()
    roadmap_title='Roadmap Platino GTA 6 PS5: guida ai 55 trofei'
    roadmap_desc='Roadmap per il Platino di GTA VI su PS5: meditazioni, 5 fasi, 100%, medaglie Oro e checklist privata dei progressi.'
    roadmap_trophies=json.loads(Path('data/trofei.json').read_text(encoding='utf-8'))['trophies']
    validate_trophy_atlas(roadmap_trophies,TROPHY_ROUTES)
    roadmap_body=(legacy.crumbs([('Trofei','trofei/'),('Roadmap platino',ROADMAP_PATH)])+
                  render_platinum_roadmap(roadmap_trophies)+
                  render_trophy_atlas(roadmap_trophies,TROPHY_ROUTES))
    roadmap_schema={'@context':'https://schema.org','@type':'WebPage',
                    'name':roadmap_title,'description':roadmap_desc,
                    'url':url(ROADMAP_PATH),'inLanguage':'it-IT'}
    legacy.write(ROADMAP_PATH+'index.html',layout(
        roadmap_title,roadmap_desc,ROADMAP_PATH,roadmap_body,'trofei',
        structured=roadmap_schema))
    title='GTA 6 Italia: soldi facili, auto speciali e guide PS5'
    desc='Guide GTA VI in italiano: soldi facili, auto speciali, garage, trofei e HDR OLED. Passaggi chiari, immagini attribuite e avviso spoiler.'
    legacy.write('index.html',layout(title,desc,'',home(guides),'home',structured={'@context':'https://schema.org','@type':'WebSite','name':'GTA 6 Italia','url':url(),'inLanguage':'it-IT'}))
    map_title='Mappe GTA 6 PS5: 11 guide con posizioni documentate'
    map_desc=('Mappe GTA VI in italiano: 11 guide con riferimenti alle posizioni, '
              '10 luoghi di meditazione e collegamenti alle fonti originali.')
    map_body=render_interactive_map('I luoghi delle nostre guide',
        interactive_collectible_points(COLLECTIBLE_ROUTES),id_suffix='directory',
        page_label='raccolta',curated_refs=EXTERNAL_MAP_REFS['items'])+render_map_hub(
        guides, LOCATION_REFS, MEDIA,
        json.loads(Path('data/guide_extras.json').read_text(encoding='utf-8'))['guides'], media_src,
        APPROVED_PHOTOS['photos'])
    map_schema={'@context':'https://schema.org','@type':'CollectionPage',
                'name':map_title,'description':map_desc,
                'url':url(MAP_HUB_PATH),'inLanguage':'it-IT','numberOfItems':len(guides)}
    legacy.write(MAP_HUB_PATH+'index.html',layout(
        map_title,map_desc,MAP_HUB_PATH,map_body,'guide',structured=map_schema))
    for path,title,description,body,page_type in (
        (COLLECTIBLE_PATH,
         'GTA 6: 100% checklist PS5, carte e collezionabili',
         'Checklist 100% GTA VI PS5 con 35 categorie, 18 set di carte e progressi numerici salvati nel browser.',
         render_advanced_100(ADVANCED,trophies),'CollectionPage'),
        (HARD_PATH,
         'GTA 6: trofei difficili Rhino, UFO, palestra e bowling',
         'Guida pratica GTA VI ai trofei difficili: Rhino, UFO, forza di Jason e Lucia, bowling e condizioni ancora incerte.',
         render_advanced_hard(ADVANCED,trophies),'WebPage')
    ):
        schema={'@context':'https://schema.org','@type':page_type,
                'name':title,'description':description,'url':url(path),'inLanguage':'it-IT'}
        legacy.write(path+'index.html',layout(
            title,description,path,legacy.crumbs([('Trofei','trofei/'),(title,path)])+body,
            'trofei',structured=schema))
    route_title='Collezionabili GTA 6: percorsi e mappe per regione PS5'
    route_desc=('GTA VI: 123 checkpoint documentati in 7 aree, riviste e copie da controllare nei capitoli, WAiNK, 24 salti, '
                'carta mancabile del Capitolo 2 e checklist locale. Nessun pin inventato.')
    route_schema={'@context':'https://schema.org','@type':'CollectionPage',
                  'name':route_title,'description':route_desc,'url':url(COLLECTIBLE_ROUTE_PATH),
                  'inLanguage':'it-IT','numberOfItems':len(COLLECTIBLE_ROUTES['points'])}
    legacy.write(COLLECTIBLE_ROUTE_PATH+'index.html',layout(
        route_title,route_desc,COLLECTIBLE_ROUTE_PATH,
        render_collectible_routes(COLLECTIBLE_ROUTES,EXTERNAL_MAP_REFS['items'],COLLECTIBLE_PHOTOS)+
        '<details class="cr-map-extra"><summary>🗺️ Apri la mappa interattiva (facoltativa, NON indica 123 pin esatti)</summary>'+
        render_interactive_map('I 123 checkpoint di Leonida',
           interactive_collectible_points(COLLECTIBLE_ROUTES),id_suffix='collectibles',
           page_label='raccolta',curated_refs=EXTERNAL_MAP_REFS['items'])+
        '</details>',
        'guide',structured=route_schema))
    legacy.write('map-rollout-v1.json',export_map_rollout(map_rollout))
    growth_data=growth_report()
    legacy.write('growth-evidence-v1.json',export_growth_report(growth_data))
    dashboard_title='GTA VI Italia: statistiche X e crescita trasparente'
    dashboard_desc=('Dashboard pubblica di GTA VI Italia: Social Radar, post X verificati, '
                    'impression Buffer solo se disponibili, visite e follower non inventati.')
    legacy.write(GROWTH_PATH+'index.html',layout(
        dashboard_title,dashboard_desc,GROWTH_PATH,render_growth_dashboard(growth_data),
        'guide',robots='noindex,follow',structured={
            '@context':'https://schema.org','@type':'WebPage',
            'name':dashboard_title,'description':dashboard_desc,
            'url':url(GROWTH_PATH),'inLanguage':'it-IT'}))
    intake_title='Invia screenshot GTA 6 PS5: consenso e guida alla foto'
    intake_desc=('Contribuisci alle guide GTA VI con screenshot originali PS5: scegli uno dei 55 '
                 'passaggi, prepara un post X e autorizza esplicitamente il riutilizzo.')
    intake_schema={'@context':'https://schema.org','@type':'WebPage',
                   'name':intake_title,'description':intake_desc,'url':url(PHOTO_INTAKE_PATH),
                   'inLanguage':'it-IT'}
    legacy.write(PHOTO_INTAKE_PATH+'index.html',layout(
        intake_title,intake_desc,PHOTO_INTAKE_PATH,
        render_photo_intake(guides,VISUAL_REQUESTS,APPROVED_PHOTOS),
        'guide',structured=intake_schema))
    coverage_title='GTA 6 Screenshot PS5: priorità, 55 foto passo per passo'
    coverage_desc=('Quali screenshot servono a GTA VI Italia: 55 passaggi in 11 guide, '
                   'priorità, consenso, stato della verifica e link X precompilati.')
    coverage_schema={'@context':'https://schema.org','@type':'CollectionPage',
                     'name':coverage_title,'description':coverage_desc,'url':url(PHOTO_COVERAGE_PATH),
                     'inLanguage':'it-IT','numberOfItems':PHOTO_COVERAGE['total_requests']}
    legacy.write(PHOTO_COVERAGE_PATH+'index.html',layout(
        coverage_title,coverage_desc,PHOTO_COVERAGE_PATH,render_photo_coverage(PHOTO_COVERAGE),
        'guide',structured=coverage_schema))
    legacy.write('photo-backlog-v5.json',export_photo_coverage(PHOTO_COVERAGE))
    new_paths=[ROADMAP_PATH,MAP_HUB_PATH,COLLECTIBLE_PATH,HARD_PATH,COLLECTIBLE_ROUTE_PATH,PHOTO_INTAKE_PATH,PHOTO_COVERAGE_PATH]
    for gp,gt,gd,gb,gtype in garage_guides.pages(BASE+'/'):
        legacy.write(gp+'index.html',layout(gt,gd,gp,gb,'guide',structured={'@context':'https://schema.org','@type':gtype,'name':gt,'description':gd,'url':url(gp),'inLanguage':'it-IT'}))
        new_paths.append(gp)
    glitch_title='Glitch GTA 6 su PS5: exploit e stato delle patch'
    legacy.write('glitch/index.html',layout(glitch_title,'Solo glitch documentati, separati dalle guide legittime.','glitch/',chronology.glitch_page(url),'guide',structured={'@context':'https://schema.org','@type':'CollectionPage','name':glitch_title,'url':url('glitch/')}))
    new_paths.append('glitch/')
    # Curated promotional photo index: never inserted into step-by-step guides.
    gallery_title='Immagini ufficiali GTA VI Rockstar: ambientazioni, personaggi e Ultimate Edition'
    gallery_description=('Galleria delle immagini ufficiali GTA VI da Rockstar Games: '
                         'personaggi, luoghi di Leonida e Ultimate Edition. '
                         'Anteprime leggere, crediti e fonti originali, senza spoiler di tutorial.')
    gallery_schema={'@context':'https://schema.org','@type':'CollectionPage',
                    'name':gallery_title,'description':gallery_description,
                    'url':url(ROCKSTAR_GALLERY_PATH),'inLanguage':'it-IT',
                    'numberOfItems':rockstar_manifest['asset_count']}
    legacy.write(ROCKSTAR_GALLERY_PATH+'index.html',layout(
        gallery_title,gallery_description,ROCKSTAR_GALLERY_PATH,
        render_rockstar_gallery(rockstar_manifest),'guide',structured=gallery_schema))
    new_paths.append(ROCKSTAR_GALLERY_PATH)
    # Each car gets its own canonical article; unverified leads are explicitly
    # noindex until their location is corroborated. No fabricated GPS markers.
    vehicle_title='Veicoli GTA VI: cerca auto, moto, posizioni e come ottenerli'
    vehicle_desc=('Trova le auto di GTA VI per nome e zona: missioni Moses, lista Randy, '
                  'luoghi verificati, prerequisiti e guide per conservarle.')
    vehicle_schema={'@context':'https://schema.org','@type':'CollectionPage',
                    'name':vehicle_title,'description':vehicle_desc,
                    'url':url(VEHICLE_PATH),'inLanguage':'it-IT',
                    'numberOfItems':len(vehicle_catalog['items'])}
    legacy.write(VEHICLE_PATH+'index.html',layout(
        vehicle_title,vehicle_desc,VEHICLE_PATH,
        render_vehicle_index(vehicle_catalog,BASE+'/'),'guide',
        structured=vehicle_schema))
    new_paths.append(VEHICLE_PATH)
    for car,vehicle_path,content in vehicle_pages(vehicle_catalog,BASE+'/'):
        vehicle_title=car['name']+': dove trovarla in GTA VI e come ottenerla'
        vehicle_desc=(car['name']+' GTA VI: '+car['area']+'. '
                     'Dove cercarla, come sbloccarla e come verificare il risultato.')
        status='index,follow' if car['status']=='Verificata' else 'noindex,follow'
        vehicle_schema=({'@context':'https://schema.org','@type':'Article',
                        'headline':vehicle_title,'description':vehicle_desc,
                        'url':url(vehicle_path),'inLanguage':'it-IT'}
                        if status=='index,follow' else None)
        legacy.write(vehicle_path+'index.html',layout(
            vehicle_title,vehicle_desc,vehicle_path,content,'guide',
            robots=status,structured=vehicle_schema))
        if status=='index,follow':new_paths.append(vehicle_path)
    for kind in ('all','soldi','auto'):
        title,desc,path,body=directory(guides,kind)
        legacy.write(path+'index.html',layout(title+' | GTA 6 Italia',desc,path,body,'guide',structured={'@context':'https://schema.org','@type':'CollectionPage','name':title,'url':url(path),'inLanguage':'it-IT'}))
        new_paths.append(path)
    for g in guides:
        guide(g,guides); new_paths.append(g['canonical_path'])
    for vp,vt,vd,vb in vehicle_progression.pages(BASE+'/'):
        legacy.write(vp+'index.html',layout(vt,vd,vp,vb,'guide',structured={'@context':'https://schema.org','@type':'Article','name':vt,'description':vd,'url':url(vp),'inLanguage':'it-IT'}))
        new_paths.append(vp)
    # Independent optional chain: never merge it with the first-car tutorial.
    moses_title='GTA 6: 6 auto per Moses, posizioni e ricompense PS5'
    moses_desc=('Dopo Daily Driver trova i 6 veicoli richiesti da Moses: '
                'luoghi, azioni rapide, pagamenti e come ritirare il regalo finale.')
    legacy.write(MOSES_JOBS_PATH+'index.html',layout(
        moses_title,moses_desc,MOSES_JOBS_PATH,render_moses_jobs(BASE),
        'guide',structured={'@context':'https://schema.org','@type':'WebPage',
                            'name':moses_title,'url':url(MOSES_JOBS_PATH),
                            'description':moses_desc,'inLanguage':'it-IT'}))
    new_paths.append(MOSES_JOBS_PATH)
    # Curated original-video portal: one distinct YouTube source per item,
    # with Italian article and exact sourced chapters. No copied footage.
    creator_items=reviewed_creator_videos(load_creator_videos())
    creator_title='Video tutorial GTA VI: creator e guide italiane PS5'
    creator_desc=('Video tutorial GTA VI selezionati: TGG e IGN per auto e soldi, '
                  'altri riferimenti della community con minuti precisi e guide italiane.')
    creator_schema={'@context':'https://schema.org','@type':'CollectionPage',
                    'name':creator_title,'description':creator_desc,
                    'url':url(CREATOR_VIDEO_PATH),'inLanguage':'it-IT',
                    'numberOfItems':len(creator_items)}
    legacy.write(CREATOR_VIDEO_PATH+'index.html',layout(
        creator_title,creator_desc,CREATOR_VIDEO_PATH,
        render_creator_videos(creator_items),'guide',structured=creator_schema))
    new_paths.append(CREATOR_VIDEO_PATH)
    photo_hub,photo_audit=render_photo_hub(
        guides,VISUAL_REQUESTS,MEDIA,
        json.loads(Path('data/guide_extras.json').read_text(encoding='utf-8'))['guides'],media_src,
        APPROVED_PHOTOS['photos'])
    photo_path='screenshot-ps5/'
    photo_title='Screenshot GTA 6 PS5: collabora con GTA VI Italia'
    photo_description=('Screenshot GTA 6 su PS5 e PS5 Pro: scegli tra 55 richieste per migliorare '
                       'le guide italiane. Proponi foto reali su X con verifica e consenso.')
    photo_schema={'@context':'https://schema.org','@type':'CollectionPage',
                  'name':photo_title,'url':url(photo_path),'description':photo_description,
                  'inLanguage':'it-IT'}
    legacy.write(photo_path+'index.html',layout(
        photo_title,photo_description,photo_path,photo_hub,'guide',
        structured=photo_schema))
    legacy.write('photo-requests.json',json.dumps(photo_audit,ensure_ascii=False,indent=2)+'\n')
    new_paths.append(photo_path)
    audit_title='Screenshot GTA 6 PS5: prove, provenienza e permessi'
    audit_desc=('Inventario di 10 screenshot di GTA VI già catalogati e 8 fonti da verificare; '
                'separiamo foto gameplay, attribuzione e diritti di utilizzo.')
    audit_body=render_photo_provenance(PHOTO_REVIEW,MEDIA,guides,media_src)
    audit_schema={'@context':'https://schema.org','@type':'CollectionPage',
                  'name':audit_title,'description':audit_desc,
                  'url':url(PROVENANCE_PATH),'inLanguage':'it-IT'}
    legacy.write(PROVENANCE_PATH+'index.html',layout(
        audit_title,audit_desc,PROVENANCE_PATH,audit_body,'guide',structured=audit_schema))
    legacy.write('photo-provenance-review.json',json.dumps(
        {'schema':PHOTO_REVIEW['schema'],'reviewed':PHOTO_REVIEW['reviewed'],
         'existing_attributed_editorial_images':len(PHOTO_REVIEW['assets']),
         'existing_optimized_local_images':sum(bool(media_src(x['key'])) for x in PHOTO_REVIEW['assets']),
         'new_images_rehosted':0,'permission_records_verified':0,
         'editorial_leads':len(PHOTO_REVIEW['leads'])},ensure_ascii=False,indent=2)+'\n')
    new_paths.append(PROVENANCE_PATH)
    legacy.write('photo-intake-audit.json',json.dumps({
        'schema':APPROVED_PHOTOS['schema'],'reviewed':APPROVED_PHOTOS['reviewed'],
        'approved_new_community_photos':len(APPROVED_PHOTOS['photos']),
        'guide_role_examples':sum(len(roles) for roles in VISUAL_REQUESTS.values()),
        'public_photo_submission':'X compose only, human posts',
        'automatic_publication':False,
        'rights_gate':'explicit consent + human review + local WebP + SHA-256'
    },ensure_ascii=False,indent=2)+'\n')
    ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9')
    editorial_paths=editorial_articles.build(legacy.write,layout,url,legacy.crumbs)
    # The media library is browsable but intentionally excluded from the index.
    new_paths.extend(p for p in editorial_paths if p != editorial_articles.GALLERY_PATH)
    new_paths.extend(patch_archive_v1.build(legacy.write,layout,url,legacy.crumbs))
    tree=ET.parse(OUT/'sitemap.xml'); root=tree.getroot(); ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    existing={loc.text for loc in root.iter(ns+'loc')}
    for path in new_paths:
        if url(path) not in existing:
            row=ET.SubElement(root,ns+'url'); ET.SubElement(row,ns+'loc').text=url(path); existing.add(url(path))
    for row in root:
        path=row.find(ns+'loc').text.removeprefix(BASE+'/')
        mod=row.find(ns+'lastmod')
        if mod is None: mod=ET.SubElement(row,ns+'lastmod')
        mod.text=site_info.iso_modified(path)
    tree.write(OUT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    legacy.write('design-version.json',json.dumps({'version':DESIGN_VERSION,'asset_version':ASSET_VERSION,'guides':len(guides),'image_assets':len(MEDIA),'generated_by':'build_visual_site.py'},indent=2)+'\n')
    print('VISUAL_SITE_BUILT',DESIGN_VERSION,'guides',len(guides),'media',len(MEDIA))


if __name__=='__main__':
    main()
