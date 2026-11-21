"""Spoiler-conscious GTA VI platinum roadmap, using the existing 55-trophy catalog.

The checklist is a local planning tool, never a PSN claim or a glitch safety
certificate. Launch-week source: PowerPyx, checked 21 November 2026.
"""
from __future__ import annotations

from html import escape

BASE = "https://xfederiko11.github.io/gta-6/"
ROADMAP_PATH = "trofei/roadmap-platino/"
POWERPYX = "https://www.powerpyx.com/gta-6-grand-theft-auto-vi-trophy-guide-roadmap/"
WALKTHROUGH = "https://www.powerpyx.com/gta-6-full-walkthrough-all-missions/"
MEDITATIONS = "https://www.powerpyx.com/gta-6-all-meditation-spot-locations/"
CHALLENGES = "https://www.powerpyx.com/gta-6-all-challenges-guide/"
CHECKLIST = "https://www.powerpyx.com/gta-6-100-completion-checklist-guide/"

# Steps deliberately describe priorities rather than inventing an optimal
# mission-by-mission route or guaranteeing that an exploit is Trophy Safe.
PHASES = (
    {
        "id": "prima-di-partire", "title": "Prima di partire",
        "timing": "Prima partita · PS5 / PS5 Pro",
        "description": "Prepara una partita orientata ai trofei prima di accumulare ore.",
        "tasks": (
            ("Leggi l'avviso sui trofei mancabili e crea un primo salvataggio manuale separato.", "trofei/"),
            ("Gioca normalmente: non ci sono livelli di difficoltà da scegliere per ottenere i trofei.", None),
            ("Non attivare trucchi durante la run del platino: le fonti segnalano blocco di trofei e salvataggi nella sessione.", "trucchi/"),
        ),
    },
    {
        "id": "capitolo-uno", "title": "Capitolo 1: proteggi la meditazione",
        "timing": "Prima di abbandonare Key Lento",
        "description": "Il checkpoint più importante: una meditazione può scomparire dopo il capitolo.",
        "tasks": (
            ("Dopo Down to Earth, quando Lucia parla della meditazione, seguila sul balcone e completa la sessione.", "guide-e-tutorial/meditazione-capitolo-1/"),
            ("Controlla che il contatore delle meditazioni sia aumentato; il primo evento potrebbe non avere una normale icona sulla mappa.", "guide-e-tutorial/meditazione-capitolo-1/"),
            ("Conserva un salvataggio manuale distinto prima di Recalibration: il finale del Capitolo 1 è un punto di non ritorno per attività e risorse iniziali.", "guide-e-tutorial/soldi-facili-capitolo-1/"),
        ),
    },
    {
        "id": "storia", "title": "Capitoli 2–5: storia e attività utili",
        "timing": "Durante la storia",
        "description": "Procedi senza dover rifare le missioni: la guida di lancio non indica mission replay né medaglie Oro di missione.",
        "tasks": (
            ("Dopo Coffee Break puoi lavorare alle meditazioni con entrambi i personaggi; controlla separatamente i progressi.", "guide-e-tutorial/meditazione-capitolo-1/"),
            ("Registra auto e scansiona veicoli quando sblocchi le attività, senza confondere il garage con la registrazione.", "salvare-auto/"),
            ("Fai le attività facoltative con clessidra quando compaiono se vuoi vedere tutta la storia; le fonti non le indicano come necessarie per il platino.", None),
            ("Mantieni un salvataggio manuale a inizio/fine capitolo, soprattutto se vuoi poter rivedere attività non ripetibili.", None),
        ),
    },
    {
        "id": "cento-percento", "title": "Dopo la storia: checklist 100%",
        "timing": "Free roam dopo il finale",
        "description": "Il menu del 100% si rende visibile dopo la storia; i progressi precedenti restano conteggiati.",
        "tasks": (
            ("Apri la checklist 100% nel menu Progressi e verifica le categorie ancora incomplete.", None),
            ("Completa 70 delle 80 sfide: puoi scegliere quali dieci lasciare fuori, salvo altri requisiti individuali.", "guide-e-tutorial/70-sfide-100-percento/"),
            ("Confronta le categorie residue con la guida 100%, senza presumere che il completamento totale del database sia obbligatorio.", None),
        ),
    },
    {
        "id": "pulizia", "title": "Pulizia finale: trofei individuali",
        "timing": "Prima del Platino",
        "description": "Il trofeo del 100% non sostituisce tutti gli altri 54 requisiti.",
        "tasks": (
            ("Controlla tutti i luoghi delle meditazioni e il trofeo dedicato, non fermarti al minimo richiesto per il 100%.", "guide-e-tutorial/meditazione-capitolo-1/"),
            ("Completa le medaglie Oro dei poligoni richieste dal trofeo individuale, verificando ogni contatore.", "trofei/medaglie-oro/"),
            ("Confronta i 55 trofei con il menu PS5: spunta quelli ottenuti nella checklist del sito solo come promemoria.", "trofei/"),
            ("Prova eventuali glitch solo su salvataggi separati quando la sicurezza dei trofei non è documentata; non usarli come scorciatoia obbligatoria.", None),
        ),
    },
)


