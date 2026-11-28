"""Bret: original Italian walkthrough, source references, no guessed trophy trigger."""
from html import escape

INTRO = "https://www.powerpyx.com/gta-6-veteran-hunted-meet-bret-walkthrough/"
ROADMAP = "https://www.powerpyx.com/gta-6-grand-theft-auto-vi-trophy-guide-roadmap/"
DECKS = "https://www.pushsquare.com/guides/gta-6-brets-hunting-target-deck-locations"
CONTACTS = "https://www.powerpyx.com/gta-6-all-contacts/"
HUNTS = "https://www.powerpyx.com/gta-6-all-brets-target-decks-locations-brets-hunts/"

STEPS = (
    ("Sblocca Bret", "Usa Jason dopo Coffee Break, nel Capitolo 2. Aspetta il suo messaggio e raggiungi il punto della missione Veteran Hunted in Lummox County, senza Lucia.", "Bret ti accoglie presso il rifugio.", INTRO),
    ("Raggiungi la zona di caccia", "Sali sul pick-up di Bret e segui il segnaposto. Ricevi il fucile da caccia della missione.", "L'obiettivo cambia quando arrivi nella zona indicata.", INTRO),
    ("Studia il cervo", "Attiva Focus con L3 + R3 per seguire la traccia; usa binocolo o mirino e tieni premuto R1 per registrare l'animale.", "La specie compare nel catalogo se non era già registrata.", INTRO),
    ("Completa Veteran Hunted", "Segui l'obiettivo di caccia della missione e carica il cervo sul pick-up. Riporta il mezzo al rifugio e consegna l'animale nell'area indicata.", "La missione è conclusa e si sbloccano gli incarichi successivi.", INTRO),
    ("Apri i Target Decks", "Gioca da solo con Jason dopo Veteran Hunted e attendi il messaggio di Bret. Per il primo incarico cerca una White Tail Doe e un White Tail Buck ad Abandoned Concrete Plant, Kalaga River oppure Mount Kalaga Park. Usa il Killtelligence SM-69 ricevuto nella missione.", "Il messaggio richiede entrambi gli animali; le tre aree sono alternative, non tre consegne obbligatorie.", HUNTS),
    ("Consegna le prede in buone condizioni", "Studia il bersaglio per leggere l’arma consigliata e mira ai punti rossi visibili in Focus. PowerPyx richiede carcasse Good o Pristine. Carica le prede trasportabili sul veicolo e portane una nel negozio: la fonte indica che vengono consegnate insieme. Per animali troppo grandi, come cinghiali e coccodrilli, usa il prompt per inviare la foto a Bret e attendi il ritiro.", "Verifica che l’incarico avanzi prima di partire per il prossimo. Denaro e condizioni variano: non assumere un ricavo fisso.", HUNTS),
    ("Controlla il trofeo", "Prosegui con i Target Decks e controlla l'elenco trofei PS5. Per il 100% sono necessari tutti i 15 incarichi.", "Segna il trofeo solo quando compare come ottenuto: le fonti non confermano quale singolo animale lo faccia scattare.", ROADMAP),
)

# Selected practical checkpoints, not a claim that all 15 decks are documented.
HUNT_CHECKPOINTS = (
    (1, "Adrenal Glands and Venison", "White Tail Doe + White Tail Buck", "Abandoned Concrete Plant, Kalaga River o Mount Kalaga Park.", "Killtelligence SM-69; il primo incarico dà anche il Wartham W-22."),
    (7, "White Fur and Feathers", "Northern Albino Raccoon + Canada Goose + North American White River Otter", "Segui le zone del messaggio; il procione compare di notte secondo la fonte, dopo le 19:30.", "Wartham W-22. Controlla la variante albina: il procione normale non la sostituisce."),
    (8, "Boar Meat and Bear Meat", "Gloriana Opossum + Spotted Wild Boar + American Black Bear", "Nelle aree indicate da Bret; l’opossum compare di notte secondo la fonte.", "W-22 per l’opossum, SM-69 per cinghiale e orso; invia la foto delle prede grandi per il ritiro."),
    (13, "Snapmatic Panther", "Unique Panther", "Belpoint Island, a ovest di Capri: raggiungila in barca o elicottero e cerca lungo la strada centrale.", "SM-69; mantieni la distanza e invia la foto a Bret per il ritiro."),
    (14, "Snapmatic Coyote", "Unique Coyote", "A nord di Belville, nei campi oltre le grandi case; cerca tracce presso il fosso a est del campo.", "Hawk & Little Mediator; questa preda va portata al negozio di Bret."),
)


