"""Two creator-declared card chapters, linked without copying game media."""
from html import escape
import json
from pathlib import Path

DATA = Path(__file__).parent / "data/collectible_video_refs_v1.json"
EXPECTED = {
    "pt-12": ("Kadisha (Rosa) — Jack of Hearts", "Kadisha - Pink", 577),
    "pt-32": ("Malena (Rosso) — Jack of Hearts", "Malena - Deep Red", 1183),
}


def load():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    validate(data)
    return data


def validate(data):
    if (data.get("schema") != "gta6-collectible-video-moments-v1"
            or data.get("youtube_id") != "LTbw8B0DQHA"
            or data.get("creator") != "GTA Series Videos"
            or data.get("source_url") != "https://www.youtube.com/watch?v=LTbw8B0DQHA"):
        raise ValueError("Unreviewed collectible video source")
    moments = data.get("moments", {})
    if set(moments) != set(EXPECTED):
        raise ValueError("Unreviewed collectible video mapping")
    for ident, expected in EXPECTED.items():
        row = moments[ident]
        if (row.get("point_name"), row.get("chapter_label"), row.get("at")) != expected:
            raise ValueError("Card identity or creator chapter changed")
        if type(row["at"]) is not int:
            raise ValueError("Invalid chapter timestamp")


REFERENCES = load()


def render(item):
    row = REFERENCES["moments"].get(item.get("id"))
    if row is None:
        return ""
    if item.get("type") != "cards" or item.get("name") != row["point_name"]:
        raise ValueError("Video chapter cannot be moved to a different card")
    stamp = row["at"]
    label = f"{stamp//60}:{stamp%60:02d}"
    target = REFERENCES["source_url"] + "&t=" + str(stamp) + "s"
    return (
        '<aside class="v-step-video" data-collectible-video="' + escape(item["id"], quote=True)
        + '" data-step-video-id="LTbw8B0DQHA" data-step-video-seconds="' + str(stamp) + '">'
        '<button type="button" class="v-step-video-open" data-step-video-open hidden>'
        '<span class="v-step-video-play" aria-hidden="true">▶</span>'
        '<span><strong>Guarda la variante nel video originale</strong>'
        '<small>GTA Series Videos · ' + label + ' · ' + escape(row["chapter_label"]) + '</small></span>'
        '</button><div class="v-step-video-slot" data-step-video-slot aria-live="polite"></div>'
        '<p class="v-step-video-note"><a href="' + escape(target, quote=True)
        + '" target="_blank" rel="noopener noreferrer">Apri GTA Series Videos da ' + label + ' ↗</a>'
        '<br>Capitolo della stessa variante: confronta il luogo con la fonte scritta. '
        'I minuti sono dichiarati dal creator; non abbiamo verificato la riproduzione '
        'o che si tratti della stessa copia. Il player si carica solo dopo il clic.</p></aside>'
    )
