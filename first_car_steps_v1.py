"""Seven concise player actions for the first car registration tutorial.

Based on the documented Moses, Scooter Bros, and garage walkthroughs.
These short microactions support the canonical guide JSON; they never create
new map coordinates, copy editorial screenshots, or introduce paid services.
"""
from html import escape

GUIDE_ID="registrare-auto-personale"
ACTIONS=(
    ("Apri la mappa dopo Girl’s Trip e cerca il marcatore MW a Port Gellhorn.",
     "Raggiungi Watkins Auto Parts con Lucia e avvia Moses.",
     "Se hai già un'auto senza tracker, portala direttamente in officina."),
    ("Segui Moses nel cortile dove ci sono tre veicoli.",
     "Tieni premuto ↑ sulla croce direzionale per aprire WAiNK.",
     "Inquadra una vettura e tieni premuto R1: leggi No Tracker, Standard o Advanced."),
    ("Raccogli lo Slim Jim vicino a Moses.",
     "Avvicinati alla Montagne XL e premi △ (Triangolo).",
     "Inclina la levetta destra finché la barra diventa rosa: evita l'allarme."),
    ("Se hai già portato un'auto senza tracker, salta questa ricerca.",
     "Altrimenti raggiungi la strada principale al centro di Port Gellhorn.",
     "Scansiona le auto con WAiNK, scegli No Tracker e riportala da Moses."),
    ("Entra nell'officina di Moses con l'auto che ha superato il controllo tracker.",
     "Apri Respray e scegli un colore diverso da quello iniziale.",
     "Conferma la riverniciatura, poi torna al menu dell'officina."),
    ("Nel menu dell'officina premi Register dopo Respray.",
     "Conferma la registrazione gratuita della prima auto per Lucia.",
     "Controlla l'avviso di veicolo personale: non basta parcheggiarla."),
    ("Dopo aver completato Moses, apri il telefono con ↑ sulla croce direzionale.",
     "Apri l'app Scooter Bros (icona verde con automobile).",
     "Seleziona il veicolo, premi Request e controlla la tariffa prima della conferma.")
)
CHECKS=(
    "MW e Moses disponibili dopo Girl’s Trip",
    "Scanner con tipo tracker visibile",
    "Slim Jim usato senza allarme",
    "Moses accetta l'auto No Tracker",
    "Respray completato e menu Register disponibile",
    "Prima auto riconosciuta come personale",
    "Scooter Bros mostra la vettura e la tariffa"
)
SOURCE_URLS=(
    "https://www.powerpyx.com/gta-6-moses-take-a-vehicle-to-moses-walkthrough/",
    "https://www.powerpyx.com/gta-6-how-to-summon-vehicles/",
    "https://www.gtabase.com/gta-6/articles/how-to-unlock-garages-in-gta-6",
)

def validate(g):
    if g.get("id")!=GUIDE_ID or len(g["steps"])!=7 or len(g["checks"])!=7:
        raise ValueError("Seven sourced first-car stages required")
    if len(ACTIONS)!=7 or len(CHECKS)!=7:
        raise ValueError("Seven action sequences and checks required")
    if any(not 2<=len(steps)<=4 or any(not 12<=len(line)<=190 for line in steps)
           for steps in ACTIONS):
        raise ValueError("Missing clear one-action-at-a-time instructions")
    if "Scooter Bros" not in g["steps"][6] or "Daily Driver" not in g["benefit"]:
        raise ValueError("Vehicle app and garage unlocks must remain distinct")
    return True

def render(index):
    if not isinstance(index,int) or index not in range(7):
        raise ValueError("Unknown first-car step")
    return ('<div class="car-microsteps" aria-label="Azioni pratiche del passaggio">'
            '<strong class="car-actions-caption">AZIONI DA ESEGUIRE</strong>'
            +''.join('<p class="car-microstep"><span aria-hidden="true">'
                     +str(n)+'</span>'+escape(action)+'</p>'
                     for n,action in enumerate(ACTIONS[index],1))
            +'</div>')
