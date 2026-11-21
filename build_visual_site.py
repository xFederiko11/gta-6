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
from visual_guide_content import enrich
from community_social_v1 import home_rail
from meditation_tracker_v1 import render as render_meditation_tracker
from x_growth_dashboard_v1 import (render as render_growth_dashboard, read_report as growth_report,
                                   to_json as export_growth_report, PATH as GROWTH_PATH)
from photo_request_hub_v1 import render as render_photo_hub
from photo_coverage_v5 import audit as audit_photo_coverage, render as render_photo_coverage, json_report as export_photo_coverage, PATH as PHOTO_COVERAGE_PATH
from platinum_roadmap_v1 import render as render_platinum_roadmap, ROADMAP_PATH
from guide_step_references_v1 import render as render_step_evidence, validate as validate_step_evidence
from step_image_sources_v1 import load as load_step_photo_sources, validate as validate_step_photo_sources, render as render_step_photo_source
from platinum_atlas_v2 import render as render_trophy_atlas, validate as validate_trophy_atlas
from advanced_platinum_v3 import (render_100 as render_advanced_100, render_hard as render_advanced_hard,
                                  validate as validate_advanced, COLLECTIBLE_PATH, HARD_PATH)
from photo_provenance_v3 import render as render_photo_provenance, validate as validate_provenance, PATH as PROVENANCE_PATH
from collectible_routes_v4 import render as render_collectible_routes, validate_routes, PATH as COLLECTIBLE_ROUTE_PATH
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
COLLECTIBLE_ROUTES=json.loads(Path('data/collectible_routes_v4.json').read_text(encoding='utf-8'))
APPROVED_PHOTOS=json.loads(Path('data/approved_screenshots_v4.json').read_text(encoding='utf-8'))
TROPHY_ITEMS=json.loads(Path('data/trofei.json').read_text(encoding='utf-8'))['trophies']
TROPHY_MAP_PATHS={'trofei/'+row['slug']+'/':row for row in TROPHY_ITEMS}
GUIDE_MAP_PATHS=set()
MAP_RENDER_PATHS=set(TROPHY_MAP_PATHS)|{MAP_HUB_PATH,COLLECTIBLE_ROUTE_PATH}
CACHE=Path('.visual-media/manifest.json')
LOCAL_MEDIA=json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
ASSET_VERSION=hashlib.sha256(b''.join(Path(p).read_bytes() for p in ('site/assets/visual-v2.css','site/assets/visual-v2.js'))).hexdigest()[:12]
DESIGN_VERSION='visual-v2-20261120'


def brand():
    return '<a class="v-brand" href="'+url()+'"><span class="v-mark" aria-hidden="true">VI</span><span><strong>GTA 6 / ITALIA</strong><small>Guide strategiche in italiano</small></span></a>'


def header(path):
    primary=[('Home',''),('Soldi facili','soldi-facili/'),('Auto speciali','auto-speciali/'),('Salvare auto','salvare-auto/'),('Guide','guide-e-tutorial/')]
    secondary=[('Trofei e platino','trofei/'),('Roadmap platino','trofei/roadmap-platino/'),('Checklist 100%','trofei/100-percento/'),('Percorsi collezionabili','collezionabili/percorsi/'),('Trofei difficili','trofei/trofei-difficili/'),('Mappe dei luoghi','mappe-guide/'),('HDR OLED','hdr-oled/'),('Trucchi PS5','trucchi/'),('Scoperte community','scoperte/'),('Screenshot PS5','screenshot-ps5/'),('Invia screenshot','screenshot-ps5/invia/'),('Fonti e metodo','fonti/')]
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
            '<div class="v-spoilerbar"><div class="wrap v-spoiler-inner">'
            '<p><strong>⚠️ Attenzione spoiler:</strong> proseguendo potresti leggere dettagli di missioni, luoghi e ricompense.</p>'
            '</div></div>')

