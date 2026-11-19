"""Publish a safe, attributed GTA VI community-news index from the bot's public issue.

Fetch happens ONLY in GitHub Actions. Rendering is deterministic and network-free.
The GitHub issue contains independently sourced headlines, not verified claims.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
from html import escape, unescape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

SOURCE_ISSUE = "https://api.github.com/repos/xFederiko11/federiko-gta-playstation-bot/issues/29"
SOURCE_URL = "https://github.com/xFederiko11/federiko-gta-playstation-bot/issues/29"
DATA_FILE = Path("data/community_watch_runtime.json")
MAX_ITEMS = 12
ALLOWED = {"youtube.com", "powerpyx.com"}
SECTION = "community/"
TITLE = re.compile(r"^### (🔵 GUIDA INDIPENDENTE|🟣 DATAMINING|🟠 RUMOR|🟡 COMMUNITY|🟡 SEGNALAZIONE) — (.+)$")
SOURCE = re.compile(r"^Fonte: \*\*(.+?)\*\* · Data fonte: (\S+)")
LINK = re.compile(r"\[Apri originale\]\((https://[^ )]+)\)")


def e(s):
    return escape(str(s), quote=True)


def parse_issue(body: str, *, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Timezone-aware clock required")
    if "<!-- gta6-community-editorial-queue-v1 -->" not in body:
        raise ValueError("Unexpected research issue format")
    generated = re.search(r"Scansione UTC: (\S+)", body)
    if not generated:
        raise ValueError("Missing scan timestamp")
    scanned = datetime.fromisoformat(generated.group(1).replace("Z", "+00:00"))
    if scanned.tzinfo is None:
        raise ValueError("Scan time without timezone")
    records, current = [], None
    for raw_line in body.splitlines():
        line = raw_line.strip()
        m = TITLE.match(line)
        if m:
            if current: records.append(current)
            current = {"label":m.group(1), "title":unescape(m.group(2))}
            continue
        if current is None:
            continue
        m = SOURCE.match(line)
        if m:
            current["source"] = unescape(m.group(1))
            current["published_utc"] = m.group(2)
        m = LINK.search(line)
        if m:
            current["url"] = m.group(1)
    if current: records.append(current)
    items, seen = [], set()
    for item in records:
        if not all(k in item for k in ("title", "source", "label", "url", "published_utc")):
            continue
        if len(item["title"]) > 260 or len(item["source"]) > 75:
            continue
        u = urlsplit(item["url"])
        if u.scheme != "https" or u.username or u.password or not u.hostname:
            continue
        if u.hostname.lower().removeprefix("www.") not in ALLOWED:
            continue
        try:
            age = now - datetime.fromisoformat(item["published_utc"].replace("Z","+00:00"))
        except (ValueError, TypeError):
            continue
        if not timedelta(minutes=-5) <= age <= timedelta(days=7):
            continue
        if item["url"] in seen:
            continue
        seen.add(item["url"])
        items.append(item)
    return {"schema":"gta6-community-watch-v1","scanned_utc":scanned.isoformat(),
            "source_issue":SOURCE_URL,"items":items[:MAX_ITEMS]}


def fetch(output: Path = DATA_FILE):
    request = Request(SOURCE_ISSUE, headers={"Accept":"application/vnd.github+json",
                                           "User-Agent":"GTA6-Italia-Community-Watch/1.0"})
    with urlopen(request, timeout=12) as res:
        if res.status != 200:
            raise ValueError("GitHub issue not available")
        raw = res.read(300_000)
    payload=json.loads(raw.decode("utf-8"))
    if payload.get("state") != "open":
        raise ValueError("Research queue is not open")
    data=parse_issue(payload.get("body") or "")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("COMMUNITY_WATCH_FETCH",len(data["items"]),data["scanned_utc"])


def load():
    if not DATA_FILE.exists():
        return {"schema":"gta6-community-watch-v1","items":[],"scanned_utc":None,"source_issue":SOURCE_URL}
    obj=json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if obj.get("schema") != "gta6-community-watch-v1" or not isinstance(obj.get("items"),list):
        raise ValueError("Unexpected community watch data")
    return obj


def render(write, layout, url, crumbs):
    data=load()
    cards=[]
    for item in data["items"]:
        cards.append(
            '<article class="index-item">'
            +f'<span class="card-label">{e(item["label"])}</span>'
            +f'<h3><a href="{e(item["url"])}" target="_blank" rel="noopener noreferrer">{e(item["title"])}</a></h3>'
            +f'<p><strong>Fonte:</strong> {e(item["source"])} · '
            +f'<strong>Pubblicato:</strong> <time datetime="{e(item["published_utc"])}">{e(item["published_utc"][:10])}</time></p>'
            +'<p class="micro">Titolo segnalato da una fonte indipendente: il contenuto non è stato '
            +'verificato nel dettaglio. Apri l’originale per informazioni, patch e piattaforma.</p></article>')
    if not cards:
        cards=['<p class="info">Non ci sono ancora nuove segnalazioni verificate dal monitor. '
               'Il sito rimane disponibile e il bot continua i controlli indipendentemente.</p>']
    stamp = ('Ultima scansione automatica: '+e(data["scanned_utc"][:19].replace("T"," "))+' UTC.'
             if data.get("scanned_utc") else "Attesa della prima sincronizzazione del monitor.")
    title = "GTA 6: novità dalla community, guide e scoperte | GTA VI Italia"
    desc = ("Scoperte e nuove guide GTA 6 da PowerPyx e GTA Series Videos: "
            "aggiornamenti del bot GitHub con fonti originali e affidabilità dichiarata.")
    body = (
        crumbs([("Community",SECTION)])
        +'<section class="page-intro"><span class="eyebrow">📡 GTA VI · RADAR COMMUNITY</span>'
        +'<h1>GTA 6: <span class="highlight">cosa sta scoprendo la community</span></h1>'
        +'<p class="lead">Novità, video e guide individuati automaticamente dal bot GitHub. '
        +'Ogni segnalazione è attribuita e classificata: una scoperta non equivale a un annuncio Rockstar.</p></section>'
        +'<div class="info"><strong>Trasparenza:</strong> le schede riportano il titolo originale '
        +'e il link; non sono sintesi di contenuti che non abbiamo consultato. '
        +'Nessuna segnalazione è automaticamente confermata o sicura per i trofei.</div>'
        +'<section class="section"><h2>Le ultime segnalazioni</h2>'
        +f'<p class="micro">{stamp} <a href="{SOURCE_URL}" target="_blank" rel="noopener noreferrer">'
        +'Consulta la coda del bot su GitHub</a>.</p>'
        +'<div class="index-list">'+"".join(cards)+'</div></section>'
        +'<section class="section prose"><h2>Come valutiamo i contenuti</h2>'
        +'<p>Le etichette identificano la provenienza e il grado di verifica: guida indipendente, '
        +'community, datamining o rumor. Non ripubblichiamo video o articoli senza permesso '
        +'e non trasformiamo indiscrezioni in fatti. I titoli provengono da feed pubblici: '
        +'per informazioni pratiche usa la nostra <a href="'+url("fonti/")+'">metodologia editoriale</a>.</p>'
        +'</section>'
    )
    structured={"@context":"https://schema.org","@type":"CollectionPage","name":title,
                "description":desc,"url":url(SECTION),"inLanguage":"it-IT"}
    write(SECTION+"index.html",layout(title,desc,SECTION,body,"community",structured=structured))
    return SECTION


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--fetch",action="store_true")
    cli.add_argument("--output",type=Path,default=DATA_FILE)
    a=cli.parse_args()
    if a.fetch:
        fetch(a.output)
