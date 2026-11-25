"""Evidence-based, build-time GTA VI meditation checklist.

Only HTML structure is generated here; browser progress is local and
never synced to a server/PSN. The site must not claim a trophy was unlocked.
"""
from __future__ import annotations
from html import escape as h
import json
from pathlib import Path
import re

FILE = Path("data/meditation_checklist_v1.json")
SOURCE_HOSTS = ("https://www.powerpyx.com/", "https://www.pushsquare.com/")

def validated(data):
    if not isinstance(data, dict) or data.get("schema") != "gta6-meditation-tracker-v1":
        raise ValueError("Unknown meditation data schema")
    spots = data.get("spots")
    if not isinstance(spots, list) or len(spots) != 10:
        raise ValueError("Must have precisely ten distinct meditation locations")
    if data.get("total_locations") != 10 or data.get("total_meditations") != 18 or data.get("target_100") != 15:
        raise ValueError("Meditation count must be 10 places / 18 sessions / 15 required for 100%")
    video=data.get("video",{})
    if (video.get("id")!="WZ9EM_i_W38" or video.get("creator")!="Maka91Productions"
            or video.get("url")!="https://www.youtube.com/watch?v=WZ9EM_i_W38"):
        raise ValueError("Unreviewed meditation video")
    seen, sessions, timestamps = set(), [], set()
    for index, spot in enumerate(spots):
        if not isinstance(spot, dict):
            raise ValueError("Invalid location")
        key = spot.get("id")
        modes = spot.get("modes")
        if not isinstance(key,str) or not re.fullmatch(r"[a-z0-9-]{3,48}", key) or key in seen:
            raise ValueError("Duplicate or invalid location")
        seen.add(key)
        second=spot.get("video_second")
        if type(second) is not int or not 0<=second<=600 or second in timestamps:
            raise ValueError("Invalid location video timestamp")
        timestamps.add(second)
        expected = ["one"] if index == 0 else ["final"] if index == 9 else ["jason", "lucia"]
        if modes != expected:
            raise ValueError("Unexpected character/session counts for "+key)
        if any(not isinstance(spot.get(field),str) or not minimum <= len(spot[field]) < 240
               for field,minimum in (("name",3),("region",3),("landmark",10))):
            raise ValueError("Location text invalid")
        if index == 0 and spot.get("phase") != "chapter1":
            raise ValueError("Lost Chapter 1 missable warning")
        if index == 9 and spot.get("phase") != "final":
            raise ValueError("Lost final meditation unlock warning")
        sessions.extend(key+":"+mode for mode in modes)
    for key in ("source", "corroboration", "trophy_source"):
        url=data.get(key)
        if not isinstance(url,str) or not url.startswith(SOURCE_HOSTS):
            raise ValueError("Invalid independent source")
    if len(sessions) != 18 or len(sessions) != len(set(sessions)):
        raise ValueError("Unstable meditation checkbox keys")
    return data

