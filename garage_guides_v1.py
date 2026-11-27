"""Garage guides: original Italian, reviewed public references, no copied gameplay."""
from html import escape

PATH="garage-gratuiti/"
SOUTH=PATH+"southside-storage/"
DOMESTIC=PATH+"domestic-timbers/"
STORY=PATH+"garage-storia/"
VANESSA="veicoli/pfister-vanessas-growler/"
BOBCAT="veicoli/declasse-applesauce-bobcat/"
COQUETTE="veicoli/invetero-spiderweb-coquette/"
BUY="trofei/trofeo-54-posto-riservato/"
RANDY="guide-e-tutorial/sportive-randy-posizioni/"
REGISTER="salvare-auto/"
GARAGES="https://www.powerpyx.com/gta-6-all-garage-locations/"
PROPERTIES="https://www.gtabase.com/gta-6/properties/"
MURALS="https://www.powerpyx.com/gta-6-all-1010-mural-locations"
MURALS_ALT="https://www.gta-companion.com/guides/1010-murals"
SOUTH_MAP="https://www.gtabase.com/gta-6/properties/southside-storage"
COLLECT="https://www.powerpyx.com/gta-6-collect-the-tempesta-walkthrough/"
TEMP_MAP="https://www.gtabase.com/gta-6/vehicles/rauls-tempesta"
WISH="https://www.powerpyx.com/gta-6-randys-wish-list-car-locations-walkthrough/"
MAMBA="https://www.powerpyx.com/gta-6-dale-mamba-steal-the-declasse-mamba-gt-walkthrough/"
THRAX="https://www.powerpyx.com/gta-6-mansion-thrax-steal-the-truffade-thrax-walkthrough/"
DELIVERY="https://www.powerpyx.com/gta-6-delivery-day-meet-randy-walkthrough/"
CLONER="https://www.powerpyx.com/gta-6-how-to-get-key-cloner/"
MISSED="https://www.vice.com/en/article/gta-6-pink-porsche-location-garage-code/"
CODES="https://www.gta-companion.com/guides/garage-codes"

