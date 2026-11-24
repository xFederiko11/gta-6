"""Phase one GTA VI Italia redesign: calm entry points, no broken flow."""
from pathlib import Path
import re
import unittest

SITE=Path("_site")

class SimpleHomeTests(unittest.TestCase):
    def test_three_immediate_destinations_without_public_operations(self):
        page=(SITE/"index.html").read_text(encoding="utf-8")
        self.assertIn('id="focus-title"',page)
        self.assertEqual(len(re.findall(r"<h1(?:\s|>)",page)),1)
        self.assertEqual(page.count('class="focus-choice"'),3)
        self.assertIn("Guide pratiche",page)
        self.assertIn("Trofei e platino",page)
        self.assertIn("Scoperte community",page)
        self.assertIn("/gta-6/guide-e-tutorial/",page)
        self.assertIn("/gta-6/trofei/",page)
        self.assertIn("/gta-6/scoperte/",page)
        self.assertIn("Fonti chiare, curiosità accesa.",page)
        self.assertIn('https://www.rockstargames.com/newswire',page)
        self.assertEqual(page.count('class="focus-quick"'),1)
        self.assertIn('guide-e-tutorial/veicoli-per-moses/',page)
        self.assertIn('site-focus-v1.css?v=',page)
        self.assertNotIn('class="social-home-rail"',page)
        self.assertNotIn('class="v-photo-hub-invite"',page)
        self.assertNotIn('class="v-promo',page)
        self.assertNotIn('class="v-spoilerbar"',page)
        self.assertNotIn("data-visual-image",page)
        self.assertNotIn("gta-v142-publication-global",page)
        self.assertNotIn("REDDIT-LEAD",page)
        self.assertNotIn("data-admin",page)
        self.assertIn("rel=\"canonical\"",page)

    def test_does_not_break_published_deep_links_or_source_labels(self):
        for path in ("guide-e-tutorial/veicoli-per-moses/",
                     "salvare-auto/","trofei/","scoperte/",
                     "collezionabili/percorsi/","hdr-oled/"):
            with self.subTest(path=path):
                page=(SITE/path/"index.html").read_text(encoding="utf-8")
                self.assertIn("<h1",page)
                self.assertIn('rel="canonical"',page)
        moses=(SITE/"guide-e-tutorial/veicoli-per-moses/index.html").read_text(encoding="utf-8")
        self.assertEqual(moses.count('data-mo-real-gameplay='),6)
        self.assertIn('Fonte video: IGN su YouTube',moses)
        self.assertIn('Guarda anche le foto sulla guida PowerPyx',moses)
        community=(SITE/"scoperte/index.html").read_text(encoding="utf-8")
        self.assertIn("segnalazioni",community.lower())

    def test_private_material_is_excluded_by_release_gate(self):
        # The staged _site still holds QA reports. The release firewall
        # removes them immediately before publishing, not before unit tests.
        from public_release_gate import PRIVATE_PREFIXES, PRIVATE_FILES
        self.assertIn('crescita-x/',PRIVATE_PREFIXES)
        self.assertIn('photo-backlog-v5.json',PRIVATE_FILES)
        home=(SITE/'index.html').read_text(encoding='utf-8')
        for private in (*PRIVATE_PREFIXES,*PRIVATE_FILES):
            self.assertNotIn(private,home)
        self.assertNotIn('data-admin',home)

if __name__=="__main__":
    unittest.main()
