"""GTA VI screenshot provenance ledger and editorial queue.

No scraped/unauthorized new images are copied to the static build.
We do not equate a third-party screenshot with original rights clearance.
"""
from __future__ import annotations
from html import escape
from urllib.parse import urlsplit
import re

PATH="screenshot-ps5/verifica/"
BASE="https://xfederiko11.github.io/gta-6/"
SOURCE_DOMAINS={"insider-gaming.com","www.pushsquare.com","www.powerpyx.com"}


def e(s):
    return escape(str(s),quote=True)


def validate(ledger,media,guides):
    if ledger.get("schema")!="gta6-photo-provenance-review-v3":
        raise ValueError("Unknown provenance schema")
    pictures={k for k,v in media.items() if v.get("kind")=="screenshot"}
    assets=ledger.get("assets",[])
    if len(assets)!=10 or {x["key"] for x in assets}!=pictures:
        raise ValueError("Screenshot ledger must cover exactly all ten existing source assets")
    by={g["id"]:g for g in guides}
    for item in assets:
        if item["guide"] not in by:
            raise ValueError("Image references a non-existent guide")
        if item.get("reuse_permission")!="not_documented" or item.get("count_as_new_photo") is not False:
            raise ValueError("Existing editorial screenshot cannot acquire unverified rights")
        if item.get("classification")!="published-gameplay-screenshot":
            raise ValueError("Only existing gameplay screenshots are indexed")
        if len(item.get("rights_note",""))<20:
            raise ValueError("Rights warning required")
        link=urlsplit(media[item["key"]]["source"])
        if link.scheme!="https" or link.hostname not in SOURCE_DOMAINS:
            raise ValueError("Unapproved screenshot source")
    leads=ledger.get("leads",[])
    if len(leads)<8 or len({x["id"] for x in leads})!=len(leads):
        raise ValueError("Missing editorial review leads")
    for lead in leads:
        path=urlsplit(lead["url"])
        if path.scheme!="https" or path.hostname!="www.powerpyx.com" or path.username or path.password:
            raise ValueError("Unsupported photo review destination")
        if lead.get("copy_to_site") is not False or lead.get("reuse_permission")!="not_documented":
            raise ValueError("External photo lead cannot be copied before consent review")
        if lead.get("original_visual")!="review_at_source" or lead.get("priority") not in {"alta","media"}:
            raise ValueError("Unreviewed source must be disclosed")
        if not re.fullmatch(r"(?:[a-z0-9-]+/)+",lead["guide"]):
            raise ValueError("Bad internal guide path")
    return True


