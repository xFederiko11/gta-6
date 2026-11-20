"""Browser QA of real generated HTML. No social publishing or user credentials."""
from __future__ import annotations
import json
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import threading
from urllib.parse import urlsplit,unquote
from playwright.sync_api import sync_playwright

ROOT=Path('_site').resolve()
OUTPUT=Path('visual-qa'); OUTPUT.mkdir(exist_ok=True)
BASE='https://xfederiko11.github.io/gta-6/'

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        clean=unquote(urlsplit(path).path)
        if clean.startswith('/gta-6/'): clean=clean[len('/gta-6/'):]
        dest=(ROOT/clean.lstrip('/')).resolve()
        if not dest.is_relative_to(ROOT): return str(ROOT/'missing')
        return str(dest)
    def log_message(self,*args): pass

server=ThreadingHTTPServer(('127.0.0.1',8765),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
report=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch()
        for width,height,label in [(1440,1000,'desktop'),(390,844,'mobile'),(768,1024,'tablet')]:
            context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1)
            def local_route(route):
                request=route.request.url
                relative=request.removeprefix(BASE)
                response=route.fetch(url='http://127.0.0.1:8765/gta-6/'+relative)
                route.fulfill(response=response)
            context.route(BASE+'**',local_route)
            page=context.new_page()
            errors=[]; page.on('pageerror',lambda error:errors.append(str(error)))
            pages=[('','home'),('salvare-auto/','garage'),('guide-e-tutorial/soldi-2500-three-sheets-liquor/','money')]
            for path,name in pages:
                page.goto(BASE+path,wait_until='networkidle',timeout=60000)
                assert page.locator('h1').count()==1,(label,name,'heading')
                assert page.locator('body').get_attribute('data-design-version')=='visual-v2-20261120'
                if name=='money':
                    panel=page.locator('details[data-spoiler]')
                    assert panel.count()==1
                    assert panel.get_attribute('open') is None,'Spoiler initially exposed'
                    page.locator('[data-spoiler-choice="show"]').click()
                    assert panel.get_attribute('open') is not None,'Spoiler toggle failed'
                    page.reload(wait_until='networkidle')
                    assert page.locator('details[data-spoiler]').get_attribute('open') is not None,'Spoiler preference not persisted'
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(800)
                page.evaluate('window.scrollTo(0, 0)')
                page.wait_for_timeout(600)
                overflow=page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
                assert not overflow,(label,name,'horizontal overflow')
                stats=page.locator('img[data-visual-image]').evaluate_all('(images)=>({total:images.length,loaded:images.filter(i=>i.complete&&i.naturalWidth>0).length,failed:images.filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.src)})')
                if label=='desktop' and name=='home': assert stats['loaded']>0,'No genuine home images loaded'
                page.screenshot(path=str(OUTPUT/f'{label}-{name}.png'),full_page=True)
                report.append({'viewport':label,'page':path,'no_horizontal_overflow':True,'images':stats})
                if name=='money':
                    page.locator('[data-spoiler-choice="hide"]').click()
                    assert page.locator('details[data-spoiler]').get_attribute('open') is None
            page.goto(BASE+'guide-e-tutorial/',wait_until='networkidle')
            page.locator('[data-guide-filter="garage"]').click()
            visible=page.locator('[data-guide-searchable]:visible').count()
            assert visible==1,('garage filter',visible)
            page.locator('[data-guide-filter="all"]').click()
            page.locator('[data-guide-search]').fill('taxi')
            assert page.locator('[data-guide-searchable]:visible').count()>=1
            page.locator('[data-guide-search]').fill('zznonexistentzz')
            assert page.locator('[data-guide-searchable]:visible').count()==0
            assert 'Nessuna guida' in page.locator('[data-guide-result]').inner_text()
            if label=='mobile':
                page.locator('.v-menu summary').click()
                assert page.locator('.v-menu[open] nav').is_visible()
                page.keyboard.press('Escape')
                assert page.locator('.v-menu').get_attribute('open') is None
            assert not errors,errors
            context.close()
        browser.close()
finally:
    server.shutdown()
    (OUTPUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('VISUAL_BROWSER_QA_OK',json.dumps(report))
