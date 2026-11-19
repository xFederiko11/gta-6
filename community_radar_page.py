"""One SEO landing page for GTA VI community research leads, not unsourced news."""
from __future__ import annotations

from datetime import datetime
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

PATH = "community/"
ALLOWED_LABELS = {
    "Guida indipendente", "Community", "Datamining",
    "Rumor non verificato", "Segnalazione da verificare",
}
ALLOWED_HOSTS = {"youtube.com", "powerpyx.com"}


def e(s):
    return escape(str(s), quote=True)


def render(write, layout, url, crumbs):
    data = json.loads(Path("data/community_radar.json").read_text(encoding="utf-8"))
    if data.get("schema") != "gta6-community-radar-v1":
        raise ValueError("Unexpected community radar schema")
    items = data.get("candidates", [])[:25]
    cards = []
    structured_items = []
    for item in items:
        link = str(item["source_url"])
        u = urlsplit(link)
        if (u.scheme != "https" or (u.hostname or "").removeprefix("www.") not in ALLOWED_HOSTS
                or u.username or u.password or u.port not in (None,443)
                or item["label"] not in ALLOWED_LABELS or item["verified_article"] is not False):
            raise ValueError("Community research item cannot be published as a confirmed fact")
        title, source, status, when = [e(item[k]) for k in
                                       ("title", "source", "label", "published_utc")]
        cards.append(
            '<article class="index-item community-item">'
            f'<span class="card-label">{status}</span>'
            f'<h3>{title}</h3>'
            f'<p>Fonte: <strong>{source}</strong> · Pubblicato: <time datetime="{when}">{when[:10]}</time></p>'
            '<p class="micro">Titolo individuato dal monitor. Contenuto e correttezza non verificati '
            'dal nostro sito; potrebbero esserci spoiler o informazioni superate.</p>'
            f'<a href="{e(link)}" rel="noopener noreferrer nofollow" target="_blank">'
            'Consulta il contenuto originale →</a></article>')
        structured_items.append({"@type":"ListItem","position":len(structured_items)+1,
                                 "name":item["title"],"url":link})
    scanned = data.get("scan_utc")
    if scanned:
        scan_label = e(datetime.fromisoformat(scanned).strftime("%d/%m/%Y, %H:%M UTC"))
    else:
        scan_label = "in attesa della prima sincronizzazione"
    warnings = data.get("feed_warnings") or []
    warning_note = (f'<p class="micro">⚠️ {len(warnings)} avvisi feed registrati '
                    '(consultabili nella coda GitHub).</p>' if warnings else '')
    if not cards:
        cards = ['<p class="info">Il monitor è pronto, ma non ci sono ancora titoli da mostrare. '
                 'Controlla la coda GitHub per lo stato della scansione.</p>']
    title = "GTA 6: novità community, PowerPyx, video PS5 e rumor verificabili"
    desc = ("Radar aggiornato GTA VI: nuove guide PowerPyx e video GTA Series Videos, "
            "indiscrezioni e segnalazioni con fonte, data ed etichetta di affidabilità.")
    body = (
        crumbs([("Radar community", PATH)])
        + '<section class="page-intro"><span class="eyebrow">📡 GTA VI · SCANSIONE AUTONOMA</span>'
        '<h1>Novità GTA 6: <span class="highlight">radar community</span></h1>'
        '<p class="lead">Guide, video e nuove segnalazioni individuate dal nostro bot GitHub. '
        'Non sono notizie confermate da Rockstar: ogni elemento conserva fonte e livello '
        'di affidabilità, e rimanda all’originale.</p>'
        f'<div class="statline"><span><b>{len(items)}</b> titoli in osservazione</span>'
        f'<span>Ultima scansione: {scan_label}</span></div></section>'
        '<div class="info">🔎 <strong>Trasparenza:</strong> la scansione importa soltanto '
        'titoli, date e link dal monitor. Non legge né ricrea integralmente gli articoli. '
        'Gli eventuali rumor restano rumor; nessun metodo è considerato sicuro per i '
        'trofei finché non viene verificato sulla versione PS5.</div>'
        + '<section class="section"><h2>Ultimi titoli segnalati dalle fonti</h2>'
        + warning_note + '<div class="index-list">' + ''.join(cards) + '</div></section>'
        + '<section class="section prose"><h2>Da dove provengono questi aggiornamenti?</h2>'
        '<p>Il bot gira autonomamente su GitHub Actions tre volte al giorno, '
        'senza dipendere da una chat o da ChatGPT. Le fonti raccolte automaticamente '
        'comprendono PowerPyx e GTA Series Videos. GTAForums, GTA Wiki/Fandom, '
        'GTABase e altre community sono registrate per verifiche ulteriori, '
        'ma non vengono descritte come acquisite automaticamente.</p>'
        f'<p><a href="{e(data["queue_url"])}" target="_blank" rel="noopener noreferrer">'
        'Consulta la coda editoriale GitHub →</a>'
        f' · <a href="{url("fonti/")}">Metodo di verifica delle fonti →</a></p>'
        '<p>Le informazioni confermate e utili al platino diventano guide specifiche; '
        'non assegniamo automaticamente lo stato “ufficiale” a un titolo di community.</p>'
        '</section>'
    )
    structured = {
        "@context":"https://schema.org", "@type":"CollectionPage",
        "name":title, "url":url(PATH), "inLanguage":"it-IT",
        "description":desc,
        "mainEntity":{"@type":"ItemList","itemListElement":structured_items},
    }
    write(PATH+"index.html",layout(title,desc,PATH,body,"community",structured=structured))
    return PATH