def footer():
    links=[('Roadmap platino','trofei/roadmap-platino/'),('Checklist 100%','trofei/100-percento/'),('Percorsi collezionabili','collezionabili/percorsi/'),('Trofei difficili','trofei/trofei-difficili/'),('Invia foto','screenshot-ps5/invia/'),('Mappe e luoghi','mappe-guide/'),('Soldi facili','soldi-facili/'),('Auto speciali','auto-speciali/'),('Salvare le auto','salvare-auto/'),('Tutte le guide','guide-e-tutorial/'),('Trofei','trofei/'),('HDR OLED','hdr-oled/'),('Foto della community','screenshot-ps5/'),('Fonti e metodo','fonti/'),('Privacy e visite','privacy/')]
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
    page=ORIGINAL_LAYOUT(title,desc,path,body,section,image,robots,structured)
    page=re.sub(r'<header class="site-header">.*?</header>',lambda _:header(path),page,count=1,flags=re.S)
    page=re.sub(r'<footer class="footer">.*?</footer>',lambda _:footer(),page,count=1,flags=re.S)
    page=page.replace('<body>',f'<body data-design-version="{DESIGN_VERSION}">',1)
    page=page.replace('</head>',f'<link rel="stylesheet" href="{url("assets/visual-v2.css")}?v={ASSET_VERSION}"><meta name="color-scheme" content="light"></head>',1)
    page=page.replace('</body>',f'<script src="{url("assets/visual-v2.js")}?v={ASSET_VERSION}" defer></script></body>',1)
    if path == GROWTH_PATH:
        css='x-growth-dashboard-v1.css'
        version=hashlib.sha256(Path('site/assets',css).read_bytes()).hexdigest()[:12]
        page=page.replace('</head>',f'<link rel="stylesheet" href="{url("assets/"+css)}?v={version}"></head>',1)
    if path in MAP_RENDER_PATHS or path in GUIDE_MAP_PATHS:
        css,js='interactive-map-v1.css','interactive-map-v1.js'
        version=hashlib.sha256(Path('site/assets',css).read_bytes()+Path('site/assets',js).read_bytes()).hexdigest()[:12]
        page=page.replace('</head>',f'<link rel="stylesheet" href="{url("assets/"+css)}?v={version}"></head>',1)
        page=page.replace('</body>',f'<script src="{url("assets/"+js)}?v={version}" defer></script></body>',1)
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
    """Never hotlink a provider asset when local optimization failed.

    A third-party URL can expire, rate-limit, or reject mobile browsers.
    Instead, readers get an attributed, actionable source link.
    """
    local=LOCAL_MEDIA.get(key,{})
    candidate=local.get(str(width))
    if candidate and candidate.startswith('assets/visual/') and Path('site',candidate).is_file():
        return url(candidate)
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
        if u.scheme!='https' or u.hostname not in ('trari.com','www.trari.com','www.dexerto.com'):
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
        if not isinstance(chapters,list) or len(chapters)>5:
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
    """Plain indexed card: no illustrative screenshot confused for game instructions."""
    return (
        f'<article class="v-guide-card v-guide-card-plain" data-category="{e(g["category"])}" '
        f'data-guide-searchable="{e(g["safe_title"]+" "+g["tag"]+" "+g["summary"])}">'
        f'<a href="{url(g["canonical_path"])}">'
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
    by={g['id']:g for g in guides}
    featured=by['registrare-auto-personale']
    hero=('<section class="v-hero">'+image('vice-city',eager=True)+
          '<div><span class="eyebrow">GUIDE IN ITALIANO · PS5 / PS5 PRO</span><h1>GTA 6, senza<br><span>giri a vuoto.</span></h1><p>Trova soldi, scegli la tua prossima auto e scopri come conservarla. Passaggi chiari, mappe quando disponibili e avviso sui possibili spoiler.</p>'+
          f'<a class="v-button" href="{url("soldi-facili/")}">Inizia dai soldi facili →</a></div>'+
          f'<a class="v-featured" href="{url(featured["canonical_path"])}"><span class="v-featured-symbol" aria-hidden="true">🚗</span>'+
          '<div class="v-featured-copy"><span class="v-kicker">DA SAPERE PRIMA DI RIPARTIRE</span><h2>Hai trovato un’auto che vuoi tenere?</h2><p>Parcheggio, registrazione e richiamo: non sono la stessa cosa. Apri la guida →</p></div></a></section>'+
          '<p class="v-hero-credit">Immagine ufficiale di GTA VI, non la schermata di un tutorial. Fonte: <a href="https://www.rockstargames.com/VI/">Rockstar Games</a>.</p>')
    chosen=[by[k] for k in ('soldi-facili-capitolo-1','registrare-auto-personale','sportive-randy-posizioni')]
    body=categories()+hero+'<section class="v-section">'+section_head('LE PRIORITÀ','Soldi, auto, garage. Parti da qui.','Tre percorsi pratici, senza mescolare notizie e tutorial.','guide-e-tutorial/')+'<div class="v-grid">'+''.join(card(g) for g in chosen)+'</div></section>'
    body+=('<aside class="v-follow-home" aria-label="Seguici su X per nuove guide">'
           '<div><span class="v-kicker">𝕏 SEGUI IL PROGETTO</span>'
           '<h2>Soldi, auto e platino: le prossime scoperte arrivano su X.</h2>'
           '<p>Guide in italiano, segnalazioni con fonti e novità per PS5 e PS5 Pro. '
           'Seguici per ritrovare le nuove procedure appena pubblicate.</p></div>'
           '<a class="v-button" href="https://x.com/intent/follow?screen_name=xFederiko11" '
           'target="_blank" rel="noopener noreferrer">𝕏 Segui @xFederiko11</a>'
           '</aside>')
    body+='<section class="v-section v-promo v-promo-no-media"><div><span class="eyebrow">GUIDA PRATICA · 7 PASSAGGI</span><h2>Come salvare un’auto e ritrovarla</h2><p>Parcheggio, registrazione e richiamo non sono la stessa cosa. Segui solo le istruzioni della procedura.</p>'+f'<a class="v-button" href="{url("salvare-auto/")}">Leggi il tutorial →</a></div></section>'
    remaining=[by[k] for k in ('scansionare-veicoli','viaggio-rapido-taxi','70-sfide-100-percento')]
    body+='<section class="v-section">'+section_head('PICCOLE AZIONI, MENO TEMPO PERSO','Continua con le guide pratiche')+'<div class="v-grid">'+''.join(card(g) for g in remaining)+'</div></section>'
    body+=('<section class="v-photo-hub-invite"><div>'
           '<span class="v-kicker">📸 GTA VI ITALIA · FOTO COMMUNITY</span>'
           '<h2>Hai uno screenshot PS5 che può aiutare altri giocatori?</h2>'
           '<p>Mappe, comandi, menu e risultati reali: scegli fra esempi di fotografie che mostrano dove andare, quali tasti premere e cosa controllare. Solo immagini autentiche, mai schermate inventate.</p>'
           '</div><a class="v-button secondary" href="'+url('screenshot-ps5/')+'">Scopri le richieste di screenshot →</a>'
           '</section>')
    body+=home_rail()
    body+='<section class="v-section">'+section_head('ANCHE NEL SITO','Platino e immagine, senza confusione')+'<div class="v-links">'+f'<a class="v-button secondary" href="{url("trofei/roadmap-platino/")}">Roadmap Platino</a><a class="v-button secondary" href="{url("mappe-guide/")}">Mappe e luoghi</a><a class="v-button secondary" href="{url("hdr-oled/")}">Trova la tua TV OLED</a><a class="v-button secondary" href="{url("scoperte/")}">Scoperte della community</a></div></section>'
    return body


def directory(guides,kind='all'):
    config={
        'all':('Guide GTA 6: scegli cosa fare','Tutti i percorsi in italiano. Cerca un obiettivo, apri una guida e segui i passaggi.','guide-e-tutorial/'),
        'soldi':('Soldi facili, percorsi chiari.','Luoghi e bottino del Capitolo 1. Controlla i rischi prima di partire: niente promesse di guadagni infiniti.','soldi-facili/'),
        'auto':('Trova l’auto. Poi tienila.','Richieste, ricerca dei veicoli e garage: scegli il percorso giusto senza confondere consegna e conservazione.','auto-speciali/'),
    }
    title,desc,path=config[kind]
    selected=guides if kind=='all' else [g for g in guides if g['category']==kind or (kind=='auto' and g['category']=='garage')]
    body=legacy.crumbs([(title,path)])+f'<section class="v-directory-head"><span class="eyebrow">GTA 6 · GUIDE OPERATIVE</span><h1>{e(title)}</h1><p>{e(desc)}</p></section>'
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
    body=legacy.crumbs([('Guide','guide-e-tutorial/'),(title,path)])
    body+=('<section class="v-intro v-guide-intro" aria-label="Introduzione alla guida">'
           '<span class="v-tag">'+e(g['tag'])+' · PS5 / PS5 Pro</span>'
           '<h1>'+e(title)+'</h1>'
           '<p>'+e(g['summary'])+'</p>'
           '<span class="v-guide-step-count">'+str(count)+' passaggi pratici</span>'
           '</section>')
    body+='<div class="v-guide-layout v-guide-single"><article class="v-guide-main">'
    controls={
        'registrare-auto-personale':'↑ croce direzionale · R1 · △ (Triangolo) · levetta destra',
        'prima-persona-glitch-ps5':'OPTIONS · ↑ croce direzionale · ○ (Cerchio) · touchpad',
        'scansionare-veicoli':'↑ croce direzionale · WAiNK (segui i comandi a schermo)',
        'viaggio-rapido-taxi':'Telefono → Contatti → Paradise Taxi'
    }
    body+=('<details class="v-guide-prep">'
           '<summary>Prima di iniziare: requisiti e luogo di partenza</summary>'
           '<div class="v-guide-prep-content">'
           '<p><strong>Serve:</strong> '+e(g["requirements"])+'</p>'
           '<p><strong>Dove:</strong> '+e(g["location"])+'</p>'
           +('<p class="v-guide-controls"><strong>Comandi PS5:</strong> '+e(controls[g['id']])+'</p>' if g['id'] in controls else '')
           +'</div></details>')
    # Critical trophy/save warnings must remain visible BEFORE the first step.
    if g['id'] in {'soldi-facili-capitolo-1','soldi-2500-three-sheets-liquor'}:
        body+=('<p class="v-guide-urgent" role="note"><strong>⚠️ Non perdere i soldi:</strong> '
               'il denaro del Capitolo 1 può andare perso avanzando nella storia. '
               'Prima di accumularlo, crea un salvataggio manuale separato e leggi '
               'le precauzioni sotto il tutorial.</p>')
    if g['id']=='prima-persona-glitch-ps5':
        body+=('<p class="v-guide-urgent" role="note"><strong>🏆 Trofei non verificati.</strong> '
               'Non usare il salvataggio principale del platino: crea prima '
               'un salvataggio di prova separato.</p>')
    if g['id']=='meditazione-capitolo-1':
        body+=('<p class="v-guide-urgent" role="note"><strong>🏆 Prima meditazione mancabile:</strong> '
               'completala durante il Capitolo 1, prima di proseguire nella storia.</p>')
    body+=('<section id="procedura" class="v-tutorial" aria-labelledby="titolo-procedura">'
           '<header class="v-tutorial-head">'
           '<span class="v-tutorial-start-here">▶ INIZIA QUI</span>'
           '<h2 id="titolo-procedura">TUTORIAL · ISTRUZIONI DA SEGUIRE</h2>'
           '<p>Questa è la procedura da eseguire. Segui i passaggi in ordine.</p>'
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
        body+=('<aside class="v-glitch-status" role="note"><strong>🟡 Probabilmente funzionante su PS5 · 19–20 novembre 2026</strong>'
               '<p>PC Gamer riferisce una prova indipendente sul lancio, '
               'ma la <strong>patch esatta non è documentata</strong> e Rockstar potrebbe correggere il metodo. '
               'È un cambio di visuale, non un glitch soldi o XP.</p>'
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
    allowed={'powerpyx.com','www.powerpyx.com','insider-gaming.com','www.insider-gaming.com','www.pushsquare.com','www.gamesradar.com','www.gtabase.com','gtabase.com','gta.tech4gamers.com','www.videogameschronicle.com','www.pcgamer.com','www.dexerto.com','www.reddit.com'}
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
    records=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
    records+=json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides']
    guides=enrich(records)
    validate(guides)
    for guide_id,items in PHOTO_STEP_REVIEW.get('context_approved',{}).items():
        guide=next((g for g in guides if g['id']==guide_id),None)
        if guide is None:
            raise ValueError('Photo context for unknown guide: '+guide_id)
        for index,item in items.items():
            if not index.isdigit() or int(index)>=len(guide['steps']) or int(index)<0:
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
    validate_routes(COLLECTIBLE_ROUTES)
    validate_approved(APPROVED_PHOTOS,guides,VISUAL_REQUESTS)
    PHOTO_COVERAGE=audit_photo_coverage(guides,VISUAL_REQUESTS,APPROVED_PHOTOS,PHOTO_REVIEW)
    site_info.sources_for=lambda path: ORIGINAL_SOURCES(path)+('build_visual_site.py','collectible_routes_v4.py','data/collectible_routes_v4.json','photo_intake_v4.py','data/approved_screenshots_v4.json','advanced_platinum_v3.py','data/advanced_platinum_v3.json','photo_provenance_v3.py','data/photo_provenance_review_v3.json','visual_guide_content.py','data/visual_guides.json','data/visual_media.json','data/visual_requests.json','data/guide_visual_refs.json','data/guide_step_refs.json','guide_step_references_v1.py','data/step_image_sources_v1.json','step_image_sources_v1.py','data/guide_locations_v2.json','guide_location_atlas_v2.py','data/map_external_permalinks_v1.json','interactive_article_maps_v1.py','site/assets/interactive-map-v1.css','site/assets/interactive-map-v1.js','data/guide_extras.json','photo_request_hub_v1.py','data/meditation_checklist_v1.json','meditation_tracker_v1.py','site/assets/visual-v2.css','site/assets/visual-v2.js') + (('platinum_roadmap_v1.py','platinum_atlas_v2.py','data/platinum_trophy_routes_v2.json','site/assets/platinum-roadmap.css','site/assets/platinum-roadmap.js','site/assets/platinum-atlas-v2.css','site/assets/platinum-atlas-v2.js') if path==ROADMAP_PATH else ())
    site_info.last_modified_at.cache_clear()
    legacy.layout=layout
    from community_discovery_v2 import render as community_render
    legacy.render_community_page=community_render
    legacy.main()
    roadmap_title='Roadmap Platino GTA 6 PS5: guida ai 55 trofei'
    roadmap_desc='Roadmap per il Platino di GTA VI su PS5: meditazioni mancabili, 5 fasi, 100%, medaglie Oro e checklist privata dei progressi.'
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
        render_interactive_map('I 123 checkpoint di Leonida',
           interactive_collectible_points(COLLECTIBLE_ROUTES),id_suffix='collectibles',
           page_label='raccolta',curated_refs=EXTERNAL_MAP_REFS['items'])+
           render_collectible_routes(COLLECTIBLE_ROUTES,EXTERNAL_MAP_REFS['items']),
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
    for kind in ('all','soldi','auto'):
        title,desc,path,body=directory(guides,kind)
        legacy.write(path+'index.html',layout(title+' | GTA 6 Italia',desc,path,body,'guide',structured={'@context':'https://schema.org','@type':'CollectionPage','name':title,'url':url(path),'inLanguage':'it-IT'}))
        new_paths.append(path)
    for g in guides:
        guide(g,guides); new_paths.append(g['canonical_path'])
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
