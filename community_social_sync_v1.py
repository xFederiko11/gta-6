"""Create and refresh first-party discussions in public GitHub Issues.

Site deploy has write permission only during an authenticated main-branch
build, never for PR validation. Uses standard GitHub Issues, not hidden
credentials in a browser. A new issue is unique by a validated path marker.
"""
from __future__ import annotations
import json,os
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
    for item in data:
        path=item.get("canonical_path") or ("guide-e-tutorial/"+item.get("id","")+"/")
        if not path.endswith("/") or not path.startswith("guide-e-tutorial/"):
            raise ValueError("Unsupported discussion guide path")
        name=item.get("safe_title") or item.get("title") or item.get("id")
        outputs.append((path,str(name)[:100]))
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
    INDEX.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("COMMUNITY_DISCUSSIONS_SNAPSHOT",len(snapshot["issues"]),
          len(snapshot["latest_comments"]),flush=True)

if __name__=="__main__":main()
