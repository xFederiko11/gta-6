"""Source-attributed Rockstar media library, separate from gameplay tutorials.

The collection is illustrative media provided by the project owner. Its SHA-256
manifest identifies files; it does NOT confer copyright or gameplay verification.
The web page uses small previews only. Full originals are never deployed to Pages.
"""
from __future__ import annotations
from collections import Counter
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

PATH="immagini-ufficiali/"
ROOT=Path("site/assets/rockstar/gta-vi")
MANIFEST=ROOT/"manifest.json"
REFERENCE="https://www.rockstargames.com/VI/media"
POLICY="https://support.rockstargames.com/articles/7bNaeoMFTV0iUDGhStTXvz/policy-on-posting-copyrighted-rockstar-games-material"
CATEGORIES={"Personaggi","Luoghi","Ultimate Edition"}
MIN_ASSETS=180

def family(asset):
    if asset["collection"]=="Ultimate Edition":
        return "Ultimate Edition"
    if asset["collection"]=="Screenshot" and asset["category"] in ("Personaggi","Luoghi"):
        return asset["category"]
    raise ValueError("Unknown Rockstar category or collection")

def validate(manifest=None):
    m=manifest if manifest is not None else json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows=m.get("assets")
    if (m.get("schema")!="gta6-rockstar-library-v1" or not isinstance(rows,list)
            or len(rows)<MIN_ASSETS or len(rows)!=m.get("asset_count")
            or m.get("reference_url")!=REFERENCE):
        raise ValueError("Invalid owner-supplied Rockstar library")
    ids=set()
    for item in rows:
        family(item)
        name=item["preview"]
        path=Path(name)
        if (path.is_absolute() or len(path.parts)!=2 or path.parts[0]!="previews"
                or not re.fullmatch(r"[a-f0-9]{20}-480[.]webp",path.name)):
            raise ValueError("Unexpected preview reference")
        if path.name in ids:
            raise ValueError("Duplicate Rockstar preview")
        ids.add(path.name)
        if not (ROOT/path).is_file():
            raise ValueError("Missing Rockstar preview "+name)
        if not (1<=int(item["width"])<=8000 and 1<=int(item["height"])<=8000):
            raise ValueError("Invalid Rockstar dimensions")
        if (not re.fullmatch(r"[0-9a-f]{64}",item["sha256"])
                or item.get("credit")!="Rockstar Games"
                or not 2<=len(item["title"])<=100 or not 2<=len(item["subject"])<=100):
            raise ValueError("Missing attribution or verified original digest")
    return m

def render(manifest=None):
    m=validate(manifest)
    rows=m["assets"]
    parts=[]
    groups=Counter(family(x) for x in rows)
    for i,x in enumerate(rows):
        alt="Immagine promozionale ufficiale di GTA VI: "+x["title"]
        preview="assets/rockstar/gta-vi/"+x["preview"]
        ratio=round(480*x["height"]/x["width"])
        group=family(x)
        label=(x["title"] if group=="Ultimate Edition" else x["subject"]+" · "+x["title"].split(" ")[-1])
        parts.append(
            '<figure class="rg-card" data-rg-card data-rg-group="'+escape(group,quote=True)+'"'
            ' data-rg-search="'+escape((x["title"]+" "+x["subject"]+" "+group).casefold(),quote=True)+'">'
            '<img src="/gta-6/'+escape(preview,quote=True)+'" loading="lazy" decoding="async"'
            ' width="480" height="'+str(ratio)+'" alt="'+escape(alt,quote=True)+'">'
            '<figcaption><strong>'+escape(label)+'</strong>'
            '<small>'+escape(group)+' · Immagine ufficiale promozionale, non prova di gameplay</small>'
            '<a href="'+REFERENCE+'" target="_blank" rel="noopener noreferrer"'
            ' aria-label="Fonte Rockstar Games per '+escape(x["title"],quote=True)+'">'
            'Fonte: Rockstar Games ↗</a></figcaption></figure>')
    return (
        '<section class="rg-hero" aria-labelledby="rg-title"><span class="rg-kicker">ARCHIVIO UFFICIALE · GTA VI</span>'
        '<h1 id="rg-title">Immagini ufficiali Rockstar di GTA VI</h1>'
        '<p>Esplora '+str(len(rows))+' immagini tratte dagli archivi ufficiali forniti per il progetto. '
        'Filtra ambientazioni, personaggi e contenuti della Ultimate Edition. '
        'Le immagini sono <strong>promozionali</strong>: non identificano necessariamente '
        'una missione, un bottino o una posizione esatta.</p>'
        '<p class="rg-rights"><strong>Crediti:</strong> © Rockstar Games / Take-Two Interactive. '
        'GTA VI Italia è indipendente. Il possesso degli archivi e la verifica degli hash '
        'non conferiscono una licenza di riutilizzo; la pubblicazione è soggetta alle '
        '<a href="'+POLICY+'" target="_blank" rel="noopener noreferrer">regole Rockstar</a>. '
        'Nessuna immagine viene usata automaticamente come prova nei tutorial.</p></section>'
        '<section class="rg-library" data-rockstar-gallery aria-label="Sfoglia le immagini ufficiali">'
        '<div class="rg-controls"><label for="rg-search">Cerca un soggetto'
        '<input id="rg-search" type="search" data-rg-search placeholder="Es. Vice City, Lucia, Grotti…" autocomplete="off"></label>'
        '<label for="rg-filter">Categoria'
        '<select id="rg-filter" data-rg-filter><option value="Tutte">Tutte · '+str(len(rows))+'</option>'
        +''.join('<option value="'+escape(c)+'">'+escape(c)+' · '+str(groups[c])+'</option>'
                 for c in ("Luoghi","Personaggi","Ultimate Edition"))+
        '</select></label></div>'
        '<p class="rg-counter" data-rg-counter aria-live="polite">'+str(len(rows))+' immagini nella raccolta</p>'
        '<div class="rg-grid" data-rg-grid>'+''.join(parts)+'</div>'
        '<p class="rg-empty" data-rg-empty hidden>Nessuna immagine per questa ricerca.</p>'
        '<div class="rg-more-wrap"><button type="button" data-rg-more hidden>Mostra altre immagini</button></div>'
        '</section>'
    )
