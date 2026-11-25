"""Read-only bridge for the existing bot's public official patch metadata.

No third-party calls during the site generator, no copied notes, no automatic
translations, no invented builds. Failed production imports prevent replacing
the last published site with a degraded archive. PRs/local builds use an
explicit empty baseline unless a validated runtime file is available.
"""
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
from urllib.request import Request, build_opener, HTTPRedirectHandler

SOURCE = "https://raw.githubusercontent.com/xFederiko11/federiko-gta-playstation-bot/main/history-public.json"
OFFICIAL_ARTICLE = "https://support.rockstargames.com/articles/sN5pEdFYZdlvijKXd6xpJ/grand-theft-auto-vi-launch-updates-ps5-xbox-series-x-or-s"
DEST = Path(".runtime/patch-observations-v1.json")
MAX_BYTES = 2_000_000
SCHEMA = "gta6-patch-observations-v1"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def utc(value):
    if not isinstance(value, str):
        raise ValueError("Missing observation time")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Observation time must have timezone")
    return dt.astimezone(timezone.utc)


def iso(dt):
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def valid_day(value):
    dt = date.fromisoformat(value)
    if dt.isoformat() != value or dt.year < 2026:
        raise ValueError("Invalid patch date")
    return dt


def validate_snapshot(data, *, now=None):
    now = now or datetime.now(timezone.utc)
    if not isinstance(data, dict) or data.get("schema") != SCHEMA or not isinstance(data.get("observations"), list):
        raise ValueError("Invalid patch observation snapshot")
    if set(data) != {"schema", "exported_at", "observations"}:
        raise ValueError("Unexpected snapshot fields")
    exported = utc(data["exported_at"])
    if exported > now:
        raise ValueError("Future export")
    seen = set()
    for row in data["observations"]:
        if not isinstance(row, dict) or set(row) != {"date","first_observed_at","last_observed_at","entry_count","content_sha256","source"}:
            raise ValueError("Invalid observation fields")
        day = valid_day(row["date"])
        first, last = utc(row["first_observed_at"]), utc(row["last_observed_at"])
        if row["date"] in seen or not day <= first.date() or not first <= last <= exported:
            raise ValueError("Duplicate or inconsistent observation")
        if row["source"] != OFFICIAL_ARTICLE or type(row["entry_count"]) is not int or not 1 <= row["entry_count"] <= 300:
            raise ValueError("Invalid official patch metadata")
        if not isinstance(row["content_sha256"],str) or not re.fullmatch("[0-9a-f]{64}",row["content_sha256"]):
            raise ValueError("Invalid revision identifier")
        seen.add(row["date"])
    return data


def extract(payload, *, now=None):
    if not isinstance(payload, dict) or payload.get("schema_version") != 1 or not isinstance(payload.get("records"), list):
        raise ValueError("Invalid public history schema")
    observations = []
    for record in payload["records"]:
        if not isinstance(record, dict):
            raise ValueError("Invalid history record")
        if record.get("event_type") != "official_patch_notes_available":
            continue
        if (record.get("game") != "GTA VI" or record.get("platform") != "common"
            or record.get("region") != "global" or record.get("metric_kind") != "availability"
            or record.get("date_precision") != "date" or record.get("source_tier") != "primary"
            or record.get("verification") != "verified" or record.get("source_url") != OFFICIAL_ARTICLE
            or record.get("version") is not None or record.get("size_bytes") is not None):
            raise ValueError("Unverified or incompatible patch observation")
        metadata = record.get("metadata")
        if (not isinstance(metadata,dict) or metadata.get("kind") != "official_patch_note_metadata_v1"
            or metadata.get("platforms") != ["PS5","Xbox Series X|S"]):
            raise ValueError("Unknown patch observation metadata")
        observations.append({"date":record["occurred_at"],"first_observed_at":iso(utc(record["first_observed_at"])),
                             "last_observed_at":iso(utc(record["last_observed_at"])),
                             "entry_count":metadata.get("entry_count"),"content_sha256":metadata.get("content_sha256"),
                             "source":OFFICIAL_ARTICLE})
    return validate_snapshot({"schema":SCHEMA,"exported_at":iso(utc(payload["generated_at"])),
                              "observations":sorted(observations,key=lambda x:x["date"],reverse=True)},now=now)


def fetch(*, opener=None, now=None):
    opener = opener or build_opener(NoRedirect()).open
    request = Request(SOURCE, headers={"Accept":"application/json, text/plain",
                                     "User-Agent":"GTA6Italia-PatchArchive/1.0","Cache-Control":"no-cache"})
    with opener(request,timeout=12) as response:
        if response.status != 200 or response.geturl() != SOURCE:
            raise ValueError("Unexpected bot history response")
        raw = response.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:
        raise ValueError("Bot history exceeds maximum size")
    return extract(json.loads(raw.decode("utf-8")),now=now)


def load(path=DEST):
    if not path.is_file():
        if os.getenv("PATCH_LEDGER_REQUIRED") == "true":
            raise FileNotFoundError("Validated production patch history required")
        return {"schema":SCHEMA,"exported_at":None,"observations":[]}
    return validate_snapshot(json.loads(path.read_text(encoding="utf-8")))


def main():
    data = fetch()
    DEST.parent.mkdir(parents=True,exist_ok=True)
    temporary = DEST.with_suffix(".tmp")
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    temporary.replace(DEST)
    print("PATCH_OBSERVATIONS_VALIDATED",len(data["observations"]),"history_export",data["exported_at"])


if __name__ == "__main__":
    main()
