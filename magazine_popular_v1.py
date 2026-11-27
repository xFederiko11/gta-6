"""Display real aggregate Umami pageviews only; never estimate popularity.

Input data/popular_articles_v1.json is an OPTIONAL owner-approved aggregate
export, not a browser tracker, private analytics dump, or API credential.
Umami Hobby has dashboard export but not API access: no paid upgrade here.
"""
from datetime import date,timedelta
from html import escape
from pathlib import Path
from functools import lru_cache
import json
from article_chronology_v1 import BASE,inventory,record
SNAPSHOT=Path("data/popular_articles_v1.json")
EDITORIAL=[
 ("salvare-auto/","Salvare e registrare le auto"),
 ("garage-gratuiti/","Sbloccare i garage gratuiti"),
 ("guide-e-tutorial/scansionare-veicoli/","Scansionare i veicoli con WAiNK"),
 ("trofei/roadmap-platino/","Roadmap del platino"),
 ("guide-e-tutorial/soldi-facili-capitolo-1/","Soldi nel Capitolo 1"),
]
def esc(value):return escape(str(value),quote=True)
def validate(snapshot,today,articles):
    if not isinstance(snapshot,dict) or snapshot.get("schema")!="magazine-pageviews-v1" or snapshot.get("source")!="Umami dashboard export" or snapshot.get("metric")!="pageviews":
        raise ValueError("Invalid aggregate snapshot")
    start=date.fromisoformat(snapshot["start"]);end=date.fromisoformat(snapshot["end"])
    if not start<=end<=today or (end-start).days>30 or today-end>timedelta(days=7):
        raise ValueError("Stale or invalid date range")
    counts={}
    for row in snapshot["items"]:
        p=row["path"];n=row["pageviews"]
        if p in counts or type(n) is not int or n<0:raise ValueError("Invalid aggregate")
        if p in articles and not articles[p]["secret"]:counts[p]=n
    return start,end,sorted(((p,n) for p,n in counts.items() if n>0),key=lambda pair:(-pair[1],pair[0]))[:5]
@lru_cache(maxsize=1)
def ranked():
    articles={r[0]:record(r) for r in inventory()}
    try:
        start,end,rows=validate(json.loads(SNAPSHOT.read_text(encoding="utf-8")),date.today(),articles)
        return start,end,[(articles[p]["title"],p,n) for p,n in rows]
    except (OSError,ValueError,KeyError,TypeError,AttributeError):
        return None,None,[]
def popular_panel():
    start,end,rows=ranked()
    if rows:
        note="Visualizzazioni di pagina, non lettori unici · "+start.strftime("%d/%m")+"–"+end.strftime("%d/%m/%Y")+" · Umami"
        entries="".join('<li><span class="sb-rank" aria-hidden="true">'+str(i)+'</span><a href="'+BASE+p+'">'+esc(t)+'<small>'+str(n)+' visualizzazioni</small></a></li>' for i,(t,p,n) in enumerate(rows,1))
        return '<div class="sb-panel sb-popular" data-magazine-popular="measured"><p class="sb-kicker">TOP 5</p><p class="sb-heading">Articoli più letti</p><p class="sb-popular-note">'+esc(note)+'</p><ol class="sb-popular-list">'+entries+'</ol></div>'
    # Do not label an editorial list as a measured ranking.
    entries="".join('<li><a href="'+BASE+p+'">'+esc(t)+' <span aria-hidden="true">→</span></a></li>' for p,t in EDITORIAL)
    return '<div class="sb-panel sb-popular" data-magazine-popular="unavailable"><p class="sb-kicker">TOP 5 · IN ATTESA DEI DATI</p><p class="sb-heading">Articoli più letti</p><p class="sb-popular-note">Classifica non disponibile. Nel frattempo, cinque guide scelte dalla redazione:</p><ul class="sb-popular-list">'+entries+'</ul></div>'
