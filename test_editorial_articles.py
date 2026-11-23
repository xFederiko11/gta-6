"""Verify the imported originals and real article/catalog output, offline."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from html.parser import HTMLParser
import hashlib
import json
import unittest
import editorial_articles as editorial


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images=[]
    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.images.append(dict(attrs))


class EditorialTests(unittest.TestCase):
    def test_all_originals_match_the_supplied_archive_hashes(self):
        library, articles, images=editorial.load()
        self.assertEqual(len(images),189)
        for row in library['assets']:
            data=(editorial.LIBRARY/row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(),row['sha256'],row['file'])
            self.assertEqual(len(data),row['bytes'])
        self.assertNotIn('/Users/',json.dumps(library))

    def test_article_and_gallery_use_real_local_photographs(self):
        root=Path('_site')
        if not (root/'articoli').is_dir():
            self.skipTest('Generated site not available')
        _,articles,_=editorial.load()
        article=articles[0]
        page=(root/article['path']/'index.html').read_text(encoding='utf-8')
        parser=Images();parser.feed(page)
        photos=[im for im in parser.images if '/assets/rockstar/' in im.get('src','')]
        self.assertEqual(len(photos),6)
        self.assertEqual(len({p['src'] for p in photos}),6)
        self.assertEqual(page.count('<h1'),1)
        self.assertIn('"datePublished":"2026-11-24"',page)
        for image in photos:
            rel=unquote(urlsplit(image['src']).path.removeprefix('/gta-6/'))
            self.assertTrue((root/rel).is_file(),rel)
            self.assertIn('Rockstar',image['alt'])
            self.assertIn('srcset',image)
        gallery=(root/editorial.GALLERY_PATH/'index.html').read_text(encoding='utf-8')
        self.assertEqual(gallery.count('data-library-card '),189)
        self.assertIn('content="noindex,follow"',gallery)
        sitemap=(root/'sitemap.xml').read_text(encoding='utf-8')
        self.assertIn(article['path'],sitemap)
        home=(root/'index.html').read_text(encoding='utf-8')
        self.assertIn(article['path'],home)

    def test_x_draft_uses_four_distinct_originals_and_stays_a_draft(self):
        draft=json.loads(Path('editorial/x/gta-vi-leonida-sei-luoghi.json').read_text(encoding='utf-8'))
        self.assertEqual(draft['status'],'draft')
        self.assertEqual(len(draft['images']),4)
        self.assertEqual(len({im['file'] for im in draft['images']}),4)
        import re
        weighted=re.sub(r'https?://\S+','x'*23,draft['text'])
        self.assertLessEqual(len(weighted)+1,280)
        for image in draft['images']:
            self.assertTrue(Path(image['file']).is_file())
            self.assertTrue(image['alt'])


if __name__=='__main__':
    unittest.main()
