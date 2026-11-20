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

def verified_permalinks(*,opener=None):
    """Read the published read-only Buffer receipts from the public bot repo.

    Missing files and connection failures are normal before initial sync; no
    permalink should be guessed from the Buffer post ID.
    """
    from urllib.error import HTTPError,URLError
    from community_social_v1 import verified_x_url
    target=("https://raw.githubusercontent.com/xFederiko11/"
            "federiko-gta-playstation-bot/main/data/x-permalinks-v1.json")
    http=opener or urlopen
    try:
        with http(Request(target,headers={
            "User-Agent":"GTA6-Italia-Real-Permalink-Site/1.0",
            "Accept":"application/json","Cache-Control":"no-cache"}),timeout=12) as r:
            contents=r.read(400000)
        data=json.loads(contents)
    except (HTTPError,URLError,TimeoutError,ValueError,OSError):
        return []
    if data.get("schema")!="verified-buffer-x-permalinks-v1":
        return []
    verified=[]
    for entry in data.get("posts",[])[:200]:
        if not isinstance(entry,dict):continue
        link=verified_x_url(entry.get("x_url"))
        target_url=str(entry.get("article_url") or "")
        parts=urlsplit(target_url)
        if (not link or parts.scheme!="https" or parts.hostname!="xfederiko11.github.io"
            or not parts.path.startswith("/gta-6/") or parts.query or parts.fragment
            or not target_url.endswith("/") or ".." in target_url):
            continue
        if entry.get("verified_by")!="Buffer sent Post.externalLink on verified @xFederiko11 channel":
            continue
        if not isinstance(entry.get("buffer_id"),str) or not isinstance(entry.get("sent_at"),str):
            continue
        text=str(entry.get("excerpt") or "").strip()
        if len(text)<12:continue
        verified.append({"url":target_url,"x_url":link,"text":text[:440],
                         "buffer_status":"sent","completed_utc":entry["sent_at"],
                         "source":"Buffer sent Post.externalLink on verified X channel"})
    return verified

def merge_post_snippets(ledger,verified):
    """Prefer actual X permalink-bearing records over older Buffer snippets."""
    mapped={}
    for item in ledger:
        if not isinstance(item,dict):continue
        url=item.get("url")
        if not url:continue
        mapped[(url,None)]=item
    for item in verified:
        # Keep only the freshest directly verifiable post per guide in primary UI.
        url=item["url"]
        for k in list(mapped):
            if k[0]==url:del mapped[k]
        mapped[(url,item["x_url"])]=item
    return sorted(mapped.values(),key=lambda x:x.get("completed_utc",""),reverse=True)[:100]

def main():
    try:
        posts=x_posts(token=os.getenv("GITHUB_TOKEN",""))
    except Exception as error:
        print("X_EXCERPT_LEDGER_NOT_AVAILABLE",type(error).__name__)
        posts=[]
    verified=verified_permalinks()
    posts=merge_post_snippets(posts,verified)
    result={"schema":VERSION,"x_posts":posts,"x_metrics_available":False,
            "comment_provider":"X/YouTube only; no Github account required"}
    INDEX.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("X_PUBLIC_EXCERPTS",len(posts),"verified_x_urls",len(verified),"no_comment_api_calls")

if __name__=="__main__":main()
