"""Curated GTA VI video hub sourced from the site's existing reviewed references.

No video download, mirrored thumbnail, invented creator consent or endorsement.
Each YouTube player is instantiated only after the reader explicitly clicks.
"""
from __future__ import annotations
from html import escape
from pathlib import Path
import json
import re

from moses_vehicle_jobs_v1 import IGN_TIMELINE, IGN_VIDEO_ID, SOURCE as MOSES_SOURCE
from garage_guides_v1 import SOUTH_MEDIA, SOUTH_STEPS, SOUTH
from vehicle_progression_guides_v1 import CLONER, CLONER_VIDEO_ID, CLONER_VIDEO
from collectible_video_refs_v1 import REFERENCES as CARD_VIDEO
from waink_visual_v1 import VIDEO_ID as WAINK_VIDEO_ID, CREATOR as WAINK_CREATOR, SOURCE as WAINK_SOURCE

PATH = "video-tutorial/"
VIDEO_DATA = Path("data/guide_visual_refs.json")
BASE = "https://xfederiko11.github.io/gta-6/"
# Local editorial descriptions, not invented quotations or descriptions of
# unseen footage. The linked guide provides the source-checked procedure.
CURATED = (
    ("registrare-auto-personale", "auto", "Registrare la prima auto da Moses",
     "Dal controllo tracker alla registrazione: usa il video come riferimento mentre segui i sette passaggi italiani.",
     "salvare-auto/"),
    ("moses-ign", "auto", "Le sei auto da recuperare per Moses",
     "Sei momenti del filmato IGN associati alle sei consegne; il regalo finale NON compare in questo video.",
     "guide-e-tutorial/veicoli-per-moses/"),
    ("waink-tutorial", "auto", "Scansionare veicoli con WAiNK",
     "Apri il filmato originale dedicato allo scanner, poi confronta i cinque passaggi e i tracker descritti nella guida italiana.",
     "guide-e-tutorial/scansionare-veicoli/"),
    ("key-cloner-perfect-score", "auto", "Key Cloner: la missione di Randy",
     "Guarda il filmato originale dall’inizio e confrontalo con i sei passaggi italiani. Nessun minuto specifico è stato accertato.",
     CLONER),
    ("southside-powerpyx-video", "garage", "Southside Storage: cinque murales e garage",
     "Scegli il riferimento video di ciascun murale 1010 oppure della ricompensa. La guida separa il punto di scatto dal pin della mappa.",
     SOUTH),
    ("meditazione-capitolo-1", "collezionabili", "Le dieci meditazioni: luoghi e percorso",
     "Dieci capitoli dichiarati dal creator, associati ai luoghi della guida. Usa anche la checklist italiana e la mappa della fonte.",
     "guide-e-tutorial/meditazione-capitolo-1/"),
    ("jack-of-hearts-gta-series", "collezionabili", "Jack of Hearts: le 36 carte",
     "Il titolo del filmato indica tutte le 36 carte; sono disponibili due riferimenti temporali dichiarati dal creator. Confronta numero, colore e luogo con l’atlante italiano.",
     "collezionabili/percorsi/"),
    ("soldi-facili-capitolo-1", "soldi", "Riconoscere Three Sheets Liquor",
     "Il filmato mostra il negozio e l’indizio del pappagallo: non è prova di tutte le altre posizioni o di un bottino garantito.",
     "guide-e-tutorial/soldi-facili-capitolo-1/"),
    ("prima-persona-glitch-ps5", "extra", "Visuale in prima persona su PS5",
     "Segnalazione della community: prova soltanto su un salvataggio separato. Patch e compatibilità con i trofei non certificate.",
     "guide-e-tutorial/glitch-prima-persona-ps5/"),
)
KINDS = {"auto": "Auto e missioni", "garage": "Garage e sblocchi",
         "collezionabili": "Collezionabili e meditazioni", "soldi": "Soldi e segreti",
         "extra": "Glitch della community"}
IDS = frozenset(row[0] for row in CURATED)


def load():
    return json.loads(VIDEO_DATA.read_text(encoding="utf-8"))


