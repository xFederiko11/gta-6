"""Article-specific illustrations: original diagrams, never a recreated game UI."""
from html import escape

VIDEO_ID="0RBe_fz67gs"
CREATOR="Games & Apps Tutorials"
SOURCE="https://www.powerpyx.com/gta-6-how-to-study-animals-scan-vehicles/"
SCREEN_SOURCE="https://allthings.how/gta-6-waink-app-explained-how-to-open-scan-locations/"
BASE="https://xfederiko11.github.io/gta-6/assets/waink-guide/"
ALTS=(
    "Schema della croce direzionale: tieni premuto il tasto su.",
    "Schema concettuale: inquadra un veicolo, una barca o un velivolo.",
    "Schema del comando R1: tienilo premuto durante la scansione.",
    "Confronto dei tracker No Tracker, Standard e Advanced; non interfaccia del gioco.",
    "Percorso Progressi, Veicoli e obiettivo 200 modelli base su 277.",
)


def intro():
    return (
        '<section class="waink-video-intro" aria-label="Video tutorial WAiNK">'
        '<div class="v-step-video waink-main-player" data-step-video-id="'+VIDEO_ID+'" data-step-video-seconds="0">'
        '<button type="button" class="v-step-video-open" data-step-video-open hidden aria-label="Apri il video tutorial WAiNK">'
        '<span class="v-step-video-play" aria-hidden="true">▶</span>'
        '<span><strong>Video tutorial · come usare WAiNK</strong>'
        '<small>'+CREATOR+' · player originale YouTube</small></span></button>'
        '<div class="v-step-video-slot" data-step-video-slot aria-live="polite"></div>'
        '<p class="v-step-video-note">Guida esterna dedicata allo scanner. '
        '<a href="https://www.youtube.com/watch?v='+VIDEO_ID+'" target="_blank" rel="noopener noreferrer">Apri il video originale ↗</a>'
        ' · <a href="'+SCREEN_SOURCE+'" target="_blank" rel="noopener noreferrer">Schermate reali WAiNK ↗</a></p>'
        '</div><a class="waink-start" href="#procedura">Vai ai 5 passaggi illustrati ↓</a></section>'
    )


def step(index):
    if type(index) is not int or not 0<=index<len(ALTS):
        raise ValueError("Invalid WAiNK illustration")
    n=index+1
    image=BASE+"step-"+str(n)+".svg"
    # Explicitly label the illustrations as diagrams, not gameplay photos.
    # The external page has genuine UI reference screenshots; no copied bytes.
    out=('<figure class="waink-instruction-art" data-waink-diagram="'+str(n)+'">'
         '<img data-visual-kind="editorial-diagram" data-waink-illustration="'+str(n)+'" src="'+image+'" alt="'+escape(ALTS[index],quote=True)+'" width="640" height="220" '
         'decoding="async"'+('' if index==0 else ' loading="lazy"')+'>'
         '<figcaption>Schema originale GTA VI Italia · non screenshot · '
         '<a href="'+SOURCE+'" target="_blank" rel="noopener noreferrer">Fonte comandi ↗</a>')
    if index in (0,2):
        out+=' · <a href="'+SCREEN_SOURCE+'" target="_blank" rel="noopener noreferrer">Vedi schermata reale dello scanner ↗</a>'
    return out+'</figcaption></figure>'
