# GTA 6 Italia: struttura visiva ed editoriale

## Il sito reale, non i mockup

Il sito e' implementato in HTML/CSS/JavaScript. Il workflow di produzione esegue ora `python reader_experience.py --build`: non pubblicare soltanto il risultato del vecchio generatore, altrimenti tema e approfondimenti vengono persi.

- `build_site.py` mantiene le pagine e i contenuti precedenti.
- `build_visual_site.py` applica la navigazione e genera home, categorie e tutorial visivi.
- `reader_experience.py --build` richiama il generatore visivo, concilia i dettagli editoriali ricontrollati e applica tema, controlli di lettura e approfondimenti all'HTML finale.
- `visual_guide_content.py` gestisce titoli pubblici senza spoiler, introduzioni, requisiti e associazioni fra passaggi e immagini.
- `data/visual_guides.json` contiene le nuove guide originali in italiano con fonti.
- `data/visual_media.json` contiene immagini selezionate: URL, fonte, attribuzione, testo alternativo, didascalia e distinzione fra schermata e materiale promozionale.
- `data/guide_extras.json` contiene consigli, errori da evitare e curiosita' documentate, con fonte per ogni nota, data di verifica e classificazione spoiler esplicita.
- `prepare_visual_media.py` prepara varianti WebP da 480 e 960 pixel, senza copiare indiscriminatamente gli articoli.
- `visual-v2.css/js` e `reader-theme.css/js` sono gli asset del sito; hash negli URL aggiornano la cache dopo le modifiche.

## Tema e lettura notturna

Per impostazione attuale il tema e' scuro su mobile (fino a 760 px) e chiaro su desktop; una scelta manuale del lettore prevale e persiste durante la navigazione. Il lettore puo' scegliere Scuro o Chiaro nella barra superiore. La preferenza e' locale al browser (`gta6-theme-v1`), indipendente dagli spoiler. Il tema viene applicato prima dei fogli di stile per evitare un iniziale sfondo bianco durante la navigazione. Se la memoria del browser non e' disponibile, il cambio resta utilizzabile nella pagina ma non viene promesso il salvataggio della scelta.

Le schermate di gioco mantengono i colori originali: non applicare inversioni, filtri o oscuramenti alle immagini operative. Lo zoom nella pagina serve a leggere mappe e menu; non crea dettaglio che manca nell'immagine originale. Il dialogo si chiude con Chiudi o Esc e conserva la fonte dell'immagine.

## Struttura delle guide

Una guida parte dall'obiettivo, non da un'introduzione generica. Ordine: risposta pratica, requisiti, dove andare, mappe pertinenti quando disponibili, azioni numerate, controlli di riuscita documentati, consigli contestuali, rischi, fonti in fondo e percorsi correlati.

Ogni immagine deve aiutare a riconoscere una posizione, un menu, un oggetto o un'azione. Le immagini promozionali sono dichiarate e non costituiscono prova del passaggio. Una schermata mancante non va sostituita con una mappa, un'interfaccia o una ricompensa generata.

Il testo resta leggibile senza JavaScript e gli spoiler rimangono apribili con i controlli nativi. Le immagini sotto la prima schermata sono caricate in modo differito. Le mappe vanno raggruppate vicino alle istruzioni di posizione, con didascalie e apertura ingrandita; evitare duplicati decorativi.

## Standard fotografico: cinque immagini contestuali quando disponibili

L'obiettivo di qualita' e' **almeno cinque immagini uniche, pertinenti e verificabili per guida**, senza duplicati decorativi. L'ordine consigliato per un tutorial con posizione e' (1) mappa autentica del punto, (2) ingresso o riferimento in gioco, (3) azione/controllo o menu, (4) risultato o bottino, (5) conferma finale/salvataggio. Per le altre guide adattare il percorso visuale all'azione reale, senza inventare mappe o screenshot.

