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

    def test_chronology_and_strict_glitch_archive(self):
        from article_chronology_v1 import inventory,GLITCH
        rows=inventory()
        dated=[r for r in rows if r[3]]
        self.assertEqual([r[3] for r in dated],sorted([r[3] for r in dated],reverse=True))
        home=(SITE/"index.html").read_text(encoding="utf-8")
        index=(SITE/"articoli/index.html").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r'data-chronology-path="([^"]+)"',home),[r[0] for r in dated[:12]])
        self.assertEqual(re.findall(r'data-chronology-path="([^"]+)"',index),[r[0] for r in rows])
        self.assertEqual(re.findall(r'data-chronology-path="([^"]+)"',(SITE/"glitch/index.html").read_text(encoding="utf-8")),[GLITCH])
        for path,*_ in rows:self.assertTrue((SITE/path/"index.html").is_file(),path)
        self.assertEqual(len({r[0] for r in rows}),len(rows))
        self.assertGreater(len(rows),120)
        self.assertEqual({r[2] for r in rows if r[2]=="Glitch"},{"Glitch"})
        self.assertIn('data-chronology-filters hidden',index)
        self.assertIn('article-chronology-v1.js?v=',index)
        self.assertIn('data-chronology-search',index)
        self.assertIn('data-chronology-filter',index)

    def test_documented_publication_history(self):
        import json
        from article_chronology_v1 import inventory
        registry=json.loads(Path("data/publication_dates_v1.json").read_text(encoding="utf-8"))
        dated=registry["published"]
        evidence={p:g["publication_day_rome"] for g in registry["evidence"] for p in g["paths"]}
        self.assertEqual(dated,evidence)
        self.assertEqual(len(dated),sum(len(g["paths"]) for g in registry["evidence"]))
        self.assertGreaterEqual(len(dated),151)
        self.assertEqual(dated["trofei/medaglie-oro/"],"2026-11-18")
        self.assertEqual(dated["garage-gratuiti/garage-storia/port-gellhorn/"],"2026-11-27")
        rows=inventory()
        self.assertEqual({p:d for p,t,c,d in rows if p in dated},dated)

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
