"""In-depth, attribution-forward GTA VI trophies & collectibles pages (PS5).

Numeric checkpoints and finished card sets are manual local browser records.
Neither page reads PSN, copies gameplay images, or certifies exploits.
"""
from __future__ import annotations

from collections import Counter
from html import escape
from urllib.parse import urlsplit
import re

BASE="https://xfederiko11.github.io/gta-6/"
COLLECTIBLE_PATH="trofei/100-percento/"
HARD_PATH="trofei/trofei-difficili/"
GROUP_ORDER=("story","activities","discovery")
TARGETS={ "story":12, "activities":20, "discovery":3 }

def e(x):
    return escape(str(x),quote=True)

def validate(data, trophy_catalog):
    if data.get("schema")!="gta6-advanced-platinum-20261121-v1":
        raise ValueError("Unexpected advanced platinum data schema")
    if len(trophy_catalog)!=55:
        raise ValueError("55 trophy records required")
    if not isinstance(data.get("sources"),dict) or len(data["sources"])<8:
        raise ValueError("Sources required")
    for url in data["sources"].values():
        p=urlsplit(url)
        if (p.scheme!="https" or p.hostname not in
            {"www.powerpyx.com","www.gtabase.com","grindcoast.com","leonipedia.com"}
            or p.username or p.password or p.port not in (None,443)):
            raise ValueError("Unsafe source URL")
    requirements=data.get("requirements",[])
    if len(requirements)!=35 or len({x["id"] for x in requirements})!=35:
        raise ValueError("Expected 35 distinct 100 percent requirements")
    if Counter(x["category"] for x in requirements)!=Counter(TARGETS):
        raise ValueError("100 percent category distribution drift")
    for item in requirements:
        if not re.fullmatch(r"c[0-9]{2}-[a-z0-9-]+",item["id"]):
            raise ValueError("Bad tracker id")
        if (type(item["target"]) is not int or item["target"]<1 or
            item["total"] is not None and (type(item["total"]) is not int
            or item["target"]>item["total"])):
            raise ValueError("Invalid progress count")
        if not 8<=len(item["label"])<=90 or not 15<=len(item["note"])<=220:
            raise ValueError("Missing metric context")
        if item.get("guide") and not re.fullmatch(r"(?:[a-z0-9-]+/)+",item["guide"]):
            raise ValueError("Invalid internal guide link")
    cards=data.get("cards",[])
    if len(cards)!=18 or sum(x["total"] for x in cards)!=480:
        raise ValueError("Collectible card counts do not total 480")
    if len({x["id"] for x in cards})!=18 or len({x["name"] for x in cards})!=18:
        raise ValueError("Duplicate card set")
    if sum(x["total"] for x in sorted(cards,key=lambda x:x["total"])[:15])!=372:
        raise ValueError("Expected 372-card mathematical minimum")
    for x in cards:
        if not re.fullmatch(r"set[0-9]{2}",x["id"]) or not 12<=x["total"]<=36:
            raise ValueError("Malformed set")
    hard=data.get("hard",[])
    if [x["trophy"] for x in hard]!=[38,46,47,48,49,50,30]:
        raise ValueError("Hard-trophy focus set changed")
    for x in hard:
        if x["status"] not in {"documentato","probabile","incerto"} or len(x["steps"])<3:
            raise ValueError("Unknown hard trophy confidence")
        if x["trophy"]==49 and x["status"]!="incerto":
            raise ValueError("Unconfirmed trophy cannot be certified")
        for src in x["sources"]:
            if src not in data["sources"]:
                raise ValueError("Unregistered trophy evidence")
        if not x.get("warning") or len(x["warning"])>470:
            raise ValueError("Missing caution / status boundary")
    return True

def _sources(data,names):
    return '<ul class="ap-sources">'+''.join(
        '<li><a href="'+e(data["sources"][name])+'" target="_blank" rel="noopener noreferrer">'
        +e(urlsplit(data["sources"][name]).hostname.removeprefix("www."))+
        ' · apri la fonte e le immagini originali ↗</a></li>'
        for name in names
    )+'</ul>'

