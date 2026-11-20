#!/usr/bin/env python3
"""Final idempotent reader pass. Run with --build for the production pipeline.

Canonical URLs, H1s and structured data remain; guide spoilers are visible after warning.
No network calls, invented claims or credentials. Source timestamps use Git.
"""
from __future__ import annotations
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlsplit

ROOT = Path('_site')
BASE = 'https://xfederiko11.github.io/gta-6/'
VERSION = 'reader-adaptive-v2-20261120'
ASSETS = ('reader-theme.css', 'reader-theme.js', 'community-social-v1.js')
BOOT = '''<meta name="color-scheme" content="light dark">
<style id="reader-first-paint">html{background:#fcf8fc;color-scheme:light}html[data-theme="dark"]{background:#0c0b13;color-scheme:dark}@media(max-width:760px){html[data-theme="auto"]{background:#0c0b13;color-scheme:dark}}body{background:inherit}</style>
<script id="reader-theme-boot">(function(){var t=matchMedia('(max-width:760px)').matches?'dark':'light';try{var v=localStorage.getItem('gta6-theme-v1');if(v==='light'||v==='dark')t=v;}catch(e){}document.documentElement.dataset.theme=t;document.documentElement.style.colorScheme=t;})();</script>'''
CONTROLS = '''<div class="r-theme-control"><span>Aspetto</span><div class="v-switch" role="group" aria-label="Scegli tema scuro o chiaro"><button type="button" data-theme-choice="dark" aria-pressed="false">Scuro</button><button type="button" data-theme-choice="light" aria-pressed="false">Chiaro</button></div></div>'''
DIALOG = '''<dialog class="r-lightbox" data-image-dialog aria-labelledby="reader-image-title"><header><strong id="reader-image-title" data-image-title>Immagine della guida</strong><div class="r-lightbox-tools"><button type="button" data-image-zoom aria-pressed="false">Zoom 2x</button><button type="button" data-image-close autofocus>Chiudi</button></div></header><div class="r-lightbox-viewport" data-image-viewport data-zoom="false"><img alt="" width="960" height="540"></div><p><a data-image-credit target="_blank" rel="noopener noreferrer">Fonte originale</a> &middot; Colori originali, nessuna mappa ridisegnata. Premi Esc per chiudere.</p></dialog>'''
LABELS = {'tip':'Consiglio utile', 'avoid':'Da evitare', 'curiosity':'Curiosità'}
HOSTS = {'www.powerpyx.com','powerpyx.com','insider-gaming.com','www.pushsquare.com','www.gamesradar.com'}


def validate(data):
    if data.get('schema') != 'guide-extras-v1':
        raise ValueError('Unsupported guide extras schema')
    for path, entry in data['guides'].items():
        if not re.fullmatch(r'(?:[a-z0-9-]+/)+', path):
            raise ValueError('Unsafe guide path')
        if not isinstance(entry.get('spoiler'), bool):
            raise ValueError('Explicit spoiler classification required')
        if not entry.get('tips') or not entry.get('checked'):
            raise ValueError('Empty or undated tips are not published')
        for tip in entry['tips']:
            if tip['kind'] not in LABELS or not tip['title'] or not tip['text']:
                raise ValueError('Incomplete editorial tip')
            source = urlsplit(tip['source'])
            if source.scheme != 'https' or source.hostname not in HOSTS or source.username or source.password or source.port not in (None,443):
                raise ValueError('Unapproved tip source')
    return True


