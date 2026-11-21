"""GTA VI Italia public X growth evidence: verifiable sources, never fake reach.

Production reads only three public issues of the user's existing GTA VI
bot through GitHub's anonymous REST API. Each source can be unavailable:
a missing source means NULL, never 0. In PRs this module uses a deliberately
empty report, so build/tests are fully offline.
"""
from __future__ import annotations
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import argparse,json,re

SCHEMA="gta6-x-growth-provenance-v1"
ISSUE_IDS=(48,72,42)
API="https://api.github.com/repos/xFederiko11/federiko-gta-playstation-bot/issues/"
PUBLIC="https://github.com/xFederiko11/federiko-gta-playstation-bot/issues/"
SITE="https://xfederiko11.github.io/gta-6/"
PATH="crescita-x/"
REPORT=Path(".runtime/x-growth-evidence-v1.json")
MAX_BYTES=160_000
MAX_COUNT=100_000_000
MAX_AGE=timedelta(hours=48)


def e(value):
    return escape(str(value),quote=True)


def iso(value):
    if not isinstance(value,str):raise ValueError("Timestamp absent")
    d=datetime.fromisoformat(value.replace("Z","+00:00"))
    if d.tzinfo is None:raise ValueError("Timestamp without timezone")
    return d.astimezone(timezone.utc)


def blank(now=None):
    current=now or datetime.now(timezone.utc)
    if current.tzinfo is None:raise ValueError("Timestamp required")
    clock=current.astimezone(timezone.utc)
    return {"schema":SCHEMA,"checked_utc":clock.isoformat(),
            "source_status":"unavailable",
            "radar":{"articles_checked":None,"post_urls_discovered":None,
                     "recent_links":None,"official_oembed_checks":None,
                     "questions_verified":None,"source_posts_verified":None,
                     "owned_posts_in_issue":None},
            "buffer":{"impressions":None,"status":"not_available",
                      "sample_label":"Subset of at most 10 Buffer Sent posts",
                      "checked_utc":None},
            "x":{"profile_visits":None,"new_followers":None,
                 "metrics_date":None,"provenance":"not_observed"},
            "umami":{"site_tracking_configured":True,"events_reported":None,
                     "note":"Tracker configured; no authorized event export available to this dashboard"},
            "sources":[{"issue":n,"url":PUBLIC+str(n),"observed_utc":None,
                        "status":"not_fetched"} for n in ISSUE_IDS],
            "disclaimer":"Counts from GitHub issues reflect a bounded audit; they are not the total activity of X. A NULL metric means unavailable, not zero."}


def public_issue(n,opener=urlopen):
    if n not in ISSUE_IDS:raise ValueError("Unapproved public issue number")
    address=API+str(n)
    request=Request(address,headers={"Accept":"application/vnd.github+json",
                        "User-Agent":"GTA6Italia-PublicGrowthEvidence/1.0"})
    with opener(request,timeout=12) as response:
        if response.geturl()!=address:
            raise ValueError("Issue API redirected unexpectedly")
        content=response.read(MAX_BYTES+1)
        if len(content)>MAX_BYTES:raise ValueError("Oversized public issue")
    record=json.loads(content.decode("utf-8"))
    if (not isinstance(record,dict) or record.get("number")!=n or
        record.get("html_url")!=PUBLIC+str(n) or
        "pull_request" in record or not isinstance(record.get("body"),str) or
        len(record["body"])>125_000):
        raise ValueError("Issue provenance does not match the fixed source")
    iso(record.get("updated_at"))
    return record


def number(pattern,body):
    match=re.search(pattern,body,re.I|re.M)
    if not match:return None
    value=int(match.group(1))
    return value if 0<=value<=MAX_COUNT else None


