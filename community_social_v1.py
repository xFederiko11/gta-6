"""Public GitHub Issues discussions and recent site activity.

GitHub Pages has no server: one issue per guide is created by an Actions
workflow, never in a visitor browser. Comments require GitHub authentication,
are written on github.com, and displayed read-only through its public API.
No invented X metrics, no arbitrary HTML or stored visitor credentials.
"""
from __future__ import annotations
from datetime import datetime,timezone
from html import escape
import json,re
from pathlib import Path
from urllib.parse import quote,urlsplit
from urllib.request import Request,urlopen

REPO="xFederiko11/gta-6"
ROOT="https://api.github.com/repos/"+REPO
BASE="https://xfederiko11.github.io/gta-6/"
INDEX=Path("data/community_social.json")
MARKER="<!-- gta6-discussion-v1 "
LABEL="community-discussion"
MAX_ITEMS=100

def api(path:str, *, opener=urlopen, token:str=""):
    if not path.startswith("/"):
        raise ValueError("Relative GitHub endpoint required")
    headers={"Accept":"application/vnd.github+json","User-Agent":"Federiko11-GTA6-site/1",
             "X-GitHub-Api-Version":"2022-11-28"}
    if token:headers["Authorization"]="Bearer "+token
    req=Request(ROOT+path,headers=headers)
    with opener(req,timeout=15) as r:raw=r.read(600000)
    return json.loads(raw.decode("utf-8"))

def path_from_issue(issue:dict):
    body=str(issue.get("body") or "")
    match=re.search(r"<!-- gta6-discussion-v1 path=([a-z0-9-]+(?:/[a-z0-9-]+)*/?) -->",body)
    if not match:return None
    path=match.group(1)
    if not path.endswith("/") or path.startswith("/") or ".." in path:return None
    if not issue.get("html_url","").startswith("https://github.com/"+REPO+"/issues/"):
        return None
    if issue.get("state")!="open" or issue.get("pull_request"):
        return None
    if LABEL not in [v.get("name") for v in issue.get("labels",[]) if isinstance(v,dict)]:
        return None
    return path

def public_comment(c):
    if not isinstance(c,dict):return None
    user=c.get("user") or {}
    body=str(c.get("body") or "").strip()
    if user.get("type")!="User" or not user.get("login") or not body:return None
    if c.get("author_association")=="BOT":return None
    link=str(c.get("html_url",""))
    if not re.fullmatch(r"https://github\.com/"+re.escape(REPO)+r"/issues/\d+#issuecomment-\d+",link):return None
    stamp=c.get("created_at")
    try:
        if datetime.fromisoformat(str(stamp).replace("Z","+00:00")).tzinfo is None:return None
    except (ValueError,TypeError):return None
    return {"author":str(user["login"])[:39],"body":body[:260],
            "created_at":stamp,"url":link}

def collect(*,token="",read=api):
    entries=read("/issues?state=open&labels="+LABEL+"&per_page=100",token=token)
    if not isinstance(entries,list):raise ValueError("Untrusted GitHub Issues response")
    issues={};activity=[]
    for issue in entries[:MAX_ITEMS]:
        path=path_from_issue(issue)
        if not path or path in issues:continue
        number=issue["number"]
        comments=int(issue.get("comments") or 0)
        reactions=issue.get("reactions") or {}
        likes=max(0,int(reactions.get("+1") or 0))
        issues[path]={"number":number,"url":issue["html_url"],"title":str(issue.get("title",""))[:180],
                      "comment_count":comments,"likes":likes}
        if comments:
            try:
                recent=read(f"/issues/{number}/comments?per_page=5&page=1",token=token)
            except (ValueError,KeyError,TypeError):
                recent=[]
            for c in recent if isinstance(recent,list) else []:
                comment=public_comment(c)
                if comment:activity.append({**comment,"path":path})
    activity.sort(key=lambda x:x["created_at"],reverse=True)
    return {"schema":"community-social-v1","generated_utc":datetime.now(timezone.utc).isoformat(),
            "issues":issues,"latest_comments":activity[:6],
            "x_posts":[],"x_metrics_available":False,
            "comment_provider":"GitHub Issues; signin required; comment moderation/report available on GitHub"}

