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
IGN_VIDEO_ID="UyxxY0A_kow"
IGN_VIDEO="https://www.youtube.com/watch?v="+IGN_VIDEO_ID
# Official IGN video on YouTube, linked from the real publisher's channel.
# YouTube's privacy-enhanced player accepts start=N and is independently embeddable.

IGN_TIMELINE=((101,"01:41"),(191,"03:11"),(293,"04:53"),
              (346,"05:46"),(428,"07:08"),(520,"08:40"))
# Link to the publisher's own embeddable VIDEO PLAYER, never copied still frames.
# Each of the six chapters shows its actual corresponding car. Gift is not
# included in the footage, so do not label the video as evidence for the Sultan.
VISUAL_CUES=("Pickup giallo sul carro attrezzi","Coupé rossa dentro un garage",
             "Fuoristrada bianco nel vialetto","Buggy argentato in movimento",
             "Muscle car rossa in un capanno","Moto arancione nel garage")


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
    if len(IGN_TIMELINE)!=6 or len(VISUAL_CUES)!=6 or any(
       IGN_TIMELINE[k][0]>=IGN_TIMELINE[k+1][0] for k in range(5)):
        raise ValueError("Missing verified video chapters")
    return True

def render_source_visual(i, name):
    """Visual evidence is the publisher's permitted player, NOT copied photos."""
    if i==7:
        return ('<figure class="mo-visual mo-gift-visual" data-mo-gift-ref="source-only">'
                '<figcaption><strong>📷 Riconosci il regalo</strong>'
                '<span>Apri il piccolo garage accanto all’officina di Moses.'
                ' All’interno trovi la Sultan speciale.</span>'
                '<small><a href="'+e(GIFT)+'" target="_blank" rel="noopener noreferrer">'
                'Fonte: guida originale del regalo di Moses — PowerPyx ↗</a></small>'
                '<small>Non è disponibile qui un’immagine riutilizzabile verificata.'
                ' Non mostriamo foto di un veicolo diverso.</small></figcaption></figure>')
    seconds,stamp=IGN_TIMELINE[i-1]
    return (
        '<figure class="mo-visual" data-mo-real-gameplay="'+str(i)+'" '
        'data-mo-chapter-seconds="'+str(seconds)+'">'
        '<div class="mo-video-head"><strong>🎬 Guarda il veicolo e il luogo nel gameplay</strong>'
        '<span>'+e(VISUAL_CUES[i-1])+'</span></div>'
        '<div class="mo-video-screen"><iframe '
        'src="https://www.youtube-nocookie.com/embed/'+e(IGN_VIDEO_ID)+
        '?start='+str(seconds)+'&amp;rel=0" loading="lazy" '
        'title="IGN: GTA VI, tutti i veicoli di Moses — '+e(name)+'" '
        'referrerpolicy="strict-origin-when-cross-origin" '
        'allow="autoplay; encrypted-media; picture-in-picture; fullscreen" '
        'allowfullscreen></iframe></div>'
        '<figcaption>'
        '<strong>▶ Gameplay dal minuto '+e(stamp)+'</strong>'
        '<span>Il video è impostato su questo minuto. Se parte dall’inizio, vai a '
        +e(stamp)+' per vedere questa consegna.</span>'
        '<small class="mo-photo-link"><a href="'+e(IGN_VIDEO)+'&amp;t='+str(seconds)+'s" '
        'target="_blank" rel="noopener noreferrer">'
        'Fonte video: IGN su YouTube, player ufficiale incorporato ↗</a> · '
        '<a href="'+e(SOURCE)+'" target="_blank" rel="noopener noreferrer">'
        'Guarda anche le foto sulla guida PowerPyx ↗</a></small>'
        '<small>Non abbiamo copiato, ritagliato o ricaricato fotografie '
        'di altri editori.</small></figcaption></figure>'
    )