def parse_radar(body):
    if not body.startswith("# GTA VI - Social Radar:"):
        raise ValueError("Unrecognized Social Radar issue")
    segment=body.split("## 🆓 Tweet trovati senza API X a pagamento",1)
    if len(segment)!=2:raise ValueError("No auditable public-radar section")
    part=segment[1].split("\n---",1)[0]
    radar={
      "articles_checked":number(r"Articoli di testate controllati:\s*(\d+)",part),
      "post_urls_discovered":number(r"Permalink X candidati rintracciati \(non tutti verificati\):\s*(\d+)",part),
      "recent_links":number(r"Candidati recenti dall'ID X \(NON verificati\):\s*(\d+)",part),
      "official_oembed_checks":number(r"embed originali interrogati:\s*(\d+)",part),
      "questions_verified":number(r"Domande esterne confermate da oEmbed:\s*(\d+)",part),
      "source_posts_verified":number(r"altri post verificati usabili solo come riferimenti:\s*(\d+)",part),
      "owned_posts_in_issue":None,
    }
    if radar["questions_verified"] is None and "Nessun permalink esterno recente confermato tramite X oEmbed" in part:
        radar["questions_verified"]=0
        radar["source_posts_verified"]=0
    if (radar["articles_checked"] is not None and radar["articles_checked"]>4 or
        radar["official_oembed_checks"] is not None and radar["official_oembed_checks"]>8):
        raise ValueError("Public radar limits unexpectedly exceeded")
    return radar


def parse_buffer(body,now):
    if "## 📈 Buffer: diagnosi sperimentale delle performance X" not in body:
        raise ValueError("Unknown Buffer probe report")
    match=re.search(r"Controllo UTC:\s*([^\s]+)",body)
    if not match:raise ValueError("Buffer report has no timestamp")
    checked=iso(match.group(1))
    result={"impressions":None,"status":"not_reported","checked_utc":checked.isoformat(),
            "sample_label":"Subset of at most 10 Buffer Sent posts"}
    if now-checked>MAX_AGE:
        result["status"]="stale"
        return result
    if "Metriche X da Buffer: **non disponibili**" in body:
        result["status"]="unavailable"
        return result
    value=number(r"^- Impression \(Buffer\):\s*(\d+)\s*$",body)
    if value is not None and "Totali **solo sulle voci effettivamente ricevute nel campione**" in body:
        result.update({"impressions":value,"status":"reported_buffer_subset"})
    return result


def parse_owned_and_manual(body):
    if "<!-- gta6-organic-growth-v1 -->" not in body:
        raise ValueError("Unknown organic growth report")
    own=body.split("## 🎯 Conversazioni nostre da valorizzare (post X reali)",1)
    samples=None
    if len(own)==2:
        piece=own[1].split("\n## ",1)[0]
        samples=len(set(re.findall(r"\[Apri la conversazione originale\]\((https://x\.com/xFederiko11/status/\d{8,25})\)",piece)))
    day=re.search(r"\*\*Data registrata:\*\*\s*(\d{4}-\d{2}-\d{2})",body)
    manual={"profile_visits":None,"new_followers":None,"metrics_date":None,
            "provenance":"not_observed"}
    if day:
        found={}
        try:datetime.strptime(day.group(1),"%Y-%m-%d")
        except ValueError:raise ValueError("Invalid manual metric date") from None
        # Only values physically recorded by the owner in the public issue,
        # never a followers count inferred from X link open intents.
        for key in ("x_profile_visits","x_new_followers"):
            hit=re.search(r"(?m)^- "+key+r":\s*(\d+)\s*$",body[day.end():])
            if hit:
                val=int(hit.group(1))
                if val<=MAX_COUNT:found[key]=val
        manual.update({"profile_visits":found.get("x_profile_visits"),
                       "new_followers":found.get("x_new_followers"),
                       "metrics_date":day.group(1),"provenance":"owner_manual_entry"})
    return samples,manual