def render(data=None):
    if data is None:
        data=json.loads(FILE.read_text(encoding="utf-8"))
    data=validated(data)
    parts=[
        '<section class="v-meditation-tracker" id="meditazioni-checklist" data-meditation-tracker data-meditation-total="18" data-meditation-target="15">',
        '<div class="v-meditation-header"><span class="v-kicker">🏆 CHECKLIST PLATINO · SOLO NEL TUO BROWSER</span>',
        '<h2>10 luoghi, 18 meditazioni: controlla il tuo progresso</h2>',
        '<p>La checklist serve come promemoria, non legge i salvataggi PS5. Spunta soltanto dopo '
        'aver verificato la meditazione nel menu <strong>Progressi → Collezioni → Esplorazione → Meditazioni</strong>.</p></div>',
        '<div class="v-meditation-stats" aria-live="polite">',
        '<div><strong data-meditation-summary>0 / 18</strong><small>sessioni segnate</small></div>',
        '<div><strong data-meditation-100>0 / 15</strong><small>obiettivo 100%</small></div>',
        '<div><strong data-meditation-house>Da fare</strong><small>balcone del Capitolo 1</small></div>',
        '</div>',
        '<progress max="18" value="0" data-meditation-progress aria-label="Meditazioni confermate nella checklist"></progress>',
        '<p class="v-meditation-save-note" data-meditation-save-status>La tua selezione viene conservata solo in questo browser, se lo consenti. Non sincronizza la PS5.</p>',
        '<ol class="v-meditation-spots">',
    ]
    for number,spot in enumerate(data["spots"],1):
        name,region,loc = (h(spot[k],quote=True) for k in ("name","region","landmark"))
        key=spot["id"]
        status=' <span class="v-meditation-missable">PRIMA OCCASIONE · CAPITOLO 1</span>' if number==1 else (
            ' <span class="v-meditation-final">ULTIMA MEDITAZIONE</span>' if number==10 else '')
        parts.append(
            '<li class="v-meditation-spot" id="meditazione-luogo-'+key+'">'
            '<div class="v-meditation-spot-head"><span class="v-meditation-spot-number">'+str(number).zfill(2)+'</span>'
            '<div><h3>'+name+status+'</h3><p class="v-meditation-county">'+region+'</p></div></div>'
            '<p class="v-meditation-landmark">'+loc+'</p><div class="v-meditation-checks">'
        )
        for mode in spot["modes"]:
            identity=key+":"+mode
            label=("Jason" if mode=="jason" else "Lucia" if mode=="lucia" else
                   "Lezione iniziale o alternativa" if mode=="one" else "Sessione finale (unica)")
            eid="mt-"+key+"-"+mode
            parts.append('<label class="v-meditation-option" for="'+eid+'">'
                         '<input type="checkbox" id="'+eid+'" data-meditation-check="'+h(identity)+'" '
                         'autocomplete="off"><span>'+h(label)+'</span></label>')
        parts.append('</div>')
        second=spot["video_second"]
        stamp=f"{second//60}:{second%60:02d}"
        parts.append('<p class="v-meditation-video"><a data-meditation-video-link href="'+
                     h(data["video"]["url"]+"&t="+str(second)+"s",quote=True)+
                     '" target="_blank" rel="noopener noreferrer">▶ Guarda il luogo · '+stamp+
                     ' · '+h(data["video"]["creator"])+' ↗</a></p>')
        if number in (1,10):
            parts.append('<p class="v-meditation-note">'+h(spot.get("warning",""))+'</p>')
        parts.append('</li>')
    parts.extend([
        '</ol>',
        '<p class="v-meditation-unlock" data-meditation-unlock role="status">Il cerchio di pietre di Ascent Mountain compare sulla mappa dopo le altre meditazioni. Se non lo vedi, controlla il menu del gioco.</p>',
        '<p class="v-meditation-warning"><strong>Trofeo non certificato.</strong> '
        +h(data["not_confirmed"])+'</p>',
        '<div class="v-meditation-actions"><button type="button" data-meditation-reset>Azzera le mie spunte</button>'
        '<a href="'+h(data["source"],quote=True)+'" target="_blank" rel="noopener noreferrer">Vedi le mappe originali su PowerPyx ↗</a>'
        '<a href="'+h(data["corroboration"],quote=True)+'" target="_blank" rel="noopener noreferrer">Schermate su Push Square ↗</a>'
        '</div>',
        '<p class="v-meditation-source">Riferimenti: '
        '<a href="'+h(data["trophy_source"],quote=True)+'" target="_blank" rel="noopener noreferrer">PowerPyx – Trophy Guide</a>. '
        'Posizioni e quantità delle sessioni sono basate sulle fonti, non su una run completata dal nostro team. '
        'I minuti dei video provengono dai capitoli dichiarati dal creator; riproduzione e singoli fotogrammi non verificati indipendentemente.</p>',
        '</section>'
    ])
    return "".join(parts)
