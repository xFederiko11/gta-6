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

    def test_landing_pages_have_contextual_covers(self):
        for path in c.COVERS:
            page=(Path('_site')/path/'index.html').read_text(encoding='utf-8')
            self.assertIn('class="ci-section-cover"',page,path)
            self.assertIn('Immagine promozionale ufficiale',page,path)


if __name__=='__main__':unittest.main()
