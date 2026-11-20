"""Transparent, searchable source-methodology landing page for GTA VI."""
from __future__ import annotations
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

PATH = "fonti/"


def e(value):
    return escape(str(value), quote=True)


def render(write, layout, url, crumbs):
    config = json.loads(Path("data/fonti_editoriali.json").read_text(encoding="utf-8"))
    if config.get("schema") != "gta6-fonti-v1":
        raise ValueError("Unsupported GTA VI source directory schema")
    items = config["sources"]
    if len({x["slug"] for x in items}) != len(items):
        raise ValueError("Duplicate source slugs")
    cards = []
    for src in items:
        parsed = urlsplit(src["link"])
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Invalid source link")
        cards.append(
            '<article class="index-item">'
            f'<span class="card-label">{e(src["tier"])}</span>'
            f'<h3><a href="{e(src["link"])}" target="_blank" rel="noopener noreferrer">{e(src["name"])}</a></h3>'
            f'<p><strong>Per cosa la consultiamo:</strong> {e(src["usage"])}</p>'
            f'<p class="micro"><strong>Limiti:</strong> {e(src["caution"])}</p></article>'
        )
    title = "Fonti GTA 6: PowerPyx, GTAForums, GTABase e metodo"
    desc = ("Come verifichiamo trucchi, glitch, veicoli, missioni e novità di GTA VI: "
            "fonti ufficiali Rockstar, PowerPyx, GTAForums, Fandom, GTABase e video.")
    body = (
        crumbs([("Fonti editoriali", PATH)])
        + '<section class="page-intro"><span class="eyebrow">🔎 GTA VI · METODO EDITORIALE</span>'
        + '<h1>GTA 6: <span class="highlight">fonti, verifiche e novità</span></h1>'
        + '<p class="lead">Non tutte le informazioni su GTA VI arrivano da Rockstar: '
        + 'raccogliamo guide indipendenti, video e analisi della community senza '
        + 'confondere una segnalazione con un annuncio ufficiale.</p>'
        + f'<div class="statline"><span><b>{len(items)}</b> fonti elencate</span>'
        + '<span>🎮 PS5 / PS5 Pro</span><span>🏆 Attenzione ai trofei</span></div></section>'
        + '<div class="info"><strong>Principio di verifica:</strong> le novità ufficiali '
        + 'si basano su dichiarazioni dirette di Rockstar o PlayStation. Le guide '
        + 'di PowerPyx e le testimonianze di GTAForums/Fandom sono fonti '
        + 'indipendenti da confrontare con la patch e la piattaforma.</div>'
        + '<section class="section"><h2>Fonti GTA VI consultabili</h2>'
        + '<p>Ogni fonte ha un ruolo preciso. Il collegamento porta al sito originale: '
        + 'non copiamo articoli o video di terzi.</p>'
        + '<div class="index-list">' + ''.join(cards) + '</div></section>'
        + '<section class="section prose"><h2>Come verifichiamo un trucco GTA VI</h2>'
        + '<ol><li>Confrontiamo i pulsanti e la modalità di inserimento su PS5; '
        + 'una guida che riprende PowerPyx non conta come conferma indipendente.</li>'
        + '<li>Annotiamo requisito, patch, piattaforma e presenza di prove video.</li>'
        + '<li>Se due fonti discordano, segnaliamo il conflitto e rimandiamo '
        + 'alle informazioni mostrate nel menu Progressi del gioco.</li>'
        + '<li>Non definiamo un trucco sicuro per il platino senza prova '
        + 'specifica: GTA VI disabilita trofei e salvataggi durante la sessione '
        + 'con trucchi attivi, secondo le guide consultate.</li></ol>'
        + '<p><a href="' + url("trucchi/") + '">🎮 Elenco codici e sequenze PS5</a></p>'
        + '<h2>Come nascono articoli e aggiornamenti</h2>'
        + '<p>Le discussioni di forum, le wiki e i datamine suggeriscono nuove '
        + 'verifiche. Quando un dato trova conferma, lo trasformiamo in un '
        + 'articolo originale in italiano con fonte, data, versione quando nota '
        + 'e istruzioni utili. Le indiscrezioni attribuite rimangono tali.</p>'
        + '<p>Le notizie e gli aggiornamenti del progetto sono condivisi anche '
        + '<a href="https://x.com/xFederiko11" target="_blank" '
        + 'rel="me noopener noreferrer">sul profilo X @xFederiko11</a>. '
        + 'Nessuna raccolta di dati della community autorizza automaticamente una pubblicazione.</p>'
        + '</section>'
    )
    structured = {
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": title, "description": desc, "inLanguage": "it-IT",
        "url": url(PATH), "numberOfItems": len(items),
        "mainEntity": {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": src["name"], "url": src["link"]}
            for i, src in enumerate(items)
        ]},
    }
    write(PATH + "index.html", layout(title, desc, PATH, body, "sources", structured=structured))
    return PATH
