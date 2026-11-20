#!/usr/bin/env python3
"""Production visual layer. Retains every existing canonical URL and source data.
No generated gameplay imagery, invented popularity, account credentials or API calls.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

import build_site as legacy
import site_info
from visual_guide_content import enrich

e=legacy.e
url=legacy.url
BASE=legacy.BASE
OUT=legacy.OUT
ORIGINAL_LAYOUT=legacy.layout
ORIGINAL_SOURCES=site_info.sources_for
MEDIA=json.loads(Path('data/visual_media.json').read_text(encoding='utf-8'))['images']
CACHE=Path('.visual-media/manifest.json')
LOCAL_MEDIA=json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
ASSET_VERSION=hashlib.sha256(b''.join(Path(p).read_bytes() for p in ('site/assets/visual-v2.css','site/assets/visual-v2.js'))).hexdigest()[:12]
DESIGN_VERSION='visual-v2-20261120'


def brand():
    return '<a class="v-brand" href="'+url()+'"><span class="v-mark" aria-hidden="true">VI</span><span><strong>GTA 6 / ITALIA</strong><small>Guide strategiche in italiano</small></span></a>'


def header(path):
    primary=[('Home',''),('Soldi facili','soldi-facili/'),('Auto speciali','auto-speciali/'),('Salvare auto','salvare-auto/'),('Guide','guide-e-tutorial/')]
    secondary=[('Trofei e platino','trofei/'),('HDR OLED','hdr-oled/'),('Trucchi PS5','trucchi/'),('Scoperte community','scoperte/'),('Fonti e metodo','fonti/')]
    def link(label,target):
        current=' aria-current="page"' if path==target else ''
        return f'<a href="{url(target)}"{current}>{e(label)}</a>'
    main=''.join(link(*item) for item in primary)
    more=''.join(link(*item) for item in secondary)
    x_link=('<a class="v-x-link" href="https://x.com/xFederiko11" '
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
    links=[('Soldi facili','soldi-facili/'),('Auto speciali','auto-speciali/'),('Salvare le auto','salvare-auto/'),('Tutte le guide','guide-e-tutorial/'),('Trofei','trofei/'),('HDR OLED','hdr-oled/'),('Fonti e metodo','fonti/'),('Privacy e visite','privacy/')]
    return ('<footer class="v-footer"><div class="wrap"><div class="v-footer-grid"><div>'+brand()+
            '<p>Guide indipendenti per PS5 e PS5 Pro. Sintesi originali, schermate attribuite e avvisi spoiler. Non affiliato a Rockstar Games.</p></div><nav class="v-footer-links" aria-label="Link utili">'+
            ''.join(f'<a href="{url(p)}">{e(t)}</a>' for t,p in links)+
            '</nav></div><div class="v-footer-note"><span>Le guide possono contenere spoiler. Le schermate appartengono ai rispettivi titolari.</span><a href="https://x.com/xFederiko11" target="_blank" rel="me noopener noreferrer">𝕏 @xFederiko11</a></div></div></footer><a class="v-top" href="#inizio" aria-label="Torna all’inizio">↑</a>')


def layout(title,desc,path,body,section=None,image=None,robots='index,follow',structured=None):
    page=ORIGINAL_LAYOUT(title,desc,path,body,section,image,robots,structured)
    page=re.sub(r'<header class="site-header">.*?</header>',lambda _:header(path),page,count=1,flags=re.S)
    page=re.sub(r'<footer class="footer">.*?</footer>',lambda _:footer(),page,count=1,flags=re.S)
    page=page.replace('<body>',f'<body data-design-version="{DESIGN_VERSION}">',1)
    page=page.replace('</head>',f'<link rel="stylesheet" href="{url("assets/visual-v2.css")}?v={ASSET_VERSION}"><meta name="color-scheme" content="light"></head>',1)
    page=page.replace('</body>',f'<script src="{url("assets/visual-v2.js")}?v={ASSET_VERSION}" defer></script></body>',1)
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
    return f'<img class="v-photo" data-visual-image="{e(key)}" src="{e(original)}"{srcset} alt="{e(record["alt"])}" width="960" height="540" decoding="async"{extra}>'


def figure(key):
    record=MEDIA[key]
    photo=media_src(key)
    credit=(f'<figcaption class="v-caption">{e(record["caption"])} '
            f'<a href="{e(record["source"])}" target="_blank" rel="noopener noreferrer">'
            f'{e(record["credit"])} — apri la fonte ↗</a></figcaption>')
    if not photo:
        return '<figure class="v-unavailable-figure">'+unavailable_media(key)+credit+'</figure>'
    return (f'<figure><a class="v-image-link" href="{e(photo)}" '
            f'data-image-source="{e(record["source"])}" target="_blank" rel="noopener noreferrer" '
            f'aria-label="Ingrandisci: {e(record["alt"])}">'+image(key)+
            '<span class="v-image-label">Ingrandisci ↗</span></a>'+credit+'</figure>')


def reading_time(g):
    count=len((' '.join(g['steps'])+' '+g['summary']+' '+g.get('benefit','')+' '+g.get('caution','')).split())
    return max(1,round(count/180))


def card(g):
    return (f'<article class="v-guide-card" data-category="{e(g["category"])}" data-guide-searchable="{e(g["safe_title"]+" "+g["tag"]+" "+g["summary"])}">'+
            f'<a href="{url(g["canonical_path"])}">'+image(g['hero_media'])+
            '<div class="v-card-copy">'+f'<span class="v-tag">{e(g["tag"])}</span><h3>{e(g["safe_title"])}</h3><p>{e(g["summary"])}</p>'+
            f'<div class="v-card-meta"><span>{len(g["steps"])} passaggi · ~{reading_time(g)} min lettura</span><b>Apri la guida →</b></div></div></a></article>')


def section_head(kicker,title,desc='',href=None):
    tail=f'<a href="{url(href)}">Tutte le guide →</a>' if href else ''
    return '<div class="v-section-head"><div>'+f'<span class="v-kicker">{e(kicker)}</span><h2>{e(title)}</h2>'+ (f'<p>{e(desc)}</p>' if desc else '')+'</div>'+tail+'</div>'


def categories():
    items=[('€','Soldi facili','Dove cercare e cosa raccogliere','soldi-facili/'),('↗','Auto speciali','Zone, richieste e veicoli','auto-speciali/'),('⌂','Salvare le auto','Registrazione e garage','salvare-auto/'),('★','Trofei e platino','Requisiti e checklist','trofei/')]
    return '<nav class="v-categories" aria-label="Scegli il tuo obiettivo">'+''.join(f'<a class="v-category" href="{url(p)}"><span class="v-icon" aria-hidden="true">{e(icon)}</span><span><strong>{e(t)}</strong><small>{e(d)}</small></span><span class="v-arrow" aria-hidden="true">→</span></a>' for icon,t,d,p in items)+'</nav>'


def home(guides):
    by={g['id']:g for g in guides}
    featured=by['registrare-auto-personale']
    hero=('<section class="v-hero">'+image('vice-city',eager=True)+
          '<div><span class="eyebrow">GUIDE IN ITALIANO · PS5 / PS5 PRO</span><h1>GTA 6, senza<br><span>giri a vuoto.</span></h1><p>Trova soldi, scegli la tua prossima auto e scopri come conservarla. Passaggi chiari, mappe quando disponibili e avviso sui possibili spoiler.</p>'+
          f'<a class="v-button" href="{url("soldi-facili/")}">Inizia dai soldi facili →</a></div>'+
          f'<a class="v-featured" href="{url(featured["canonical_path"])}">'+image('save-car')+
          '<div class="v-featured-copy"><span class="v-kicker">DA SAPERE PRIMA DI RIPARTIRE</span><h2>Hai trovato un’auto che vuoi tenere?</h2><p>Parcheggio, registrazione e richiamo: non sono la stessa cosa. Apri la guida →</p></div></a></section>'+
          '<p class="v-hero-credit">Sfondo promozionale: <a href="https://www.rockstargames.com/VI/">Rockstar Games</a> · Schermata veicolo: <a href="https://www.pushsquare.com/guides/gta-6-tips-and-tricks-you-need-to-know">Push Square</a></p>')
    chosen=[by[k] for k in ('soldi-facili-capitolo-1','registrare-auto-personale','sportive-randy-posizioni')]
    body=categories()+hero+'<section class="v-section">'+section_head('LE PRIORITÀ','Soldi, auto, garage. Parti da qui.','Tre percorsi pratici, senza mescolare notizie e tutorial.','guide-e-tutorial/')+'<div class="v-grid">'+''.join(card(g) for g in chosen)+'</div></section>'
    body+='<section class="v-section v-promo">'+image('scooter-menu')+'<div><span class="eyebrow">NON PERDERE IL MEZZO CHE HAI SCELTO</span><h2>Prima di scendere,<br>pensa a come ritrovarlo.</h2><p>La guida distingue un’auto lasciata in parcheggio da un veicolo registrato. Segui i passaggi e controlla la conferma nel gioco.</p>'+f'<a class="v-button" href="{url("salvare-auto/")}">Apri la guida al garage →</a></div></section>'
    remaining=[by[k] for k in ('scansionare-veicoli','viaggio-rapido-taxi','70-sfide-100-percento')]
    body+='<section class="v-section">'+section_head('PICCOLE AZIONI, MENO TEMPO PERSO','Continua con le guide pratiche')+'<div class="v-grid">'+''.join(card(g) for g in remaining)+'</div></section>'
    body+='<section class="v-section">'+section_head('ANCHE NEL SITO','Platino e immagine, senza confusione')+'<div class="v-links">'+f'<a class="v-button secondary" href="{url("trofei/")}">Checklist trofei</a><a class="v-button secondary" href="{url("hdr-oled/")}">Trova la tua TV OLED</a><a class="v-button secondary" href="{url("scoperte/")}">Scoperte della community</a></div></section>'
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
    body+='<section data-guide-directory aria-label="Catalogo delle guide"><div class="v-filterbar" id="cerca-guide"><label><span class="micro">Cerca per obiettivo</span><br><input type="search" data-guide-search placeholder="Es. soldi, auto, taxi…" aria-label="Cerca una guida"></label>'
    if kind=='all':
        body+='<div class="v-filters" role="group" aria-label="Filtra per obiettivo">'+''.join(f'<button type="button" data-guide-filter="{value}" aria-pressed="{str(value=="all").lower()}">{label}</button>' for value,label in [('all','Tutte'),('soldi','Soldi'),('auto','Auto'),('garage','Garage'),('inizio','Altre guide')])+'</div>'
    body+=f'</div><p class="v-result" data-guide-result role="status" aria-live="polite">{len(selected)} guide disponibili</p><div class="v-grid">'+''.join(card(g) for g in selected)+'</div></section>'
    if kind=='soldi':
        body+='<section class="v-section v-promo">'+image('bank-phone')+'<div><span class="eyebrow">DOPO AVER RACCOLTO IL BOTTINO</span><h2>Non tenere tutto nel portafoglio.</h2><p>Quando BuckMe è disponibile, apri il telefono, scegli BuckMe → ATM Finder e raggiungi il bancomat indicato. Controlla e deposita il contante.</p><p class="v-caption">Fonte e schermata: <a href="https://www.pushsquare.com/guides/gta-6-tips-and-tricks-you-need-to-know">Push Square — proteggere il denaro</a>.</p></div></section>'
    return title,desc,path,body


def sources(g,media_keys):
    links=list(dict.fromkeys([g['source_url'],*g.get('extra_sources',[]),*[MEDIA[k]['source'] for k in media_keys]]))
    names={'powerpyx.com':'PowerPyx','pushsquare.com':'Push Square','insider-gaming.com':'Insider Gaming','gamesradar.com':'GamesRadar+','rockstargames.com':'Rockstar Games'}
    body='<section class="v-sources" id="fonti"><h2>Fonti, immagini e verifica</h2><ul>'
    for source in links:
        host=urlsplit(source).hostname.removeprefix('www.')
        body+=f'<li><a href="{e(source)}" target="_blank" rel="noopener noreferrer">{e(names.get(host,host))} — apri il riferimento ↗</a></li>'
    body+='</ul><p>Testo sintetizzato e riorganizzato in italiano. Le schermate sono attribuite ai rispettivi editori e a Rockstar Games; le immagini promozionali sono dichiarate e non provano una posizione o un passaggio.</p>'
    body+='<p>Le indicazioni riportano le fonti, non test personali. Ricontrolla i prompt della tua patch. Nessuna certificazione automatica di compatibilità tra exploit e trofei.</p></section>'
    return body


def guide(g,guides):
    path=g['canonical_path']
    title=g['safe_title']
    body=legacy.crumbs([('Guide','guide-e-tutorial/'),(title,path)])
    body+='<section class="v-intro"><div>'+f'<span class="v-tag">{e(g["tag"])} · PS5</span><h1>{e(title)}</h1><p>{e(g["summary"])}</p><div class="v-read-meta"><span>{len(g["steps"])} passaggi</span><span>~{reading_time(g)} min di lettura</span><span>Fonti in fondo</span></div><a class="v-button" href="#procedura">Vai ai passaggi ↓</a></div><figure>'+image(g['hero_media'],eager=True)+f'<figcaption class="v-caption">{e(MEDIA[g["hero_media"]]["caption"])}</figcaption></figure></section>'
    body+='<div class="v-guide-layout"><article class="v-guide-main">'
    benefit=g.get('benefit','')
    body+=f'<div class="v-answer"><strong>La cosa da sapere</strong><p>{e(benefit)}</p></div><div class="v-facts"><div class="v-fact"><strong>Prima di iniziare</strong><p>{e(g["requirements"])}</p></div><div class="v-fact"><strong>Dove andare</strong><p>{e(g["location"])}</p></div></div>'
    body+='<section id="procedura">'+section_head('UNA COSA ALLA VOLTA','Il percorso, passo per passo')
    if g['spoiler']:
        body+='<div class="v-spoiler-warning" role="note"><strong>⚠️ Questa guida contiene spoiler.</strong> Continuando leggerai luoghi, obiettivi e ricompense.</div>'
        body+=f'<div class="v-fact"><strong>Riferimenti e bottino</strong><p>{e(g.get("benefit",""))}</p></div>'
    body+='<ol class="v-steps">'
    used=[g['hero_media']]
    for n,raw in enumerate(g['steps']):
        text=re.sub(r'^SPOILER(?: LUOGHI)?:\s*','',raw)
        heading=g['step_headings'][n] if n<len(g['step_headings']) else 'Segui il passaggio'
        body+=f'<li class="v-step" id="passaggio-{n+1}"><div class="v-step-head"><span class="v-step-n" aria-hidden="true">{n+1:02d}</span><div><h3>{e(heading)}</h3><p>{e(text)}</p></div></div>'
        key=g['step_media'].get(n)
        if key:
            body+=figure(key); used.append(key)
        checks=g.get('checks',[])
        if n<len(checks):
            body+=f'<p class="v-check"><strong>Controllo:</strong> {e(checks[n])}</p>'
        body+='</li>'
    body+='</ol>'
    if not g['step_media']:
        body+='<div class="v-no-image">Non abbiamo ancora una schermata verificata per ogni passaggio di questa guida. I riferimenti disponibili restano nella fonte: non li sostituiamo con una mappa inventata.<br>'+f'<a href="{e(g["source_url"])}" target="_blank" rel="noopener noreferrer">Apri la guida di riferimento ↗</a></div>'
    body+='</section>'+f'<aside class="v-notice"><strong>Prima di continuare</strong>{e(g.get("caution","Controlla il progresso in gioco."))}</aside>'
    if g['id']=='poligoni-concentrazione':
        body+=f'<p><a class="v-button secondary" href="{url("trofei/trofeo-17-cecchino/")}">Apri la checklist delle medaglie →</a></p>'
    body+=sources(g,used)+'</article><aside class="v-guide-aside"><h2>In questa guida</h2><a href="#procedura">Il percorso passo per passo</a><a href="#fonti">Fonti e immagini</a>'+f'<a href="{url("soldi-facili/")}">Altri modi per fare soldi</a><a href="{url("auto-speciali/")}">Auto e garage</a><a href="{url("trofei/")}">Percorso platino</a></aside></div>'
    related=[x for x in guides if x['id']!=g['id'] and (x['category']==g['category'] or x['category'] in ('garage','soldi'))][:3]
    body+='<section class="v-section">'+section_head('IL PROSSIMO PASSO','Potrebbero servirti anche')+'<div class="v-grid">'+''.join(card(x) for x in related)+'</div></section>'
    structured=legacy.schema_article(title,g['summary'],url(path),media_src(g['hero_media']))
    legacy.write(path+'index.html',layout(title+' | Guida GTA 6 PS5',g['summary'],path,body,'guide',media_src(g['hero_media']),structured=structured))


def validate(guides):
    seen=set()
    allowed={'powerpyx.com','www.powerpyx.com','insider-gaming.com','www.insider-gaming.com','www.pushsquare.com','www.gamesradar.com'}
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
    records=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
    records+=json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides']
    guides=enrich(records)
    validate(guides)
    site_info.sources_for=lambda path: ORIGINAL_SOURCES(path)+('build_visual_site.py','visual_guide_content.py','data/visual_guides.json','data/visual_media.json','site/assets/visual-v2.css','site/assets/visual-v2.js')
    site_info.last_modified_at.cache_clear()
    legacy.layout=layout
    legacy.main()
    title='GTA 6 Italia: soldi facili, auto speciali e guide PS5'
    desc='Guide GTA VI in italiano: soldi facili, auto speciali, garage, trofei e HDR OLED. Passaggi chiari, immagini attribuite e avviso spoiler.'
    legacy.write('index.html',layout(title,desc,'',home(guides),'home',structured={'@context':'https://schema.org','@type':'WebSite','name':'GTA 6 Italia','url':url(),'inLanguage':'it-IT'}))
    new_paths=[]
    for kind in ('all','soldi','auto'):
        title,desc,path,body=directory(guides,kind)
        legacy.write(path+'index.html',layout(title+' | GTA 6 Italia',desc,path,body,'guide',structured={'@context':'https://schema.org','@type':'CollectionPage','name':title,'url':url(path),'inLanguage':'it-IT'}))
        new_paths.append(path)
    for g in guides:
        guide(g,guides); new_paths.append(g['canonical_path'])
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
