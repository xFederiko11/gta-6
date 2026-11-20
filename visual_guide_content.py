"""Presentation-only enrichment of sourced guides; never invent gameplay steps."""
from copy import deepcopy

SAFE_TITLES = {
    'soldi-facili-capitolo-1': 'Soldi subito: 4 luoghi da controllare',
    'soldi-2500-three-sheets-liquor': 'Denaro nascosto nel negozio: il percorso',
    'scansionare-veicoli': 'Scansionare i veicoli con WAiNK',
    'studiare-animali': 'Studiare gli animali senza cacciarli',
    '70-sfide-100-percento': 'Le sfide da scegliere per il 100%',
    'meditazione-capitolo-1': '18 meditazioni GTA VI: checklist e platino',
    'viaggio-rapido-taxi': 'Viaggiare più in fretta con il taxi',
    'poligoni-concentrazione': 'Poligoni: allenamento e medaglie Oro',
    'registrare-auto-personale': 'Come salvare un’auto e ritrovarla',
    'sportive-randy-posizioni': 'Sportive ricercate: dove cercarle',
    'prima-persona-glitch-ps5': 'Glitch prima persona GTA VI: come attivarlo',
}
HERO = {
    'soldi-facili-capitolo-1': 'bank-deposit',
    'soldi-2500-three-sheets-liquor': 'bank-phone',
    'scansionare-veicoli': 'traffic',
    'studiare-animali': 'leonida',
    '70-sfide-100-percento': 'vice-city',
    'meditazione-capitolo-1': 'leonida',
    'viaggio-rapido-taxi': 'taxi-phone',
    'poligoni-concentrazione': 'vice-city',
    'registrare-auto-personale': 'save-car',
    'sportive-randy-posizioni': 'register-car',
    'prima-persona-glitch-ps5': 'traffic',
}
STEP_MEDIA = {
    'soldi-2500-three-sheets-liquor': {0:'shirley-house',1:'liquor-store'},
    'soldi-facili-capitolo-1': {0:'liquor-store'},
    'registrare-auto-personale': {0:'save-car',4:'register-car',6:'scooter-menu'},
    'viaggio-rapido-taxi': {0:'taxi-phone',1:'taxi-ride'},
}
HEADINGS = {
    'soldi-facili-capitolo-1': ['Il retro del negozio','Il motel da esplorare','La casa sull’acqua','L’oggetto di valore nel magazzino'],
    'soldi-2500-three-sheets-liquor': ['Parti dall’incarico giusto','Raggiungi il retro','Individua il riferimento','Controlla il nascondiglio','Completa l’esplorazione'],
    'registrare-auto-personale': ['Raggiungi l’officina','Controlla la registrazione','Verifica lo spazio disponibile','Richiama il mezzo dal telefono'],
    'sportive-randy-posizioni': ['Apri la lista delle richieste','Restringi la zona di ricerca','Identifica il veicolo','Decidi se consegnarlo o conservarlo'],
    'prima-persona-glitch-ps5': ['Proteggi prima i tuoi progressi','Imposta Camera sul touchpad','Entra nell’auto','Apri il telefono','Chiudi e premi il touchpad','Conferma l’effetto e torna alla visuale normale'],
    'scansionare-veicoli': ['Apri WAiNK','Inquadra il veicolo','Completa la scansione'],
    'studiare-animali': ['Seleziona il binocolo','Avvicina l’inquadratura','Studia la specie'],
    '70-sfide-100-percento': ['Apri le sfide','Controlla ciò che manca','Scegli le prove più rapide'],
    'meditazione-capitolo-1': ['Prima del Capitolo 2','Segui Lucia sul balcone','Completa il minigioco','Sblocca entrambi i personaggi','Completa gli otto luoghi doppi','Raggiungi la meditazione finale'],
    'viaggio-rapido-taxi': ['Chiama il taxi','Scegli la destinazione','Salta il tragitto'],
    'poligoni-concentrazione': ['Raggiungi un poligono','Avvia la prova','Distingui allenamento e medaglie'],
}
REQUIREMENTS = {
    'soldi-facili-capitolo-1': 'Accesso alle zone del Capitolo 1. Per il luogo sull’acqua serve una barca. Prevedi possibili scontri.',
    'soldi-2500-three-sheets-liquor': 'L’incarico iniziale che porta al negozio. Conserva un salvataggio manuale prima di esporti ai rischi.',
    'scansionare-veicoli': 'App WAiNK disponibile. Comandi riferiti a PS5; controlla i prompt della tua configurazione.',
    'studiare-animali': 'Binocolo disponibile nella ruota degli oggetti.',
    '70-sfide-100-percento': 'Menu Progressi e sezione Sfide accessibili.',
    'meditazione-capitolo-1': 'Parti dal Capitolo 1, a casa di Jason. Dal Capitolo 2 puoi proseguire con entrambi i personaggi dopo Coffee Break.',
    'viaggio-rapido-taxi': 'Prima missione completata e servizio taxi disponibile nei Contatti.',
    'poligoni-concentrazione': 'Accesso a un poligono di tiro. Le medaglie vanno controllate separatamente dall’allenamento.',
}
LOCATIONS = {
    'soldi-facili-capitolo-1': 'Quattro luoghi diversi. Apri il riquadro spoiler per vedere i riferimenti geografici disponibili.',
    'soldi-2500-three-sheets-liquor': 'Il negozio dell’incarico. Le schermate e i riferimenti sono nel percorso protetto qui sotto.',
    'scansionare-veicoli': 'Davanti al veicolo che vuoi registrare nel catalogo. Non serve una posizione di spawn specifica.',
    'studiare-animali': 'Vicino a un animale visibile attraverso il binocolo.',
    '70-sfide-100-percento': 'Menu Progressi → Sfide, poi l’attività scelta sulla mappa.',
    'meditazione-capitolo-1': 'Primo luogo: balcone della casa di Jason a Key Lento. Gli altri nove luoghi sono elencati nella checklist, con riferimenti geografici verificati.',
    'viaggio-rapido-taxi': 'Telefono → Contatti → Paradise Taxi.',
    'poligoni-concentrazione': 'Uno dei poligoni disponibili sulla mappa. La fonte completa è in fondo.',
}
SUMMARIES = {
    'soldi-facili-capitolo-1': 'Scegli un luogo, controlla il bottino indicato e valuta i rischi prima di muoverti. Posizioni e incontri restano nascosti finché non li apri.',
    'soldi-2500-three-sheets-liquor': 'Un percorso breve: incarico, retro del negozio e nascondiglio. Due schermate aiutano a riconoscere i riferimenti della fonte.',
    'meditazione-capitolo-1': 'La prima meditazione è mancabile nel Capitolo 1. Hai 10 luoghi e 18 sessioni: 15 bastano per il 100%; per il trofeo punta a tutti, anche se la necessità della sessione iniziale resta da verificare.',
    'prima-persona-glitch-ps5': 'Premi Cerchio per riporre il telefono mentre tocchi rapidamente il touchpad impostato su Camera. PC Gamer ha provato il metodo, ma i trofei restano da verificare.',
    'sportive-randy-posizioni': 'Parti dalle richieste del gioco, cerca nelle zone documentate e controlla l’auto prima della consegna. Non promettiamo spawn fissi o veicoli unici.',
    'registrare-auto-personale': 'Parcheggiare non è registrare. Porta il mezzo in officina, controlla lo spazio disponibile e verifica che sia richiamabile.',
}


