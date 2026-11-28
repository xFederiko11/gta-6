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
import magazine_article_v1 as magazine_article
from magazine_popular_v1 import popular_panel

ROOT=Path("_site")
BASE="https://xfederiko11.github.io/gta-6/"
CSS="sunset-blog-v1.css"
SEARCH_JS="magazine-quick-search-v1.js"
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
 ("glitch/","Glitch e exploit","pink"),
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
HUBS={"glitch/","guide-e-tutorial/","soldi-facili/","auto-speciali/","articoli/","patch/","scoperte/"}
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

def search_panel():
    """Native links remain usable when JS or the public catalog is unavailable."""
    return ('<section class="sb-panel sb-search" data-magazine-search aria-label="Ricerca articoli">'
            '<p class="sb-kicker">TROVA LA TUA GUIDA</p>'
            '<form class="sb-search-form" role="search" method="get" action="'+BASE+'articoli/" data-search-form>'
            '<label class="sb-heading sb-search-label">Cerca articoli<span class="sb-search-field">'
            '<input type="search" name="q" maxlength="100" placeholder="Auto, trofei, soldi…" autocomplete="off" enterkeyhint="search" data-search-input aria-label="Cerca negli articoli">'
            '<button type="submit" aria-label="Mostra tutti i risultati"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg></button>'
            '</span></label></form>'
            '<p class="sb-search-help" data-search-status role="status" aria-live="polite">Cerca per titolo, veicolo, missione o trofeo.</p>'
            '<div class="sb-search-results" data-search-results hidden></div>'
            '<div class="sb-search-shortcuts"><span>Vai a:</span><a href="'+BASE+'salvare-auto/">Auto</a>'
            '<a href="'+BASE+'garage-gratuiti/">Garage</a><a href="'+BASE+'trofei/roadmap-platino/">Platino</a></div>'
            '<noscript><p class="sb-search-help">I suggerimenti richiedono JavaScript. Puoi comunque sfogliare l’archivio e le categorie.</p></noscript></section>')

