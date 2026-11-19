"""GTA VI public community radar: import attributed research leads from bot issue.

No ChatGPT, paid API, scraped full articles or Buffer dependency. The bot's
Github issue is a *research queue*, not confirmation of any article contents.
"""
from __future__ import annotations

from datetime import datetime, timezone
from html import escape, unescape
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ISSUE_API = "https://api.github.com/repos/xFederiko11/federiko-gta-playstation-bot/issues/29"
ISSUE_WEB = "https://github.com/xFederiko11/federiko-gta-playstation-bot/issues/29"
MARKER = "<!-- gta6-community-editorial-queue-v1 -->"
OUTPUT = Path("data/community_radar.json")
SCHEMA = "gta6-community-radar-v1"
LABELS = {
    "🔵 GUIDA INDIPENDENTE": "Guida indipendente",
    "🟡 COMMUNITY": "Community",
    "🟣 DATAMINING": "Datamining",
    "🟠 RUMOR": "Rumor non verificato",
    "🟡 SEGNALAZIONE": "Segnalazione da verificare",
}
SOURCES = {"PowerPyx", "GTA Series Videos"}
HOSTS = {"powerpyx.com", "youtube.com"}
HEADER = re.compile(r"^### (.+?) — (.+)$", re.M)
SOURCE = re.compile(r"^Fonte: \*\*(.+?)\*\* · Data fonte: ([^\n]+)$", re.M)
LINK = re.compile(r"^\s*· \[Apri originale\]\((https://[^)\s]+)\)", re.M)
DATE = re.compile(r"^Scansione UTC: (.+)$", re.M)


def verify_iso(timestamp: str) -> str:
    dt = datetime.fromisoformat(timestamp.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timezone needed")
    return dt.astimezone(timezone.utc).isoformat()


def parse_issue(body: str) -> dict:
    if MARKER not in body:
        raise ValueError("Issue is not the authorized GTA VI research queue")
    m = DATE.search(body)
    if not m:
        raise ValueError("Research queue has no scan timestamp")
    timestamp = verify_iso(m.group(1))
    # Issue text can contain unrelated paragraphs. Only a small, explicit
    # headline/source/URL pattern is allowed into an indexable page.
    section = body.split("## Nuove piste editoriali", 1)
    if len(section) < 2:
        raise ValueError("Research queue missing candidate section")
    chunk = section[1].split("## Salute dei feed", 1)[0]
    candidates = []
    seen = set()
    for block in re.split(r"(?=^### )", chunk, flags=re.M):
        h = HEADER.search(block)
        p = SOURCE.search(block)
        l = LINK.search(block)
        if not (h and p and l):
            continue
        label, raw_title = h.groups()
        source, published = p.groups()
        link = l.group(1)
        parsed = urlsplit(link)
        hostname = (parsed.hostname or "").lower().removeprefix("www.")
        title = unescape(raw_title).strip()
        if (label not in LABELS or source not in SOURCES or
                parsed.scheme != "https" or hostname not in HOSTS or
                parsed.username or parsed.password or parsed.port not in (None, 443) or
                not title or len(title) > 220 or link in seen):
            continue
        try:
            published = verify_iso(published)
        except ValueError:
            continue
        seen.add(link)
        candidates.append({
            "title": title,
            "source": source,
            "source_url": link,
            "published_utc": published,
            "label": LABELS[label],
            "verified_article": False,
        })
        if len(candidates) >= 25:
            break
    failures = re.findall(r"^- ⚠️ ([^\n]{1,130})$", body.split("## Salute dei feed", 1)[-1]
                          .split("## Fonti registrate", 1)[0], re.M)
    return {
        "schema": SCHEMA,
        "scan_utc": timestamp,
        "queue_url": ISSUE_WEB,
        "editorial_status": "Titoli attribuiti e classificati, senza verifica del contenuto completo",
        "candidates": candidates,
        "feed_warnings": failures[:10],
    }


def fetch_issue(*, url=ISSUE_API, timeout=15) -> dict:
    if url != ISSUE_API:
        raise ValueError("Research import must use pinned public issue")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GTA6Italia-Site-Radar/1.0",
    }
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as response:
        if response.geturl() != ISSUE_API:
            raise ValueError("Unexpected issue redirect")
        if response.status != 200:
            raise ValueError("Unexpected GitHub API response")
        raw = response.read(250_001)
    if len(raw) > 250_000:
        raise ValueError("Issue too large")
    payload = json.loads(raw)
    if (payload.get("title") != "GTA VI - Coda fonti community" or
            payload.get("state") != "open" or
            payload.get("html_url") != ISSUE_WEB):
        raise ValueError("Issue provenance changed")
    return parse_issue(payload.get("body") or "")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["refresh", "validate"], required=True)
    args = parser.parse_args()
    if args.mode == "validate":
        current=json.loads(OUTPUT.read_text(encoding="utf-8"))
        if current.get("schema") != SCHEMA:
            raise ValueError("Unknown community radar schema")
        print("COMMUNITY_RADAR_VALID", len(current.get("candidates", [])))
        return
    data=fetch_issue()
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("COMMUNITY_RADAR_SYNC", len(data["candidates"]),
          "source=verified-public-GitHub-Issue", "read_only=true")


if __name__ == "__main__":
    main()
