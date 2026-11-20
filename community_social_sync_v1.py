"""Read only our own Buffer-sent post records and verified X links.

No visitor needs GitHub. This bridge has NO GitHub Issues creation/read
permissions and makes no replies or likes.
"""
from __future__ import annotations
import json,os,base64
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit
from community_social_v1 import INDEX,VERSION,verified_x_url

def x_posts(*, opener=None, token=""):
    """Read only Buffer-sent excerpts. No fabricated X link or metrics."""
    from urllib.request import Request,urlopen
    from urllib.parse import urlsplit
    target=("https://api.github.com/repos/xFederiko11/"
            "federiko-gta-playstation-bot/contents/.state/editorial-autopilot-v137.json")
    headers={"Accept":"application/vnd.github+json","User-Agent":"Federiko-GTA-VI-Site-Bridge/1"}
    if token:headers["Authorization"]="Bearer "+token
    http=opener or urlopen
    with http(Request(target,headers=headers),timeout=15) as r:
        raw=r.read(2000000)
    response=json.loads(raw)
    if response.get("encoding")!="base64":raise ValueError("Invalid GitHub file encoding")
    state=json.loads(base64.b64decode(response["content"]))
    found={}
    for entry in state.get("entries",{}).values():
        if not isinstance(entry,dict) or entry.get("status")!="sent":continue
        url=str(entry.get("url") or "")
        parsed=urlsplit(url)
        if parsed.scheme!="https" or parsed.hostname!="xfederiko11.github.io" or not parsed.path.startswith("/gta-6/"):continue
        body=entry.get("thread")
        excerpt=(body[0] if isinstance(body,list) and body and body[0] else entry.get("text") or "")
        if not isinstance(excerpt,str) or not excerpt.strip():continue
        item={"url":url,"text":excerpt.strip()[:440],"buffer_status":"sent",
              "x_url":verified_x_url(entry.get("external_url") or entry.get("external_link") or ""),
              "completed_utc":str(entry.get("completed_utc") or entry.get("reserved_utc") or ""),
              "source":"Buffer editorial journal; not independently verified X post URL"}
        if url not in found or item["completed_utc"]>found[url]["completed_utc"]:found[url]=item
    return sorted(found.values(),key=lambda x:x["completed_utc"],reverse=True)[:15]

def main():
    try:
        posts=x_posts(token=os.getenv("GITHUB_TOKEN",""))
    except Exception as error:
        print("X_EXCERPT_LEDGER_NOT_AVAILABLE",type(error).__name__)
        posts=[]
    result={"schema":VERSION,"x_posts":posts,"x_metrics_available":False,
            "comment_provider":"X/YouTube only; no Github account required"}
    INDEX.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("X_PUBLIC_EXCERPTS",len(posts),"no_comment_api_calls")

if __name__=="__main__":main()
