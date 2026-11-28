"""Chapter navigation from explicit, already documented guide prerequisites.

This is a reading route, not a guess at the earliest possible unlock. Guides
with a disputed final unlock remain outside the numbered chapter groups.
"""
from html import escape

from garage_guides_v1 import STORY, STORY_ROWS, VANESSA


# Labels distinguish the first available activity from completion of a chain.
CHAPTER_ROUTES = (
    (1, (
        ("guide-e-tutorial/soldi-facili-capitolo-1/", "Bottini e denaro iniziale", "Prima del passaggio al Capitolo 2."),
        ("guide-e-tutorial/viaggio-rapido-taxi/", "Viaggio rapido in taxi", "Dopo Gone Fishing."),
        ("guide-e-tutorial/meditazione-capitolo-1/", "Prima meditazione", "Prima occasione a casa di Jason; il percorso prosegue nei capitoli successivi."),
    )),
    (2, (
        ("salvare-auto/", "Prima auto personale", "Dopo Girl’s Trip, da Moses a Watkins Auto Parts."),
        ("guide-e-tutorial/veicoli-per-moses/", "Le sei consegne di Moses", "Dopo Daily Driver; ogni consegna apre la successiva."),
    ) + tuple((STORY + ident + "/", name + " Garage", "Dopo " + mission + ".")
              for ident, name, chapter, mission, _, _ in STORY_ROWS if chapter == "2")),
    (3, (
        ("guide-e-tutorial/key-cloner/", "Key Cloner", "Dopo Crosstown Traffic: completa Clonin’ Keys, Makin’ GS."),
        ("guide-e-tutorial/sportive-randy-posizioni/", "Inizia Randy’s Wish List", "Dopo Clonin’ Keys, Makin’ Gs; le ricompense finali richiedono altri incarichi."),
        (VANESSA, "Del Rio Boulevard e Growler rosa", "Recuperala prima di The Cartel Heist: possibile contenuto mancabile."),
    )),
) + tuple((number, tuple((STORY + ident + "/", name + " Garage", "Dopo " + mission + ".")
                        for ident, name, chapter, mission, _, _ in STORY_ROWS if chapter == str(number)))
          for number in (4, 5))

UNCERTAIN_ROUTES = (
    ("garage-gratuiti/southside-storage/", "Southside Storage e cinque murales", "Capitolo minimo non documentato."),
    ("garage-gratuiti/domestic-timbers/", "Domestic Timbers e Tempesta", "La catena di Randy parte nel Capitolo 3; il capitolo del ritiro finale non è accertato."),
    ("guide-e-tutorial/vendere-veicoli/", "Vendita di auto con tracker avanzato", "Le fonti divergono sul capitolo di Dale Mamba: verifica la notifica di sblocco."),
)


def _links(rows, url):
    return '<ul>' + ''.join(
        '<li><a href="' + escape(url(path), quote=True) + '">' + escape(label) +
        '</a><p>' + escape(requirement) + '</p></li>'
        for path, label, requirement in rows) + '</ul>'


def render(url):
    body = ('<section class="v-chapter-routes" id="guide-per-capitolo" aria-labelledby="chapter-routes-title">'
            '<h2 id="chapter-routes-title">Guide per capitolo</h2>'
            '<p>Scegli il capitolo e controlla la missione richiesta. Ogni voce rimanda alle istruzioni '
            'e alle fonti della guida; iniziare un’attività non significa averne già sbloccato tutte le ricompense.</p>'
            '<div class="v-chapter-grid">')
    for chapter, rows in CHAPTER_ROUTES:
        body += ('<details data-guide-chapter="' + str(chapter) + '"><summary>Capitolo ' +
                 str(chapter) + ' <span>' + str(len(rows)) + (' guida' if len(rows) == 1 else ' guide') + '</span></summary>' +
                 _links(rows, url) + '</details>')
    body += ('<details data-guide-chapter="uncertain"><summary>Capitolo da verificare <span>3 percorsi</span></summary>' +
             _links(UNCERTAIN_ROUTES, url) + '</details></div></section>')
    return body