def records(data):
    if data.get("schema") != "gta6-guide-video-evidence-v1":
        raise ValueError("Unrecognized reviewed video registry")
    refs = data.get("guides", {})
    result = []
    videos = set()
    for key, category, title, detail, guide_path in CURATED:
        if category not in KINDS or not re.fullmatch(r"(?:[a-z0-9-]+/)+", guide_path):
            raise ValueError("Invalid curated guide location")
        if key == "moses-ign":
            video_id = IGN_VIDEO_ID
            creator = "IGN"
            chapters = [{"at": second, "label": label+" · "+name}
                        for (second,label),name in zip(IGN_TIMELINE, (
                            "Yosemite 1500", "Karin Futo", "Annis Hellion",
                            "BF Bandito", "Declasse Vamos", "Western Nightblade"))]
            source = MOSES_SOURCE
            spoiler = True
            provenance = "Filmato sul canale IGN; riferimenti alle sei consegne."
        elif key == "waink-tutorial":
            video_id = WAINK_VIDEO_ID
            creator = WAINK_CREATOR
            chapters = [{"at":0, "label":"0:00 · Tutorial WAiNK"}]
            source = WAINK_SOURCE
            spoiler = True
            provenance = "Video originale già collegato alla guida WAiNK; non costituisce una prova di ogni singola schermata."
        elif key == "key-cloner-perfect-score":
            video_id = CLONER_VIDEO_ID
            creator = "Perfect Score"
            chapters = [{"at":0, "label":"0:00 · Avvia il filmato originale"}]
            source = CLONER_VIDEO
            spoiler = True
            provenance = "Video già collegato alla guida Key Cloner; inizio del filmato, non un timecode verificato della missione. Riproduzione non verificata indipendentemente."
        elif key == "jack-of-hearts-gta-series":
            video_id = CARD_VIDEO["youtube_id"]
            creator = CARD_VIDEO["creator"]
            chapters = [{"at":row["at"], "label":str(row["at"]//60)+":"+str(row["at"]%60).zfill(2)+" · "+row["chapter_label"]}
                        for row in sorted(CARD_VIDEO["moments"].values(),key=lambda row:row["at"])]
            source = CARD_VIDEO["source_url"]
            spoiler = True
            provenance = "Due capitoli dichiarati dal creator: confronta la carta con la fonte scritta. Malena Deep Red non è confermata equivalente a Malena Rosso; nessuna posizione duplicata o riproduzione verificata."
        elif key == "southside-powerpyx-video":
            item = SOUTH_MEDIA[key]
            if item["rights_status"] != "youtube_platform_embed_only" or "site_opt_in_embed" not in item["allowed_channels"]:
                raise ValueError("Southside video lacks the existing embed-only media contract")
            video_id = item["video_id"]
            creator = item["source_name"]
            chapters=[]
            for number, second in sorted(item["timestamps_seconds"].items(),key=lambda x:int(x[0])):
                n=int(number)
                chapters.append({"at":second, "label":str(second//60)+":"+str(second%60).zfill(2)+" · "+SOUTH_STEPS[n-1][0]})
            source = item["timestamp_evidence"]["source_url"]
            spoiler = True
            provenance = "Riferimenti al filmato PowerPyx documentati nella mappa della fonte; riproduzione non verificata indipendentemente."
        else:
            item = refs.get(key)
            if not isinstance(item, dict):
                raise ValueError("Missing original external video record: "+key)
            video_id = item.get("youtube_id")
            creator = item.get("creator")
            chapters = item.get("chapters")
            source = item.get("context_source")
            spoiler = item.get("spoiler")
            provenance = item.get("why")
        if (not isinstance(video_id,str) or
                not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id) or video_id in videos):
            raise ValueError("Duplicate or invalid publisher video reference")
        videos.add(video_id)
        if (not isinstance(creator,str) or not 2<=len(creator)<=120 or
                not isinstance(provenance,str) or len(provenance)<25 or
                not isinstance(source,str) or not source.startswith("https://")):
            raise ValueError("Incomplete sourced creator credit")
        if type(spoiler) is not bool or not isinstance(chapters,list) or not 1<=len(chapters)<=12:
            raise ValueError("Missing spoiler classification or reliable chapters")
        stamps = []
        for chapter in chapters:
            at = chapter.get("at")
            label = chapter.get("label")
            if (type(at) is not int or not 0<=at<=21600 or at in stamps or
                    not isinstance(label,str) or not 5<=len(label)<=120 or
                    "<" in label or ">" in label):
                raise ValueError("Unreviewed video moment")
            stamps.append(at)
        if not (Path("data/visual_guides.json").exists() and
                (Path("_site") / guide_path / "index.html").is_file()):
            # The actual guide must exist in the completed static build.
            raise ValueError("Curated creator video has no real local guide")
        result.append(dict(key=key, category=category, title=title, detail=detail,
                           guide_path=guide_path, video_id=video_id, creator=creator,
                           source=source, spoiler=spoiler, chapters=chapters,
                           provenance=provenance))
    return result


def render(items):
    if len(items)!=len(CURATED) or {item["key"] for item in items}!=IDS:
        raise ValueError("Incomplete reviewed video selection")
    out = [
        '<section class="cv-intro" aria-labelledby="cv-title">'
        '<span class="v-tag">CREATOR SHOWCASE · SELEZIONE INDIPENDENTE</span>'
        '<h1 id="cv-title">Video tutorial GTA VI: guarda i creator, segui la guida italiana</h1>'
        '<p>Il filmato originale mostra il percorso; GTA VI Italia riassume in italiano '
        'le azioni, i prerequisiti e i controlli. Scegli il video che ti serve.</p>'
        '<p class="cv-ethics">Questa è una selezione editoriale, <strong>non una partnership '
        'o sponsorizzazione pagata</strong>. Nessun video o fotogramma è copiato sul sito. '
        'L’incorporamento ufficiale YouTube si attiva solo quando premi Guarda. '
        'La riproduzione e i singoli fotogrammi non sono verificati indipendentemente: '
        'disponibilità e restrizioni possono variare.</p>'
        '</section>',
        '<nav class="cv-filter" aria-label="Filtra video per obiettivo" data-cv-filters>'
        '<button type="button" data-cv-filter="all" aria-pressed="true">Tutti · '+str(len(items))+'</button>'
        + ''.join('<button type="button" data-cv-filter="'+kind+
                  '" aria-pressed="false">'+escape(text)+' · '+str(sum(item["category"]==kind for item in items))+'</button>'
                  for kind,text in KINDS.items())+'</nav>',
        '<section class="cv-grid" aria-label="Video originali selezionati" data-cv-grid>',
    ]
    for item in items:
        ident = escape(item["video_id"],quote=True)
        creator = escape(item["creator"])
        title = escape(item["title"])
        category = escape(item["category"],quote=True)
        guide = BASE + item["guide_path"]
        stamp = item["chapters"][0]["at"]
        original = "https://www.youtube.com/watch?v="+ident+"&t="+str(stamp)+"s"
        chapters = ''.join(
            '<li><button type="button" class="cv-chapter" data-cv-seek="'+str(ch["at"])+
            '" aria-label="Vai al minuto '+escape(ch["label"],quote=True)+'">'
            +escape(ch["label"])+'</button></li>'
            for ch in item["chapters"])
        out.append(
            '<article class="cv-card" id="video-'+escape(item["key"],quote=True)+'" data-cv-category="'+category+'" '
            'data-cv-video-id="'+ident+'" data-cv-start="'+str(stamp)+'">'
            '<div class="cv-poster" aria-label="Player YouTube esterno non ancora caricato">'
            '<span class="cv-poster-badge">VIDEO ORIGINALE · '+creator+'</span>'
            '<span class="cv-big-play" aria-hidden="true">▶</span>'
            '<button type="button" class="cv-load" data-cv-load hidden>'
            '▶ Guarda il filmato di '+creator+'</button>'
            '<div class="cv-embed-slot" data-cv-slot></div>'
            '</div>'
            '<div class="cv-content">'
            '<span class="cv-kind">'+escape(KINDS[item["category"]])+
            (' · Attenzione spoiler' if item["spoiler"] else ' · Community')+'</span>'
            '<h2>'+title+'</h2><p>'+escape(item["detail"])+'</p>'
            '<div class="cv-chapters"><h3>Vai al punto utile</h3><ul>'+chapters+'</ul></div>'
            '<p class="cv-credit"><strong>Creator:</strong> '+creator+'. '
            +escape(item["provenance"])+'</p>'
            '<p class="cv-links"><a href="'+escape(guide,quote=True)+
            '">Segui la guida passo per passo →</a>'
            '<a href="'+escape(original,quote=True)+
            '" target="_blank" rel="noopener noreferrer">Video originale su YouTube ↗</a>'
            '<a href="'+escape(item["source"],quote=True)+
            '" target="_blank" rel="noopener noreferrer">Fonte della verifica ↗</a></p>'
            '</div></article>'
        )
    out.append('</section><p class="cv-empty" data-cv-empty hidden>Nessun video in questa categoria.</p>'
               '<section class="cv-policy" aria-labelledby="cv-policy-title">'
               '<h2 id="cv-policy-title">Come scegliamo i creator</h2>'
               '<p>Ogni filmato deve avere un link pubblico, un autore identificabile, '
               'un momento utile collegabile a una guida verificata e un’attribuzione chiara. '
               'I video sono di terzi, non una prova che il nostro team abbia ripetuto '
               'la procedura. Se il creator disattiva l’embed, apri il video direttamente '
               'su YouTube. Le collaborazioni saranno dichiarate soltanto quando reali.</p>'
               '<p>Hai un filmato utile? <a href="https://x.com/xFederiko11" '
               'target="_blank" rel="noopener noreferrer">Segnalalo a GTA VI Italia su X ↗</a>. '
               'Valutiamo i contenuti senza promettere pubblicazione o remunerazione.</p>'
               '</section>')
    return ''.join(out)
