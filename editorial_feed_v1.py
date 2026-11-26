"""Public reader-facing article feed, generated only from rendered reviewed pages.

No queue, candidate research, credentials or private workflow reports. The
consumer must independently verify canonical, photo digest and deduplication.
"""
from pathlib import Path
from html.parser import HTMLParser
from datetime import date
import argparse,hashlib,json,re,time
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.parse import urlsplit

ROOT=Path("_site")
BASE="https://xfederiko11.github.io/gta-6/"
FEED_PATH="articoli/feed.json"
SCHEMA="gta6-editorial-feed-v1"
KINDS={"official_game_photo","approved_gameplay"}
FIELDS={"url","title","summary","published","image","sha256","kind"}

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.m={};self.canonical=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="meta":
            key=a.get("name") or a.get("property")
            if key:self.m.setdefault(key,[]).append(a.get("content",""))
        if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
    def one(self,key):
        values=self.m.get(key,[])
        if len(values)!=1:raise ValueError("Missing or duplicated public metadata: "+key)
        return values[0]

def valid_summary(value):
    return (isinstance(value,str) and 40<=len(value)<=150
            and not any(x in value for x in ("<",">","@","http:","https:","\n","\r"))
            and not any(ord(x)<32 for x in value))

def validate(doc):
    if not isinstance(doc,dict) or set(doc)!={"schema","items"} or doc["schema"]!=SCHEMA:
        raise ValueError("Unexpected reader feed schema")
    rows=doc["items"]
    if not isinstance(rows,list) or len(rows)>100:raise ValueError("Invalid reader inventory")
    seen=set()
    for row in rows:
        if set(row)!=FIELDS or not re.fullmatch(re.escape(BASE)+r"articoli/[a-z0-9-]+/",row["url"]) or row["url"] in seen:
            raise ValueError("Invalid/duplicate editorial URL")
        seen.add(row["url"])
        if not isinstance(row["title"],str) or not 8<=len(row["title"])<=140 or not valid_summary(row["summary"]):
            raise ValueError("Invalid public excerpt")
        date.fromisoformat(row["published"])
        rel=row["url"].removeprefix(BASE)
        cover=BASE+"assets/social-cards/"+hashlib.sha256(rel.encode()).hexdigest()[:16]+".jpg"
        if row["image"]!=cover or row["kind"] not in KINDS or not re.fullmatch(r"[a-f0-9]{64}",row["sha256"]):
            raise ValueError("Invalid editorial photograph")
    return doc

def verify_page(row,html,binary):
    p=Page();p.feed(html)
    if (p.canonical!=[row["url"]] or p.one("gta6:share-summary")!=row["summary"]
        or p.one("gta6:cover-kind")!=row["kind"] or p.one("gta6:cover-sha256")!=row["sha256"]
        or p.one("og:image")!=row["image"] or p.one("twitter:image")!=row["image"]):
        raise ValueError("Reader feed differs from article")
    if not 8000<=len(binary)<=1600000 or not binary.startswith(bytes.fromhex("ffd8ff")) or not binary.endswith(bytes.fromhex("ffd9")) or hashlib.sha256(binary).hexdigest()!=row["sha256"]:
        raise ValueError("Photograph bytes differ from article")

def build(root=ROOT):
    rows=[]
    for a in json.loads(Path("data/articles.json").read_text(encoding="utf-8"))["articles"]:
        summary=a.get("share_summary")
        if summary is None:continue
        path=a["path"];html=(root/path/"index.html").read_text(encoding="utf-8")
        p=Page();p.feed(html)
        row={"url":BASE+path,"title":a["title"],"summary":summary,"published":a["published"],
             "image":p.one("og:image"),"kind":p.one("gta6:cover-kind"),"sha256":p.one("gta6:cover-sha256")}
        validate({"schema":SCHEMA,"items":[row]})
        binary=(root/row["image"].removeprefix(BASE)).read_bytes()
        verify_page(row,html,binary);rows.append(row)
    doc=validate({"schema":SCHEMA,"items":sorted(rows,key=lambda r:(r["published"],r["url"]),reverse=True)})
    (root/FEED_PATH).write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EDITORIAL_FEED_BUILD_OK",len(rows),"public reader excerpts")
    return doc

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

def fetch(url,limit,mime):
    if not url.startswith(BASE):raise ValueError("Unexpected public URL")
    opener=build_opener(NoRedirect())
    req=Request(url,headers={"User-Agent":"GTA6Italia-FeedQA/1.0","Cache-Control":"no-cache"})
    with opener.open(req,timeout=10) as res:
        if res.status!=200 or res.geturl()!=url or res.headers.get_content_type() not in mime:raise ValueError("Unexpected HTTP source")
        data=res.read(limit+1)
        if len(data)>limit:raise ValueError("Oversized public source")
        return data

def live():
    for attempt in range(3):
        try:
            doc=validate(json.loads(fetch(BASE+FEED_PATH,160000,{"application/json","text/plain","application/octet-stream"})))
            # Compare against this exact checkout so a stale feed cannot pass.
            expected=build_expected()
            if {r["url"]:r["summary"] for r in doc["items"]}!=expected:raise ValueError("Stale or incomplete reader feed")
            for row in doc["items"]:
                html=fetch(row["url"],1500000,{"text/html"}).decode("utf-8")
                jpeg=fetch(row["image"],1600000,{"image/jpeg"})
                verify_page(row,html,jpeg)
            print("PUBLIC_EDITORIAL_FEED_OK",len(doc["items"]),"article-photo contracts")
            return
        except (OSError,ValueError,KeyError,TypeError):
            if attempt==2:raise
            time.sleep(4*(attempt+1))

def build_expected():
    return {BASE+a["path"]:a["share_summary"] for a in json.loads(Path("data/articles.json").read_text(encoding="utf-8"))["articles"] if "share_summary" in a}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--live",action="store_true");args=p.parse_args()
    live() if args.live else build()
