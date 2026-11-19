"""Interactive, source-attributed trophy experience for GTA VI PS5.

All visual ornament is CSS/SVG authored for this site. External videos are
embedded only after the user clicks and are clearly marked when illustrative.
"""
from __future__ import annotations
from html import escape

SHOOTING_SOURCE="https://www.powerpyx.com/gta-6-all-shooting-range-gold-medal-challenges/"
OFFICIAL_VIDEO="https://www.youtube.com/watch?v=tJbzMqJGH4k&t=1112s"
RANGES=(
    ("Griffin Shooting Range", "18", (
       ("3-Point Range",("Principiante","Intermedio","Avanzato")),
       ("Hook Range",("Principiante","Intermedio","Avanzato")),
       ("Loop Range",("Principiante","Intermedio","Avanzato")),
       ("Maze Range",("Principiante","Intermedio","Master")),
       ("Compound Range",("Principiante","Intermedio","Master")),
       ("Villa Range",("Principiante","Intermedio","Master"))
    )),
    ("Rodgers Ranch", "24", (
       ("Market Range",("Principiante","Intermedio","Avanzato","Master")),
       ("Zombie Range",("Principiante","Intermedio","Avanzato","Master")),
       ("Hunting Range",("Principiante","Intermedio","Avanzato","Master")),
       ("Saloon Range",("Principiante","Intermedio","Avanzato","Master")),
       ("Cops & Robbers Range",("Principiante","Intermedio","Avanzato","Master")),
       ("Alien Range",("Principiante","Intermedio","Avanzato","Master"))
    ))
)
assert sum(len(levels) for _,_,courses in RANGES for _,levels in courses)==42


def e(value):
    return escape(str(value),quote=True)


def ornament(tier):
    """Original vector art, not an unofficial in-game screenshot."""
    color={"Platino":"#c2fdff","Oro":"#ffd494",
           "Argento":"#dae7ff","Bronzo":"#edb89c"}.get(tier,"#c2fdff")
    return (f'<svg class="trophy-art" width="280" height="230" viewBox="0 0 280 230" '
            'role="img" aria-label="Illustrazione originale di un bersaglio">'
            '<defs><radialGradient id="trophyglow">'
            f'<stop stop-color="{color}" stop-opacity=".34"/><stop offset="1" '
            f'stop-color="{color}" stop-opacity="0"/></radialGradient></defs>'
            '<circle cx="140" cy="112" r="110" fill="url(#trophyglow)"/>'
            f'<circle cx="140" cy="112" r="86" fill="none" stroke="{color}" stroke-opacity=".22" stroke-width="2"/>'
            f'<circle cx="140" cy="112" r="62" fill="none" stroke="{color}" stroke-opacity=".54" stroke-width="3"/>'
            f'<circle cx="140" cy="112" r="36" fill="none" stroke="{color}" stroke-opacity=".8" stroke-width="4"/>'
            f'<circle cx="140" cy="112" r="12" fill="{color}"/>'
            f'<path d="M140 8v40m0 128v40M36 112h40m128 0h40" stroke="{color}" stroke-width="3" '
            'stroke-linecap="round" stroke-opacity=".62"/></svg>')


def related_trophies(current, all_trophies, url):
    picks=[]
    for number in (14,17,35,1):
        t=next((x for x in all_trophies if x["number"]==number),None)
        if t and t["number"]!=current["number"] and not t["hidden"]:
            picks.append(t)
        if len(picks)==3:
            break
    links="".join(
        f'<a class="discovery-card" href="{url("trofei/"+t["slug"]+"/")}">'
        f'<span class="discovery-label">🏆 {e(t["tier"])} · TROFEO {t["number"]:02d}</span>'
        f'<strong>{e(t["name_it"])}</strong>'
        f'<span>Scopri la guida →</span></a>' for t in picks)
    return (
        '<section class="section discover-more" aria-label="Trofei correlati">'
        '<div class="section-head"><div><span class="eyebrow">PROSSIMO OBIETTIVO</span>'
        '<h2>Continua verso il platino</h2></div></div>'
        '<div class="discovery-rail">'+links+'</div></section>'
    )


