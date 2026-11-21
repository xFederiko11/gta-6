"""PS5 photo submission workflow via X (no backend), with strict rights-gated review.

Contributors post screenshots themselves. A checkbox alone is NOT verified
permission: maintainers must review the status post and image before adding an
approved local WebP file and signed provenance record to the repository.
"""
from __future__ import annotations
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
from datetime import date
import hashlib
import re

BASE="https://xfederiko11.github.io/gta-6/"
PATH="screenshot-ps5/invia/"
AUTHORIZED_RIGHTS="explicit_nonexclusive_site_and_social"
IMAGE_DIR=Path("site/assets/approved")
MAX_IMAGE_BYTES=4_000_000


def e(value):
    return escape(str(value),quote=True)


def validate_approved(registry,guides,requests):
    if registry.get("schema")!="gta6-approved-screenshots-v4":
        raise ValueError("Unknown approved screenshot manifest")
    known={g["id"] for g in guides}
    if known!=set(requests) or len(known)!=11:
        raise ValueError("Every guide must have a five-role screenshot request")
    records=registry.get("photos",[])
    if not isinstance(records,list):
        raise ValueError("Invalid photo registry")
    seen=set()
    slots=set()
    for photo in records:
        name=photo.get("id")
        if not isinstance(name,str) or not re.fullmatch(r"[a-z0-9-]{6,55}",name) or name in seen:
            raise ValueError("Invalid or duplicate photo id")
        seen.add(name)
        guide=photo.get("guide_id")
        slot=photo.get("role")
        if guide not in known or type(slot) is not int or not 1<=slot<=5:
            raise ValueError("Photo must map to exactly one existing guide and step")
        if (guide,slot) in slots:
            raise ValueError("Duplicate approved screenshot role for guide")
        slots.add((guide,slot))
        if photo.get("platform") not in ("PS5","PS5 Pro"):
            raise ValueError("Unverified screenshot platform")
        if photo.get("rights")!=AUTHORIZED_RIGHTS or photo.get("author_confirmed") is not True:
            raise ValueError("Screenshot requires creator rights and explicit grant")
        if photo.get("approved_by")!="xFederiko11" or photo.get("human_reviewed") is not True:
            raise ValueError("Screenshots cannot be auto-approved by a bot")
        if photo.get("published") is not True:
            raise ValueError("Approved screenshot must be explicitly published")
        try:
            if date.fromisoformat(photo["approved_on"])<date(2026,11,21):
                raise ValueError("Photo approval date predates intake workflow")
        except (KeyError,TypeError,ValueError) as exc:
            raise ValueError("Missing or invalid human approval date") from exc
        for key in ("source_post","consent_evidence"):
            address=photo.get(key,"")
            url=urlsplit(address)
            if (url.scheme!="https" or url.hostname not in {"x.com","twitter.com"}
                or url.username or url.password or url.query or url.fragment or url.port not in (None,443)
                or not re.fullmatch(r"/[a-zA-Z0-9_]{1,15}/status/[0-9]{6,25}",url.path)):
                raise ValueError("Public X status URL required for source and explicit consent")
        for key in ("credit","alt","caption"):
            label=photo.get(key)
            if not isinstance(label,str) or not 3<=len(label)<=150 or any(x in label for x in "<>"):
                raise ValueError("Missing safe attribution or alt text")
        for key in ("source_sha256","file"):
            if not isinstance(photo.get(key),str):
                raise ValueError("Missing binary proof")
        if not re.fullmatch(r"[0-9a-f]{64}",photo["source_sha256"]):
            raise ValueError("Invalid SHA-256 integrity")
        if photo["file"]!="assets/approved/"+name+".webp":
            raise ValueError("Only reviewed local WebP can be published")
        path=Path("site")/photo["file"]
        root=IMAGE_DIR.resolve()
        if not path.resolve().is_relative_to(root) or not path.is_file():
            raise ValueError("Approved WebP must exist inside site/assets/approved")
        binary=path.read_bytes()
        if not (1500<=len(binary)<=MAX_IMAGE_BYTES and
                binary[:4]==b"RIFF" and binary[8:12]==b"WEBP"):
            raise ValueError("Approved image must be a valid-sized WebP container")
        if hashlib.sha256(binary).hexdigest()!=photo["source_sha256"]:
            raise ValueError("Approved image hash changed")
    return True


def approved_count(registry,guide_id):
    return sum(1 for p in registry["photos"] if p["guide_id"]==guide_id)


def render_approved_for_guide(guide,registry):
    items=[p for p in registry["photos"] if p["guide_id"]==guide["id"]]
    if not items:
        return ""
    body=[
        '<section class="pi-approved" id="foto-community-approvate">',
        '<h2>Foto PS5 della community approvate</h2>',
        '<p>Screenshot originali verificati editorialmente, con consenso',
        ' esplicito alla ripubblicazione. Non sono sincronizzati con PSN.</p>',
        '<div class="pi-approved-grid">'
    ]
    for photo in items:
        body.extend([
            '<figure><a href="'+BASE+e(photo["file"])+'" target="_blank" rel="noopener noreferrer">',
            '<img class="v-photo" data-visual-image="community-'+e(photo["id"])+'" data-visual-kind="screenshot" '
            'data-approved-community-photo="'+e(photo["id"])+'" src="'+BASE+e(photo["file"])+'" loading="lazy" decoding="async" ',
            'alt="'+e(photo["alt"])+'" width="960" height="540"></a>',
            '<figcaption>'+e(photo["caption"])+
            ' · Step '+str(photo["role"])+' · © '+e(photo["credit"])+' ',
            '<a href="'+e(photo["consent_evidence"])+'" target="_blank" rel="noopener noreferrer">',
            'Fonte e consenso verificati ↗</a></figcaption></figure>'
        ])
    body.append('</div></section>')
    if guide.get("spoiler"):
        return '<details class="pi-approved-spoilers"><summary>Apri screenshot approvati (spoiler)</summary>'+''.join(body)+'</details>'
    return ''.join(body)