def render_100(data,trophies):
    validate(data,trophies)
    out=[
        '<section class="ap-main" data-advanced-platinum-100>',
        '<header class="ap-hero"><span class="eyebrow">🏆 GTA VI · CHECKLIST 100% PS5</span>',
        '<h1>100% GTA 6: checklist completa senza grinding inutile</h1>',
        '<p>Traccia le <strong>35 categorie</strong> richieste dal gioco e i <strong>18 set di carte</strong>.',
        ' Gli obiettivi parziali non richiedono tutto il contenuto: 15 set carte su 18,',
        ' 200 veicoli base su 277, 100 animali su 255, 300 acrobazie su 397.',
        ' Le cifre sono attribuite a PowerPyx e confrontate con GTABase.</p>',
        '<nav class="ap-top-links"><a class="v-button" href="#ap-100-categories">Le 35 categorie ↓</a>',
        '<a class="v-button secondary" href="#ap-cards">18 set di carte ↓</a>',
        '<a class="v-button secondary" href="'+BASE+'trofei/trofei-difficili/">Trofei difficili ↗</a></nav>',
        '</header>',
        '<aside class="ap-alert"><strong>Risparmio tempo:</strong> concludi la storia, completa',
        ' le attività obbligatorie e conserva le 70 sfide come rifinitura. La checklist',
        ' ufficiale appare dopo i titoli di coda in Progressi → Statistiche → 100%.',
        ' I dati immessi qui restano <strong>solo nel tuo browser</strong>, senza sincronizzazione con PSN.</aside>',
        '<div class="ap-summary" aria-live="polite"><strong data-ap-done-count>0 / 35 categorie raggiunte</strong>',
        '<progress data-ap-overall-progress max="35" value="0" aria-label="Categorie al target"></progress>',
        '<small data-ap-storage>Conteggi manuali, mai dati PSN.</small></div>',
        '<div id="ap-100-categories" class="ap-groups">'
    ]
    for group in GROUP_ORDER:
        arr=[r for r in data["requirements"] if r["category"]==group]
        out+=['<section class="ap-group" data-ap-group="'+e(group)+'"><h2>'+
              e(data["categories"][group])+'</h2><p>'+str(len(arr))+
              ' requisiti: imposta il progresso corrente dal menu in gioco.</p>',
              '<div class="ap-metrics">']
        for item in arr:
            suffix=" GTA$" if item["kind"]=="denaro" else ""
            total_info=" / "+str(item["total"])+" disponibili" if item["total"] is not None else ""
            href=('<a href="'+BASE+e(item["guide"])+'">Guida correlata ↗</a>'
                  if item.get("guide") else "")
            out+=['<article class="ap-metric" data-ap-metric="'+e(item["id"])+'" '
                  'data-ap-target="'+str(item["target"])+'">',
                  '<div class="ap-metric-title"><h3>'+e(item["label"])+'</h3>',
                  '<span class="ap-metric-status" data-ap-metric-status>Da fare</span></div>',
                  '<p>Obiettivo: <strong>'+format(item["target"],",").replace(",","." )+
                  suffix+'</strong>'+e(total_info)+'</p>',
                  '<p class="ap-note">'+e(item["note"])+'</p>',
                  '<label class="ap-metric-label">Progresso in gioco <input type="number" '
                  'min="0" max="'+str(item["total"] or item["target"])+'" step="1" '
                  'inputmode="numeric" data-ap-input="'+e(item["id"])+'" value="0" '
                  'aria-label="Progresso '+e(item["label"])+'"></label>',
                  '<div class="ap-metric-track"><progress max="'+str(item["target"])+'" value="0" '
                  'data-ap-bar aria-label="Avanzamento obiettivo"></progress>',
                  '<span data-ap-ratio>0 / '+str(item["target"])+'</span></div>',
                  href,'</article>']
        out+=['</div></section>']
    out+=['</div><section id="ap-cards" class="ap-cards" data-ap-cards>',
          '<h2>Le 18 collezioni di carte: quali completare prima</h2>',
          '<p>Il trofeo <a href="'+BASE+
          'trofei/trofeo-30-non-toccare-il-mio-mazzo/">«Non toccare il mio mazzo»</a>',
          ' richiede <strong>3 set</strong>; il 100% ne richiede <strong>15 su 18</strong>.',
          ' Tutte le 18 collezioni contengono 480 carte uniche.',
          ' Lasciando da parte tre set da 36, il minimo teorico diventa',
          ' <strong>372 carte</strong>, ma non è una rotta geografica garantita.</p>',
          '<div class="ap-summary"><strong data-ap-card-count>0 / 18 set completati</strong>',
          '<progress max="15" value="0" data-ap-card-progress aria-label="Set verso il 100%"></progress>',
          '<small data-ap-card-details>Obiettivo primo trofeo: 3 set · 100%: 15 set.</small></div>',
          '<div class="ap-card-sets">']
    for c in data["cards"]:
        out+=['<label class="ap-card-set"><input type="checkbox" data-ap-card="'+e(c["id"])+'">',
              '<span><strong>'+e(c["name"])+'</strong><small>'+str(c["total"])+' carte</small></span>',
              '</label>']
    out+=['</div><p><strong>Come raccoglierle:</strong> controlla Progressi → Collezioni',
          ' → Carte collezionabili. Cerca dentro edifici, cabine telefoniche gialle',
          ' e cassette degli attrezzi; vendere una carta registrata non rimuove il progresso,',
          ' ma i doppioni non aggiungono una nuova voce. '
          '<a href="'+e(data["sources"]["cards"])+'" target="_blank" rel="noopener noreferrer">',
          'Apri posizioni e screenshot nella guida originale PowerPyx ↗</a>.</p></section>',
          '<footer class="ap-foot"><h2>Fonti verificate il 21 novembre 2026</h2>',
          _sources(data,("completion","cards","trophy"))+
          '<p>La checklist manuale non consulta PSN e non promette trofei automatici.</p></footer>',
          '</section>']
    return ''.join(out)