- Annotare fonte precisa, credito, testo alternativo descrittivo, didascalia e classificazione spoiler per ogni immagine.
- Le immagini promozionali non sostituiscono mappe o schermate di gameplay e non dimostrano un punto della mappa.
- Pubblicare solo media locali ottimizzati che siano stati scaricati e verificati. Vietati hotlink remoti nei tutorial: se il download fallisce mostrare un messaggio con link alla fonte e non l'icona di immagine rotta.
- Se meno di cinque immagini pertinenti sono disponibili o riutilizzabili appropriatamente, mantenere la guida utile con i riferimenti esistenti, segnalare la lacuna nel report e non creare contenuti fittizi.
- La copertura effettiva e' verificata in _site/media-quality.json dal test media_quality_v1.py. Lo stato needs_more_verified_images genera un debito editoriale, non una certificazione di copertura.
- Priorita' di ricerca e aggiornamento: soldi iniziali, posizioni precise sulle mappe, auto rare, registrazione e salvataggio veicoli.

## Consigli e curiosita'

Inserire una nota solo quando aggiunge qualcosa rispetto ai passaggi principali. Tipi previsti: `tip` (consiglio utile), `avoid` (errore da evitare), `curiosity` (dettaglio interessante). Non aggiungere paragrafi riempitivi per avere una curiosita' in ogni pagina.

Ogni nota deve avere titolo, testo originale in italiano, fonte esatta, data di controllo e classificazione spoiler. Il riferimento numerato rimanda alla fonte in fondo alla guida. Non trasformare supposizioni, commenti isolati o titoli di feed in fatti verificati. Se una nuova fonte corregge il procedimento principale, correggere anche quel procedimento: non lasciare due istruzioni contraddittorie nella stessa pagina.

La prima raccolta aggiunge nove note in cinque guide. La galleria usa risorse gia' selezionate: questo aggiornamento non aumenta il numero di immagini uniche e non certifica tutte le posizioni mancanti.

## Spoiler

- I dettagli sensibili partono chiusi con elementi HTML `details`.
- La barra chiede al lettore se mostrare o nascondere gli spoiler.
- La preferenza e' conservata solo nel browser con la chiave `gta6-spoilers-v2`.
- Tema e spoiler sono scelte separate: cambiare colore non deve rivelare contenuti.
- Titoli, descrizioni, copertine e anteprime pubbliche non devono rivelare dettagli protetti.
- Mappe, consigli e curiosita' sensibili devono stare dentro il pannello. Gli eventuali collegamenti interni di apertura devono indicare chiaramente `(spoiler)`.

## Revisione delle segnalazioni: Buffer Community (senza nuove API)

