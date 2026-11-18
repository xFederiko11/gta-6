# GTA 6 Italia — guide, tutorial e trofei

Portale pubblico e gratuito dedicato a **GTA VI su PS5 e PS5 Pro**. I contenuti sono in italiano.

**Indirizzo previsto:** https://xfederiko11.github.io/gta-6/

## Struttura

- **Homepage** — `/gta-6/`
- **Trofei** — `/gta-6/trofei/`: 55 schede individuali, requisiti Oro, protezione degli spoiler.
- **Guide e tutorial** — `/gta-6/guide-e-tutorial/`: consigli rapidi con procedura PS5, vantaggi e fonte.
- **Medaglie Oro** — `/gta-6/trofei/medaglie-oro/`.
- **SEO** — sitemap, robots, canonical, Open Graph, metadati e JSON-LD.

I contenuti sono separati dai template in `data/trofei.json` e `data/guide.json`.
Il generatore `build_site.py` produce il sito statico in `_site/` senza API e senza abbonamenti.

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
