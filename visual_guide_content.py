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
    'registrare-auto-personale': 'Come salvare e richiamare la prima auto in GTA VI',
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
# Only step-specific screenshots approved in data/tutorial_photo_review.json
# may appear in a numbered tutorial. Other media remains in source records only.
STEP_MEDIA = {
    # No third-party gameplay photograph may appear inline without a documented
    # reuse permission. This guide links to original photos and video instead.
}

HEADINGS = {
    'soldi-facili-capitolo-1': ['Il retro del negozio','Il motel da esplorare','La casa sull’acqua','L’oggetto di valore nel magazzino'],
    'soldi-2500-three-sheets-liquor': ['Parti dall’incarico giusto','Raggiungi il retro','Individua il riferimento','Controlla il nascondiglio','Completa l’esplorazione'],
    'registrare-auto-personale': ['Raggiungi Moses a Port Gellhorn','Scansiona le auto con WAiNK','Apri la Montagne XL con lo Slim Jim','Scegli un’auto senza tracker, se necessario','Rivernicia l’auto da Moses','Registra gratis la prima auto','Richiama il mezzo con Scooter Bros'],
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
    'soldi-2500-three-sheets-liquor': 'Un percorso breve: incarico, retro del negozio e nascondiglio. Passi numerati e fonti consultabili senza immagini fuori contesto.',
    'meditazione-capitolo-1': 'La prima meditazione è mancabile nel Capitolo 1. Hai 10 luoghi e 18 sessioni: 15 bastano per il 100%; per il trofeo punta a tutti, anche se la necessità della sessione iniziale resta da verificare.',
    'prima-persona-glitch-ps5': 'Premi Cerchio per riporre il telefono mentre tocchi rapidamente il touchpad impostato su Camera. PC Gamer ha provato il metodo, ma i trofei restano da verificare.',
    'sportive-randy-posizioni': 'Parti dalle richieste del gioco, cerca nelle zone documentate e controlla l’auto prima della consegna. Non promettiamo spawn fissi o veicoli unici.',
    'registrare-auto-personale': 'Dopo Girl’s Trip, porta un’auto senza tracker da Moses a Port Gellhorn: la prima registrazione è gratuita. Scooter Bros si sblocca al termine della missione.',
}


# SEO snippets are separate from human-readable guide summaries. Reuse only
# verified guide facts; do not turn an uncertain trophy status into a promise.
SEO_DESCRIPTIONS = {
    'registrare-auto-personale': 'GTA VI PS5: come trovare Moses, usare WAiNK e Slim Jim, registrare gratis la prima auto e richiamarla tramite Scooter Bros.',
    'scansionare-veicoli': 'GTA 6 PS5: come usare WAiNK per scansionare i veicoli e completare il catalogo verso il 100%. Passaggi pratici e controlli nel gioco.',
    'studiare-animali': 'GTA VI PS5: studia le specie con il binocolo per il completamento al 100%. Scopri i comandi, il controllo dei progressi e le fonti della guida.',
    '70-sfide-100-percento': 'GTA VI 100% su PS5: completa 70 sfide su 80 scegliendo quelle più rapide. Checklist e consigli per ridurre il tempo necessario al platino.',
    'meditazione-capitolo-1': 'GTA VI PS5: checklist delle 18 meditazioni in 10 luoghi, la prima occasione mancabile nel Capitolo 1 e gli avvisi per il platino.',
    'viaggio-rapido-taxi': 'GTA 6 su PS5: chiama Paradise Taxi, scegli la destinazione e salta i tragitti tra missioni. Procedura, pulsanti e costi documentati.',
    'poligoni-concentrazione': 'GTA VI PS5: allenati ai poligoni di tiro e distingui Concentrazione e medaglie Oro. Controlla le prove richieste per il platino.',
    'prima-persona-glitch-ps5': 'GTA VI PS5: attiva la visuale in prima persona con telefono e touchpad. Procedura DualSense, ripristino e stato trofei incerto.',
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
        g['seo_description']=SEO_DESCRIPTIONS.get(ident,g['summary'])
        if not 70 <= len(g['seo_description']) <= 160:
            raise ValueError('Guide SEO description needs a sourced, readable 70-160 char snippet: '+ident)
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
