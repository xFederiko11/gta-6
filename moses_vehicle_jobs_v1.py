"""Original compact GTA VI Moses vehicle jobs, based on credited walkthroughs.

A separate optional chain, NOT the Chapter 2 first-vehicle registration.
Do not mirror PowerPyx screenshots or imply a photo has been rights-cleared.
"""
from __future__ import annotations
from html import escape

PATH="guide-e-tutorial/veicoli-per-moses/"
SOURCE="https://www.powerpyx.com/gta-6-steal-vehicles-for-moses-walkthrough/"
GIFT="https://www.powerpyx.com/gta-6-collect-moses-gift-walkthrough/"
DAILY="https://www.powerpyx.com/gta-6-daily-driver-steal-the-crawler-for-moses-walkthrough/"
# Official embed version distributed by Yahoo for IGN's real vehicle walkthrough.
# It shows the actual gameplay without copying images or video into this repository.
IGN_EMBED="https://tech.yahoo.com/videos/gta-6-moses-vehicle-locations-222512470.html?format=embed"
IGN_SOURCE="https://tech.yahoo.com/videos/gta-6-moses-vehicle-locations-222512470.html"
IGN_CHAPTERS=("01:41","03:11","04:53","05:46","07:08","08:40")

TASKS=(
    ("Declasse Yosemite 1500","1.850 GTA$",
     "Bastion Street, quartiere a sud-ovest di Port Gellhorn",
     "Cerca il pickup su un carro attrezzi, nel vialetto a est della zona indicata. Metti KO il conducente e sgancia il mezzo agendo dietro al carro.",
     "Il pickup è libero dal gancio: guidalo all’officina di Moses."),
    ("Karin Futo","1.500 GTA$",
     "Draper Island Docks, margine meridionale",
     "Entra nell’edificio dal lato nord. Il Futo è nel garage sul lato ovest: apri il portone usando il comando vicino. La zona è sorvegliata.",
     "Esci dal garage senza danneggiare inutilmente l’auto e consegnala."),
    ("Annis Hellion","1.400 GTA$",
     "Orchard Avenue, case nel sud di Port Gellhorn",
     "Trova il fuoristrada nel vialetto della casa al centro della zona di ricerca. Il cane del cortile può attirare l’attenzione.",
     "Sali sul veicolo e raggiungi Moses."),
    ("BF Bandito","3.350 GTA$",
     "Buckskin Swamp, Kelly County sud-orientale",
     "Individua il buggy argentato fra i fuoristrada in movimento. Avvicinati al conducente, fallo fermare e prendi il mezzo. Ha un solo posto.",
     "Allontanati dagli inseguitori e consegna il Bandito a Moses."),
    ("Declasse Vamos","4.200 GTA$",
     "Casa a nord-est di Grayson",
     "Raggiungi il capanno a est della casa e digita 2727 sulla tastiera della porta laterale. Il codice è mostrato dentro il trailer. Apri il portone e prendi la Vamos.",
     "Esci evitando gli uomini armati, poi consegna l’auto."),
    ("Western Nightblade","6.310 GTA$",
     "Base dei Final Chapter ad Ambrosia",
     "Prepara armatura e armi prima di entrare. La moto arancione si trova al piano inferiore del garage centrale. Puoi entrare dal container verde a nord per un accesso meno esposto.",
     "Porta fuori la moto dalla base, supera gli ostili e consegnala."),
    ("Moses’ Sultan — regalo finale","Veicolo speciale",
     "Watkins Auto Parts, Port Gellhorn",
     "Dopo tutte e sei le consegne attendi il messaggio di Moses. Apri il garage piccolo accanto all’officina principale e trova la sua Sultan.",
     "Per conservarla, verifica prima la disponibilità e procedi alla registrazione quando possibile.")
)

def e(v):
    return escape(str(v),quote=True)

def validate():
    if len(TASKS)!=7 or len({row[0] for row in TASKS})!=7:
        raise ValueError("Six sourced cars plus one final gift required")
    for row in TASKS:
        if len(row)!=5 or any(not isinstance(v,str) or len(v)<8 for v in row):
            raise ValueError("Incomplete practical objective")
    if "2727" not in TASKS[4][3] or "Daily Driver" in TASKS[0][3]:
        raise ValueError("Unverified guide summary")
    if len(IGN_CHAPTERS)!=6 or not IGN_EMBED.endswith("?format=embed"):
        raise ValueError("Only sourced, publisher-supplied gameplay embed allowed")
    return True