def render(base):
    validate()
    body=[
      '<section class="v-intro v-guide-intro"><span class="v-tag">GUIDA RAPIDA · PS5 / PS5 PRO</span>',
      '<h1>Le 6 auto da rubare per Moses: luoghi e ricompense</h1>',
      '<p>Missioni facoltative dopo Daily Driver, non la missione della prima auto personale.</p></section>',
      '<div class="v-guide-layout v-guide-single"><article class="v-guide-main">',
      '<section class="v-operation-brief" aria-label="Prima di iniziare">',
      '<h2>Prima di iniziare</h2><dl>',
      '<div><dt>Quando</dt><dd>Capitolo 2, dopo Daily Driver</dd></div>',
      '<div><dt>Dove</dt><dd>Consegne all’officina Moses, Port Gellhorn</dd></div>',
      '<div><dt>Premio</dt><dd>Denaro per auto + bonus condizioni; alla fine Moses’ Sultan</dd></div>',
      '</dl></section>',
      '<p class="v-guide-urgent" role="note"><strong>🏆 Platino:</strong> secondo le fonti citate,',
      ' queste consegne sono facoltative e non richieste per i trofei. Evita danni ai',
      ' veicoli: il bonus dipende dalle condizioni di consegna.</p>',
      '<section id="procedura" class="v-tutorial" data-mo-default-all aria-labelledby="titolo-procedura">',
      '<header class="v-tutorial-head"><span class="v-tutorial-start-here">▶ INIZIA QUI</span>',
      '<h2 id="titolo-procedura">LE 6 AUTO · GUIDA COMPLETA CON GAMEPLAY</h2>',
      '<p>Moses comunica i veicoli nell’ordine indicato. Consegna il precedente per sbloccare il successivo.</p>',
      '</header><div class="mo-viewbar"><button type="button" '
      'data-mo-show-all>📖 Mostra l’articolo completo (7 passaggi)</button></div>'
      '<ol class="v-steps">'
    ]
    for i,(name,reward,where,action,check) in enumerate(TASKS,1):
        body.extend([
          '<li class="v-step" id="passaggio-'+str(i)+'"><div class="v-step-head">',
          '<span class="v-step-n" aria-hidden="true">'+str(i).zfill(2)+'</span><div>',
          '<span class="v-step-kicker">PASSO '+str(i)+' DI 7</span>',
          '<h3>'+e(name)+' · '+e(reward)+'</h3>',
          '<p><strong>DOVE:</strong> '+e(where)+'</p>',
          '<p><strong>COSA FARE:</strong> '+e(action)+'</p></div></div>',
          render_source_visual(i,name),
          '<p class="v-check"><strong>✓ CONTROLLO:</strong> '+e(check)+'</p></li>'
        ])
    body.extend([
      '</ol><p class="v-tutorial-finish"><strong>FINE DELLA PROCEDURA</strong></p></section>',
      '<details class="v-guide-more" id="approfondimenti"><summary><span><strong>Fonti e approfondimenti</strong>',
      '<small>Non sono altri passaggi</small></span><span class="v-more-chevron">⌄</span></summary>',
      '<div class="v-guide-more-content"><p>Le zone indicate sono quelle della missione,',
      ' non pin GPS verificati. I pagamenti indicati sono i valori base documentati;',
      ' il bonus condizioni varia.</p>',
      '<p>Prima devi sbloccare la prima registrazione con Moses, poi completare Daily Driver.</p>',
      '<p><a href="'+e(base+'salvare-auto/')+'">Prima auto personale: guida separata →</a></p>',
      '<ul><li><a href="'+e(DAILY)+'" target="_blank" rel="noopener noreferrer">Daily Driver — PowerPyx ↗</a></li>',
      '<li><a href="'+e(SOURCE)+'" target="_blank" rel="noopener noreferrer">Sei auto da rubare — PowerPyx ↗</a></li>',
      '<li><a href="'+e(GIFT)+'" target="_blank" rel="noopener noreferrer">Regalo finale — PowerPyx ↗</a></li></ul>',
      '</div></details></article></div>'
    ])
    return ''.join(body)