def render(trophies):
    """Return the published page body; source links are ordinary audited URLs."""
    if len(trophies) != 55 or len({t["number"] for t in trophies}) != 55:
        raise ValueError("The official-sized 55-trophy catalog is required")
    by_number = {t["number"]: t for t in trophies}
    for required in (1, 14, 17, 28):
        if required not in by_number:
            raise ValueError("Critical trophy number absent: " + str(required))
    total = sum(len(phase["tasks"]) for phase in PHASES)
    parts = [
        '<section class="p-roadmap" data-platinum-roadmap data-step-total="' + str(total) + '">',
        '<header class="p-roadmap-hero"><span class="eyebrow">🏆 GTA VI · PS5 / PS5 PRO</span>',
        '<h1>Roadmap Platino GTA 6: il percorso senza errori</h1>',
        '<p>Una guida operativa in cinque fasi: salva la meditazione del Capitolo 1, ', 
        'finisci la storia, completa il 100% e verifica i trofei individuali. ', 
        'Le caselle sono promemoria locali: <strong>non leggono il tuo account PSN</strong>.</p>',
        '<div class="p-roadmap-stats" role="group" aria-label="Riepilogo percorso">',
        '<div><strong>55</strong><small>trofei PS5</small></div>',
        '<div><strong>0</strong><small>trofei online segnalati</small></div>',
        '<div><strong>~200 h</strong><small>stima PowerPyx, non garantita</small></div>',
        '</div><nav class="p-roadmap-links" aria-label="Collegamenti rapidi">',
        '<a class="v-button" href="' + BASE + 'trofei/">Tutti i 55 trofei →</a>',
        '<a class="v-button secondary" href="' + BASE + 'guide-e-tutorial/meditazione-capitolo-1/">Meditazione mancabile →</a>',
        '<a class="v-button secondary" href="#guida-55-trofei">Strategia per tutti i 55 trofei ↓</a>',
        '<a class="v-button secondary" href="' + BASE + 'mappe-guide/">Mappe e posizioni delle guide →</a>',
        '</nav></header>',
        '<aside class="p-roadmap-warning" role="note"><h2>⚠️ Il rischio del Capitolo 1</h2>',
        '<p>La meditazione iniziale a casa di Jason diventa inaccessibile dopo il capitolo. ', 
        'PowerPyx non ha ancora stabilito con certezza se sia indispensabile per ', 
        '<strong>Positive Mental Attitude</strong>: trattala come potenzialmente mancabile. ', 
        'Completa la sessione e conserva un salvataggio precedente.</p>',
        '<p>I trucchi sono segnalati come incompatibili con trofei e salvataggi ', 
        'nella sessione di utilizzo. Nessun glitch è definito «Trophy Safe» senza ', 
        'una verifica separata.</p></aside>',
        '<div class="p-roadmap-summary" aria-live="polite">',
        '<div><strong data-roadmap-count>0 / ' + str(total) + ' attività segnate</strong>',
        '<p data-roadmap-storage>Progressi salvati solo nel browser corrente.</p></div>',
        '<progress data-roadmap-progress max="' + str(total) + '" value="0"',
        ' aria-label="Attività del percorso completate"></progress></div>',
    ]
    for i, phase in enumerate(PHASES, 1):
        parts.extend([
            '<section class="p-roadmap-phase" id="' + escape(phase["id"]) + '" data-roadmap-phase>',
            '<div class="p-roadmap-phase-head"><span class="p-roadmap-index">' + str(i).zfill(2) + '</span>',
            '<div><span class="p-roadmap-timing">' + escape(phase["timing"]) + '</span>',
            '<h2>' + escape(phase["title"]) + '</h2>',
            '<p>' + escape(phase["description"]) + '</p></div>',
            '<strong class="p-roadmap-phase-count" data-phase-count>0 / ' + str(len(phase["tasks"])) + '</strong></div>',
            '<ol class="p-roadmap-tasks">',
        ])
        for j, (label, link) in enumerate(phase["tasks"], 1):
            key = phase["id"] + "-" + str(j)
            parts.append(
                '<li><label><input type="checkbox" data-roadmap-check="' + escape(key) + '">'
                '<span>' + escape(label) + '</span></label>'
                + (' <a href="' + BASE + escape(link) + '">Apri la guida →</a>' if link else '')
                + '</li>'
            )
        parts.append('</ol></section>')
    parts.extend([
        '<section class="p-roadmap-critical"><h2>Tre schede da tenere a portata di mano</h2>',
        '<p>Il 100%, le meditazioni e i poligoni hanno controlli distinti. Le schede ', 
        'di seguito rimandano ai requisiti del sito e si aggiornano solo quando ', 
        'segni manualmente il relativo trofeo nella sua pagina.</p>',
        '<div class="p-roadmap-trophy-grid">',
    ])
    for number in (28, 14, 17):
        trophy = by_number[number]
        href = BASE + 'trofei/' + escape(trophy["slug"]) + '/'
        parts.append(
            '<a class="p-roadmap-trophy" data-roadmap-trophy="' + str(number) +
            '" href="' + href + '"><strong>' + escape(trophy["name_it"]) +
            '</strong><span>' + escape(trophy["tier"]) +
            ' · <span data-roadmap-trophy-status>da verificare su PS5</span></span></a>'
        )
    parts.extend([
        '</div></section>',
        '<section class="p-roadmap-sources" id="fonti-platino"><h2>Fonti e limiti della guida</h2>',
        '<p>Verifica editoriale del 21 novembre 2026. Le stime di tempo, la ', 
        'disponibilità delle missioni e l\'eventuale mancabilità possono cambiare ', 
        'con nuove patch e riscontri della community. Nessun dato PSN viene letto.</p><ul>',
        '<li><a href="' + POWERPYX + '">PowerPyx — roadmap trofei</a></li>',
        '<li><a href="' + WALKTHROUGH + '">PowerPyx — missioni, capitoli e replay</a></li>',
        '<li><a href="' + MEDITATIONS + '">PowerPyx — meditazioni e punto mancabile</a></li>',
        '<li><a href="' + CHALLENGES + '">PowerPyx — 70 sfide su 80</a></li>',
        '<li><a href="' + CHECKLIST + '">PowerPyx — checklist 100%</a></li>',
        '</ul></section></section>',
    ])
    return ''.join(parts)
