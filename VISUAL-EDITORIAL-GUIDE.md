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

Scuro e' il tema predefinito anche con sistema operativo chiaro. Il lettore puo' scegliere Scuro o Chiaro nella barra superiore. La preferenza e' locale al browser (`gta6-theme-v1`), indipendente dagli spoiler. Il tema viene applicato prima dei fogli di stile per evitare un iniziale sfondo bianco durante la navigazione. Se la memoria del browser non e' disponibile, il cambio resta utilizzabile nella pagina ma non viene promesso il salvataggio della scelta.

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
