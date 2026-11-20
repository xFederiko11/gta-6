"""Regression tests for final production HTML and real-browser reader behavior."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import re
import sys
import unittest
from reader_experience import VERSION, validate, transform
from test_visual_site import Tags

ROOT = Path('_site')
BASE = 'https://xfederiko11.github.io/gta-6/'


class ReaderTests(unittest.TestCase):
    def test_all_pages_start_dark_before_stylesheets(self):
        for file in ROOT.rglob('*.html'):
            text = file.read_text(encoding='utf-8')
            self.assertIn('<html lang="it" data-theme="dark">',text,str(file))
            self.assertIn('id="reader-theme-boot"',text,str(file))
            self.assertLess(text.index('id="reader-theme-boot"'),text.index('rel="stylesheet"'),str(file))
            self.assertNotIn('<meta name="color-scheme" content="light">',text)
            self.assertIn('reader-theme.css?v=',text)
            if 'data-design-version=' in text:
                self.assertEqual(text.count('data-theme-choice="dark"'),1)
                self.assertEqual(text.count('data-theme-choice="light"'),1)

    def test_release_and_idempotence(self):
        release=json.loads((ROOT/'design-version.json').read_text())
        self.assertEqual(release['default_theme'],'dark')
        self.assertEqual(release['reader_version'],VERSION)
        self.assertEqual(release['guides_with_extras'],5)
        self.assertEqual(release['tip_count'],9)
        page=(ROOT/'salvare-auto/index.html').read_text()
        self.assertEqual(transform(page,version='anything'),page)

    def test_tips_sourced_and_native_spoilers_closed(self):
        data=json.loads(Path('data/guide_extras.json').read_text())
        self.assertTrue(validate(data))
        for path, entry in data['guides'].items():
            text=(ROOT/path/'index.html').read_text()
            self.assertEqual(text.count('class="r-tip"'),len(entry['tips']))
            self.assertEqual(text.count('id="consigli"'),1)
            tags=Tags();tags.feed(text)
            panels=[a for t,a in tags.tags if t=='details' and 'data-spoiler' in a]
            self.assertTrue(all('open' not in a for a in panels))
            if entry['spoiler']:
                panel=re.search(r'<details class="v-spoiler" data-spoiler>(.*?)</details>',text,re.S)
                self.assertIsNotNone(panel)
                self.assertIn('id="consigli"',panel[1])
                self.assertIn('id="mappa"',panel[1])
                self.assertIn('Consigli e curiosità (spoiler)',text)
            for tip in entry['tips']:
                self.assertIn(tip['source'],text)
            ids=[a['id'] for t,a in tags.tags if 'id' in a]
            self.assertEqual(len(ids),len(set(ids)),path)

    def test_reject_unsafe_sources_and_missing_spoiler_classification(self):
        original=json.loads(Path('data/guide_extras.json').read_text())
        for bad in ['http://www.powerpyx.com/a/','https://www.powerpyx.com.evil.test/a/','https://user@www.powerpyx.com/a/']:
            data=copy.deepcopy(original)
            next(iter(data['guides'].values()))['tips'][0]['source']=bad
            with self.assertRaises(ValueError): validate(data)
        data=copy.deepcopy(original)
        del next(iter(data['guides'].values()))['spoiler']
        with self.assertRaises(ValueError): validate(data)

    def test_no_screenshot_inversion_or_network_calls(self):
        css=Path('site/assets/reader-theme.css').read_text()
        js=Path('site/assets/reader-theme.js').read_text()
        self.assertNotIn('filter:invert',css.replace(' ',''))
        self.assertNotIn('brightness(',css)
        self.assertIn('gta6-theme-v1',js)
        self.assertNotIn("setItem('gta6-spoilers",js)
        self.assertNotIn('fetch(',js)
        self.assertNotIn('prefers-color-scheme',js)
        self.assertIn('showModal()',js)
        self.assertIn('event.ctrlKey',js)

    def test_reviewed_details_not_contradicted_by_guide(self):
        taxi=(ROOT/'guide-e-tutorial/viaggio-rapido-taxi/index.html').read_text()
        self.assertIn('in aggiunta alla tariffa della corsa',taxi)
        self.assertNotIn('un costo di 100 GTA$ per il servizio',taxi)
        garage=(ROOT/'salvare-auto/index.html').read_text()
        self.assertIn('sblocchi successivi',garage)
        self.assertNotIn("Porta l&#x27;auto che vuoi conservare dentro un Pay",garage)


def browser_qa():
    import os
    import shutil
    import threading
    from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
    from urllib.parse import urlsplit, unquote
    from playwright.sync_api import sync_playwright
    directory=ROOT.resolve(); out=Path('reader-qa');out.mkdir(exist_ok=True)
    class Handler(SimpleHTTPRequestHandler):
        def translate_path(self,path):
            clean=unquote(urlsplit(path).path).removeprefix('/gta-6/')
            target=(directory/clean.lstrip('/')).resolve()
            return str(target if target.is_relative_to(directory) else directory/'missing')
        def do_GET(self):
            target=Path(self.translate_path(self.path))
            if target.is_dir(): target=target/'index.html'
            if target.is_file() and target.suffix in ('.html','.css','.js'):
                raw=target.read_text(encoding='utf-8').replace(BASE,origin).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type',{'.html':'text/html; charset=utf-8','.css':'text/css','.js':'application/javascript'}[target.suffix])
                self.send_header('Content-Length',str(len(raw)))
                self.end_headers();self.wfile.write(raw)
            else: super().do_GET()
        def log_message(self,*args): pass
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
                    if req.request.url.startswith(origin): req.continue_()
                    else: req.abort()
                context.route('**/*',route)
            for width in (320,390,768,1440):
                context=browser.new_context(viewport={'width':width,'height':900},color_scheme='light')
                bind(context);page=context.new_page();errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                paths=['','salvare-auto/','guide-e-tutorial/soldi-2500-three-sheets-liquor/','trofei/','hdr-oled/','trucchi/','scoperte/','guide-e-tutorial/']
                for path in paths:
                    page.goto(origin+path,wait_until='load')
                    if path=='':
                        assert page.locator('html').get_attribute('data-theme')=='dark','fresh light OS must default dark'
                    for theme in ('light','dark'):
                        page.locator(f'[data-theme-choice="{theme}"]').click()
                        assert page.locator('html').get_attribute('data-theme')==theme
                        expected='rgb(12, 11, 19)' if theme=='dark' else 'rgb(252, 248, 252)'
                        assert page.evaluate('getComputedStyle(document.body).backgroundColor')==expected,(path,theme)
                        page.reload(wait_until='load')
                        assert page.locator('html').get_attribute('data-theme')==theme,'persistence'
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),(width,path,theme,'overflow')
                    if path.endswith('soldi-2500-three-sheets-liquor/'):
                        assert not page.locator('#mappa').is_visible()
                        assert not page.locator('#consigli').is_visible()
                        page.locator('[data-spoiler-choice="show"]').click()
                        assert page.locator('#consigli').is_visible()
                        page.locator('#mappa a.v-image-link').first.click()
                        assert page.locator('dialog[open]').count()==1
                        page.wait_for_function('document.querySelector("dialog img").naturalWidth>0')
                        page.locator('[data-image-zoom]').click()
                        assert page.locator('[data-image-viewport]').get_attribute('data-zoom')=='true'
                        page.keyboard.press('Escape')
                        assert page.locator('dialog[open]').count()==0
                        if width==390:
                            page.locator('#mappa').scroll_into_view_if_needed()
                            page.screenshot(path=str(out/'mobile-map-dark.png'))
                            page.locator('#consigli').scroll_into_view_if_needed()
                            page.screenshot(path=str(out/'mobile-tips-dark.png'))
                        page.locator('[data-spoiler-choice="hide"]').click()
                        assert not page.locator('#consigli').is_visible()
                        assert page.locator('html').get_attribute('data-theme')=='dark'
                    if path=='' and width in (390,1440):
                        page.screenshot(path=str(out/f'home-dark-{width}.png'))
                        page.locator('[data-theme-choice="light"]').click()
                        page.screenshot(path=str(out/f'home-light-{width}.png'))
                        page.locator('[data-theme-choice="dark"]').click()
                    if path=='guide-e-tutorial/':
                        page.locator('[data-guide-search]').fill('taxi')
                        assert page.locator('[data-guide-searchable]:visible').count()==1
                    report.append(dict(width=width,path=path,themes=['dark','light'],persistence=True,no_overflow=True))
                assert not errors,errors
                context.close()
            for nojs,blocked in ((True,False),(False,True)):
                context=browser.new_context(java_script_enabled=not nojs,color_scheme='light')
                bind(context)
                if blocked: context.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('disabled')}})")
                page=context.new_page();page.goto(origin,wait_until='load')
                assert page.locator('html').get_attribute('data-theme')=='dark'
                assert page.evaluate('getComputedStyle(document.body).backgroundColor')=='rgb(12, 11, 19)'
                if blocked:
                    page.locator('[data-theme-choice="light"]').click()
                    assert page.locator('html').get_attribute('data-theme')=='light'
                context.close()
            browser.close()
    finally:
        server.shutdown()
        (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('READER_BROWSER_QA_OK',len(report),'page/width combinations; both themes; no-JS; blocked storage; spoiler+zoom')


if __name__=='__main__':
    if '--browser' in sys.argv: browser_qa()
    else: unittest.main()
