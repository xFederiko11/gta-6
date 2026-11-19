# Analytics per GTA 6 / ITALIA — configurazione e metodo

## Stato

L'integrazione di **GoatCounter** è pronta ma **disattivata finché non imposti `GOATCOUNTER_CODE`** nelle variabili di GitHub Actions. Non esistono metriche di pagina o clic osservate da questo strumento prima di quell'attivazione. Non aggiungere credenziali o token nel codice: è sufficiente il sottodominio pubblico del progetto.

Il vecchio badge `hitscounter.dev`, già presente nel sito, resta indipendente: è un contatore delle richieste al badge, **non** una misura di utenti unici né dei clic sui collegamenti.

## Come attivare (una sola volta, scelta volontaria)

1. Crea un account per il sito `https://xfederiko11.github.io/gta-6/` su [GoatCounter](https://www.goatcounter.com/) e scegli il suo codice di sottodominio. Il servizio ospitato è attualmente offerto gratuitamente per utilizzi pubblici ragionevoli; non è garantita gratuità perpetua. Valuta i termini e la privacy del servizio prima di attivarlo.
2. Apri la repository [xFederiko11/gta-6](https://github.com/xFederiko11/gta-6) → **Settings → Secrets and variables → Actions → Variables → New repository variable**.
3. Nome esatto: `GOATCOUNTER_CODE`. Valore: **solo la parte iniziale del dominio** (per esempio `gta6italia` se il dashboard è `https://gta6italia.goatcounter.com`). Non inserire `https://`, password, token né l'intero URL.
4. Avvia manualmente [GTA 6 Italia - Website](https://github.com/xFederiko11/gta-6/actions/workflows/deploy-site.yml) con **Run workflow** su `main`, oppure attendi il successivo deploy. Una volta superati i test e completato GitHub Pages, il sito includerà il *loader locale* di analytics.
5. Visita una pagina dal browser senza protezioni che blocchino il servizio; poi controlla il tuo dashboard GoatCounter. Con protezioni anti-tracking o filtri pubblicitari è normale che alcune visite non siano registrate. Non presentare statistiche non ancora verificate.

**Per disattivare tutto:** elimina la variabile `GOATCOUNTER_CODE` e ripeti il deployment. Gli script analitici non verranno più inclusi nelle pagine generate; il badge pubblico hitscounter.dev è un'integrazione separata.

Non sono richieste modifiche alla repository del bot editoriale, a Buffer o ad X. Non esistono task ChatGPT programmati.

## Cosa sarà misurato (soltanto dopo l'attivazione)

- **Visualizzazioni per pagina e provenienza**: offerte dal dashboard GoatCounter tramite il suo script, con possibili sottostime dovute a blocchi dei browser.
- **Clic su link interni**: evento `click:<posizione>:<pagina-origine>:site-<destinazione>`. Esempio: da un trofeo a una guida correlata. Posizioni consentite: menu, suggerimenti, sidebar, fonte, footer, hero o contenuto.
- **Clic sulle fonti e su X**: eventi verso categorie di dominio consentite (`powerpyx`, `gtabase`, `youtube`, `social-x`, ecc.); non vengono inviati URL esterni completi, query o frammenti.
- **Interazioni utili**: clic per copiare passaggi, valori HDR o sequenze PS5 e per avviare video. Sono *azioni richieste*, non la prova che l'utente abbia giocato o sbloccato un trofeo.
- **Campagne social**: puoi usare URL con parametri UTM (`utm_source=x&utm_medium=social&utm_campaign=nome-rubrica`) quando condividi i link; GoatCounter dispone di funzioni per classificare campagne. Le nostre misurazioni personalizzate dei clic non copiano né archiviano tali parametri.

Lo script locale `site/assets/site-analytics.js` viene incorporato soltanto se `GOATCOUNTER_CODE` è presente e valido. Verifica l'hostname effettivo del sito, rispetta i segnali browser Global Privacy Control e Do Not Track prima di contattare GoatCounter, non usa cookie né localStorage per gli analytics e non legge ricerche o checklist personali. Se GoatCounter non risponde, pagine e link restano utilizzabili normalmente.

## Decisioni da prendere con dati veri

Dopo almeno una o due settimane di raccolta, guarda la *tendenza*, non il singolo clic:

| Domanda editoriale | Metrica da confrontare | Possibile azione |
|---|---|---|
| Quali guide attirano più interesse? | Visualizzazioni relative per pagina e tempo | Metti in evidenza guide cercate, migliorando i contenuti |
| La homepage porta alle sezioni? | Clic `click:home-hero:home:site-...` | Modifica posizione e testo delle CTA |
| I consigli correlati funzionano? | `click:recommended:<origine>:site-...` | Cambia i collegamenti fuori tema |
| Quale canale porta visitatori? | Referrer e campagne del dashboard | Migliora rubrica, orari e formato dei link social |
| I tutorial sono usabili? | Clic su `interaction:...:copy-...` e visualizzazioni | Riduci passaggi inutili o aumenta l'accessibilità |
| I video attirano clic? | `interaction:...:play-...` | Inserisci video soltanto dove pertinenti |

Non fare confronti tra traffico precedente e successivo all'attivazione come se fossero misurati nello stesso modo. Non confondere *clic*, *richieste al badge*, *pageview* e *persone uniche*. L'analisi deve inoltre tenere conto di pubblicazioni X, nuove patch e variazioni nella quantità dei contenuti.

## Privacy e manutenzione

La pagina pubblica `/gta-6/privacy/` descrive sia il vecchio badge esterno sia l'eventuale servizio di analytics aggregati. GoatCounter è una piattaforma terza e la sua documentazione GDPR non costituisce consulenza legale; per trattamenti/consenso bisogna considerare la normativa applicabile e la situazione effettiva del sito. Guida ufficiale: https://www.goatcounter.com/help/start e https://www.goatcounter.com/help/events.

Per non gonfiare le metriche con le tue visite, consulta [le istruzioni GoatCounter per escludere il tuo browser](https://www.goatcounter.com/help/skip-dev).

Non abbiamo creato un dashboard interno pubblico con numeri inventati né un servizio a pagamento. L'account e la scelta di attivare la misurazione restano sotto il tuo controllo.