def render_hard(data,trophies):
    validate(data,trophies)
    by={t["number"]:t for t in trophies}
    out=[
        '<section class="ap-main ap-hard" id="guida-trofei-difficili">',
        '<header class="ap-hero"><span class="eyebrow">🏆 PS5 · TROFEI DIFFICILI E NASCOSTI</span>',
        '<h1>GTA 6: trofei difficili, Rhino, UFO e percorso Platino</h1>',
        '<p>Procedure operative con verifica separata delle fonti e dell’incertezza.',
        ' Alcuni obiettivi sono nascosti per evitare spoiler automatici.',
        ' <strong>Nessun glitch qui è presentato come Trophy Safe.</strong></p>',
        '<nav class="ap-top-links"><a class="v-button" href="'+BASE+'trofei/100-percento/">Checklist 100% →</a>',
        '<a class="v-button secondary" href="'+BASE+'trofei/roadmap-platino/#guida-55-trofei">Tutti i 55 trofei →</a>',
        '</nav></header><aside class="ap-alert">⚠️ Gli eventi segreti potrebbero',
        ' includere spoiler e segnalazioni contrastanti. Apri solo le schede che ti servono.',
        ' Prima delle operazioni rischiose crea un salvataggio manuale separato.</aside>',
        '<div class="ap-hard-list">'
    ]
    for item in data["hard"]:
        t=by[item["trophy"]]
        links=[
            '<a href="'+BASE+'trofei/'+e(t["slug"])+'/">Apri la scheda del trofeo →</a>'
        ]
        if item["trophy"] in {30}:
            links.append('<a href="'+BASE+'trofei/100-percento/#ap-cards">Checklist 18 set di carte →</a>')
        status={'documentato':"Procedura documentata da guide",
                'probabile':"Evidenze concordanti, dettagli da verificare",
                'incerto':"Procedura non confermata"}[item["status"]]
        steps=''.join('<li>'+e(x)+'</li>' for x in item["steps"])
        inner=(
            '<div class="ap-hard-content"><p>'+e(item["summary"])+'</p>'
            '<ol>'+steps+'</ol><p class="ap-hard-warning">'+e(item["warning"])+'</p>'
            '<div class="ap-hard-links">'+' '.join(links)+'</div>'
            '<p class="ap-photo-note">📷 I link alle fonti seguenti possono contenere',
            ' screenshot originali degli editori. Non li copiamo sul nostro sito',
            ' senza una verifica dei diritti di riutilizzo.</p>'
            +_sources(data,item["sources"])+'</div>'
        )
        out+=['<article class="ap-hard-card" data-hard-trophy="'+str(item["trophy"])+'" '
              'data-hard-status="'+e(item["status"])+'">',
              '<details'+(' open' if not t["hidden"] else '')+'>',
              '<summary><span class="ap-hard-num">#'+str(item["trophy"]).zfill(2)+'</span>',
              '<span><strong>'+e(t["name_it"])+'</strong><small>'+e(status)+
              (' · spoiler' if t["hidden"] else '')+'</small></span>',
              '<span class="ap-hard-arrow" aria-hidden="true">⌄</span></summary>',
              inner+'</details></article>']
    out+=['</div><footer class="ap-foot"><h2>Metodo di verifica</h2>',
          '<p>“Documentato” significa che una guida cita espressamente la procedura;',
          ' non significa che il nostro team abbia sbloccato personalmente il trofeo.',
          ' Per gli eventi casuali e i segreti controversi verifica la tua versione.',
          ' Non forziamo modifiche ai salvataggi, trucchi o procedure pericolose per il Platino.</p>',
          '</footer></section>']
    return ''.join(out)
