"""Source-reviewed GTA VI patch archive; no network calls or automatic claims."""
from datetime import date
from html import escape as e
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

PATH = 'patch/'
DATA = Path('data/patches_v1.json')


def source_ok(url, host=None):
    u = urlsplit(url)
    return u.scheme == 'https' and bool(u.hostname) and not u.username and not u.password and (host is None or u.hostname == host)


def load():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    if data['schema'] != 'gta6-official-patches-v1' or not data['records']:
        raise ValueError('Invalid patch archive schema')
    seen = set()
    for row in data['records']:
        for key in ('date', 'reviewed', 'published'):
            if date.fromisoformat(row[key]).isoformat() != row[key]:
                raise ValueError('Noncanonical patch date')
        if row['date'] in seen or row['date'] > row['reviewed'] or row['date'] > row['published']:
            raise ValueError('Duplicate or inconsistent patch date')
        seen.add(row['date'])
        if not source_ok(row['official_source'], 'support.rockstargames.com') or not urlsplit(row['official_source']).path.startswith('/articles/'):
            raise ValueError('Missing primary Rockstar article')
        if not row['platforms'] or not row['fixes'] or any(not fix['title'].strip() or not fix['detail'].strip() for fix in row['fixes']):
            raise ValueError('Empty official patch summary')
        if row['version_reports'] and not row['version_sources']:
            raise ValueError('Missing version evidence')
        if any(not source_ok(s['url']) for s in row['version_sources']):
            raise ValueError('Invalid secondary source')
        if any(not re.fullmatch(r'(?:[a-z0-9-]+/)+', link['path']) for link in row['related']):
            raise ValueError('Invalid related path')
    return sorted(data['records'], key=lambda row: row['date'], reverse=True)


def display_date(value):
    dt = date.fromisoformat(value)
    return f'{dt.day} {("gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre").split()[dt.month-1]} {dt.year}'


def source_link(url, label):
    return '<a href="'+e(url, quote=True)+'" target="_blank" rel="noopener noreferrer">'+e(label)+' ↗</a>'


def build(write, layout, url, crumbs):
    records = load()
    paths = [PATH]
    index = (crumbs([('Patch GTA VI', PATH)]) +
             '<div class="ed-article"><section class="ed-intro"><h1>Patch e aggiornamenti GTA VI</h1>'
             '<p>Archivio cronologico delle correzioni confermate da Rockstar Games. '
             'Le versioni riportate da fonti indipendenti sono distinte dalle note ufficiali. '
             'Un aggiornamento non prova che ogni glitch o problema sia stato risolto.</p></section>'
             '<section class="ed-section"><h2>Ultimi aggiornamenti verificati</h2><ul>')
    for row in records:
        path = PATH+row['date']+'/'
        title = 'Patch GTA VI del '+display_date(row['date'])
        desc = f"{len(row['fixes'])} correzioni ufficiali di GTA VI del {display_date(row['date'])}: riepilogo in italiano, piattaforme e fonte Rockstar."
        index += ('<li><a href="'+url(path)+'">'+e(title)+'</a> · '+str(len(row['fixes']))+' correzioni · Ufficiale</li>')
        body = (crumbs([('Patch GTA VI', PATH), (display_date(row['date']), path)]) +
                '<article class="ed-article"><header class="ed-intro" data-patch-intro><span class="ed-kicker">AGGIORNAMENTO · UFFICIALE</span>'
                '<h1>'+e(title)+'</h1><p>Data delle note Rockstar: <time datetime="'+row['date']+'">'+display_date(row['date'])+
                '</time> · Fonte consultata il '+display_date(row['reviewed'])+'</p><p>'+
                e('Piattaforme: '+', '.join(row['platforms']))+
                '. Ecco cosa cambia secondo le note ufficiali; non abbiamo effettuato una prova indipendente nel gioco.</p></header>'
                '<section class="v-section" id="correzioni-ufficiali"><h2>Correzioni ufficiali</h2><ul>')
        for fix in row['fixes']:
            body += '<li data-patch-fix><strong>'+e(fix['title'])+'</strong> — '+e(fix['detail'])+'</li>'
        body += '</ul><p>Fonte primaria: '+source_link(row['official_source'], 'Rockstar Support – note di lancio GTA VI')+'</p></section>'
        if row['version_reports']:
            body += '<section class="v-section" id="versioni-segnalate"><h2>Numeri di versione</h2><p>Riportati da fonti indipendenti; non presenti nelle note ufficiali consultate.</p><ul>'
            for version in row['version_reports']:
                body += '<li>'+e(version['platform'])+': <strong>'+e(version['version'])+'</strong></li>'
            body += '</ul><p>Fonti: '+ ' · '.join(source_link(s['url'], s['name']) for s in row['version_sources'])+'</p></section>'
        body += ('<section class="v-section"><h2>Se riscontri ancora un problema</h2>'
                 '<p>Verifica di avere l’aggiornamento installato dalla console e conserva un salvataggio separato prima di riprovare. '
                 'Non diamo per risolti bug non citati nelle note.</p><p>Guide correlate: '+
                 ' · '.join('<a href="'+url(link['path'])+'">'+e(link['label'])+'</a>' for link in row['related'])+
                 '</p><p><a href="'+url(PATH)+'">Tutte le patch GTA VI →</a></p></section></article>')
        schema = {'@context':'https://schema.org','@type':'Article','headline':title,'description':desc,'url':url(path),
                  'mainEntityOfPage':url(path),'inLanguage':'it-IT','datePublished':row['published'],
                  'author':{'@type':'Organization','name':'GTA 6 Italia','url':url()},
                  'citation':[row['official_source']]+[s['url'] for s in row['version_sources']]}
        write(path+'index.html', layout(title, desc, path, body, 'patch', structured=schema))
        paths.append(path)
    index += '</ul></section></div>'
    title = 'Patch GTA VI: tutte le correzioni ufficiali | GTA 6 Italia'
    write(PATH+'index.html', layout(title, 'Archivio delle patch GTA VI per console, con date e fonti ufficiali Rockstar Games.', PATH, index, 'patch',
                                   structured={'@context':'https://schema.org','@type':'CollectionPage','name':title,'url':url(PATH),'inLanguage':'it-IT'}))
    return paths
