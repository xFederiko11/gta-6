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
                paths=['','salvare-auto/','guide-e-tutorial/soldi-2500-three-sheets-liquor/','guide-e-tutorial/meditazione-capitolo-1/','guide-e-tutorial/glitch-prima-persona-ps5/','trofei/','hdr-oled/','trucchi/','scoperte/','screenshot-ps5/','collezionabili/percorsi/','screenshot-ps5/invia/','guide-e-tutorial/']
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
                        page.on('dialog',lambda dialog:dialog.accept())
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
                        assert page.locator('[data-cr-step]').count()==76
                        assert page.locator('[data-cr-filter]').count()==6
                        page.locator('[data-cr-query]').fill('Victor Maravilla')
                        assert page.locator('[data-cr-step]:visible').count()==1
                        page.locator('[data-cr-query]').fill('')
                        page.locator('[data-cr-done]').first.check()
                        assert '1 / 76' in page.locator('[data-cr-progress]').inner_text()
                        page.reload(wait_until='load')
                        assert page.locator('[data-cr-done]').first.is_checked()
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
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