def render(ledger,media,guides,get_local):
    validate(ledger,media,guides)
    guides_by_id={g["id"]:g for g in guides}
    available=sum(bool(get_local(a["key"])) for a in ledger["assets"])
    body=[
        '<section class="pr-ledger" data-photo-review-ledger>',
        '<header class="pr-hero"><span class="eyebrow">📷 GTA VI · SCREENSHOT PS5</span>',
        '<h1>Screenshot GTA 6: fonti, verifica e immagini mancanti</h1>',
        '<p>Inventario delle <strong>10 immagini di gameplay attribuite a editori</strong>',
        ' già presenti nel catalogo: distinguere la disponibilità tecnica',
        ' dall’autenticità attribuita e dai <strong>diritti di riutilizzo</strong>',
        ' è fondamentale. Nessuna immagine nuova viene importata senza revisione.</p>',
        '<div class="pr-totals"><div><strong>'+str(len(ledger["assets"]))+
        '</strong><small>schermate editoriali catalogate</small></div>',
        '<div><strong>'+str(available)+
        '</strong><small>asset locali disponibili nella build</small></div>',
        '<div><strong>0</strong><small>permessi specifici documentati</small></div>',
        '<div><strong>'+str(len(ledger["leads"]))+
        '</strong><small>fonti prioritarie da esaminare</small></div></div>',
        '<nav class="pr-shortcuts"><a class="v-button" href="'+BASE+'screenshot-ps5/">',
        'Guarda le 55 richieste fotografiche →</a><a class="v-button secondary" href="' + BASE + 'screenshot-ps5/invia/">Invia con consenso →</a><a class="v-button secondary" href="'
        +BASE+'mappe-guide/">Tutte le mappe delle guide →</a></nav></header>',
        '<aside class="pr-warning"><strong>Nota sui diritti:</strong> link, crediti e',
        ' screenshot già presenti nell’archivio non dimostrano una licenza',
        ' per ripubblicare. Per nuove immagini chiediamo una cattura originale',
        ' PS5 e consenso esplicito. La pubblicazione su X di una foto non autorizza',
        ' automaticamente a copiarla sul nostro sito. I render promozionali',
        ' non sono prove di gameplay.</aside>',
        '<section class="pr-group"><h2>10 immagini: origine e stato</h2>',
        '<p>Le immagini collegate non sono ripubblicate ulteriormente in questa',
        ' pagina: usa la guida corrispondente e apri la fonte editoriale.</p>',
        '<div class="pr-list">'
    ]
    for item in ledger["assets"]:
        k=item["key"]; src=media[k]; g=guides_by_id[item["guide"]]
        local=bool(get_local(k))
        body.append(
            '<article class="pr-record" data-provenance-key="'+e(k)+'" data-local-evidence="'+
            ("true" if local else "false")+'"><div class="pr-record-head">'
            '<strong>'+e(src["caption"])+'</strong>'
            '<small>'+("Asset locale disponibile" if local else "Asset locale non disponibile")+'</small></div>'
            '<p>'+e(item["subject"])+' · '+e(src["credit"])+'</p>'
            '<p class="pr-rights">Diritti: permesso specifico non documentato.</p>'
            '<div class="pr-links"><a href="'+BASE+e(g["canonical_path"])+'">Guida con immagini →</a>'
            '<a href="'+e(src["source"])+'" target="_blank" rel="noopener noreferrer">'
            'Vai alla fonte originale ↗</a></div></article>'
        )
    body.extend([
        '</div></section>',
        '<section class="pr-group"><h2>8 nuove fonti per screenshot ancora mancanti</h2>',
        '<p>Queste pagine possono aiutare a verificare percorsi e scatti,',
        ' ma sono <strong>candidati editoriali</strong>, non contenuti importati',
        ' o concessi in licenza.</p><div class="pr-list">'
    ])
    for item in ledger["leads"]:
        body.append(
            '<article class="pr-record" data-photo-source-lead="'+e(item["id"])+'">'
            '<div class="pr-record-head"><strong>'+e(item["id"].capitalize())+'</strong>'
            '<small>Priorità '+e(item["priority"])+'</small></div>'
            '<p>'+e(item["review"])+'</p>'
            '<p class="pr-rights">Da verificare: immagine originale e diritti di pubblicazione.</p>'
            '<div class="pr-links"><a href="'+BASE+e(item["guide"])+'">Guida sul nostro sito →</a>'
            '<a href="'+e(item["url"])+'" target="_blank" rel="noopener noreferrer">'
            'Controlla la fonte originale ↗</a></div></article>'
        )
    body.extend([
        '</div></section><section class="pr-group"><h2>Come contribuire senza perdere attribuzione</h2>',
        '<ol class="pr-intake-steps"><li>Fai una cattura originale PS5 della fase descritta',
        ' nella richiesta fotografica della guida.</li>',
        '<li>Indica nome della missione, capitolo, eventuale versione/patch e',
        ' passo rappresentato; evita di mostrare dati personali o l’ID PSN se non vuoi.</li>',
        '<li>Invia il riferimento a <a href="https://x.com/xFederiko11"',
        ' target="_blank" rel="noopener noreferrer">@xFederiko11 su X</a>.',
        ' Il semplice invio non implica autorizzazione alla pubblicazione.</li>',
        '<li>Prima di pubblicare chiediamo un permesso esplicito per la riproduzione',
        ' dell’immagine e conserviamo il credito.</li></ol>',
        '<p>La coda di revisione del bot è visibile alla redazione '
        '<a href="https://github.com/xFederiko11/federiko-gta-playstation-bot/issues" '
        'target="_blank" rel="noopener noreferrer">nelle Issue GitHub del bot ↗</a>, '
        'ma i giocatori inviano le foto soltanto tramite X e non devono accedere a GitHub.</p>',
        '<p>Inventario aggiornato il '+e(ledger["reviewed"])+
        '. Non sono stati importati screenshot aggiuntivi in questo aggiornamento.</p>',
        '</section></section>'
    ])
    return ''.join(body)
