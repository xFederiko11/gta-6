"""Community discoveries page without filters; verified source provenance first.

The page is a discoverability index. We can show only facts available from
read-only source feeds, never invent Reddit/X/Discord popularity statistics.
"""
from __future__ import annotations
from datetime import datetime
from html import escape
from pathlib import Path
import json
from urllib.parse import urlsplit,quote
from community_page import DATA,validate,_video_id
from community_social_v1 import home_rail,xpost_for

CATEGORIES=(
    ("𝕏","X Italia: conversazioni GTA VI",
     "https://x.com/search?q="+quote('("GTA VI" OR "GTA 6") lang:it -filter:retweets')+"&f=live",
     "Leggi post pubblici e rispondi dall’account X. I dati di popolarità non sono disponibili in questo sito."),
    ("💬","Reddit: guide e scoperte",
     "https://www.reddit.com/r/GTA6/new/",
     "Confronta i racconti con video e prove. Le segnalazioni sono da verificare."),
    ("🎮","GTAForums: discussioni dettagliate",
     "https://gtaforums.com/",
     "Thread tecnici e scoperte da approfondire prima di pubblicare una nostra guida."),
    ("🗣️","Discord: segnalazioni dei membri",
     "https://discord.com/servers",
     "Solo server e messaggi condivisi pubblicamente dai rispettivi autori; niente accesso a chat private."),
)
def card(item):
    source=item["source"]
    status=item["status"]
    url=item["url"]
    published=item["published_utc"]
    video=_video_id(item)
    image=(
        '<div class="community-video-slot" data-community-video-slot>'
        '<img loading="lazy" decoding="async" alt="Anteprima del video GTA VI pubblicato da '
        +escape(source,quote=True)+'" width="480" height="270" src="https://i.ytimg.com/vi/'+video+'/hqdefault.jpg">'
        '<button class="community-video-play" type="button" data-community-video-id="'+video+'">'
        '▶ Guarda il video originale</button></div>'
        if video else '<div class="community-card-art"><span aria-hidden="true">'+
        ('🧭' if source=="PowerPyx" else "🗺️" if source=="GTABase" else "🔎")+
        '</span><small>FONTE DA VERIFICARE</small></div>')
    # Only the originating page is clickable. No fake excerpt or false social metrics.
    return ('<article class="community-card">'
            +image+'<div class="community-card-copy"><div class="community-card-label">'
            '<span>'+escape(status)+'</span><span class="community-card-source">'+escape(source)+'</span>'
            '</div><h3>'+escape(item["title"])+'</h3>'
            '<p class="micro">Rilevato il <time datetime="'+escape(published,quote=True)+'">'
            +escape(published[:10])+'</time> · Titolo da verificare alla fonte.</p>'
            '<p class="community-verification">Affidabilità: '+('fonte specializzata, contenuto non ricontrollato'
            if source in {"PowerPyx","GTA Series Videos","GTABase"} else
            'segnalazione community non confermata')+'. '
            'Visualizzazioni e like non disponibili.</p>'
            '<a class="community-card-link" href="'+escape(url,quote=True)+'" target="_blank" '
            'rel="noopener noreferrer">Apri la fonte originale ↗</a></div></article>')

def render(write,layout,url,crumbs):
    feed=json.loads(DATA.read_text(encoding="utf-8"))
    rows=validate(feed)
    # Source type is informative; numeric view-count ranking is intentionally
    # NOT used because the public feed provides no verified popularity data.
    ranked=sorted(rows,key=lambda item:(
        item["source"] not in {"GTA Series Videos","PowerPyx","GTABase"},
        -datetime.fromisoformat(item["published_utc"].replace("Z","+00:00")).timestamp()))
    title="GTA VI: scoperte della community, X, Reddit e GTAForums"
    desc=("Scoperte GTA VI in italiano: X, Reddit, GTAForums, community Discord, "
          "guide e video con fonti, stato di verifica, commenti e discussioni.")
    picks="".join(
        '<a class="community-discovery-source" href="'+escape(link,quote=True)+'" '
        'target="_blank" rel="noopener noreferrer"><span>'+icon+'</span><strong>'
        +escape(name)+'</strong><small>'+escape(note)+'</small>'
        '<em>Apri la community ↗</em></a>'
        for icon,name,link,note in CATEGORIES
    )
    stamp=feed.get("generated_utc")
    when=('Scansione: '+escape(stamp[:16].replace("T"," "))+' UTC'
          if isinstance(stamp,str) and stamp else "Prima scansione in preparazione")
    cards="".join(card(row) for row in ranked)
    if not cards:
        cards='<p class="community-empty">Non abbiamo titoli recenti verificabili. '
        cards+='Le conversazioni ufficiali sono accessibili dalle community collegate sopra.</p>'
    page=(
      crumbs([("Scoperte community","scoperte/")])
      +'<section class="community-new-intro"><span class="eyebrow">GTA VI · RICERCA CONDIVISA</span>'
      '<h1>Le scoperte della <span class="highlight">community GTA VI</span></h1>'
      '<p class="lead">Mappe, auto rare, soldi, missioni e curiosità. Le esperienze dei giocatori '
      'sono spunti da controllare, non fatti già confermati. Tutto consultabile senza filtri.</p>'
      '<a class="v-button" href="#commenti">💬 Proponi una scoperta</a>'
      '<a class="v-button secondary" href="#fonti-community">Esplora le fonti ↓</a></section>'
      '<section class="community-discussions-feature" id="fonti-community">'
      '<span class="eyebrow">DOVE NASCONO LE SCOPERTE</span>'
      '<h2>X, Reddit, GTAForums e Discord</h2>'
      '<div class="community-discovery-links">'+picks+'</div></section>'
      '<section class="v-section" id="ultime-scoperte">'
      '<div class="v-section-head"><div><span class="eyebrow">ULTIMI CONTENUTI RACCOLTI</span>'
      '<h2>Video e segnalazioni alla fonte</h2><p>'+escape(when)+
      ' · Il numero di visualizzazioni non è confrontabile tra fonti.</p></div></div>'
      '<div class="community-grid" data-community-grid>'+cards+'</div></section>'
      '<div class="v-spoiler-warning" role="note"><strong>⚠️ Segnalazioni da verificare.</strong> '
      'Un titolo, un commento o un numero di like non dimostra che un glitch funzioni '
      'sull’ultima patch PS5 o che conservi i trofei.</div>'
      '<section class="v-section"><h2>Facci sapere cosa hai trovato</h2>'
      '<p>Indica il luogo, la versione del gioco, i passaggi e — se esiste — '
      'un video o uno screenshot della scoperta. Non pubblicare dati personali.</p>'
      '</section>'
      '<script src="'+url("assets/community-interactions.js")+'" defer></script>'
    )
    structured={"@context":"https://schema.org","@type":"CollectionPage",
                "name":title,"description":desc,"url":url("scoperte/"),
                "inLanguage":"it-IT","numberOfItems":len(rows)}
    write("scoperte/index.html",layout(title,desc,"scoperte/",page,"community",structured=structured))
    return "scoperte/"
