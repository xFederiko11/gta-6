"""Photo-led discovery for GTA VI Italia, using the owner's Rockstar originals.

Promotional media remains separate from the evidence used by tutorial steps.
Responsive copies are generated locally; the original archive never ships to Pages.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import hashlib
import json

VERSION = 'cinematic-v3-20261124'
ROOT = Path('site/assets/rockstar/gta-vi')
DEST = Path('site/assets/cinematic')
ARTICLE = 'articoli/gta-vi-leonida-sei-luoghi/'
BASE = 'https://xfederiko11.github.io/gta-6/'
ROWS = {Path(row['file']).name: row for row in json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))['assets']}
HERO = 'Jason_and_Lucia_03.jpg'
GUIDES = {
    'registrare-auto-personale': 'Jason_and_Lucia_11.jpg',
    'veicoli-per-moses': 'Vice_City_24.jpg',
    'soldi-facili-capitolo-1': 'Jason_and_Lucia_15.jpg',
}
CATEGORY_IMAGES = {'soldi':'Jason_and_Lucia_15.jpg', 'auto':'Vice_City_24.jpg',
                   'garage':'Jason_and_Lucia_11.jpg', 'inizio':'Jason_and_Lucia_09.jpg'}
PLACES = [
    ('vice-city','Vice City','Vice_City_27.jpg','La città dopo il tramonto.','Grattacieli, quartieri e luci della sera: guarda da vicino il volto urbano di Leonida.'),
    ('leonida-keys','Leonida Keys','Leonida_Keys_01.jpg','L’orizzonte si apre.','Isole, ponti e acqua turchese. Un altro ritmo, a pochi scatti dalla città.'),
    ('grassrivers','Grassrivers','Grassrivers_03.jpg','Fuori dalle strade battute.','Acqua scura e vegetazione fitta: osserva i dettagli della raccolta fotografica ufficiale.'),
    ('port-gellhorn','Port Gellhorn','Port_Gellhorn_01.jpg','Un’insegna nella sera.','Lo Starlet Motel, le palme e una luce diversa: il viaggio fotografico continua.'),
    ('ambrosia','Ambrosia','Ambrosia_01.jpg','La strada prende vita.','Motociclette, insegne e sole basso. Esplora un altro paesaggio di GTA VI.'),
    ('mount-kalaga','Mount Kalaga','Mount_Kalaga_National_Park_03.jpg','Respira, poi riparti.','Alberi, erba alta e luce che filtra: l’ultima tappa del nostro itinerario per immagini.'),
]
COVERS = {
    'guide-e-tutorial/':'Jason_and_Lucia_17.jpg', 'trofei/':'Jason_and_Lucia_09.jpg',
    'soldi-facili/':'Jason_and_Lucia_15.jpg', 'auto-speciali/':'Vice_City_24.jpg',
    'salvare-auto/':'Jason_and_Lucia_11.jpg', 'veicoli/':'Vice_City_24.jpg',
    'hdr-oled/':'Vice_City_22.jpg', 'mappe-guide/':'Leonida_Keys_01.jpg',
    'collezionabili/percorsi/':'Mount_Kalaga_National_Park_03.jpg',
    'scoperte/':'Vice_City_06.jpg', 'trucchi/':'Jason_and_Lucia_04.jpg',
}
SELECTED = {HERO, 'Jason_and_Lucia_01.jpg','Jason_and_Lucia_16.jpg','Vice_City_06.jpg',
            'Vice_City_03.jpg', *GUIDES.values(), *CATEGORY_IMAGES.values(),
            *COVERS.values(), *(p[2] for p in PLACES)}


def media_name(name, width):
    return ROWS[name]['sha256'][:20]+'-'+str(width)+'.webp'


def prepare():
    from PIL import Image
    DEST.mkdir(parents=True, exist_ok=True)
    generated = 0
    for name in sorted(SELECTED):
        for width in (960,1600):
            out = DEST/media_name(name,width)
            if out.is_file():
                continue
            with Image.open(ROOT/ROWS[name]['file']) as source:
                image=source.convert('RGB')
                image.thumbnail((width,width*9//16))
                image.save(out,'WEBP',quality=82,method=4)
            generated += 1
    print('CINEMATIC_MEDIA_READY',len(SELECTED),'selected originals',generated,'new responsive files')


def image(name, url, *, eager=False, css='', sizes='(max-width: 700px) 100vw, 50vw'):
    row=ROWS[name]
    small=url('assets/rockstar/gta-vi/'+row['preview'])
    medium=url('assets/cinematic/'+media_name(name,960))
    large=url('assets/cinematic/'+media_name(name,1600))
    alt='GTA VI: '+row['title'].title()+' — immagine ufficiale Rockstar Games'
    return (f'<img class="{css}" src="{medium}" srcset="{small} 480w, {medium} 960w, {large} 1600w" '
            f'sizes="{sizes}" width="1600" height="900" alt="{escape(alt,quote=True)}" '
            f'loading="{"eager" if eager else "lazy"}" decoding="async"'+
            (' fetchpriority="high"' if eager else '')+' data-promotional-media="rockstar">')


def card_image(guide, url):
    name=GUIDES.get(guide['id'],CATEGORY_IMAGES.get(guide['category'],'Jason_and_Lucia_09.jpg'))
    return '<div class="ci-card-photo">'+image(name,url)+'<span>Immagine illustrativa · Rockstar Games</span></div>'


def home(guides, url):
    count=len(json.loads(Path('data/trofei.json').read_text(encoding='utf-8'))['trophies'])
    by={g['id']:g for g in guides}
    first=by['registrare-auto-personale']['canonical_path']
    cash=by['soldi-facili-capitolo-1']['canonical_path']
    out = ('<div class="cinema-home" data-cinematic-home><section class="focus-hero" aria-labelledby="focus-title">'+
           image(HERO,url,eager=True,css='ci-hero-image',sizes='(max-width: 700px) 1300px, 100vw')+
           '<div class="ci-hero-shade"></div><div class="ci-hero-inner ci-shell">'
           '<span class="ci-eyebrow ci-hero-eyebrow">GTA VI ITALIA <span>PS5 · PS5 PRO</span></span>'
           '<div class="ci-hero-copy"><p class="ci-overline">OGNI STRADA, UNA POSSIBILITÀ.</p>'
           '<h1 id="focus-title" class="ci-hero-title">LEONIDA.<br><em>A MODO TUO.</em></h1>'
           '<p class="ci-hero-description">La prossima auto. Il prossimo obiettivo. La prossima scoperta.<br>'
           'Trova la tua strada in GTA VI, una guida alla volta.</p>'
           '<div class="ci-actions"><a class="ci-button" href="#scegli">Trova la tua prossima guida</a>'
           '<a class="ci-button ci-button-ghost" href="#esplora">Esplora Leonida</a></div></div>'
           '<div class="ci-hero-bottom"><span>IL TUO PUNTO DI PARTENZA A LEONIDA</span>'
           '<small>Immagine promozionale © Rockstar Games</small></div></div></section>'
           '<div class="ci-ticker"><div class="ci-shell"><span>Guide in italiano</span><i></i>'
           f'<span>{count} trofei da scoprire</span><i></i><span>Immagini ufficiali Rockstar</span>'
           '<a href="'+url('immagini-ufficiali/')+'">Sfoglia la raccolta</a></div></div>'
           '<section class="ci-section ci-shell" id="scegli"><div class="ci-heading">'
           '<div><span class="ci-eyebrow">SCEGLI LA TUA DIREZIONE</span><h2>Cosa vuoi fare in GTA VI?</h2></div>'
           '<p>Un obiettivo preciso o la voglia di lasciarti sorprendere.<br>Parti da qui.</p></div>'
           '<nav class="focus-choice-grid" aria-label="Scegli cosa cercare">')
    for tag,title,desc,path,name in [
        ('PASSA ALL’AZIONE','Guide pratiche','Soldi, auto e missioni. Trova il prossimo passo.', 'guide-e-tutorial/','Jason_and_Lucia_11.jpg'),
        ('PUNTA PIÙ IN ALTO','Trofei e platino','La tua roadmap, i requisiti e le checklist.', 'trofei/','Jason_and_Lucia_09.jpg'),
        ('SEGUI LA CURIOSITÀ','Scoperte community','Idee e segnalazioni dei giocatori, con fonte e stato della verifica.', 'scoperte/','Vice_City_06.jpg')]:
        out+=('<a class="focus-choice" href="'+url(path)+'"><div class="ci-choice-image">'+image(name,url)+
              '</div><div class="ci-choice-copy"><small>'+tag+'</small><strong>'+title+'</strong><span>'+desc+'</span></div></a>')
    out+=('</nav><p class="ci-credit">Immagini promozionali Rockstar Games, usate per illustrare i percorsi.</p></section>'
          '<section class="ci-feature ci-shell" aria-labelledby="ci-feature-title"><a class="ci-feature-art" href="'+url(ARTICLE)+'">'+
          image('Vice_City_27.jpg',url)+'<span class="ci-photo-label">VIAGGIO FOTOGRAFICO · ROCKSTAR GAMES</span></a>'
          '<div class="ci-feature-copy"><span class="ci-eyebrow">DENTRO LEONIDA</span>'
          '<h2 id="ci-feature-title">VICE CITY È<br>SOLO L’INIZIO.</h2>'
          '<p>Dalle luci della città ai ponti delle Keys, fino alla vegetazione di Grassrivers. '
          'Sei luoghi, sei immagini ufficiali e un viaggio da guardare con calma.</p>'
          '<a class="ci-button" href="'+url(ARTICLE)+'">Leggi l’articolo</a></div></section>'
          '<section class="focus-content ci-section ci-shell" aria-labelledby="focus-guide-title">'
          '<div class="ci-heading"><div><span class="ci-eyebrow">METTITI IN MOTO</span>'
          '<h2 id="focus-guide-title">Il prossimo passo è qui.</h2></div><a class="ci-text-link" href="'+url('guide-e-tutorial/')+'">Tutte le guide</a></div>'
          '<ol class="focus-quick">')
    for label,title,desc,path,name in [
        ('AUTO & GARAGE','La prima auto. Tienila.','Registrazione, garage e cosa controllare prima di partire.',first,'Jason_and_Lucia_11.jpg'),
        ('VEICOLI','Le 6 auto per Moses','Modelli da trovare, riferimenti ai luoghi e fonti gameplay.', 'guide-e-tutorial/veicoli-per-moses/','Vice_City_24.jpg'),
        ('SOLDI','Parti con il piede giusto.','Il Capitolo 1: percorsi e precauzioni prima di accumulare denaro.',cash,'Jason_and_Lucia_15.jpg')]:
        out+=('<li><a href="'+url(path)+'"><div class="ci-guide-image">'+image(name,url)+'</div>'
              '<div class="ci-guide-copy"><small>'+label+'</small><strong>'+title+'</strong><span>'+desc+'</span>'
              '<b>Apri la guida</b></div></a></li>')
    out+=('</ol><a class="ci-catalog-link" href="'+url('veicoli/')+'"><span>Cerchi un modello preciso?</span>'
          '<strong>Trova un veicolo per nome, zona o richiesta.</strong><b>Apri il catalogo veicoli</b></a></section>'
          '<section class="ci-explore" id="esplora"><div class="ci-shell"><div class="ci-heading">'
          '<div><span class="ci-eyebrow">CAMBIA PROSPETTIVA</span><h2>Un mondo da guardare.<br>E da scoprire.</h2></div>'
          '<p>Scegli un luogo e lasciati portare dalle immagini ufficiali.</p></div>'
          '<div class="ci-place-tabs" role="tablist" aria-label="Scegli un luogo" data-place-tabs>')
    for i,(slug,title,name,kicker,desc) in enumerate(PLACES):
        out+=(f'<button type="button" role="tab" id="place-tab-{slug}" aria-controls="place-{slug}" '
              f'aria-selected="{str(i==0).lower()}" tabindex="{0 if i==0 else -1}" data-place-tab="{slug}">{title}</button>')
    out+='</div><div class="ci-place-panels">'
    for i,(slug,title,name,kicker,desc) in enumerate(PLACES):
        out+=(f'<section class="ci-place-panel" id="place-{slug}" role="tabpanel" aria-labelledby="place-tab-{slug}" data-place-panel="{slug}">'+
              image(name,url,sizes='(max-width: 700px) 100vw, 85vw')+
              '<div class="ci-place-shade"></div><div class="ci-place-copy"><span>'+escape(kicker)+'</span><h3>'+title+'</h3>'
              '<p>'+escape(desc)+'</p><a class="ci-button ci-button-ghost" href="'+url(ARTICLE)+'#'+slug+'">Scopri '+title+'</a></div>'
              '<small class="ci-photo-label">Immagine ufficiale © Rockstar Games</small></section>')
    out+=('</div></div></section><section class="ci-follow ci-shell">'+image('Jason_and_Lucia_16.jpg',url)+
          '<div class="ci-follow-shade"></div><div class="focus-x"><span class="ci-eyebrow">IL VIAGGIO CONTINUA</span>'
          '<h2>Una scoperta tira l’altra.</h2><p>Nuove guide, percorsi da provare e dettagli da condividere. '
          'Ritroviamoci anche su X.</p><a class="ci-button" href="https://x.com/xFederiko11" target="_blank" rel="noopener noreferrer">'
          'Segui @xFederiko11</a></div><small class="ci-photo-label">Immagine promozionale © Rockstar Games</small></section>'
          '<section class="focus-news ci-source-note ci-shell"><strong>Fonti chiare, curiosità accesa.</strong>'
          '<p>Le guide riportano le proprie fonti; le segnalazioni community conservano il loro stato di verifica.</p>'
          '<a href="https://www.rockstargames.com/newswire" target="_blank" rel="noopener noreferrer">Newswire Rockstar</a>'
          '<a href="'+url('fonti/')+'">Il nostro metodo</a></section></div>')
    return out


def enhance(page, path):
    digest=hashlib.sha256(Path('site/assets/cinematic-v3.css').read_bytes()+Path('site/assets/cinematic-v3.js').read_bytes()).hexdigest()[:12]
    css=f'<meta name="cinematic-version" content="{VERSION}"><link rel="stylesheet" href="{BASE}assets/cinematic-v3.css?v={digest}">'
    page=page.replace('</head>',css+'</head>',1)
    if path == '':
        page=page.replace('</body>',f'<script src="{BASE}assets/cinematic-v3.js?v={digest}" defer></script></body>',1)
    elif path in COVERS:
        cover=('<figure class="ci-section-cover">'+image(COVERS[path],lambda p:BASE+p,sizes='100vw')+
               '<figcaption>Immagine promozionale ufficiale © Rockstar Games</figcaption></figure>')
        # Visual introduction only; tutorial evidence and numbered steps remain intact.
        import re
        page,count=re.subn(r'(<nav class="breadcrumbs"[^>]*>.*?</nav>)',lambda m:m.group(0)+cover,page,count=1,flags=re.S)
        if not count:
            page=re.sub(r'(<main\b[^>]*>)',lambda m:m.group(0)+cover,page,count=1)
    return page