STORY_ROWS=(
 ("port-gellhorn","Port Gellhorn Station","2","Daily Driver","Port Gellhorn, Kelly County",1),
 ("thompson-court","Thompson Court","4","Company Cars","Ocean Beach, Vice Beach",2),
 ("ne-15th-street","NE 15th Street","5","Operation Savage Glory","Stockyard, Vice City",2),
 ("pegassi-residences","Pegassi Residences","5","Operation Savage Glory","Tequesta Retreat, Vice City",3),
)
SOUTH_STEPS=(
 ("Controlla il registro","Apri Progressi → Collezioni. Dopo la prima foto valida appare 1010 Murals. Usa la fotocamera del gioco e verifica ogni voce prima di lasciare la zona.","Il registro mostra i murales già completati; non è il contatore delle scansioni WAiNK.",MURALS),
 ("Rockridge — Loophole Architecture","Entra nei Parlor Apartments, usa l'ascensore per salire e fotografa la struttura circolare verso ovest.","La voce Loophole Architecture è registrata.",MURALS),
 ("Downtown — Compliance Theater","Raggiungi la terrazza del teatro, facendo attenzione alla sicurezza. Sali sull'antenna a sud e inquadra il tetto dipinto sotto di te.","La voce Compliance Theater è registrata.",MURALS),
 ("Downtown — Extraction Service","Usa l'ascensore nell'atrio; dal settore nord-ovest del tetto scatta verso il tetto più basso a ovest.","La voce Extraction Service è registrata.",MURALS),
 ("Ocean Beach — Privatized Pains Socialized Gains","Fermati sul marciapiede a nord-ovest di Effluvia Bar e punta verso la parte dipinta sotto il parcheggio a sud-est.","Il quarto soggetto risulta acquisito, se segui questo ordine.",MURALS_ALT),
 ("Crosstown — You Signed the Terms & Conditions","Aspetta a sud della fermata Mule City Line. Scatta soltanto quando il treno decorato è fermo al binario.","Il registro mostra cinque murales e arriva l'indizio della ricompensa.",MURALS_ALT),
 ("Apri Southside Storage","Segui l'indizio fino al sud di Salton, a nord di Slator Towing. Digita 1010 sul tastierino.","Il garage è accessibile e la 1010 Cheetah è all'interno.",SOUTH_MAP),
 ("Registra la Cheetah","Se vuoi conservarla, porta l'auto all'officina di registrazione disponibile e verifica il prezzo in gioco.","Controlla separatamente il garage di proprietà e la vettura registrata.",MURALS),
)
DOMESTIC_STEPS=(
 ("Sblocca Key Cloner","Nel Capitolo 3 raggiungi Clonin’ Keys, Makin’ GS e segui l'installazione sul telefono. Concludi la missione di Randy.","Il Key Cloner è disponibile e si apre Randy’s Wish List.",CLONER),
 ("Randy’s Wish List","Apri la lista in Mappa → Rapine, cerca i modelli richiesti e verifica ciascuno con WAiNK. Consegna i veicoli secondo le richieste attive.","Il registro delle consegne avanza; non fermarti a un numero stimato.",WISH),
 ("Dale Mamba","Quando Randy ti contatta, vai a Leaf Links. Cerca la chiave della Mamba GT nel salotto della villa; recupera il veicolo e consegnalo.","La missione Dale Mamba risulta completata.",MAMBA),
 ("Mansion Thrax","Termina le consegne richieste e attendi il contatto. Vai a Dalton Island; cerca la Thrax nell'area del club, presso Spa Splendido, poi segui la destinazione di consegna.","Randy accetta la Thrax.",THRAX),
 ("Delivery Day","Torna al concessionario dopo il messaggio di Randy. Segui la missione fino al porto, proteggendo la consegna secondo gli obiettivi del gioco.","Verifica il trofeo Supply & Demand (Bronzo), separato dal ritiro dell'auto.",DELIVERY),
 ("Collect the Tempesta","Attendi un ulteriore messaggio di Randy e segui il nuovo indicatore verso il garage a Balsero. Recupera Raul’s Tempesta.","Domestic Timbers compare tra i garage utilizzabili, con un posto.",COLLECT),
 ("Decidi se conservarla","Controlla il costo di registrazione e il ricavo proposto prima di confermare. Per una collezione di varianti speciali, conserva l'auto.","La Tempesta è registrata, oppure la vendita è confermata; il garage è un premio distinto.",TEMP_MAP),
)
def e(value):return escape(str(value),quote=True)
def ref(target,label):return '<a href="'+e(target)+'" target="_blank" rel="noopener noreferrer">'+e(label)+'</a>'
def internal(base,target,label):return '<a href="'+e(base+target)+'">'+e(label)+'</a>'
def banner(base):
    return '<p class="v-guide-video-crosslink"><strong>Garage gratis e segreti:</strong> '+internal(base,PATH,"scopri tutti gli sblocchi, i codici e le ricompense →")+'</p>'
def start(base,title,desc):
    return '<article class="vc-article garage-guide" data-garage-guide><nav class="vc-crumb" aria-label="Percorso">'+internal(base,PATH,"Garage gratuiti")+'</nav><section class="vc-article-hero"><span class="vc-eyebrow">GTA VI · PS5 / PS5 PRO</span><h1>'+e(title)+'</h1><p>'+e(desc)+'</p><p>Verifica delle fonti: 27 novembre 2026. Patch di gioco non verificata direttamente; possibili spoiler.</p></section>'
def facts(rows):
    return '<section class="vc-facts"><h2>Risposta immediata</h2><dl>'+''.join('<div><dt>'+e(k)+'</dt><dd>'+e(v)+'</dd></div>' for k,v in rows)+'</dl></section>'
