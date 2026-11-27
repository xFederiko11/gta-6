"""Two independent, source-reviewed legitimate gameplay articles."""
from html import escape
from garage_guides_v1 import facts, steps, internal, ref

CLONER="guide-e-tutorial/key-cloner/"
SELL="guide-e-tutorial/vendere-veicoli/"
P_CLONER="https://www.powerpyx.com/gta-6-how-to-get-key-cloner/"
P_MISSION="https://www.powerpyx.com/gta-6-clonin-keys-makin-gs-steal-the-zorrusso-for-randy-walkthrough"
G_CLONER="https://www.gtabase.com/gta-6/articles/how-to-get-key-cloner-in-gta-6-to-steal-keyless-cars"
G_SELL="https://www.gtabase.com/gta-6/articles/how-to-sell-cars-and-other-vehicles-in-gta-6"
P_MONEY="https://www.powerpyx.com/gta-6-money-guide-how-to-get-money-fast/"
G_MISSION="https://www.gtabase.com/gta-6/missions/steal-the-zorrusso-for-randy"
G_COMPANION="https://www.gta-companion.com/guides/key-cloner"

ARTICLES=(
 (CLONER,"Key Cloner GTA 6: come sbloccarlo e rubare auto senza chiave",
  "Nel Capitolo 3 completa la missione di Randy: installazione sul telefono, Granforma Zorrusso, minigioco e consegna."),
 (SELL,"Come vendere auto e veicoli in GTA 6: Moses, Randy e Pay ’n’ Spray",
  "Quando si sblocca la vendita, dove andare e quali tracker impediscono di vendere un veicolo: guida legittima per PS5."),
)
def start(base,title,desc):
    return ('<article class="vc-article" data-legit-guide><nav class="vc-crumb" aria-label="Percorso">'+
            internal(base,"guide-e-tutorial/","Guide e tutorial")+'</nav><section class="vc-article-hero"><span class="vc-eyebrow">GTA VI · GUIDA LEGITTIMA · PS5 / PS5 PRO</span><h1>'+escape(title)+'</h1><p>'+escape(desc)+'</p><p>Fonti indipendenti consultate il 27 novembre 2026. Possibili spoiler di missione; versione della patch e prova diretta non accertate.</p></section>')
def finish(base,refs,related):
    return ('<section class="vc-source"><h2>Fonti e immagini originali</h2>'+''.join(ref(u,n+" ↗") for n,u in refs)+
            '<p>Le schermate e le mappe delle guide sono consultabili presso i rispettivi autori. Nessuna copia di screenshot, video o coordinate non verificate.</p></section><nav class="vc-related" aria-label="Guide correlate"><h2>Continua con</h2>'+
            ''.join(internal(base,p,n) for n,p in related)+'</nav></article>')
def cloner_body(base):
    body=start(base,*ARTICLES[0][1:])
    body+=facts([("Prerequisito","Capitolo 3, dopo Crosstown Traffic"),("Missione","Clonin’ Keys, Makin’ GS"),("Luogo","Hathaway Apartments, Ocean Beach"),("Risultato","Key Cloner sul telefono e lista di Randy")])
    body+=steps((
      ("Raggiungi il parcheggio","Segui il segnale della missione fino agli Hathaway Apartments ed entra nell’area di parcheggio indicata.","Inizia l’incarico per Randy.",P_MISSION),
      ("Installa Key Cloner","Apri il telefono e segui la richiesta di installazione durante la missione.","L’app è disponibile; lo sblocco riguarda Jason e Lucia.",P_CLONER),
      ("Trova la Granforma Zorrusso","Cerca l’auto indicata al piano terra, sul lato est del parcheggio.","Il modello corrisponde all’obiettivo.",G_MISSION),
      ("Clona la chiave","Avvicinati all’auto, attiva il Key Cloner e segui il minigioco con lo stick destro quando il segnale è rosa.","Il gioco conferma l’apertura; puoi entrare.",G_CLONER),
      ("Consegna la Zorrusso","Guida verso il concessionario indicato. Segui il segnale del tracker e gli obiettivi della missione; non presumere che l’auto sia già tua.","Randy accetta la consegna.",P_MISSION),
      ("Controlla la lista","Parla con Randy e verifica la disponibilità delle richieste successive nel menu.","Key Cloner resta disponibile e puoi consultare Randy’s Wish List.",G_COMPANION),
    ))
    body+='<p class="vc-check">Lo sblocco del Key Cloner è previsto dalla storia. Il trofeo Supply &amp; Demand richiede la successiva catena di Randy, non la sola installazione. Non confondere accesso all’auto con registrazione o vendita.</p>'
    return body+finish(base,[("PowerPyx — Key Cloner",P_CLONER),("PowerPyx — missione",P_MISSION),("GTABase — sblocco",G_CLONER),("GTA Companion",G_COMPANION)],[("Vendere veicoli",SELL),("Lista di Randy","guide-e-tutorial/sportive-randy-posizioni/"),("Domestic Timbers","garage-gratuiti/domestic-timbers/"),("Scanner WAiNK","guide-e-tutorial/scansionare-veicoli/")])
