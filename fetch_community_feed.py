"""Fetch the independent public GTA VI bot's editorial issue into GitHub Pages.

Only public GitHub API data; zero Buffer, OpenAI or third-party paid API keys.
If the fetch fails, do not deploy stale or fabricated community headlines.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen

from community_page import validate

API = "https://api.github.com/repos/xFederiko11/federiko-gta-playstation-bot/issues?state=open&per_page=100"
ISSUE_TITLE = "GTA VI - Coda fonti community"
PAYLOAD = re.compile(r"<!-- gta6-verified-source-feed-b64:([A-Za-z0-9_=-]+) -->")
DEST = Path("data/community_feed.json")


def extract(issues: list[dict]) -> dict | None:
    for issue in issues:
        if issue.get("title") != ISSUE_TITLE or "pull_request" in issue:
            continue
        body = str(issue.get("body") or "")
        found = PAYLOAD.search(body)
        if not found:
            raise ValueError("Editorial issue has no safe machine-readable feed")
        if len(found.group(1)) > 150_000:
            raise ValueError("Research feed exceeds allowed size")
        raw = base64.urlsafe_b64decode(found.group(1).encode("ascii"))
        data = json.loads(raw.decode("utf-8"))
        validate(data)
        return data
    return None


def fetch(*, opener=urlopen, token: str = "") -> dict | None:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GTA6-Italia-community-bridge/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(API, headers=headers)
    with opener(request, timeout=12) as response:
        body = response.read(2_000_000)
    issues = json.loads(body.decode("utf-8"))
    if not isinstance(issues, list):
        raise ValueError("Invalid GitHub Issues API payload")
    return extract(issues)


def main():
    result = fetch(token=os.getenv("GITHUB_TOKEN", ""))
    if result is None:
        print("COMMUNITY_FEED_NO_ISSUE: using the non-claiming empty baseline")
        return
    DEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("COMMUNITY_FEED_VALIDATED", len(result["items"]),
          "source=public-github-issue; verified_claims=zero")


if __name__ == "__main__":
    main()