def steps(rows):
    result=['<section class="vc-instructions" id="procedura"><h2>Come sbloccarlo: '+str(len(rows))+' passaggi</h2><ol>']
    for n,(title,action,check,source) in enumerate(rows,1):
        result.append('<li data-garage-step="'+str(n)+'"><span aria-hidden="true">'+str(n)+'</span><div><h3>'+e(title)+'</h3><p>'+e(action)+'</p><p><strong>Controllo:</strong> '+e(check)+'</p><p>'+ref(source,"Posizione, schermate o dettagli nella fonte originale ↗")+'</p></div></li>')
    return ''.join(result)+'</ol></section>'
def end(base,refs,extra=""):
    return ('<section class="vc-source" id="fonti"><h2>Fonti e verifica</h2>'+''.join(ref(u,n) for n,u in refs)+
            '<p>Guide indipendenti, non prova diretta nella nostra partita. Le immagini originali restano presso gli autori; non abbiamo copiato screenshot. Le posizioni sono riferimenti descritti, non coordinate inventate.</p>'+extra+
            '</section><nav class="vc-related" aria-label="Guide correlate"><h2>Continua con</h2>'+internal(base,PATH,"Garage gratuiti")+internal(base,REGISTER,"Registrare e conservare auto")+internal(base,BUY,"Trofeo Little Boxes")+'</nav></article>')
def index_body(base):
    cards=[
        ("Del Rio Boulevard · priorità Capitolo 3",VANESSA,"1 posto + Growler rosa · codice 92665","Recupera prima di The Cartel Heist: le fonti segnalano una finestra mancabile."),
        ("Southside Storage",SOUTH,"1 posto + 1010 Cheetah · codice 1010","Completa cinque murales. Garage gratuito, registrazione auto separata."),
        ("Domestic Timbers",DOMESTIC,"1 posto + Raul’s Tempesta","Termina la catena di Randy e ritira il premio a Balsero."),
    ]+[(name,STORY+"#"+ident,str(spots)+" posti · Capitolo "+chapter,"Completa "+mission+"; sblocco di storia.") for ident,name,chapter,mission,area,spots in STORY_ROWS]
    body=start(base,"GTA VI: garage gratuiti e segreti","Sette garage documentati: tre bonus opzionali e quattro ricompense della storia. Non serve acquistare un garage per ottenere questi sblocchi.")
    body+='<section><h2>Quale sbloccare prima?</h2><p>Nel Capitolo 3, fai subito Del Rio se non l’hai già preso. Poi scegli i murales o la catena di Randy. I garage dei Capitoli 4 e 5 arrivano con la storia.</p><div class="vc-grid">'
    for name,target,reward,desc in cards:
        body+='<div class="vc-card" data-garage-entry><h3>'+internal(base,target,name)+'</h3><p><strong>'+e(reward)+'</strong></p><p>'+e(desc)+'</p></div>'
    body+='</div></section><section><h2>Garage con auto, proprietà non confermata</h2><p>'+internal(base,BOBCAT,"Red Apple Orchard — 360782, Applesauce Bobcat")+' · '+internal(base,COQUETTE,"Party House — 092319, Spiderweb Coquette")+'</p><p>Il recupero dell’auto non conferma uno slot di proprietà. Controlla il menu garage e la registrazione.</p></section>'
    body+='<section><h2>Platino: otto acquisti separati</h2><p>Little Boxes richiede tutti gli otto garage acquistabili tramite Vice City Real Estate. I bonus gratuiti, di storia o di edizione non li sostituiscono. Non sommare varianti di cataloghi discordanti come totale definitivo dei garage.</p>'+internal(base,BUY,"Requisito del trofeo →")+'</section>'
    return body+end(base,[("PowerPyx — garage",GARAGES),("GTABase — proprietà",PROPERTIES),("GTABase — Southside",SOUTH_MAP),("PowerPyx — Tempesta",COLLECT),("VICE — Del Rio mancabile",MISSED),("GTA Companion — codici",CODES)])
