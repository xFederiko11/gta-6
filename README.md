# GTA 6 Italia — guide, tutorial e trofei

Portale pubblico e gratuito dedicato a **GTA VI su PS5 e PS5 Pro**. I contenuti sono in italiano.

**Indirizzo previsto:** https://xfederiko11.github.io/gta-6/

## Struttura

- **Homepage** — `/gta-6/`
- **Trofei** — `/gta-6/trofei/`: 55 schede individuali, requisiti Oro, protezione degli spoiler.
- **Guide e tutorial** — `/gta-6/guide-e-tutorial/`: consigli rapidi con procedura PS5, vantaggi e fonte.
- **Scoperte community** — `/gta-6/scoperte/`: feed di ricerca GTA VI generato automaticamente da GitHub con link, date ed etichette, non conferme dei rumor.
- **Fonti e metodologia editoriale** — `/gta-6/fonti/`: fonte ufficiale vs guida indipendente, community, dataminer, giornalismo, verifica trucchi e notizie.
- **Trucchi GTA VI PS5** — `/gta-6/trucchi/`: 17 sequenze pubblicate illustrate con icone croce direzionale DualSense; singole pagine SEO, requisiti, fonti e avviso trofei.
- **HDR OLED** — `/gta-6/hdr-oled/`: cerca marca, codice TV o diagonale; 21 famiglie e 92 codici per PS5 e PS5 Pro, pagine SEO per serie.
- **Medaglie Oro** — `/gta-6/trofei/medaglie-oro/`.
- **SEO** — sitemap, robots, canonical, Open Graph, metadati e JSON-LD.

I contenuti sono separati dai template in `data/trofei.json`, `data/guide.json` e `data/hdr_oled.json`.
L’indice OLED e le 21 pagine di famiglia sono generate da `hdr_catalog.py`, con fonti del produttore. Le impostazioni HDR specifiche di GTA VI non sono inventate: usare soltanto i controlli effettivamente disponibili nel gioco e nel firmware TV.
Il generatore `build_site.py` produce il sito statico in `_site/` senza API e senza abbonamenti.


## Novità v15.0: aggiornamento, visualizzazioni e X

Ogni pagina reale (homepage, indice trofei, 55 schede, indice e sei guide, medaglie Oro, indice HDR e 21 schede OLED) ha una microbarra immediatamente sotto la navigazione con:

