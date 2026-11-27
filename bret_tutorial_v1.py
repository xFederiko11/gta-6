"""Bret: original Italian walkthrough, source references, no guessed trophy trigger."""
from html import escape

INTRO = "https://www.powerpyx.com/gta-6-veteran-hunted-meet-bret-walkthrough/"
ROADMAP = "https://www.powerpyx.com/gta-6-grand-theft-auto-vi-trophy-guide-roadmap/"
DECKS = "https://www.pushsquare.com/guides/gta-6-brets-hunting-target-deck-locations"
CONTACTS = "https://www.powerpyx.com/gta-6-all-contacts/"

STEPS = (
    ("Sblocca Bret", "Usa Jason dopo Coffee Break, nel Capitolo 2. Aspetta il suo messaggio e raggiungi il punto della missione Veteran Hunted in Lummox County, senza Lucia.", "Bret ti accoglie presso il rifugio.", INTRO),
    ("Raggiungi la zona di caccia", "Sali sul pick-up di Bret e segui il segnaposto. Ricevi il fucile da caccia della missione.", "L'obiettivo cambia quando arrivi nella zona indicata.", INTRO),
    ("Studia il cervo", "Attiva Focus con L3 + R3 per seguire la traccia; usa binocolo o mirino e tieni premuto R1 per registrare l'animale.", "La specie compare nel catalogo se non era già registrata.", INTRO),
    ("Completa Veteran Hunted", "Segui l'obiettivo di caccia della missione e carica il cervo sul pick-up. Riporta il mezzo al rifugio e consegna l'animale nell'area indicata.", "La missione è conclusa e si sbloccano gli incarichi successivi.", INTRO),
    ("Apri i Target Decks", "Seleziona gli incarichi di Bret nelle attività della mappa. Usa il personaggio Jason e leggi ogni messaggio per riconoscere le specie richieste.", "I bersagli della richiesta attiva risultano indicati sulla mappa.", DECKS),
    ("Completa le richieste", "Raggiungi i luoghi indicati, consegna le prede nella condizione richiesta e attendi il prossimo messaggio di Bret.", "Il contatore degli incarichi completati aumenta.", DECKS),
    ("Controlla il trofeo", "Prosegui con i Target Decks e controlla l'elenco trofei PS5. Per il 100% sono necessari tutti i 15 incarichi.", "Segna il trofeo solo quando compare come ottenuto: le fonti non confermano quale singolo animale lo faccia scattare.", ROADMAP),
)

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
                 '<p><b>Non confondere i contatori:</b> studiare 100 specie e terminare 15 Target Decks sono requisiti distinti. Push Square documenta i primi incarichi ma il suo elenco è ancora in aggiornamento.</p>',
                 '<p>'+link(CONTACTS,"Contatti e incarichi PowerPyx ↗")+' · '+link(DECKS,"Bersagli e luoghi Push Square ↗")+'</p>',
                 '<p><a href="https://xfederiko11.github.io/gta-6/guide-e-tutorial/studiare-animali/">Come registrare le specie senza cacciare →</a> · <a href="https://xfederiko11.github.io/gta-6/guide-e-tutorial/viaggio-rapido-taxi/#consigli">Come cambiare orario nel gioco →</a></p>',
                 '<p><small>Le immagini restano presso i rispettivi autori: nessuna schermata ripubblicata.</small></p></div>'])
    return "".join(rows)
