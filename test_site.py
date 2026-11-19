"""Offline validation of generated GTA 6 Pages. No scraping or API calls."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

class PortalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.out=Path(cls.tmp.name)
        env=dict(os.environ,SITE_OUT=str(cls.out))
        proc=subprocess.run([sys.executable,"build_site.py"],env=env,capture_output=True,text=True)
        if proc.returncode:
            raise AssertionError(proc.stdout+"\n"+proc.stderr)
        cls.trophies=json.loads(Path("data/trofei.json").read_text(encoding="utf-8"))["trophies"]
        cls.guides=json.loads(Path("data/guide.json").read_text(encoding="utf-8"))["guides"]
        cls.hdr=json.loads(Path("data/hdr_oled.json").read_text(encoding="utf-8"))
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_content_counts_and_links(self):
        self.assertEqual(len(self.trophies),55)
        self.assertEqual(len(self.guides),6)
        self.assertEqual(len(self.hdr["families"]),21)
        self.assertEqual(sum(len(f["models"]) for f in self.hdr["families"]),92)
        self.assertEqual(sum(t["hidden"] for t in self.trophies),28)
        homepage=(self.out/"index.html").read_text(encoding="utf-8")
        self.assertIn("Trofei",homepage)
        self.assertIn("Guide e tutorial",homepage)
        self.assertIn("HDR OLED",homepage)
        self.assertIn("https://xfederiko11.github.io/gta-6/hdr-oled/",homepage)
        self.assertIn("https://xfederiko11.github.io/gta-6/",homepage)
        self.assertNotIn("federiko-gta-playstation-bot",homepage)

    def test_every_trophy_seo_page_and_legacy_alias(self):
        for trophy in self.trophies:
            directory=self.out/"trofei"/trophy["slug"]
            html=(directory/"index.html").read_text(encoding="utf-8")
            self.assertIn(trophy["name_it"],html)
            self.assertIn("rel=\"canonical\"",html)
            self.assertIn("application/ld+json",html)
            self.assertIn("lang=\"it\"",html)
            self.assertIn("PowerPyx",html)
            self.assertIn("https://xfederiko11.github.io/gta-6/trofei/",html)
            legacy=(self.out/(trophy["id"]+".html")).read_text(encoding="utf-8")
            self.assertIn(trophy["slug"],legacy)

    def test_guides_each_have_original_source_and_italian_steps(self):
        for guide in self.guides:
            html=(self.out/"guide-e-tutorial"/guide["id"]/"index.html").read_text(encoding="utf-8")
            self.assertIn(guide["title"],html)
            self.assertIn(guide["source_url"].replace("&","&amp;"),html)
            self.assertEqual(html.count("<li>"),len(guide["steps"]))
            self.assertIn("Screenshot promozionale",html)
            self.assertIn("Passaggi",html) if "Passaggi" in html else self.assertIn("Procedura",html)

    def test_robots_and_sitemap(self):
        self.assertTrue((self.out/"robots.txt").exists())
        self.assertTrue((self.out/".nojekyll").exists())
        raw=(self.out/"sitemap.xml").read_text(encoding="utf-8")
        root=ET.fromstring(raw)
        locs=[x.text for x in root.iter() if x.tag.endswith("loc")]
        self.assertEqual(len(locs),4+27+6+1+len(self.hdr["families"]))
        self.assertEqual(len(locs),len(set(locs)))
        self.assertTrue(all(x.startswith("https://xfederiko11.github.io/gta-6/") for x in locs))
        self.assertTrue((self.out/"trofei"/"medaglie-oro"/"index.html").exists())
        self.assertIn("https://xfederiko11.github.io/gta-6/hdr-oled/",locs)

    def test_spoiler_indexing_before_launch_grace(self):
        # When executed after 21 November, all 55 pages become indexable.
        # The homepage keeps spoiler list collapsed in both cases.
        html=(self.out/"trofei"/"index.html").read_text(encoding="utf-8")
        self.assertIn("<details>",html)
        self.assertIn("28 trofei nascosti",html)

    def test_all_public_pages_show_real_update_views_and_x(self):
        pages=[self.out/"index.html",self.out/"trofei"/"index.html",
               self.out/"guide-e-tutorial"/"index.html",
               self.out/"trofei"/"medaglie-oro"/"index.html"]
        pages += [self.out/"trofei"/t["slug"]/"index.html" for t in self.trophies]
        pages += [self.out/"guide-e-tutorial"/g["id"]/"index.html" for g in self.guides]
        pages += [self.out/"hdr-oled"/"index.html"]
        pages += [self.out/"hdr-oled"/f["slug"]/"index.html" for f in self.hdr["families"]]
        self.assertEqual(len(pages),4+55+6+1+len(self.hdr["families"]))
        for page in pages:
            markup=page.read_text(encoding="utf-8")
            self.assertIn('class="page-meta"',markup,str(page))
            self.assertIn("Aggiornata il",markup,str(page))
            self.assertRegex(markup,r'<time datetime="20\d{2}-\d{2}-\d{2}">')
            self.assertIn('article:modified_time',markup,str(page))
            self.assertIn('"dateModified"',markup,str(page))
            self.assertIn("hitscounter.dev/api/hit?url=",markup,str(page))
            self.assertIn("Visualizzazioni",markup,str(page))
            self.assertIn('https://x.com/xFederiko11',markup,str(page))
            self.assertIn('rel="me noopener noreferrer"',markup,str(page))
            self.assertNotIn("12345 visite",markup)
        # Every URL counts its own visits, never a site-wide combined count.
        first=pages[0].read_text(encoding="utf-8")
        second=pages[1].read_text(encoding="utf-8")
        self.assertIn("https%3A%2F%2Fxfederiko11.github.io%2Fgta-6%2F",first)
        self.assertIn("https%3A%2F%2Fxfederiko11.github.io%2Fgta-6%2Ftrofei%2F",second)

    def test_freshness_date_source_is_not_deploy_clock_only(self):
        import site_info
        from unittest.mock import patch, Mock
        from datetime import datetime, timezone
        site_info.last_modified_at.cache_clear()
        stamp="2026-11-17T08:31:00+00:00"
        with patch("site_info.subprocess.run",return_value=Mock(returncode=0,stdout=stamp)):
            actual=site_info.last_modified_at("trofei/trofeo-14-una-lunga-strada/")
            self.assertEqual(actual,datetime(2026,11,17,8,31,tzinfo=timezone.utc))
        site_info.last_modified_at.cache_clear()
        with self.assertRaises(ValueError):
            site_info.view_badge_url("https://example.com/elsewhere")
        with self.assertRaises(ValueError):
            site_info.view_badge_url("https://xfederiko11.github.io/gta-6.evil.net/")

    def test_hdr_oled_family_pages_models_and_search(self):
        root=self.out/"hdr-oled"/"index.html"
        self.assertTrue(root.exists())
        index=root.read_text(encoding="utf-8")
        self.assertIn('id="hdr-ricerca"',index)
        self.assertIn("data-hdr-search=",index)
        self.assertIn("data-hdr-brand=",index)
        self.assertIn('data-hdr-brand-filter="all"',index)
        self.assertEqual(index.count('data-hdr-brand-filter='),6)
        self.assertIn("Nessun modello trovato",index)
        self.assertIn("Max Brightness",index)
        self.assertIn("Paper White",index)
        self.assertIn("1100",index)
        self.assertIn("600",index)
        self.assertIn("valori di partenza osservati nel gioco",index)
        self.assertIn("OLED55C44LA",index)
        self.assertIn("OLED65C47LA",index)
        self.assertIn("QE77S90DAEXZT",index)
        self.assertIn("Game HDR",index)
        self.assertIn("HGiG",index)
        self.assertIn("application/ld+json",index)
        self.assertIn("92",index)
        for family in self.hdr["families"]:
            path=self.out/"hdr-oled"/family["slug"]/"index.html"
            self.assertTrue(path.exists(),family["slug"])
            page=path.read_text(encoding="utf-8")
            self.assertIn('rel="canonical"',page)
            self.assertIn("Regola HDR",page)
            self.assertIn("https://www.playstation.com/it-it/support/hardware/ps5-enable-adjust-hdr/",page)
            self.assertIn("Fonti per modello e impostazioni",page)
            self.assertIn("GTA VI",page)
            for model in family["models"]:
                self.assertIn(model["code"],index)
                self.assertIn(model["code"],page)
                self.assertIn(str(model["size"])+"″",page)
            for source in family["sources"]:
                self.assertIn(source.replace("&","&amp;"),page)
            if family["brand"] == "LG":
                self.assertIn("Compensazione mappatura toni",page)
        c4=(self.out/"hdr-oled"/"lg-oled-c4"/"index.html").read_text(encoding="utf-8")
        c2=(self.out/"hdr-oled"/"lg-oled-c2"/"index.html").read_text(encoding="utf-8")
        g5=(self.out/"hdr-oled"/"lg-oled-g5"/"index.html").read_text(encoding="utf-8")
        self.assertIn("1100",c4)
        self.assertIn("800",c2)
        self.assertIn("non misurata",c4)
        self.assertIn("NON preset personalizzato",g5)
        self.assertIn("Brightness Booster",c4)
        self.assertIn("OLED55C43LA",c4)
        self.assertIn("Compensazione mappatura toni",c4)
        self.assertNotIn("1000 nit calibrati per GTA 6",index)

    def test_no_external_paid_dependencies(self):
        self.assertFalse((self.out/"node_modules").exists())
        self.assertEqual(len(list((self.out/"trofei").glob("trofeo-*/index.html"))),55)
        self.assertEqual(len(list((self.out/"guide-e-tutorial").glob("*/index.html"))),6)

if __name__=="__main__":
    unittest.main()
