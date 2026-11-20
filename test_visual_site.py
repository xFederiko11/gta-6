"""Regression checks on the actual visual production output, not just legacy HTML."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json
import re
import unittest
import xml.etree.ElementTree as ET

ROOT=Path('_site')
BASE='https://xfederiko11.github.io/gta-6/'

class Tags(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]; self.scripts=[]; self.json=False; self.buf=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); self.tags.append((tag,a))
        if tag=='script' and a.get('type')=='application/ld+json': self.json=True; self.buf=[]
    def handle_data(self,data):
        if self.json: self.buf.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.json:
            self.scripts.append(json.loads(''.join(self.buf))); self.json=False

def parse(path):
    text=path.read_text(encoding='utf-8'); tags=Tags(); tags.feed(text); return text,tags

class VisualSiteTests(unittest.TestCase):
    def test_design_release_marker(self):
        release=json.loads((ROOT/'design-version.json').read_text())
        self.assertEqual(release['version'],'visual-v2-20261120')
        self.assertGreaterEqual(release['guides'],10)
        self.assertGreaterEqual(release['image_assets'],10)

    def test_home_is_real_new_layout(self):
        text,tags=parse(ROOT/'index.html')
        self.assertIn('v-hero',text)
        self.assertIn('giri a vuoto',text)
        self.assertNotIn('Tutto GTA 6.<br>',text)
        self.assertNotIn('128.941',text)
        self.assertNotIn('50 guide',text)
        self.assertIn('/soldi-facili/',text)
        self.assertIn('/auto-speciali/',text)
        self.assertIn('/salvare-auto/',text)
        self.assertGreaterEqual(sum((t=='img' and 'data-visual-image' in a) or (t=='div' and 'data-media-missing' in a) for t,a in tags.tags),8)

    def test_sitemap_pages_exist_keep_canonicals_and_one_h1(self):
        root=ET.parse(ROOT/'sitemap.xml').getroot()
        locs=[x.text for x in root.iter() if x.tag.endswith('loc')]
        self.assertEqual(len(locs),len(set(locs)))
        for loc in locs:
            self.assertTrue(loc.startswith(BASE))
            target=ROOT/loc.removeprefix(BASE)/'index.html'
            self.assertTrue(target.is_file(),str(target))
            text,tags=parse(target)
            self.assertEqual(sum(t=='h1' for t,a in tags.tags),1,str(target))
            canonical=[a['href'] for t,a in tags.tags if t=='link' and a.get('rel')=='canonical']
            self.assertEqual(canonical,[loc],str(target))
            self.assertIn('data-design-version="visual-v2-20261120"',text)
            self.assertTrue(tags.scripts,str(target))
            self.assertTrue(any(t=='meta' and a.get('name')=='description' for t,a in tags.tags),str(target))
            self.assertIn('visual-v2.css?v=',text)
            self.assertIn('visual-v2.js?v=',text)
        for path in ('soldi-facili/','auto-speciali/','salvare-auto/','guide-e-tutorial/sportive-randy-posizioni/'):
            self.assertIn(BASE+path,locs)

    def test_existing_guides_are_preserved_and_rewritten(self):
        data=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
        for guide in data:
            page=ROOT/'guide-e-tutorial'/guide['id']/'index.html'
            text,tags=parse(page)
            self.assertIn('v-step-head',text)
            self.assertEqual(text.count('class="v-step"'),len(guide['steps']))
            self.assertIn('id="fonti"',text)
            self.assertIn(guide['source_url'].replace('&','&amp;'),text)
        self.assertEqual(len(list((ROOT/'trofei').glob('trofeo-*/index.html'))),55)

    def test_guides_show_spoilers_directly_with_clear_warning(self):
        for path in ('guide-e-tutorial/soldi-facili-capitolo-1/','guide-e-tutorial/soldi-2500-three-sheets-liquor/','guide-e-tutorial/sportive-randy-posizioni/'):
            text,tags=parse(ROOT/path/'index.html')
            self.assertFalse(any(t=='details' and 'data-spoiler' in a for t,a in tags.tags))
            self.assertIn('v-spoiler-warning',text)
            self.assertIn('Attenzione spoiler',text)
            self.assertNotIn('Mostra spoiler',text)
            self.assertNotIn('data-spoiler-choice=',text)
            self.assertIn('id="procedura"',text)

    def test_header_x_link_and_primary_shortcuts_on_every_page(self):
        for target in (ROOT/'index.html',ROOT/'salvare-auto/index.html',ROOT/'trofei/index.html'):
            text,tags=parse(target)
            self.assertIn('class="v-x-link"',text)
            self.assertIn('href="https://x.com/xFederiko11"',text)
            self.assertIn('aria-label="Segui Federiko su X"',text)
            for path in ('soldi-facili/','auto-speciali/','salvare-auto/'):
                self.assertIn(BASE+path,text)
        html=(ROOT/'index.html').read_text()
        self.assertLess(html.index('class="v-categories"'),html.index('class="v-hero"'))

    def test_screenshots_have_real_provenance(self):
        manifest=json.loads(Path('data/visual_media.json').read_text(encoding='utf-8'))['images']
        for key,item in manifest.items():
            self.assertEqual(urlsplit(item['url']).scheme,'https')
            self.assertEqual(urlsplit(item['source']).scheme,'https')
            self.assertIn(item['kind'],('screenshot','promotional'))
            self.assertTrue(item['alt']); self.assertTrue(item['credit'])
            self.assertNotIn('imagegen',item['url'])
        for path in ('salvare-auto/','guide-e-tutorial/soldi-2500-three-sheets-liquor/'):
            text,tags=parse(ROOT/path/'index.html')
            images=[a for t,a in tags.tags if t=='img' and 'data-visual-image' in a]
            unavailable=[a for t,a in tags.tags if t=='div' and 'data-media-missing' in a]
            self.assertGreaterEqual(len(images)+len(unavailable),3)
            for a in images:
                self.assertIn('alt',a); self.assertIn('width',a); self.assertIn('height',a)
                self.assertIn('loading',a)
                self.assertIn('/gta-6/assets/visual/',a['src'])
                self.assertTrue((ROOT/a['src'].split('/gta-6/',1)[1]).is_file())
            for a in unavailable:
                self.assertIn('aria-label',a)

    def test_internal_links_and_assets_do_not_point_to_ghost_pages(self):
        for target in ROOT.rglob('index.html'):
            text,tags=parse(target)
            for t,a in tags.tags:
                value=a.get('href' if t=='a' else 'src','')
                if not value.startswith(BASE): continue
                rel=unquote(urlsplit(value).path.removeprefix('/gta-6/'))
                local=ROOT/rel
                if value.split('?',1)[0].split('#',1)[0].endswith('/'):
                    local=local/'index.html'
                self.assertTrue(local.exists(),f'{target}: {value}')

    def test_no_credentials_or_external_mutations_in_client(self):
        script=Path('site/assets/visual-v2.js').read_text()
        for token in ('api.buffer.com','Authorization','createPost','innerHTML','fetch('):
            self.assertNotIn(token,script)
        self.assertNotIn('data-spoiler-choice',script)
        self.assertIn('aria-pressed',script)
        self.assertIn('prefers-reduced-motion',Path('site/assets/visual-v2.css').read_text())

if __name__=='__main__': unittest.main()
