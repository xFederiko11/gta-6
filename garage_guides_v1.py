"""Garage guides: original Italian, reviewed public references, no copied gameplay."""
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import json
from garage_codes_v1 import code_field
from interactive_article_maps_v1 import render as render_interactive_map, render_vehicle_map

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
PROPERTIES="https://www.gtabase.com/gta-6/articles/how-to-unlock-garages-in-gta-6"
MURALS="https://www.powerpyx.com/gta-6-all-1010-mural-locations"
MURALS_ALT="https://www.gta-companion.com/guides/1010-murals"
SOUTH_MAP="https://www.gtabase.com/gta-6/properties/southside-storage"
COLLECT="https://www.powerpyx.com/gta-6-collect-the-tempesta-walkthrough/"
TEMP_MAP="https://www.gtabase.com/gta-6/properties/domestic-timbers"
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
 ("Controlla requisito e registro","Il capitolo minimo non è documentato. Le fonti descrivono il challenge Snapmatic 1010 come open world. Apri Progressi → Collezioni; se 1010 Murals non compare, prova un primo scatto valido con la fotocamera del telefono (non WAiNK), poi riapri il registro.","Il registro 1010 Murals compare e mostra i soggetti acquisiti. I cinque murales non contano nel 100% né nelle 100 scansioni WAiNK.",MURALS),
 ("Rockridge — Loophole Architecture","Il murale è sul tetto del Rockridge Blood Center. Raggiungi il tetto di fronte, indicato come Parlor Apartments; cerca il cerchio 1010, fermati sul segno, guarda la grafica circolare sul tetto opposto e scatta con la fotocamera del telefono.","La voce Loophole Architecture risulta acquisita nel registro 1010 Murals.",MURALS),
 ("Downtown — Compliance Theater","Raggiungi il grattacielo vicino a SE 2nd Ave. Sali sul tetto con ascensore e scala di manutenzione; raggiungi l’antenna del palazzo accanto. Cerca il cerchio 1010 e, dal segno, inquadra il tetto dipinto sottostante.","La voce Compliance Theater è registrata. Usa il segno sul tetto come punto di scatto, non il tetto dipinto come punto di partenza.",MURALS),
 ("Downtown — Extraction Service","Vai al tetto dell’edificio residenziale vicino al parco, in zona SE 1st Ave. Il punto di scatto è sul tetto adiacente: cerca il cerchio 1010 presso l’angolo nord-ovest e guarda verso la grafica sul tetto della torre accanto.","La voce Extraction Service compare nel registro. La mappa esterna marca il murale; il punto di scatto è sul tetto vicino.",MURALS),
 ("Ocean Beach — Privatized Pains Socialized Gains","Il murale è dipinto sul fianco del parcheggio pubblico nella zona nord-occidentale di Ocean Beach/Vice Beach. Raggiungi il marciapiede di Barlow St, individua il cerchio 1010 a livello strada e, dal segno, punta verso il murale sul lato del garage.","La voce Privatized Pains Socialized Gains è registrata. Il pin esterno indica il murale; non sostituisce il punto di scatto sul marciapiede.",MURALS),
 ("Crosstown — You Signed the Terms & Conditions","Raggiungi a livello strada il cavalcavia ferroviario della Mule City Line, sul lato sud di NE 2nd Ave. Cerca il cerchio 1010 sul margine erboso, fermati sul segno e fotografa la grafica sul lato del cavalcavia con la fotocamera del telefono. Le fonti non concordano se il soggetto sia un treno o il cavalcavia: segui il video e il marcatore visibile, senza aspettare un treno in fermata come requisito certo.","Il registro mostra cinque voci e compare l’indizio per Southside Storage. Se la grafica non corrisponde, riapri il riferimento video e verifica il registro prima di proseguire.",MURALS_ALT),
 ("Apri Southside Storage","Dopo aver fotografato tutti e cinque i murales, guida fino alla punta meridionale di Salton, a nord di Slator Towing. Il garage è una rimessa con serranda. Interagisci con il tastierino montato sulla parete e inserisci 1010; entra e prendi la ’95 Grotti Cheetah.","La serranda si apre e la Cheetah è disponibile all’interno. Il garage gratuito e il veicolo sono due ricompense distinte.",SOUTH_MAP),
 ("Registra la Cheetah","La Cheetah non diventa automaticamente un veicolo personale registrato quando entri nel garage. Se vuoi conservarla, portala a un servizio di registrazione auto disponibile nel gioco e conferma il prezzo mostrato prima di procedere.","Controlla separatamente il garage di proprietà e la Cheetah nella lista dei veicoli personali; non confermare un acquisto se vuoi solo sbloccare il garage.",MURALS),
)
DOMESTIC_STEPS=(
 ("Sblocca Key Cloner","Nel Capitolo 3 raggiungi Clonin’ Keys, Makin’ GS e segui l'installazione sul telefono. Concludi la missione di Randy.","Il Key Cloner è disponibile e si apre Randy’s Wish List.",CLONER),
 ("Randy’s Wish List","Apri la lista in Mappa → Rapine, cerca i modelli richiesti e verifica ciascuno con WAiNK. Consegna i veicoli secondo le richieste attive.","Il registro delle consegne avanza; non fermarti a un numero stimato.",WISH),
 ("Dale Mamba","PowerPyx indica il Capitolo 3, GTABase il Capitolo 4. Quando Randy ti contatta, vai a Leaf Links. Cerca la chiave della Mamba GT nel salotto della villa; recupera il veicolo e consegnalo.","La missione Dale Mamba risulta completata.",MAMBA),
 ("Mansion Thrax","Termina le consegne richieste e attendi il contatto. Vai a Dalton Island; cerca la Thrax nell'area del club, presso Spa Splendido, poi segui la destinazione di consegna.","Randy accetta la Thrax.",THRAX),
 ("Delivery Day","Torna al concessionario dopo il messaggio di Randy. Segui la missione fino al porto, proteggendo la consegna secondo gli obiettivi del gioco.","Verifica il trofeo Supply & Demand (Bronzo) e il premio di 25.000 GTA$ riportato da PowerPyx, separati dal ritiro dell’auto.",DELIVERY),
 ("Collect the Tempesta","Attendi un ulteriore messaggio di Randy e segui il nuovo indicatore verso il garage a Balsero. Recupera Raul’s Tempesta.","Domestic Timbers compare tra i garage utilizzabili, con un posto: è un garage premio, non uno degli otto acquisti Little Boxes.",COLLECT),
 ("Decidi se conservarla","Controlla il costo di registrazione e il ricavo proposto prima di confermare. Per una collezione di varianti speciali, conserva l'auto.","La Tempesta è registrata, oppure la vendita è confermata; il garage è un premio distinto.",TEMP_MAP),
)
def e(value):return escape(str(value),quote=True)
def ref(target,label):return '<a href="'+e(target)+'" target="_blank" rel="noopener noreferrer">'+e(label)+'</a>'
def internal(base,target,label):return '<a href="'+e(base+target)+'">'+e(label)+'</a>'
def _load_media_registry():
    path=Path(__file__).parent/"data"/"editorial_media_registry_v1.json"
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema")!="gta6-editorial-media-rights-v1":
        raise ValueError("Unknown editorial media rights registry")
    rows=data.get("items")
    if not isinstance(rows,list) or len(rows)!=7:
        raise ValueError("Southside registry must contain six map pins and one video")
    by_id={row.get("id"):row for row in rows}
    if len(by_id)!=len(rows):
        raise ValueError("Duplicate media registry ID")
    expected_map_steps={
        "southside-map-loophole":2,"southside-map-compliance":3,
        "southside-map-extraction":4,"southside-map-privatized":5,
        "southside-map-terms":6,"southside-map-garage":7}
    if {key:by_id.get(key,{}).get("step") for key in expected_map_steps}!=expected_map_steps:
        raise ValueError("Southside map pin step mapping changed")
    for ident,step in expected_map_steps.items():
        row=by_id[ident]
        parts=urlsplit(row.get("source_url",""))
        if (row.get("kind")!="community_map_location_link" or row.get("article_path")!=SOUTH or
            row.get("rights_status")!="external_link_only" or parts.scheme!="https" or
            parts.hostname!="gtatown.com" or row.get("allowed_channels")!=["site_external_link"]):
            raise ValueError("Map assets must remain source-linked and rights scoped")
    video=by_id.get("southside-powerpyx-video",{})
    seconds={"2":6,"3":70,"4":172,"5":294,"6":255,"7":323}
    if (video.get("kind")!="youtube_video" or video.get("video_id")!="mu_VCQKeXvM" or
        video.get("rights_status")!="youtube_platform_embed_only" or
        video.get("timestamps_seconds")!=seconds or
        video.get("allowed_channels")!=["site_opt_in_embed","site_external_link","x_link"] or
        video.get("embed_setting")!="creator-controlled; fall back to original link"):
        raise ValueError("Video reuse must stay opt-in and platform-hosted")
    return data,by_id


