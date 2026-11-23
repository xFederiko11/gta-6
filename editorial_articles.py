"""Illustrated editorial articles and the owner-supplied Rockstar image library."""
from __future__ import annotations

from html import escape
from pathlib import Path
from urllib.parse import quote
import json
import re

LIBRARY = Path('site/assets/rockstar/gta-vi')
LIBRARY_PATH = 'assets/rockstar/gta-vi/'
GALLERY_PATH = 'media/rockstar/'
INDEX_PATH = 'articoli/'


def load():
    library = json.loads((LIBRARY/'manifest.json').read_text(encoding='utf-8'))
    articles = json.loads(Path('data/articles.json').read_text(encoding='utf-8'))['articles']
    if library['asset_count'] != len(library['assets']) or len(library['assets']) != 189:
        raise ValueError('Incomplete owner-supplied Rockstar library')
    images = {Path(row['file']).name: row for row in library['assets']}
    if len(images) != 189:
        raise ValueError('Ambiguous Rockstar image names')
    for article in articles:
        if not re.fullmatch(r'articoli/[a-z0-9-]+/', article['path']):
            raise ValueError('Invalid editorial article path')
        if len({row['image'] for row in article['sections']}) != len(article['sections']):
            raise ValueError('Repeated editorial photograph')
        for name in [article['hero']] + [row['image'] for row in article['sections']]:
            row = images[name]
            if '1600' not in row['variants'] or not (LIBRARY/row['file']).is_file():
                raise ValueError('Missing selected image: '+name)
    return library, articles, images


def asset_url(url, path):
    return url(LIBRARY_PATH+quote(path, safe='/'))


def figure(section, row, url, *, eager=False):
    src = asset_url(url, row['variants']['960'])
    srcset = ', '.join(asset_url(url, row['variants'][str(w)])+' '+str(w)+'w'
                       for w in (480, 960, 1600))
    original = asset_url(url, row['file'])
    return ('<figure class="ed-photo"><a href="'+original+'" target="_blank" rel="noopener">'
            '<img src="'+src+'" srcset="'+srcset+'" sizes="(max-width: 800px) 100vw, 900px" '
            'width="1600" height="900" alt="'+escape(section['alt'], quote=True)+'" '
            'loading="'+('eager' if eager else 'lazy')+'" decoding="async"'+
            (' fetchpriority="high"' if eager else '')+'></a><figcaption>'+
            escape(section['caption'])+' <a href="'+original+'" target="_blank" rel="noopener">'
            'Apri originale 4K ↗</a></figcaption></figure>')


def home_feature(url):
    _, articles, images = load()
    article = articles[0]
    image = asset_url(url, images[article['hero']]['preview'])
    return ('<section class="focus-content ed-home" aria-labelledby="ed-home-title">'
            '<h2 id="ed-home-title">Dentro Leonida</h2><a class="ed-home-card" href="'+url(article['path'])+'">'
            '<img src="'+image+'" width="480" height="270" loading="lazy" '
            'alt="Veduta di Vice City, screenshot ufficiale Rockstar Games">'
            '<span><small>ARTICOLO ILLUSTRATO · ROCKSTAR GAMES</small><strong>'+escape(article['title'])+
            '</strong><span>Un viaggio fotografico attraverso sei luoghi di GTA VI.</span></span></a>'
            '<p><a href="'+url(INDEX_PATH)+'">Tutti gli articoli →</a></p></section>')