def render(guides,requests,registry):
    validate_approved(registry,guides,requests)
    ordered=sorted(guides,key=lambda g:g["safe_title"].casefold())
    options=[]
    roleoptions=[]
    for g in ordered:
        options.append('<option value="'+e(g["id"])+'" data-guide-link="'+e(g["canonical_path"])+'">'+e(g["safe_title"])+'</option>')
        for index,role in enumerate(requests[g["id"]],1):
            roleoptions.append('<option value="'+str(index)+'" data-photo-guide="'+e(g["id"])+'">'+str(index)+'. '+e(role)+'</option>')
    return ''.join((
        '<section class="pi-page" data-photo-intake><header class="pi-hero">'
        '<span class="eyebrow">📸 GTA VI ITALIA · CONTRIBUTI PS5</span>',
        '<h1>Invia uno screenshot PS5 per una guida GTA 6</h1>',
        '<p>Scegli <strong>guida e passaggio</strong>, prepara il post su X e',
        ' allega personalmente la foto originale. <strong>Non è un upload dal sito:</strong>',
        ' non raccogliamo file, password o dati PSN e non salviamo qui il modulo.</p>',
        '<nav class="pi-links"><a class="v-button secondary" href="'+BASE+'screenshot-ps5/">',
        '55 richieste di foto →</a><a class="v-button secondary" href="'+BASE,
        'screenshot-ps5/verifica/">Registro fonti e diritti →</a></nav></header>',
        '<aside class="pi-warning"><strong>Autorizzazione, non caricamento automatico.</strong>',
        ' Il post su X sarà pubblico e dovrai allegare manualmente lo screenshot.',
        ' La dichiarazione di consenso non garantisce che la foto venga accettata:',
        ' ogni immagine, origine e permesso saranno ricontrollati da un revisore umano.',
        ' Nessun contributo può entrare sul sito tramite un link social da solo.</aside>',
        '<form class="pi-form" data-intake-form novalidate>',
        '<label>Guida da illustrare',
        '<select required data-pi-guide name="guide">'+''.join(options)+'</select></label>',
        '<label>Quale screenshot manca?',
        '<select required data-pi-role name="step"></select></label>',
        '<label>Piattaforma',
        '<select data-pi-platform name="platform"><option>PS5</option><option>PS5 Pro</option></select></label>',
        '<label>Versione/patch (facoltativa, non inventarla)',
        '<input data-pi-patch type="text" maxlength="18" autocomplete="off" placeholder="Es. 1.001"></label>',
        '<label>Credito pubblico da indicare',
        '<input data-pi-credit type="text" maxlength="24" required autocomplete="off" placeholder="Es. @tuoprofiloX"></label>',
        '<label class="pi-check"><input type="checkbox" data-pi-owner required>',
        '<span>Confermo di aver catturato personalmente lo screenshot e',
        ' di non mostrare ID PSN, messaggi privati o dati sensibili.</span></label>',
        '<label class="pi-check"><input type="checkbox" data-pi-rights required>',
        '<span><strong>Autorizzo volontariamente e in modo non esclusivo</strong>',
        ' GTA VI Italia a ripubblicare questo screenshot gratuitamente',
        ' sul sito e sui canali social del progetto con il credito indicato.',
        ' Posso chiedere di non riutilizzarlo in futuro scrivendo al profilo X.',
        ' La proprietà della mia foto rimane mia.</span></label>',
        '<label class="pi-check"><input type="checkbox" data-pi-public required>',
        '<span>So che aprire X non pubblica nulla: dovrò allegare la foto',
        ' e confermare il post io stesso.</span></label>',
        '<p class="pi-form-status" data-pi-status role="status" aria-live="polite">',
        'Seleziona i dati e conferma le caselle per preparare il post.</p>',
        '<button class="v-button" type="submit" data-pi-submit disabled>',
        'Prepara post X con consenso ↗</button>',
        '<a href="#" data-pi-fallback target="_blank" rel="noopener noreferrer" hidden>',
        'Apri manualmente la bozza su X ↗</a>',
        '<template data-pi-role-options>'+''.join(roleoptions)+'</template>',
        '</form>',
        '<section class="pi-how"><h2>Cosa succede dopo il post</h2>',
        '<ol><li>Su X controlla il testo, allega l’immagine originale PS5,',
        ' segnala spoiler e <strong>pubblica</strong> se vuoi partecipare.</li>',
        '<li>Un revisore verifica che foto e contesto coincidano con il',
        ' passaggio, che il consenso sia esplicito e che sia presente il credito.</li>',
        '<li>Solo dopo revisione, l’immagine ottimizzata può essere aggiunta',
        ' tramite pull request al repository con prova di provenienza, hash',
        ' e controllo automatico della build.</li></ol>',
        '<p>Stato attuale: <strong>'+str(len(registry["photos"]))+
        '</strong> nuove foto di community autorizzate in archivio.',
        ' Il sito non legge automaticamente i post X, quindi i contributi',
        ' non sono pubblicati in modo automatico.</p></section></section>'
    ))