def hunt_checkpoints():
    rows = ['<details class="tg-deep" id="bret-target-decks"><summary>Target Decks: luoghi e controlli utili</summary>',
            '<p>La guida PowerPyx del 27 novembre documenta gli incarichi da 1 a 14 su 15: il quindicesimo è ancora in aggiornamento. Qui trovi cinque tappe pratiche; per tutti i bersagli e le mappe apri la fonte originale. Nessun punto di spawn garantito.</p>',
            '<ol class="tg-linear-steps">']
    for number, name, animals, where, action in HUNT_CHECKPOINTS:
        rows.append('<li data-bret-deck="' + str(number) + '"><h3>Deck ' + str(number) + ' · ' + escape(name) + '</h3><p><b>Bersagli:</b> ' + escape(animals) + '</p><p><b>Dove:</b> ' + escape(where) + '</p><p>' + escape(action) + '</p></li>')
    rows += ['</ol><p>Le varianti di colore e le specie precise contano: non sostituirle con animali simili. Se Bret non scrive, PowerPyx suggerisce di salvare e ricaricare mentre giochi da solo con Jason; è un tentativo di recupero, non una soluzione garantita.</p>',
             '<p>' + link(HUNTS, "PowerPyx — 14 Target Decks, immagini e posizioni originali ↗") + '</p></details>']
    return ''.join(rows)

def link(target,label):
    return '<a href="'+escape(target,quote=True)+'" target="_blank" rel="noopener noreferrer">'+escape(label)+'</a>'


def render():
    rows=['<div class="tg-guidance" id="bret-tutorial" data-bret-tutorial>',
          '<strong>COME FARLO · CONSIGLIO DOCUMENTATO</strong>',
          '<p><b>Quando:</b> Capitolo 2, dopo Coffee Break. <b>Chi:</b> solo Jason. <b>Dove:</b> Lummox County, segnaposto Veteran Hunted. <b>Premio:</b> trofeo Bronzo; il primo incarico dà anche 500 GTA$ e il fucile unico secondo PowerPyx.</p>',
          '<p>⚠️ Spoiler delle attività di Bret. Il requisito esatto del singolo animale resta da confermare; non abbiamo eseguito una prova in gioco.</p>',
          '<ol class="tg-linear-steps">']
    for n,(title,action,check,source) in enumerate(STEPS,1):
        rows.append('<li data-bret-step="'+str(n)+'"><h3>'+escape(title)+'</h3><p>'+escape(action)+'</p><p><b>Controllo:</b> '+escape(check)+'</p><p>'+link(source,"Apri la fonte originale con le immagini ↗")+'</p></li>')
    rows.extend(['</ol>',
                 hunt_checkpoints(),
                 '<p><b>Non confondere i contatori:</b> studiare 100 specie e terminare 15 Target Decks sono requisiti distinti. La fonte PowerPyx documenta 14 incarichi al controllo del 28 novembre 2026; non certifica il singolo trigger del trofeo. Anche l’elenco Push Square resta in aggiornamento.</p>',
                 '<p>'+link(CONTACTS,"Contatti e incarichi PowerPyx ↗")+' · '+link(DECKS,"Bersagli e luoghi Push Square ↗")+'</p>',
                 '<p><a href="https://xfederiko11.github.io/gta-6/guide-e-tutorial/studiare-animali/">Come registrare le specie senza cacciare →</a> · <a href="https://xfederiko11.github.io/gta-6/guide-e-tutorial/viaggio-rapido-taxi/#consigli">Come cambiare orario nel gioco →</a></p>',
                 '<p><small>Le immagini restano presso i rispettivi autori: nessuna schermata ripubblicata.</small></p></div>'])
    return "".join(rows)
