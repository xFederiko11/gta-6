"""Isolated, unlisted design experiment; no new media or publication integration."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from urllib.request import Request, urlopen
from urllib.parse import urljoin
import argparse, hashlib, json, time

ROOT = Path("_site")
ROUTE = "anteprima-cloux/"
BASE = "https://xfederiko11.github.io/gta-6/"
MARKER = "cloux-reader-preview-v1"
GUIDE = "guide-e-tutorial/scansionare-veicoli/"
CREDIT = "https://www.rockstargames.com/VI"
SLIDES = [
    ("094c23fcef7629ed2949", "Port Gellhorn · Tramonto"),
    ("bcdd989596461c2c0178", "Vice City · Marina"),
    ("90bb51136148ee7c4c44", "Leonida Keys"),
]

def e(s):
    return escape(str(s), quote=True)

def cover(path):
    return "../assets/social-cards/" + hashlib.sha256(path.encode()).hexdigest()[:16] + ".jpg"

def credit():
    return '<a href="'+CREDIT+'">Rockstar Games · immagine illustrativa</a>'

def card(title, desc, tag, href, image, alt):
    return ('<article class="card"><a class="photo" href="'+e(href)+'"><img src="'+e(image)+
            '" alt="'+e(alt)+'" width="1200" height="630" loading="lazy"><span class="tag">'+e(tag)+
            '</span></a><div class="credit">'+credit()+'</div><div class="cardbody"><h3>'+
            e(title)+'</h3><p>'+e(desc)+'</p><a class="read" href="'+e(href)+'">Apri →</a></div></article>')

def slide_markup():
    return "".join('<img class="slide'+(' active' if i==0 else '')+
        '" src="../assets/cinematic/'+key+'-1600.webp" srcset="../assets/cinematic/'+key+
        '-960.webp 960w, ../assets/cinematic/'+key+'-1600.webp 1600w" sizes="100vw" width="1600" height="900" alt="'+
        e(label+' · immagine ufficiale Rockstar Games')+'" data-label="'+e(label)+'"'+
        (' fetchpriority="high"' if i==0 else ' loading="lazy"')+'>' for i,(key,label) in enumerate(SLIDES))

def build(root=ROOT):
    data=json.loads(Path("data/guide.json").read_text(encoding="utf-8"))
    rows=data if isinstance(data,list) else data["guides"]
    g=next(x for x in rows if x["id"]=="scansionare-veicoli")
    titles=["Apri WAiNK","Inquadra il veicolo","Tieni premuto R1","Controlla il tracker","Controlla i progressi"]
    assert len(g["steps"])==len(g["checks"])==len(titles)==5
    steps="".join(
        '<section class="step" id="passaggio-'+str(i)+'"><div class="num">'+str(i).zfill(2)+
        '</div><div class="stepbody"><h3>'+e(title)+'</h3><p>'+e(instruction)+
        '</p><figure><img src="../assets/waink-guide/step-'+str(i)+'.svg" width="640" height="220" alt="'+
        e("Schema originale: "+title)+'" loading="lazy"><figcaption>Schema originale GTA VI Italia · non screenshot · <a href="'+
        e(g["source_url"])+'">Fonte</a></figcaption></figure><label class="checkrow"><input type="checkbox" class="check"><span>'+
        e(check)+'</span></label></div></section>'
        for i,(title,instruction,check) in enumerate(zip(titles,g["steps"],g["checks"]),1))
    cards="".join([
        card("Come salvare un'auto personale","Dal recupero alla registrazione: segui tutti i passaggi.","Veicoli","../salvare-auto/",cover("salvare-auto/"),"Auto in officina Rideout Customs"),
        card("WAiNK: scansionare i veicoli","Cinque passaggi per usare lo scanner e leggere i tracker.","Tutorial","#guide",cover(GUIDE),"Jason accanto a una motocicletta"),
        card("Tutti i trofei di GTA VI","Schede e percorsi per il completamento.","Platino","../trofei/","../assets/cinematic/f2881a37f088521a58e0-960.webp","Jason e Lucia, immagine promozionale"),
    ])
    categories="".join('<a href="../'+path+'"><span aria-hidden="true">'+icon+'</span>'+name+'</a>' for name,path,icon in [
        ("Guide","guide-e-tutorial/","▤"),("Platino","trofei/","◇"),("Veicoli","veicoli/","▰"),
        ("Mappe","mappe-guide/","⌖"),("Collezionabili","collezionabili/percorsi/","✦"),("HDR OLED","hdr-oled/","▣")])
    news="".join([
        card("GTA VI oltre Vice City: Leonida in sei immagini ufficiali","Un viaggio fotografico tra le ambientazioni.","Approfondimento","../articoli/gta-vi-leonida-sei-luoghi/",cover("articoli/gta-vi-leonida-sei-luoghi/"),"Vice City, fotografia promozionale"),
        card("Ultimate Edition: auto e garage in quattro immagini","Scopri l'articolo illustrato dedicato ai veicoli.","Approfondimento","../articoli/gta-vi-ultimate-edition-auto-garage/",cover("articoli/gta-vi-ultimate-edition-auto-garage/"),"Auto e garage, materiale Ultimate Edition"),
    ])
    sources=[g["source_url"],*g.get("extra_sources",[])]
    source_links="".join('<li><a href="'+e(s)+'">'+e(s.split("/")[2])+' · '+e(s.rstrip("/").split("/")[-1].replace("-"," "))+'</a></li>' for s in sources)
    html=HTML.replace("@SLIDES@",slide_markup()).replace("@CATEGORIES@",categories).replace("@CARDS@",cards).replace("@NEWS@",news).replace("@COVER@",cover(GUIDE)).replace("@SUMMARY@",e(g["summary"])).replace("@STEPS@",steps).replace("@BENEFIT@",e(g["benefit"])).replace("@CAUTION@",e(g["caution"])).replace("@SOURCES@",source_links)
    from sunset_blog_v1 import preview
    html=preview(html)
    protected=[root/"index.html",root/"sitemap.xml",root/"articoli/feed.json"]
    before=[p.read_bytes() for p in protected]
    out=root/ROUTE/"index.html"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(html,encoding="utf-8")
    assert before==[p.read_bytes() for p in protected]
    verify(root)
    print("CLOUX_PREVIEW_BUILD_OK",out)

class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images=set()
        self.links=set()
        self.robots=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="img":
            self.images.add(a["src"])
            self.images.update(x.strip().split()[0] for x in a.get("srcset","").split(",") if x.strip())
        if tag=="a":
            self.links.add(a.get("href",""))
        if tag=="meta" and a.get("name")=="robots":
            self.robots.append(a["content"])

def inspect(html):
    p=Assets()
    p.feed(html)
    assert p.robots==["noindex,nofollow"]
    assert MARKER in html and html.count('class="check"')==5
    assert "growth-analytics-v1" not in html and "<iframe" not in html
    assert all(x.startswith("../assets/") for x in p.images)
    assert not any("@" + t + "@" in html for t in ("SLIDES","CARDS","STEPS","NEWS"))
    return p

def verify(root=ROOT):
    from PIL import Image
    html=(root/ROUTE/"index.html").read_text(encoding="utf-8")
    p=inspect(html)
    assert ROUTE not in (root/"sitemap.xml").read_text(encoding="utf-8")
    assert ROUTE not in (root/"articoli/feed.json").read_text(encoding="utf-8")
    assert ROUTE not in (root/"index.html").read_text(encoding="utf-8")
    for src in p.images:
        path=(root/ROUTE/src).resolve()
        assert path.is_relative_to((root/"assets").resolve()) and path.is_file(), src
        if path.suffix!=".svg":
            with Image.open(path) as im:
                im.verify()
    for link in p.links:
        if link.startswith("../") or link=="../":
            path=(root/ROUTE/link).resolve()
            assert path.is_relative_to(root.resolve()) and (path/"index.html").is_file(),link
    print("CLOUX_PREVIEW_STATIC_OK",len(p.images),"existing assets")

def browser(root=ROOT):
    from playwright.sync_api import sync_playwright
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(root)))
    Thread(target=server.serve_forever,daemon=True).start()
    address="http://127.0.0.1:"+str(server.server_port)+"/"+ROUTE
    screenshots=Path("reader-qa")
    screenshots.mkdir(exist_ok=True)
    try:
        with sync_playwright() as pw:
            b=pw.chromium.launch()
            for width in (390,1440):
                page=b.new_page(viewport={"width":width,"height":844 if width==390 else 1000},reduced_motion="reduce")
                errors=[]
                page.on("pageerror",lambda err:errors.append(str(err)))
                assert page.goto(address).status==200
                page.locator("#home .slide.active").evaluate("(img)=>img.decode()")
                assert page.locator("#count").inner_text()=="1 / 3"
                page.locator("#next").click()
                page.locator("#home .slide.active").evaluate("(img)=>img.decode()")
                assert page.locator("#count").inner_text()=="2 / 3"
                page.locator("#prev").click()
                assert page.locator("#count").inner_text()=="1 / 3"
                page.locator("#theme").click()
                assert page.locator("html").get_attribute("data-theme")=="light"
                page.locator("#theme").click()
                assert page.locator("html").get_attribute("data-theme")=="dark"
                page.locator("#home img").evaluate_all("(imgs)=>Promise.all(imgs.map(i=>{i.loading='eager';return i.decode()}))")
                assert page.evaluate("document.documentElement.scrollWidth===innerWidth")
                page.screenshot(path=str(screenshots/("cloux-home-"+str(width)+".png")),full_page=True)
                page.locator("#guide-tab").click()
                assert page.locator("#guide").is_visible() and page.locator("#guide .step").count()==5
                page.locator("#guide img").evaluate_all("(imgs)=>Promise.all(imgs.map(i=>{i.loading='eager';return i.decode()}))")
                page.locator(".check").first.check()
                assert page.locator("#progress").inner_text()=="1 / 5 completati"
                page.reload()
                assert page.locator("#progress").inner_text()=="1 / 5 completati"
                assert page.evaluate("document.documentElement.scrollWidth===innerWidth")
                page.screenshot(path=str(screenshots/("cloux-guide-"+str(width)+".png")),full_page=True)
                assert not errors,errors
                page.close()
            b.close()
    finally:
        server.shutdown()
        server.server_close()
    print("CLOUX_PREVIEW_BROWSER_OK 390 1440; image decoding, navigation, theme, progress, overflow")

def live():
    def fetch(url):
        req=Request(url,headers={"User-Agent":"GTA6Italia-PreviewQA/1.0","Cache-Control":"no-cache"})
        with urlopen(req,timeout=12) as res:
            assert res.status==200
            return res.read(4000000),res.headers.get_content_type()
    for attempt in range(4):
        try:
            raw,mime=fetch(BASE+ROUTE)
            assert mime=="text/html"
            p=inspect(raw.decode())
            for src in sorted(p.images):
                binary,mime=fetch(urljoin(BASE+ROUTE,src))
                assert mime.startswith("image/") and len(binary)>100,src
            for path in ("sitemap.xml","articoli/feed.json"):
                assert ROUTE.encode() not in fetch(BASE+path)[0]
            print("PUBLIC_CLOUX_PREVIEW_OK",BASE+ROUTE,len(p.images),"image responses")
            return
        except Exception:
            if attempt==3: raise
            time.sleep(4*(attempt+1))

HTML = r'''<!doctype html>
<html lang="it" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#101018"><title>GTA VI Italia — Anteprima grafica</title>
<style>
:root{color-scheme:dark;--bg:#101018;--panel:#191922;--ink:#f7f5fa;--muted:#b7b4c6;--line:#34313e;--pink:#ff8bb9;--header:#11111a}html[data-theme=light]{color-scheme:light;--bg:#f5f2f5;--panel:#fff;--ink:#231e2c;--muted:#61596e;--line:#ded8e1;--pink:#a32d65;--header:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit;text-decoration:none}button,input{font:inherit}button{cursor:pointer}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid var(--pink);outline-offset:3px}[hidden]{display:none!important}.wrap{max-width:1220px;margin:auto;padding:0 26px}.preview{background:var(--panel);border-bottom:1px solid var(--line);font-size:12px;color:var(--muted)}.preview .wrap{display:flex;align-items:center;justify-content:space-between;gap:10px;min-height:40px}.tabs{display:flex;gap:4px}.tabs button,.tool{border:1px solid var(--line);background:transparent;color:var(--ink);padding:8px 12px;border-radius:4px}.tabs button[aria-selected=true]{background:var(--line);font-weight:700}.header{background:var(--header);border-bottom:1px solid var(--line)}.nav{display:flex;align-items:center;justify-content:space-between;min-height:78px;gap:22px}.brand{font-size:26px;font-weight:950;letter-spacing:-.065em;white-space:nowrap;line-height:1}.brand b,h2 b{color:var(--pink)}.brand small{display:block;color:var(--muted);font-size:10px;letter-spacing:.22em;font-weight:700;margin-top:8px}.navlinks{display:flex;gap:20px;align-items:center;font-size:13px;font-weight:750;text-transform:uppercase}.navtools{display:flex;gap:8px}.tool{min-width:42px;min-height:42px}.menu{display:none}.hero{position:relative;isolation:isolate;min-height:520px;display:flex;align-items:center;overflow:hidden;background:#171724;color:white}.slide{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:60% center;opacity:0;transition:opacity .4s ease;z-index:-2}.slide.active{opacity:1}.hero:after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(90deg,rgba(9,9,18,.86),rgba(9,9,18,.53) 43%,rgba(9,9,18,.08) 80%),linear-gradient(0deg,rgba(9,9,18,.75),transparent 24%)}.hero .wrap{width:100%;padding-top:24px;padding-bottom:86px}.eyebrow{color:var(--pink);text-transform:uppercase;letter-spacing:.14em;font-size:12px;font-weight:800}.eyebrow:before{content:"";display:inline-block;width:23px;height:2px;vertical-align:middle;background:currentColor;margin-right:9px}.hero .eyebrow,.hero h1 em{color:#ff9ac6}.hero h1{font-size:clamp(43px,6vw,86px);line-height:.98;text-transform:uppercase;font-weight:950;letter-spacing:-.06em;margin:20px 0}.hero h1 em{font-style:normal}.hero p{max-width:530px;margin:0 0 24px;color:#f1edf5;font-size:17px}.actions{display:flex;gap:10px;flex-wrap:wrap}.primary,.secondary{display:inline-flex;align-items:center;padding:12px 17px;border-radius:3px;font-size:12px;font-weight:850;letter-spacing:.08em;text-transform:uppercase;border:1px solid #ff9ac6}.primary{background:#ff9ac6;color:#17111e}.secondary{border-color:#fff;color:#fff;background:#19152466}.hero-controls{position:absolute;bottom:18px;left:max(26px,calc((100% - 1168px)/2));display:flex;align-items:center;gap:8px;font-size:13px}.hero-controls button{width:40px;height:40px;border:1px solid #ffffff9c;border-radius:4px;background:#14121d99;color:white}.hero-credit{position:absolute;bottom:20px;right:max(26px,calc((100% - 1168px)/2));text-align:right;font-size:11px;color:#f0eaf4}.hero-credit a{text-decoration:underline}.categories{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));background:var(--panel)}.category-strip{background:var(--panel);border-bottom:1px solid var(--line)}.categories a{display:grid;place-items:center;align-content:center;gap:8px;padding:23px 6px;border-right:1px solid var(--line);text-transform:uppercase;font-weight:800;font-size:12px;letter-spacing:.06em;text-align:center;min-width:0}.categories a:last-child{border-right:0}.categories span{font-size:24px;color:var(--pink);line-height:1}.section{padding:48px 0 12px}.sectionhead{display:flex;align-items:flex-end;justify-content:space-between;gap:15px;margin-bottom:20px}h2{font-size:clamp(25px,3.1vw,38px);line-height:1.1;letter-spacing:-.04em;margin:8px 0 0;font-weight:900;text-transform:uppercase}.sectionhead>a,.read{color:var(--pink);font-weight:750;font-size:13px}.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.newsgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}.card{background:var(--panel);border:1px solid var(--line);min-width:0}.photo{display:block;position:relative;aspect-ratio:1200/630;overflow:hidden;background:var(--line)}.photo img{width:100%;height:100%;object-fit:cover;display:block}.tag{position:absolute;left:12px;bottom:12px;background:#17111e;color:#ff9ac6;border:1px solid #ff9ac6;padding:4px 7px;font-size:10px;text-transform:uppercase;font-weight:800;letter-spacing:.08em}.credit,figcaption{font-size:11px;color:var(--muted);padding:7px 14px}.credit a,figcaption a{text-decoration:underline}.cardbody{padding:9px 16px 18px}.cardbody h3{margin:0;font-size:20px;line-height:1.2;letter-spacing:-.02em}.cardbody p{font-size:14px;color:var(--muted);margin:8px 0 13px}.article{max-width:880px;margin:auto;padding:30px 26px 45px}.crumb{font-size:12px;color:var(--muted);margin:0 0 20px}.article h1{font-size:clamp(32px,4vw,56px);line-height:1.04;letter-spacing:-.05em;margin:12px 0 20px;font-weight:900}.article figure{margin:0}.cover{display:block;width:100%;height:auto;border:1px solid var(--line)}.intro,.aside,.sources{margin-top:22px;padding:18px;background:var(--panel);border-left:3px solid var(--pink)}.intro h2,.aside h2,.sources h2,.stepshead h2{font-size:24px;margin:0 0 12px}.intro p,.aside p{margin:0 0 12px}.facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:15px}.facts div{display:grid;gap:5px;border:1px solid var(--line);padding:10px;font-size:13px}.facts b{font-size:10px;color:var(--pink);letter-spacing:.08em}.video{display:block;background:var(--panel);padding:14px;margin:16px 0;border:1px solid var(--line);font-weight:750;color:var(--pink)}.stepshead{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:26px}.progress{font-size:12px;color:var(--muted);white-space:nowrap}.track{height:6px;background:var(--line);margin:0 0 18px}.track span{height:100%;display:block;background:var(--pink);width:0;transition:width .2s}.step{display:grid;grid-template-columns:50px minmax(0,1fr);gap:14px;padding:18px;margin:12px 0;border:1px solid var(--line);background:var(--panel)}.num{color:var(--pink);font-size:28px;font-weight:900;line-height:1}.step h3{margin:0;font-size:22px;line-height:1.2}.step p{margin:8px 0 12px}.step img{display:block;width:100%;height:auto;border:1px solid var(--line)}.step figcaption{padding:7px 0}.checkrow{display:flex;gap:10px;align-items:flex-start;border-top:1px solid var(--line);padding-top:12px;font-size:14px;color:var(--muted)}.checkrow input{width:21px;height:21px;flex:none;accent-color:var(--pink);margin:0}.sources a{color:var(--pink);text-decoration:underline;overflow-wrap:anywhere}.sources ul{padding-left:18px}.notice{font-size:12px;color:var(--muted)}footer{margin-top:40px;border-top:1px solid var(--line);padding:22px 0;color:var(--muted);font-size:12px}footer a{color:var(--pink)}
@media(max-width:720px){.wrap{padding:0 16px}.preview .wrap{min-height:36px}.preview strong{font-size:10px}.tabs button{padding:5px 7px;font-size:11px}.nav{min-height:65px;gap:8px;flex-wrap:wrap}.brand{font-size:23px}.brand small{font-size:9px}.navlinks{display:none;order:3;width:100%;padding:0 0 12px;flex-wrap:wrap;gap:12px}.navlinks.open{display:flex}.menu{display:inline-block}.hero{min-height:415px;align-items:flex-end}.hero .wrap{padding:65px 16px 73px}.hero:after{background:linear-gradient(0deg,rgba(9,9,18,.95),rgba(9,9,18,.51) 67%,rgba(9,9,18,.05))}.slide{object-position:59% center}.hero h1{font-size:clamp(40px,12vw,57px);margin:13px 0}.hero .eyebrow{font-size:10px}.hero p{font-size:14px;line-height:1.45;margin-bottom:18px}.actions{gap:7px}.primary,.secondary{font-size:10px;padding:10px 12px;letter-spacing:.04em}.hero-controls{left:16px;bottom:13px;gap:5px}.hero-controls button{width:34px;height:34px}.hero-credit{right:16px;bottom:14px;max-width:155px;font-size:9px}.categories{grid-template-columns:repeat(3,minmax(0,1fr))}.categories a{padding:13px 2px;font-size:10px;letter-spacing:.02em;border-bottom:1px solid var(--line)}.categories a:nth-child(3n){border-right:0}.categories span{font-size:20px}.section{padding:27px 0 8px}.sectionhead{align-items:flex-start;flex-direction:column;gap:8px;margin-bottom:14px}.cards,.newsgrid{grid-template-columns:1fr;gap:13px}.cardbody h3{font-size:19px}.article{padding:20px 16px 30px}.facts div{padding:7px;font-size:11px}.facts b{font-size:9px}.step{grid-template-columns:33px minmax(0,1fr);padding:12px;gap:8px}.num{font-size:24px}.step h3{font-size:18px}.step p{font-size:15px}.intro,.aside,.sources{padding:13px}.stepshead h2{font-size:21px}.progress{font-size:11px}footer{margin-top:22px}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{transition:none!important;scroll-behavior:auto!important}}
</style></head><body data-preview="cloux-reader-preview-v1">
<div class="preview"><div class="wrap"><strong>ANTEPRIMA GRAFICA · NON DEFINITIVA</strong><div class="tabs" role="tablist" aria-label="Pagine demo"><button id="home-tab" role="tab" aria-controls="home" aria-selected="true">Homepage</button><button id="guide-tab" role="tab" aria-controls="guide" aria-selected="false">Tutorial</button></div></div></div>
<header class="header"><div class="wrap nav"><a class="brand" href="#home">GTA <b>VI</b> ITALIA<small>GUIDE · NEWS · PLATINO</small></a><nav class="navlinks" id="navlinks" aria-label="Navigazione"><a href="../guide-e-tutorial/">Guide</a><a href="../trofei/">Platino</a><a href="../veicoli/">Veicoli</a><a href="../articoli/">News</a><a href="https://x.com/xFederiko11">X</a></nav><div class="navtools"><button class="tool" id="theme" aria-label="Passa al tema chiaro">☼</button><button class="tool menu" id="menu" aria-controls="navlinks" aria-expanded="false" aria-label="Menu">☰</button></div></div></header>
<main id="home" role="tabpanel" aria-labelledby="home-tab"><section class="hero" aria-label="Fotografie promozionali di Leonida">@SLIDES@<div class="wrap"><div class="eyebrow">La tua guida a Leonida · PS5 / PS5 Pro</div><h1>Esplora.<br>Gioca. <em>Completa.</em></h1><p>Guide passo per passo, trofei, veicoli e novità di GTA VI. Tutto quello che ti serve, in italiano.</p><div class="actions"><a class="primary" href="../guide-e-tutorial/">Trova una guida →</a><a class="secondary" href="../trofei/">Verso il platino</a></div></div><div class="hero-controls"><button id="prev" aria-label="Foto precedente">←</button><span id="count">1 / 3</span><button id="next" aria-label="Foto successiva">→</button><button id="pause" aria-label="Metti in pausa">Ⅱ</button></div><div class="hero-credit"><a href="https://www.rockstargames.com/VI">Immagine illustrativa · Rockstar Games</a><br><span id="caption">Port Gellhorn · Tramonto</span></div></section>
<div class="category-strip"><div class="wrap categories">@CATEGORIES@</div></div><div class="wrap"><section class="section"><div class="sectionhead"><div><div class="eyebrow">Vai dritto al punto</div><h2>Guide <b>in evidenza</b></h2></div><a href="../guide-e-tutorial/">Tutte le guide →</a></div><div class="cards">@CARDS@</div></section><section class="section"><div class="sectionhead"><div><div class="eyebrow">Redazione GTA VI Italia</div><h2>Notizie &amp; <b>approfondimenti</b></h2></div><a href="../articoli/">Tutti gli articoli →</a></div><div class="newsgrid">@NEWS@</div></section></div></main>
<main id="guide" role="tabpanel" aria-labelledby="guide-tab" hidden><article class="article"><p class="crumb"><a href="#home">Home</a> › Guide › WAiNK</p><div class="eyebrow">Tutorial · PS5 / PS5 Pro</div><h1>WAiNK: come scansionare i veicoli</h1><figure><img class="cover" src="@COVER@" alt="Jason accanto a una motocicletta verde, materiale promozionale Rockstar" width="1200" height="630"><figcaption>Immagine illustrativa, non prova della procedura · <a href="https://www.rockstargames.com/VI">Rockstar Games</a>. Stessa copertina della guida pubblica.</figcaption></figure><section class="intro"><h2>Cosa fare</h2><p>@SUMMARY@</p><div class="facts"><div><b>OBIETTIVO</b>200 modelli base</div><div><b>COMANDI</b>↑ e R1</div><div><b>PROCEDURA</b>5 passaggi</div></div></section><a class="video" href="https://www.youtube.com/watch?v=0RBe_fz67gs">▶ Video tutorial WAiNK · Games &amp; Apps Tutorials ↗</a><div class="stepshead"><h2>Passo per passo</h2><span class="progress" id="progress">0 / 5 completati</span></div><div class="track" role="progressbar" aria-label="Passaggi completati" aria-valuemin="0" aria-valuemax="5" aria-valuenow="0"><span></span></div>@STEPS@<aside class="aside"><h2>Risultato</h2><p>@BENEFIT@</p></aside><aside class="aside"><h2>Attenzione ai tracker</h2><p>@CAUTION@</p></aside><section class="sources"><h2>Fonti e guida completa</h2><ul>@SOURCES@</ul><p><a href="https://allthings.how/gta-6-waink-app-explained-how-to-open-scan-locations/">Vedi le schermate reali dello scanner ↗</a></p><a href="../guide-e-tutorial/scansionare-veicoli/">Vai alla guida originale →</a></section><p class="notice">Prova grafica separata. La checklist non modifica il progresso della guida pubblica.</p></article></main>
<footer><div class="wrap">GTA VI Italia · Demo indipendente, non affiliata a Rockstar Games. <a href="../">Torna al sito attuale →</a></div></footer>
<script>
(()=>{const $=s=>document.querySelector(s),all=s=>Array.from(document.querySelectorAll(s)),pages=["home","guide"];let page="home";
const storage={get:k=>{try{return localStorage.getItem(k)}catch{return null}},set:(k,v)=>{try{localStorage.setItem(k,v)}catch{}}};
function show(){const p=location.hash.slice(1);page=pages.includes(p)?p:"home";for(const id of pages){$("#"+id).hidden=id!==page;$("#"+id+"-tab").setAttribute("aria-selected",String(id===page))}window.scrollTo(0,0)}
for(const id of pages)$("#"+id+"-tab").onclick=()=>{location.hash=id;show()};addEventListener("hashchange",show);show();
const menu=$("#menu");menu.onclick=()=>menu.setAttribute("aria-expanded",String($("#navlinks").classList.toggle("open")));
const theme=$("#theme");function setTheme(t){document.documentElement.dataset.theme=t;theme.textContent=t==="dark"?"☼":"☾";theme.setAttribute("aria-label",t==="dark"?"Passa al tema chiaro":"Passa al tema scuro");storage.set("cloux-preview-theme",t)}setTheme(storage.get("cloux-preview-theme")==="light"?"light":"dark");theme.onclick=()=>setTheme(document.documentElement.dataset.theme==="dark"?"light":"dark");
const slides=all(".slide");let index=0,paused=matchMedia("(prefers-reduced-motion: reduce)").matches;
function slide(delta){index=(index+delta+slides.length)%slides.length;slides.forEach((s,i)=>s.classList.toggle("active",i===index));$("#count").textContent=(index+1)+" / "+slides.length;$("#caption").textContent=slides[index].dataset.label}
$("#prev").onclick=()=>slide(-1);$("#next").onclick=()=>slide(1);const pause=$("#pause");function pauseState(){pause.textContent=paused?"▶":"Ⅱ";pause.setAttribute("aria-label",paused?"Avvia slideshow":"Metti in pausa")}pauseState();pause.onclick=()=>{paused=!paused;pauseState()};setInterval(()=>{if(!paused&&!document.hidden&&page==="home")slide(1)},1750);
const checks=all(".check");let saved=[];try{saved=JSON.parse(storage.get("cloux-preview-checks")||"[]")}catch{}if(!Array.isArray(saved))saved=[];checks.forEach((c,i)=>c.checked=saved[i]===true);
function update(){const n=checks.filter(c=>c.checked).length;$("#progress").textContent=n+" / 5 completati";$(".track").setAttribute("aria-valuenow",n);$(".track span").style.width=(n*20)+"%";storage.set("cloux-preview-checks",JSON.stringify(checks.map(c=>c.checked)))}checks.forEach(c=>c.addEventListener("change",update));update();
})();
</script></body></html>'''

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("build","verify","browser","live"))
    args=parser.parse_args()
    {"build":build,"verify":verify,"browser":browser,"live":live}[args.mode]()
