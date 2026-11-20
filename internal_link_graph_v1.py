"""Check GTA VI Italia's STATIC internal link graph; no crawler or network.

Useful for SEO: sitemaps advertise URLs, but ordinary site links are also
needed to help people and crawlers discover the content. Counts are factual
from the generated static HTML, not Google impressions or index statuses.
"""
from __future__ import annotations

from collections import Counter, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import json
import xml.etree.ElementTree as ET

BASE = "https://xfederiko11.github.io/gta-6/"
ROOT = Path("_site")
PRIMARY = ("trofei/", "guide-e-tutorial/", "hdr-oled/", "soldi-facili/", "auto-speciali/")
MAX_SAMPLED = 20


class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value is not None:
                self.hrefs.append(value)


def normalized_page_link(href: str, current: str) -> str | None:
    """Return an exact canonical URL under our project prefix, or None."""
    if not isinstance(href, str) or not href or len(href) > 2048:
        return None
    try:
        absolute = urljoin(current, href)
        u = urlsplit(absolute)
        if (u.scheme != "https" or u.hostname != "xfederiko11.github.io"
                or u.username or u.password or u.port not in (None, 443)):
            return None
    except ValueError:
        return None
    # Never follow root-host pages owned by a different GitHub repository.
    if not u.path.startswith("/gta-6/"):
        return None
    # Only canonical folder-style URLs are considered for sitemap graph.
    return "https://xfederiko11.github.io" + u.path


def sitemap_urls(root=ROOT):
    tree = ET.parse(Path(root) / "sitemap.xml")
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    urls = [node.text for node in tree.iter(ns + "loc")]
    if not urls or len(urls) != len(set(urls)):
        raise ValueError("Missing or repeated sitemap URLs")
    for item in urls:
        if item != BASE and (not item.startswith(BASE) or not item.endswith("/")):
            raise ValueError("Invalid project sitemap URL: " + repr(item))
    if BASE not in urls:
        raise ValueError("Homepage omitted from sitemap")
    return urls


def file_for(url: str, root=ROOT) -> Path:
    if url != BASE and (not url.startswith(BASE) or not url.endswith("/")):
        raise ValueError("URL outside canonical GTA VI Italia project")
    subpath = url[len(BASE):]
    if ".." in subpath.split("/"):
        raise ValueError("Traversal in sitemap URL")
    return Path(root) / subpath / "index.html"


def analyze(root=ROOT):
    """Read exactly the indexed URLs and their static (no JS) anchor links."""
    pages = sitemap_urls(root)
    s = set(pages)
    graph: dict[str, set[str]] = {}
    missing = []
    broken = []
    for page in pages:
        path = file_for(page, root)
        if not path.is_file():
            missing.append(page)
            continue
        html = path.read_text(encoding="utf-8")
        parser = AnchorParser()
        parser.feed(html)
        graph[page] = set()
        for href in parser.hrefs:
            link = normalized_page_link(href, page)
            if link is None:
                continue
            if link in s:
                graph[page].add(link)
            elif link.endswith("/"):
                # We only count navigable HTML folder links. Static asset
                # files, downloads and fragments are outside this report.
                broken.append({"source": page, "target": link})
    if missing:
        raise ValueError("Missing HTML files for sitemap URLs: " + repr(missing[:5]))
    if broken:
        raise ValueError("Canonical internal links not in sitemap: " + repr(broken[:8]))
    distance = {BASE: 0}
    todo = deque([BASE])
    while todo:
        current = todo.popleft()
        for target in graph[current]:
            if target not in distance:
                distance[target] = distance[current] + 1
                todo.append(target)
    orphan = sorted(s - distance.keys())
    deep = sorted((dist, page) for page, dist in distance.items() if dist > 3)
    priorities = {BASE + p: distance.get(BASE + p) for p in PRIMARY}
    return {
        "schema": "gta-vi-static-crawl-graph-v1",
        "scope": "Same-project static a[href], no network or Google index data",
        "pages": len(pages),
        "links": sum(len(v) for v in graph.values()),
        "reachable": len(distance),
        "not_linked_from_home": len(orphan),
        "orphan_sample": orphan[:MAX_SAMPLED],
        "over_three_clicks": len(deep),
        "deep_sample": [{"clicks": dist, "url": page} for dist, page in deep[:MAX_SAMPLED]],
        "primary_hubs_clicks": priorities,
        "distance_distribution": dict(sorted(Counter(distance.values()).items())),
        "warning": "Not a Google crawl or proof of indexing; counts sitemap and HTML links only.",
    }


def main():
    result = analyze()
    Path(".runtime").mkdir(exist_ok=True)
    out = Path(".runtime/seo-link-graph-v1.json")
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("GTA6_INTERNAL_LINK_GRAPH", json.dumps(result, ensure_ascii=False))
    for hub, dist in result["primary_hubs_clicks"].items():
        if dist is None or dist > 2:
            raise SystemExit("CRITICAL HUB ISOLATED: " + hub + " hops=" + str(dist))


if __name__ == "__main__":
    main()
