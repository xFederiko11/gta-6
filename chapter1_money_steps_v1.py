"""Action-first Chapter 1 loot reference, grounded in original source headings.

Not an infinite-money method. A referenced location or editorial photograph
never proves exact loot, game version, resale price, or a safe trophy status.
"""
from html import escape

GUIDE_ID="soldi-facili-capitolo-1"
ACTIONS=(
    ("Durante l'incarico di Shirley raggiungi Three Sheets Liquor, a Key Lento.",
     "Controlla il retro del negozio solo dopo aver valutato guardie e accessi.",
     "Ispeziona nascondigli e oggetti; verifica nell'inventario cosa hai raccolto."),
    ("Raggiungi il Manatee Motel a sud-ovest di Hamlet, sopra Shoeless Keys.",
     "Prima di entrare considera gli incontri segnalati con una tigre e membri della gang.",
     "Esplora la zona segnalata e controlla il bottino effettivamente ottenuto."),
    ("Prendi una barca e raggiungi la casa su palafitte a nord-est di Corsair Key.",
     "Cerca una tavola mobile: la fonte suggerisce L3 + R3 per individuarla.",
     "Controlla il contenuto del nascondiglio e verifica le risorse ottenute."),
    ("Raggiungi il magazzino South Vice-Dale a nord-est di Hamlet.",
     "Controlla l'ufficio laterale per la carta da baseball segnalata.",
     "Verifica l'oggetto nell'inventario: 6.000 GTA$ è una stima, non contanti accreditati.")
)
SOURCE="https://insider-gaming.com/gta-6-early-game-locations-make-money/"

def validate(g):
    if g.get("id")!=GUIDE_ID or len(g.get("steps",[]))!=4 or len(g.get("checks",[]))!=4:
        raise ValueError("Four sourced money locations and completion checks required")
    if len(ACTIONS)!=4 or any(len(group)!=3 or any(not 20<=len(part)<=170 for part in group) for group in ACTIONS):
        raise ValueError("Three concise one-action instructions required per location")
    if g.get("source_url")!=SOURCE or "Family Savings" not in g.get("benefit",""):
        raise ValueError("Wrong source or absent Chapter 1 cash-safety warning")
    if "Recalibration" not in g.get("caution","") or "Tourist Trap" not in g.get("caution",""):
        raise ValueError("Point of no return is missing")
    return True

def render(index):
    if not isinstance(index,int) or not 0<=index<4:
        raise ValueError("Unknown Chapter 1 money step")
    return ('<div class="cash-microsteps" aria-label="Azioni pratiche per questo luogo">'
            '<strong class="cash-actions-caption">COSA FARE QUI</strong>'
            +''.join('<p class="cash-microstep"><span aria-hidden="true">'
                     +str(n)+'</span>'+escape(text)+'</p>'
                     for n,text in enumerate(ACTIONS[index],1))
            +'</div>')
