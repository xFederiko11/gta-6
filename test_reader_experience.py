"""Regression tests for production HTML and real-browser reader behavior."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import re
import sys
import unittest
from reader_experience import VERSION, validate, transform, gsc_verification_meta
from test_visual_site import Tags

ROOT=Path('_site')
BASE='https://xfederiko11.github.io/gta-6/'

class ReaderTests(unittest.TestCase):
    def test_search_console_verification_opt_in_without_new_tracking(self):
        homepage='<html lang="it"><head></head><body></body></html>'
        token='verified_public_sample_token_123456'
        self.assertEqual(gsc_verification_meta(''), '')
        default=transform(homepage,version='unit')
        self.assertNotIn('google-site-verification',default)
        verified=transform(homepage,version='unit',gsc_token=token)
        self.assertIn('<meta name="google-site-verification" content="'+token+'">',verified)
        self.assertNotIn('cloudflareinsights',verified)
        self.assertNotIn('google-analytics',verified)
        for bad in ('x', 'token\" onload=\"danger', '<script>alert(1)</script>', 'ä'*30):
            with self.assertRaises(ValueError):gsc_verification_meta(bad)

    def test_google_search_console_file_and_meta_survive_static_generation(self):
        from reader_experience import GSC_PUBLIC_VERIFICATION_TOKEN
        token='U1WNfaHHGPHzojaeFvn_GGhVrWb5TYeDyUPgpmCX6Nw'
        name='google232edbd3526a5a1d.html'
        exact=b'google-site-verification: google232edbd3526a5a1d.html'
        self.assertEqual(GSC_PUBLIC_VERIFICATION_TOKEN,token)
        self.assertEqual((Path('site')/name).read_bytes(),exact)
        homepage=(ROOT/'index.html').read_text(encoding='utf-8')
        tag='<meta name="google-site-verification" content="'+token+'">'
        self.assertEqual(homepage.count(tag),1)
        self.assertIn('<link rel="canonical" href="'+BASE+'">',homepage)
        self.assertNotIn('google-site-verification',(ROOT/'trofei/index.html').read_text(encoding='utf-8'))
        workflow=Path('.github/workflows/deploy-site.yml').read_text(encoding='utf-8')
        self.assertIn('GSC_VERIFICATION_FILE_INCLUDED',workflow)
        self.assertIn('PUBLIC_GSC_VERIFICATION_FILE_OK',workflow)
        self.assertIn('PUBLIC_GSC_META_TAG_OK',workflow)

    def test_umami_publication_is_site_wide_but_never_in_pull_request_preview(self):
        import os
        from growth_tracking_v1 import normalize_id
        owner_id='ec3592c0-e9f7-4e13-8c29-f9c7d59aa8fd'
        homepage=(ROOT/'index.html').read_text(encoding='utf-8')
        matched=re.search(r'<script id="growth-analytics-v1"[^>]*data-website-id="([^"]+)"',homepage)
        # The build step has the configuration, but this separate test step
        # does not inherit its step-scoped UMAMI_WEBSITE_ID environment value.
        # Inspect the *generated HTML*, then check the actual GitHub event.
        site_id=normalize_id(matched.group(1)) if matched else None
        event=os.getenv('GITHUB_EVENT_NAME')
        if event=='pull_request':
            self.assertIsNone(site_id,'PR preview must not load Umami')
        elif event:
            self.assertEqual(site_id,owner_id,'Production must use the verified Umami site')
        urls=('index.html','trofei/index.html','guide-e-tutorial/index.html',
              'hdr-oled/index.html','privacy/index.html',
              'guide-e-tutorial/glitch-prima-persona-ps5/index.html')
        for path in urls:
            with self.subTest(page=path):
                source=(ROOT/path).read_text(encoding='utf-8')
                scripts=source.count('id="growth-analytics-v1"')
                self.assertEqual(scripts,1 if site_id else 0)
                if site_id:
                    self.assertEqual(source.count('data-website-id="'+site_id+'"'),1)
                    self.assertIn('data-domains="xfederiko11.github.io"',source)
                    self.assertIn('data-do-not-track="true"',source)
                else:
                    self.assertNotIn('cloud.umami.is/script.js',source)
                    self.assertNotIn('data-umami-event=',source)
        privacy=(ROOT/'privacy/index.html').read_text(encoding='utf-8')
        if site_id:
            self.assertIn('Umami Cloud è attivo',privacy)
            self.assertIn('Un clic per seguire',privacy)
            guide=(ROOT/'guide-e-tutorial/glitch-prima-persona-ps5/index.html').read_text(encoding='utf-8')
            self.assertIn('data-umami-event="youtube-player-open"',guide)
        else:
            self.assertNotIn('Umami Cloud è attivo',privacy)

    def test_all_pages_initialize_responsive_theme_before_stylesheets(self):
        for file in ROOT.rglob('*.html'):
            text=file.read_text(encoding='utf-8')
            self.assertIn('<html lang="it" data-theme="auto">',text,str(file))
            self.assertIn('id="reader-theme-boot"',text,str(file))
            self.assertLess(text.index('id="reader-theme-boot"'),text.index('rel="stylesheet"'),str(file))
            self.assertNotIn('<meta name="color-scheme" content="light">',text)
            self.assertIn('reader-theme.css?v=',text)
            if 'data-design-version=' in text:
                self.assertEqual(text.count('data-theme-choice="dark"'),1)
                self.assertEqual(text.count('data-theme-choice="light"'),1)
    def test_11_guides_are_complete_linear_articles_without_navigation(self):
        guides=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
        guides+=json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides']
        self.assertEqual(len(guides),11)
        css=Path('site/assets/guide-flow-v1.css').read_text(encoding='utf-8')
        js=Path('site/assets/guide-flow-v1.js').read_text(encoding='utf-8')
        self.assertNotIn('[data-gf-next]',js)
        self.assertNotIn('step.hidden',js)
        self.assertNotIn('guide-flow-on',css)
        for guide in guides:
            path=guide.get('canonical_path') or 'guide-e-tutorial/'+guide['id']+'/'
            html=(ROOT/path/'index.html').read_text(encoding='utf-8')
            with self.subTest(guide=guide['id']):
                self.assertIn('guide-flow-v1.css?v=',html)
                self.assertNotIn('guide-flow-v1.js?v=',html)
                self.assertNotIn('data-gf-next',html)
                self.assertNotIn('data-gf-back',html)
                self.assertIn('id="procedura" class="v-tutorial"',html)
                self.assertEqual(html.count('class="v-step"'),len(guide['steps']))
                self.assertNotIn('hidden class="v-step"',html)
                self.assertNotIn('class="v-step" hidden',html)
                self.assertLess(html.index('<ol class="v-steps">'),
                                html.index('class="v-guide-more"'))
        for path in ('index.html','trofei/index.html','hdr-oled/index.html'):
            html=(ROOT/path).read_text(encoding='utf-8')
            self.assertNotIn('guide-flow-v1.js?v=',html,path)
            self.assertNotIn('guide-flow-v1.css?v=',html,path)

    def test_release_and_idempotence(self):
        release=json.loads((ROOT/'design-version.json').read_text())
        self.assertEqual(release['default_theme'],'unified-dark-mobile-desktop')
        self.assertEqual(release['reader_version'],VERSION)
        self.assertEqual(release['guides_with_extras'],5)
        self.assertEqual(release['tip_count'],12)  # includes sourced time-skip note
        page=(ROOT/'salvare-auto/index.html').read_text()
        self.assertEqual(transform(page,version='anything'),page)
    def test_sourced_tips_and_images_visible_with_warning(self):
        data=json.loads(Path('data/guide_extras.json').read_text())
        self.assertTrue(validate(data))
        for path,entry in data['guides'].items():
            text=(ROOT/path/'index.html').read_text()
            self.assertEqual(text.count('class="r-tip"'),len(entry['tips']))
            self.assertEqual(text.count('id="consigli"'),1)
            tags=Tags();tags.feed(text)
            self.assertFalse(any(t=='details' and 'data-spoiler' in a for t,a in tags.tags))
            if entry['spoiler']:
                self.assertIn('v-spoiler-warning',text)
                self.assertIn('id="mappa"',text)
                self.assertIn('id="consigli"',text)
            for tip in entry['tips']:self.assertIn(tip['source'],text)
            ids=[a['id'] for t,a in tags.tags if 'id' in a]
            self.assertEqual(len(ids),len(set(ids)),path)
    def test_reject_unsafe_sources_and_missing_spoiler_classification(self):
        original=json.loads(Path('data/guide_extras.json').read_text())
        for bad in ['http://www.powerpyx.com/a/','https://www.powerpyx.com.evil.test/a/','https://user@www.powerpyx.com/a/']:
            data=copy.deepcopy(original);next(iter(data['guides'].values()))['tips'][0]['source']=bad
            with self.assertRaises(ValueError):validate(data)
        data=copy.deepcopy(original);del next(iter(data['guides'].values()))['spoiler']
        with self.assertRaises(ValueError):validate(data)
    def test_no_screenshot_inversion_or_network_calls(self):
        css=Path('site/assets/reader-theme.css').read_text();js=Path('site/assets/reader-theme.js').read_text()
        self.assertNotIn('filter:invert',css.replace(' ',''));self.assertNotIn('brightness(',css)
        self.assertIn('gta6-theme-v1',js);self.assertNotIn('data-spoiler-choice',js)
        self.assertIn("const chooseDefault = () => 'dark'",js)
        self.assertNotIn('fetch(',js);self.assertNotIn('prefers-color-scheme',js)
        self.assertIn('showModal()',js);self.assertIn('event.ctrlKey',js)
    def test_reviewed_details_not_contradicted_by_guide(self):
        taxi=(ROOT/'guide-e-tutorial/viaggio-rapido-taxi/index.html').read_text()
        self.assertIn('in aggiunta alla tariffa della corsa',taxi)
        self.assertNotIn('un costo di 100 GTA$ per il servizio',taxi)
        self.assertIn('Gone Fishing (Capitolo 1)',taxi)
        self.assertIn('100 GTA$ in aggiunta alla tariffa della corsa.',taxi.split('id="procedura"',1)[0])
        self.assertEqual(taxi.count('class="v-step"'),4)
        self.assertEqual(taxi.count('class="v-check"'),4)
        self.assertIn('RydeMe',taxi)
        animals=(ROOT/'guide-e-tutorial/studiare-animali/index.html').read_text()
        self.assertIn('100 specie su 255',animals)
        self.assertEqual(animals.count('class="v-step"'),4)
        self.assertEqual(animals.count('class="v-check"'),4)
        self.assertIn('Progressi → Animali',animals)
        garage=(ROOT/'salvare-auto/index.html').read_text()
        self.assertIn('sblocchi successivi',garage)
        self.assertNotIn("Porta l&#x27;auto che vuoi conservare dentro un Pay",garage)


def check_layout(page,out,width,path,theme):
    page.evaluate('document.fonts.ready')
    page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
    overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
    if overflow:
        detail=page.evaluate('''() => ({viewport:innerWidth,document:document.documentElement.scrollWidth,
          elements:Array.from(document.querySelectorAll('body *')).filter(e=>{
            const r=e.getBoundingClientRect();return r.width && (r.right>innerWidth+1 || r.left < -1);
          }).slice(0,25).map(e=>({tag:e.tagName,css:e.className,text:e.textContent.slice(0,80),
             left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right,
             width:e.getBoundingClientRect().width,font:getComputedStyle(e).fontFamily}))})''')
        name=f'overflow-{width}-{theme}-{path.replace("/","-") or "home"}'
        page.screenshot(path=str(out/(name+'.png')),full_page=True)
        (out/(name+'.json')).write_text(json.dumps(detail,indent=2),encoding='utf-8')
        print('READER_OVERFLOW',width,path,theme,json.dumps(detail),flush=True)
    assert not overflow,(width,path,theme,'overflow')


def browser_qa():
    import os,shutil,threading
    from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
    from urllib.parse import urlsplit,unquote
    from playwright.sync_api import sync_playwright
    directory=ROOT.resolve();out=Path('reader-qa');out.mkdir(exist_ok=True)
    class Handler(SimpleHTTPRequestHandler):
        def translate_path(self,path):
            clean=unquote(urlsplit(path).path).removeprefix('/gta-6/')
            target=(directory/clean.lstrip('/')).resolve()
            return str(target if target.is_relative_to(directory) else directory/'missing')
        def do_GET(self):
            target=Path(self.translate_path(self.path))
            if target.is_dir():target=target/'index.html'
            if target.is_file() and target.suffix in ('.html','.css','.js'):
                raw=target.read_text(encoding='utf-8').replace(BASE,origin).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type',{'.html':'text/html; charset=utf-8','.css':'text/css','.js':'application/javascript'}[target.suffix])
                self.send_header('Content-Length',str(len(raw)))
                self.end_headers();self.wfile.write(raw)
            else:super().do_GET()
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)+'/gta-6/'
    report=[]
    try:
        with sync_playwright() as p:
            executable=os.getenv('QA_CHROMIUM') or shutil.which('chromium')
            browser=p.chromium.launch(**({'executable_path':executable} if executable else {}))
            def bind(context):
                def route(req):
                    if req.request.url.startswith(origin):req.continue_()
                    else:req.abort()
                context.route('**/*',route)
            for width in (320,390,768,1440):
                context=browser.new_context(viewport={'width':width,'height':900},color_scheme='light')
                bind(context);page=context.new_page();errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                paths=['','guide-e-tutorial/key-cloner/','guide-e-tutorial/vendere-veicoli/','glitch/','articoli/','garage-gratuiti/','garage-gratuiti/southside-storage/','garage-gratuiti/domestic-timbers/','garage-gratuiti/garage-storia/','garage-gratuiti/garage-storia/port-gellhorn/','garage-gratuiti/garage-storia/thompson-court/','garage-gratuiti/garage-storia/ne-15th-street/','garage-gratuiti/garage-storia/pegassi-residences/','patch/','patch/2026-11-23/','salvare-auto/','guide-e-tutorial/veicoli-per-moses/','guide-e-tutorial/studiare-animali/','guide-e-tutorial/viaggio-rapido-taxi/','guide-e-tutorial/70-sfide-100-percento/','guide-e-tutorial/poligoni-concentrazione/','guide-e-tutorial/sportive-randy-posizioni/','guide-e-tutorial/soldi-facili-capitolo-1/','guide-e-tutorial/scansionare-veicoli/','guide-e-tutorial/soldi-2500-three-sheets-liquor/','guide-e-tutorial/meditazione-capitolo-1/','guide-e-tutorial/glitch-prima-persona-ps5/','trofei/','trofei/trofeo-14-una-lunga-strada/','trofei/trofeo-17-cecchino/','hdr-oled/','hdr-oled/lg-oled-c4/','hdr-oled/samsung-s90f/','trucchi/','scoperte/','screenshot-ps5/','collezionabili/percorsi/','screenshot-ps5/invia/','screenshot-ps5/priorita/','immagini-ufficiali/','articoli/gta-vi-ultimate-edition-auto-garage/','video-tutorial/','veicoli/','veicoli/declasse-yosemite-1500/','veicoli/pegassi-toros/','veicoli/pegassi-vitello/','veicoli/pegassi-infernus/','veicoli/pegassi-tempesta/','veicoli/buckingham-windsor-drop/','veicoli/ocelot-jagular/','veicoli/buckingham-jubilee/','veicoli/grotti-itali-rsx/','veicoli/pfister-growler/','veicoli/gallivanter-baller-st-d/','veicoli/ascot-paragon/','veicoli/bravado-gauntlet-hellfire/','veicoli/piccia-furia/','veicoli/benefactor-dubsta/','veicoli/bravado-banshee/','veicoli/declasse-akane-anime/','veicoli/annis-drifter-elegy/','veicoli/vapid-rocket-slamvan/','veicoli/invetero-spiderweb-coquette/','veicoli/declasse-applesauce-bobcat/','veicoli/pfister-vanessas-growler/','veicoli/maibatsu-penumbra-ff-verde/','veicoli/invetero-coquette-d10/','guide-e-tutorial/']
                for path in paths:
                    print('READER_CASE',width,path or 'home',flush=True)
                    page.goto(origin+path,wait_until='load')
                    if path=='':assert page.locator('html').get_attribute('data-theme')=='dark'
                    for theme in ('light','dark'):
                        page.locator(f'[data-theme-choice="{theme}"]').click()
                        assert page.locator('html').get_attribute('data-theme')==theme
                        expected='rgb(16, 19, 29)' if theme=='dark' else 'rgb(247, 245, 250)'
                        assert page.evaluate('getComputedStyle(document.body).backgroundColor')==expected,(path,theme)
                        page.reload(wait_until='load')
                        assert page.locator('html').get_attribute('data-theme')==theme,'persistence'
                        check_layout(page,out,width,path,theme)
                    if path=='articoli/':
                        page.locator('[data-chronology-filters]').wait_for(state='visible')
                        assert page.locator('[data-chronology-path]:visible').count()==25
                        page.locator('[data-chronology-filter]').select_option('glitch')
                        assert page.locator('[data-chronology-path]:visible').count()==1
                        page.locator('[data-chronology-filter]').select_option('veicoli')
                        page.locator('[data-chronology-subfilter]').select_option('garage')
                        assert page.locator('[data-chronology-path]:visible').count()>=4
                        assert page.locator('[data-chronology-path][data-sub="garage"]:visible').count()==page.locator('[data-chronology-path]:visible').count()
                        page.locator('[data-chronology-filter]').select_option('')
                        page.locator('[data-chronology-search]').fill('Southside Storage')
                        # Search now covers titles AND descriptions. Related pages
                        # mentioning the garage are valid; assert the exact guide
                        # is found and each result contains both terms.
                        matches=page.locator('[data-chronology-path]:visible')
                        assert 1<=matches.count()<=25
                        assert page.locator('[data-chronology-path="garage-gratuiti/southside-storage/"]:visible').count()==1
                        for result in matches.all():
                            text=result.inner_text().lower()
                            assert 'southside' in text and 'storage' in text,text
                        page.locator('[data-chronology-search]').fill('nessunrisultatozzzz')
                        assert page.locator('[data-chronology-path]:visible').count()==0
                        assert 'Nessun articolo trovato' in page.locator('[data-chronology-count]').inner_text()
                        page.locator('[data-chronology-reset]').click()
                        assert page.locator('[data-chronology-search]').input_value()==''
                        assert page.locator('[data-chronology-path]:visible').count()==25
                        page.locator('[data-chronology-search]').fill('trofeo')
                        assert page.locator('[data-chronology-path]:visible').count()==25
                        before=page.locator('[data-chronology-path]').first.get_attribute('data-chronology-path')
                        page.locator('[data-archive-pager] button').filter(has_text='Avanti').click()
                        assert page.locator('[data-chronology-path]').first.get_attribute('data-chronology-path')!=before
                        page.locator('[data-chronology-reset]').click()
                        page.locator('[data-archive-pager] a.archive-next').click()
                        assert page.url.endswith('/articoli/pagina/2/')
                        assert page.locator('[data-chronology-path]').count()==25
                        assert page.locator('[data-archive-pager] [aria-current=page]').inner_text()=='2'
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                        page.goto(origin+'articoli/categoria/veicoli/garage/',wait_until='load')
                        assert page.locator('[data-chronology-path][data-sub="garage"]').count()==page.locator('[data-chronology-path]').count()
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                        page.goto(origin+'articoli/',wait_until='load')
                        print('MAGAZINE_ARCHIVE_BROWSER_OK',width,flush=True)
                    if path=='garage-gratuiti/southside-storage/' and width==390:
                        field=page.locator('[data-vc-code-value]')
                        assert field.input_value()=="1010"
                        assert field.get_attribute('readonly') is not None
                        context.grant_permissions(['clipboard-read','clipboard-write'])
                        page.locator('[data-vc-copy-code]').click()
                        assert page.evaluate('navigator.clipboard.readText()')=="1010"
                        assert page.locator('[data-vc-code-status]').inner_text()=="Codice copiato."
                    if path.startswith('patch/'):
                        intro=page.locator('[data-patch-intro]')
                        if intro.count():
                            assert intro.evaluate('(el) => getComputedStyle(el).display')!='grid'
                            assert intro.locator('h1 + .article-cover').count()==1
                            heading=intro.locator('h1').bounding_box()
                            cover=intro.locator('.article-cover').bounding_box()
                            assert heading and cover and cover['y'] >= heading['y']+heading['height']-1
                        if width in (390,1440):
                            page.screenshot(path=str(out/('patch-'+path.strip('/').replace('/','-')+'-'+str(width)+'.png')),full_page=True,animations='disabled')
                    if path=='' and width==1440:
                        # The actual desktop hero must be centered, without the
                        # old 13% horizontal shift, and advance automatically.
                        hero=page.locator('[data-hero-slideshow]')
                        page.wait_for_function(
                            "() => !!document.querySelector('[data-hero-slideshow]')?.dataset.heroIndex",
                            timeout=10000)
                        position=page.locator('.ci-hero-image[data-hero-active="true"]').evaluate(
                            "(img) => getComputedStyle(img).objectPosition")
                        self_center=position in ('50% 50%', 'center center')
                        assert self_center,(position,'desktop photo not centered')
                        translation=page.locator('.ci-hero-image[data-hero-active="true"]').evaluate(
                            "(img) => getComputedStyle(img).transform")
                        assert translation=='none',(translation,'desktop photo shifted')
                        old_index=hero.get_attribute('data-hero-index')
                        page.mouse.move(0,0)
                        page.wait_for_function(
                            "old => document.querySelector('[data-hero-slideshow]')?.dataset.heroIndex !== old",
                            arg=old_index,timeout=6000)
                    if path=='hdr-oled/lg-oled-c4/':
                        assert page.locator('[data-hdr-tv-reference="lg-oled-c4"]').count()==1
                        assert page.locator('.hdr-tv-settings-table tbody tr').count()==11
                        assert page.locator('.hdr-tv-settings-table .hdr-tv-status-verified').count()==8
                        assert page.locator('img[src*="hdr-tv-reference-v1.svg"]').count()==1
                        assert page.locator('[data-hdr-photo-gallery="lg-oled-c4"]').count()==1
                        if width in (390,1440):
                            page.screenshot(path=str(out/f'hdr-tv-c4-{width}.png'),
                                            full_page=True,animations='disabled')
                    if path=='hdr-oled/samsung-s90f/':
                        assert page.locator('[data-hdr-tv-reference="samsung-s90f"]').count()==1
                        assert page.locator('.hdr-tv-settings-table tbody tr').count()==7
                        assert page.get_by_text('Non verificato', exact=True).count()>=4
                        assert page.locator('[data-hdr-photo-gallery="samsung-s90f"]').count()==1
                        assert page.get_by_text('variante regionale',exact=False).count()>=1
                    if path=='video-tutorial/':
                        cards=page.locator('[data-cv-video-id]')
                        assert cards.count()==4
                        assert page.locator('.cv-card:visible').count()==4
                        assert page.locator('.cv-embed-slot iframe').count()==0
                        assert page.locator('[data-cv-load]').first.is_visible()
                        assert page.locator('h1').count()==1
                        # No external YouTube frame until a real user click.
                        page.locator('[data-cv-seek="675"]').click()
                        frame=page.locator('.cv-embed-slot iframe')
                        assert frame.count()==1
                        assert 'youtube-nocookie.com/embed/R0GdEkPZSvM?start=675' in frame.get_attribute('src')
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                        page.locator('[data-cv-filter="soldi"]').click()
                        assert page.locator('.cv-card:visible').count()==1
                        assert page.locator('.cv-embed-slot iframe').count()==0
                        assert page.locator('[data-cv-filter="soldi"]').get_attribute('aria-pressed')=='true'
                        page.locator('[data-cv-filter="all"]').click()
                        assert page.locator('.cv-card:visible').count()==4
                        assert page.locator('.cv-embed-slot iframe').count()==0
                        if width in (390,1440):
                            shot=page.screenshot(
                                path=str(out/f'creator-video-hub-{width}.png'),
                                full_page=True,animations='disabled')
                            assert int.from_bytes(shot[16:20],'big')==width
                            print('CREATOR_VIDEO_HUB_FULL_PAGE_QA',width,
                                  int.from_bytes(shot[20:24],'big'),flush=True)
                    if path=='veicoli/':
                        cards=page.locator('[data-vc-card]')
                        assert cards.count()==32
                        assert page.locator('[data-vc-card]:visible').count()==12
                        assert page.locator('[data-vc-more]').is_visible()
                        page.locator('[data-vc-search]').fill('Futo')
                        assert page.locator('[data-vc-card]:visible').count()==1
                        assert page.locator('[data-vc-card]:visible h2').inner_text()=='Karin Futo'
                        page.locator('[data-vc-search]').fill('')
                        page.locator('[data-vc-filter-owner]').select_option('Esplorazione')
                        assert page.locator('[data-vc-card]:visible').count()==7
                        page.locator('[data-vc-filter-owner]').select_option('Moses')
                        assert page.locator('[data-vc-card]:visible').count()==8
                        page.locator('[data-vc-filter-status]').select_option('Verificata')
                        assert page.locator('[data-vc-card]:visible').count()==8
                        mark=page.locator('[data-vc-found="canis-crawler"]')
                        mark.click()
                        assert mark.get_attribute('aria-pressed')=='true'
                        page.reload(wait_until='load')
                        assert page.locator('[data-vc-found="canis-crawler"]').get_attribute('aria-pressed')=='true'
                        page.locator('[data-vc-filter-owner]').select_option('Moses')
                        page.locator('[data-vc-filter-status]').select_option('Verificata')
                        page.locator('[data-vc-todo]').check()
                        assert page.locator('[data-vc-card]:visible').count()==7
                        page.locator('[data-vc-todo]').uncheck()
                        page.locator('[data-vc-filter-owner]').select_option('Tutti')
                        page.locator('[data-vc-filter-status]').select_option('Tutte')
                        assert page.locator('[data-vc-card]:visible').count()==12
                        assert page.locator('[data-vc-more]').is_visible()
                        page.locator('[data-vc-more]').click()
                        assert page.locator('[data-vc-card]:visible').count()==24
                        page.locator('[data-vc-more]').click()
                        assert page.locator('[data-vc-card]:visible').count()==32
                        assert not page.locator('[data-vc-more]').is_visible()
                        if width in (390,1440):
                            page.evaluate('window.scrollTo(0,0)')
                            shot=page.screenshot(path=str(out/f'vehicles-directory-{width}.png'),
                                                 full_page=True,animations='disabled')
                            assert int.from_bytes(shot[16:20],'big')==width
                            print('VEHICLE_INDEX_FULL_PAGE_QA',width,
                                  int.from_bytes(shot[20:24],'big'),flush=True)
                    if path=='veicoli/declasse-yosemite-1500/':
                        assert page.locator('[data-vc-detail="declasse-yosemite-1500"]').count()==1
                        assert page.locator('.vc-instructions li').count()==4
                        assert 'Bastion Street' in page.locator('.vc-facts').inner_text()
                        assert '1.850 GTA$' in page.locator('.vc-facts').inner_text()
                        assert page.locator('.vc-social a[href*="intent/tweet"]').count()==1
                        assert page.locator('.vc-video a').count()==1
                        assert page.locator('[data-vc-load-video]').count()==1
                        assert page.locator('.vc-video-slot iframe').count()==0
                        if width in (390,1440):
                            shot=page.screenshot(path=str(out/f'vehicle-yosemite-article-{width}.png'),
                                                 full_page=True,animations='disabled')
                            assert int.from_bytes(shot[16:20],'big')==width
                            print('VEHICLE_ARTICLE_FULL_PAGE_QA',width,flush=True)
                        page.locator('[data-vc-load-video]').click()
                        assert page.locator('.vc-video-slot iframe').count()==1
                        assert 'start=101' in page.locator('.vc-video-slot iframe').get_attribute('src')
                    randy_areas={'pegassi-toros':'Southside','pegassi-vitello':'Waning Sands','pegassi-infernus':'Crosstown','pegassi-tempesta':'Vespucci Island','buckingham-windsor-drop':'Bayside','ocelot-jagular':'Belville','buckingham-jubilee':'Bayside','grotti-itali-rsx':'Bayside','pfister-growler':'Southside','gallivanter-baller-st-d':'Casanova Island','ascot-paragon':'Bayside','bravado-gauntlet-hellfire':'Capri','piccia-furia':'Vespucci Island','benefactor-dubsta':'Bayside','bravado-banshee':'Southside'}
                    if path in tuple('veicoli/'+slug+'/' for slug in randy_areas):
                        slug=path.split('/')[1]
                        assert page.locator('[data-vc-detail="'+slug+'"]').count()==1
                        assert page.locator('meta[name="robots"]').get_attribute('content')=='index,follow'
                        assert randy_areas[slug] in page.locator('.vc-facts').inner_text()
                        assert page.locator('.vc-instructions li').count()==5
                        assert page.locator('.vc-social a[href*="intent/tweet"]').count()==1
                        if width in (390,1440):
                            page.evaluate('window.scrollTo(0,0)')
                            page.screenshot(path=str(out/f'vehicle-{slug}-{width}.png'),full_page=True,animations='disabled')
                    if path in ('veicoli/declasse-akane-anime/','veicoli/annis-drifter-elegy/','veicoli/vapid-rocket-slamvan/'):
                        assert page.locator('.vc-instructions li').count()==5
                        assert page.locator('.vc-social-pending').count()==1
                        assert page.locator('.vc-source a').count()==2
                        assert page.locator('meta[name="robots"]').get_attribute('content')=='index,follow'
                        if width in (390,1440):
                            page.evaluate('window.scrollTo(0,0)')
                            page.screenshot(path=str(out/f'vehicle-{path.split("/")[1]}-{width}.png'),full_page=True,animations='disabled')
                    if path in ('veicoli/invetero-spiderweb-coquette/','veicoli/declasse-applesauce-bobcat/','veicoli/pfister-vanessas-growler/','veicoli/maibatsu-penumbra-ff-verde/'):
                        assert page.locator('.vc-instructions li').count()==5
                        assert page.locator('.vc-map a').count()==1
                        assert page.locator('.vc-social-pending').count()==1
                        assert page.locator('meta[name="robots"]').get_attribute('content')=='index,follow'
                        if width in (390,1440):
                            page.screenshot(path=str(out/f'vehicle-{path.split("/")[1]}-{width}.png'),full_page=True,animations='disabled')
                    if path=='veicoli/invetero-coquette-d10/':
                        assert page.locator('[data-vc-detail="invetero-coquette-d10"]').count()==1
                        assert page.locator('meta[name="robots"]').get_attribute('content')=='noindex,follow'
                        assert page.locator('.vc-social-pending').count()==1
                        assert page.locator('.vc-social').count()==0
                    if path=='immagini-ufficiali/':
                        # 189 source-attributed posters are separate from any walkthrough.
                        cards=page.locator('[data-rg-card]')
                        assert cards.count()==189
                        assert page.locator('[data-rg-card]:visible').count()==24
                        assert 'Rockstar Games' in page.locator('.rg-rights').inner_text()
                        assert not page.locator('.rg-card img').first.get_attribute('src').startswith(
                            '/gta-6/assets/rockstar/gta-vi/originals/')
                        page.locator('[data-rg-search]').fill('Port Gellhorn')
                        assert page.locator('[data-rg-card]:visible').count()==7
                        assert '7 immagini trovate' in page.locator('[data-rg-counter]').inner_text()
                        page.locator('[data-rg-filter]').select_option('Luoghi')
                        assert page.locator('[data-rg-card]:visible').count()==7
                        page.locator('[data-rg-search]').fill('impossibile-189')
                        assert page.locator('[data-rg-empty]').is_visible()
                        page.locator('[data-rg-search]').fill('')
                        page.locator('[data-rg-filter]').select_option('Personaggi')
                        assert page.locator('[data-rg-card]:visible').count()==24
                        page.locator('[data-rg-more]').click()
                        assert page.locator('[data-rg-card]:visible').count()==48
                        page.locator('[data-rg-filter]').select_option('Tutte')
                        assert page.locator('[data-rg-card]:visible').count()==24
                        if width in (390,1440):
                            # Place sticky navigation at the top in full-page QA output.
                            page.evaluate('window.scrollTo(0,0)')
                            img=page.screenshot(
                                path=str(out/f'rockstar-gallery-{width}.png'),
                                full_page=True,animations='disabled')
                            assert int.from_bytes(img[16:20],'big')==width
                            print('ROCKSTAR_GALLERY_QA',width,flush=True)
                    if path=='articoli/gta-vi-ultimate-edition-auto-garage/':
                        assert page.locator('.ed-section').count()==4
                        assert page.locator('.ed-photo img').count()==4
                        assert page.locator('.ed-related a[href$="/salvare-auto/"]').count()==1
                        if width in (390,1440):
                            for photo in page.locator('.ed-photo img').all():
                                photo.scroll_into_view_if_needed()
                                assert photo.evaluate('(i)=>i.complete && i.naturalWidth>0')
                            page.evaluate('window.scrollTo(0,0)')
                            page.screenshot(path=str(out/f'ultimate-car-editorial-{width}.png'),full_page=True,animations='disabled')
                    if page.locator('[data-article-cover]').count():
                        cover=page.locator('[data-article-cover] img')
                        assert cover.count()==1 and cover.is_visible()
                        assert page.locator('.ci-section-cover').count()==0
                        assert cover.evaluate('(i)=>i.complete && i.naturalWidth===1200 && i.naturalHeight===630')
                        assert cover.get_attribute('src')==page.locator('meta[property="og:image"]').get_attribute('content')
                        assert cover.get_attribute('src')==page.locator('meta[name="twitter:image"]').get_attribute('content')
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                    if page.locator('#procedura.v-tutorial').count():
                        assert page.locator('[data-article-cover]').count()==1
                        assert page.locator('.v-operation-brief').is_visible()
                        assert page.locator('.v-operation-brief dt').count()==3
                        assert page.locator('.v-operation-brief dd').count()==3
                        assert page.locator('.v-operation-brief').bounding_box()['y']<page.locator('#procedura').bounding_box()['y']
                    if path=='guide-e-tutorial/scansionare-veicoli/':
                        assert page.locator('#procedura .v-step').count()==5
                        assert page.locator('#procedura .v-check').count()==5
                        assert page.locator('.waink-tracker-warning').is_visible()
                        assert page.locator('.v-external-step-photo').count()==1
                        assert 'No Tracker' in page.locator('.waink-tracker-warning').inner_text()
                        assert 'Advanced' in page.locator('.waink-tracker-warning').inner_text()
                        assert page.locator('.v-guide-prep').count()==0
                        assert page.locator('.waink-instruction-art img').count()==5
                        assert page.locator('#passaggio-1 .waink-instruction-art img').is_visible()
                        assert page.locator('#passaggio-1 .waink-instruction-art img').evaluate('(img)=>img.complete && img.naturalWidth>0')
                        assert page.locator('.v-header').evaluate('(el)=>getComputedStyle(el).position')=='relative'
                        page.evaluate('window.scrollTo(0,0)')
                        page.wait_for_function('window.scrollY === 0')
                        intro=page.locator('.waink-main-player')
                        play=intro.locator('[data-step-video-open]')
                        assert play.is_visible()
                        assert intro.locator('iframe').count()==0
                        if width==390:
                            assert play.bounding_box()['y']<650,play.bounding_box()
                            first=page.locator('#passaggio-1').bounding_box()
                            diagram=page.locator('#passaggio-1 .waink-instruction-art img').bounding_box()
                            assert first and first['y']<1080,(first,diagram)
                            assert diagram and diagram['y']<1250,diagram
                            print('WAINK_INITIAL_VIEWPORT',first['y'],diagram['y'],flush=True)
                            page.screenshot(path=str(out/'waink-mobile-first-screen.png'))
                            page.locator('[data-theme-choice="light"]').click()
                            page.evaluate('window.scrollTo(0,0)')
                            page.wait_for_function('window.scrollY === 0')
                            assert page.locator('html').get_attribute('data-theme')=='light'
                            assert play.is_visible()
                            assert page.locator('#passaggio-1 .waink-instruction-art img').is_visible()
                            page.screenshot(path=str(out/'waink-mobile-first-screen-light.png'))
                            page.locator('[data-theme-choice="dark"]').click()
                        play.click()
                        assert intro.locator('iframe').get_attribute('src')=='https://www.youtube-nocookie.com/embed/0RBe_fz67gs?start=0&rel=0'
                        play.click()
                        assert intro.locator('iframe').count()==0
                        if width in (390,1440):
                            assert page.locator('.v-step:visible').count()==5
                            page.wait_for_function("""() => {
                              const images = [...document.querySelectorAll('.waink-instruction-art img')];
                              return images.length === 5 && images.every(i => i.complete && i.naturalWidth > 0);
                            }""")
                            page.evaluate('window.scrollTo(0,0)')
                            page.wait_for_function('window.scrollY === 0')
                            print('WAINK_ALL_IMAGES_LOADED',width,5,flush=True)
                            snap=page.screenshot(
                                path=str(out/f'waink-full-article-{width}.png'),
                                full_page=True,animations='disabled')
                            sw=int.from_bytes(snap[16:20],'big')
                            sh=int.from_bytes(snap[20:24],'big')
                            assert sw==width and sh>1250,(sw,sh)
                            assert page.locator('.gf-progress-track').count()==0
                            print('WAINK_FULL_PAGE_QA',width,sh,flush=True)
                    if path=='guide-e-tutorial/veicoli-per-moses/':
                        assert page.locator('#procedura .v-step').count()==7
                        assert page.locator('.mo-visual').count()==7
                        frames=page.locator('.mo-video-screen iframe')
                        buttons=page.locator('.mo-video-screen [data-step-video-open]')
                        assert frames.count()==0
                        assert buttons.count()==6 and page.locator('.mo-video-screen [data-step-video-open]:visible').count()==6
                        assert 'Moses’ Sultan' not in page.locator('.v-operation-brief').inner_text()
                        if width==390:
                            buttons.nth(0).click()
                            assert frames.count()==1
                            assert frames.first.get_attribute('src')=='https://www.youtube-nocookie.com/embed/UyxxY0A_kow?start=101&rel=0'
                            buttons.nth(1).click()
                            assert frames.count()==1
                            assert frames.first.get_attribute('src')=='https://www.youtube-nocookie.com/embed/UyxxY0A_kow?start=191&rel=0'
                            buttons.nth(1).click()
                            assert frames.count()==0
                        assert page.locator('.mo-photo-link').count()==6
                        assert page.locator('.mo-photo-link img').count()==0
                        assert page.locator('.mo-jump-link').count()==6
                        assert page.locator('.mo-microsteps').count()==7
                        assert page.locator('.mo-gift-reveal').count()==1
                        assert not page.locator('.mo-gift-reveal').evaluate('(el)=>el.open')
                        page.locator('.mo-gift-reveal summary').click()
                        assert page.locator('.mo-gift-reveal').evaluate('(el)=>el.open')
                        page.locator('.mo-gift-reveal summary').click()
                        assert page.locator('.v-operation-brief').is_visible()
                        assert page.locator('.v-guide-urgent').is_visible()
                        assert '2727' in page.locator('#passaggio-5').inner_text()
                        assert page.locator('.v-guide-more').count()==1
                        assert page.locator('.v-step:visible').count()==7,'Entire visual article must be shown'
                        assert page.locator('.mo-video-screen:visible').count()==6
                        assert page.locator('[data-mo-show-all]').count()==0
                        assert page.locator('.gf-progress-track').count()==0
                        assert page.locator('.v-guide-more').is_visible()
                        if width in (390,1440):
                            # Full-page proof, not a misleading 900px viewport crop.
                            png=page.screenshot(path=str(out/f'moses-full-article-{width}.png'),
                                                full_page=True, animations='disabled')
                            real_width=int.from_bytes(png[16:20],'big')
                            real_height=int.from_bytes(png[20:24],'big')
                            assert real_width==width and real_height>1500, (width,real_width,real_height)
                            print('MOSES_FULL_PAGE_QA',width,'height',real_height,flush=True)
                            if width==390:
                                page.locator('#passaggio-1').screenshot(
                                    path=str(out/'moses-step1-opt-in-390.png'))
                                page.locator('#passaggio-7').screenshot(
                                    path=str(out/'moses-gift-closed-390.png'))
                        page.reload(wait_until='load')
                        assert page.locator('.v-step:visible').count()==7
                        assert page.locator('.mo-video-screen iframe').count()==0
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                    if path=='guide-e-tutorial/soldi-facili-capitolo-1/':
                        assert page.locator('.cash-microsteps').count()==4
                        assert page.locator('.cash-microstep').count()==12
                        assert page.locator('.cash-critical-warning').is_visible()
                        assert 'Recalibration' in page.locator('.cash-critical-warning').inner_text()
                        assert 'Family Savings' in page.locator('.cash-critical-warning').inner_text()
                        assert page.locator('.v-external-step-photo').count()==4
                        assert page.locator('[data-step-external-evidence="map"]').count()==1
                        assert page.locator('[data-visual-location-image="liquor-store"]').count()==0
                        assert page.locator('#passaggio-1').count()==1
                        clips=page.locator('#procedura .v-step-video')
                        assert clips.count()==1
                        assert clips.first.get_attribute('data-step-video-seconds')=='285'
                        assert page.locator('.v-step-video-slot iframe').count()==0
                        play=page.locator('#passaggio-1 [data-step-video-open]')
                        assert play.is_visible()
                        play.click()
                        frame=page.locator('#passaggio-1 .v-step-video-slot iframe')
                        assert frame.count()==1
                        assert frame.get_attribute('src')=='https://www.youtube-nocookie.com/embed/1GtrjKhSwzM?start=285&rel=0'
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                        play.click()
                        assert frame.count()==0
                    if path=='salvare-auto/':
                        assert page.locator('.car-microsteps').count()==7
                        assert page.locator('.car-microstep').count()==21
                        assert page.locator('.car-story-warning').is_visible()
                        assert 'Scooter Bros si sblocca' in page.locator('.car-story-warning').inner_text()
                        assert 'Daily Driver' in page.locator('.car-story-warning').inner_text()
                        tracker=page.locator('#sblocchi-tracker')
                        assert tracker.is_visible()
                        assert 'Dale Mamba' in tracker.inner_text()
                        assert 'No Tracker' in tracker.inner_text() and 'Standard' in tracker.inner_text()
                        assert '16 consegne' in tracker.inner_text()
                        assert page.locator('[data-step-external-evidence="map"]').count()==1
                        assert page.locator('[data-step-external-evidence="video"]').count()==2
                        assert page.locator('[data-visual-proof-image="scooter-phone"]').count()==0
                        assert page.locator('.v-step').count()==7
                        refs=page.locator('.v-external-step-photo')
                        assert refs.count()==7
                        for i in range(refs.count()):
                            ref=refs.nth(i)
                            assert 'LINK ESTERNO' in ref.inner_text()
                            assert 'permesso di riutilizzo non è documentato' in ref.inner_text()
                            assert ref.locator('img').count()==0
                            assert ref.locator('a').get_attribute('target')=='_blank'
                        clips=page.locator('#procedura .v-step-video')
                        assert clips.count()==2
                        assert clips.first.get_attribute('data-step-video-seconds')=='266'
                        assert clips.nth(1).get_attribute('data-step-video-seconds')=='675'
                        assert page.locator('.v-step-video-slot iframe').count()==0
                        assert page.locator('[data-step-video-open]').first.get_attribute('hidden') is None
                        # All steps are visible; videos still load only on click.
                        assert page.locator('#passaggio-2').is_visible()
                        play=page.locator('#passaggio-2 [data-step-video-open]')
                        assert play.is_visible()
                        play.click()
                        frame=page.locator('#passaggio-2 .v-step-video-slot iframe')
                        assert frame.count()==1
                        assert frame.get_attribute('src')=='https://www.youtube-nocookie.com/embed/R0GdEkPZSvM?start=266&rel=0'
                        assert play.get_attribute('aria-expanded')=='true'
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                        if width==390:
                            page.locator('#passaggio-2').screenshot(path=str(out/'first-car-opt-in-video-390.png'))
                        play.click()
                        assert frame.count()==0
                        assert play.get_attribute('aria-expanded')=='false'
                        assert page.locator('#passaggio-1').is_visible()
                    if path=='guide-e-tutorial/soldi-2500-three-sheets-liquor/':
                        refs=page.locator('#procedura .v-external-step-photo')
                        assert refs.count()==2 and refs.nth(0).is_visible() and refs.nth(1).is_visible()
                        assert refs.locator('img').count()==0
                        assert page.locator('#procedura [data-visual-location-image]').count()==0
                        clips=page.locator('#procedura .v-step-video')
                        assert clips.count()==2
                        assert clips.first.get_attribute('data-step-video-seconds')=='285'
                        assert clips.nth(1).get_attribute('data-step-video-seconds')=='455'
                        assert page.locator('.v-step-video-slot iframe').count()==0
                        play=page.locator('#passaggio-1 [data-step-video-open]')
                        assert play.is_visible()
                        play.click()
                        frame=page.locator('#passaggio-1 .v-step-video-slot iframe')
                        assert frame.count()==1
                        assert frame.get_attribute('src')=='https://www.youtube-nocookie.com/embed/1GtrjKhSwzM?start=285&rel=0'
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                        play.click()
                        assert frame.count()==0
                        play=page.locator('#passaggio-3 [data-step-video-open]')
                        assert play.is_visible()
                        play.click()
                        frame=page.locator('#passaggio-3 .v-step-video-slot iframe')
                        assert frame.get_attribute('src')=='https://www.youtube-nocookie.com/embed/1GtrjKhSwzM?start=455&rel=0'
                        if width==390:
                            page.locator('#passaggio-3').screenshot(path=str(out/'three-sheets-opt-in-video-390.png'))
                        play.click()
                        assert frame.count()==0
                    if path in ('guide-e-tutorial/scansionare-veicoli/','guide-e-tutorial/glitch-prima-persona-ps5/'):
                        n,ident,second=(4,'R0GdEkPZSvM','266') if path.endswith('scansionare-veicoli/') else (6,'CJi2DWXxsoQ','0')
                        clips=page.locator('#procedura .v-step-video')
                        assert clips.count()==1
                        assert clips.first.get_attribute('data-step-video-seconds')==second
                        assert page.locator('.v-step-video-slot iframe').count()==0
                        play=page.locator(f'#passaggio-{n} [data-step-video-open]')
                        assert play.is_visible()
                        play.click()
                        frame=page.locator(f'#passaggio-{n} .v-step-video-slot iframe')
                        assert frame.count()==1
                        assert frame.get_attribute('src')=='https://www.youtube-nocookie.com/embed/'+ident+'?start='+second+'&rel=0'
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                        play.click()
                        assert frame.count()==0
                    if page.locator('#procedura.v-tutorial').count():
                        steps=page.locator('#procedura .v-step')
                        count=steps.count()
                        assert count>=3
                        assert page.locator('#procedura .v-step:visible').count()==count
                        assert page.locator('[data-gf-next],[data-gf-back],[data-gf-all],[data-mo-show-all]').count()==0
                        assert page.locator('.v-tutorial-finish').is_visible()
                        assert page.locator('.v-guide-more').is_visible()
                        assert not page.locator('details.v-guide-more').evaluate('(el)=>el.open')
                        if width in (390,1440) and path in ('salvare-auto/','guide-e-tutorial/soldi-facili-capitolo-1/','guide-e-tutorial/meditazione-capitolo-1/','guide-e-tutorial/soldi-2500-three-sheets-liquor/','guide-e-tutorial/glitch-prima-persona-ps5/','guide-e-tutorial/studiare-animali/','guide-e-tutorial/viaggio-rapido-taxi/','guide-e-tutorial/70-sfide-100-percento/','guide-e-tutorial/poligoni-concentrazione/','guide-e-tutorial/sportive-randy-posizioni/'):
                            page.evaluate('window.scrollTo(0,0)')
                            shot=page.screenshot(path=str(out/('linear-'+path.strip('/').replace('/','-')+'-'+str(width)+'.png')),full_page=True,animations='disabled')
                            assert int.from_bytes(shot[16:20],'big')==width
                            assert int.from_bytes(shot[20:24],'big')>1500
                        # Native anchor links scroll, never hide preceding/following steps.
                        if width==390:
                            page.evaluate("location.hash='#passaggio-2'")
                            assert page.locator('#procedura .v-step:visible').count()==count
                            page.evaluate("history.replaceState(null,'',location.pathname);window.scrollTo(0,0)")
                            print('LINEAR_ARTICLE_QA',path,count,flush=True)
                        page.locator('details.v-guide-more > summary').click()
                        assert page.locator('details.v-guide-more').evaluate('(el) => el.open')
                        if path=='salvare-auto/':
                            assert page.locator('#advanced-tracker-details').is_visible()
                            assert 'circa 5–7' in page.locator('#advanced-tracker-details').inner_text()
                        if path=='guide-e-tutorial/sportive-randy-posizioni/':
                            assert page.locator('[data-randy-completion="separate"]').is_visible()
                            assert page.locator('#randy-trophy-finale').is_visible()
                            assert 'Delivery Day' in page.locator('#randy-trophy-finale').inner_text()
                        if width in (390,1440) and path in ('salvare-auto/','guide-e-tutorial/70-sfide-100-percento/','guide-e-tutorial/poligoni-concentrazione/','guide-e-tutorial/sportive-randy-posizioni/'):
                            page.evaluate('window.scrollTo(0,0)')
                            page.screenshot(path=str(out/('extended-'+path.strip('/').replace('/','-')+'-'+str(width)+'.png')),full_page=True,animations='disabled')
                        if width in (390,1440) and path=='guide-e-tutorial/meditazione-capitolo-1/':
                            page.evaluate('window.scrollTo(0,0)')
                            page.screenshot(path=str(out/f'extended-meditation-{width}.png'),full_page=True,animations='disabled')
                    if path.endswith('soldi-2500-three-sheets-liquor/'):
                        assert page.locator('#mappa').is_visible()
                        assert page.locator('#consigli').is_visible()
                        assert page.locator('[data-spoiler-choice]').count()==0
                        assert page.locator('.v-spoiler-warning').count()>0
                        if page.locator('#mappa a.v-image-link').count():
                            page.locator('#mappa a.v-image-link').first.click()
                            assert page.locator('dialog[open]').count()==1
                            page.wait_for_function('document.querySelector("dialog img").naturalWidth>0')
                            page.locator('[data-image-zoom]').click()
                            assert page.locator('[data-image-viewport]').get_attribute('data-zoom')=='true'
                            page.keyboard.press('Escape');assert page.locator('dialog[open]').count()==0
                        if width==390:
                            page.locator('#mappa').scroll_into_view_if_needed();page.screenshot(path=str(out/'mobile-map-dark.png'))
                            page.locator('#consigli').scroll_into_view_if_needed();page.screenshot(path=str(out/'mobile-tips-dark.png'))
                    if path=='guide-e-tutorial/meditazione-capitolo-1/' and width==390:
                        checklist=page.locator('[data-meditation-tracker]')
                        assert checklist.count()==1
                        assert checklist.locator('[data-meditation-video-link]').count()==10
                        assert checklist.locator('#meditazione-luogo-ascent-mountain [data-meditation-video-link]').get_attribute('href')=='https://www.youtube.com/watch?v=WZ9EM_i_W38&t=377s'
                        assert page.locator('#passaggio-2 [data-step-video-open]').is_visible()
                        assert page.locator('#passaggio-6 [data-step-video-open]').is_visible()
                        assert page.locator('input[data-meditation-check]').count()==18
                        assert page.locator('[data-meditation-summary]').inner_text()=='0 / 18'
                        page.locator('#mt-jasons-house-one').check()
                        page.locator('#mt-smooth-sand-jason').check()
                        assert page.locator('[data-meditation-summary]').inner_text()=='2 / 18'
                        assert page.locator('[data-meditation-100]').inner_text()=='2 / 15'
                        assert page.locator('[data-meditation-house]').inner_text()=='Completata'
                        page.reload(wait_until='load')
                        assert page.locator('[data-meditation-summary]').inner_text()=='2 / 18'
                        assert page.locator('#mt-jasons-house-one').is_checked()
                        assert page.locator('#mt-smooth-sand-jason').is_checked()
                        page.locator('#meditazioni-checklist').scroll_into_view_if_needed()
                        page.screenshot(path=str(out/'mobile-meditations-checklist-dark.png'))
                        page.once('dialog',lambda dialog:dialog.accept())
                        page.locator('[data-meditation-reset]').click()
                        assert page.locator('[data-meditation-summary]').inner_text()=='0 / 18'
                        assert not page.locator('#mt-jasons-house-one').is_checked()
                    if path=='guide-e-tutorial/glitch-prima-persona-ps5/' and width==390:
                        assert page.locator('.v-glitch-status').is_visible()
                        warning=page.locator('[data-glitch-patch-status="community"]')
                        assert warning.is_visible()
                        assert 'dopo la patch del 23 novembre' in warning.inner_text()
                        assert warning.bounding_box()['y'] < page.locator('#procedura').bounding_box()['y']
                        page.locator('.v-glitch-status').screenshot(path=str(out/'glitch-post-patch-sources-390.png'))
                        assert page.locator('iframe[data-original-video-player]').count()==0
                        assert page.locator('.v-video-reference').count()==1
                        assert page.locator('.v-step').count()==6
                    if path=='salvare-auto/' and width==390:
                        # Third-party YouTube is never loaded merely by visiting.
                        assert page.locator('iframe[data-original-video-player]').count()==0
                        assert page.locator('[data-load-youtube]').count()==1
                        page.locator('details.v-video-reference > summary').click()
                        assert page.locator('iframe[data-original-video-player]').count()==0
                        page.locator('[data-load-youtube]').click()
                        iframe=page.locator('iframe[data-original-video-player]')
                        assert iframe.count()==1
                        assert iframe.get_attribute('src').startswith(
                            'https://www.youtube-nocookie.com/embed/R0GdEkPZSvM?start=675')
                    if path=='' and width in (390,1440):
                        page.wait_for_function("document.querySelector('[data-hero-slideshow]').dataset.heroIndex !== undefined")
                        assert page.locator('.ci-hero-image[data-hero-active="true"]').is_visible()
                        original=page.locator('[data-hero-slideshow]').get_attribute('data-hero-name')
                        page.get_by_role('button',name='Foto successiva',exact=True).click()
                        page.wait_for_function("""()=>{const a=document.querySelector('.ci-hero-image[data-hero-fade=true]'),b=document.querySelector('.ci-hero-image[data-hero-underlay=true]');if(!a||!b)return false;const x=getComputedStyle(a),y=getComputedStyle(b);return +x.opacity>0&&+x.opacity<1&&+y.opacity===1&&+x.zIndex>+y.zIndex&&a.naturalWidth>0&&b.naturalWidth>0}""")
                        page.wait_for_function("name => document.querySelector('[data-hero-slideshow]').dataset.heroName !== name",arg=original)
                        page.wait_for_function("!document.querySelector('[data-hero-fade=true],[data-hero-underlay=true]')")
                        print('HERO_CROSSFADE_OK',width,flush=True)
                        page.get_by_role('button',name='Foto precedente',exact=True).click()
                        page.wait_for_function("name => document.querySelector('[data-hero-slideshow]').dataset.heroName === name",arg=original)
                        page.locator('[data-hero-toggle]').click()
                        assert page.locator('[data-hero-toggle]').get_attribute('aria-pressed')=='true'
                        assert page.locator('[data-hero-slideshow]').get_attribute('data-hero-playing')=='false'
                        page.locator('[data-hero-toggle]').click()
                        assert page.locator('[data-hero-slideshow]').get_attribute('data-hero-playing')=='true'
                        if width==1440:
                            page.wait_for_function("name => document.querySelector('[data-hero-slideshow]').dataset.heroName !== name",arg=original,timeout=14000)
                            page.emulate_media(reduced_motion='reduce')
                            page.wait_for_function("document.querySelector('[data-hero-toggle]').getAttribute('aria-pressed') === 'true'")
                            assert page.locator('[data-hero-toggle]').get_attribute('aria-pressed')=='true'
                            assert page.locator('[data-hero-slideshow]').get_attribute('data-hero-playing')=='false'
                            page.emulate_media(reduced_motion='no-preference')
                        assert page.locator('.focus-choice').count()==3
                        for photo in page.locator('.ci-choice-image').all():
                            assert photo.bounding_box()['height'] < 350
                        page.get_by_role('tab',name='Leonida Keys',exact=True).click()
                        assert page.locator('#place-leonida-keys').is_visible()
                        assert page.locator('#place-vice-city').is_hidden()
                        page.get_by_role('tab',name='Vice City',exact=True).click()
                        page.locator('#inizio').scroll_into_view_if_needed()
                        page.screenshot(path=str(out/f'home-dark-{width}.png'))
                        page.locator('[data-theme-choice="light"]').click();page.screenshot(path=str(out/f'home-light-{width}.png'))
                        page.locator('[data-theme-choice="dark"]').click()
                    if path in ('trofei/trofeo-14-una-lunga-strada/',
                                'trofei/trofeo-17-cecchino/') and width in (390,1440):
                        assert page.locator('[data-trophy-beginner]').count()==1
                        assert page.locator('[data-trophy-beginner]').is_visible()
                        assert page.locator('.tg-goal').is_visible()
                        assert page.locator('.tg-finish [data-trophy-done]').is_visible()
                        assert page.locator('.trophy-art-wrap').is_hidden()
                        assert page.locator('.tg-extra:not([open])').count()==2
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                        button=page.locator('.tg-finish [data-trophy-done]')
                        button.click()
                        assert button.get_attribute('aria-pressed')=='true'
                        page.reload(wait_until='load')
                        assert button.get_attribute('aria-pressed')=='true'
                        button.click()
                        assert button.get_attribute('aria-pressed')=='false'
                        if width==390:
                            page.locator('.tg-goal').scroll_into_view_if_needed()
                            page.screenshot(path=str(out/('mobile-trophy-'+path.split('/')[1]+'.png')))
                        if path.endswith('trofeo-17-cecchino/'):
                            group=page.locator('details.tg-deep')
                            assert group.count()==1
                            assert not group.evaluate('(el)=>el.open')
                            group.locator(':scope > summary').click()
                            assert page.locator('input[data-medal-id]').count()==42
                            first=page.locator('input[data-medal-id]').first
                            first.check()
                            assert page.locator('[data-medal-count]').inner_text()=='1 / 42'
                            page.reload(wait_until='load')
                            page.locator('details.tg-deep > summary').click()
                            assert page.locator('input[data-medal-id]').first.is_checked()
                            page.once('dialog',lambda dialog:dialog.accept())
                            page.locator('[data-medal-reset]').click()
                            assert page.locator('[data-medal-count]').inner_text()=='0 / 42'
                    if path=='screenshot-ps5/':
                        cards=page.locator('.v-photo-hub-card')
                        assert cards.count()==11
                        assert page.locator('[data-visual-request-photo]').count()==55
                        assert page.locator('details.v-photo-hub-details[open]').count()==0
                        if width in (320,390):
                            first=page.locator('details.v-photo-hub-details').first
                            first.locator('summary').click()
                            assert first.get_attribute('open') is not None
                            assert first.locator('li.v-photo-hub-task').count()==5
                            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
                            page.screenshot(path=str(out/f'photo-hub-mobile-{width}.png'))
                            first.locator('summary').click()
                            assert first.get_attribute('open') is None
                    if path=='collezionabili/percorsi/' and width in (390,1440):
                        assert page.locator('[data-cr-step]').count()==123
                        assert page.locator('[data-cr-filter]').count()==10
                        assert page.locator('[data-cr-wizard]').count()==0
                        assert page.locator('[data-cr-step]:visible').count()==123
                        assert page.locator('.cr-hero').is_visible()
                        assert page.locator('.cr-priority-links a').count()==5
                        first=page.locator('#cr-pt-102')
                        assert first.locator('.cr-instruction-where').is_visible()
                        assert first.locator('.cr-instruction-do').is_visible()
                        assert first.locator('[data-cr-photo-state="source-only"]').count()==1
                        assert first.locator('[data-cr-photo-state="approved"]').count()==0
                        assert first.locator('.cr-photo-evidence > a').is_visible()
                        assert first.locator('.cr-photo-evidence > a').get_attribute('href').startswith('https://www.powerpyx.com/')
                        assert page.locator('[data-cr-progress]').inner_text().startswith('0 / 123')
                        first.locator('[data-cr-done]').check()
                        assert page.locator('[data-cr-progress]').inner_text().startswith('1 / 123')
                        page.reload(wait_until='load')
                        assert first.locator('[data-cr-done]').is_checked()
                        assert '1 / 123' in page.locator('[data-cr-progress]').inner_text()
                        assert page.locator('[data-cr-step]:visible').count()==123
                        assert page.locator('[data-cr-query]').is_visible()
                        page.locator('[data-cr-query]').fill('Victor Maravilla')
                        assert page.locator('[data-cr-step]:visible').count()==1
                        page.locator('[data-cr-query]').fill('')
                        assert page.locator('[data-cr-step]:visible').count()==123
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                        if width==390:
                            page.evaluate("window.scrollTo(0,0)")
                            page.screenshot(path=str(out/'mobile-collectibles-linear-390.png'))
                        print('LINEAR_COLLECTIBLES_QA',width,123,flush=True)
                    if path=='collezionabili/percorsi/' and width==390:
                        map_details=page.locator('details.cr-map-extra')
                        assert map_details.count()==1
                        assert not map_details.evaluate('(el)=>el.open')
                        viewer=page.locator('[data-vi-map]')
                        assert viewer.count()==1
                        assert viewer.locator('iframe').count()==0,'external map must not autoload'
                        map_details.locator(':scope > summary').click()
                        assert map_details.evaluate('(el)=>el.open')
                        viewer.locator('[data-vim-provider="city"]').click()
                        assert viewer.locator('iframe').count()==0
                        viewer.locator('[data-vim-load]').click()
                        frame=viewer.locator('iframe.vim-iframe')
                        assert frame.count()==1
                        assert frame.get_attribute('src')=='https://gta6.city/embed/map'
                        viewer.locator('[data-vim-provider="vice"]').click()
                        assert frame.get_attribute('src')=='https://vice-map.com/embed/map'
                        page.locator('#cr-pt-102 details.cr-step-extra > summary').click()
                        page.locator('#cr-pt-102 [data-vim-map-search]').click()
                        assert frame.get_attribute('src').startswith('https://vice-map.com/embed/map?marker=')
                        assert 'non è un pin esatto' in viewer.inner_text()
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                        viewer.scroll_into_view_if_needed()
                        page.screenshot(path=str(out/'mobile-interactive-map-390.png'))
                    if path=='screenshot-ps5/invia/' and width in (390,1440):
                        assert page.locator('template[data-pi-role-options]').evaluate(
                            "(el)=>el.content.querySelectorAll('[data-photo-guide]').length")==55
                        assert page.locator('[data-pi-role] option').count()==5
                        assert page.locator('[data-pi-submit]').is_disabled()
                        page.locator('[data-pi-credit]').fill('@samplephoto')
                        for flag in ('owner','rights','public'):
                            page.locator('[data-pi-'+flag+']').check()
                        assert page.locator('[data-pi-submit]').is_enabled()
                        assert page.locator('[data-pi-fallback]').is_hidden()
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                    if path=='screenshot-ps5/priorita/' and width in (390,1440):
                        tasks=page.locator('[data-pc-task]')
                        assert tasks.count()==55
                        assert page.locator('[data-pc-guide]').count()==11
                        page.locator('[data-pc-filter]').select_option('alta')
                        shown=page.locator('[data-pc-task]:visible').count()
                        assert 12<=shown<55
                        page.locator('[data-pc-filter]').select_option('all')
                        assert page.locator('[data-pc-task]:visible').count()==55
                        link=page.locator('[data-pc-task] a.pc-send').first
                        target=link.get_attribute('href')
                        assert '?guida=' in target and '&passo=' in target
                        assert '/screenshot-ps5/invia/' in target
                        # QA hosts canonical absolute links on localhost; compare the
                        # actual user-selected query without fetching external Pages.
                        page.goto(origin+'screenshot-ps5/invia/?'+target.split('?',1)[1],wait_until='load')
                        assert page.locator('[data-pi-guide]').input_value() in target
                        assert ('passo='+page.locator('[data-pi-role]').input_value()) in target
                        assert not page.locator('[data-pi-owner]').is_checked()
                        assert not page.locator('[data-pi-rights]').is_checked()
                        assert page.locator('[data-pi-submit]').is_disabled()
                    if path=='guide-e-tutorial/':
                        page.locator('[data-guide-search]').fill('taxi')
                        assert page.locator('[data-guide-searchable]:visible').count()==1
                    report.append(dict(width=width,path=path,themes=['dark','light'],persistence=True,no_overflow=True))
                assert not errors,errors
                context.close()
            for nojs,blocked in ((True,False),(False,True)):
                for width in (390,1440):
                    context=browser.new_context(java_script_enabled=not nojs,
                                                viewport={'width':width,'height':900},
                                                color_scheme='light')
                    bind(context)
                    if blocked:context.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('disabled')}})")
                    page=context.new_page();page.goto(origin,wait_until='load')
                    expected='dark'
                    self_theme=page.locator('html').get_attribute('data-theme')
                    assert self_theme==('auto' if nojs else expected),(width,nojs,self_theme)
                    expected_bg='rgb(16, 19, 29)'
                    assert page.evaluate('getComputedStyle(document.body).backgroundColor')==expected_bg
                    if nojs:
                        page.goto(origin+'articoli/',wait_until='load')
                        assert page.locator('[data-chronology-path]').count()==25
                        page.locator('[data-archive-pager] a.archive-next').click()
                        assert page.url.endswith('/articoli/pagina/2/')
                        assert page.locator('[data-chronology-path]').count()==25
                        page.locator('.archive-group-nav a').filter(has_text='Glitch ed exploit').click()
                        assert page.locator('[data-chronology-path]').count()==1
                        print('MAGAZINE_ARCHIVE_NO_JS_OK',width,flush=True)
                    if blocked:
                        page.locator('[data-theme-choice="dark"]').click()
                        assert page.locator('html').get_attribute('data-theme')=='dark'
                    context.close()
            browser.close()
    finally:
        server.shutdown();(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('READER_BROWSER_QA_OK',len(report),'page/width combinations; responsive themes; no-JS; blocked storage; visible spoilers+zoom')

if __name__=='__main__':
    if '--browser' in sys.argv:browser_qa()
    else:unittest.main()