MEDIA_REGISTRY, SOUTH_MEDIA = _load_media_registry()


def map_reference(record_id, *, note):
    row=SOUTH_MEDIA[record_id]
    return ('<aside class="v-map-reference" data-southside-map-pin="'+e(record_id)+'" aria-label="Riferimento mappa: '+e(row["label"])+'">'
            '<span aria-hidden="true">⌖</span><div><strong>'+e(row["label"])+'</strong>'
            '<p>'+e(note)+'</p>'
            '<a href="'+e(row["source_url"])+'" target="_blank" rel="noopener noreferrer">'
            'Apri il riferimento sulla mappa community ↗</a>'
            '<small>Fonte: GTA Town; dati base Open GTA 6 Map (fbritoferreira), CC BY 4.0. Link alla fonte, nessuna mappa o schermata copiata.</small>'
            '</div></aside>')


def video_reference(title,seconds,source):
    video=SOUTH_MEDIA["southside-powerpyx-video"]
    if seconds not in video["timestamps_seconds"].values():
        raise ValueError("Unreviewed video timestamp")
    stamp=f"{seconds//60}:{seconds%60:02d}"
    youtube="https://www.youtube.com/watch?v="+video["video_id"]+"&t="+str(seconds)+"s"
    return ('<details class="v-video-reference" open><summary>Gameplay originale PowerPyx · '+e(title)+' · '+stamp+'</summary>'
            '<div class="v-video-copy"><strong>Riferimento visivo per questo passaggio</strong>'
            '<p>Il video resta su YouTube. Premi il pulsante per caricare il player qui, dal minuto indicato.</p>'
            '<div class="v-video-shell" data-youtube-id="'+e(video["video_id"])+'" data-youtube-start="'+str(seconds)+'">'
            '<div class="v-video-embed" data-youtube-holder>'
            '<span class="v-video-play-art" aria-hidden="true">▶</span>'
            '<button type="button" data-load-youtube>Riproduci da '+stamp+'</button>'
            '<small>Player YouTube privacy-enhanced; nessun iframe o richiesta a YouTube prima del clic.</small></div></div>'
            '<p class="v-video-links"><a href="'+e(youtube)+'" target="_blank" rel="noopener noreferrer">Apri il video PowerPyx da '+stamp+' ↗</a></p>'
            '<p class="v-caption"><small>Capitolo e posizione indicati da GTA Town: '+
            ref(source,"scheda del luogo e timestamp ↗")+
            '. L’embed dipende dall’impostazione del creator; se non disponibile, usa il link YouTube. Il filmato non è stato registrato dal nostro team.</small></p>'
            '</div></details>')
