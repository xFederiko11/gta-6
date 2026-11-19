"""Source-backed discovery links on relevant GTA VI guide pages.

Only inserts link metadata from the existing independently validated site feed.
Never changes walkthrough steps, factual advice, patch status or trophy claims.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import json
import re

from community_page import validate

PATTERNS={
    "scansionare-veicoli":re.compile(r"\b(waink|scan(?:ning)?\s+(?:the\s+)?vehicles?|vehicle\s+(?:scan|database|catalog))\b",re.I),
    "studiare-animali":re.compile(r"\b(animal(?:s)?|wildlife|species|studying\s+animals)\b",re.I),
    "70-sfide-100-percento":re.compile(r"\b(100\s?%|completion\s+checklist|challenges?|100 percent)\b",re.I),
    "meditazione-capitolo-1":re.compile(r"\b(meditation|meditat(?:e|ing|ion)|mindful)\b",re.I),
    "viaggio-rapido-taxi":re.compile(r"\b(taxi|fast\s+travel|paradise\s+taxi)\b",re.I),
    "poligoni-concentrazione":re.compile(r"\b(shooting\s+range|shooting\s+challenge|concentration|focus\s+ability|gun\s+range)\b",re.I),
}
MAX_LINKS = 3


def load(path=Path("data/community_feed.json")):
    report=json.loads(Path(path).read_text(encoding="utf-8"))
    return validate(report)


def matching(guide_id: str, entries: list[dict]) -> list[dict]:
    expression=PATTERNS.get(guide_id)
    if expression is None:
        return []
    matched = [entry for entry in entries if expression.search(entry["title"])]
    return sorted(matched,key=lambda entry: entry["published_utc"], reverse=True)[:MAX_LINKS]


def box(guide_id: str, entries: list[dict]) -> str:
    links=matching(guide_id,entries)
    if not links:
        return ""
    cards=[]
    for item in links:
        title=escape(item["title"],quote=True)
        source=escape(item["source"],quote=True)
        href=escape(item["url"],quote=True)
        date=escape(item["published_utc"][:10],quote=True)
        cards.append(
            '<article class="index-item">'
            '<span class="card-label">🔎 NUOVA FONTE · DA VERIFICARE</span>'
            f'<p><a href="{href}" target="_blank" rel="noopener noreferrer">{title}</a></p>'
            f'<p class="micro">{source} · <time datetime="{date}">{date}</time></p>'
            '</article>'
        )
    return (
        '<section class="section community-related" aria-label="Nuove fonti da verificare">'
        '<h2>🔎 Nuove fonti su questo argomento</h2>'
        '<p>Il bot ha individuato titoli pertinenti. <strong>Non abbiamo ancora verificato '
        'le loro affermazioni o eventuali modifiche alla guida.</strong> '
        'Queste segnalazioni non certificano glitch, patch o compatibilità con i trofei. '
        'Le istruzioni sopra restano basate sulle fonti già citate.</p>'
        + '<div class="index-list">' + ''.join(cards) + '</div></section>'
    )
