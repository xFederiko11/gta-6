"""Illustrated editorial articles and the owner-supplied Rockstar image library."""
from __future__ import annotations

from html import escape
from pathlib import Path
from urllib.parse import quote
import json
import re

LIBRARY = Path('site/assets/rockstar/gta-vi')
LIBRARY_PATH = 'assets/rockstar/gta-vi/'
GALLERY_PATH = 'immagini-ufficiali/'
INDEX_PATH = 'articoli/'


def load():
    library = json.loads((LIBRARY/'manifest.json').read_text(encoding='utf-8'))
    articles = json.loads(Path('data/articles.json').read_text(encoding='utf-8'))['articles']
    if library['asset_count'] != len(library['assets']) or len(library['assets']) != 189:
        raise ValueError('Incomplete owner-supplied Rockstar library')
    images = {Path(row['file']).name: row for row in library['assets']}
    if len(images) != 189:
        raise ValueError('Ambiguous Rockstar image names')
    if len({a['path'] for a in articles}) != len(articles):
        raise ValueError('Duplicate editorial path')
    for article in articles:
        if not re.fullmatch(r'articoli/[a-z0-9-]+/', article['path']):
            raise ValueError('Invalid editorial article path')
        if len({row['image'] for row in article['sections']}) != len(article['sections']):
            raise ValueError('Repeated editorial photograph')
        if article['hero'] not in {row['image'] for row in article['sections']}:
            raise ValueError('Cover must be one of the reviewed article photos')
        for related in article.get('related', []):
            if not re.fullmatch(r'(?:[a-z0-9-]+/)+', related['path']):
                raise ValueError('Invalid related article path')
        for name in [article['hero']] + [row['image'] for row in article['sections']]:
            row = images[name]
            if not (LIBRARY/row['file']).is_file():
                raise ValueError('Missing selected image: '+name)
            # New editorial selections can use any reviewed archive original.
            # Generate larger reader derivatives locally, without committing
            # new binary assets or packaging the originals on Pages.
            for width in (960,1600):
                row['variants'].setdefault(str(width),'previews/'+row['sha256'][:20]+'-'+str(width)+'.webp')
    return library, articles, images


def prepare():
    from PIL import Image
    import hashlib
    _, articles, images=load()
    selected={name for article in articles for name in
              [article['hero']]+[section['image'] for section in article['sections']]}
    generated=0
    for name in sorted(selected):
        row=images[name]
        original=LIBRARY/row['file']
        missing=[width for width in (960,1600) if not (LIBRARY/row['variants'][str(width)]).is_file()]
        if not missing:
            continue
        if hashlib.sha256(original.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Editorial original digest mismatch: '+name)
        with Image.open(original) as opened:
            image=opened.convert('RGB')
            for width in missing:
                resized=image.copy()
                resized.thumbnail((width,round(width*image.height/image.width)),Image.Resampling.LANCZOS)
                target=LIBRARY/row['variants'][str(width)]
                target.parent.mkdir(parents=True,exist_ok=True)
                resized.save(target,'WEBP',quality=84,method=4)
                generated+=1
    print('EDITORIAL_RESPONSIVE_MEDIA_READY',len(selected),'reviewed originals',generated,'generated variants')


def asset_url(url, path):
    return url(LIBRARY_PATH+quote(path, safe='/'))


def figure(section, row, url, *, eager=False):
    src = asset_url(url, row['variants']['960'])
    srcset = ', '.join(asset_url(url, row['variants'][str(w)])+' '+str(w)+'w'
                       for w in (480, 960, 1600))
    original = row['public_url']
    return ('<figure class="ed-photo"><a href="'+original+'" target="_blank" rel="noopener">'
            '<img src="'+src+'" srcset="'+srcset+'" sizes="(max-width: 800px) 100vw, 900px" '
            'width="1600" height="900" alt="'+escape(section['alt'], quote=True)+'" '
            'loading="'+('eager' if eager else 'lazy')+'" decoding="async"'+
            (' fetchpriority="high"' if eager else '')+'></a><figcaption>'+
            escape(section['caption'])+' <a href="'+original+'" target="_blank" rel="noopener">'
            'Apri originale 4K ↗</a></figcaption></figure>')


def home_feature(url, *, all_articles=False):
    _, articles, images = load()
    def card(article):
        image = asset_url(url, images[article['hero']]['preview'])
        alt = next(s['alt'] for s in article['sections'] if s['image']==article['hero'])
        return ('<a class="ed-home-card" href="'+url(article['path'])+'">'
                '<img src="'+image+'" width="480" height="270" loading="lazy" alt="'+escape(alt,quote=True)+'">'
                '<span><small>ARTICOLO ILLUSTRATO · ROCKSTAR GAMES</small><strong>'+escape(article['title'])+
                '</strong><span>'+escape(article['description'])+'</span></span></a>')
    heading='Articoli illustrati' if all_articles else 'Approfondimenti fotografici'
    featured=articles if all_articles else articles[-1:]
    extra=''
    return ('<section class="focus-content ed-home" aria-labelledby="ed-home-title">'
            '<h2 id="ed-home-title">'+heading+'</h2>'+''.join(card(a) for a in featured)+extra+
            ('' if all_articles else '<p><a href="'+url(INDEX_PATH)+'">Tutti gli articoli →</a></p>')+'</section>')


def build(write, layout, url, crumbs):
    library, articles, images = load()
    paths = [INDEX_PATH]
    for article in articles:
        path = article['path']
        intro = ''.join('<p>'+escape(p)+'</p>' for p in article['intro'])
        toc = ''.join('<a href="#'+s['id']+'">'+escape(s['title'].split(':')[0])+'</a>'
                      for s in article['sections'])
        body = (crumbs([('Articoli', INDEX_PATH), (article['title'], path)])+
                '<article class="ed-article"><header class="ed-intro"><span class="ed-kicker">'
                'GTA VI · ARTICOLO ILLUSTRATO</span><h1>'+escape(article['title'])+'</h1>'
                '<p class="ed-byline">GTA 6 Italia · <time datetime="'+article['published']+'">'+
                article['published']+'</time> · Immagini Rockstar Games</p>'+intro+'</header>'
                '<nav class="ed-toc" aria-label="Sezioni dell’articolo">'+toc+'</nav>')
        for i, section in enumerate(article['sections']):
            body += ('<section class="ed-section" id="'+section['id']+'"><h2>'+
                     escape(section['title'])+'</h2>'+figure(section, images[section['image']], url, eager=i==0)+
                     ''.join('<p>'+escape(p)+'</p>' for p in section['paragraphs'])+'</section>')
        related=article.get('related', [{'path':'mappe-guide/','label':'Mappe delle guide'},
                                      {'path':'collezionabili/percorsi/','label':'Percorsi collezionabili'}])
        related_html=''.join('<a href="'+url(r['path'])+'">'+escape(r['label'])+' →</a>' for r in related)
        body += ('<p>'+escape(article['closing'])+'</p><nav class="ed-related" aria-label="Continua a esplorare">'
                 +related_html+
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
            '<p>Approfondimenti originali in italiano, con immagini e fonti attribuite.</p></section>'+home_feature(url,all_articles=True))
    index_schema={'@context':'https://schema.org','@type':'CollectionPage','name':title,
                  'url':url(INDEX_PATH),'inLanguage':'it-IT'}
    write(INDEX_PATH+'index.html', layout(title, 'Articoli illustrati su GTA VI, con immagini ufficiali Rockstar Games e fonti.', INDEX_PATH, body, 'articles', structured=index_schema))
    return paths
