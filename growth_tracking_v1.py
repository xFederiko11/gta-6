"""Optional, cookie-free conversion analytics for the public GTA VI Italia website.

Pure build-time markup enhancement. No analytics URL, script, network request
or browser storage exists until the owner explicitly configures UMAMI_WEBSITE_ID.
Every tracked CTA is on a verified public first-party page and only uses
generic event names. No user IDs, PSN data, account details or X APIs.
"""
from __future__ import annotations

from html import unescape
import re
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

SCRIPT = "https://cloud.umami.is/script.js"
HOSTNAME = "xfederiko11.github.io"
TAG = "growth-analytics-v1"
ANCHOR = re.compile(r'<a\b[^>]*>', re.I | re.S)
HREF = re.compile(r'\bhref="([^"]{1,2048})"', re.I)
EVENT_ATTR = 'data-umami-event='
OWN_STATUS = re.compile(r'/xFederiko11/status/[0-9]{8,25}/?', re.I)
YOUTUBE_ID = re.compile(r'/watch/?')

def normalize_id(value):
    """Only allow standard canonical Umami site UUIDs, never arbitrary HTML/JS."""
    if value is None or value == "":
        return None
    if not isinstance(value, str) or len(value) != 36:
        raise ValueError("UMAMI_WEBSITE_ID must be a canonical UUID")
    try:
        parsed = UUID(value)
    except (ValueError, TypeError, AttributeError):
        raise ValueError("UMAMI_WEBSITE_ID must be a canonical UUID") from None
    if str(parsed) != value.lower() or parsed.int == 0:
        raise ValueError("UMAMI_WEBSITE_ID must be a canonical nonzero UUID")
    return str(parsed)

def script_tag(value):
    site_id = normalize_id(value)
    if site_id is None:
        return ""
    return (
        '<script id="'+TAG+'" defer src="'+SCRIPT+'" '
        'data-website-id="'+site_id+'" data-domains="'+HOSTNAME+'" '
        'data-do-not-track="true" data-exclude-search="true"></script>'
    )

def classify(tag):
    """Classify only outbound destinations/actions we actually control."""
    match = HREF.search(tag)
    if match is None:
        return None
    raw = unescape(match.group(1))
    if len(raw) > 2048:
        return None
    try:
        u = urlsplit(raw)
        if (u.scheme != "https" or u.username or u.password or u.fragment
                or u.port not in (None,443)):
            return None
    except ValueError:
        return None
    if u.hostname == "x.com":
        if u.path == "/intent/follow":
            query = parse_qs(u.query)
            if query.get("screen_name") == ["xFederiko11"]:
                return "x-follow-intent"
        elif u.path == "/intent/tweet":
            query = parse_qs(u.query)
            if "in_reply_to" in query:
                return "x-reply-intent"
            if "url" in query or "social-share-link" in tag:
                return "x-share-intent"
            if "text" in query:
                return "x-contact-intent"
        elif not u.query and OWN_STATUS.fullmatch(u.path):
            return "x-post-open"
        elif not u.query and u.path.rstrip("/").casefold() == "/xfederiko11":
            return "x-profile-open"
    if u.hostname == "www.youtube.com" and u.path == "/watch":
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", parse_qs(u.query).get("v",[""])[0]):
            return "youtube-video-open"
    return None

def annotate(html):
    """Annotate existing native anchors without redirect links or changing hrefs."""
    def add(m):
        anchor = m.group(0)
        if EVENT_ATTR in anchor:
            return anchor
        event = classify(anchor)
        return anchor[:-1] + ' data-umami-event="'+event+'">' if event else anchor
    return ANCHOR.sub(add, html)

def enhance(page, value):
    """No changes to HTML when analytics is unconfigured."""
    tag = script_tag(value)
    if not tag:
        return page
    if 'id="'+TAG+'"' in page:
        return page
    if "</head>" not in page:
        raise ValueError("Missing closing head in HTML page")
    page = annotate(page)
    return page.replace("</head>", tag+"</head>", 1)
