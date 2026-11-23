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
        self.assertIn("1 · Guide pratiche",page)
        self.assertIn("2 · Trofei e platino",page)
        self.assertIn("3 · Scoperte community",page)
        self.assertIn("/gta-6/guide-e-tutorial/",page)
        self.assertIn("/gta-6/trofei/",page)
        self.assertIn("/gta-6/scoperte/",page)
        self.assertIn("Novità: distinguiamo le fonti",page)
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

    def test_no_private_material_copied_to_public_site(self):
        from public_release_gate import PRIVATE_PREFIXES, PRIVATE_FILES
        for prefix in PRIVATE_PREFIXES:
            self.assertFalse((SITE/prefix).exists(),prefix)
        for filename in PRIVATE_FILES:
            self.assertFalse((SITE/filename).exists(),filename)

if __name__=="__main__":
    unittest.main()