La funzione **Proponi uno screenshot** apre un tweet dall'account del lettore contenente `@xFederiko11`, il permalink della guida e `#GTA6Italia`. Per recuperare eventuali contributi, il gestore puo' aprire [Buffer Community](https://community.buffer.com/) o la sezione **Community** dall'app Buffer, selezionare il canale X connesso e la scheda **Mentions**. In base alla [documentazione ufficiale Buffer](https://support.buffer.com/en-us/articles/using-community-on-the-buffer-mobile-app-mCNla9C1We), le menzioni X sono disponibili anche nella Community mobile; per X la lettura e gestione dei commenti **non e' disponibile via API Buffer**: [limiti dell'API](https://support.buffer.com/articles/what-is-buffers-api-GtIYIQilz5).

I contributi restano quindi da verificare manualmente. Non promettere uno scanner automatico delle menzioni, una raccolta certa degli allegati o la ripubblicazione dei media. Quando un lettore offre uno screenshot, verificare che sia suo, chiedere consenso esplicito e registrare la fonte prima di ottimizzare e inserire l'immagine. La scheda Community e' utile anche per rispondere alle domande sulle guide senza obbligare i visitatori ad accedere a GitHub.

## Da una scoperta a una guida italiana

1. Aprire la fonte originale e registrare cosa documenta, distinguendo piattaforma, patch e data quando disponibili. Il titolo di un feed non certifica il contenuto.
2. Confrontare riscontri indipendenti per affermazioni importanti. Non contare siti che riprendono lo stesso video come verifiche indipendenti.
3. Scrivere una sintesi operativa originale in italiano, senza inventare pulsanti, coordinate, tempi, ricompense o condizioni di spawn.
4. Distinguere funzionalita' normale ed exploit. Una guida non certifica automaticamente la compatibilita' con i trofei.
5. Selezionare immagini pertinenti con una base di riutilizzo appropriata, conservando provenienza e attribuzione. La reperibilita' online non e' una licenza generale.
6. Inserire dati, immagini e consigli verificati; classificare tutti gli spoiler e generare la pagina prima di promuoverla.
7. Eseguire i test sul risultato effettivo e verificare il link pubblico dopo il deploy.
8. Solo dopo il deploy rendere il contenuto eleggibile per il bot, conservando anti-duplicazione e regole editoriali. Nessun retry cieco di post dall'esito incerto.

Questa procedura non significa che il feed crei, verifichi e pubblichi nuove guide senza revisione.

## SEO e verifiche

Conservare gli indirizzi delle guide esistenti. Ogni pagina deve avere un H1, titolo, descrizione, canonical, dati strutturati coerenti, collegamenti interni validi e data di aggiornamento derivata dai sorgenti, non solo dall'orario del deploy. Non inventare visite, classifiche o test personali.

```sh
python -m unittest -q test_site.py test_community_feed.py test_related_research.py test_guide_source_validation.py
python prepare_visual_media.py
python reader_experience.py --build
python -m unittest -q test_visual_site.py test_reader_experience.py
python test_reader_experience.py --browser
```

Il controllo reader usa otto pagine a 320, 390, 768 e 1440 pixel in entrambi i temi, verifica ricaricamento e persistenza, assenza di overflow, ricerca, spoiler, zoom, JavaScript disabilitato e memoria locale non disponibile. Se un controllo fallisce, il deploy non prosegue. La produzione controlla anche gli indirizzi pubblici e i marker del tema dopo la pubblicazione.

## Limiti espliciti

Il catalogo visivo contiene dieci tutorial e tredici immagini selezionate. Non ogni passaggio ha una schermata o una posizione verificata. Dove manca il materiale resta il riferimento alla fonte: nessun punto sulla mappa inventato. Tema e contenuti del sito non modificano automaticamente coda o frequenza dei post Buffer/X.


## Raccolta di schermate originali dalla community (X)

Ogni guida visiva espone un piccolo invito **Proponi uno screenshot** collegato alla conversazione su **X**; non richiede un account GitHub né permette di caricare file direttamente sul sito. I cinque esempi sono gestiti da `data/visual_requests.json` e sono **richieste editoriali**, non cinque prove o cinque immagini già disponibili. L'aggiornamento non deve modificare il conteggio del controllo `media_quality_v1.py`.

Flusso previsto: il lettore cattura una schermata PS5 con **Crea (Create)**, apre X tramite l'intent col permalink della guida, allega la propria immagine **manualmente**, specifica piattaforma/patch e avvisa degli spoiler. Il bot non legge messaggi privati X, non invia post per conto degli utenti e non registra automaticamente i media ricevuti.

Un'immagine segnalata diventa candidabile **solo dopo revisione umana**: correttezza dell'immagine rispetto al passaggio/patch, provenienza, titolarità e autorizzazione esplicita alla ripubblicazione, didascalia/alt text, spoiler, ottimizzazione locale e nuovo audit. Il tweet pubblico da solo **non concede** diritti di ripubblicazione; i crediti da soli non sostituiscono il consenso.

L'invito è un canale di partecipazione e può aumentare le conversazioni sul nostro X, ma **non dimostra nuovi follower, numero di invii o licenze**. Le 50 richieste restano aperte finché non esistono le rispettive immagini autentiche. Gli utenti possono interagire solo se lo desiderano, senza registrarsi al portale.


## Tracciamento fotografico per passaggio (20 novembre 2026)

La sezione **Contribuisci con immagini** di tutte le undici guide mostra ora il numero reale di **schermate gameplay locali presenti nei passaggi e nella galleria** rapportato all'obiettivo di cinque. Una foto promozionale Rockstar, un video YouTube, un link a una mappa esterna, una schermata mancante o un'immagine non scaricata non aumenta il contatore. Il conteggio non certifica il diritto di ripubblicazione: la provenienza e l'autorizzazione di ogni foto vanno valutate prima del riuso.

- La galleria originale del Reader può spostare le immagini davanti ai passaggi; ciascun passo conserva ora un rimando alla galleria e il conteggio viene ricalcolato **dopo** questo spostamento, sulla pagina finale pubblicata.
- Una piccola nota `Screenshot del passaggio non ancora disponibile` appare nel passo che non ha una schermata di gameplay associata, senza coprirne le istruzioni. Il link raggiunge la sezione delle richieste.
- Il pannello dettagliato rimane chiuso per impostazione predefinita perché le cinque richieste possono rivelare luoghi o oggetti della storia. Dentro, ogni richiesta ha un link X distinto con ruolo fotografico, URL canonico della guida e hashtag, pronto per allegare manualmente la foto. I cinque ruoli **non sono assegnati automaticamente a passaggi numerati**, per evitare di indicare un'immagine come prova di un passaggio differente.
- Il pulsante X generale resta disponibile, ma **non invia** un'immagine. Il tracciamento Umami `x-screenshot-intent` registra solo il clic sull'apertura della bozza (se consentito dal browser), mai un contributo effettivamente ricevuto, un follower o il permesso di pubblicare.
- `media_quality_v1.py` espone `real_step_screenshots`, `promotional_images`, `gameplay_screenshots_in_steps` e lo stato `needs_more_verified_images`; cinque screenshot distinti sono indispensabili per `target_met`. La metrica legacy `unique_real_images` resta per compatibilità ma **non** include automaticamente il criterio editoriale.
- Il risultato test viene verificato in entrambi i temi e su mobile, senza creare nuove immagini, punti mappa, premi o mappe ipotetiche. I contributi della community devono essere valutati e autorizzati manualmente prima di poter accrescere la copertura.

---

## Video di gameplay verificabili e mappe (20 novembre 2026)

Le guide iniziali possono mostrare un blocco **Fonti visive**, immediatamente prima della procedura, con un link alla categoria reale della mappa GTABase e/o un video YouTube con minuti specifici. Le associazioni fra guida, video, capitoli, timestamp, autore e fonte della cronologia sono curate in `data/guide_visual_refs.json`.

- I video del creator TGG sono riferimenti **non ufficiali**; il player `youtube-nocookie.com` viene creato dal JavaScript **solo dopo il clic esplicito del lettore**. In assenza di JavaScript resta il link diretto YouTube già impostato al minuto utile.
- Per il negozio Three Sheets Liquor, il filmato di TGG documentato da Trari contiene i punti 4:45 (arrivo al negozio) e 7:35 (pappagallo). Non dimostra gli altri tre luoghi dell'articolo sui soldi.
- Per la registrazione auto iniziale, il video di TGG pubblicato il 19 novembre è collegato ai punti 4:26 (tracker spiegati da Moses) e 11:15 (Dinka Blista e registrazione). Va distinto dallo sblocco più tardo dei Pay 'n' Spray.
- Le mappe GTABase filtrate per `liquor-store`, `vehicle-mod-shop` e `garages` **non** sono screenshot della nostra guida, né pin sempre precisamente equivalenti. Il testo specifica il luogo e i limiti. Non inserire coordinate, marcatori o immagini di mappe inventate.
- I video sono embeddati tramite il player **originale**; nessuna copia, ripubblicazione, screenshot o miniatura esterna viene memorizzata. Gli utenti possono aprire direttamente YouTube se l'embed è bloccato. I minuti provengono dalla cronologia di fonte e non rappresentano test manuali effettuati da ChatGPT.
- I video e le mappe **non contano** come le cinque schermate autentiche desiderate per guida: `media_quality_v1.py` continua a misurare esclusivamente immagini locali con attributi reali.

### Passaggi di sicurezza migliorati per la prima auto

Non iniziare dai Pay 'n' Spray generici: nel **Capitolo 2** la prima registrazione è durante Moses a Watkins Auto Parts (Port Gellhorn) dopo *Girl's Trip*. Si controllano i tracker con WAiNK, si ottiene lo Slim Jim, si prende un'auto senza tracker, la si rivernicia e si sceglie Register. Solo dopo vengono sbloccati ulteriori strumenti e officine. Le prove raccolte sono [PowerPyx](https://www.powerpyx.com/gta-6-moses-take-a-vehicle-to-moses-walkthrough/) e [GTABase](https://www.gtabase.com/gta-6/articles/how-to-unlock-garages-in-gta-6). Non inventare disponibilità di funzionalità o costi fuori dal contesto della storia.

Le missioni **Get Shirley's Rum** e **Steal the Scooter** sono mancabili nel Capitolo 1, ma PowerPyx indica che **non sono richieste per trofei o 100%**: chiarirlo sulle guide permette di scegliere senza allarmismi chi punta al platino.


## Checklist meditazioni e protezione del platino — 20 novembre 2026

La guida pubblica `guide-e-tutorial/meditazione-capitolo-1/` include un pannello accessibile **10 luoghi / 18 meditazioni**. Il catalogo `data/meditation_checklist_v1.json` riprende i nomi e i riferimenti geografici attestati da [PowerPyx](https://www.powerpyx.com/gta-6-all-meditation-spot-locations/), con una fonte aggiuntiva di [Push Square](https://www.pushsquare.com/guides/gta-6-meditation-locations). Nessun marcatore mappa è inventato e nessuna immagine protetta è copiata: le mappe e schermate originali sono apribili via link.

- **10 luoghi, 18 sessioni**: Jason's House vale una sessione iniziale; gli otto luoghi centrali si segnano separatamente con Jason e con Lucia; Ascent Mountain vale una singola sessione conclusiva. La checklist contiene esattamente 18 caselle.
- **100% = 15/18**: non confondere la checklist del 100% con i requisiti del trofeo `Positive Mental Attitude`, per cui conviene fare ogni luogo. Il requisito effettivo della prima meditazione sul balcone per il trofeo **non è ancora accertato**: mantenere l'etichetta di incertezza. Il balcone è definitivamente mancabile dopo il Capitolo 1; completarlo con Lucia prima di avanzare.
- **Sblocco**: dopo `Coffee Break` nel Capitolo 2 puoi segnare i luoghi centrali con entrambi i personaggi. La meditazione finale su Mount Kalaga compare soltanto dopo le altre, da verificare direttamente nella mappa del gioco.
- **Salvataggio esclusivamente locale**: i dati del pannello sono salvati nella chiave browser `gta6-meditations-v1`; il reset esplicito richiede conferma. Nessuna chiamata PSN, nessuna sincronizzazione fra dispositivi, nessuna raccolta server di sessioni o progressi. In modalità JavaScript disabilitata, le caselle restano visibili ma il conteggio dinamico non funziona.
- **Test**: `test_meditation_tracker_v1.py` controlla schemi, fonti e stabilità; `test_visual_site.py` testa l'HTML pubblicato; `test_reader_experience.py --browser` verifica le caselle su telefono, il ricaricamento e l'azzeramento.
- Le nuove spunte non rappresentano schermate di gioco né aumentano `media-quality.json`. Quando non ci sono screenshot originali autorizzati, mostrare soltanto i collegamenti alle fonti.

La priorità è che nessuno perda una componente eventualmente necessaria al platino per una nostra guida troppo vaga: evitare formulazioni che promettono **Trophy Safe** quando il criterio non è stato verificato.


## Scoperta Reddit: glitch prima persona PS5 · 20 novembre 2026

- Nuova guida: `guide-e-tutorial/glitch-prima-persona-ps5/`; segnalazione bot [Issue #77](https://github.com/xFederiko11/federiko-gta-playstation-bot/issues/77), post originale [r/GTA6](https://www.reddit.com/r/GTA6/comments/1y15kfv/).
- Riscontri tecnici indipendenti: [VGC](https://www.videogameschronicle.com/guide/gta-6-first-person-mode-glitch-grand-theft-auto/), [PC Gamer, prova autonoma](https://www.pcgamer.com/games/grand-theft-auto/gta-6-is-playable-in-first-person-heres-how-to-activate-it/), [Dexerto](https://www.dexerto.com/gta/gta-6-glitch-lets-players-access-first-person-mode-3430025/) e la discussione [r/gtaglitches](https://www.reddit.com/r/gtaglitches/comments/1y0ude9/gta_6_enter_first_person_view/). Distinguere i racconti comunitari da test effettuati dalla redazione. Il video originale è di oneboyler, attribuzione della scoperta a Kackalack secondo Reddit.
- Stato alla data: **🟡 Probabilmente funzionante** su versioni di lancio PS5/PS5 Pro; versione specifica della patch **non documentata**. **⚠️ Trophy Status Uncertain**: il glitch non è la scelta principale per chi protegge il platino. Prima un **salvataggio manuale separato**. Nessun guadagno di soldi o XP; solo visuale.
- Metodo documentato: `Settings > Controller > Touch Pad Button > Camera (2/2)`; entra al volante; telefono con ↑; riponilo con ○ e premi ripetutamente il touchpad mentre il telefono scompare. Se la camera rimane in prima persona, l'effetto è riuscito. Per tornare, ricarica un salvataggio; cambio abito o personaggio è una segnalazione community, non garantita.
- La guida include il video originale YouTube caricato soltanto dopo il clic (o link diretto), **non** un download, fotogramma copiato o immagine di gameplay prodotta artificialmente. Il target immagini aumenta da **10 a 11 guide**; non inventare cinque screenshot per raggiungerlo.
- Il nostro bot **non** deve fare auto-reply su Reddit/X o dichiarare un exploit «trophy safe» perché è stato citato in un thread. Citare la fonte e la data nei futuri post.


## Fotogrammi dei creator e anteprime social (25 novembre 2026)

- Accettare solo gameplay: escludere webcam, volti reali, inserti live action e dati personali. Il revisore conferma esplicitamente `gameplay_only` e `no_real_people`. Non e' riconoscimento automatico dei volti.
- Per un fotogramma di un video, ottenere un file fornito dal creator e un permesso documentato per sito e social, conservando le prove richieste dal registro e il video ID con secondo esatto. Non scaricare o ritagliare video pubblici automaticamente. Verificare anche i diritti del gioco e le condizioni delle piattaforme.
- Selezionare al massimo una foto approvata per guida mediante `social_preview: true`; il resto resta nei passaggi. Il generatore delle anteprime controlla che l'immagine compaia davvero nella pagina e che i byte WebP pubblicati corrispondano al SHA-256 approvato. Compone una card 1200x630 con immagine intera, credito leggibile e titolo, senza ritagliare menu o mappa. Mantiene l'URL JPG stabile per Buffer e Open Graph.
- Se non esiste una foto approvata e selezionata, resta la copertina grafica originale (o la selezione promozionale esplicita gia' prevista per gli articoli editoriali). Nessun fotogramma o fotografia nuova viene aggiunta in questa modifica. Nessuna licenza e' presunta.


## Controllo dei filmati e riferimenti visivi (25 novembre 2026)

Il workflow esistente usa l'endpoint ufficiale YouTube oEmbed per i quattro ID curati, senza download di filmati o miniature. Il riepilogo di Actions distingue metadati coerenti, creator da ricontrollare, risposta limitata e verifica non conclusiva. Non certifica playback, timestamp, disponibilita' geografica, licenza o correttezza del gameplay. Nessun errore del provider deve cancellare una guida o bloccare il deploy. Il sito dichiara esplicitamente il limite.

Per la selezione di riferimenti visivi: filmati originali, da incorporare al minuto documentato senza scaricare autonomamente i fotogrammi:
- TGG: canale ufficiale https://www.youtube.com/@TGG_ ; prima auto, video R0GdEkPZSvM, 4:26 e 11:15; Three Sheets Liquor, video 1GtrjKhSwzM, 4:45 e 7:35. I riferimenti temporali provengono dal registro, non da riproduzione indipendente.
- IGN: sei consegne di Moses, video UyxxY0A_kow, capitoli 01:41, 03:11, 04:53, 05:46, 07:08, 08:40.
- oneboyler: dimostrazione prima persona, video CJi2DWXxsoQ, fotogramma da selezionare dopo visione effettiva.
- Diritto sottostante del gioco: https://support.rockstargames.com/articles/7bNaeoMFTV0iUDGhStTXvz/policy-on-posting-copyrighted-rockstar-games-material . La tolleranza per uso fan occasionale e non commerciale non e' una licenza generale per una pubblicazione digitale sistematica. Il registro deve contenere anche una base valida per l'uso dei contenuti Rockstar.

Decisione del titolare del progetto, 25 novembre 2026: non inviare email di richiesta a Rockstar, Take-Two o ai creator. Nessun contatto esterno o risposta X automatica per ottenere immagini. Privilegiare embed ufficiali, link ai minuti pertinenti e immagini con base di riuso gia' documentata, senza presumere licenze dalla visibilita' pubblica o dalla sola citazione della fonte. Nessun costo aggiuntivo. Nessun consenso ricevuto; il registro approvato resta invariato.


## WAiNK — criterio visivo mobile del 25 novembre 2026

Il video dedicato precede i prerequisiti: niente doppio blocco introduttivo. Cinque schemi originali spiegano i comandi e il risultato senza simulare l'interfaccia del gioco; non contano come screenshot autentici. Collegamento alle schermate reali del sito fonte e al video originale. Test browser sul primo viewport a 390px, caricamento del file immagine, apertura e chiusura del player e articolo intero. Nessun contatto esterno.


## Articoli lineari e copertina condivisa

Dal 25 novembre 2026 i tutorial numerati sono interamente leggibili nella stessa pagina, senza pulsanti avanti/indietro, modalità di lettura o blocchi dei passaggi. Restano opzionali spoiler, approfondimenti e attivazione dei video. Tutti gli articoli effettivi hanno sotto H1 la stessa copertina JPEG 1200x630 usata da og:image, twitter:image e dal bot, con fonte dove applicabile. I diagrammi originali di copertina sono tematici e non screenshot; si privilegiano foto autentiche già approvate e pertinenti. Homepage, directory e strumenti di servizio non ricevono copertine ridondanti. Non modificare URL canonici o contratti delle social-card.

I percorsi dei collezionabili seguono lo stesso principio: tutti i 123 checkpoint visibili per impostazione predefinita; ricerca, filtri e spunte locali facoltative, link rapidi ai mancabili e alle copie legate ai capitoli. La copertina resta visibile. Nessun conteggio PSN simulato; nessuna posizione o mappa aggiunta senza fonte.

Revisione visiva delle catture QA #45635784695: la guida WAiNK è lineare; su alcune altre pagine la vecchia foto decorativa cinematografica precedeva H1 e duplicava la copertina. La fase social-card rimuove soltanto quel banner decorativo dagli articoli e usa il titolo H1 nella copertina; non rimuove media operativi o le foto dalle pagine indice. URL e metadati SEO restano stabili.
