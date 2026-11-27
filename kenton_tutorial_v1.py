"""Original Italian, linear Kenton trophy walkthrough with source-only visual references."""
from html import escape

SETS = "https://www.powerpyx.com/gta-6-all-kenton-sets-locations-search-the-dive-sites/"
CHECK = "https://www.powerpyx.com/gta-6-check-in-with-kenton-walkthrough/"
FINAL = "https://www.powerpyx.com/gta-6-maritime-dispute-stop-by-kentons-shop-walkthrough/"
DIVES = "https://www.pushsquare.com/guides/gta-6-underwater-discoveries-locations-and-kentons-treasures"
PERCENT = "https://www.powerpyx.com/gta-6-100-completion-checklist-guide/"

STEPS = (
    ("Sblocca le immersioni", "Con Jason completa Island Dreams nel Capitolo 1. Aspetta le indicazioni di Kenton a Key Lento.", "Compaiono i forzieri viola sulla mappa.", SETS),
    ("Completa tre siti", "Usa una barca con attrezzatura subacquea. Cerca i reperti sul fondale con il metal detector; completa ogni gruppo indicato.", "Il contatore del singolo sito mostra tutti i reperti richiesti.", SETS),
    ("Consegna i reperti", "Rientra al negozio di Kenton e vendi i tesori raccolti.", "Dopo le consegne ricevi l'invito a tornare.", SETS),
    ("Fai visita a Kenton", "Torna al negozio quando compare Check in with Kenton.", "La scena si conclude; in seguito Kenton comunica nuove immersioni.", CHECK),
    ("Aspetta Maritime Dispute", "Prosegui nella storia fino al Capitolo 3 e aspetta che Kenton ricontatti Jason. Raggiungi il negozio.", "L'incarico finale diventa disponibile; l'assenza temporanea nel Capitolo 2 non richiede un nuovo salvataggio.", FINAL),
    ("Raggiungi il cargo", "Segui la destinazione a Gambit Bay. Individua la nave e sali dalla scaletta.", "Sei a bordo e si avvia la scena successiva.", FINAL),
    ("Recupera le casse", "Indossa la muta. Segui i segnali del metal detector verso l'aereo sommerso e collega i palloni alle casse contrassegnate.", "Gli obiettivi di recupero si aggiornano e la missione prosegue.", FINAL),
    ("Torna sulla nave", "Raggiungi di nuovo il cargo e risali attraverso l'apertura sul fianco.", "L'obiettivo ti indirizza alla stiva D.", FINAL),
    ("Raggiungi Kenton", "Segui il percorso praticabile fino alla porta segnata D e salva Kenton.", "Kenton si muove verso l'uscita.", FINAL),
    ("Concludi la missione", "Segui Kenton fuori dalla nave e nuota in superficie tenendo premuto X quando richiesto.", "Verifica il completamento e il trofeo Bronzo sulla PS5.", FINAL),
)


def link(target, label):
    return '<a href="'+escape(target, quote=True)+'" target="_blank" rel="noopener noreferrer">'+escape(label)+'</a>'


def render():
    rows = [
        '<div class="tg-guidance" id="kenton-tutorial" data-kenton-tutorial>',
        '<strong>COME FARLO · CONSIGLIO DOCUMENTATO</strong>',
        '<p><b>Quando:</b> Jason dal Capitolo 1, finale dal Capitolo 3. <b>Dove:</b> negozio di Kenton, Key Lento. <b>Premio:</b> trofeo Bronzo.</p>',
        '<p>⚠️ Spoiler della missione finale. Procedura ricostruita da guide indipendenti, non da una nostra prova in gioco.</p>',
        '<ol class="kenton-steps">',
    ]
    for n, (title, action, check, source) in enumerate(STEPS, 1):
        rows.append('<li data-kenton-step="'+str(n)+'"><h3>'+escape(title)+'</h3><p>'+escape(action)+'</p>'
                    '<p><b>Controllo:</b> '+escape(check)+'</p><p>'+link(source,"Guarda la fonte originale con le immagini ↗")+'</p></li>')
    rows.extend([
        '</ol>',
        '<p><b>Tre obiettivi distinti:</b> il trofeo richiede Maritime Dispute; per il 100%, la checklist PowerPyx richiede 5 set di Kenton su 7, oltre alle 33 scoperte subacquee. Le fonti non concordano su quali siti alimentino entrambi i contatori: controllali separatamente in gioco.</p>',
        '<p>'+link(PERCENT,"Checklist 100% PowerPyx ↗")+' · '+link(DIVES,"Guida immersioni Push Square ↗")+'</p>',
        '<p><a href="https://xfederiko11.github.io/gta-6/collezionabili/percorsi/">Apri i percorsi subacquei già documentati →</a></p>',
        '<p><small>Le schermate sono consultabili presso gli autori originali. Nessuna fotografia del gameplay è stata ripubblicata in questi passaggi.</small></p></div>',
    ])
    return "".join(rows)
