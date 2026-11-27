"""Evidence-led Italian strip-club guide with opt-in hosted video and external map pins."""
from __future__ import annotations
import hashlib
from pathlib import Path

PATH = "guide-e-tutorial/strip-club-gta-6/"
PUBLISHED = "2026-11-27"
TITLE = "GTA 6: dove sono i tre strip club e come raggiungerli"
DESCRIPTION = (
    "Mappa e indicazioni per NINE1NINE, Jack of Hearts e Delights Cabaret in GTA 6. "
    "Capitoli e prezzi sono separati per livello di conferma."
)
VIDEO_ID = "uMEhEEfQt1U"

MAPS = {
    "nine": "https://gtami.com/en/map/?place=gtadb-L190",
    "jack": "https://gtami.com/en/map/?place=gtadb-L172",
    "delights": "https://gtami.com/en/map/?place=gtadb-L629",
}
VIDEO = "https://www.youtube.com/watch?v=" + VIDEO_ID
SOURCES = {
    "gtami": "https://gtami.com/en/guides/strip-clubs/",
    "pcgamer": "https://www.pcgamer.com/games/grand-theft-auto/gta-6-strip-club-locations/",
    "everyeye": "https://www.everyeye.it/notizie/gta-6-trovare-strip-club-sbloccare-balli-privati-912844.html",
}
CSS_PATH = "site/assets/strip-club-guide-v1.css"
JS_PATH = "site/assets/strip-club-guide-v1.js"


