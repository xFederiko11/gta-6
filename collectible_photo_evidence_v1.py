"""Evidence-gated collectible pictures. Never mistake a source URL for photo rights.

All 11 urgent collectibles have location-specific photo requests and a source
link; approved in-page photos require verified contributor consent, an actual
scrubbed WebP, checksum, precise checkpoint ID and human review.
"""
from __future__ import annotations
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import re

BASE = "https://xfederiko11.github.io/gta-6/"
ALLOWED = {"www.powerpyx.com", "www.pushsquare.com", "www.gtabase.com"}
EXPECTED = {
    "pt-102", "pt-103", "pt-104", "pt-105", "pt-106",
    "pt-26", "pt-66", "pt-108", "pt-109", "pt-111", "pt-112",
}
RIGHTS = "explicit_nonexclusive_site_and_social"


def e(text):
    return escape(str(text), quote=True)


def _x_status(value):
    link = urlsplit(value or "")
    return (link.scheme == "https" and link.hostname in {"x.com", "twitter.com"}
            and not link.username and not link.password and not link.query
            and not link.fragment and link.port in (None, 443)
            and bool(re.fullmatch(r"/[A-Za-z0-9_]{1,15}/status/[0-9]{6,25}", link.path)))


def validate(manifest, routes):
    if manifest.get("schema") != "gta6-collectible-photo-evidence-v1":
        raise ValueError("Unknown collectible evidence manifest")
    if manifest.get("reviewed") != "2026-11-22":
        raise ValueError("Unreviewed collectible evidence data")
    points = {p["id"]: p for p in routes["points"]}
    requests = manifest.get("requests")
    if not isinstance(requests, list) or len(requests) != 11:
        raise ValueError("Exactly eleven high-priority photo requests required")
    ids = [p.get("checkpoint_id") for p in requests]
    if len(set(ids)) != 11 or set(ids) != EXPECTED:
        raise ValueError("Missing or duplicated chapter-limited photo request")
    for row in requests:
        ident = row["checkpoint_id"]
        if ident not in points or not (points[ident].get("missable") or points[ident].get("location_limited")):
            raise ValueError("Photo request does not match a source-verified critical point")
        if row.get("approved") is not False:
            raise ValueError("Request cannot self-certify an image")
        if not isinstance(row.get("requested_visual"), str) or not 25 <= len(row["requested_visual"]) <= 160:
            raise ValueError("Missing precise human-requested photo subject")
        source = routes["sources"][points[ident]["source"]]
        url = urlsplit(source)
        if url.scheme != "https" or url.hostname not in ALLOWED or url.username or url.password:
            raise ValueError("Invalid source photo reference")

    approved = manifest.get("approved_photos")
    if not isinstance(approved, list):
        raise ValueError("Missing approved photo registry")
    visited = set()
    for photo in approved:
        ident = photo.get("checkpoint_id")
        if ident not in EXPECTED or ident in visited:
            raise ValueError("Unmatched or duplicated collectible picture")
        visited.add(ident)
        if (photo.get("human_reviewed") is not True
                or photo.get("approved_by") != "xFederiko11"
                or photo.get("rights") != RIGHTS
                or photo.get("author_confirmed") is not True
                or photo.get("published") is not True):
            raise ValueError("Photo must pass human rights review, not a bot")
        if photo.get("platform") not in ("PS5", "PS5 Pro"):
            raise ValueError("Unknown image platform")
        if not _x_status(photo.get("source_post")) or not _x_status(photo.get("consent_evidence")):
            raise ValueError("Individual source and creator consent required")
        try:
            if date.fromisoformat(photo["approved_on"]) < date(2026, 11, 22):
                raise ValueError("Approval predates evidence workflow")
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Missing reviewed date") from exc
        for field in ("alt", "credit", "caption"):
            value = photo.get(field)
            if not isinstance(value, str) or not 5 <= len(value) <= 180 or any(x in value for x in "<>"):
                raise ValueError("Missing safe photo caption/credit")
        expected_path = "assets/approved/collectible-" + ident + ".webp"
        if photo.get("file") != expected_path:
            raise ValueError("Collectible photos must use their original verified checkpoint")
        path = Path("site") / expected_path
        if not path.resolve().is_relative_to((Path("site") / "assets/approved").resolve()) or not path.is_file():
            raise ValueError("No local consent-cleared photo file")
        raw = path.read_bytes()
        if (len(raw) < 1500 or len(raw) > 4_000_000
                or raw[:4] != b"RIFF" or raw[8:12] != b"WEBP"
                or b"EXIF" in raw or b"XMP " in raw):
            raise ValueError("Must be real, metadata-scrubbed WebP")
        digest = hashlib.sha256(raw).hexdigest()
        if not re.fullmatch(r"[a-f0-9]{64}", photo.get("sha256", "")) or digest != photo["sha256"]:
            raise ValueError("Collectible photo checksum mismatch")
    return True


def render(item, manifest, routes):
    """Evidence lives directly under WHERE/WHAT for critical checkpoints."""
    ident = item["id"]
    task = next((r for r in manifest["requests"] if r["checkpoint_id"] == ident), None)
    if task is None:
        return ""
    photo = next((p for p in manifest["approved_photos"] if p["checkpoint_id"] == ident), None)
    source = routes["sources"][item["source"]]
    if photo is None:
        return ('<div class="cr-photo-evidence" data-cr-photo-state="source-only" '
                'data-cr-photo-checkpoint="' + e(ident) + '">'
                '<strong>📷 Foto del punto non ancora disponibile qui</strong>'
                '<a href="' + e(source) + '" target="_blank" rel="noopener noreferrer">'
                'Apri le immagini e la posizione sulla fonte originale ↗</a>'
                '<small>Fonte: ' + e(urlsplit(source).hostname.removeprefix("www.")) +
                ' · foto non copiata; questo link non è una prova del recupero.</small>'
                '</div>')
    path = BASE + e(photo["file"])
    return ('<figure class="cr-photo-evidence cr-photo-approved" '
            'data-cr-photo-state="approved" data-cr-photo-checkpoint="' + e(ident) + '">'
            '<a href="' + path + '" target="_blank" rel="noopener noreferrer">'
            '<img src="' + path + '" loading="lazy" decoding="async" '
            'data-visual-kind="screenshot" alt="' + e(photo["alt"]) + '"></a>'
            '<figcaption><span>' + e(photo["caption"]) + '</span>'
            '<small><a href="' + e(photo["source_post"]) + '" target="_blank" rel="noopener noreferrer">'
            'Fonte foto: ' + e(photo["credit"]) + ' ↗</a></small></figcaption></figure>')