def sell_body(base):
    body=start(base,*ARTICLES[1][1:])
    body+=facts([("Capitolo 2","Moses, dopo Girls’ Trip: veicoli senza tracker"),("Capitolo 3","Pay ’n’ Spray dopo Welcome to Vice City: tracker standard"),("Auto avanzate","Randy, dopo Key Cloner; vendita generica dopo Dale Mamba e notifica; capitolo discusso"),("Ricavo","Dipende dal veicolo e dalle condizioni; controlla il prezzo in gioco")])
    body+=steps((
      ("Scansiona il veicolo","Apri WAiNK e controlla il tipo di tracker prima di scegliere il punto vendita.","Sai se il veicolo è senza tracker, standard o avanzato.",G_SELL),
      ("Vendi a Moses","Dopo lo sblocco nel Capitolo 2, porta un veicolo senza tracker da Moses e usa la voce di vendita nel dialogo.","Verifica che il pagamento sia accreditato.",G_SELL),
      ("Usa Pay ’n’ Spray","Dopo Welcome to Vice City, cerca il servizio Vendita nell’officina. Per i tracker standard controlla che l’opzione sia disponibile.","Il menu propone il prezzo; conferma soltanto se vuoi cedere l’auto.",G_SELL),
      ("Segui Randy per le auto di fascia alta","Sblocca Key Cloner e consegna le auto richieste. Per vendere genericamente quelle con tracker avanzato, PowerPyx colloca Dale Mamba nel Capitolo 3 dopo alcune consegne, mentre GTABase indica Photo/Shoot nel Capitolo 4. Segui il contatto effettivo di Randy e, dopo la consegna della Mamba GT, aspetta la notifica di sblocco. Non garantiamo il capitolo.","Il servizio di vendita accetta la categoria; non dare per scontato un numero fisso di consegne.",G_SELL),
      ("Gestisci il limite e la collezione","Se il gioco blocca ulteriori vendite, attendi un nuovo giorno di gioco. Conserva prima le varianti rare che desideri registrare.","Controlla saldo, garage e disponibilità del servizio prima di ripetere.",P_MONEY),
    )).replace("Come sbloccarlo:","Come vendere:").replace('data-garage-step=','data-legit-step=')
    body+='<p class="vc-check">Non vendere auto speciali potenzialmente mancabili se vuoi collezionarle. La vendita non equivale a registrare un’auto. Aerei e imbarcazioni non rientrano nel servizio descritto. Nessun glitch o ricavo garantito.</p>'
    return body+finish(base,[("GTABase — vendita e tracker",G_SELL),("PowerPyx — guadagni",P_MONEY)],[("Sbloccare Key Cloner",CLONER),("Scanner WAiNK","guide-e-tutorial/scansionare-veicoli/"),("Registrare un veicolo","salvare-auto/"),("Garage gratuiti","garage-gratuiti/")])
def pages(base):
    for (path,title,desc),renderer in zip(ARTICLES,(cloner_body,sell_body)):
        yield path,title,desc,renderer(base)

def links(base):
    return '<section class="vc-related" aria-label="Guide per auto e guadagni"><h2>Altre guide legittime</h2>'+''.join(internal(base,path,title) for path,title,_ in ARTICLES)+'</section>'
