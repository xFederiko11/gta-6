"""Optional automatic source references for GTA VI guides.

Never rewrite mission instructions, cheat button sequences or trophy requirements
from public headlines. Only link directly relevant independently-attributed
items with explicitly unverified status.
"""
from __future__ import annotations
from html import escape
import json
from pathlib import Path
import re

from community_page import validate

DATA = Path("data/community_feed.json")
GUIDE_PATTERNS = {
    "scansionare-veicoli": r"\b(waink|scan(?:ning)?\s+(?:cars|vehicles)|(?:cars|vehicles)\s+scan)\b",
    "studiare-animali": r"\b(animal|wildlife|fauna|species|bird|fish)\b",
    "70-sfide-100-percento": r"\b(challenges?|100\s*%|completion\s+checklist)\b",
    "meditazione-capitolo-1": r"\b(meditat(?:e|ion|ing))\b",
    "viaggio-rapido-taxi": r"\b(taxi|fast\s+travel)\b",
    "poligoni-concentrazione": r"\b(shooting\s+range|firing\s+range|concentration|focus\s+abilit)\b",
}
HUB_PATTERN = re.compile(
    r"\b(guide|walkthrough|missions?|troph(?:y|ies)|collectible|challenges?|vehicles?|cheat|glitch)\b",
    re.I
)


def e(text):
    return escape(str(text), quote=True)


def candidates(report=None):
    if report is None:
        report = json.loads(DATA.read_text(encoding="utf-8"))
    return [x for x in validate(report) if (
            x["status"] == "🔵 GUIDA INDIPENDENTE"
            and x["source"] in {"PowerPyx", "GTA Series Videos"}) or (
            x["status"] == "🟡 SEGNALAZIONE" and x["source"] == "GTABase")]


def render_cards(items, heading="Ultime fonti specialistiche da confrontare"):
    if not items:
        return ""
    rows=[]
    for x in items:
        rows.append(
            '<li><span class="micro">'+e(x["status"])+' — '
            +e(x["source"])+' · '+e(x["published_utc"][:10])+'</span> '
            +'<a href="'+e(x["url"])+'" target="_blank" rel="noopener noreferrer">'
            +e(x["title"])+'</a></li>')
    return ('<section class="section related-research"><h2>'+e(heading)+'</h2>'
            '<p class="micro"><strong>In verifica:</strong> il bot ha rilevato '
            'questi titoli da fonti esterne, senza verificare i dettagli '
            'della procedura, la patch o i trofei. Non modificano le istruzioni '
            'di questa guida.</p><ul>'+"".join(rows)+'</ul>'
            '<p><a href="https://xfederiko11.github.io/gta-6/scoperte/">'
            'Tutte le scoperte e le fonti →</a></p></section>')


def for_guide(guide_id, report=None):
    pattern=GUIDE_PATTERNS.get(guide_id)
    if not pattern:
        return ""
    regex=re.compile(pattern,re.I)
    items=[x for x in candidates(report) if regex.search(x["title"])]
    return render_cards(items[:2], "Nuove fonti sulla stessa meccanica")


def for_catalog(report=None):
    items=[x for x in candidates(report) if HUB_PATTERN.search(x["title"])]
    return render_cards(items[:4], "Nuove guide indipendenti da verificare")
