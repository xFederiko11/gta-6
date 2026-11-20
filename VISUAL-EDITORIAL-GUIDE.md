# GTA 6 Italia: struttura visiva ed editoriale

## Il sito reale, non i mockup

La versione `visual-v2-20261120` e' implementata in HTML/CSS/JavaScript. Il workflow di produzione esegue `build_visual_site.py`, non soltanto il vecchio `build_site.py`.

- `build_site.py` mantiene pagine e contenuti precedenti.
- `build_visual_site.py` applica la nuova navigazione a tutte le pagine e genera home, categorie e tutorial visivi.
- `visual_guide_content.py` gestisce titoli pubblici senza spoiler, introduzioni, requisiti, riferimenti e associazioni fra passaggi e immagini.
- `data/visual_guides.json` contiene nuove guide originali in italiano con fonti.
- `data/visual_media.json` contiene solo immagini selezionate: URL, fonte, attribuzione, testo alternativo, didascalia e distinzione tra schermata e materiale promozionale.
- `prepare_visual_media.py` prepara varianti WebP da 480 e 960 pixel. Non esegue una copia indiscriminata degli articoli.
- `site/assets/visual-v2.css` e `visual-v2.js` sono gli asset del nuovo sito. Il loro hash viene aggiunto agli URL per aggiornare la cache dopo le modifiche.

## Struttura delle guide

Una guida parte dall'obiettivo, non da un'introduzione generica. Ordine: risposta pratica, requisiti, dove andare, azioni numerate, controlli di riuscita documentati, rischi, fonti in fondo e percorsi correlati.

Ogni immagine deve aiutare a riconoscere una posizione, un menu, un oggetto o un'azione. Le immagini promozionali sono dichiarate e non devono essere presentate come prova del passaggio. Una schermata mancante non va sostituita con una mappa, un'interfaccia o una ricompensa generata.

Le schermate nel tutorial sono ingrandibili. Il testo resta leggibile senza JavaScript. Il caricamento delle immagini sotto la prima schermata e' differito; dimensioni e varianti responsive riducono il peso e gli spostamenti del layout.

## Spoiler

- I dettagli sensibili partono chiusi con elementi HTML `details`.
- La barra chiede al lettore se mostrare o nascondere gli spoiler.
- La preferenza viene conservata solo nel browser con la chiave `gta6-spoilers-v2`.
- Titoli, descrizioni, copertine e anteprime pubbliche non devono rivelare i dettagli che il pannello protegge.
- Le mappe e le immagini di luoghi sensibili devono stare dentro il pannello, non nella copertina pubblica.

## Da una scoperta a una guida italiana

1. Aprire la fonte originale e registrare cosa documenta davvero, distinguendo piattaforma, patch e data quando disponibili. Il titolo di un feed non certifica il contenuto.
2. Confrontare riscontri indipendenti per affermazioni importanti. Non sommare siti che riprendono lo stesso video come verifiche indipendenti.
3. Scrivere una sintesi operativa originale in italiano, senza inventare pulsanti, coordinate, tempi, ricompense o condizioni di spawn.
4. Distinguere la funzionalita' normale del gioco da un exploit. L'esistenza di una guida non certifica automaticamente la compatibilita' con i trofei.
5. Selezionare immagini pertinenti con una base di riutilizzo appropriata e mantenerne provenienza e attribuzione. La semplice reperibilita' online non e' una licenza generale.
6. Inserire dati e associazioni dei passaggi, classificare gli spoiler e generare la pagina prima di promuoverla.
7. Eseguire i test sul risultato effettivamente pubblicato. Verificare che il link pubblico risponda e contenga il nuovo tutorial.
8. Solo dopo il deploy, rendere il contenuto eleggibile per il bot, mantenendo il registro anti-duplicazione e le regole editoriali. Nessun retry cieco dei post dall'esito incerto.

Questa e' la procedura editoriale del repository: non implica che il solo feed crei, verifichi e pubblichi automaticamente nuove guide senza revisione.

## SEO e verifiche

Conservare gli indirizzi delle guide gia' esistenti. Ogni pagina deve avere un solo H1, titolo, descrizione, canonical, dati strutturati coerenti, collegamenti interni validi e una data di aggiornamento derivata dai file sorgente, non soltanto dall'orario del deploy. Non inventare numeri di visite, classifiche o attestazioni di test personali.

Comandi di verifica:

```sh
python -m unittest -q test_site.py test_community_feed.py test_related_research.py test_guide_source_validation.py
python prepare_visual_media.py
python build_visual_site.py
python -m unittest -q test_visual_site.py
python visual_browser_qa.py
```

Il controllo browser copre home, garage e tutorial del negozio a 390, 768 e 1440 pixel, immagini caricate, assenza di overflow, ricerca, filtri, menu mobile e persistenza della preferenza spoiler. Il deploy controlla anche le risposte pubbliche di home e sezioni principali e il marker `data-design-version`.

## Limiti mantenuti espliciti

La prima versione contiene dieci tutorial e tredici immagini selezionate, non le centinaia di immagini ipotizzate nel progetto. La copertura visiva dei singoli passaggi non e' completa per tutte le guide. Dove mancano immagini verificate, resta il collegamento alla fonte: nessun riferimento di gioco inventato. Il redesign non modifica da solo le impostazioni di Buffer o la frequenza dei post X.