def body(url, crumbs):
    maps = MAPS
    crumb_html = crumbs([("Guide e tutorial", "guide-e-tutorial/"), ("Strip club GTA 6", PATH)])
    return f"""
{crumb_html}
<article class="sc-article">
  <header class="sc-intro">
    <p class="sc-eyebrow">Guida GTA VI · posizioni sulla mappa</p>
    <h1>{TITLE}</h1>
    <p class="sc-answer"><strong>Risposta rapida:</strong> le tre location sono NINE1NINE, Jack of Hearts e Delights Cabaret. Trovi NINE1NINE nel Downtown di Vice City, Jack of Hearts a Crosstown e Delights a Port Gellhorn. Apri il pin esterno del locale per orientarti sulla mappa di Leonida.</p>
    <p class="sc-date">Pubblicata <time datetime="{PUBLISHED}">il 27 novembre 2026</time> · aggiornamento mostrato nella testata della pagina.</p>
    <p class="sc-confidence"><strong>Affidabilità:</strong> alta per nomi e aree, riportati da più fonti; media per capitoli e prezzi, non verificati con una nostra cattura PS5. Le divergenze sono indicate nei singoli punti.</p>
  </header>

  <nav class="sc-map-index" aria-label="Apri la mappa esterna del locale">
    <a href="{maps['nine']}" target="_blank" rel="noopener noreferrer"><span>01</span><strong>NINE1NINE</strong><small>Downtown · Vice City</small><b>Apri pin esterno ↗</b></a>
    <a href="{maps['jack']}" target="_blank" rel="noopener noreferrer"><span>02</span><strong>Jack of Hearts</strong><small>Crosstown · Vice City</small><b>Apri pin esterno ↗</b></a>
    <a href="{maps['delights']}" target="_blank" rel="noopener noreferrer"><span>03</span><strong>Delights Cabaret</strong><small>Port Gellhorn</small><b>Apri pin esterno ↗</b></a>
  </nav>

  <section class="sc-video" aria-labelledby="sc-video-title">
    <h2 id="sc-video-title">Guarda le tre zone in un video</h2>
    <p>Video in spagnolo di GTAAccess, canale fan non affiliato a Rockstar. Il filmato resta ospitato su YouTube: il player viene richiesto solo quando scegli di caricarlo; senza clic rimane disponibile il link diretto.</p>
    <div class="sc-video-frame">
      <button type="button" class="sc-video-load" data-strip-video-load data-video-id="{VIDEO_ID}" aria-label="Carica il video GTAAccess su YouTube">
        <span class="sc-play" aria-hidden="true">▶</span>
        <strong>Carica il video YouTube</strong>
        <small>Nessuna anteprima o connessione a YouTube prima del clic</small>
      </button>
    </div>
    <p class="sc-video-source">Fonte: <a href="{VIDEO}" target="_blank" rel="noopener noreferrer">GTAAccess su YouTube</a>. La descrizione del video attribuisce alcune immagini a HarryNinetyFour. Non scarichiamo né riutilizziamo immagini del video.</p>
  </section>

  <section class="sc-locations" aria-labelledby="sc-locations-title">
    <h2 id="sc-locations-title">Dove si trova ogni strip club</h2>
    <ol class="sc-locations-list">
      <li id="nine1nine">
        <h3>NINE1NINE — Downtown, Vice City</h3>
        <p>È accanto al nightclub The Vault. Da Leonida Keys, PC Gamer descrive il tragitto lungo Route 1 verso Hamlet, poi Route 97 in direzione nord fino al Downtown. Il pin GTAMI aiuta a individuare l’isolato senza copiare la mappa sul nostro sito.</p>
        <ul><li><strong>Accesso:</strong> GTAMI lo indica disponibile dal Capitolo 1.</li><li><strong>Ballo privato:</strong> GTAMI e PC Gamer riportano 300 GTA$.</li></ul>
        <a class="sc-map-link" href="{maps['nine']}" target="_blank" rel="noopener noreferrer">Apri il pin NINE1NINE sulla mappa GTAMI ↗</a>
      </li>
      <li id="jack-of-hearts">
        <h3>Jack of Hearts — Crosstown, Vice City</h3>
        <p>Si trova su Miramar Drive, nella piccola area commerciale di Crosstown a nord del NINE1NINE. GTAMI colloca l’apertura all’inizio del Capitolo 3. PC Gamer dice che l’accesso dipende dalla storia, ma precisa di non essere riuscito a entrare e di ipotizzare il Capitolo 3: considera quindi il capitolo un riferimento da verificare in partita.</p>
        <ul><li><strong>Prezzo:</strong> non lo presentiamo come verificato. Everyeye riferisce 1.000 GTA$, mentre PC Gamer non è entrato e GTAMI non indica una tariffa.</li><li><strong>Se l’ingresso è chiuso:</strong> prosegui la storia e torna al locale; non c’è una procedura di sblocco alternativa documentata nelle fonti consultate.</li></ul>
        <a class="sc-map-link" href="{maps['jack']}" target="_blank" rel="noopener noreferrer">Apri il pin Jack of Hearts sulla mappa GTAMI ↗</a>
      </li>
      <li id="delights-cabaret">
        <h3>Delights Cabaret — Port Gellhorn</h3>
        <p>È nel nord-ovest di Leonida, vicino alla I-404. PC Gamer suggerisce di raggiungere Hamlet, proseguire a nord-ovest su Route 82, poi Route 103 fino alla 404 e seguire il cartellone verso Port Gellhorn. Per l’ultimo tratto usa il pin esterno.</p>
        <ul><li><strong>Accesso:</strong> GTAMI lo indica dal Capitolo 1; PC Gamer riferisce di averlo visitato nelle prime ore.</li><li><strong>Ballo privato:</strong> le fonti sono in disaccordo. PC Gamer riporta un ballo da 40 GTA$; Everyeye afferma che non è disponibile. GTAMI lo definisce il più economico ma non dà il prezzo. Controlla il menu del locale nella tua partita prima di spendere.</li></ul>
        <a class="sc-map-link" href="{maps['delights']}" target="_blank" rel="noopener noreferrer">Apri il pin Delights Cabaret sulla mappa GTAMI ↗</a>
      </li>
    </ol>
  </section>

  <section class="sc-map-note">
    <h2>Come usare i pin esterni</h2>
    <ol><li>Scegli il locale nell’indice qui sopra.</li><li>Il collegamento apre GTAMI in una nuova scheda e centra il pin.</li><li>Confronta l’area con la mappa in gioco e imposta il waypoint se la tua versione lo consente.</li></ol>
    <p>GTAMI è un progetto indipendente e non una mappa ufficiale Rockstar. Dichiara che alcune coordinate e descrizioni provengono dalla community e potrebbero non essere ancora verificate in gioco. Usa il pin come orientamento, non come prova di una cattura PS5 o di un punto ufficiale.</p>
  </section>

  <section class="sc-rights-note">
    <h2>Immagini e verifica</h2>
    <p>Questa guida non riutilizza screenshot statici: non abbiamo una prova documentata per questo contenuto e per il canale sito. La copertina editoriale è una grafica originale con testo e simboli cartografici, non un’immagine di gioco né una cattura PS5 e non prova la posizione di un locale. Per vedere gameplay, carica il video YouTube sopra o aprilo direttamente; non ospitiamo copie, miniature o fotogrammi.</p>
  </section>

  <section class="sc-sources" aria-labelledby="sc-sources-title">
    <h2 id="sc-sources-title">Fonti e crediti</h2>
    <ul>
      <li><a href="{SOURCES['gtami']}" target="_blank" rel="noopener noreferrer">GTAMI — posizioni, capitoli e mappa interattiva</a> (aggiornata il 20 novembre 2026; progetto fan indipendente).</li>
      <li><a href="{SOURCES['pcgamer']}" target="_blank" rel="noopener noreferrer">PC Gamer — posizioni, itinerari e note sulle attività</a> (articolo del 19 novembre 2026; autore dichiara di aver giocato).</li>
      <li><a href="{SOURCES['everyeye']}" target="_blank" rel="noopener noreferrer">Everyeye — guida in italiano a posizioni e balli privati</a> (21 novembre 2026; alcune informazioni sui prezzi divergono dalle altre fonti).</li>
      <li><a href="{VIDEO}" target="_blank" rel="noopener noreferrer">GTAAccess — video in spagnolo sulle tre location</a> (canale fan; contenuto ospitato da YouTube).</li>
    </ul>
    <p>Non affiliati a Rockstar Games o Take-Two. Priorità alle schermate del gioco e alla verifica personale quando saranno disponibili. Nessun dato di questa pagina è una posizione acquisita dai nostri screenshot PS5.</p>
  </section>

  <nav class="sc-related" aria-label="Altre guide">
    <a href="{url('guide-e-tutorial/')}">Tutte le guide e i tutorial GTA 6</a>
    <a href="{url('articoli/')}">Cerca negli articoli e nelle categorie</a>
  </nav>
</article>
"""


def build(write, layout, url, crumbs):
    css = Path(CSS_PATH).read_bytes()
    js = Path(JS_PATH).read_bytes()
    version = hashlib.sha256(css + js).hexdigest()[:12]
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": TITLE,
        "description": DESCRIPTION,
        "inLanguage": "it-IT",
        "url": url(PATH),
        "mainEntityOfPage": url(PATH),
        "datePublished": PUBLISHED,
        "author": {"@type": "Organization", "name": "GTA VI Italia"},
        "articleSection": "Guide e missioni",
    }
    page = layout(TITLE, DESCRIPTION, PATH, body(url, crumbs), "guide", structured=schema)
    page = page.replace(
        "</head>",
        f'<link rel="stylesheet" href="{url("assets/strip-club-guide-v1.css")}?v={version}"></head>',
        1,
    )
    page = page.replace(
        "</body>",
        f'<script src="{url("assets/strip-club-guide-v1.js")}?v={version}" defer></script></body>',
        1,
    )
    write(PATH + "index.html", page)
    return PATH