def render(base):
    validate()
    body=[
      '<section class="v-intro v-guide-intro"><span class="v-tag">GUIDA COMPLETA · PS5 / PS5 PRO</span>',
      '<h1>Le 6 auto da rubare per Moses: luoghi e ricompense</h1>',
      '<p>Missioni facoltative dopo Daily Driver, non la missione della prima auto personale.</p></section>',
      '<div class="v-guide-layout v-guide-single"><article class="v-guide-main">',
      '<section class="v-operation-brief" aria-label="Prima di iniziare">',
      '<h2>Prima di iniziare</h2><dl>',
      '<div><dt>Quando</dt><dd>Capitolo 2, dopo Daily Driver</dd></div>',
      '<div><dt>Dove</dt><dd>Consegne all’officina Moses, Port Gellhorn</dd></div>',
      '<div><dt>Premio</dt><dd>18.610 GTA$ di base in totale, più bonus condizioni e Moses’ Sultan</dd></div>',
      '</dl></section>',
      '<p class="v-guide-urgent" role="note"><strong>🏆 Platino:</strong> secondo le fonti citate,',
      ' queste consegne sono facoltative e non richieste per i trofei. Evita danni ai',
      ' veicoli: il bonus dipende dalle condizioni di consegna.</p>',
      '<section id="procedura" class="v-tutorial" data-moses-full-article="true" aria-labelledby="titolo-procedura">',
      '<header class="v-tutorial-head"><span class="v-tutorial-start-here">▶ IL TUTORIAL INIZIA QUI</span>',
      '<h2 id="titolo-procedura">Tutti i 6 veicoli + il regalo finale</h2>',
      '<p>Scorri la guida completa: nessun passaggio nascosto. Moses comunica i veicoli nell’ordine',
      ' indicato; consegnane uno per ricevere il successivo.</p></header>',
      '<nav class="mo-quick-nav" aria-label="Vai direttamente a un veicolo">',
      '<strong>Vai al veicolo:</strong><div class="mo-quick-items">'
    ]
    for i,(name,reward,where,action,check) in enumerate(TASKS,1):
        body.append('<a href="#passaggio-'+str(i)+'">'+str(i)+' · '+e(name)+'</a>')
    body.append('</div></nav><ol class="v-steps">')
    for i,(name,reward,where,action,check) in enumerate(TASKS,1):
        source=GIFT if i==7 else SOURCE
        body.extend([
          '<li class="v-step" id="passaggio-'+str(i)+'"><div class="v-step-head">',
          '<span class="v-step-n" aria-hidden="true">'+str(i).zfill(2)+'</span><div>',
          '<span class="v-step-kicker">VEICOLO '+str(i)+' DI 7</span>',
          '<h3>'+e(name)+' <small class="mo-reward">'+e(reward)+'</small></h3>',
          '<p class="mo-where"><strong>📍 DOVE:</strong> '+e(where)+'</p>',
          '<p class="mo-action"><strong>🎮 COSA FARE:</strong> '+e(action)+'</p></div></div>'
        ])
        if i<=6:
            minute=IGN_CHAPTERS[i-1]
            body.extend([
                '<section class="mo-inline-scene" data-moses-scene data-moses-time="'+e(minute)+'">',
                '<strong>🎥 VIDEO DEL LUOGO E DELL’AUTO</strong>',
                '<button type="button" data-moses-watch aria-expanded="false">',
                '▶ Mostra il gameplay qui · minuto '+e(minute)+'</button>',
                '<div class="mo-scene-player" data-moses-scene-player hidden></div>',
                '<small>Video originale di <a href="'+e(IGN_SOURCE)+
                '" target="_blank" rel="noopener noreferrer">IGN ↗</a>',
                ' · inizio del veicolo a '+e(minute)+'. Se non parte dal minuto giusto, sposta la barra del video.</small>',
                '</section>'
            ])
        body.extend([
          '<p class="mo-photo-link">📷 <a href="'+e(source)+
          '" target="_blank" rel="noopener noreferrer">Vedi le fotografie del luogo su PowerPyx ↗</a>',
          '<small>Fonte immagini: PowerPyx · consultabili sul sito originale, non ripubblicate senza permesso.</small></p>',
          '<p class="v-check"><strong>✓ COME VERIFICARE:</strong> '+e(check)+'</p>',
          '</li>'
        ])
    body.extend([
      '</ol><p class="v-tutorial-finish"><strong>FINE DEL TUTORIAL</strong> · Le sei consegne sono concluse: il regalo è il settimo passo.</p>',
      '</section>',
      '<section class="mo-visible-sources" id="approfondimenti">',
      '<h2>Fonti e note utili</h2>',
      '<p>I luoghi descritti sono aree di ricerca, non coordinate GPS esatte.',
      ' I compensi indicati sono quelli base pubblicati da PowerPyx;',
      ' i bonus per le condizioni possono variare.</p>',
      '<p>Per iniziare la serie di consegne devi prima registrare un’auto con Moses e',
      ' completare Daily Driver. <a href="'+e(base+'salvare-auto/')+
      '">Prima auto personale: guida separata ↗</a></p>',
      '<ul><li><a href="'+e(SOURCE)+'" target="_blank" rel="noopener noreferrer">',
      'Foto e walkthrough delle sei auto — PowerPyx ↗</a></li>',
      '<li><a href="'+e(IGN_SOURCE)+'" target="_blank" rel="noopener noreferrer">',
      'Filmato di gameplay dei sei veicoli — IGN ↗</a></li>',
      '<li><a href="'+e(GIFT)+'" target="_blank" rel="noopener noreferrer">',
      'Regalo finale Moses’ Sultan — PowerPyx ↗</a></li>',
      '<li><a href="'+e(DAILY)+'" target="_blank" rel="noopener noreferrer">',
      'Missione Daily Driver — PowerPyx ↗</a></li></ul>',
      '<p class="mo-publisher-note">Le immagini PowerPyx non sono caricate su questo sito:',
      ' l’autore richiede autorizzazione scritta per riutilizzarle. Il filmato IGN',
      ' si carica soltanto quando selezioni Mostra il gameplay.</p>',
      '</section></article></div>'
    ])
    return ''.join(body)