def render_extras(entry):
    from build_visual_site import figure, MEDIA
    esc = html.escape
    refs = list(dict.fromkeys(tip['source'] for tip in entry['tips']))
    tips = '<section class="r-extra" id="consigli"><h2>Consigli e curiosità</h2><p class="r-extra-intro">Dettagli utili per questo percorso, con le fonti in fondo alla guida.</p>'
    for tip in entry['tips']:
        number = refs.index(tip['source']) + 1
        tips += (f'<article class="r-tip" data-kind="{tip["kind"]}"><span class="r-tip-label">{LABELS[tip["kind"]]}</span>'
                 f'<h3>{esc(tip["title"])}</h3><p>{esc(tip["text"])} '
                 f'<sup><a href="#extra-fonte-{number}" aria-label="Fonte del consiglio: {number}">[{number}]</a></sup></p></article>')
    tips += '</section>'
    gallery = ''
    if entry.get('gallery'):
        gallery = '<section class="r-extra" id="mappa"><h2>'+esc(entry.get('gallery_title','Immagini di riferimento'))+'</h2><p class="r-extra-intro">Tocca una schermata per aprirla e ingrandire i riferimenti. Le immagini mantengono i colori originali.</p><div class="r-gallery">'
        for item in entry['gallery']:
            key = item['key']
            if key not in MEDIA or MEDIA[key]['kind'] != 'screenshot':
                raise ValueError('Only attributed screenshots can document locations')
            if MEDIA[key].get('spoiler') and not entry['spoiler']:
                raise ValueError('Spoiler screenshot must stay protected')
            gallery += '<div><h3 class="r-media-heading">'+esc(item['label'])+'</h3>'+figure(key)+'</div>'
        gallery += '</div></section>'
    source_html = '<h3>Fonti dei consigli</h3><ol>'
    for n, source in enumerate(refs, 1):
        name = urlsplit(source).hostname.removeprefix('www.')
        source_html += f'<li id="extra-fonte-{n}"><a href="{esc(source,quote=True)}" target="_blank" rel="noopener noreferrer">{esc(name)} &mdash; approfondimento {n}</a></li>'
    source_html += '</ol><p>Consigli ricontrollati il '+esc(entry['checked'])+'. Sintesi delle fonti, non test personali; nessuna certificazione di exploit o trofei.</p>'
    return gallery, tips, source_html


def augment_guide(page, entry):
    """Place maps and sourced advice directly in the readable article flow."""
    gallery,tips,refs = render_extras(entry)
    source_marker = '<section class="v-sources" id="fonti">'
    if source_marker not in page:
        raise ValueError('Guide source section missing')
    keys = {item['key'] for item in entry.get('gallery', [])}
    # Avoid duplicate screenshot galleries; retain the original source credits.
    if keys:
        page = re.sub(r'<figure>.*?</figure>',
                      lambda match: '' if any(f'data-visual-image="{key}"' in match[0] for key in keys) else match[0],
                      page, flags=re.S)
    if gallery:
        before_steps='<ol class="v-steps">'
        if before_steps not in page:
            raise ValueError('Guide steps missing')
        page=page.replace(before_steps,gallery+before_steps,1)
    page=page.replace(source_marker,tips+source_marker,1)
    page=page.replace('<h2>Fonti, immagini e verifica</h2>',
                      '<h2>Fonti, immagini e verifica</h2>'+refs,1)
    page=page.replace('<a href="#fonti">Fonti e immagini</a>',
                      '<a href="#consigli" data-reader-anchor>Consigli e curiosità</a><a href="#fonti">Fonti e immagini</a>',1)
    if gallery:
        page=page.replace('<a href="#procedura">Il percorso passo per passo</a>',
                          '<a href="#procedura">Il percorso passo per passo</a><a href="#mappa" data-reader-anchor>Mappa e immagini</a>',1)
    return page

def gsc_verification_meta(token):
    """Explicitly configured public Search Console proof; never a tracker."""
    if token is None or token == '':
        return ''
    if not isinstance(token,str) or not re.fullmatch(r'[A-Za-z0-9_-]{10,160}',token):
        raise ValueError('Invalid Search Console verification token')
    return '<meta name="google-site-verification" content="'+token+'">'


def transform(page, *, version, entry=None, discussion_path=None, gsc_token=None):
    if f'name="reader-version" content="{VERSION}"' in page:
        return page
    if entry:
        page = augment_guide(page, entry)
    page = re.sub(r'<meta name="color-scheme"[^>]*>', '', page)
    page = re.sub(r'<meta name="theme-color"[^>]*>', '<meta name="theme-color" content="#fcf8fc">', page)
    page = page.replace('<html lang="it">', '<html lang="it" data-theme="auto">', 1)
    page = page.replace('<head>', '<head>'+BOOT+gsc_verification_meta(gsc_token), 1)
    page = page.replace('</head>', f'<meta name="reader-version" content="{VERSION}"><link rel="stylesheet" href="{BASE}assets/reader-theme.css?v={version}"></head>', 1)
    page = page.replace('<div class="wrap v-spoiler-inner">', '<div class="wrap v-spoiler-inner">'+CONTROLS, 1)
    if discussion_path is not None:
        from community_social_v1 import widget, xpost_for
        if '</main>' not in page:
            raise ValueError('Article has no closing main content region')
        page=page.replace('</main>',xpost_for(discussion_path)+widget(discussion_path, youtube_url=page)+'</main>',1)
    page = page.replace('</body>', DIALOG+f'<script src="{BASE}assets/reader-theme.js?v={version}" defer></script>'
                        +f'<script src="{BASE}assets/community-social-v1.js?v={version}" defer></script></body>', 1)
    return page