def sidebar(path="",*,preview=False,guide=False,track=False):
    from article_chronology_v1 import tree, inventory, taxonomy
    active_group=""
    if not preview:
        if path.startswith("articoli/categoria/"):
            active_group=path.split("/")[2]
        else:
            current=next((r for r in inventory() if r[0]==path),None)
            if current:active_group=taxonomy(current)[0]
    def category_link(target,label,cls=""):
        return ('<a'+(' class="'+cls+'"' if cls else '')+' href="'+BASE+target+'"'+
                (' aria-current="page"' if not preview and target==path else '')+
                tracking(track and not preview,"category-open",target)+'>'+esc(label)+'</a>')
    categories=category_link("articoli/","Tutti gli articoli →","sb-all-articles")+''.join(
        '<details class="sb-taxonomy" data-color="'+esc(g["color"])+'"'+(' open' if g["id"]==active_group else '')+'><summary><span class="sb-taxonomy-label">'+esc(g["label"])+'</span><span class="sb-taxonomy-count">'+str(g["count"])+'</span></summary>'+
        category_link(g["path"],"Tutta la categoria")+''.join(category_link(c["path"],c["label"]) for c in g["children"])+'</details>' for g in tree())
    important="".join('<a href="'+BASE+target+'"'+tracking(track,"important-guide-open",target)+'>'+esc(label)+' <span aria-hidden="true">→</span></a>' for target,label in IMPORTANT if target!=path)
    jump=('<div class="sb-panel"><p class="sb-kicker">IN QUESTA GUIDA</p><nav class="sb-important" aria-label="Indice della guida">'
          '<a href="#procedura"'+tracking(track,"tutorial-jump","procedura")+'>Passaggi del tutorial <span aria-hidden="true">↓</span></a>'
          '<a href="#approfondimenti"'+tracking(track,"tutorial-jump","approfondimenti")+'>Approfondimenti e fonti <span aria-hidden="true">↓</span></a></nav></div>') if guide else ""
    return ('<aside class="sb-sidebar" aria-label="Categorie e aggiornamenti GTA VI Italia">'+search_panel()+popular_panel()+jump+
            '<div class="sb-panel"><p class="sb-kicker">ESPLORA LEONIDA</p><p class="sb-heading">Categorie</p>'
            '<nav class="sb-categories" aria-label="Categorie del sito">'+categories+'</nav><a class="sb-tag-directory" href="'+BASE+'articoli/tag/"'+tracking(track,"tag-directory-open","articoli/tag/")+'>Esplora tutti i tag →</a></div>'
            '<div class="sb-panel"><p class="sb-kicker">NON PERDERTELI</p><p class="sb-heading">Da tenere a portata di mano</p>'
            '<nav class="sb-important" aria-label="Guide importanti">'+important+'</nav></div>'
            '<div class="sb-panel sb-x-panel"><p class="sb-kicker">DALLA REDAZIONE</p><p class="sb-heading">𝕏 Ultimi post</p>'
            '<p class="sb-x-description">Ultimi cinque post pubblici, incorporati direttamente da X.</p>'
            '<div class="sb-x-feed" data-x-timeline-slot aria-live="polite">'
            '<a class="twitter-timeline" data-height="460" data-tweet-limit="5" data-lang="it" data-chrome="nofooter" data-theme="dark" href="https://twitter.com/xFederiko11?ref_src=twsrc%5Etfw">Post pubblici di @xFederiko11</a>'
            '</div>'
            '<button class="sb-x-button" type="button" data-x-timeline-load'+tracking(track,"x-timeline-open")+' hidden>Riprova il feed X</button>'
            '<p class="sb-x-description">Feed fornito da X. Se non viene caricato, apri il profilo dal collegamento qui sotto.</p>'
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
    return GUIDE_MARKER in page or "data-legit-guide" in page or path in HUBS or path.startswith(("articoli/","patch/","garage-gratuiti/"))

def inject(page,path,digest,catalog=None):
    if 'data-design-version=' not in page or 'name="sunset-blog-version"' in page:
        return page
    page=page.replace('</head>','<meta name="sunset-blog-version" content="'+VERSION+
                      '"><link rel="stylesheet" href="'+BASE+'assets/'+CSS+'?v='+digest+'"></head>',1)
    track='id="growth-analytics-v1"' in page
    if catalog is not None:
        page=magazine_article.enhance(page,path,catalog,track)
    if path=="" or eligible(path,page):
        page=page.replace('</head>','<script src="'+BASE+'assets/'+SEARCH_JS+'?v='+digest+'" defer></script></head>',1)
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
    page=page.replace("</body>",'<script src="../assets/community-social-v1.js" defer></script><script src="../assets/magazine-quick-search-v1.js" defer></script></body>',1)
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
    script=Path("site/assets")/SEARCH_JS
    digest=hashlib.sha256(src.read_bytes()+script.read_bytes()).hexdigest()[:12]
    shutil.copy2(src,root/"assets"/CSS)
    shutil.copy2(script,root/"assets"/SEARCH_JS)
    stable=[root/"sitemap.xml",root/"articoli/feed.json"]
    before=[p.read_bytes() for p in stable]
    catalog=magazine_article.load_catalog(root)
    total=layouts=0
    for file in sorted(root.rglob("index.html")):
        path=file.relative_to(root).as_posix().removesuffix("index.html")
        page=file.read_text(encoding="utf-8")
        out=inject(page,path,digest,catalog)
        if out==page:continue
        assert contracts(page)==contracts(out),path
        assert page.count('class="v-step"')==out.count('class="v-step"'),path
        assert page.count('<iframe')==out.count('<iframe'),path
        assert inject(out,path,digest,catalog)==out,path
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
        assert page.count('data-magazine-search')==1,path
        assert page.index('data-magazine-search')<page.index('data-magazine-popular')<page.index('class="sb-categories"'),path
        assert SEARCH_JS+'?v=' in page,path
        assert page.count('data-x-live-grid')==0,path
        assert page.count('class="twitter-timeline"')==1,path
        assert page.count('data-tweet-limit="5"')==1,path
        assert page.count('data-lang="it"')==1,path
        assert 'data-chrome="noheader' not in page,path
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
    assert (root/"assets"/SEARCH_JS).is_file()
    magazine_article.verify(root)
    print("SUNSET_BLOG_STATIC_OK",len(paths),"complete tutorials")

def prepare_full_capture(page):
    """Warm visible first-party lazy photos for QA only; never load external embeds."""
    visible_images = """() => [...document.images].filter(img => {
        const r = img.getBoundingClientRect();
        return r.width > 0 && r.height > 0 &&
            getComputedStyle(img).visibility !== 'hidden' &&
            img.getAttribute('src') &&
            new URL(img.src, location.href).origin === location.origin;
    })"""
    count = page.evaluate(f"() => {{const imgs=({visible_images})(); "
                          "imgs.forEach(img=>img.loading='eager');return imgs.length;}")
    page.wait_for_function(f"() => ({visible_images})().every(img=>img.complete && img.naturalWidth>0)",
                           timeout=15000)
    page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    page.wait_for_function("window.scrollY===0")
    print("MAGAZINE_CAPTURE_LOCAL_IMAGES_OK", count, flush=True)


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
            for width in (390,768,1440):
                context=b.new_context(viewport={"width":width,"height":900},reduced_motion="reduce")
                remote=[];widget_requests=[]
                def route(request):
                    request_url=request.request.url
                    if request_url.startswith(origin):
                        request.continue_()
                    elif request_url=="https://platform.twitter.com/widgets.js":
                        widget_requests.append(request_url)
                        request.fulfill(status=200,content_type="application/javascript",
                            body="window.twttr={widgets:{load:function(slot){slot.dataset.xTestWidgetLoaded='true';return Promise.resolve();}}};")
                    else:
                        remote.append(request_url)
                        request.abort()
                context.route("**/*",route)
                page=context.new_page()
                # In a headless test, explicitly cross the lazy-load threshold
                # when the X panel registers; all other observers stay native.
                page.add_init_script("""(() => {
                  const Native=window.IntersectionObserver;
                  if(!Native)return;
                  const instances=[];
                  window.IntersectionObserver=class extends Native{
                    constructor(callback,options){
                      super(callback,options);
                      this.__callback=callback;
                      this.__targets=[];
                      instances.push(this);
                    }
                    observe(target){
                      super.observe(target);
                      this.__targets.push(target);
                    }
                  };
                  window.__triggerTestIntersection=(selector)=>{
                    for(const observer of instances){
                      for(const target of observer.__targets){
                        if(target&&target.matches&&target.matches(selector))
                          observer.__callback([{target,isIntersecting:true,intersectionRatio:1}],observer);
                      }
                    }
                  };
                })();""")
                for path in ("",EXAMPLE,"guide-e-tutorial/scansionare-veicoli/","salvare-auto/","articoli/gta-vi-ultimate-edition-auto-garage/"):
                    previous_widgets=len(widget_requests)
                    assert page.goto(origin+path).status==200
                    assert page.locator(".sb-sidebar").count()==1
                    assert page.locator(".sb-sidebar .sb-taxonomy").count()==8
                    assert page.locator("[data-magazine-popular]").count()==1
                    quick=page.locator("[data-magazine-search]")
                    assert quick.count()==1
                    assert quick.evaluate("e=>!!(e.compareDocumentPosition(document.querySelector('[data-magazine-popular]')) & Node.DOCUMENT_POSITION_FOLLOWING)")
                    if not path:
                        field=quick.locator("[data-search-input]")
                        field.fill("Southside Storage")
                        result=quick.locator('[data-search-results] a[href$="/garage-gratuiti/southside-storage/"]')
                        result.wait_for(state="visible")
                        assert 1<=quick.locator("[data-search-results] a").count()<=6
                        assert not page.evaluate("document.documentElement.scrollWidth>innerWidth+1")
                        quick.screenshot(path=str(shots/("magazine-search-"+str(width)+".png")))
                        field.press("ArrowDown")
                        assert quick.locator("[data-search-results] a").first.evaluate("e=>e===document.activeElement")
                        page.keyboard.press("Escape")
                        assert field.evaluate("e=>e===document.activeElement")
                        assert quick.locator("[data-search-results]").is_hidden()
                        assert quick.locator("[data-search-status]").inner_text()=="Cerca per titolo, veicolo, missione o trofeo."
                        field.fill("automobili")
                        quick.locator('[data-search-results] a').first.wait_for(state="visible")
                        assert "Nessun articolo" not in quick.locator('[data-search-status]').inner_text()
                        field.fill("zzzxxyy123")
                        page.wait_for_function("document.querySelector('[data-search-status]').textContent.includes('Nessun articolo')")
                        assert quick.locator("[data-search-results] a").count()==0
                        field.fill("Southside Storage")
                        field.press("Enter")
                        page.wait_for_url("**/articoli/?q=Southside+Storage")
                        page.wait_for_function("document.querySelector('[data-chronology-search]').value==='Southside Storage' && !document.querySelector('[data-chronology-filters]').hidden")
                        assert page.locator('[data-chronology-path="garage-gratuiti/southside-storage/"]').count()==1
                        assert 1<=page.locator("[data-chronology-path]").count()<=25
                        page.goto(origin)
                        print("MAGAZINE_QUICK_SEARCH_BROWSER_OK",width,flush=True)
                    assert page.locator("[data-magazine-popular]").evaluate("e=>!!(e.compareDocumentPosition(document.querySelector('.sb-categories')) & Node.DOCUMENT_POSITION_FOLLOWING)")
                    assert page.locator(".sb-taxonomy:not([open])").first.evaluate("e=>e.getBoundingClientRect().height<75")
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
                        if path:
                            assert page.locator('[data-magazine-article="v1"]').count()==1,(width,path)
                            assert page.locator('h1 + .article-cover').count()==1,(width,path)
                            assert page.locator('[data-magazine-related]').count()==1,(width,path)
                            assert page.locator('[data-magazine-article="v1"] nav a').count()==2
                            if page.locator('#procedura.v-tutorial').count():
                                index=page.locator('[data-magazine-steps]')
                                steps=page.locator('#procedura .v-step')
                                assert index.locator('a').count()==steps.count()
                                assert steps.count()>0
                                if path==EXAMPLE:
                                    assert index.locator('details').get_attribute('open') is None
                                    index.locator('summary').click()
                                    assert index.locator('a').last.is_visible()
                                    index.locator('a').last.click()
                                    assert page.url.endswith('#passaggio-'+str(steps.count()))
                                    assert steps.last.is_visible()
                                    index.screenshot(path=str(shots/("magazine-step-index-"+str(width)+"-"+theme+".png")))
                                    page.locator('[data-magazine-related]').screenshot(path=str(shots/("magazine-related-"+str(width)+"-"+theme+".png")))
                                    index.locator('summary').click()
                                    page.evaluate('window.scrollTo(0,0)')
                        if path in ("",EXAMPLE):
                            page.screenshot(path=str(shots/("sunset-"+("home" if not path else "money")+"-"+str(width)+"-"+theme+".png")),full_page=False)
                            prepare_full_capture(page)
                            suffix = "" if theme=="dark" else "-light"
                            page.screenshot(path=str(shots/("magazine-full-"+("home" if not path else "article")+"-"+str(width)+suffix+".png")),
                                            full_page=True,animations="disabled")
                    if path==EXAMPLE:
                        print("MAGAZINE_ARTICLE_BROWSER_OK",width)
                    page.locator(".sb-x-panel").scroll_into_view_if_needed()
                    page.evaluate("window.__triggerTestIntersection('.sb-x-panel')")
                    page.wait_for_function("document.querySelector('[data-x-timeline-slot]')?.dataset.xTestWidgetLoaded==='true'",timeout=10000)
                    assert page.locator('[data-x-timeline-slot] a.twitter-timeline').get_attribute("data-tweet-limit")=="5"
                    assert page.locator("[data-x-timeline-load]").is_hidden()
                    assert page.locator(".sb-profile").is_visible()
                    assert len(widget_requests)==previous_widgets+1,path
                    assert not any("platform.twitter.com/widgets.js" in url for url in remote),path
                context.close()
            b.close()
    finally:
        server.shutdown();server.server_close()
    print("SUNSET_BLOG_BROWSER_OK desktop right / mobile below / light dark / lazy five-post X timeline")

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
                assert page.index('data-magazine-search')<page.index('data-magazine-popular'),path
                assert SEARCH_JS+'?v=' in page,path
                if path in (EXAMPLE,"guide-e-tutorial/scansionare-veicoli/"):
                    assert 'data-magazine-article="v1"' in page and 'data-magazine-steps' in page and 'data-magazine-related' in page,path
            with urlopen(BASE+"assets/"+CSS,timeout=15) as response:
                assert response.status==200 and b"--sb-gradient" in response.read(100000)
            with urlopen(BASE+"assets/"+SEARCH_JS,timeout=15) as response:
                assert response.status==200 and b"MAGAZINE_QUICK_SEARCH_V1" in response.read(100000)
            print("PUBLIC_MAGAZINE_QUICK_SEARCH_OK")
            print("PUBLIC_SUNSET_BLOG_OK",BASE+EXAMPLE)
            return
        except Exception:
            if attempt==3:raise
            time.sleep(4*(attempt+1))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("build","verify","browser","live"))
    {"build":apply,"verify":verify,"browser":browser,"live":live}[p.parse_args().mode]()
