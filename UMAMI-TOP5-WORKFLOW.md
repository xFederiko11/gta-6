# Top 5 articoli: dati Umami gratuiti, senza nuovi abbonamenti

La classifica utilizza visualizzazioni di pagina, non utenti unici. L'export
Cloud completo descritto nella documentazione Umami include anche sessioni,
eventi e dati evento: **non caricarlo in GitHub**. Non inserire token o share
URL nel repository pubblico.

1. Nel dashboard Umami del sito, seleziona Pages e gli ultimi 7 giorni.
   Usa i conteggi di visualizzazione per pagina; non confondere Visitors,
   Visits o eventi personalizzati con le visualizzazioni delle pagine.
2. Ricava un CSV aggregato completo con sole colonne path,pageviews. Se il
   dashboard è paginato, includi tutte le righe. Non usare un campione
   troncato o mescolare periodi. I percorsi devono essere puliti, senza
   query string, e ciascuna pagina canonica deve avere un solo conteggio.
   Mantieni il CSV originale fuori dal repository.
3. Dalla root del repository:

    python3 import_umami_popular_v1.py /percorso/aggregati.csv --start AAAA-MM-GG --end AAAA-MM-GG --complete-report --approve-public-aggregates

   Sostituisci le date con quelle del report effettivo. Il comando valida
   senza scrivere. Dopo verifica, aggiungi --write per produrre
   data/popular_articles_v1.json, contenente soltanto fino a cinque
   URL canonici di articoli pubblici e i relativi conteggi aggregati,
   senza righe di homepage, raccolte, trofei segreti o dati privati.
4. Controlla il diff e integra soltanto il JSON sanificato. La build
   pubblica aggiorna la classifica indicando il periodo e Umami come fonte.
   Se il report è mancante, vecchio o non valido, il sito mantiene una
   lista esplicitamente editoriale. Non usare contatori inventati.

L'importatore non acquisisce dati da Umami autonomamente: serve un report
aggregato autentico fornito dall'account autorizzato. L'approvazione dei
conteggi pubblici non autorizza la pubblicazione dell'export grezzo.
Documentazione: https://docs.umami.is/docs/cloud/export-data
