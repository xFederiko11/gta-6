"""Photo delivery, navigation and evidence boundaries for the new visual site."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import unittest
from PIL import Image
import cinematic_site as c


class Images(HTMLParser):
    def __init__(self):
        super().__init__();self.images=[];self.anchors=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='img' and 'data-promotional-media' in a:self.images.append(a)
        if tag=='a' and a.get('href'):self.anchors.append(a['href'])


class CinematicTests(unittest.TestCase):
    def test_home_photos_are_light_local_attributed_and_distinct(self):
        root=Path('_site');page=(root/'index.html').read_text(encoding='utf-8')
        parser=Images();parser.feed(page)
        self.assertEqual(len(parser.images),15)
        self.assertGreaterEqual(len({i['src'] for i in parser.images}),12)
        self.assertEqual(sum(i['loading']=='eager' for i in parser.images),1)
        self.assertEqual(parser.images[0]['fetchpriority'],'high')
        for image in parser.images:
            self.assertIn('Rockstar Games',image['alt'])
            self.assertIn('srcset',image)
            self.assertNotIn('data-visual-image',image)
            rel=unquote(urlsplit(image['src']).path.removeprefix('/gta-6/'))
            file=root/rel
            self.assertTrue(file.is_file(),rel)
            self.assertLess(file.stat().st_size,350_000)
        self.assertFalse((root/'assets/rockstar/gta-vi/originals').exists())

    def test_every_discovery_destination_exists(self):
        root=Path('_site');page=(root/'index.html').read_text(encoding='utf-8')
        parser=Images();parser.feed(page)
        for link in parser.anchors:
            if not link.startswith(c.BASE):continue
            path=urlsplit(link).path.removeprefix('/gta-6/')
            if path.endswith('/'):
                self.assertTrue((root/path/'index.html').is_file(),link)
        for slug,*_ in c.PLACES:
            self.assertIn('id="place-'+slug+'"',page)
            self.assertIn('aria-controls="place-'+slug+'"',page)
        self.assertIn('prefers-reduced-motion',Path('site/assets/cinematic-v3.css').read_text())

    def test_first_screen_links_to_indexable_car_save_guide(self):
        """GSC car-saving queries should reach the precise article in one click."""
        import xml.etree.ElementTree as ET
        root=Path('_site')
        page=(root/'index.html').read_text(encoding='utf-8')
        target='https://xfederiko11.github.io/gta-6/guide-e-tutorial/registrare-auto-personale/'
        self.assertIn('href="'+target+'">Come salvare un’auto in GTA 6</a>',page)
        self.assertIn('Come salvare le auto in GTA VI',page)
        self.assertEqual(page.count('class="focus-choice"'),3)
        self.assertTrue((root/'guide-e-tutorial/registrare-auto-personale/index.html').exists())
        body=(root/'guide-e-tutorial/registrare-auto-personale/index.html').read_text(encoding='utf-8')
        self.assertIn('<link rel="canonical" href="'+target+'"',body)
        self.assertNotIn('name="robots" content="noindex',body)
        sitemap=ET.parse(root/'sitemap.xml')
        self.assertIn(target,[x.text for x in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')])

    def test_landing_pages_have_contextual_covers(self):
        for path in c.COVERS:
            page=(Path('_site')/path/'index.html').read_text(encoding='utf-8')
            self.assertIn('class="ci-section-cover"',page,path)
            self.assertIn('Immagine promozionale ufficiale',page,path)

    def test_slideshow_has_twenty_real_responsive_originals(self):
        import json,re
        page=Path('_site/index.html').read_text(encoding='utf-8')
        raw=re.search(r'<script type="application/json" id="hero-slides">(.*?)</script>',page).group(1)
        slides=json.loads(raw)
        self.assertEqual(len(slides),20)
        self.assertEqual(len({s['name'] for s in slides}),20)
        self.assertNotIn('Jason_and_Lucia_03.jpg',{s['name'] for s in slides})
        for slide in slides:
            rel=unquote(urlsplit(slide['src']).path.removeprefix('/gta-6/'))
            self.assertTrue((Path('_site')/rel).is_file())
            self.assertIn('Rockstar Games',slide['alt'])
        self.assertIn('data-hero-toggle',page)
        self.assertIn('data-hero-prev',page)
        self.assertIn('data-hero-next',page)


if __name__=='__main__':unittest.main()
