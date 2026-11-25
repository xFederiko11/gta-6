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
                paths=['','salvare-auto/','guide-e-tutorial/veicoli-per-moses/','guide-e-tutorial/soldi-facili-capitolo-1/','guide-e-tutorial/scansionare-veicoli/','guide-e-tutorial/soldi-2500-three-sheets-liquor/','guide-e-tutorial/meditazione-capitolo-1/','guide-e-tutorial/glitch-prima-persona-ps5/','trofei/','trofei/trofeo-14-una-lunga-strada/','trofei/trofeo-17-cecchino/','hdr-oled/','hdr-oled/lg-oled-c4/','hdr-oled/samsung-s90f/','trucchi/','scoperte/','screenshot-ps5/','collezionabili/percorsi/','screenshot-ps5/invia/','screenshot-ps5/priorita/','immagini-ufficiali/','video-tutorial/','veicoli/','veicoli/declasse-yosemite-1500/','veicoli/pegassi-toros/','guide-e-tutorial/']
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
                        assert cards.count()==25
                        assert page.locator('[data-vc-card]:visible').count()==12
                        assert page.locator('[data-vc-more]').is_visible()
                        page.locator('[data-vc-search]').fill('Futo')
                        assert page.locator('[data-vc-card]:visible').count()==1
                        assert page.locator('[data-vc-card]:visible h2').inner_text()=='Karin Futo'
                        page.locator('[data-vc-search]').fill('')
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
                        assert page.locator('[data-vc-card]:visible').count()==25
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
                    if path=='veicoli/pegassi-toros/':
                        assert page.locator('[data-vc-detail="pegassi-toros"]').count()==1
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
                    if page.locator('#procedura.v-tutorial').count():
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
                        intro=page.locator('.waink-main-player')
                        play=intro.locator('[data-step-video-open]')
                        assert play.is_visible()
                        assert intro.locator('iframe').count()==0
                        if width==390:
                            assert play.bounding_box()['y']<420,play.bounding_box()
                            page.screenshot(path=str(out/'waink-mobile-first-screen.png'))
                        play.click()
                        assert intro.locator('iframe').get_attribute('src')=='https://www.youtube-nocookie.com/embed/0RBe_fz67gs?start=0&rel=0'
                        play.click()
                        assert intro.locator('iframe').count()==0
                        if width in (390,1440):
                            page.locator('[data-gf-all]').click()
                            assert page.locator('.v-step:visible').count()==5
                            snap=page.screenshot(
                                path=str(out/f'waink-full-article-{width}.png'),
                                full_page=True,animations='disabled')
                            sw=int.from_bytes(snap[16:20],'big')
                            sh=int.from_bytes(snap[20:24],'big')
                            assert sw==width and sh>1250,(sw,sh)
                            assert not page.locator('.gf-progress-track').is_visible()
                            page.locator('[data-gf-all]').click()
                            assert page.locator('.v-step:visible').count()==1
                            print('WAINK_FULL_PAGE_QA',width,sh,flush=True)
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
                        # The reader is initially on step 1. Nothing is fetched
                        # from YouTube before the reader opens step 2 and clicks.
                        page.locator('[data-gf-next]').click()
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
                        page.locator('[data-gf-back]').click()
                        assert page.locator('#passaggio-1').is_visible()
                    if path=='guide-e-tutorial/soldi-2500-three-sheets-liquor/':
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
                        page.locator('[data-gf-next]').click()
                        page.locator('[data-gf-next]').click()
                        play=page.locator('#passaggio-3 [data-step-video-open]')
                        assert play.is_visible()
                        play.click()
                        frame=page.locator('#passaggio-3 .v-step-video-slot iframe')
                        assert frame.get_attribute('src')=='https://www.youtube-nocookie.com/embed/1GtrjKhSwzM?start=455&rel=0'
                        if width==390:
                            page.locator('#passaggio-3').screenshot(path=str(out/'three-sheets-opt-in-video-390.png'))
                        play.click()
                        assert frame.count()==0
                        page.locator('[data-gf-back]').click()
                        page.locator('[data-gf-back]').click()
                    if path in ('guide-e-tutorial/scansionare-veicoli/','guide-e-tutorial/glitch-prima-persona-ps5/'):
                        n,ident,second=(4,'R0GdEkPZSvM','266') if path.endswith('scansionare-veicoli/') else (6,'CJi2DWXxsoQ','0')
                        clips=page.locator('#procedura .v-step-video')
                        assert clips.count()==1
                        assert clips.first.get_attribute('data-step-video-seconds')==second
                        assert page.locator('.v-step-video-slot iframe').count()==0
                        for _ in range(n-1):
                            page.locator('[data-gf-next]').click()
                        play=page.locator(f'#passaggio-{n} [data-step-video-open]')
                        assert play.is_visible()
                        play.click()
                        frame=page.locator(f'#passaggio-{n} .v-step-video-slot iframe')
                        assert frame.count()==1
                        assert frame.get_attribute('src')=='https://www.youtube-nocookie.com/embed/'+ident+'?start='+second+'&rel=0'
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                        play.click()
                        assert frame.count()==0
                        for _ in range(n-1):
                            page.locator('[data-gf-back]').click()
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
                        if path=='guide-e-tutorial/soldi-facili-capitolo-1/' and width in (390,1440):
                            page.locator('[data-gf-all]').click()
                            assert page.locator('.v-step:visible').count()==4
                            png=page.screenshot(
                                path=str(out/f'chapter1-money-full-article-{width}.png'),
                                full_page=True,animations='disabled')
                            png_w=int.from_bytes(png[16:20],'big')
                            png_h=int.from_bytes(png[20:24],'big')
                            assert png_w==width and png_h>1500,(png_w,png_h)
                            assert not page.locator('.gf-progress-track').is_visible()
                            print('CHAPTER1_MONEY_FULL_PAGE_QA',width,png_h,flush=True)
                            page.locator('[data-gf-all]').click()
                            assert page.locator('.v-step:visible').count()==1
                        if path=='salvare-auto/' and width in (390,1440):
                            # Capture and assert the entire edited tutorial, not a cropped viewport.
                            page.locator('[data-gf-all]').click()
                            assert page.locator('.v-step:visible').count()==7
                            shot=page.screenshot(path=str(out/f'first-car-full-article-{width}.png'),
                                                 full_page=True,animations='disabled')
                            png_w=int.from_bytes(shot[16:20],'big')
                            png_h=int.from_bytes(shot[20:24],'big')
                            assert png_w==width and png_h>1700,(width,png_w,png_h)
                            assert not page.locator('.gf-progress-track').is_visible()
                            print('FIRST_CAR_FULL_PAGE_QA',width,png_h,flush=True)
                            page.locator('[data-gf-all]').click()
                            assert page.locator('.v-step:visible').count()==1
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
                        page.wait_for_function("document.querySelector('[data-hero-slideshow]').dataset.heroIndex !== undefined")
                        assert page.locator('.ci-hero-image[data-hero-active="true"]').is_visible()
                        original=page.locator('[data-hero-slideshow]').get_attribute('data-hero-name')
                        page.get_by_role('button',name='Foto successiva',exact=True).click()
                        page.wait_for_function("name => document.querySelector('[data-hero-slideshow]').dataset.heroName !== name",arg=original)
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