def load(path=INDEX):
    if not path.exists():return {"issues":{},"latest_comments":[],"x_posts":[]}
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema")!="community-social-v1":raise ValueError("Unsafe community social snapshot")
    return data

def widget(path:str, *, title="Partecipa alla discussione"):
    info=load().get("issues",{}).get(path)
    label="💬 "+title
    if not info:
        return ('<section class="social-discussion" aria-label="Commenti" data-discussion-path="'+escape(path,quote=True)+'">'
                '<h2>'+escape(label)+'</h2><p>Discussione in preparazione. '
                'Nel frattempo puoi partecipare dalla nostra pagina community su X.</p>'
                '<a href="https://x.com/xFederiko11" target="_blank" rel="noopener noreferrer">Apri @xFederiko11 su X ↗</a></section>')
    number=info["number"];url=escape(info["url"],quote=True)
    return (f'<section class="social-discussion" id="commenti" data-discussion-issue="{number}" '
            f'aria-label="Commenti su {escape(path,quote=True)}">'
            '<div class="social-discussion-head"><div><span class="eyebrow">LA COMMUNITY PARTECIPA</span>'
            f'<h2>{escape(label)}</h2><p>Consigli, posizioni, dubbi e segnalazioni in italiano.</p>'
            '</div><span class="social-count" data-comment-count>'
            f'{int(info["comment_count"])} commenti</span></div>'
            '<div class="social-discussion-cta">'
            f'<a class="v-button" href="{url}#new_comment_field" target="_blank" rel="noopener noreferrer">💬 Scrivi un commento</a>'
            f'<a class="v-button secondary" href="{url}" target="_blank" rel="noopener noreferrer">Leggi su GitHub</a>'
            '</div><p class="social-disclosure">Per commentare serve un account GitHub. '
            'Il tuo testo è pubblico e soggetto alle regole di GitHub; non viene pubblicato automaticamente su X. '
            'Una nuova discussione pertinente può ispirare un nostro post originale dopo i controlli editoriali.</p>'
            '<div data-comments-list class="social-comment-list" aria-live="polite">'
            '<p>Caricamento dei commenti pubblici…</p></div></section>')

def home_rail():
    data=load()
    items=data.get("latest_comments",[])[:4]
    parts=['<section class="social-home-rail" aria-label="Attività della community">'
           '<div class="v-section-head"><div><span class="v-kicker">LA COMMUNITY PARTECIPA</span>'
           '<h2>Ultimi commenti e discussioni</h2>'
           '<p>Contributi pubblici alle nostre guide, non recensioni inventate.</p></div>'
           '<a href="'+BASE+'scoperte/">Tutte le scoperte →</a></div><div class="social-home-grid">']
    for c in items:
        parts.append('<article class="social-comment-card"><span>💬 @'+escape(c["author"])+'</span>'
                     '<p>'+escape(c["body"][:170])+'</p><a href="'+escape(c["url"],quote=True)
                     '" rel="noopener noreferrer" target="_blank">Vai al commento ↗</a></article>')
    if not items:
        parts.append('<p class="social-empty">Ancora nessun commento verificato. '
                     'Apri una guida e inaugura la conversazione!</p>')
    parts.append('</div><div class="social-home-x"><div><strong>𝕏 Gli ultimi post di Federiko</strong>'
                 '<p>Apri la conversazione originale. Like, repost e visualizzazioni sono mostrati da X '
                 'quando disponibili: qui non inventiamo contatori.</p></div>'
                 '<button type="button" class="v-button secondary" data-x-timeline-load>'
                 'Mostra il feed X</button><a class="v-button" href="https://x.com/xFederiko11" '
                 'target="_blank" rel="me noopener noreferrer">Partecipa su X ↗</a>'
                 '<div data-x-timeline-slot aria-live="polite"></div></div></section>')
    return "".join(parts)
