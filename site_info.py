"""Shared freshness metadata, page-view badge, and reciprocal X branding.

GitHub Pages is static: counts are loaded as a third-party SVG badge, never
invented or estimated server-side. A 'view' is a badge request, not a unique
person; counts begin when the badge is installed. No API key/cookie needed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
import subprocess
import json
from pathlib import Path

SOCIAL_URL = "https://x.com/xFederiko11"
SOCIAL_HANDLE = "@xFederiko11"
COUNT_SERVICE = "https://hitscounter.dev/api/hit"
COUNTER_START = "18 novembre 2026"
MONTHS = (
    "", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"
)


def sources_for(path: str) -> tuple[str, ...]:
    """Identify source files that can change the rendered page."""
    shared = ("build_site.py", "site_info.py", "site/assets/style.css")
    if path.startswith("trofei/"):
        return shared + ("data/trofei.json", "data/guide.json")
    if path.startswith("guide-e-tutorial/"):
        return shared + ("data/guide.json", "data/trofei.json", "related_research.py", "data/community_feed.json")
    if path.startswith("hdr-oled/"):
        return shared + ("hdr_catalog.py", "data/hdr_oled.json")
    if path.startswith("trucchi/"):
        return shared + ("cheats_catalog.py", "data/trucchi.json", "data/fonti_editoriali.json")
    if path.startswith("fonti/"):
        return shared + ("sources_page.py", "data/fonti_editoriali.json", "data/trucchi.json")
    if path.startswith("scoperte/"):
        return shared + ("community_page.py", "data/community_feed.json")
    # Home links to every main section, including the OLED model finder.
    return shared + ("data/trofei.json", "data/guide.json", "hdr_catalog.py", "data/hdr_oled.json", "cheats_catalog.py", "data/trucchi.json")


@lru_cache(maxsize=128)
def last_modified_at(path: str) -> datetime:
    """Most recent source revision, including the bot scan for community pages."""
    if path.startswith("scoperte/"):
        try:
            report=json.loads(Path("data/community_feed.json").read_text(encoding="utf-8"))
            stamp=report.get("generated_utc")
            if stamp:
                parsed=datetime.fromisoformat(stamp.replace("Z","+00:00"))
                if parsed.tzinfo is not None:
                    return parsed.astimezone(timezone.utc)
        except (OSError,ValueError,TypeError,KeyError):
            pass
    try:
        process = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", *sources_for(path)],
            check=False, capture_output=True, text=True, timeout=4
        )
        if process.returncode == 0 and process.stdout.strip():
            stamp = datetime.fromisoformat(process.stdout.strip().splitlines()[0])
            if stamp.tzinfo is not None:
                return stamp.astimezone(timezone.utc)
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
        pass
    # Only used for a local/source snapshot without Git metadata: the page
    # was just generated and that is the only defensible timestamp.
    return datetime.now(timezone.utc)


def iso_modified(path: str) -> str:
    return last_modified_at(path).isoformat(timespec="seconds")


def local_modified(path: str) -> tuple[str, str]:
    t = last_modified_at(path).astimezone(ZoneInfo("Europe/Rome"))
    machine = t.date().isoformat()
    display = f"{t.day} {MONTHS[t.month]} {t.year}"
    return machine, display


def view_badge_url(canonical: str) -> str:
    """Unique counter for each exact canonical URL: no secrets or fixed counts."""
    if not canonical.startswith("https://xfederiko11.github.io/gta-6/"):
        raise ValueError("Counter requires an internal canonical page")
    params = urlencode({"url": canonical, "label": "Visualizzazioni", "color": "indigo"})
    return f"{COUNT_SERVICE}?{params}"


def page_meta(canonical: str, path: str) -> str:
    date_value, date_label = local_modified(path)
    badge = escape(view_badge_url(canonical), quote=True)
    return (
        '<div class="page-meta" aria-label="Aggiornamento e visualizzazioni della pagina">'
        '<div class="page-meta-group">'
        '<span class="page-meta-date"><span aria-hidden="true">🗓️</span> '
        f'Aggiornata il <time datetime="{date_value}">{date_label}</time></span>'
        '<span class="page-meta-views" '
        f'title="Conteggio dei caricamenti del badge dal {COUNTER_START}; non indica utenti unici">'
        '<svg class="view-eye" aria-hidden="true" width="21" height="21" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"/>'
        '<circle cx="12" cy="12" r="3"/></svg>'
        '<span class="views-fallback" role="status">Visualizzazioni · in aggiornamento</span>'
        f'<img src="{badge}" width="190" height="24" class="views-badge" '
        f'alt="Visualizzazioni della pagina conteggiate dal {COUNTER_START}" '
        'loading="eager" decoding="async" referrerpolicy="no-referrer" '
        'style="display:none" '
        'onload="this.style.display=\'inline-block\';this.previousElementSibling.hidden=true" '
        'onerror="this.style.display=\'none\';this.previousElementSibling.textContent=\'Conteggio non disponibile\'">'
        '</span></div>'
        f'<a href="{SOCIAL_URL}" class="page-meta-social" target="_blank" '
        'rel="me noopener noreferrer" aria-label="Segui le notizie di GTA 6 Italia su X">'
        '𝕏 <span>News in tempo reale</span> <strong>@xFederiko11</strong> ↗</a>'
        '</div>'
    )
