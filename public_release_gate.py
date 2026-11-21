#!/usr/bin/env python3
"""Final publishing firewall for the *public* GitHub Pages artifact.

Editorial reports may exist during CI for validation but must not be shipped to
readers. This is not access control for the public GitHub repositories or their
commit histories. Keep genuine walkthrough screenshots at their numbered steps.
"""
from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

ROOT = Path("_site")
BASE = "https://xfederiko11.github.io/gta-6/"
PRIVATE_PREFIXES = (
    "crescita-x/",
    "screenshot-ps5/verifica/",
    "screenshot-ps5/priorita/",
)
PRIVATE_FILES = (
    "growth-evidence-v1.json",
    "photo-backlog-v5.json",
    "photo-requests.json",
    "photo-provenance-review.json",
    "photo-intake-audit.json",
    "map-rollout-v1.json",
    "design-version.json",
    "media-quality.json",
    "social-cards-audit.json",
    "assets/x-growth-dashboard-v1.css",
    "assets/photo-coverage-v5.css",
    "assets/photo-coverage-v5.js",
)
# No reports, operational dashboards, or links to the bot's management console.
PRIVATE_REFERENCES = (*PRIVATE_PREFIXES, *PRIVATE_FILES,
                      "github.com/xFederiko11/federiko-gta-playstation-bot/issues/",
                      "github.com/xFederiko11/federiko-gta-playstation-bot/actions/")
SECRET_PATTERNS = (
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:buffer_access_token|x_api_secret|github_token)[\x22\x27]?\s*[:=]\s*[\x22\x27][A-Za-z0-9_\-]{25,}"),
)
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def is_private(relative: str) -> bool:
    return relative in PRIVATE_FILES or any(relative == p.rstrip("/") or relative.startswith(p) for p in PRIVATE_PREFIXES)


def compact_guide(html: str) -> str:
    """Remove editorial collection checklists, not readers' step instructions."""
    def contribution(m: re.Match) -> str:
        ident = re.search(r'data-visual-request-id="([a-z0-9-]{1,90})"', m.group(0))
        if not ident:
            raise ValueError("Unrecognized screenshot contribution section")
        target = BASE + "screenshot-ps5/invia/?guida=" + ident.group(1)
        return ('<aside class="reader-photo-invite" id="contributi-foto">'
                '<strong>Hai una schermata che rende questo passaggio più chiaro?</strong>'
                '<p>Puoi proporre su X una foto autentica di mappa, tasti o risultato. '
                'La pubblicazione richiede una verifica e il tuo consenso.</p>'
                '<a href="' + escape(target, quote=True) + '">Condividi una schermata PS5 →</a>'
                '</aside>')
    html = re.sub(r'<aside id="contributi-foto"\b.*?</aside>',
                  contribution, html, flags=re.S)
    html = re.sub(r'<p class="v-step-photo-gap" data-step-photo-status="missing">.*?</p>',
                  '', html, flags=re.S)
    html = re.sub(r'<p class="v-no-image">.*?</p>', '', html, flags=re.S)
    return html


def remove_bot_management_links(html: str) -> str:
    return re.sub(
        r'<a\b[^>]*href="https://github\.com/xFederiko11/federiko-gta-playstation-bot/(?:issues|actions)/[^"]*"[^>]*>.*?</a>',
        '', html, flags=re.S | re.I)


def prune_sitemap(path: Path) -> None:
    ET.register_namespace("", NS[1:-1])
    tree = ET.parse(path)
    root = tree.getroot()
    for row in list(root):
        node = row.find(NS + "loc")
        if node is not None and node.text:
            loc = node.text
            if loc.startswith(BASE) and is_private(urlsplit(loc).path.removeprefix("/gta-6/")):
                root.remove(row)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def apply(root: Path = ROOT) -> dict:
    if not (root / "index.html").is_file() or not (root / "sitemap.xml").is_file():
        raise FileNotFoundError("Expected a complete generated site before publishing firewall")
    cleaned = 0
    for file in root.rglob("*.html"):
        if is_private(file.relative_to(root).as_posix()):
            continue
        before = file.read_text(encoding="utf-8")
        after = remove_bot_management_links(compact_guide(before))
        if after != before:
            file.write_text(after, encoding="utf-8")
            cleaned += 1
    prune_sitemap(root / "sitemap.xml")
    removed = []
    for prefix in PRIVATE_PREFIXES:
        directory = root / prefix
        if directory.is_dir():
            shutil.rmtree(directory)
            removed.append(prefix)
    for name in PRIVATE_FILES:
        file = root / name
        if file.is_file():
            file.unlink()
            removed.append(name)
    verify(root)
    return {"removed_artifacts": sorted(removed), "updated_reader_pages": cleaned}


def verify(root: Path = ROOT) -> None:
    if not (root / "index.html").is_file():
        raise ValueError("Missing public homepage")
    for private in PRIVATE_FILES:
        if (root / private).exists():
            raise ValueError("Private report shipped: " + private)
    for prefix in PRIVATE_PREFIXES:
        if (root / prefix).exists():
            raise ValueError("Private page shipped: " + prefix)
    for page in root.rglob("*"):
        if not page.is_file() or page.suffix.lower() not in {".html", ".js", ".css", ".json", ".xml"}:
            continue
        rel = page.relative_to(root).as_posix()
        raw = page.read_text(encoding="utf-8")
        if page.suffix.lower() in {".html", ".xml"}:
            for private in PRIVATE_REFERENCES:
                if private in raw:
                    raise ValueError("Reader-facing reference to internal material in " + rel + ": " + private)
        for pattern in SECRET_PATTERNS:
            if pattern.search(raw):
                raise ValueError("Credential-like string in public asset: " + rel)
    sitemap = (root / "sitemap.xml").read_text(encoding="utf-8")
    for prefix in PRIVATE_PREFIXES:
        if BASE + prefix in sitemap:
            raise ValueError("Private path still in sitemap: " + prefix)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Strip operational artifacts before uploading Pages")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.apply:
        result = apply(args.root)
        print("PUBLIC_RELEASE_GATE_OK", len(result["removed_artifacts"]),
              "operational files removed,", result["updated_reader_pages"], "reader pages streamlined")
    else:
        verify(args.root)
        print("PUBLIC_RELEASE_VERIFIED", args.root)


if __name__ == "__main__":
    main()
