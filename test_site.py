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
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_content_counts_and_links(self):
        self.assertEqual(len(self.trophies),55)
        self.assertEqual(len(self.guides),6)
        self.assertEqual(sum(t["hidden"] for t in self.trophies),28)
        homepage=(self.out/"index.html").read_text(encoding="utf-8")
        self.assertIn("Trofei",homepage)
        self.assertIn("Guide e tutorial",homepage)
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
        self.assertEqual(len(locs),4+27+6)
        self.assertEqual(len(locs),len(set(locs)))
        self.assertTrue(all(x.startswith("https://xfederiko11.github.io/gta-6/") for x in locs))
        self.assertTrue((self.out/"trofei"/"medaglie-oro"/"index.html").exists())

    def test_spoiler_indexing_before_launch_grace(self):
        # When executed after 21 November, all 55 pages become indexable.
        # The homepage keeps spoiler list collapsed in both cases.
        html=(self.out/"trofei"/"index.html").read_text(encoding="utf-8")
        self.assertIn("<details>",html)
        self.assertIn("28 trofei nascosti",html)

    def test_no_external_paid_dependencies(self):
        self.assertFalse((self.out/"node_modules").exists())
        self.assertEqual(len(list((self.out/"trofei").glob("trofeo-*/index.html"))),55)
        self.assertEqual(len(list((self.out/"guide-e-tutorial").glob("*/index.html"))),6)

if __name__=="__main__":
    unittest.main()
