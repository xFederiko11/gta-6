# GTA 6 Italia — guide, tutorial e trofei

Portale pubblico e gratuito dedicato a **GTA VI su PS5 e PS5 Pro**. I contenuti sono in italiano.

**Indirizzo previsto:** https://xfederiko11.github.io/gta-6/

## Struttura

- **Homepage** — `/gta-6/`
- **Trofei** — `/gta-6/trofei/`: 55 schede individuali, requisiti Oro, protezione degli spoiler.
- **Guide e tutorial** — `/gta-6/guide-e-tutorial/`: consigli rapidi con procedura PS5, vantaggi e fonte.
- **HDR OLED** — `/gta-6/hdr-oled/`: cerca marca, codice TV o diagonale; 13 famiglie e 50 codici per PS5 e PS5 Pro, pagine SEO per serie.
- **Medaglie Oro** — `/gta-6/trofei/medaglie-oro/`.
- **SEO** — sitemap, robots, canonical, Open Graph, metadati e JSON-LD.

I contenuti sono separati dai template in `data/trofei.json`, `data/guide.json` e `data/hdr_oled.json`.
L’indice OLED e le 13 pagine di famiglia sono generate da `hdr_catalog.py`, con fonti del produttore. Le impostazioni HDR specifiche di GTA VI non sono inventate: usare soltanto i controlli effettivamente disponibili nel gioco e nel firmware TV.
Il generatore `build_site.py` produce il sito statico in `_site/` senza API e senza abbonamenti.


## Novità v15.0: aggiornamento, visualizzazioni e X

Ogni pagina reale (homepage, indice trofei, 55 schede, indice e sei guide, medaglie Oro, indice HDR e 13 schede OLED) ha una microbarra immediatamente sotto la navigazione con:

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

- **13 famiglie:** LG C5/C6/G5/G6, Samsung S90F/S90H/S95F/S95H, Sony BRAVIA 8/8 II, Philips OLED850/OLED811 e Panasonic Z95A.
- **50 codici TV verificabili** nel catalogo, con diagonali in pollici. I codici italiani Panasonic hanno il suffisso **EG**; es. TV-55Z95AEG, TV-65Z95AEG.
- URL stabili sotto `/hdr-oled/<famiglia>/`; una pagina per gruppo di configurazioni, non una pagina duplicata per ciascuna diagonale.
- Ricerca client-side per sigla/serie/brand/pollici, canonical, sitemap, JSON-LD CollectionPage e Article, fonti e data di aggiornamento.
- Non indicare valori di nit, paper white o click PS5 come universali per tutti i pannelli: luminosità, firmware e impostazioni di tone mapping cambiano la resa. Non attribuire controlli HDR specifici a GTA VI senza verificarli.
- Per ampliare il catalogo, modificare `data/hdr_oled.json` e ripetere `python build_site.py && python -m unittest -q test_site.py`.

Fonti principali: [HDR PS5 - PlayStation](https://www.playstation.com/it-it/support/hardware/ps5-enable-adjust-hdr/), schede produttore direttamente in ogni famiglia.