def enrich(records):
    result=[]
    for original in records:
        g=deepcopy(original)
        ident=g['id']
        g['safe_title']=SAFE_TITLES.get(ident,g.get('safe_title',g['title']))
        g['hero_media']=HERO.get(ident,'vice-city')
        g['step_media']=STEP_MEDIA.get(ident,{})
        g['step_headings']=HEADINGS.get(ident,[])
        g['requirements']=g.get('requirements') or REQUIREMENTS.get(ident,'Controlla i requisiti nella procedura e nella fonte.')
        g['location']=g.get('location') or LOCATIONS.get(ident,'Segui i riferimenti documentati nella procedura.')
        g['summary']=SUMMARIES.get(ident,g['summary'])
        g['spoiler']=g.get('spoiler',ident in {'soldi-facili-capitolo-1','soldi-2500-three-sheets-liquor','meditazione-capitolo-1'})
        g['category']=('soldi' if g['tag']=='Soldi' else 'garage' if g['tag']=='Garage' else 'auto' if ident in {'sportive-randy-posizioni','scansionare-veicoli'} else 'inizio')
        g['canonical_path']=g.get('canonical_path') or 'guide-e-tutorial/'+ident+'/'
        if ident in {'soldi-facili-capitolo-1','soldi-2500-three-sheets-liquor'}:
            g['extra_sources']=list(dict.fromkeys([*g.get('extra_sources',[]),
                'https://www.gtabase.com/gta-6/articles/how-to-keep-your-money-safe-in-gta-6',
                'https://gta.tech4gamers.com/gta-6/guides/money-end-of-chapter-1/',
                'https://www.powerpyx.com/gta-6-all-strangers-freaks-side-missions/']))
        if ident=='registrare-auto-personale':
            # The current guide source already covers Moses in Chapter 2.
            # Never overwrite its researched steps and checks with outdated
            # all-Pay-n-Spray instructions from an earlier presentation layer.
            g['extra_sources']=list(dict.fromkeys([*g.get('extra_sources',[]),
                'https://www.powerpyx.com/gta-6-moses-take-a-vehicle-to-moses-walkthrough/',
                'https://www.gtabase.com/gta-6/articles/how-to-unlock-garages-in-gta-6',
                'https://www.gamesradar.com/games/grand-theft-auto/gta-6-personal-vehicles-how-to-register-switch-recover-car/']))
            if len(g.get('steps',[]))<7 or len(g.get('checks',[]))!=len(g['steps']):
                raise ValueError('Car registration steps/checks must include Moses Chapter 2 and later unlocks')
        result.append(g)
    return result