- **Aggiornata il:** ultima modifica dei file sorgente pertinenti secondo la cronologia Git, in data italiana; build programmati senza modifica non aggiornano artificialmente la data. In anteprima senza Git si usa la data della generazione come ripiego.
- **Visualizzazioni:** badge per singolo URL canonico fornito da [Hits Counter](https://hitscounter.dev/), attivo dal lancio della funzione. Conta richieste al badge/visite approssimative, **non visitatori unici certificati**, non recupera visite storiche; un ad blocker o cache può alterare il valore. Se il servizio esterno è inattivo non si inventano visualizzazioni.
- **Profilo X:** collegamenti visibili a [@xFederiko11](https://x.com/xFederiko11), nell'header, nella microbarra e nel footer, con riferimento anche ai post breaking e alle guide collegate al sito.

I metadati `dateModified` JSON-LD e `article:modified_time` supportano la trasparenza SEO. Gli utenti vengono informati della natura indipendente del portale. Il badge esterno carica un'immagine dal server del fornitore: per privacy e affidabilità verificare la sua policy prima di sviluppare analitiche più avanzate. Non sono necessari cookie o identificativi creati dal nostro codice, database, API X o abbonamenti.

## Anteprima e test

Servono soltanto Python 3.12 e la libreria standard:

```bash
python build_site.py
python -m unittest -q test_site.py
python -m http.server --directory _site 8000
```

L'URL `http://localhost:8000/` mostra la versione locale; su GitHub Pages tutti i collegamenti puntano all'URL pubblico.

## Prima pubblicazione: GitHub Pages

1. Apri **Settings → Pages** della repository `gta-6`.
2. In **Build and deployment** scegli **Source: GitHub Actions**.
3. Apri **Actions → GTA 6 Italia - Website**, avvia **Run workflow** dal branch `main`.
4. Verifica l'indirizzo pubblico e il sitemap:
   `https://xfederiko11.github.io/gta-6/sitemap.xml`.

La pagina non va considerata pubblicata prima di un deploy e di un HTTP 200 reale. I motori di ricerca indicizzano i contenuti secondo i propri tempi.

## Relazione con il bot di X

Il bot continua a vivere nella repository `xFederiko11/federiko-gta-playstation-bot` e **non viene trasferito in questa repository**. Il collegamento ai nuovi URL deve essere attivato solo dopo che le pagine saranno online e verificabili.

Formato editoriale futuro:
- Post principale in italiano, azione immediata e immagine illustrativa con diritti verificati.
- Risposta collegata con URL della specifica pagina su questo sito.
- Fonte PowerPyx indicata nella pagina e, se utile, anche nella risposta.

Non copiare lunghi testi o immagini di terzi senza verificarne i diritti. Le immagini promozionali Rockstar sono attribuite, illustrative e non equivalgono a fotografie delle singole procedure.

## Manutenzione

- Non cancellare i dati dei 55 trofei.
- Evitare modifiche ai permalink dei trofei senza redirect 301 e aggiornamento del bot.
- Per nuove guide aggiungere una voce a `data/guide.json`, quindi rieseguire i test.
- I trofei nascosti sono protetti dagli spoiler nella homepage; l'indicizzazione delle relative schede inizia dal 21 novembre 2026 (UTC).
- Nessun dato di monitoraggio dell'account X, token o secret deve essere copiato qui.

## Fonti

- [PowerPyx: GTA VI Trophy Guide](https://www.powerpyx.com/gta-6-grand-theft-auto-vi-trophy-guide-roadmap/)
- [Trofei GTA VI in italiano](https://www.planetgta6.com/it/trofei-gta-6/)

Progetto fan indipendente, non affiliato a Rockstar Games, Take-Two, PlayStation o PowerPyx.

## Catalogo HDR OLED (novembre 2026)

- **21 famiglie:** LG C3/C4/C5/C6, B4 e G4/G5/G6; Samsung S90D/S90F/S90H e S95D/S95F/S95H; Sony A80L, BRAVIA 8 e 8 II; Philips OLED850/OLED811 e Panasonic Z95A.
- **92 codici TV verificabili** nel catalogo, con diagonali in pollici. I codici italiani Panasonic hanno il suffisso **EG**; es. TV-55Z95AEG, TV-65Z95AEG.
- URL stabili sotto `/hdr-oled/<famiglia>/`; una pagina per gruppo di configurazioni, non una pagina duplicata per ciascuna diagonale.
- Ricerca client-side per sigla/serie/brand/pollici, canonical, sitemap, JSON-LD CollectionPage e Article, fonti e data di aggiornamento.
- Non indicare valori di nit, paper white o click PS5 come universali per tutti i pannelli: luminosità, firmware e impostazioni di tone mapping cambiano la resa. Non attribuire controlli HDR specifici a GTA VI senza verificarli.
- Per ampliare il catalogo, modificare `data/hdr_oled.json` e ripetere `python build_site.py && python -m unittest -q test_site.py`.

La serie LG C4 include codici italiani **C44LA/C43LA** e tedeschi **C47LA** confermati dai siti LG, con differenze di luminosità fra 42/48 e 55/65/77/83 pollici. Il catalogo conserva un URL per serie, non uno per ogni SKU.

Fonti principali: [HDR PS5 - PlayStation](https://www.playstation.com/it-it/support/hardware/ps5-enable-adjust-hdr/), schede produttore direttamente in ogni famiglia.

## GTA VI in-game HDR (19 novembre 2026)

La priorità editoriale è il **menu interno del gioco**: Options → Settings → Display → HDR Calibration. Il sito mostra per ciascuna famiglia i tre campi Max Brightness / Black Levels / Paper White, distinguendo:
- C4: **1100/0/50**, C3: **800/35/50**, C2: **800/50/50** — *rapporti individuali Reddit, non preset strumentali*, diagonale non indicata.
- Altre TV: **600/50/50** — valori iniziali visualizzati in GTA VI nelle schermate PS5, **non** valori ottimizzati per la TV. Invece di inventare profili, spiegare come calibrare e raccogliere misure di pannello/fonte.
- La pagina TV conserva le istruzioni HGiG come sezione secondaria, dopo i valori in-game.

Fonti: https://allthings.how/best-gta-6-settings-to-change-first-on-ps5/ e https://www.reddit.com/r/OLED_Gaming/comments/1xzf4z4/gta_hdr_settings_megathread/ . Prima di chiamare un preset «confermato» servono misurazioni e test riproducibili sul modello/taglio specifico.

## Trucchi GTA VI (novembre 2026)

- Fonte dati: `data/trucchi.json`, generatore `cheats_catalog.py` senza dipendenze esterne.
- La pagina `/trucchi/` e 17 pagine singole con canonical, meta description, JSON-LD e sitemap distinguono codici noti e restanti sequenze non pubblicate.
- Tutte le sequenze sono disegnate con `<kbd>` accessibili della croce direzionale DualSense e etichette ARIA (nessun font esterno o immagine proprietaria del controller).
- **Post-storia soltanto.** I trucchi non sono utili per anticipare la progressione: bloccano trofei e salvataggi mentre attivi; backup manuale separato PRIMA di provarli.
- Fonti editoriali: https://www.powerpyx.com/gta-6-all-cheats/ , https://www.pcgamer.com/games/grand-theft-auto/gta-6-cheats-list/ e https://gtadb.net/gta-6/cheats/ . I codici sono attribuiti, non testati personalmente dall'autore del sito.
- Ricontrollare i codici con fonti indipendenti in caso di aggiornamenti o segnalazioni di errori, senza inventarne di mancanti.


## Verifica fonti GTA VI (19 novembre 2026)

La pagina `/fonti/` è generata da `sources_page.py` e `data/fonti_editoriali.json`, con canonical, JSON-LD, sitemap e data reale di modifica. Elenca fonti ufficiali e indipendenti senza mescolarne l'autorità. Le 17 sequenze GTA VI pubblicate sono attribuite a PowerPyx; soltanto 9 risultano corrispondere anche agli input della guida indipendente PC Gamer al 19/11, e 8 restano da verificare indipendentemente. Il requisito di medaglie per Max Ammo è controverso (20 vs 25) e viene esplicitato. Il bot editoriale raccoglie nuovi elementi PowerPyx e GTA Series Videos in modalità ricerca prima della pubblicazione. Fonti non accessibili automaticamente non vengono descritte come lette dal bot.

## Aggiornamento autonomo delle scoperte dal bot

Il monitor pubblico `xFederiko11/federiko-gta-playstation-bot` aggiorna una singola issue GitHub di ricerca ogni tre scansioni al giorno, inserendo un payload JSON firmato dal contesto di origine (non crittograficamente). Il sito recupera esclusivamente quella issue tramite API GitHub pubblica prima della build con `fetch_community_feed.py`; `community_page.py` valida schema, URL, fonti, date ed etichette. La pagina `/scoperte/` è SEO-indicizzabile, ma **esplicita che i titoli sono segnalazioni non verificate**. Non si copiano articoli, non si presentano rumor come annunci e non si inviano messaggi Buffer. Se il servizio sorgente non è disponibile, il deploy si blocca lasciando pubblicata la versione precedente; quando non esiste ancora alcuna issue, viene mostrata la pagina vuota con avviso. La scansione avviene via GitHub Actions senza ChatGPT, chiavi API commerciali o automazioni ChatGPT.


## Collegamenti dinamici alle fonti delle guide

`related_research.py` legge il feed già importato dal bot GitHub per mostrare, nell'indice delle guide e nelle singole guide, **soltanto collegamenti esterni chiaramente pertinenti** all'argomento, con fonte e data. Non usa i titoli per modificare procedimenti, numeri di trofei, combinazioni di trucchi o avvertenze trophy-safe. Sulle pagine pratiche evita i rumor; questi rimangono nell'indice `/scoperte/` con l'etichetta di affidabilità. I titoli delle fonti sono sempre soggetti a validazione del dominio e HTML escaping.

Fonti di ricerca abilitate: PowerPyx, GTA Series Videos e GTABase (quando il feed news risponde). Avere un feed è solo un modo di rilevare nuovi contenuti, non una certificazione di quanto affermato. I cambiamenti richiedenti verifica in-game rimangono in una checklist del bot su GitHub Issues, non sono pubblicati come fatti. `test_related_research.py` controlla collegamenti pertinenti e protezioni contro contenuti non attendibili.



## Continuità dei workflow programmati

La repository è pubblica: GitHub documenta la possibile disattivazione dei workflow `schedule` dopo **60 giorni senza attività** (<https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows>).

Per ridurre questo rischio il workflow `.github/workflows/gta6-schedule-keepalive.yml` esegue **un controllo settimanale**, ma crea un commit minimale nel solo file `.state/workflow-keepalive.json` **soltanto dopo almeno 35 giorni senza nuovi commit su `main`**. Usa `GITHUB_TOKEN` con il solo permesso GitHub `contents:write`; non legge o modifica Buffer, X, guide, trofei o contenuti editoriali e non richiede servizi esterni.

**Limiti:** questo sistema è preventivo e non garantisce che GitHub o i provider restino sempre disponibili, che tutti i run schedulati avvengano in orario o che GitHub continui a contare gli heartbeat automatici come attività idonea. Se GitHub disattiva il workflow prima dell'esecuzione, è necessario riabilitarlo manualmente. La manutenzione delle credenziali Buffer e dei feed rimane separata.


## GTA Wiki: rilevamento sperimentale delle modifiche

Il sito riconosce anche `GTA Wiki (independent)` (dominio `gta.wiki`) come fonte community **non ufficiale**. Il bot tenta di raccogliere i titoli delle modifiche recenti mediante l'interfaccia pubblica MediaWiki Atom; l'accessibilità reale viene misurata e registrata a ogni scansione. Le revisioni di una wiki NON sono conferme dei contenuti: sul sito appaiono soltanto come `🟡 SEGNALAZIONE` con link originale, data e avvertenze sui trofei. `gta.fandom.com` e GTAForums restano nel percorso di ricerca manuale finché non sarà confermato un accesso affidabile. Nessuna riscrittura automatica delle guide o dei codici deriva da una modifica wiki.


## Restyling operativo delle schede (19 novembre 2026)

- **Tutte le 55 schede dei trofei:** nuovo hero illustrato in SVG originale, requisito immediato senza ripetizioni, pulsante «Segna trofeo ottenuto» salvato localmente nel solo browser, fonti espandibili e rail di tre trofei pertinenti. Non comunica con PSN e non simula sblocchi veri.
- **Trofeo Cecchino (#17):** procedura in 3 azioni, checklist interattiva di **42 medaglie Oro** distribuite su 12 percorsi/2 poligoni, nome e livello di difficoltà per ciascuna casella. Dati dalla [guida PowerPyx ai poligoni](https://www.powerpyx.com/gta-6-all-shooting-range-gold-medal-challenges/). Il giocatore spunta manualmente le medaglie, la progressione è conservata tramite `localStorage` se consentito. Nessuna lettura di salvataggi PS5 o sincronizzazione tra dispositivi.
- **Video:** anteprima ufficiale Rockstar [GTA VI: An Extended Look](https://www.youtube.com/watch?v=tJbzMqJGH4k&t=1112s), incorporata tramite `youtube-nocookie.com` solo dopo un clic. Il segmento del poligono intorno a 18:32 è una dimostrazione visiva e **non** un tutorial per tutte le 42 medaglie. La miniatura è caricata da YouTube; nessun video copiato o ospitato sul nostro server.
- **Sei guide pratiche:** immagini promozionali già referenziate dal sito, ora visibili prima dei passaggi; risposta rapida, istruzioni, avvertenze, fonte e schede «La prossima guida». Le immagini restano proprietà dei titolari, non sono estratte da PowerPyx e non vengono presentate come schermate delle procedure.
- **Mobile:** navigazione superiore compatta con scorrimento orizzontale, contenitori senza overflow e card correlate a carosello CSS con scroll-snap. Nessun framework o nuovo servizio a pagamento.
- **SEO:** URL/canonical esistenti preservati, JSON-LD Article, metadati e data di modifica reali invariati. I test automatici verificano markup per 55 trofei, 6 guide, 42 caselle, sorgente del video e interazioni senza telemetria.


### Riepilogo trofei ottenuti (locale)

La pagina `/trofei/` mostra ora un contatore personale `x / 55` e contrassegna le schede spuntate. Il pulsante **«Segna trofeo ottenuto»** delle singole schede aggiorna il contatore: lo stato viene salvato esclusivamente nel `localStorage` del browser, senza accesso a PSN né sincronizzazione. Il riepilogo si aggiorna tornando all'elenco e quando cambiano i dati in un'altra scheda. Non sono necessarie credenziali, tracking utenti o API esterne.


## Esperienza mobile delle guide (novembre 2026)

Le **sei guide pratiche** ora hanno anteprime visuali nel catalogo, un'immagine promozionale attribuita a Rockstar e un segnaposto grafico **disegnato in CSS** che compare anche quando un browser blocca l'immagine remota. Non copiamo screenshot o miniature di PowerPyx: gli scatti promozionali sono dichiarati illustrativi, mai spacciati per prova del singolo passaggio. La guida rimane pienamente leggibile anche senza immagini.

Ogni procedura presenta passaggi spuntabili, progresso numerico e un comando «Copia passaggi» che usa gli strumenti del browser. Le spunte sono memorizzate **solo nel localStorage del dispositivo**, quando disponibile; non leggono PSN e non rappresentano requisiti reali del platino. Cambiando il contenuto dei passaggi, l'identificatore della checklist cambia per evitare di segnare come eseguite istruzioni modificate. Se la memoria o la clipboard sono bloccate dal browser integrato, viene mostrato un messaggio esplicito e le procedure restano consultabili.

Le schede correlate preferiscono guide riferite allo **stesso trofeo o argomento**. Su mobile il carosello resta navigabile orizzontalmente, senza suggerimenti pubblicitari. Le pagine trofei già più complete (Cecchino con 42 caselle e video ufficiale a richiesta) mantengono le loro funzioni; per i trofei privi di consigli specifici il sito non ripete artificialmente il requisito né inventa metodi di farming.

Verifica: il workflow GitHub Pages ricostruisce e controlla automaticamente gli HTML SEO, i tag delle immagini, i fallback, le checklist e i permalink senza usare ChatGPT o Buffer.


### Video contestuali con fallback mobile

Il player dell'anteprima ufficiale Rockstar già usato nella pagina del trofeo **Cecchino** è ora presente anche nella guida pratica **Poligoni di tiro: Concentrazione e medaglie Oro**. Non si afferma che il filmato insegni le 42 prove: è un riferimento illustrativo alla modalità di gioco. Il player YouTube viene caricato solo dopo il clic dell'utente. Se la miniatura remota non si carica nel browser X, il pulsante resta visibile con un elegante sfondo CSS senza mostrare immagini rotte. La modifica non riutilizza video di PowerPyx senza autorizzazione e non altera i requisiti dei trofei.

### Trucchi PS5 — navigazione e consultazione mobile

Le 17 schede trucchi ora mettono in evidenza la **sequenza DualSense** in un pannello grafico originale, con link rapido dalla testata, pulsante di copia e link alle combinazioni della **stessa categoria**. Quando una categoria contiene un solo codice, l'invito rimanda al catalogo completo invece di suggerire contenuti scollegati. La copia funziona solo dopo il clic e si limita alla sequenza già visibile (nessun invio ai server e nessuna modifica alla sessione di gioco).

Le pagine mantengono gli avvisi ben visibili sui trofei e sui salvataggi. Nessuna sequenza o requisito è stato cambiato, nessun nuovo codice è stato inventato. Le icone freccia PS5 sono già disegnate con elementi accessibili e non richiedono font o immagini del controller di terzi. Gli aggiornamenti a questo script partecipano al `dateModified` delle relative schede.


## Restyling HDR OLED e scoperte community — mobile (19 novembre 2026)

La sezione **HDR OLED** presenta i tre campi del menu reale di GTA VI (Max Brightness, Black Levels e Paper White), un'illustrazione grafica originale di una TV (non uno screenshot), accessi rapidi ai valori e alla ricerca per modello e un comando per copiare la tripletta nel browser. Il testo copiato conserva un'avvertenza sull'origine dei numeri: i tre profili LG C2/C3/C4 sono testimonianze community individuali, mentre gli altri valori 600/50/50 sono semplici impostazioni iniziali viste nel gioco, **non calibrazioni misurate**. Le famiglie di uno stesso produttore si possono confrontare tramite schede correlate che non inventano preset.

La pagina **Scoperte** è ora un catalogo leggibile su smartphone: card con arte CSS locale originale, ricerca per parole, filtri per fonte e classificazione, conteggio dei risultati e collegamenti diretti alle fonti originali. L'utente può riprodurre soltanto **video diretti YouTube** pubblicati nella fonte GTA Series Videos; il player `youtube-nocookie` viene caricato esclusivamente dopo il clic e rimane separato dal link originale. Non scarichiamo o copiamo le immagini dei portali di terzi. Un titolo del bot non diventa automaticamente un fatto verificato, una raccomandazione trophy-safe, un annuncio ufficiale o una notizia confermata.

Le interazioni sono statiche e gratuite: `site/assets/hdr-interactions.js` e `site/assets/community-interactions.js` non richiedono cookie, tracker, account, Buffer, ChatGPT o API commerciali. I controlli di regressione verificano escaping HTML, validazione host/ID video, fallback per feed vuoti, filtri e preservation dei permalink e metadati SEO.


## Conteggio visualizzazioni senza iscrizioni

Ogni pagina conserva il badge preesistente `hitscounter.dev` con conteggio per URL canonico. Il servizio è esterno ma **non richiede un account**; il conteggio si riferisce alle richieste al badge, non a utenti unici o a sessioni verificabili. Il sito non include più GoatCounter, configurazioni, SDK o script di analytics opzionali. Tutte le pagine rimangono pubblicate su GitHub Pages senza server, servizi a pagamento o accessi manuali.

La pagina [Privacy e visite](https://xfederiko11.github.io/gta-6/privacy/) spiega come interpretare i contatori e il funzionamento del badge. **Non è possibile ricavare da un badge statico il tasso di conversione dei link o visite uniche attendibili**: non verranno inventati.


## Anteprime social originali, senza servizi o licenze esterne

La homepage (e le pagine senza una fotografia specifica) ora dichiara `og:image` e `twitter:image` a un file PNG 1200 × 630 ospitato nel sito. Il file `assets/social-preview.png` è generato durante ogni build da `social_preview.py`, con **solo Python standard library**, e presenta una grafica originale pixel-style con nome GTA 6 Italia, PS5, trofei, guide e HDR OLED: nessuna immagine o logo Rockstar copiato, nessuna API di generazione, nessun account.

Questo può migliorare le anteprime dei **nuovi** link condivisi su X e altri social; non dimostra che il riquadro grigio nel post fissato fosse dovuto a un errore Open Graph. I social possono conservare cache e miniature per ore o giorni, o bloccare alcuni URL: non è garantito l'aggiornamento dei post esistenti. La modifica non cambia il testo o la pubblicazione del post fissato su X.


## Google Search Console: attivazione SEO senza tracker

Il portale pubblica `robots.txt`, `sitemap.xml`, tag canonici e dati strutturati. Per misurare **impression e clic organici di Google** (non visite totali, clic sui pulsanti X o nuovi follower) è disponibile una verifica proprietà facoltativa via HTML meta tag. Non è abilitata finché il proprietario non fornisce il token.

1. Aprire [Google Search Console](https://search.google.com/search-console/), aggiungere la proprietà **Prefisso URL** `https://xfederiko11.github.io/gta-6/` (non una proprietà Dominio di `github.io`).
2. Selezionare la verifica **Tag HTML**; copiare **solo il valore del campo `content`**, senza i tag HTML. Non occorre fornire credenziali Google a GitHub o al bot.
3. In GitHub → `xFederiko11/gta-6` → Settings → Secrets and variables → Actions → **Variables**, creare `GSC_SITE_VERIFICATION` con quel valore. Il token di verifica è pubblico per definizione; il codice lo valida e lo emette esclusivamente nel `<head>` della homepage.
4. Eseguire il workflow Pages normale e visitare `https://xfederiko11.github.io/gta-6/`; verificare che il meta tag compaia nella sorgente pubblica. Solo allora premere **Verifica** in Search Console.
5. Inviare la sitemap `https://xfederiko11.github.io/gta-6/sitemap.xml`. La presenza in sitemap non garantisce l'indicizzazione: controllare in Search Console l'effettiva copertura e le prestazioni.

Se la variabile non esiste, **non viene aggiunto alcun tag o script** e il sito continua a funzionare come prima. Se il valore è malformato, la build fallisce per evitare iniezioni HTML. Non aggiungiamo Google Analytics, pixel di marketing, cookie o profilazione ai lettori.

**Limite di misurazione:** il contatore di richieste al badge e i clic Search Console non provano né utenti unici, né CTR del pulsante Segui X, né follower acquisiti. Per un vero funnel `pagina → click su X → follower` servono almeno eventi di click raccolti con uno strumento autorizzato e statistiche dell'account X; il collegamento individuale non è ricavabile da questi dati aggregati. Cloudflare Web Analytics gratuito potrebbe misurare pagine e visitatori dopo configurazione esplicita, ma al novembre 2026 la sua Web Analytics non supporta custom events: da solo non risolverebbe il tracking del pulsante X.


## Funnel X: misurazione opzionale con Umami (senza API X)

Il sito supporta **Umami Cloud Hobby**, senza richiedere servizi di analisi per funzionare. La pagina [Umami Pricing](https://umami.is/pricing) indica un piano gratuito per un sito fino a 100.000 eventi mensili, con conservazione limitata; **verificare il piano prima di collegare il servizio**. L'integrazione NON è attiva finché non viene impostata la variabile. Se manca, il codice di generazione non aggiunge script né attributi di analisi.

1. Accedere a [Umami Cloud](https://cloud.umami.is/), scegliere il piano gratuito **Hobby** e creare un sito per `xfederiko11.github.io`.
2. Aprire il sito appena creato nella dashboard Umami, leggere il proprio **Website ID** dal tracking code. È un UUID pubblico, non una password: non serve copiare lo script o incollare credenziali in GitHub.
3. Nella repository `xFederiko11/gta-6` aprire **Settings → Secrets and variables → Actions → Variables → New repository variable**; nome esatto **`UMAMI_WEBSITE_ID`**, valore il Website ID. Il campo deve essere un UUID valido; niente URL o tag HTML.
4. Eseguire il normale workflow **GTA 6 Italia - Website** oppure attendere il deploy automatico. La build in `main` aggiunge lo script ufficiale `https://cloud.umami.is/script.js` e il dominio autorizzato; le pull request non attivano l'analisi.
5. Aprire la dashboard di Umami e confrontare le visite per pagina con gli eventi **`x-follow-intent`**, **`x-share-intent`**, **`x-reply-intent`**, **`x-post-open`**, **`x-profile-open`** e **`youtube-video-open`**. I link nativi X rimangono invariati; nessun redirect e nessun account GitHub richiesto ai visitatori.

**KPI iniziale:** `clic Segui verso X / visualizzazioni pagina` (per pagina o insieme di pagine nello stesso intervallo). Non confonderlo con **nuovi follower**: l'account X può essere seguito o meno dopo il clic, e X non restituisce questa conferma a Umami. Tenere separati `click verso X`, `sessioni`, `visite profilo X` e `follower reali`. Per la conversione follower definitiva servono dati aggregati dell'account X provenienti da X Analytics o un'integrazione autorizzata, non stime dal badge.

La funzione rispetta **Do Not Track** quando esposto dal browser, evita il caricamento durante le pull request e non aggiunge cookie, identificatori persistenti, dati PSN o eventi su azioni nel gioco. La pagina **Privacy e visite** riflette la configurazione: in assenza dell'ID spiega che non ci sono tracker; con ID valido descrive Umami e la raccolta aggregata. Verificare gli obblighi di informativa e consenso applicabili prima dell'attivazione. Per disattivare basta eliminare la variabile e ricostruire il sito.

## Gruppo 3 · Guide, screenshot e Platino (21 novembre 2026)

- `trofei/roadmap-platino/`: roadmap in cinque fasi, checklist locale senza accesso PSN, avviso del Capitolo 1, link alle guide e alle schede trofeo. Sorgente: `platinum_roadmap_v1.py`; JS e CSS dedicati in `site/assets/platinum-roadmap.*`.
- `data/guide_step_refs.json` + `guide_step_references_v1.py`: riferimenti mappe e video **specifici per un passaggio** (con minuto derivato dalle cronologie di fonti terze). Sono link esterni, non schermate catturate da noi né prova della compatibilità trofei.
- Le 11 guide conservano gli avvisi sui veri screenshot ancora mancanti, la galleria e la pagina `screenshot-ps5/`. Nessun render generato o clip di terzi conta come screenshot documentale, nessuna licenza di riuso presunta.
- Nuovi test `test_group3_roadmap_step_refs_v1.py` nel workflow di build e PR, e verifica HTTP di `trofei/roadmap-platino/` dopo il deploy. Il sito **non** modifica le checklist PSN né pubblica nuovi post su X automaticamente.

## Gruppi 1+2: atlante visivo e 55 strategie Platino (21 novembre 2026)

- `trofei/roadmap-platino/#guida-55-trofei`: sezione con 55 schede curate individualmente, filtri per obiettivo, ricerca, riquadri spoiler per 28 trofei nascosti e spunte manuali coerenti con `gta6-italia:trophies:v1`. Le condizioni sconosciute **non** hanno procedure inventate.
- `mappe-guide/`: 11 guide e 18 riferimenti geografici documentati, con 10 landmark delle meditazioni. I link a GTABase sono **filtri di categoria**, non pin assoluti; gli altri puntano a guide sorgente con descrizione del luogo.
- `data/guide_locations_v2.json` distingue mappe filtrate, riferimenti descrittivi e attività senza luogo fisso. `guide_location_atlas_v2.py` mostra i riferimenti nelle guide originali e conserva gli spoiler.
- I conteggi foto restano quelli verificati dalle immagini gameplay realmente disponibili nel build: non aumentano per immagini promozionali, video, link a mappe o richieste non ancora ricevute.
- Generazione e test automatici: `platinum_atlas_v2.py`, `test_group12_atlas_v2.py`, `site/assets/platinum-atlas-v2.*`. Nessun login GitHub o PSN richiesto, nessuna chiamata API per memorizzare le spunte.

## Gruppo Foto + Trofei difficili (21 novembre 2026)

- `trofei/100-percento/`: 35 contatori del 100% secondo PowerPyx, 18 set di carte per un totale di 480, checklist locale separata dal PSN. Minimo teorico 372 carte per 15 set, non una rotta di viaggio.
- `trofei/trofei-difficili/`: procedure operative #38 Rhino, #46 Bowling, #47 Forza Jason/Lucia, #48 Profilo criminale, #50 UFO (spawn e location con caveat), #30 carte; #49 resta **incerto**.
- `screenshot-ps5/verifica/`: 10 screenshot editoriali già catalogati, con provenienza e diritti non documentati; 8 fonti da verificare prima di acquisire nuove foto. Non aggiunge immagini di terzi senza autorizzazione.
- Asset, test e controllo HTTP dedicati: `advanced_platinum_v3.py`, `photo_provenance_v3.py`, `test_advanced_platinum_v3.py`, `data/advanced_platinum_v3.json`, `data/photo_provenance_review_v3.json`. I contatori sono manuali e privati nel browser; il sito non legge i trofei PSN.

## Gruppo acquisizione foto + percorsi regionali (21 novembre 2026)

- `screenshot-ps5/invia/`: modulo statico per scegliere una delle 11 guide e uno dei 55 ruoli fotografici, con dichiarazione originale di titolarità e concessione non esclusiva, apertura manuale della bozza X. **Nessun file viene caricato dal sito** e nessun post è pubblicato dal bot; la foto va allegata su X dall’autore.
- `data/approved_screenshots_v4.json`: elenco **attualmente vuoto** delle immagini nuove autorizzate. La CI vieta foto senza consenso documentato via status X, revisore umano, WebP locale e SHA-256. Nuovi file approvati possono essere mostrati nella guida corretta dopo revisione della PR; non si presume che la sola attribuzione basti.
- `collezionabili/percorsi/`: 41 punti con fonti, divisi in 7 aree, ricerca, filtri, spunte private nel browser. Priorità alla carta Vicki prima del Capitolo 2. **Copertura parziale**: 6/33 immersioni, 16 carte e 14 WAiNK, non 100% geolocalizzato. L’ordine è editoriale, non un navigatore GPS.
- Test e verifiche HTTP aggiunti tramite `test_photo_routes_v4.py` e `.github/workflows/deploy-site.yml`. Nessuna credenziale o accesso PSN richiesti.

## Palette uniforme e ampliamento collezionabili — 21 novembre 2026

- Tema GTA VI **scuro per impostazione predefinita su mobile e desktop**, fondo blu-antracite `#10131d`, testo `#f3f3fa` e accenti rosa `#ff9bca`. I pulsanti `Scuro / Chiaro` restano attivi; `gta6-theme-v1` conserva la preferenza personale.
- Atlante ampliato da 41 a **76 punti documentati**: 21 carte (due possibili mancabili nello Starlet Motel entro il Capitolo 2), 20 WAiNK, 5 poster playlist, 6 immersioni, 24 salti acrobatici. Fonti WIP, nessun pin fittizio. Restano 27 immersioni non localizzate in questa selezione.
- Monitoraggio fotografico dell'account X tramite bot in sola lettura e coda GitHub per la revisione umana (abilitazione API X esplicitamente opzionale): nessun uso delle immagini senza permesso e nessun post social automatico.

## Copertine social per URL + artwork ufficiale Rockstar (21 novembre 2026)

Il generatore `social_cards_v2.py` produce per **ogni pagina canonica** una copertina JPEG 1200×630 dedicata, aggiorna i metadata `og:image` e `twitter:image` e pubblica `social-cards-audit.json` con numero pagine/immagini uniche e stato dell'import. La chiave è SHA-256 del percorso relativo canonico, coerente con `social_media_gate_v2.py` nel bot. Le copertine hanno un titolo specifico; un banner promozionale non è mai descritto come screenshot di gameplay o prova del trofeo.
L'import opzionale di `https://media-rockstargames-com.akamaized.net/VI/downloads/artwork_wallpapers/GTAVI_Artwork_Wallpapers.zip` viene tentato dalla build di produzione GitHub (timeout/dimensioni/formati e deduplicazione percettiva); se il server non è raggiungibile, le copertine originali sono comunque tutte diverse. Non archiviare lo ZIP né interpretare un download ufficiale come licenza illimitata per riuso commerciale. Immagini attribuite nell'alt, distinte dagli screenshot delle guide.
Atlante esteso da 76 a **92 checkpoint**: 21 carte, 36 WAiNK, 6 immersioni, 5 playlist e 24 salti, in 7 aree, con nuove sculture e landmark da Push Square. Copertura parziale; 27 immersioni ancora senza luoghi documentati.