def video_panel():
    # This is an official gameplay *preview*, NOT a 42-medal walkthrough.
    return (
        '<section class="section media-showcase" id="video">'
        '<div class="section-head"><div><span class="eyebrow">▶ VIDEO UFFICIALE</span>'
        '<h2>Guarda il poligono in azione</h2></div></div>'
        '<p>Una sequenza dell’anteprima Rockstar mostra l’attività intorno al minuto 18:32. '
        '<strong>È un riferimento visivo, non una guida a tutte le medaglie.</strong></p>'
        '<div class="video-consent" data-video-slot>'
        '<button class="video-launch" type="button" data-video-id="tJbzMqJGH4k" '
        'data-video-start="1112" aria-label="Riproduci la sequenza del poligono dal video ufficiale Rockstar">'
        '<img loading="lazy" decoding="async" '
        'src="https://i.ytimg.com/vi/tJbzMqJGH4k/hqdefault.jpg" '
        'alt="" onload="this.classList.add(\'media-loaded\')" '
        'onerror="this.remove()">'
        '<span class="video-play" aria-hidden="true">▶</span>'
        '<span class="video-callout">Riproduci dal minuto 18:32</span></button></div>'
        '<p class="micro">Player YouTube caricato soltanto dopo il clic. '
        f'<a href="{e(OFFICIAL_VIDEO)}" target="_blank" rel="noopener noreferrer">'
        'Apri l’originale sul canale Rockstar Games ↗</a></p></section>'
    )


def shooting_tracker():
    sections=[]
    for group,index_total,courses in RANGES:
        course_rows=[]
        for name,levels in courses:
            key=group.lower().replace(" ","-")
            controls="".join(
                f'<label class="medal-toggle"><input type="checkbox" '
                f'data-medal-id="{e(key+"-"+name.lower().replace(" ","-")+"-"+str(n))}">'
                f'<span class="medal-chip">🥇 {e(level)}</span></label>'
                for n,level in enumerate(levels,1))
            course_rows.append(
                '<div class="medal-course">'
                f'<h4>{e(name)}</h4>'
                '<div class="medal-options" role="group" '
                f'aria-label="Medaglie Oro {e(name)}">{controls}</div></div>'
            )
        sections.append(
            '<details class="medal-group" open>'
            f'<summary><span><strong>{e(group)}</strong><small>6 percorsi · '
            f'{e(index_total)} medaglie Oro</small></span><span class="medal-group-arrow">⌄</span></summary>'
            '<div class="medal-course-list">' + "".join(course_rows) + '</div></details>'
        )
    return (
        '<section class="shooting-tracker" id="checklist-cecchino" data-medal-tracker>'
        '<div class="section-head"><div><span class="eyebrow">CHECKLIST PERSONALE</span>'
        '<h2>Le tue 42 medaglie Oro</h2></div>'
        '<div class="medal-count" aria-live="polite" data-medal-count>0 / 42</div></div>'
        '<p>Spunta una difficoltà soltanto dopo aver ottenuto la medaglia Oro in gioco. '
        'Questa checklist non legge il salvataggio PS5.</p>'
        '<progress class="medal-progress" data-medal-progress max="42" value="0" '
        'aria-label="Progressi personali delle medaglie Oro"></progress>'
        '<div class="medal-location-grid">'+ "".join(sections) +'</div>'
        '<div class="tracker-footer"><span data-medal-feedback role="status" aria-live="polite">'
        'I progressi sono conservati soltanto in questo browser, quando disponibile.</span>'
        '<button type="button" class="tracker-reset" data-medal-reset>Azzerare checklist</button>'
        '</div><p class="micro">Percorsi e difficoltà: '
        f'<a href="{e(SHOOTING_SOURCE)}" rel="noopener noreferrer" target="_blank">'
        'PowerPyx — 42 medaglie nei due poligoni ↗</a>.</p></section>'
    )


def shootist_content():
    return (
        '<section class="quick-route" aria-label="Procedura rapida">'
        '<div class="section-head"><div><span class="eyebrow">LA STRADA PIÙ DIRETTA</span>'
        '<h2>Come sbloccare Cecchino</h2></div></div>'
        '<div class="action-grid">'
        '<div class="action-step"><span>01</span><div><strong>Raggiungi i due poligoni</strong>'
        '<p>Griffin (area nord-occidentale di Vice City) e Rodgers Ranch '
        '(nord-est di Port Gellhorn).</p></div></div>'
        '<div class="action-step"><span>02</span><div><strong>Sblocca le prove</strong>'
        '<p>Acquista il Waiver Pass da 5 $ al banco di ciascun poligono. '
        'Le armi richieste possono essere noleggiate per 10 $.</p></div></div>'
        '<div class="action-step"><span>03</span><div><strong>Conquista tutte le medaglie Oro</strong>'
        '<p>Griffin: 18 medaglie. Rodgers Ranch: 24. '
        'Controlla il progresso sotto Progressi → Attività → Poligoni di tiro.</p></div></div>'
        '</div><p class="micro">Requisiti descritti da PowerPyx il 18 novembre 2026; '
        'percorso dei menu soggetto alla localizzazione italiana installata.</p></section>'
        +shooting_tracker()+video_panel()
    )
