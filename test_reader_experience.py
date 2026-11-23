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
    def test_11_guides_use_single_step_wizard_without_hiding_content_from_no_js(self):
        guides=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
        guides+=json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides']
        self.assertEqual(len(guides),11)
        css=Path('site/assets/guide-flow-v1.css').read_text(encoding='utf-8')
        js=Path('site/assets/guide-flow-v1.js').read_text(encoding='utf-8')
        self.assertIn('[data-gf-next]',js)
        self.assertIn('[data-gf-back]',js)
        self.assertIn('HO FINITO IL TUTORIAL',js)
        self.assertIn('scrollIntoView',js)
        self.assertIn('aria-current',js)
        self.assertIn('gf-done',css)
        self.assertNotIn('fetch(',js)
        self.assertNotIn('localStorage',js)
        for guide in guides:
            path=guide.get('canonical_path') or 'guide-e-tutorial/'+guide['id']+'/'
            html=(ROOT/path/'index.html').read_text(encoding='utf-8')
            with self.subTest(guide=guide['id']):
                self.assertIn('guide-flow-v1.css?v=',html)
                self.assertIn('guide-flow-v1.js?v=',html)
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
        self.assertEqual(release['tip_count'],9)
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
                paths=['','salvare-auto/','guide-e-tutorial/veicoli-per-moses/','guide-e-tutorial/soldi-2500-three-sheets-liquor/','guide-e-tutorial/meditazione-capitolo-1/','guide-e-tutorial/glitch-prima-persona-ps5/','trofei/','trofei/trofeo-14-una-lunga-strada/','trofei/trofeo-17-cecchino/','hdr-oled/','trucchi/','scoperte/','screenshot-ps5/','collezionabili/percorsi/','screenshot-ps5/invia/','screenshot-ps5/priorita/','guide-e-tutorial/']
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
                    if page.locator('#procedura.v-tutorial').count():
                        assert page.locator('.v-operation-brief').is_visible()
                        assert page.locator('.v-operation-brief dt').count()==3
                        assert page.locator('.v-operation-brief dd').count()==3
                        assert page.locator('.v-operation-brief').bounding_box()['y']<page.locator('#procedura').bounding_box()['y']
                    if path=='guide-e-tutorial/veicoli-per-moses/':
                        assert page.locator('#procedura .v-step').count()==7
                        assert page.locator('.mo-visual').count()==7
                        assert page.locator('.mo-video-screen iframe').count()==6
                        assert page.locator('.mo-video-screen iframe').first.get_attribute('src').startswith(
                            'https://www.youtube-nocookie.com/embed/UyxxY0A_kow?start=101')
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
                        assert page.locator('html').evaluate('(el)=>el.classList.contains("guide-flow-all")')
                        assert not page.locator('.gf-progress-track').is_visible(), 'Full article is not 100% complete'
                        assert page.locator('.gf-progress-track').get_attribute('aria-valuenow') is None
                        assert page.locator('[data-mo-show-all]').is_visible()
                        assert page.locator('[data-mo-show-all]').get_attribute('aria-pressed')=='true'
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
                                    path=str(out/'moses-step1-with-video-390.png'))
                                page.locator('#passaggio-7').screenshot(
                                    path=str(out/'moses-gift-closed-390.png'))
                        page.locator('[data-mo-show-all]').click()
                        assert page.locator('.v-step:visible').count()==1
                        assert page.locator('.gf-progress-track').is_visible()
                        assert page.locator('.gf-progress-track').get_attribute('aria-valuenow')=='1'
                        assert page.locator('[data-mo-show-all]').get_attribute('aria-pressed')=='false'
                        assert not page.locator('.v-guide-more').is_visible()
                        page.locator('[data-mo-show-all]').click()
                        assert page.locator('.v-step:visible').count()==7
                        assert not page.locator('.gf-progress-track').is_visible()
                        assert page.locator('.v-guide-more').is_visible()
                        assert page.locator('[data-mo-show-all]').get_attribute('aria-pressed')=='true'
                        assert page.evaluate('location.hash===""')
                        page.reload(wait_until='load')
                        assert page.locator('.v-step:visible').count()==7
                        assert page.locator('.mo-video-screen iframe').count()==6
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                    if path=='salvare-auto/':
                        refs=page.locator('.v-external-step-photo')
                        assert refs.count()>=1
                        for i in range(refs.count()):
                            ref=refs.nth(i)
                            assert 'LINK ESTERNO' in ref.inner_text()
                            assert 'permesso di riutilizzo non è documentato' in ref.inner_text()
                            assert ref.locator('img').count()==0
                            assert ref.locator('a').get_attribute('target')=='_blank'
                    if page.locator('details.v-guide-more').count() and path!='guide-e-tutorial/veicoli-per-moses/':
                        # The beginner experience is a WIZARD, not an article full
                        # of unrelated boxes. Only one numbered step visible.
                        steps=page.locator('#procedura .v-step')
                        count=steps.count()
                        assert count>=3
                        assert page.locator('.v-tutorial-start-here').is_visible()
                        assert page.locator('.gf-progress').is_visible()
                        assert page.locator('[data-gf-status]').inner_text()=='PASSO 1 DI '+str(count)
                        assert page.locator('.v-step:visible').count()==1
                        assert page.locator('#passaggio-1').is_visible()
                        assert page.locator('.gf-next').is_visible()
                        assert not page.locator('.gf-back').is_visible()
                        assert not page.locator('.v-guide-more').is_visible(),'Extras must be hidden during task mode'
                        assert page.locator('.v-tutorial-finish').is_hidden()
                        if width==390:
                            first=page.locator('#passaggio-1').bounding_box()
                            assert first and first['y']<900,(path,'first numbered step below mobile viewport',first)
                            page.screenshot(path=str(out/('tutorial-first-'+path.strip('/').replace('/','-')+'.png')))
                            print('GUIDED_MOBILE_FIRST_STEP',path,round(first['y']),flush=True)
                            page.locator('[data-gf-next]').click()
                            assert page.locator('.v-step:visible').count()==1
                            assert page.locator('#passaggio-1').is_hidden()
                            assert page.locator('#passaggio-2').is_visible()
                            assert page.locator('[data-gf-status]').inner_text()=='PASSO 2 DI '+str(count)
                            assert page.locator('.gf-back').is_visible()
                            page.locator('[data-gf-back]').click()
                            assert page.locator('#passaggio-1').is_visible()
                            assert page.locator('.gf-back').is_hidden()
                            # Read all remains an explicit accessible alternative.
                            page.locator('[data-gf-all]').click()
                            assert page.locator('.v-step:visible').count()==count
                            assert page.locator('.v-guide-more').is_visible()
                            page.locator('[data-gf-all]').click()
                            assert page.locator('.v-step:visible').count()==1
                            assert page.locator('#passaggio-1').is_visible()
                            # End-to-end beginner flow, including extra materials
                            # which appear only when the procedure is completed.
                            for n in range(count):
                                assert page.locator('.v-step:visible').count()==1
                                assert page.locator('#passaggio-'+str(n+1)).is_visible()
                                page.locator('[data-gf-next]').click()
                            assert page.locator('.gf-done').is_visible()
                            assert page.locator('.gf-next').is_hidden()
                            assert page.locator('.v-guide-more').is_visible()
                            page.screenshot(path=str(out/('tutorial-finished-'+path.strip('/').replace('/','-')+'.png')))
                            print('GUIDED_MOBILE_COMPLETE',path,count,flush=True)
                        assert page.evaluate('''() => {
                            const first=document.querySelector('#passaggio-1');
                            const extras=document.querySelector('details.v-guide-more');
                            return first && extras && !!(first.compareDocumentPosition(extras) & Node.DOCUMENT_POSITION_FOLLOWING);
                        }''')
                        if width!=390:
                            # Reach completion for all widths, then inspect extras.
                            for n in range(count):
                                page.locator('[data-gf-next]').click()
                            assert page.locator('.gf-done').is_visible()
                        page.locator('details.v-guide-more > summary').click()
                        assert page.locator('details.v-guide-more').evaluate('(el) => el.open')
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
                        assert page.locator('[data-cr-wizard]').is_visible()
                        assert page.locator('[data-cr-step]:visible').count()==1
                        assert page.locator('.cr-wizard-item [data-cr-step]').get_attribute('id')=='cr-pt-102'
                        assert 'PRIORITÀ' in page.locator('[data-cr-wizard-help]').inner_text()
                        assert page.locator('.cr-wizard-item .cr-instruction-where').is_visible()
                        assert page.locator('.cr-wizard-item .cr-instruction-do').is_visible()
                        assert page.locator('.cr-wizard-item [data-cr-photo-state="source-only"]').count()==1
                        assert page.locator('.cr-wizard-item [data-cr-photo-state="approved"]').count()==0
                        assert page.locator('.cr-wizard-item .cr-photo-evidence > a').is_visible()
                        assert page.locator('.cr-wizard-item .cr-photo-evidence > a').get_attribute('href').startswith('https://www.powerpyx.com/')
                        assert not page.locator('.cr-hero').is_visible()
                        if width==390:
                            pos=page.locator('.cr-wizard-item .cr-instruction-where').bounding_box()
                            assert pos and pos['y']<850,(path,'first real action too far down',pos)
                            photo=page.locator('.cr-wizard-item .cr-photo-evidence').bounding_box()
                            done=page.locator('[data-cr-wizard-found]').bounding_box()
                            assert photo and done and photo['y']<done['y'],'source link should be before done action'
                        # Skip does not claim an object collected; back returns.
                        page.locator('[data-cr-wizard-skip]').click()
                        assert page.locator('.cr-wizard-item [data-cr-step]').get_attribute('id')=='cr-pt-103'
                        assert page.locator('[data-cr-progress]').inner_text().startswith('0 / 123')
                        page.locator('[data-cr-wizard-back]').click()
                        assert page.locator('.cr-wizard-item [data-cr-step]').get_attribute('id')=='cr-pt-102'
                        page.locator('[data-cr-wizard-found]').click()
                        assert page.locator('.cr-wizard-item [data-cr-step]').get_attribute('id')=='cr-pt-103'
                        assert page.locator('[data-cr-progress]').inner_text().startswith('1 / 123')
                        page.reload(wait_until='load')
                        assert page.locator('.cr-wizard-item [data-cr-step]').get_attribute('id')=='cr-pt-103'
                        assert '1 / 123' in page.locator('[data-cr-progress]').inner_text()
                        page.locator('[data-cr-wizard-toggle]').click()
                        assert page.locator('[data-cr-step]:visible').count()==123
                        assert page.locator('[data-cr-query]').is_visible()
                        page.locator('[data-cr-query]').fill('Victor Maravilla')
                        assert page.locator('[data-cr-step]:visible').count()==1
                        page.locator('[data-cr-query]').fill('')
                        assert page.locator('[data-cr-step]:visible').count()==123
                        page.locator('[data-cr-wizard-toggle]').click()
                        assert page.locator('[data-cr-step]:visible').count()==1
                        assert page.locator('.cr-wizard-item [data-cr-step]').get_attribute('id')=='cr-pt-103'
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                        if width==390:
                            page.screenshot(path=str(out/'mobile-collectibles-one-checkpoint-390.png'))
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
                        page.locator('.cr-wizard-item details.cr-step-extra > summary').click()
                        page.locator('.cr-wizard-item [data-vim-map-search]').first.click()
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