def banner(base):
    return '<p class="v-guide-video-crosslink"><strong>Garage gratis e segreti:</strong> '+internal(base,PATH,"scopri tutti gli sblocchi, i codici e le ricompense →")+'</p>'
def start(base,title,desc):
    return '<article class="vc-article garage-guide" data-garage-guide><nav class="vc-crumb" aria-label="Percorso">'+internal(base,PATH,"Garage gratuiti")+'</nav><section class="vc-article-hero"><span class="vc-eyebrow">GTA VI · PS5 / PS5 PRO</span><h1>'+e(title)+'</h1><p>'+e(desc)+'</p><p>Verifica delle fonti: 27 novembre 2026. Patch di gioco non verificata direttamente; possibili spoiler.</p></section>'
def facts(rows):
    return '<section class="vc-facts"><h2>Risposta immediata</h2><dl>'+''.join('<div><dt>'+e(k)+'</dt><dd>'+e(v)+'</dd></div>' for k,v in rows)+'</dl></section>'
def steps(rows,video_chapters=None,map_refs=None):
    result=['<section class="vc-instructions" id="procedura"><h2>Come sbloccarlo: '+str(len(rows))+' passaggi</h2><ol>']
    for n,(title,action,check,source) in enumerate(rows,1):
        video=video_reference(title,*video_chapters[n]) if video_chapters and n in video_chapters else ""
        map_card=map_reference(map_refs[n],note="Pin cartografico del luogo; il punto da cui fotografare è descritto separatamente nel passaggio.") if map_refs and n in map_refs else ""
        source_card="" if map_refs and n in map_refs else '<p>'+ref(source,"Fonte e dettagli originali ↗")+'</p>'
        result.append('<li data-garage-step="'+str(n)+'"><span aria-hidden="true">'+str(n)+'</span><div><h3>'+e(title)+'</h3><p>'+e(action)+'</p><p><strong>Controllo:</strong> '+e(check)+'</p>'+map_card+source_card+video+'</div></li>')
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
    ]+[(name,STORY+ident+"/",str(spots)+" posti · Capitolo "+chapter,"Completa "+mission+"; sblocco di storia.") for ident,name,chapter,mission,area,spots in STORY_ROWS]
    body=start(base,"GTA VI: garage gratuiti e segreti","Sette garage documentati: tre bonus opzionali e quattro ricompense della storia. Non serve acquistare un garage per ottenere questi sblocchi.")
    body+='<section><h2>Quale sbloccare prima?</h2><p>Nel Capitolo 3, fai subito Del Rio se non l’hai già preso. Poi scegli i murales o la catena di Randy. I garage dei Capitoli 4 e 5 arrivano con la storia.</p><div class="vc-grid">'
    for name,target,reward,desc in cards:
        body+='<div class="vc-card" data-garage-entry><h3>'+internal(base,target,name)+'</h3><p><strong>'+e(reward)+'</strong></p><p>'+e(desc)+'</p></div>'
    body+='</div></section><section><h2>Codici dei garage</h2>'+code_field("1010","Southside Storage")+code_field("92665","Del Rio Boulevard")+'</section><section><h2>Garage con auto, proprietà non confermata</h2><p>'+internal(base,BOBCAT,"Red Apple Orchard — 360782, Applesauce Bobcat")+' · '+internal(base,COQUETTE,"Party House — 092319, Spiderweb Coquette")+'</p><p>Il recupero dell’auto non conferma uno slot di proprietà. Controlla il menu garage e la registrazione.</p></section>'
    body+='<section><h2>Platino: otto acquisti separati</h2><p>Little Boxes richiede tutti gli otto garage acquistabili tramite Vice City Real Estate. I bonus gratuiti, di storia o di edizione non li sostituiscono. Non sommare varianti di cataloghi discordanti come totale definitivo dei garage.</p>'+internal(base,BUY,"Requisito del trofeo →")+'</section>'
    return body+end(base,[("PowerPyx — garage",GARAGES),("GTABase — sblocco garage",PROPERTIES),("GTABase — Southside",SOUTH_MAP),("GTABase — Domestic Timbers",TEMP_MAP),("PowerPyx — Tempesta",COLLECT),("VICE — Del Rio mancabile",MISSED),("GTA Companion — codici",CODES)])
