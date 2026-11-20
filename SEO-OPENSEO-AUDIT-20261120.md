# GTA VI Italia — OpenSEO audit (20 novembre 2026)

Audit: https://app.openseo.so/p/99a43785-0c0a-45a3-aaaa-7883b4fa8c75/audit?auditId=fb235245-2ff7-46c8-8d04-1be28351c2f7

## Stato più recente — 20 novembre 2026, dopo le 21:15 (Europe/Rome)

**Proprietà verificata, sitemap inviata, OpenSEO collegato.** Google ha confermato con screenshot del proprietario la verifica sia tramite `google232edbd3526a5a1d.html` che tramite meta tag. La sitemap `https://xfederiko11.github.io/gta-6/sitemap.xml` è stata inviata correttamente. OpenSEO ora legge la proprietà URL-prefix con permessi `siteOwner`, non soltanto il progetto SEO senza account.

- Il **test in tempo reale** ha restituito «L'URL è disponibile per Google» per homepage, `/trofei/`, `/guide-e-tutorial/` e `/hdr-oled/`. Il proprietario ha confermato l'invio delle richieste; per la homepage è disponibile anche screenshot di «Indicizzazione richiesta». Non confondere il test live con l'indice.
- La lettura **Google Search Console URL Inspection API** successiva mostra **homepage e `/trofei/`: «Pagina scansionata, ma attualmente non indicizzata»**. La fetch è riuscita, robots consente la scansione, Google ha usato lo stesso canonical dichiarato. Le altre due directory sono ancora **«L'URL è sconosciuto a Google»** nell'ultimo indice disponibile, pur avendo superato il test live.
- Cinque URL aggiuntive (`/soldi-facili/`, `/auto-speciali/`, `/guide-e-tutorial/meditazione-capitolo-1/`, `/guide-e-tutorial/glitch-prima-persona-ps5/`, `/guide-e-tutorial/soldi-2500-three-sheets-liquor/`) erano ancora sconosciute all'indice in questa lettura: questo **non è un blocco tecnico accertato**.
- GSC Search Performance, `2026-10-21..2026-11-17`: **zero righe restituite**, non un dato accertato di zero visite. Il periodo non include il lancio del sito o i test odierni. **GA4 non collegata**; non sappiamo utenti, conversioni, clic su X o nuovi follower.
- È attivo un controllo automatico ChatGPT + OpenSEO delle quattro URL principali e dei primi dati organici, ogni giorno per 30 giorni dal 21 novembre: avvisa solo alla prima indicizzazione/visibilità o in caso di problema reale, senza nuove richieste di indicizzazione. È **separato dal bot GitHub**, che non possiede credenziali Google né deve accedere all'account del proprietario.
- Il tracciamento facoltativo delle CTA X/YouTube è già implementato in `growth_tracking_v1.py`, ma è attivabile soltanto tramite la variabile `UMAMI_WEBSITE_ID` di un sito Umami effettivamente creato. L'evento `x-follow-intent` indica un clic e non può dimostrare un nuovo follower.
- Prossima verifica utile: attendere la prima indicizzazione, leggere query/impression reali da GSC, poi configurare l'analytics opzionale con il proprietario. Non fare richieste ripetute o creare false metriche social.

### Audit tecnico già concluso

Dopo PR #62 (titoli 55 trofei, metadata 11 guide) e PR #63 (21 schede HDR OLED, 17 trucchi PS5), entrambi i deploy sono riusciti. Una terza scansione OpenSEO di **50 URL, 22 HDR**, ha rilevato **soltanto il limite di 50 pagine** e nessun altro problema sulle pagine di quel campione. Non equivale a certificare tutte le URL. [Rapporto aggiornato](https://app.openseo.so/p/99a43785-0c0a-45a3-aaaa-7883b4fa8c75/reports/0fd13efe-d00f-43b2-8419-bd89e1d062b5).

---

## Storico — audit prima della verifica GSC


- Progetto OpenSEO: **GTA VI Italia**; mercato **Italia/italiano**; proprietà editoriale: https://xfederiko11.github.io/gta-6/ (sottopercorso GitHub Pages del dominio condiviso, non un intero dominio esclusivo).
- Audit preliminare: **50 pagine su 115 URL individuati**, **34 segnalazioni** (una pagina-limit, 20 titoli lunghi, 5 meta description fuori intervallo, 4 gerarchie di intestazioni, 4 pagine `noindex` intenzionali). Nessuna segnalazione critica nel campione; **non è una certificazione completa delle 170+ pagine**.
- La sitemap ufficiale del sottosito è https://xfederiko11.github.io/gta-6/sitemap.xml. Il file `/gta-6/robots.txt` non equivale al file `/robots.txt` di dominio e non garantisce che Google scopra la sitemap automaticamente; inviarla esplicitamente nella Search Console URL-prefix appropriata, senza sovrascrivere il dominio root gestito da un'altra repository.
- Soluzioni: titoli SEO di massimo 60 caratteri sui 55 trofei senza troncare i nomi; titoli brevi per fonti, HDR e trucchi; meta-description sorgente per le 11 guide visuali (70–160 caratteri) senza togliere avvisi spoiler e incertezza dei trofei; H2 semantici nelle directory e H3 nelle schede di poligono.
- Il `noindex,follow` dei trofei nascosti è temporaneo **fino al 21 novembre 2026 UTC**; il generatore li include in sitemap quando la finestra termina. Il suo scopo è limitare spoiler nei primissimi giorni del lancio; non rimuoverlo per inseguire i punteggi dell'audit senza scelta editoriale esplicita.
- **Al momento della prima scansione, Google Search Console non era ancora collegata** ad OpenSEO (stato superato dall'aggiornamento sopra); **GA4 non collegata**. OpenSEO non dispone di dati Google reali su impression, clic, CTR, posizione, indicizzazione, utenti o conversioni. Nessun conteggio di follower può essere dedotto da Buffer, da un click su X o dalla scansione del sito.
- Umami resta **opt-in** tramite il solo `UMAMI_WEBSITE_ID` (UUID) in GitHub Pages; senza quel valore non viene caricato alcuno script di tracciamento. Non incollare credenziali o API token in repository pubbliche.
- Azione proprietario prevista nel primo audit (ora completata): configurare Search Console con proprietà **URL-prefix** `https://xfederiko11.github.io/gta-6/`, verificarla tramite il metodo consentito da Google e inviare `sitemap.xml`, quindi collegare l'account Google da OpenSEO → Search Performance. L'esito dipende dalla verifica della proprietà; non dichiarare che questa sia già riuscita.
- Riprova l'audit di pagina dopo il deploy; confronta le stesse 50 URL o usa sottosezioni, evitando di descrivere i 65 URL non verificati come privi di problemi.

**SEO e crescita:** misurare prima impression e query reali di Search Console, poi click X/YouTube con analytics consensuali configurati, poi confrontare i dati X follower solo quando disponibili. **Un click `x-follow-intent` non dimostra una conversione in follower.**
