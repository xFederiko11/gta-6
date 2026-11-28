#!/usr/bin/env python3
"""Offline import of owner-approved aggregate Umami Pages counts.

This is NOT a raw Cloud export reader. Only two-column CSV copied from a
complete aggregate Pages report is accepted. No network, sessions, events,
cookies, tokens, visitor IDs, URLs with query strings, or source CSV output.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlsplit

from article_chronology_v1 import BASE, inventory, record
from magazine_popular_v1 import SNAPSHOT, validate

MAX_BYTES = 100_000
MAX_ROWS = 5_000
HEADER = ("path", "pageviews")
HOST = urlsplit(BASE).netloc
PREFIX = urlsplit(BASE).path
SLUG = re.compile(r"(?:[a-z0-9-]+/)*\Z")

def canonical_path(raw):
    """Only site-relative canonical paths or URLs on the exact Pages site."""
    value = raw.strip()
    if not value or len(value)>512 or any(c in value for c in ("?", "#", "%", "\\")):
        raise ValueError("Invalid path: use only clean aggregate page paths")
    if any(ord(c)<32 for c in value):
        raise ValueError("Invalid path")
    parts = urlsplit(value)
    if parts.scheme or parts.netloc:
        if parts.scheme!="https" or parts.netloc!=HOST:
            raise ValueError("Unexpected origin in aggregate report")
        if not parts.path.startswith(PREFIX):
            raise ValueError("Path outside this website")
        value=parts.path
    if value==PREFIX.rstrip("/"):
        value=PREFIX
    if value.startswith("/"):
        if not value.startswith(PREFIX):
            raise ValueError("Path outside this website")
        value=value[len(PREFIX):]
    if value=="index.html":
        value=""
    elif value.endswith("/index.html"):
        value=value[:-len("index.html")]
    if value and not value.endswith("/"):
        value+="/"
    if not SLUG.fullmatch(value):
        raise ValueError("Noncanonical path in aggregate report")
    return value

def convert(text, start, end, today, articles):
    """Return only the five public article rows, never raw analytics data."""
    if len(text.encode("utf-8"))>MAX_BYTES:
        raise ValueError("Aggregate report too large")
    reader=csv.reader(io.StringIO(text.lstrip("\ufeff")),strict=True)
    header=next(reader,None)
    if header is None or tuple(x.strip().lower() for x in header)!=HEADER:
        raise ValueError("Expected exactly two columns: path,pageviews")
    seen=set()
    rows=[]
    for i, row in enumerate(reader,1):
        if i>MAX_ROWS:
            raise ValueError("Too many aggregate rows")
        if not row or all(not x.strip() for x in row):
            continue
        if len(row)!=2:
            raise ValueError("Unexpected columns: do not import raw analytics")
        path=canonical_path(row[0])
        if path in seen:
            raise ValueError("Duplicate canonical path: aggregate it before import")
        seen.add(path)
        count=row[1].strip()
        if not re.fullmatch(r"[0-9]{1,10}",count):
            raise ValueError("Pageviews must be a nonnegative integer")
        if path in articles and not articles[path]["secret"]:
            rows.append({"path":path,"pageviews":int(count)})
    snapshot={"schema":"magazine-pageviews-v1","source":"Umami dashboard export",
              "metric":"pageviews","start":start.isoformat(),"end":end.isoformat(),
              "items":rows}
    _,_,ranked=validate(snapshot,today,articles)
    if not ranked:
        raise ValueError("No positive article pageviews: keep the honest fallback")
    snapshot["items"]=[{"path":p,"pageviews":n} for p,n in ranked]
    return snapshot

def write_snapshot(snapshot,destination):
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=destination.parent,
                                         prefix=".popular-",delete=False) as out:
            temporary=out.name
            json.dump(snapshot,out,ensure_ascii=False,indent=2)
            out.write("\n")
        os.replace(temporary,destination)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv",help="Aggregate CSV outside the repository; - reads stdin")
    parser.add_argument("--start",required=True,type=date.fromisoformat)
    parser.add_argument("--end",required=True,type=date.fromisoformat)
    parser.add_argument("--complete-report",action="store_true",help="Confirm this covers all page rows for the stated period, not a truncated sample")
    parser.add_argument("--approve-public-aggregates",action="store_true",help="Authorize publication of up to five article paths and their pageview counts")
    parser.add_argument("--write",action="store_true",help="Write the sanitized snapshot; otherwise validate only")
    args=parser.parse_args()
    if not args.complete_report or not args.approve_public_aggregates:
        parser.error("Both report completeness and permission to publish aggregate counts are required")
    try:
        if args.csv=="-":
            raw=sys.stdin.buffer.read(MAX_BYTES+1)
        else:
            with open(args.csv,"rb") as f:
                raw=f.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:
            raise ValueError("Aggregate report too large")
        catalog={row[0]:record(row) for row in inventory()}
        snapshot=convert(raw.decode("utf-8-sig"),args.start,args.end,date.today(),catalog)
        if args.write:
            write_snapshot(snapshot,SNAPSHOT)
        print("UMAMI_AGGREGATE_IMPORT_OK",len(snapshot["items"]),"article rows",snapshot["start"],snapshot["end"],
              "written" if args.write else "validation only")
    except (OSError,ValueError,csv.Error,UnicodeError):
        # Never echo source CSV, paths, or exception messages from private data.
        parser.exit(2,"Aggregate import refused. Check the two-column format, clean paths, dates and counts; existing snapshot is unchanged.\n")

if __name__=="__main__":
    main()