def south_body(base):
    body=start(base,"Southside Storage: 5 murales e 1010 Cheetah","Fotografa tutti i cinque murales 1010, poi usa il codice 1010 per sbloccare Southside Storage a Salton.")
    body+=facts([("Garage","Gratuito, 1 posto"),("Zona","Salton, a nord di Slator Towing"),("Codice","1010"),("Veicolo","1010 Cheetah: registrazione a parte")])
    body+='<p class="vc-check">I cinque murales non sono necessari per il 100% e non contano nelle 100 scansioni WAiNK. Verifica il loro registro specifico.</p>'+steps(SOUTH_STEPS)
    return body+end(base,[("PowerPyx — cinque murales",MURALS),("GTA Companion — percorso",MURALS_ALT),("GTABase — garage e mappa",SOUTH_MAP)])
def domestic_body(base):
    body=start(base,"Domestic Timbers: garage gratuito e Raul’s Tempesta","Completa tutte le richieste di Randy nel Capitolo 3, quindi ritira il premio in Collect the Tempesta.")
    body+=facts([("Garage","Gratuito, 1 posto"),("Zona","Balsero, Vice City"),("Prerequisito","Delivery Day conclusa"),("Personaggi","Jason o Lucia"),("Veicolo","Raul’s Tempesta"),("Prezzi indicativi","11.600 GTA$ registrazione; circa 27.150 GTA$ vendita in buone condizioni")])
    body+='<p class="vc-check">Non vendere la variante speciale per sbaglio. Il trofeo arriva con Delivery Day, non con il ritiro successivo. Nessuna soglia di consegne garantita: segui i messaggi di Randy.</p>'+steps(DOMESTIC_STEPS)
    body+='<section><h2>Lista auto e Key Cloner</h2><p>'+internal(base,RANDY,"Posizioni delle auto di Randy e consegne →")+' · '+ref(CLONER,"Sblocco Key Cloner su PowerPyx ↗")+'</p></section>'
    return body+end(base,[("PowerPyx — ritiro Tempesta",COLLECT),("GTABase — variante e mappa",TEMP_MAP),("PowerPyx — Delivery Day",DELIVERY),("PowerPyx — lista Randy",WISH)])
def story_body(base):
    body=start(base,"Garage gratuiti della storia: Capitoli 2, 4 e 5","Quattro garage assegnati automaticamente dalle missioni principali, per otto posti complessivi secondo le fonti.")
    for ident,name,chapter,mission,area,spots in STORY_ROWS:
        body+='<section class="vc-instructions" id="'+e(ident)+'" data-story-garage="'+e(ident)+'"><h2>'+e(name)+'</h2><p><strong>'+e(area)+' · '+str(spots)+' '+('posto' if spots==1 else 'posti')+'</strong></p><ol><li><span aria-hidden="true">1</span><div>Completa '+e(mission)+' nel Capitolo '+e(chapter)+'.</div></li><li><span aria-hidden="true">2</span><div>Controlla la nuova proprietà e gli slot disponibili nel menu garage.</div></li></ol><p class="vc-check">Non acquistarlo: è un premio della storia. Nessuna auto speciale inclusa confermata.</p></section>'
    return body+end(base,[("PowerPyx — garage storia",GARAGES),("GTABase — proprietà",PROPERTIES)],'<p>Gli otto posti di storia non equivalgono agli otto garage acquistabili del trofeo Little Boxes.</p>')
def pages(base):
    return [(PATH,"Garage gratuiti GTA VI: sette sblocchi, codici e ricompense","Guida ai garage gratuiti GTA VI: Southside Storage, Domestic Timbers, Del Rio e ricompense della storia. Distinzione Little Boxes.",index_body(base),"CollectionPage"),
            (SOUTH,"Southside Storage GTA VI: 5 murales e 1010 Cheetah","Sblocca il garage di Salton e la 1010 Cheetah: cinque posizioni, codice 1010 e registrazione del veicolo.",south_body(base),"Article"),
            (DOMESTIC,"Domestic Timbers GTA VI: garage e Tempesta di Randy","Catena di Randy dal Key Cloner a Collect the Tempesta: garage gratuito, trofeo e costi indicativi.",domestic_body(base),"Article"),
            (STORY,"Garage gratuiti GTA VI: tutti gli sblocchi della storia","Port Gellhorn, Thompson Court, NE 15th Street e Pegassi Residences: missioni di sblocco e posti.",story_body(base),"Article")]