def report(issues,now=None):
    data=blank(now)
    clock=iso(data["checked_utc"])
    valid=0
    for source in data["sources"]:
        n=source["issue"]
        raw=issues.get(n)
        if raw is None:continue
        try:
            if raw.get("number")!=n or raw.get("html_url")!=source["url"]:
                raise ValueError("Wrong issue")
            updated=iso(raw.get("updated_at"))
            source["observed_utc"]=updated.isoformat()
            if updated>clock+timedelta(minutes=10) or clock-updated>MAX_AGE:
                source["status"]="stale"
                continue
            body=raw["body"]
            if n==48:
                data["radar"].update(parse_radar(body))
            elif n==72:
                data["buffer"]=parse_buffer(body,clock)
            elif n==42:
                samples,manual=parse_owned_and_manual(body)
                data["radar"]["owned_posts_in_issue"]=samples
                data["x"]=manual
            source["status"]="verified_public_issue"
            valid+=1
        except (KeyError,ValueError,TypeError,AttributeError):
            source["status"]="invalid"
    data["source_status"]="verified" if valid==len(ISSUE_IDS) else "partial" if valid else "unavailable"
    return data


def obtain(now=None,opener=urlopen):
    found={}
    for n in ISSUE_IDS:
        try:found[n]=public_issue(n,opener)
        except (HTTPError,URLError,TimeoutError,OSError,ValueError,TypeError,json.JSONDecodeError):
            continue
    return report(found,now)


def read_report(path=REPORT):
    src=Path(path)
    if not src.exists():return blank()
    obj=json.loads(src.read_text(encoding="utf-8"))
    if obj.get("schema")!=SCHEMA or set(obj.get("radar",{}))!=set(blank()["radar"]):
        raise ValueError("Unrecognized public growth report")
    if len(obj.get("sources",[]))!=3 or any(x.get("url")!=PUBLIC+str(x["issue"]) for x in obj["sources"]):
        raise ValueError("Foreign source URL in growth dashboard")
    return obj


