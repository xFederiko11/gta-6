"""Sunset editorial layer: bright shared tokens, readable blog sidebar, no new media.

Run after canonical pages, social covers and editorial feed. The only content
changes are navigation and the opt-in X panel; canonical article bytes remain.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
import argparse, hashlib, json, re, shutil, time
from community_social_v1 import load, verified_x_url, post_time_html

ROOT=Path("_site")
BASE="https://xfederiko11.github.io/gta-6/"
CSS="sunset-blog-v1.css"
VERSION="sunset-blog-v1"
GUIDE_MARKER='id="procedura" class="v-tutorial"'
MAIN='<main class="wrap" id="contenuto">'
HOME_START='<section class="ci-section ci-shell" id="scegli">'
CATEGORIES=[
 ("guide-e-tutorial/","Guide e missioni","pink"),
 ("soldi-facili/","Soldi facili","orange"),
 ("trofei/","Trofei e platino","violet"),
 ("veicoli/","Veicoli e garage","cyan"),
 ("collezionabili/percorsi/","Collezionabili","pink"),
 ("mappe-guide/","Mappe e luoghi","cyan"),
 ("trucchi/","Trucchi PS5","orange"),
 ("hdr-oled/","HDR OLED","violet"),
 ("articoli/","News e articoli","pink"),
 ("patch/","Patch e aggiornamenti","cyan"),
 ("video-tutorial/","Video tutorial","orange"),
 ("scoperte/","Scoperte community","violet"),
]
IMPORTANT=[
 ("salvare-auto/","Come salvare e registrare le auto"),
 ("trofei/roadmap-platino/","Roadmap verso il platino"),
 ("trofei/100-percento/","Checklist 100%"),
 ("guide-e-tutorial/scansionare-veicoli/","Usare WAiNK"),
 ("guide-e-tutorial/soldi-facili-capitolo-1/","Soldi nel Capitolo 1"),
]
HUBS={"guide-e-tutorial/","soldi-facili/","auto-speciali/","articoli/","patch/","scoperte/"}
EXAMPLE="guide-e-tutorial/soldi-2500-three-sheets-liquor/"

def esc(value):
    return escape(str(value),quote=True)

def tracking(enabled,event,destination="",placement="right-sidebar"):
    """Only existing owner-configured Umami; fixed editorial labels, no IDs."""
    if not enabled:
        return ""
    return (' data-umami-event="'+esc(event)+'" data-umami-event-placement="'+esc(placement)+'"'+
            (' data-umami-event-destination="'+esc(destination)+'"' if destination else ""))

def related(path):
    if path.startswith(("soldi-facili/","guide-e-tutorial/soldi-")):
        choices=[
            ("guide-e-tutorial/soldi-facili-capitolo-1/","Dove trovare soldi nel Capitolo 1"),
            (EXAMPLE,"Three Sheets Liquor: fino a circa 2.500 GTA$"),
            ("soldi-facili/","Tutte le guide per guadagnare"),
        ]
    elif path=="salvare-auto/" or path.startswith(("veicoli/","auto-speciali/")) or any(x in path for x in ("scansionare-veicoli","veicoli-per-moses","sportive-randy")):
        choices=[
            ("salvare-auto/","Come salvare e registrare le auto"),
            ("guide-e-tutorial/scansionare-veicoli/","Come scansionare un'auto con WAiNK"),
            ("guide-e-tutorial/veicoli-per-moses/","Dove trovare i veicoli per Moses"),
            ("veicoli/","Catalogo dei veicoli"),
        ]
    else:
        choices=[]
    return [(target,label) for target,label in choices if target!=path][:3]

def related_links(path,enabled):
    items=related(path)
    if not items:
        return ""
    return ('<nav class="sb-related" aria-label="Guide correlate"><p class="sb-heading">Continua con queste guide</p>'+
            "".join('<a href="'+BASE+target+'"'+tracking(enabled,"related-guide-open",target,"after-tutorial")+'>'+esc(label)+' <span aria-hidden="true">→</span></a>' for target,label in items)+'</nav>')

def sidebar(path="",*,preview=False,guide=False,track=False):
    def row(target,label,color):
        active=(path==target or (not preview and target!="guide-e-tutorial/" and path.startswith(target)))
        return ('<a class="sb-category" data-color="'+color+'" href="'+BASE+target+'"'+
                (' aria-current="page"' if active and path==target else '')+
                (' data-current-section="true"' if active else '')+tracking(track,"category-open",target)+'><span aria-hidden="true"></span>'+esc(label)+'</a>')
    categories="".join(row(*entry) for entry in CATEGORIES)
    important="".join('<a href="'+BASE+target+'"'+tracking(track,"important-guide-open",target)+'>'+esc(label)+' <span aria-hidden="true">→</span></a>' for target,label in IMPORTANT if target!=path)
    jump=('<div class="sb-panel"><p class="sb-kicker">IN QUESTA GUIDA</p><nav class="sb-important" aria-label="Indice della guida">'
          '<a href="#procedura"'+tracking(track,"tutorial-jump","procedura")+'>Passaggi del tutorial <span aria-hidden="true">↓</span></a>'
          '<a href="#approfondimenti"'+tracking(track,"tutorial-jump","approfondimenti")+'>Approfondimenti e fonti <span aria-hidden="true">↓</span></a></nav></div>') if guide else ""
    cards=[]
    for item in load().get("x_posts",[]):
        if item.get("buffer_status")!="sent":
            continue
        url=verified_x_url(item.get("x_url"))
        text=str(item.get("text") or "").strip()
        stamp=post_time_html(item)
        if not url or not text or not stamp:
            continue
        cards.append('<article class="social-comment-card"><span>𝕏 @xFederiko11</span>'+stamp+'<p>'+
                     esc(text[:210])+'</p><a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer"'+tracking(track,"x-post-open")+'>Apri il post ↗</a></article>')
        if len(cards)==3:break
    posts="".join(cards) or '<p class="sb-empty">Se gli estratti non sono disponibili, apri direttamente il profilo X.</p>'
    return ('<aside class="sb-sidebar" aria-label="Categorie e aggiornamenti GTA VI Italia">'+jump+
            '<div class="sb-panel"><p class="sb-kicker">ESPLORA LEONIDA</p><p class="sb-heading">Categorie</p>'
            '<nav class="sb-categories" aria-label="Categorie del sito">'+categories+'</nav></div>'
            '<div class="sb-panel"><p class="sb-kicker">NON PERDERTELI</p><p class="sb-heading">Da tenere a portata di mano</p>'
            '<nav class="sb-important" aria-label="Guide importanti">'+important+'</nav></div>'
            '<div class="sb-panel sb-x-panel"><p class="sb-kicker">DALLA REDAZIONE</p><p class="sb-heading">𝕏 Ultimi post</p>'
            '<p class="sb-x-description">Post verificati tramite Buffer · orario italiano.</p>'
            '<div class="sb-x-grid" data-x-live-grid>'+posts+'</div>'
            '<button class="sb-x-button" type="button" data-x-timeline-load'+tracking(track,"x-timeline-open")+'>Carica il feed X</button>'
            '<p class="sb-x-description">Il feed incorporato è facoltativo e può non essere disponibile. Si collega a X soltanto al clic.</p>'
            '<div data-x-timeline-slot aria-live="polite"></div>'
            '<a class="sb-profile" href="https://x.com/xFederiko11" target="_blank" rel="noopener noreferrer"'+tracking(track,"x-profile-open")+'>Apri @xFederiko11 su X ↗</a></div></aside>')

def wrap(inner,path="",*,home=False,preview=False,track=False):
    # The article stays first in source order: screen readers, mobile and
    # keyboard users get the numbered actions before optional navigation.
    guide=GUIDE_MARKER in inner
    if guide:
        marker='<div class="v-guide-layout v-guide-single">'
        assert inner.count(marker)==1,path
        jump=('<nav class="sb-quick-jump" aria-label="Vai direttamente al tutorial">'
              '<a href="#procedura"'+tracking(track,"tutorial-jump","procedura","guide-intro")+'>Vai ai passaggi ↓</a>'
              '<a href="'+BASE+'guide-e-tutorial/"'+tracking(track,"category-open","guide-e-tutorial/","guide-intro")+'>Tutte le guide</a></nav>')
        inner=inner.replace(marker,jump+marker,1)
        # Contextual next-guide links appear immediately after the procedure,
        # not between numbered steps or inside a closed extra panel.
        extra='<details class="v-guide-more" id="approfondimenti">'
        assert inner.count(extra)==1,path
        inner=inner.replace(extra,related_links(path,track)+extra,1)
    return ('<div class="sunset-blog'+(' sunset-home' if home else '')+'" data-sunset-layout="right-blog">'
            '<div class="sunset-content">'+inner+'</div>'+sidebar(path,preview=preview,guide=guide,track=track)+'</div>')

def eligible(path,page):
    return GUIDE_MARKER in page or path in HUBS or path.startswith(("articoli/","patch/","garage-gratuiti/"))

def inject(page,path,digest):
    if 'data-design-version=' not in page or 'name="sunset-blog-version"' in page:
        return page
    page=page.replace('</head>','<meta name="sunset-blog-version" content="'+VERSION+
                      '"><link rel="stylesheet" href="'+BASE+'assets/'+CSS+'?v='+digest+'"></head>',1)
    track='id="growth-analytics-v1"' in page
    if path=="":
        start=page.index(HOME_START)
        stop=page.rindex('</div>',start,page.index('</main>',start))
        # Preserve the full-width photographic hero and ticker unchanged.
        return page[:start]+wrap(page[start:stop],path,home=True,track=track)+page[stop:]
    if eligible(path,page):
        start=page.index(MAIN)+len(MAIN)
        stop=page.index("</main>",start)
        return page[:start]+wrap(page[start:stop],path,track=track)+page[stop:]
    return page

def preview(page):
    # Demo inherits the same colors and sidebar, with separate checklist state.
    page=page.replace("</head>",'<link rel="stylesheet" href="../assets/'+CSS+'"></head>',1)
    start=page.index('<div class="wrap"><section class="section">')
    stop=page.index("</main>",start)
    original=page[start:stop]
    # Strip the demo's old inner wrap only; the new layout supplies it.
    assert original.startswith('<div class="wrap">') and original.endswith('</div>')
    page=page[:start]+wrap(original[len('<div class="wrap">'):-len('</div>')],home=True,preview=True)+page[stop:]
    start=page.index('<article class="article">')
    stop=page.index("</main>",start)
    page=page[:start]+wrap(page[start:stop],preview=True)+page[stop:]
    page=page.replace("</body>",'<script src="../assets/community-social-v1.js" defer></script></body>',1)
    return page

def contracts(page):
    """Check canonical, metadata, exact cover and step content before/after."""
    result=[]
    for expression in (
        r'<link rel="canonical" href="[^"]+">',
        r'<meta property="og:image" content="[^"]+">',
        r'<meta name="twitter:image" content="[^"]+">',
        r'<h1\b[^>]*>.*?</h1>',
        r'<figure class="article-cover" data-article-cover="shared-social">.*?</figure>',
        r'<ol class="v-steps">.*?</ol>',
        r'<script type="application/ld\+json">.*?</script>',
    ):
        result.append(re.findall(expression,page,re.S))
    return result

def apply(root=ROOT):
    src=Path("site/assets")/CSS
    digest=hashlib.sha256(src.read_bytes()).hexdigest()[:12]
    shutil.copy2(src,root/"assets"/CSS)
    stable=[root/"sitemap.xml",root/"articoli/feed.json"]
    before=[p.read_bytes() for p in stable]
    total=layouts=0
    for file in sorted(root.rglob("index.html")):
        path=file.relative_to(root).as_posix().removesuffix("index.html")
        page=file.read_text(encoding="utf-8")
        out=inject(page,path,digest)
        if out==page:continue
        assert contracts(page)==contracts(out),path
        assert page.count('class="v-step"')==out.count('class="v-step"'),path
        assert page.count('<iframe')==out.count('<iframe'),path
        assert inject(out,path,digest)==out,path
        file.write_text(out,encoding="utf-8")
        total+=1
        layouts+=int('data-sunset-layout=' in out)
    assert before==[p.read_bytes() for p in stable]
    verify(root)
    print("SUNSET_BLOG_BUILD_OK",total,"themed pages;",layouts,"editorial layouts")

def verify(root=ROOT):
    home=(root/"index.html").read_text(encoding="utf-8")
    assert home.index('data-hero-slideshow')<home.index('data-sunset-layout')<home.index('id="scegli"')
    guides=json.loads(Path("data/guide.json").read_text(encoding="utf-8"))["guides"]
    guides+=json.loads(Path("data/visual_guides.json").read_text(encoding="utf-8"))["guides"]
    paths=[g.get("canonical_path") or "guide-e-tutorial/"+g["id"]+"/" for g in guides]
    assert EXAMPLE in paths
    for path in ["",*paths,"articoli/","patch/"]:
        page=(root/path/"index.html").read_text(encoding="utf-8")
        assert page.count('data-sunset-layout="right-blog"')==1,path
        assert page.count('data-x-timeline-load')==1,path
        assert page.count('data-x-live-grid')==1,path
        assert 'sunset-blog-v1.css?v=' in page,path
        assert 'src="https://platform.twitter.com/widgets.js"' not in page,path
        if 'id="growth-analytics-v1"' in page:
            assert 'data-umami-event="category-open"' in page and 'data-umami-event="x-timeline-open"' in page,path
        else:
            assert 'data-umami-event="category-open"' not in page,path
        if path in paths:
            assert 'class="sb-quick-jump"' in page and 'href="#procedura"' in page,path
            assert GUIDE_MARKER in page and 'data-article-cover="shared-social"' in page,path
            assert page.index('<h1')<page.index('data-article-cover="shared-social"')<page.index(GUIDE_MARKER)<page.index('class="sb-sidebar"'),path
    for target,*_ in CATEGORIES+IMPORTANT+[(target,label) for path in paths for target,label in related(path)]:
        assert (root/target/"index.html").is_file(),target
    assert (root/"assets"/CSS).is_file()
    print("SUNSET_BLOG_STATIC_OK",len(paths),"complete tutorials")

def browser(root=ROOT):
    from playwright.sync_api import sync_playwright
    directory=root.resolve()
    class Handler(SimpleHTTPRequestHandler):
        def translate_path(self,path):
            clean=unquote(urlsplit(path).path).removeprefix("/gta-6/")
            dest=(directory/clean.lstrip("/")).resolve()
            return str(dest if dest.is_relative_to(directory) else directory/"missing")
        def do_GET(self):
            target=Path(self.translate_path(self.path))
            if target.is_dir():target=target/"index.html"
            if target.is_file() and target.suffix in (".html",".js",".css"):
                raw=target.read_text(encoding="utf-8").replace(BASE,origin).encode()
                self.send_response(200)
                self.send_header("Content-Type",{".html":"text/html; charset=utf-8",".js":"application/javascript",".css":"text/css"}[target.suffix])
                self.send_header("Content-Length",str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
            else:super().do_GET()
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    origin="http://127.0.0.1:"+str(server.server_port)+"/gta-6/"
    Thread(target=server.serve_forever,daemon=True).start()
    shots=Path("reader-qa");shots.mkdir(exist_ok=True)
    try:
        with sync_playwright() as pw:
            b=pw.chromium.launch()
            for width in (390,1440):
                context=b.new_context(viewport={"width":width,"height":900},reduced_motion="reduce")
                remote=[]
                def route(request):
                    if request.request.url.startswith(origin):request.continue_()
                    else:
                        remote.append(request.request.url)
                        request.abort()
                context.route("**/*",route)
                page=context.new_page()
                for path in ("",EXAMPLE,"guide-e-tutorial/scansionare-veicoli/","salvare-auto/","articoli/gta-vi-ultimate-edition-auto-garage/"):
                    assert page.goto(origin+path).status==200
                    assert page.locator(".sb-sidebar").count()==1
                    assert page.locator(".sb-sidebar a.sb-category").count()==len(CATEGORIES)
                    assert page.locator(".sb-profile").get_attribute("href")=="https://x.com/xFederiko11"
                    for theme in ("dark","light"):
                        page.locator('[data-theme-choice="'+theme+'"]').click()
                        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),(width,path,theme)
                        bounds=page.locator(".sunset-blog").evaluate("""e=>{const c=e.querySelector(".sunset-content").getBoundingClientRect(),s=e.querySelector(".sb-sidebar").getBoundingClientRect();return [c.x,c.bottom,s.x,s.y,c.right]}""")
                        if width>=1100:assert bounds[2]>bounds[4],(width,path,theme,bounds)
                        else:assert bounds[3]>=bounds[1]-1,(width,path,theme,bounds)
                        if path and page.locator(GUIDE_MARKER.replace('id="procedura" class="v-tutorial"','#procedura.v-tutorial')).count():
                            assert page.locator(".v-steps .v-step").count()>0
                            assert page.locator(".v-steps .v-step").first.is_visible()
                            assert page.locator(".v-steps .v-step").last.is_visible()
                            assert page.locator(".sb-quick-jump a").first.get_attribute("href")=="#procedura"
                            assert page.locator(".article-cover img").evaluate("(img)=>img.decode().then(()=>img.naturalWidth)")>0
                        if path in ("",EXAMPLE):
                            page.screenshot(path=str(shots/("sunset-"+("home" if not path else "money")+"-"+str(width)+"-"+theme+".png")),full_page=False)
                    assert not any("platform.twitter.com/widgets.js" in x for x in remote),path
                page.locator("[data-x-timeline-load]").click()
                page.wait_for_function("!!document.querySelector('script[src=\"https://platform.twitter.com/widgets.js\"]')")
                assert page.locator(".sb-profile").is_visible()
                context.close()
            b.close()
    finally:
        server.shutdown();server.server_close()
    print("SUNSET_BLOG_BROWSER_OK desktop right / mobile below / light dark / opt-in X fallback")

def live():
    for attempt in range(4):
        try:
            for path in ("",EXAMPLE,"guide-e-tutorial/scansionare-veicoli/","articoli/"):
                req=Request(BASE+path,headers={"Cache-Control":"no-cache","User-Agent":"GTA6Italia-SunsetQA/1.0"})
                with urlopen(req,timeout=15) as response:
                    assert response.status==200
                    page=response.read(2000000).decode("utf-8")
                assert 'data-sunset-layout="right-blog"' in page and 'sunset-blog-v1.css?v=' in page,path
                assert 'data-x-timeline-load' in page and 'src="https://platform.twitter.com/widgets.js"' not in page,path
            with urlopen(BASE+"assets/"+CSS,timeout=15) as response:
                assert response.status==200 and b"--sb-gradient" in response.read(100000)
            print("PUBLIC_SUNSET_BLOG_OK",BASE+EXAMPLE)
            return
        except Exception:
            if attempt==3:raise
            time.sleep(4*(attempt+1))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("build","verify","browser","live"))
    {"build":apply,"verify":verify,"browser":browser,"live":live}[p.parse_args().mode]()
