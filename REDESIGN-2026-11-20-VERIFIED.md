# Redesign pubblicato e verificato - 20 novembre 2026

## Pubblicazione reale

- PR implementata e unita: https://github.com/xFederiko11/gta-6/pull/31
- Commit pubblicato: `527e3a48944d193534eb43a52cbb0d24fac3ab0c`.
- Esecuzione di produzione: https://github.com/xFederiko11/gta-6/actions/runs/44658053309
- Job build `136029082053`: completato con successo, inclusi test dei contenuti precedenti e test sul nuovo HTML effettivamente generato.
- Job deploy `136029188943`: completato con successo.
- GitHub Pages ha confermato il deploy alle 02:04:02 UTC del 20 novembre 2026 (03:04:02 CET).
- Alle 02:04:03 UTC il controllo HTTP pubblico ha confermato risposta 200, marker `data-design-version="visual-v2-20261120"`, nuovi CSS/JS e canonical corretto per tutte e cinque le pagine sotto.

Pagine pubbliche verificate dopo il deploy:

- https://xfederiko11.github.io/gta-6/
- https://xfederiko11.github.io/gta-6/soldi-facili/
- https://xfederiko11.github.io/gta-6/auto-speciali/
- https://xfederiko11.github.io/gta-6/salvare-auto/
- https://xfederiko11.github.io/gta-6/guide-e-tutorial/soldi-facili-capitolo-1/

Il controllo e' stato eseguito dal runner di deploy sulle URL pubbliche, non soltanto sui file locali. Il browser di ricerca della sessione non riusciva ad aprire GitHub Pages; non viene presentato come una seconda verifica indipendente.

## Verifiche visive

- Prima QA browser: run `44657182120`.
- Rifinitura mobile e nuova QA: run `44657793177`.
- Ultimo commit della versione testata prima del merge: `035b947f7601558b6f05879d2f526a091fb9e1f6`.
- Nove casi renderizzati: home, garage e guida del negozio a 390, 768 e 1440 pixel.
- Tutti senza overflow orizzontale; nessuna immagine fallita nei nove casi.
- Testati anche ricerca, filtri, menu mobile, apertura/chiusura degli spoiler e persistenza della preferenza dopo il ricaricamento.
- Le schermate reali sono state ispezionate; prima della pubblicazione e' stato corretto il rapporto delle copertine su mobile, evitando l'immagine troppo alta.
- Artefatto delle schermate rifinite: `visual-refined-preview`, ID `14593837719` (conservazione temporanea di tre giorni).

## Cosa cambia

Home nuova, navigazione semplificata, palette chiara con navy/rosa/viola, sezioni Soldi facili, Auto e garage, salvataggio auto; dieci tutorial nel nuovo formato. Gli otto indirizzi delle guide precedenti sono mantenuti.

Tredici immagini selezionate, convertite in varianti WebP responsive: schermate reali e materiale promozionale distinti, testi alternativi, didascalie e attribuzione. Nel tutorial del negozio compaiono le mappe della fonte; nel tutorial auto compaiono officina, registrazione e richiamo dal telefono.

I dettagli sensibili partono chiusi; il lettore sceglie Mostra spoiler o Nascondi. I tutorial hanno requisiti, luogo, passaggi numerati, controlli quando documentati, rischi e fonti in basso. Restano canonical, metadata, sitemap, collegamenti alle sezioni esistenti e date derivate dai sorgenti.

## Confini della consegna

Non tutte le guide hanno ancora un'immagine verificata per ogni passaggio. Non sono stati usati i mockup generati come prova di gameplay, ne' introdotti numeri di visite inventati o mappe fittizie. La grafica riprende la direzione approvata, usando risorse reali e contenuti documentati invece dei dati di esempio del mockup.

Questa consegna riguarda il sito. Non modifica da sola cadenza, credenziali o coda Buffer/X e non dichiara nuovi post social pubblicati. Le nuove scoperte richiedono ancora la verifica editoriale descritta in `VISUAL-EDITORIAL-GUIDE.md`; non si presenta il feed come un autore automatico di guide verificate.
