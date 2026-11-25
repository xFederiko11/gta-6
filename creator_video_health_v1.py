"""Read-only YouTube metadata checks for the four curated links.

No downloads, media extraction, thumbnails, API keys, login or publication.
An oEmbed response is metadata evidence, not proof of actual playback,
timestamp contents, availability in a reader's country or reuse rights.
"""
from __future__ import annotations
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
import json
import re
import os
from creator_video_hub_v1 import load, records

ENDPOINT = "https://www.youtube.com/oembed"
MAX_BYTES = 64_000
TIMEOUT = 6
AUTHORS = {
    "registrare-auto-personale": {"tgg"},
    "moses-ign": {"ign", "ign guides"},
    "soldi-facili-capitolo-1": {"tgg"},
    "prima-persona-glitch-ps5": {"oneboyler"},
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Embed(HTMLParser):
    def __init__(self):
        super().__init__()
        self.frames = []
    def handle_starttag(self, tag, attrs):
        if tag == "iframe":
            self.frames.append(dict(attrs).get("src", ""))


def probe(item, opener=None):
    video_id = item["video_id"]
    key = item["key"]
    if key not in AUTHORS or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError("Invalid curated video")
    query = ENDPOINT + "?" + urlencode({
        "url": "https://www.youtube.com/watch?v=" + video_id, "format": "json"})
    request = Request(query, headers={"Accept": "application/json",
                                       "User-Agent": "GTA6Italia-VideoMetadata/1.0"})
    opener = opener or build_opener(NoRedirect()).open
    try:
        with opener(request, timeout=TIMEOUT) as response:
            if response.geturl() != query or response.status != 200:
                return "metadata_unconfirmed"
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            return "metadata_unconfirmed"
        meta = json.loads(raw)
        if not isinstance(meta, dict) or meta.get("type") != "video" or meta.get("provider_name") != "YouTube":
            return "metadata_unconfirmed"
        if not all(isinstance(meta.get(k), str) and meta[k].strip()
                   for k in ("title", "author_name", "html")):
            return "metadata_unconfirmed"
        parser = Embed()
        parser.feed(meta["html"])
        if len(parser.frames) != 1:
            return "metadata_unconfirmed"
        url = urlsplit(parser.frames[0])
        if (url.scheme != "https" or url.hostname not in {"www.youtube.com", "youtube.com", "www.youtube-nocookie.com"}
                or url.username or url.password or url.port not in (None,443)
                or url.path != "/embed/" + video_id):
            return "metadata_mismatch"
        author = " ".join(meta["author_name"].casefold().split())
        if author not in AUTHORS[key]:
            return "creator_review_needed"
        return "metadata_confirmed"
    except HTTPError as exc:
        if exc.code in (401, 403, 404, 410, 451):
            return "provider_restricted_or_unavailable"
        return "metadata_unconfirmed"
    except (URLError, OSError, ValueError, TypeError, TimeoutError):
        return "metadata_unconfirmed"


def main():
    items = records(load())
    rows = [{"key": item["key"], "video_id": item["video_id"],
             "status": probe(item), "playback_verified": False,
             "reuse_rights_verified": False} for item in items]
    report = {"checked_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "official YouTube oEmbed metadata only",
              "videos": rows}
    print("CREATOR_VIDEO_METADATA " + json.dumps(report, ensure_ascii=False))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as out:
            out.write("\n### Creator videos: metadata only, not playback or permission\n\n")
            out.write("| Video | ID | Result |\n|---|---|---|\n")
            for row in rows:
                out.write("| "+row["key"]+" | "+row["video_id"]+" | "+row["status"]+" |\n")
            out.write("\nProvider failures are informational; no content was downloaded or published.\n")
    return report


if __name__ == "__main__":
    main()