def south_body(base):
    body=start(base,"Southside Storage: mappa dei cinque murales e codice 1010","Segui i cinque punti 1010, apri il garage gratuito a Southside e trova la ’95 Grotti Cheetah. Ogni tappa distingue posizione del murale, punto di scatto e verifica.")
    body+=facts([("Garage","Gratuito, 1 posto"),("Zona","Salton, a nord di Slator Towing"),("Codice tastierino","1010"),("Auto","’95 Grotti Cheetah: registrazione separata"),("Capitolo minimo","Non documentato dalle fonti; il challenge è descritto come open world")])
    map_points=[]
    for ident in ("southside-map-loophole","southside-map-compliance","southside-map-extraction","southside-map-privatized","southside-map-terms","southside-map-garage"):
        row=SOUTH_MEDIA[ident]
        map_points.append({"name":row["label"],"where":row["where"],"precision":"described"})
    body+=render_interactive_map("Southside Storage e i cinque murales 1010",map_points,
        id_suffix="southside-storage",page_label="guida")
    body+=code_field("1010","Codice Southside Storage")
    body+='<p class="vc-check">Ordine e verifica: usa la fotocamera del telefono, non WAiNK; riapri Progressi → Collezioni dopo ogni foto. Il completamento dei cinque murales dà l’indizio del garage, ma non è richiesto per il 100%.</p>'
    body+=steps(SOUTH_STEPS,
        {2:(6,"https://gtatown.com/locations/1010-mural-1-loophole-architecture-rockridge"),
         3:(70,"https://gtatown.com/locations/1010-mural-2-compliance-theater-downtown"),
         4:(172,"https://gtatown.com/locations/1010-mural-3-extraction-service-downtown"),
         5:(294,"https://gtatown.com/locations/1010-mural-5-privatized-pains-vice-beach-garage"),
         6:(255,"https://gtatown.com/locations/1010-mural-4-terms-and-conditions-crosstown-overpass"),
         7:(323,"https://gtatown.com/locations/1010-murals-reward-cheetah-southside-storage-garage")},
        {2:"southside-map-loophole",3:"southside-map-compliance",4:"southside-map-extraction",
         5:"southside-map-privatized",6:"southside-map-terms",7:"southside-map-garage"})
    sources=[("PowerPyx — guida dei cinque murales",MURALS),
        ("GTA Town — mappa e raccolta 1010", "https://gtatown.com/collectibles/1010-murals"),
        ("GTA Town — Loophole Architecture","https://gtatown.com/locations/1010-mural-1-loophole-architecture-rockridge"),
        ("GTA Town — Compliance Theater","https://gtatown.com/locations/1010-mural-2-compliance-theater-downtown"),
        ("GTA Town — Extraction Service","https://gtatown.com/locations/1010-mural-3-extraction-service-downtown"),
        ("GTA Town — Terms & Conditions","https://gtatown.com/locations/1010-mural-4-terms-and-conditions-crosstown-overpass"),
        ("GTA Town — Privatized Pains","https://gtatown.com/locations/1010-mural-5-privatized-pains-vice-beach-garage"),
        ("GTA Town — Southside e Grotti Cheetah","https://gtatown.com/locations/1010-murals-reward-cheetah-southside-storage-garage"),
        ("GTA Town — licenze dei dati mappa","https://gtatown.com/credits"),
        ("YouTube Help — incorporare video", "https://support.google.com/youtube/answer/171780?hl=en")]
    return body+end(base,sources,
        '<p class="v-rights-note"><strong>Media:</strong> i video vengono caricati dal player YouTube solo su richiesta; non sono state copiate anteprime o schermate. I riferimenti mappa aprono la fonte e sono registrati con il relativo ambito d’uso in <code>editorial_media_registry_v1.json</code>.</p>')