def render(data):
    if data.get("schema")!=SCHEMA:raise ValueError("Unverified dashboard data")
    radar=data["radar"]
    buffer=data["buffer"]
    x=data["x"]
    def value(v):
        return "Non disponibile" if v is None else f"{v:,}".replace(",",".")
    def tile(label,metric,sub,kind=""):
        return ('<article class="gx-kpi" data-metric="'+e(kind)+'">'
                '<span class="gx-label">'+e(label)+'</span><strong>'+e(value(metric))+
                '</strong><small>'+e(sub)+'</small></article>')
    def row(label,key,sub):
        return ('<li class="gx-stage"><div><strong>'+e(label)+'</strong><small>'+
                e(sub)+'</small></div><b>'+e(value(radar[key]))+'</b></li>')
    src="".join(
        '<li><a href="'+e(rec["url"])+'" target="_blank" rel="noopener noreferrer">'
        +'Issue #'+str(rec["issue"])+'</a><span>'+
        e({"verified_public_issue":"Verificata","stale":"Fonte datata",
           "not_fetched":"Non accessibile","invalid":"Formato non verificabile"}.get(rec["status"],"Non verificata"))+
        '</span><small>Ultimo aggiornamento: '+
        e(rec.get("observed_utc") or "non disponibile")+'</small></li>'
        for rec in data["sources"])
    return (
      '<main class="gx-root" id="crescita-x"><div class="gx-hero"><span class="v-kicker">'
      '𝕏 · ANALITICHE TRASPARENTI</span><h1>Crescita GTA VI Italia</h1>'
      '<p>Il nostro monitor pubblico distingue <strong>candidati X</strong>, '
      '<strong>conversazioni verificate</strong> e <strong>metriche davvero misurate</strong>. '
      'Niente follower o impression inventati. Le cifre derivano da report GitHub del bot, '
      'non da accesso privato a X.</p><p class="gx-checked">Controllo dati: <time datetime="'+
      e(data["checked_utc"])+'">'+e(data["checked_utc"])+'</time> · '
      +e({"verified":"3 fonti validate","partial":"Solo alcune fonti validate",
          "unavailable":"Fonti momentaneamente non disponibili"}[data["source_status"]])+
      '</p></div>'
      '<section aria-label="Metriche centrali"><h2>Quello che sappiamo davvero</h2>'
      '<div class="gx-kpis">'+
      tile("Domande X esterne verificate",radar["questions_verified"],
           "Solo tramite embed originale; non tutte le conversazioni di X","verified-questions")+
      tile("Impression Buffer",buffer["impressions"],
           "Solo campione di post inviati, non reach totale di X","impressions")+
      tile("Visite al profilo X",x["profile_visits"],
           "Registrazione manuale del proprietario quando disponibile","visits")+
      tile("Nuovi follower",x["new_followers"],
           "Valore giornaliero manuale, non follower complessivi","followers")+
      '</div></section>'
      '<section class="gx-two"><div class="gx-panel"><h2>Radar X: pipeline di verifica</h2>'
      '<p>Il volume di link non rappresenta persone raggiunte. Soltanto il post '
      'confermato da X oEmbed può essere proposto per una risposta manuale.</p>'
      '<ol class="gx-stages">'+
      row("Articoli di testate controllati","articles_checked","Elenco ristretto di fonti editoriali")+
      row("Permalink X candidati","post_urls_discovered","URL identificati, non post confermati")+
      row("Link temporalmente recenti","recent_links","Età dedotta dall’ID X, ancora non verificati")+
      row("Embed originali consultati","official_oembed_checks","Interrogazioni ufficiali pubbliche senza API a pagamento")+
      row("Domande verificate","questions_verified","Possibili conversazioni da revisionare prima di rispondere")+
      row("Altri post verificati","source_posts_verified","Notizie e opinioni, non richieste di aiuto")+
      '</ol><p><a href="'+PUBLIC+'48" target="_blank" rel="noopener noreferrer">'
      'Apri il radar X con le fonti ↗</a></p></div>'
      '<div class="gx-panel"><h2>Misurazione, senza finzioni</h2>'
      '<dl class="gx-facts"><div><dt>Buffer Insights</dt><dd>'+
      e({"reported_buffer_subset":"Campione numerico disponibile",
         "unavailable":"Statistiche non disponibili",
         "stale":"Lettura oltre 48 ore",
         "not_reported":"Nessun valore attendibile nel report",
         "not_available":"Report non accessibile"}.get(buffer["status"],"Dati assenti"))+
      '</dd></div><div><dt>Data della lettura Buffer</dt><dd>'+
      e(buffer.get("checked_utc") or "Non disponibile")+
      '</dd></div><div><dt>Post nostri nel campione Issue #42</dt><dd>'+
      e(value(radar["owned_posts_in_issue"]))+
      '</dd></div><div><dt>Metriche X manuali</dt><dd>'+
      e(x.get("metrics_date") or "Nessuna rilevazione registrata")+
      '</dd></div><div><dt>Umami</dt><dd>Tracker configurato, ma dati non esportati '
      'a questa pagina</dd></div></dl>'
      '<p>Un clic su «Segui» è soltanto un intento. Un post Buffer «Sent» '
      'non conferma impression, visite o follower. I dati mancanti '
      '<strong>non significano zero</strong>.</p></div></section>'
      '<section class="gx-panel gx-sources"><h2>Fonti controllabili</h2>'
      '<ul>'+src+'</ul><p>Scarica i dati strutturati: '
      '<a href="'+SITE+'growth-evidence-v1.json">report JSON con provenienza</a>. '
      'Sono esclusi password PSN, cronologia personale e cookie di tracciamento.</p>'
      '<p>Per contribuire alla crescita: <a href="https://x.com/xFederiko11" '
      'target="_blank" rel="noopener noreferrer">visita il profilo X</a> '
      'oppure <a href="'+SITE+'mappe-guide/">esplora le mappe GTA VI</a>.</p></section>'
      '</main>'
    )


def to_json(data):
    if data.get("schema")!=SCHEMA:raise ValueError("Unknown X provenance schema")
    return json.dumps(data,indent=2,ensure_ascii=False)+"\n"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--refresh",action="store_true")
    p.add_argument("--output",type=Path,default=REPORT)
    args=p.parse_args()
    data=obtain() if args.refresh else blank()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(to_json(data),encoding="utf-8")
    print("GROWTH_PUBLIC_SOURCE_STATUS",data["source_status"],
          "verified_sources",sum(x["status"]=="verified_public_issue" for x in data["sources"]),
          "no_X_API=true","unknown_is_not_zero=true")


if __name__=="__main__":main()