def build(write, layout, url, crumbs):
    library, articles, images = load()
    paths = [INDEX_PATH, GALLERY_PATH]
    for article in articles:
        path = article['path']
        intro = ''.join('<p>'+escape(p)+'</p>' for p in article['intro'])
        toc = ''.join('<a href="#'+s['id']+'">'+escape(s['title'].split(':')[0])+'</a>'
                      for s in article['sections'])
        body = (crumbs([('Articoli', INDEX_PATH), ('Leonida in sei immagini', path)])+
                '<article class="ed-article"><header class="ed-intro"><span class="ed-kicker">'
                'GTA VI · VIAGGIO FOTOGRAFICO</span><h1>'+escape(article['title'])+'</h1>'
                '<p class="ed-byline">GTA 6 Italia · <time datetime="'+article['published']+'">'+
                article['published']+'</time> · Immagini Rockstar Games</p>'+intro+'</header>'
                '<nav class="ed-toc" aria-label="Le sei tappe">'+toc+'</nav>')
        for i, section in enumerate(article['sections']):
            body += ('<section class="ed-section" id="'+section['id']+'"><h2>'+
                     escape(section['title'])+'</h2>'+figure(section, images[section['image']], url, eager=i==0)+
                     ''.join('<p>'+escape(p)+'</p>' for p in section['paragraphs'])+'</section>')
        body += ('<p>'+escape(article['closing'])+'</p><nav class="ed-related" aria-label="Continua a esplorare">'
                 '<a href="'+url('mappe-guide/')+'">Mappe delle guide →</a>'
                 '<a href="'+url('collezionabili/percorsi/')+'">Percorsi collezionabili →</a>'
                 '<a href="'+url(GALLERY_PATH)+'">Tutte le 189 immagini Rockstar →</a></nav>'
                 '<section class="ed-sources"><h2>Fonti e immagini</h2><p>Screenshot promozionali ufficiali '
                 'Rockstar Games, provenienti dagli archivi forniti al progetto. Credito: © Rockstar Games.</p><ul>'+
                 ''.join('<li><a href="'+escape(s['url'], quote=True)+'" target="_blank" rel="noopener noreferrer">'+
                         escape(s['title'])+' ↗</a></li>' for s in article['sources'])+'</ul></section></article>')
        hero = asset_url(url, images[article['hero']]['variants']['1600'])
        schema = {'@context':'https://schema.org', '@type':'Article', 'headline':article['title'],
                  'description':article['description'], 'url':url(path), 'mainEntityOfPage':url(path),
                  'inLanguage':'it-IT', 'datePublished':article['published'], 'image':hero,
                  'author':{'@type':'Organization','name':'GTA 6 Italia','url':url()},
                  'citation':[s['url'] for s in article['sources']]}
        page = layout(article['title'], article['description'], path, body, 'articles', hero, structured=schema)
        write(path+'index.html', page)
        paths.append(path)
    title = 'Articoli GTA VI: luoghi e immagini ufficiali | GTA 6 Italia'
    body = (crumbs([('Articoli', INDEX_PATH)])+'<section class="ed-intro"><h1>Articoli GTA VI</h1>'
            '<p>Approfondimenti originali in italiano, con immagini e fonti attribuite.</p></section>'+home_feature(url))
    index_schema={'@context':'https://schema.org','@type':'CollectionPage','name':title,
                  'url':url(INDEX_PATH),'inLanguage':'it-IT'}
    write(INDEX_PATH+'index.html', layout(title, 'Articoli illustrati su GTA VI, con immagini ufficiali Rockstar Games e fonti.', INDEX_PATH, body, 'articles', structured=index_schema))
    cards = []
    for row in library['assets']:
        original = asset_url(url, row['file'])
        label = escape(row['title'])
        search = escape((row['title']+' '+row['subject']+' '+row['category']).casefold(), quote=True)
        cards.append('<article class="ed-library-card" data-library-card data-category="'+escape(row['category'], quote=True)+
                     '" data-search="'+search+'"><a href="'+original+'" target="_blank" rel="noopener">'
                     '<img src="'+asset_url(url, row['preview'])+'" width="480" height="270" loading="lazy" '
                     'alt="'+label+' — Rockstar Games"></a><div><small>'+escape(row['category'])+'</small>'
                     '<h2>'+label+'</h2><p>3840 × 2160 · JPG · Rockstar Games</p>'
                     '<a href="'+original+'" target="_blank" rel="noopener">Apri originale 4K ↗</a></div></article>')
    body = (crumbs([('Immagini Rockstar', GALLERY_PATH)])+'<section class="ed-intro"><h1>Immagini ufficiali GTA VI</h1>'
            '<p>189 originali in 4K per articoli e post: 77 immagini di personaggi, 61 di luoghi e 51 della Ultimate Edition. '
            'Credito: © Rockstar Games.</p><p><a href="https://www.rockstargames.com/VI/media" '
            'target="_blank" rel="noopener noreferrer">Fonte Rockstar ↗</a> · '
            '<a href="'+url(LIBRARY_PATH+'manifest.json')+'">Indice e link dei file</a></p></section>'
            '<div class="ed-filters" id="library-filters" hidden><label>Cerca un soggetto'
            '<input type="search" id="library-search" placeholder="Jason, Vice City, Grotti…"></label>'
            '<label>Raccolta<select id="library-category"><option value="">Tutte</option><option>Personaggi</option>'
            '<option>Luoghi</option><option>Ultimate Edition</option></select></label></div>'
            '<p id="library-count" role="status" aria-live="polite">189 immagini</p>'
            '<div class="ed-library-grid">'+''.join(cards)+'</div>')
    page = layout('Immagini GTA VI in 4K — archivio Rockstar | GTA 6 Italia',
                  '189 immagini Rockstar Games in 4K, catalogate per personaggi, luoghi e Ultimate Edition.',
                  GALLERY_PATH, body, 'articles', robots='noindex,follow')
    page = page.replace('</body>', '<script src="'+url('assets/rockstar-library.js')+'" defer></script></body>', 1)
    write(GALLERY_PATH+'index.html', page)
    return paths