def domestic_body(base):
    body=start(base,"Domestic Timbers: garage gratuito e Raul’s Tempesta","Avvia la catena di Randy nel Capitolo 3; prosegui fino a Collect the Tempesta. Le fonti divergono sul capitolo di sblocco di Dale Mamba.")
    body+=facts([("Garage","Gratuito, 1 posto"),("Zona","Balsero, Vice City"),("Prerequisito","Delivery Day conclusa, poi messaggio di Randy"),("Capitolo","PowerPyx: 3; non garantito per tutte le progressioni"),("Personaggi","Jason o Lucia"),("Veicolo","Raul’s Tempesta"),("Prezzi indicativi","11.600 GTA$ registrazione; circa 27.150 GTA$ vendita in buone condizioni")])
    body+=render_vehicle_map(DOMESTIC)
    body+='<p class="vc-check">Non vendere la variante speciale per sbaglio. Il trofeo arriva con Delivery Day, non con il ritiro successivo. Nessuna soglia di consegne garantita: segui i messaggi di Randy.</p>'+steps(DOMESTIC_STEPS)
    body+='<section><h2>Lista auto e Key Cloner</h2><p>'+internal(base,RANDY,"Posizioni delle auto di Randy e consegne →")+' · '+internal(base,"guide-e-tutorial/key-cloner/","Guida Key Cloner in italiano")+" · "+ref(CLONER,"Fonte PowerPyx ↗")+'</p></section>'
    return body+end(base,[("PowerPyx — ritiro Tempesta",COLLECT),("GTABase — Domestic Timbers e mappa",TEMP_MAP),("PowerPyx — Delivery Day",DELIVERY),("PowerPyx — lista Randy",WISH)])
