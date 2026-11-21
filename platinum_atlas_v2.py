"""Accessible GTA VI 55-trophy action atlas layered onto the platinum roadmap.

Read-only from the documented trophy catalog. The frontend tracks manual local
progress only and intentionally does not offer PSN integration.
"""
from __future__ import annotations

from collections import Counter
from html import escape
from urllib.parse import urlsplit
import re

BASE = "https://xfederiko11.github.io/gta-6/"
SENSITIVE = {28}
UNCERTAIN = {38,47,49,50}
GROUP_ORDER = ("inizio","storia","cento","collezionabili","attivita","crimine","economia","segreti","finale")


def e(value):
    return escape(str(value), quote=True)


def validate(trophies, routes):
    if len(trophies) != 55 or len({t["number"] for t in trophies}) != 55:
        raise ValueError("Incomplete 55-trophy catalog")
    if routes.get("schema") != "gta6-55-route-playbook-v2":
        raise ValueError("Unknown playbook schema")
    source=urlsplit(routes.get("source",""))
    if source.scheme!="https" or source.hostname!="www.powerpyx.com":
        raise ValueError("Unexpected playbook source")
    groups=routes.get("groups")
    if not isinstance(groups,dict) or set(groups)!=set(GROUP_ORDER):
        raise ValueError("Incomplete playbook group labels")
    entries=routes.get("records",[])
    if len(entries)!=55 or [x.get("number") for x in entries]!=list(range(1,56)):
        raise ValueError("Expected 55 unique ordered playbook records")
    by={x["number"]:x for x in trophies}
    for item in entries:
        n=item["number"]
        if item.get("group") not in groups:
            raise ValueError("Unknown trophy group")
        if not by[n].get("slug") or not re.fullmatch(r"trofeo-[0-9]{2}-[a-z0-9-]+",by[n]["slug"]):
            raise ValueError("Unsafe trophy permalink")
        for prop in ("action","check"):
            text=item.get(prop)
            if not isinstance(text,str) or not 25 <= len(text) <= 360:
                raise ValueError("Missing short actionable instruction: "+str(n))
        warning=item.get("warning")
        if warning is not None and (not isinstance(warning,str) or len(warning)>250):
            raise ValueError("Invalid editorial caution")
        if n in UNCERTAIN and not warning:
            raise ValueError("Uncertain secret trophy must carry caution")
        guide=item.get("guide")
        if guide is not None and not re.fullmatch(r"(?:[a-z0-9-]+/)+",guide):
            raise ValueError("Unsafe internal guide link")
        if guide is not None and not guide.startswith(("trofei/","guide-e-tutorial/","salvare-auto/")):
            raise ValueError("Unexpected internal guide path")
        if by[n]["hidden"] and n==28:
            raise ValueError("Source catalog changed")
    return True


