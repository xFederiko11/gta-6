"""Public, spoiler-gated PS5 screenshot request hub from the existing guide manifest.

No user accounts, image uploads, automatic X posts, licensing inference, fake
completed shots, or gameplay claims. The list is a community request catalog.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import re
from urllib.parse import urlencode

BASE = "https://xfederiko11.github.io/gta-6/"
TARGET = 5
PRIORITY = (
    "soldi-facili-capitolo-1",
    "soldi-2500-three-sheets-liquor",
    "registrare-auto-personale",
    "scansionare-veicoli",
    "viaggio-rapido-taxi",
)


def screenshot_count(guide, media, extras, get_local):
    """Count only distinct real gameplay screenshots in steps or gallery.

    The final Reader pipeline moves some in-step figures into a front gallery;
    both locations are part of the same final guide. Hero promotional art,
    placeholders, remote URLs and videos do not count.
    """
    path = guide["canonical_path"]
    gallery = extras.get(path, {}).get("gallery", [])
    keys = set(guide.get("step_media", {}).values())
    keys.update(x["key"] for x in gallery)
    return sum(bool(media.get(key, {}).get("kind") == "screenshot" and get_local(key))
               for key in keys)


def x_photo_intent(role, guide_url):
    if not (isinstance(role,str) and 8 <= len(role) <= 150):
        raise ValueError("Unverified photo role")
    if not guide_url.startswith(BASE) or not re.fullmatch(
            r"https://xfederiko11\.github\.io/gta-6/(?:[a-z0-9-]+/)+",guide_url):
        raise ValueError("Invalid owned guide URL")
    message = "@xFederiko11 Screenshot PS5 GTA VI: " + role + "\n" + guide_url + " #GTA6Italia"
    if len(message) > 280:
        raise ValueError("X draft exceeds 280 characters")
    return "https://x.com/intent/tweet?" + urlencode({"text": message})


def render(guides, requests, media, extras, get_local):
    """Return valid static HTML and a factual public audit JSON snapshot."""
    if len(guides) < 11:
        raise ValueError("Guide catalog is incomplete")
    ids = {g["id"] for g in guides}
    if len(ids) != len(guides) or ids != set(requests):
        raise ValueError("Photo requests must cover exactly the published guides")
    ordered = sorted(guides,key=lambda g: (
        0 if g["id"] in PRIORITY else 1,
        PRIORITY.index(g["id"]) if g["id"] in PRIORITY else 999,
        str(g["safe_title"]).casefold()))
    records = []
    cards = []
    for g in ordered:
        ident=g["id"]
        path=g["canonical_path"]
        if not re.fullmatch(r"(?:[a-z0-9-]+/)+",path):
            raise ValueError("Unsafe guide path")
        tasks = requests[ident]
        if not isinstance(tasks,list) or len(tasks)!=TARGET:
            raise ValueError("Exactly five source requests required per guide")
        n=screenshot_count(g,media,extras,get_local)
        if n < 0:
            raise ValueError("Bad photo count")
        canonical=BASE+path
        title=str(g["safe_title"])
        tag=str(g["tag"])
        rows=[]
        for i,role in enumerate(tasks,1):
            target=x_photo_intent(role,canonical)
            rows.append(
                '<li class="v-photo-hub-task"><span class="v-photo-hub-task-number">'+
                str(i).zfill(2)+'</span><span>'+escape(role)+'</span>'+
                '<a data-visual-request-photo="'+str(i)+'" href="'+escape(target,quote=True)+
                '" target="_blank" rel="noopener noreferrer" '+
                'aria-label="Proponi su X: '+escape(role,quote=True)+'">Prepara su X ↗</a></li>')
        records.append({
            "id":ident,"path":path,"screenshot_count":n,"target":TARGET,
            "ready":n>=TARGET,"photo_prompts":len(tasks),
        })
        cards.append(
            '<article class="v-photo-hub-card" data-photo-guide="'+escape(ident,quote=True)+'" '
            'data-photo-count="'+str(n)+'"><div class="v-photo-hub-card-head">'+
            '<span class="v-kicker">'+escape(tag)+' · PS5</span>'+
            '<h3><a href="'+escape(canonical,quote=True)+'">'+escape(title)+'</a></h3>'+
            '<p><strong>'+str(n)+' / '+str(TARGET)+'</strong> screenshot di gameplay nel tutorial. '+
            ('Obiettivo editoriale raggiunto.' if n>=TARGET else
             'Restano immagini utili da verificare.')+'</p>'+
            '<progress max="5" value="'+str(min(n,TARGET))+'" aria-label="Copertura delle schermate gameplay">'+
            str(min(n,TARGET))+' di 5</progress></div>'+
            '<details class="v-photo-hub-details"><summary>Apri 5 esempi di screenshot richiesti '
            '(possibili spoiler)</summary><ol class="v-photo-hub-tasks">'+''.join(rows)+'</ol>'+
            '<p>Le richieste indicano cosa documentare, non certificano che la '
            'foto sia mancante, disponibile o autorizzata al riuso.</p></details>'+
            '<a class="v-photo-hub-guide-link" href="'+escape(canonical,quote=True)+
            '">Leggi la guida e controlla i passaggi →</a></article>')
    ready=sum(r["ready"] for r in records)
    photo_total=sum(r["screenshot_count"] for r in records)
    request_total=sum(r["photo_prompts"] for r in records)
    if request_total != len(records)*TARGET:
        raise ValueError("Unexpected photo catalog size")
    body=(
        '<section class="v-photo-hub-head">'
        '<span class="eyebrow">COMMUNITY · GTA VI ITALIA · PS5 / PS5 PRO</span>'
        '<h1>Screenshot GTA 6: rendiamo le guide più chiare</h1>'
        '<p>Ci servono schermate <strong>autentiche</strong> di mappe, menu, '
        'azioni e risultati. Scegli una guida, guarda cosa è utile documentare '
        'e proponi un tuo screenshot su X. Nessun account GitHub richiesto.</p>'
        '<div class="v-photo-hub-stats" role="group" aria-label="Copertura del progetto">'
        '<div><strong>'+str(len(records))+'</strong><small>guide operative</small></div>'
        '<div><strong>'+str(request_total)+'</strong><small>esempi di foto utili</small></div>'
        '<div><strong>'+str(ready)+' / '+str(len(records))+'</strong><small>guide con almeno 5 screenshot</small></div>'
        '</div></section>'
        '<section class="v-photo-hub-how" aria-label="Come contribuire">'
        '<h2>Come contribuire, in tre passaggi</h2>'
        '<ol><li>Apri la guida e verifica quale schermata può aiutare davvero.</li>'
        '<li>Su PS5 usa <strong>Crea (Create)</strong> per catturare una foto di '
        'gameplay originale. Evita dati personali, nomi PSN o messaggi privati.</li>'
        '<li>Premi <strong>Prepara su X</strong>, allega manualmente l’immagine, '
        'indica PS5/PS5 Pro, patch quando conosciuta e segnala gli spoiler.</li></ol>'
        '<p><strong>Importante:</strong> aprire una bozza X non significa '
        'inviare la foto. Il tweet pubblico non autorizza automaticamente '
        'la ripubblicazione: prima di aggiungerla al sito ti chiederemo '
        'il consenso esplicito e verificheremo immagine, fonte e contesto.</p></section>'
        '<section class="v-photo-hub-section"><h2>Le guide che puoi aiutare</h2>'
        '<p>I dettagli fotografici restano chiusi finché non scegli di aprirli: '
        'alcune richieste rivelano luoghi o oggetti della storia. '
        'Le 55 richieste sono <strong>esempi editoriali</strong>, non '
        '55 foto già ricevute né 55 prove tutte mancanti.</p>'
        '<div class="v-photo-hub-grid">'+''.join(cards)+'</div></section>'
        '<section class="v-photo-hub-footer"><h2>Come scegliamo le immagini</h2>'
        '<p>Pubblicheremo soltanto screenshot pertinenti e verificati, '
        'con fonte e attribuzione e autorizzazione al riuso appropriata. '
        'Non sostituiremo mai schermate assenti con mappe inventate, '
        'render fittizi o immagini promozionali spacciate per gameplay.</p>'
        '<a class="v-button secondary" href="'+BASE+'guide-e-tutorial/">Tutte le guide GTA VI →</a>'
        '</section>'
    )
    snapshot={
        "schema":"gta6-community-photo-requests-v1",
        "target_gameplay_screenshots_per_guide":TARGET,
        "guides":len(records),
        "photo_role_examples":request_total,
        "guides_at_target":ready,
        "gameplay_screenshots_counted_across_guides":photo_total,
        "note":"Requests are examples, not received uploads, licensing consent or exact missing-slot assignments.",
        "entries":records,
    }
    return body,snapshot