def build_base():
    """Track actual source changes and reconcile two reviewed guide details."""
    import build_visual_site as builder
    original_sources = builder.ORIGINAL_SOURCES
    builder.ORIGINAL_SOURCES = lambda path: original_sources(path) + (
        'reader_experience.py','data/guide_extras.json',
        'site/assets/reader-theme.css','site/assets/reader-theme.js','site/assets/community-social-v1.js','community_social_v1.py','community_discovery_v2.py','data/community_social.json')
    original_enrich = builder.enrich
    def reviewed(records):
        guides = original_enrich(records)
        for g in guides:
            if g['id'] == 'viaggio-rapido-taxi':
                g['benefit'] = 'Puoi saltare il tragitto pagando 100 GTA$ in aggiunta alla tariffa della corsa, secondo PowerPyx.'
            if g['id'] == 'registrare-auto-personale':
                g['location'] = 'Inizia dall’officina dove la storia ha sbloccato Register. La registrazione presso gli altri Pay ’N’ Spray richiede sblocchi successivi.'
                g['steps'][0] = 'Porta l’auto all’officina dove hai sbloccato Register. Non presumere che la funzione sia già disponibile in qualsiasi Pay ’N’ Spray.'
        return guides
    builder.enrich = reviewed
    builder.main()


def main():
    data = json.loads(Path('data/guide_extras.json').read_text(encoding='utf-8'))
    validate(data)
    version = hashlib.sha256(b''.join((Path('site/assets')/name).read_bytes() for name in ASSETS)).hexdigest()[:12]
    for name in ASSETS:
        shutil.copy2(Path('site/assets')/name, ROOT/'assets'/name)
    import re
    guide_info=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
    visual_info=json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides']
    discussable={'scoperte/','soldi-facili/','auto-speciali/','salvare-auto/','trofei/','hdr-oled/','trucchi/'}
    for guide in guide_info+visual_info:
        path=guide.get('canonical_path') or 'guide-e-tutorial/'+guide['id']+'/'
        if not re.fullmatch(r'(?:[a-z0-9-]+/)+',path):
            raise ValueError('Invalid article discussion path')
        discussable.add(path)
    count = 0
    gsc_token = os.getenv('GSC_SITE_VERIFICATION', '')
    gsc_verification_meta(gsc_token)  # Fail build for unsafe/mistyped tokens.
    for path in ROOT.rglob('*.html'):
        relative = path.relative_to(ROOT).as_posix().removesuffix('index.html')
        page = path.read_text(encoding='utf-8')
        is_trophy_article=relative.startswith('trofei/trofeo-') and relative.endswith('/')
        discussion_path=relative if (relative in discussable or is_trophy_article) else None
        path.write_text(transform(page, version=version, entry=data['guides'].get(relative),
                                  discussion_path=discussion_path,
                                  gsc_token=gsc_token if relative=='' else None), encoding='utf-8')
        count += 1
    for path in data['guides']:
        if not (ROOT/path/'index.html').is_file():
            raise ValueError('Extras point to a missing guide')
    release_path = ROOT/'design-version.json'
    release = json.loads(release_path.read_text(encoding='utf-8'))
    release.update(reader_version=VERSION, default_theme='mobile-dark-desktop-light', reader_asset_version=version,
                   guides_with_extras=len(data['guides']), tip_count=sum(len(x['tips']) for x in data['guides'].values()))
    release_path.write_text(json.dumps(release,indent=2)+'\n', encoding='utf-8')
    print('READER_EXPERIENCE_OK',count,'pages',release['guides_with_extras'],'guides',release['tip_count'],'tips')


if __name__ == '__main__':
    if '--build' in sys.argv:
        build_base()
    main()