def render(trophies, routes):
    validate(trophies,routes)
    by={x["number"]:x for x in trophies}
    groups=routes["groups"]
    records=routes["records"]
    counts=Counter(x["group"] for x in records)
    filter_options=[
        '<button type="button" data-atlas-filter="all" aria-pressed="true">Tutti · 55</button>'
    ]
    filter_options.extend(
        '<button type="button" data-atlas-filter="'+e(group)+'" aria-pressed="false">'+
        e(groups[group])+' · '+str(counts[group])+'</button>'
        for group in GROUP_ORDER if counts[group]
    )
    output=[
        '<section class="p-atlas" data-trophy-atlas id="guida-55-trofei">',
        '<header class="p-atlas-head"><span class="eyebrow">🏆 CHECKLIST AVANZATA · 55 SCHEDE</span>',
        '<h2>La strategia per tutti e 55 i trofei</h2>',
        '<p>Per ogni trofeo: cosa fare, come verificare la riuscita e cosa evitare.',
        'I trofei nascosti sono chiusi fino al tuo clic. Non si dichiarano sicuri',
        ' i glitch di cui non è verificata la compatibilità con i trofei.</p>',
        '<div class="p-atlas-meter" aria-live="polite"><strong data-atlas-counter>0 / 55 trofei segnati</strong>',
        '<progress max="55" value="0" data-atlas-progress aria-label="Trofei segnati manualmente"></progress>',
        '<small data-atlas-storage>Checklist privata nel browser corrente, non collegata al PSN.</small></div>',
        '</header>',
        '<nav class="p-atlas-nav" aria-label="Filtri della guida ai trofei"><label class="p-atlas-search">',
        '<span>Cerca nome, requisito o obiettivo</span>',
        '<input type="search" data-atlas-search placeholder="Es. meditazione, garage, rapine" aria-label="Cerca tra i 55 trofei">',
        '</label><div class="p-atlas-filters" role="group" aria-label="Filtra per tipo">',
        ''.join(filter_options),'</div></nav>',
        '<p class="p-atlas-results" data-atlas-results role="status" aria-live="polite">55 trofei disponibili</p>',
        '<div class="p-atlas-cards">'
    ]
    for entry in records:
        t=by[entry["number"]]
        hidden=t["hidden"]
        number=t["number"]
        status="incerto" if number in UNCERTAIN else "attenzione" if number in SENSITIVE or entry.get("warning") else "standard"
        dest=BASE+"trofei/"+t["slug"]+"/"
        title=t["name_it"]
        search=" ".join((title,t["requirement_it"],entry["action"],groups[entry["group"]]))
        content=[
            '<div class="p-atlas-card-body">',
            '<h3>'+e(title)+'</h3>',
            '<p class="p-atlas-requirement">'+e(t["requirement_it"])+'</p>',
            '<p><strong>🎮 Cosa fare:</strong> '+e(entry["action"])+'</p>',
            '<p><strong>✅ Come controllare:</strong> '+e(entry["check"])+'</p>'
        ]
        if entry.get("warning"):
            content.append('<p class="p-atlas-caution"><strong>Attenzione:</strong> '+e(entry["warning"])+'</p>')
        links=['<a href="'+e(dest)+'">Scheda completa #'+str(number).zfill(2)+' →</a>']
        if entry.get("guide"):
            links.append('<a href="'+BASE+e(entry["guide"])+'">Guida pratica correlata ↗</a>')
        content.append('<div class="p-atlas-card-links">'+' '.join(links)+'</div></div>')
        body=''.join(content)
        if hidden:
            body=('<details class="p-atlas-hidden" data-atlas-spoiler>'
                  '<summary>🔒 Trofeo nascosto #'+str(number).zfill(2)+' · Apri dettagli (spoiler)</summary>'
                  +body+'</details>')
        output.append(
            '<article class="p-atlas-card" data-atlas-card data-group="'+e(entry["group"])+
            '" data-hidden="'+str(hidden).lower()+'" data-status="'+e(status)+
            '" data-search="'+e(search)+'" data-number="'+str(number)+'">'+
            '<div class="p-atlas-card-top"><span>#{:02d} · {} · {}</span><label class="p-atlas-toggle">'.format(
                number,e(t["tier"]),e(groups[entry["group"]]))+
            '<input type="checkbox" data-atlas-trophy="'+str(number)+'" aria-label="Segna come ottenuto il trofeo '+str(number)+'">'+
            '<span>Ottenuto</span></label></div>'+body+'</article>'
        )
    output.extend([
        '</div><p class="p-atlas-empty" data-atlas-empty hidden>Nessun trofeo corrisponde ai filtri. Modifica la ricerca o scegli Tutti.</p>',
        '<p class="p-atlas-footer">Le azioni riportano il requisito documentato e i controlli pratici,',
        ' non sono prove di gioco dirette. Se una soluzione segreta non è sufficientemente',
        ' verificata è indicata come incerta. <a href="'+e(routes["source"])+'" target="_blank" rel="noopener noreferrer">',
        'Fonte generale PowerPyx e roadmap trofei ↗</a>.</p></section>'
    ])
    return ''.join(output)
