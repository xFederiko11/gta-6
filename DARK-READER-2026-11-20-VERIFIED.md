# Tema scuro e consigli contestuali: pubblicazione verificata

## Esito reale

PR #32 unita: https://github.com/xFederiko11/gta-6/pull/32
Commit pubblicato: `1367905e78a7068cc2e5768b6f059c51efba25a0`.
Esecuzione di produzione: https://github.com/xFederiko11/gta-6/actions/runs/44695818491
Build `136152182749` e deploy `136153731678` completati con successo.
GitHub Pages ha confermato la pubblicazione il 20 novembre 2026 alle 07:37:21 UTC, cioe' 08:37:21 CET.

Il controllo HTTP del runner sulle URL pubbliche ha verificato status 200, tema iniziale scuro, selettore chiaro/scuro, nuovi asset e canonical corretto per home, Soldi facili, Auto speciali, Salvare auto, soldi iniziali e taxi. Sulle guide previste sono presenti anche consigli e fonti. Questa e' una verifica reale dopo il deploy, non soltanto un controllo dell'anteprima locale.

## Funzioni pubblicate

- Tema scuro predefinito, anche con sistema operativo chiaro; selettore Aspetto > Scuro / Chiaro nella barra superiore.
- Preferenza salvata nel browser con `gta6-theme-v1`, applicata prima dei fogli di stile. Tema e spoiler restano indipendenti.
- Palette navy, viola e rosa, sfondi e pannelli scuri, testo chiaro; nessun filtro che inverta o alteri i colori delle schermate di gioco.
- Gallerie con le mappe gia' selezionate, vicino alle indicazioni del percorso, e apertura delle immagini nella pagina con zoom 2x, Chiudi ed Esc.
- Nove note documentate in cinque guide: le due guide iniziali sui soldi, salvataggio auto, scansione veicoli e taxi. Tipi distinti: Consiglio utile, Da evitare, Curiosita'. Fonti numerate in fondo.
- Mappe e curiosita' sensibili restano nei pannelli spoiler chiusi. I collegamenti interni che li aprono lo segnalano esplicitamente.
- Riconciliati due dettagli editoriali con le fonti: il salto del taxi costa 100 GTA$ oltre alla corsa; la prima registrazione del veicolo usa l'officina gia' sbloccata, non qualsiasi officina fin dall'inizio.
- Conservati indirizzi delle guide, H1, metadati, dati strutturati e sitemap. La data dei sorgenti include le modifiche al reader e agli approfondimenti.

## Test e schermate

- 33 test sui contenuti e contratti precedenti, piu' 14 test sull'output visivo e reader.
- Otto pagine a 320, 390, 768 e 1440 pixel: 32 combinazioni pagina/larghezza, ciascuna verificata nei due temi.
- Verificati cambio tema, persistenza al ricaricamento, ricerca, protezione spoiler, caricamento dell'immagine nello zoom e chiusura con Esc.
- Verificato tema scuro iniziale con JavaScript disabilitato e comportamento con localStorage non disponibile.
- Un overflow del menu a 320 pixel e' stato identificato e corretto adattando il marchio e il pulsante, senza nascondere lateralmente il contenuto.
- QA di approvazione: https://github.com/xFederiko11/gta-6/actions/runs/44695483573
- Artefatto ispezionato: `reader-qa-44695483573`, ID `14610472404`. Report con 32 casi superati, schermate reali mobile/desktop e chiaro/scuro. Le schermate sono render HTML effettivi, non immagini generate.
- Gli stessi controlli sono passati anche nella build di produzione prima del deploy.

## Confini e continuita'

Questo aggiornamento migliora la disposizione e l'ingrandimento delle immagini esistenti; non aggiunge nuove immagini uniche e non completa tutte le posizioni mancanti. Restano tredici risorse selezionate. La priorita' editoriale rimane aggiungere mappe reali e immagini operative per le singole azioni quando documentate, non decorazioni o coordinate inventate.

Consigli e curiosita' non sono generati automaticamente da titoli di feed: richiedono verifica e fonte. Nessuna dichiarazione di test personale del gioco o di exploit trophy-safe.

Lo standard aggiornato e i comandi corretti sono in `VISUAL-EDITORIAL-GUIDE.md`; la produzione esegue `python reader_experience.py --build`. Non sono state modificate coda, credenziali o cadenza del bot X/Buffer.
