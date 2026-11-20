"""Create and refresh first-party discussions in public GitHub Issues.

Site deploy has write permission only during an authenticated main-branch
build, never for PR validation. Uses standard GitHub Issues, not hidden
credentials in a browser. A new issue is unique by a validated path marker.
"""
from __future__ import annotations
import json,os,base64
from pathlib import Path
import subprocess
import time
from community_social_v1 import ROOT,MARKER,LABEL,collect,INDEX

TARGETS=[
 ("scoperte/","Scoperte GTA VI — segnala una nuova scoperta"),
 ("soldi-facili/","Soldi facili GTA VI — confrontiamoci"),
 ("auto-speciali/","Auto speciali GTA VI — posizioni"),
 ("salvare-auto/","Salvare le auto GTA VI — garage e tracker"),
 ("trofei/","Trofei e platino GTA VI — domande"),
]
def topics():
    outputs=list(TARGETS)
    data=json.loads(Path("data/guide.json").read_text(encoding="utf-8"))["guides"]
    data+=json.loads(Path("data/visual_guides.json").read_text(encoding="utf-8"))["guides"]
    known={p for p,_ in outputs}
    for item in data:
        path=item.get("canonical_path") or ("guide-e-tutorial/"+item.get("id","")+"/")
        if path in known:continue  # e.g. salvar-auto/ is already a hub
        if not path.endswith("/") or not path.startswith("guide-e-tutorial/"):
            raise ValueError("Unsupported discussion guide path")
        name=item.get("safe_title") or item.get("title") or item.get("id")
        outputs.append((path,str(name)[:100]));known.add(path)
    if len(set(p for p,_ in outputs))!=len(outputs):
        raise ValueError("Duplicate discussion paths")
    return outputs

def gh(*args):
    r=subprocess.run(["gh","api",*args],capture_output=True,text=True,check=True,timeout=30)
    return r.stdout

def ensure(*, limit=8):
    if not os.getenv("GH_TOKEN"):
        raise RuntimeError("GH_TOKEN required for authenticated issue maintenance")
    existing=json.loads(gh("/repos/xFederiko11/gta-6/issues?state=all&per_page=100"))
    known={};titles=[]
    for issue in existing:
        from community_social_v1 import path_from_issue
        # Recognize a path only from an authentic issue marker and label.
        # Closed discussions are not recreated by automation.
        body=str(issue.get("body") or "")
        for path,_ in topics():
            if MARKER+"path="+path+" -->" in body:
                known[path]=issue
    created=0
    for path,title in topics():
        if path in known:continue
        if created>=limit:break
        body=(MARKER+"path="+path+" -->\n"
              "## Condividi una scoperta, un dubbio o una soluzione\n\n"
              "Scrivi in italiano e cita la fonte quando disponibile. "
              "Niente spoiler senza avviso, link pubblicitari o dati personali. "
              "I contenuti non sono verificati dal solo commento.\n\n"
              "Guida collegata: https://xfederiko11.github.io/gta-6/"+path+"\n\n"
              "I commenti sono pubblici e soggetti alle regole GitHub. "
              "Un commento non autorizza a ripubblicarne il testo su X.\n")
        result=json.loads(gh("-X","POST","/repos/xFederiko11/gta-6/issues",
                      "-f","title=💬 GTA VI | "+title,
                      "-f","body="+body,
                      "-f","labels[]="+LABEL))
        print("COMMUNITY_DISCUSSION_CREATED",path,result.get("number"),flush=True)
        created+=1
        time.sleep(0.6)
    return created

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
              "completed_utc":str(entry.get("completed_utc") or entry.get("reserved_utc") or ""),
              "source":"Buffer editorial journal; not independently verified X post URL"}
        if url not in found or item["completed_utc"]>found[url]["completed_utc"]:found[url]=item
    return sorted(found.values(),key=lambda x:x["completed_utc"],reverse=True)[:15]

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("read","ensure"),required=True)
    args=parser.parse_args()
    if args.mode=="ensure":
        ensure()
    try:
        snapshot=collect(token=os.getenv("GH_TOKEN",""))
    except Exception as error:
        print("COMMUNITY_DISCUSSIONS_READ_UNAVAILABLE",type(error).__name__)
        # Preserve other content; site remains navigable. Don't fabricate
        # counts or overwrite a prior successful snapshot on read failure.
        if INDEX.is_file():return
        snapshot={"schema":"community-social-v1","generated_utc":None,
                  "issues":{},"latest_comments":[],"x_posts":[],"x_metrics_available":False}
    try:
        snapshot["x_posts"]=x_posts(token=os.getenv("GH_TOKEN",""))
    except Exception as error:
        print("COMMUNITY_X_LEDGER_UNAVAILABLE",type(error).__name__)
        snapshot["x_posts"]=[]
    snapshot["x_metrics_available"]=False
    INDEX.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("COMMUNITY_DISCUSSIONS_SNAPSHOT",len(snapshot["issues"]),
          len(snapshot["latest_comments"]),flush=True)

if __name__=="__main__":main()
