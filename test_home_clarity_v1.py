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
        from article_chronology_v1 import inventory,GLITCH,PAGE_SIZE,specs,tree,taxonomy,BASE,CATALOG
        rows=inventory()
        dated=[r for r in rows if r[3]]
        self.assertEqual([r[3] for r in dated],sorted([r[3] for r in dated],reverse=True))
        home=(SITE/"index.html").read_text(encoding="utf-8")
        index=(SITE/"articoli/index.html").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r'data-chronology-path="([^"]+)"',home),[r[0] for r in rows[:PAGE_SIZE]])
        self.assertEqual(re.findall(r'data-chronology-path="([^"]+)"',index),[r[0] for r in rows[:PAGE_SIZE]])
        import json,xml.etree.ElementTree as ET
        sitemap={n.text for n in ET.parse(SITE/"sitemap.xml").iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
        catalog=json.loads((SITE/CATALOG).read_text(encoding="utf-8"))
        self.assertEqual(catalog["page_size"],25)
        self.assertEqual([x["path"] for x in catalog["items"]],[r[0] for r in rows])
        self.assertEqual(catalog["groups"],tree(rows))
        self.assertEqual(len(tree(rows)),8)
        self.assertEqual(sum(g["count"] for g in tree(rows)),len(rows))
        self.assertEqual(sum(s["count"] for g in tree(rows) for s in g["children"]),len(rows))
        self.assertEqual({taxonomy(r)[0] for r in rows if r[2]=="Glitch"},{"glitch"})
        self.assertEqual({taxonomy(r)[0] for r in rows if r[2]=="Trucchi"},{"trucchi"})
        all_archive=[]
        for group,sub,n,path,indexable,selected in specs(rows):
            page=(SITE/path/"index.html").read_text(encoding="utf-8")
            expected=selected[(n-1)*PAGE_SIZE:n*PAGE_SIZE]
            actual=re.findall(r'data-chronology-path="([^"]+)"',page)
            self.assertEqual(actual,[r[0] for r in expected],path)
            self.assertLessEqual(len(actual),PAGE_SIZE)
            self.assertIn('rel="canonical" href="'+BASE+path+'"',page)
            self.assertEqual(BASE+path in sitemap,indexable,path)
            self.assertIn('data-archive-pager',page)
            if not group:all_archive.extend(actual)
            if n*PAGE_SIZE<len(selected):
                self.assertIn("Avanti",page)
            if not indexable:self.assertIn('name="robots" content="noindex,follow"',page)
        self.assertEqual(all_archive,[r[0] for r in rows])
        for item in catalog["items"]:
            self.assertTrue(item["summary"],item["path"])
            if item["secret"]:self.assertFalse(item["image"])
            if item["image"]:
                self.assertTrue((SITE/item["image"]).is_file(),item["image"])
                self.assertEqual(item["credit"],"Screenshot autorizzato · crediti nella guida")
                from PIL import Image
                with Image.open(SITE/item["image"]) as img:
                    self.assertEqual(img.size,(480,252) if item["image"].endswith(".webp") else (1200,630))
        self.assertEqual(re.findall(r'data-chronology-path="([^"]+)"',(SITE/"glitch/index.html").read_text(encoding="utf-8")),[GLITCH])
        for path,*_ in rows:self.assertTrue((SITE/path/"index.html").is_file(),path)
        self.assertEqual(len({r[0] for r in rows}),len(rows))
        self.assertGreater(len(rows),120)
        self.assertEqual({r[2] for r in rows if r[2]=="Glitch"},{"Glitch"})
        self.assertIn('data-chronology-filters hidden',index)
        self.assertIn('article-chronology-v1.js?v=',index)
        self.assertIn('data-chronology-search',index)
        self.assertIn('data-chronology-filter',index)

    def test_magazine_seo_titles_and_priority_links(self):
        from html import unescape
        from article_chronology_v1 import archive_metadata,specs,BASE
        titles=set()
        descriptions=set()
        for group,sub,n,path,indexable,rows in specs():
            page=(SITE/path/"index.html").read_text(encoding="utf-8")
            title,desc=archive_metadata(group,sub,n)
            self.assertEqual(unescape(re.search(r"<title>(.*?)</title>",page,re.S).group(1)),title)
            self.assertEqual(unescape(re.search(r'<meta name="description" content="([^"]+)">',page).group(1)),desc)
            self.assertNotIn(title,titles,path)
            self.assertNotIn(desc,descriptions,path)
            titles.add(title);descriptions.add(desc)
            self.assertEqual(len(re.findall(r"<h1(?:\s|>)",page)),1)
            if group and n==1:
                self.assertIn('aria-label="Percorsi consigliati"',page,path)
        guide=(SITE/"guide-e-tutorial/index.html").read_text(encoding="utf-8")
        self.assertIn('data-editorial-route="salvare-auto"',guide)
        self.assertIn('href="'+BASE+'salvare-auto/"',guide)
        self.assertIn('href="'+BASE+'articoli/categoria/veicoli/"',guide)
        print("MAGAZINE_SEO_METADATA_OK",len(titles))

    def test_real_popularity_and_photo_first_layout(self):
        from datetime import date
        from magazine_popular_v1 import validate, popular_panel
        from unittest.mock import patch
        today=date(2026,11,27)
        catalog={"salvare-auto/":{"secret":False},"garage-gratuiti/":{"secret":False},"trofei/test/":{"secret":True}}
        snapshot={"schema":"magazine-pageviews-v1","source":"Umami dashboard export","metric":"pageviews","start":"2026-11-21","end":"2026-11-27","items":[{"path":"salvare-auto/","pageviews":4},{"path":"garage-gratuiti/","pageviews":9},{"path":"trofei/test/","pageviews":15},{"path":"","pageviews":99}]}
        self.assertEqual(validate(snapshot,today,catalog)[2],[("garage-gratuiti/",9),("salvare-auto/",4)])
        with self.assertRaises(ValueError):validate(snapshot,date(2026,12,10),catalog)
        with patch("magazine_popular_v1.ranked",return_value=(None,None,[])):
            markup=popular_panel()
            self.assertIn('data-magazine-popular="unavailable"',markup)
            self.assertIn("scelte dalla redazione",markup)
            self.assertNotIn('class="sb-rank"',markup)
        with patch("magazine_popular_v1.ranked",return_value=(today,today,[("Garage","garage-gratuiti/",9)])):
            markup=popular_panel()
            self.assertIn('data-magazine-popular="measured"',markup)
            self.assertIn("9 visualizzazioni",markup)
        home=(SITE/"index.html").read_text(encoding="utf-8")
        self.assertIn("data-magazine-photo-nav",home)
        self.assertLess(home.index("data-magazine-photo-nav"),home.index('id="ultimi-articoli"'))
        self.assertLess(home.index("data-magazine-popular"),home.index('class="sb-categories"'))
        self.assertNotIn('class="archive-tile"',home)
        self.assertNotIn('Grafica editoriale · non gameplay',home)
        print("MAGAZINE_REAL_POPULARITY_AND_PHOTO_LAYOUT_OK")

    def test_documented_publication_history(self):
        import json
        from article_chronology_v1 import inventory
        registry=json.loads(Path("data/publication_dates_v1.json").read_text(encoding="utf-8"))
        dated=registry["published"]
        evidence={p:g["publication_day_rome"] for g in registry["evidence"] for p in g["paths"]}
        self.assertEqual(dated,evidence)
        self.assertEqual(len(dated),sum(len(g["paths"]) for g in registry["evidence"]))
        self.assertGreaterEqual(len(dated),150)
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
