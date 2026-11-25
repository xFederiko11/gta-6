"""Attach *specific* sourced map/video links to guide steps, never fake photos."""
from __future__ import annotations
from html import escape
from urllib.parse import urlsplit
import re


def _link(g, idx, data, refs, item=None):
    if item is None:
        item=data.get("guides", {}).get(g["id"], {}).get(str(idx))
    if item is None:
        return ""
    if item.get("kind") not in {"map", "video"}:
        raise ValueError("Invalid step evidence kind")
    key=item.get("ref")
    if not isinstance(key,str) or not re.fullmatch(r"[a-z0-9-]+",key):
        raise ValueError("Invalid step evidence ref")
    note=item.get("note")
    if not isinstance(note,str) or not 25 <= len(note) <= 220 or "<" in note:
        raise ValueError("Unsafe or vague evidence note")
    video_widget = ""
    if item["kind"] == "map":
        record=refs.get("maps",{}).get(key)
        if not record or "at" in item:
            raise ValueError("Missing map record or unsupported timestamp")
        target=record["url"]
        parsed=urlsplit(target)
        if parsed.scheme!="https" or parsed.hostname!="www.gtabase.com" or parsed.username or parsed.password or parsed.port not in (None,443):
            raise ValueError("Untrusted map domain")
        label="Apri la mappa interattiva"
    else:
        record=refs.get("guides",{}).get(key)
        stamp=item.get("at")
        if not record or type(stamp) is not int or stamp not in {x["at"] for x in record["chapters"]}:
            raise ValueError("No sourced video chapter for this step")
        code=record["youtube_id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}",code):
            raise ValueError("Invalid video code")
        target="https://www.youtube.com/watch?v="+code+"&t="+str(stamp)+"s"
        label="Guarda il momento utile del video"
        # Editorial evidence remains at the precise sourced moment. This
        # click-to-load embed shows authorized YouTube content rather than
        # copying a third-party gameplay frame into our static site.
        # Restrict embeds to the precise guide/action pairs independently
        # supported by the curated timestamp references. Other evidence
        # remains a link, never a generic player inserted into a step.
        if (g["id"], idx, key, stamp) in {
            ("registrare-auto-personale", 1, "registrare-auto-personale", 266),
            ("registrare-auto-personale", 4, "registrare-auto-personale", 675),
            ("soldi-2500-three-sheets-liquor", 0, "soldi-2500-three-sheets-liquor", 285),
            ("soldi-2500-three-sheets-liquor", 2, "soldi-2500-three-sheets-liquor", 455),
            ("soldi-facili-capitolo-1", 0, "soldi-facili-capitolo-1", 285),
            ("scansionare-veicoli", 3, "registrare-auto-personale", 266),
            ("prima-persona-glitch-ps5", 5, "prima-persona-glitch-ps5", 0),
        }:
            creator=escape(record["creator"])
            stamp_label=f"{stamp//60}:{stamp%60:02d}"
            # A source demonstration of the result or an explanation of
            # trackers is not evidence of the precise controller inputs.
            button_label=("Guarda il riferimento video"
                          if g["id"] in {"scansionare-veicoli","prima-persona-glitch-ps5"}
                          else "Guarda il passaggio nel video")
            video_widget=(
                '<div class="v-step-video" data-step-video-id="'+escape(code,quote=True)+'"'
                ' data-step-video-seconds="'+str(stamp)+'">'
                '<button type="button" class="v-step-video-open" data-step-video-open hidden'
                ' aria-label="Guarda il video del passaggio '+str(idx+1)+' dal minuto '+stamp_label+'">'
                '<span class="v-step-video-play" aria-hidden="true">▶</span>'
                '<span><strong>'+button_label+'</strong>'
                '<small>'+creator+' · minuto '+stamp_label+' · si carica solo dopo il clic</small></span>'
                '</button>'
                '<div class="v-step-video-slot" data-step-video-slot aria-live="polite"></div>'
                '<p class="v-step-video-note">Video di '+creator+' · possibile spoiler della missione. '
                'È un riferimento visivo, non una schermata di gioco verificata dal nostro team.</p>'
                '</div>')
    return ('<aside class="v-step-source" data-step-external-evidence="'+escape(item["kind"])+'">'
            '<strong>Riferimento esterno per questo passaggio (non screenshot)</strong>'
            '<p>'+escape(note)+'</p>'
            '<a href="'+escape(target,quote=True)+'" target="_blank" rel="noopener noreferrer">'
            +label+' ↗</a>'+video_widget+'</aside>')


def validate(guides, data, refs):
    if data.get("schema")!="gta6-per-step-external-evidence-v1":
        raise ValueError("Unrecognized step evidence schema")
    ids={g["id"]:g for g in guides}
    for guid, steps in data.get("guides",{}).items():
        if guid not in ids or not isinstance(steps,dict):
            raise ValueError("Unknown guide for step evidence")
        for number in steps:
            if not re.fullmatch(r"0|[1-9][0-9]*",number) or int(number)>=len(ids[guid]["steps"]):
                raise ValueError("Invalid guide step number")
            render(ids[guid], int(number), data, refs)
    return True


def render(g, idx, data, refs):
    item=data.get("guides", {}).get(g["id"], {}).get(str(idx))
    primary=_link(g, idx, data, refs)
    if not item or "also_video" not in item:
        return primary
    extra=item["also_video"]
    # A second reference is deliberately limited to the documented first
    # location. Keep the independently sourced map, and never imply that
    # the clip proves the other three locations or any reward.
    if (g["id"]!="soldi-facili-capitolo-1" or idx!=0 or item["kind"]!="map"
        or not isinstance(extra,dict) or set(extra)!={"kind","ref","at","note"}
        or extra["kind"]!="video" or extra["ref"]!=g["id"] or extra["at"]!=285):
        raise ValueError("Invalid supplemental video evidence")
    return primary+_link(g, idx, data, refs, item=extra)