def story_body(base):
    body=start(base,"Garage gratuiti della storia: Capitoli 2, 4 e 5","Quattro garage assegnati automaticamente dalle missioni principali, per otto posti complessivi secondo le fonti.")
    for ident,name,chapter,mission,area,spots in STORY_ROWS:
        body+='<section class="vc-instructions" id="'+e(ident)+'" data-story-garage="'+e(ident)+'"><h2>'+internal(base,STORY+ident+"/",name)+'</h2><p><strong>'+e(area)+' · '+str(spots)+' '+('posto' if spots==1 else 'posti')+'</strong></p><ol><li><span aria-hidden="true">1</span><div>Completa '+e(mission)+' nel Capitolo '+e(chapter)+'.</div></li><li><span aria-hidden="true">2</span><div>Controlla la nuova proprietà e gli slot disponibili nel menu garage.</div></li></ol><p class="vc-check">Non acquistarlo: è un premio della storia. Nessuna auto speciale inclusa confermata.</p></section>'
    return body+end(base,[("PowerPyx — garage storia",GARAGES),("GTABase — proprietà",PROPERTIES)],'<p>Gli otto posti di storia non equivalgono agli otto garage acquistabili del trofeo Little Boxes.</p>')
def story_detail(base,row):
    ident,name,chapter,mission,area,spots=row
    map_url="https://www.gtabase.com/gta-6/properties/"+ident+("-station-garage" if ident=="port-gellhorn" else "-garage")
    title=name+" Garage: come sbloccarlo in GTA 6"
    body=start(base,title,"Garage gratuito della storia: "+area+", "+str(spots)+(" posto" if spots==1 else " posti")+".")
    body+=facts([("Capitolo",chapter),("Missione",mission),("Zona",area),("Capienza",str(spots)),("Prezzo","Gratuito: premio della storia")])
    body+='<section class="vc-source"><h2>Foto originale e posizione</h2><p>'+ref(map_url,"Apri la scheda GTABase con foto e mappa ↗")+'</p><p>La mappa originale è consultabile presso la fonte: nessuna coordinata approssimata o screenshot copiato.</p></section>'
    body+=steps((("Completa la missione","Prosegui la storia fino a "+mission+" nel Capitolo "+chapter+". Completa gli obiettivi indicati dal gioco.","La missione è conclusa.",GARAGES),("Controlla il nuovo garage","Dopo la missione, controlla le proprietà e i posti disponibili. Non acquistare un secondo garage per questo sblocco.","Compare "+name+" con "+str(spots)+(" posto." if spots==1 else " posti."),map_url),("Conserva i veicoli","Prima di lasciare un’auto speciale, verifica che sia registrata e che esista un posto libero.","Il veicolo risulta registrato e il garage utilizzabile.",PROPERTIES)))
    body+='<p class="vc-check">Questo garage non sostituisce gli otto acquisti del trofeo Little Boxes. Nessun veicolo speciale incluso risulta confermato dalle fonti consultate.</p>'
    return body+end(base,[("PowerPyx — garage automatici",GARAGES),("GTABase — proprietà e mappa",map_url)],'<p>'+internal(base,STORY,"Tutti i quattro garage della storia")+'</p>')
def pages(base):
    result=[(PATH,"Garage gratuiti GTA VI: sette sblocchi, codici e ricompense","Guida ai garage gratuiti GTA VI: Southside Storage, Domestic Timbers, Del Rio e ricompense della storia. Distinzione Little Boxes.",index_body(base),"CollectionPage"),
            (SOUTH,"Southside Storage GTA VI: 5 murales e 1010 Cheetah","Sblocca il garage di Salton e la 1010 Cheetah: cinque posizioni, codice 1010 e registrazione del veicolo.",south_body(base),"Article"),
            (DOMESTIC,"Domestic Timbers GTA VI: garage e Tempesta di Randy","Catena di Randy dal Key Cloner a Collect the Tempesta: garage gratuito, trofeo e costi indicativi.",domestic_body(base),"Article"),
            (STORY,"Garage gratuiti GTA VI: tutti gli sblocchi della storia","Port Gellhorn, Thompson Court, NE 15th Street e Pegassi Residences: missioni di sblocco e posti.",story_body(base),"Article")]
    for row in STORY_ROWS:
        ident,name,chapter,mission,area,spots=row
        result.append((STORY+ident+"/",name+" Garage GTA 6: posizione e sblocco","Garage gratuito in "+area+": completa "+mission+" nel Capitolo "+chapter+". Capienza: "+str(spots)+".",story_detail(base,row),"Article"))
    return result
