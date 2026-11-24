"""Vehicle index, one-model tutorials, search and source-rights regression."""
import copy
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from vehicle_catalog_v1 import (
    PATH, VERIFIED, load, validate, index_body, article_body, social_text
)
from moses_vehicle_jobs_v1 import TASKS

ROOT=Path("_site")
BASE="https://xfederiko11.github.io/gta-6/"
ITEMS=load()["items"]

class VehicleCatalogTests(unittest.TestCase):
    def test_25_unique_source_linked_entries(self):
        doc=validate(load())
        self.assertEqual(len(doc["items"]),25)
        self.assertEqual(len({x["slug"] for x in doc["items"]}),25)
        self.assertEqual(sum(x["kind"]=="Moses" for x in doc["items"]),8)
        self.assertEqual(sum(x["kind"]=="Randy" for x in doc["items"]),17)
        self.assertEqual(sum(x["status"]==VERIFIED for x in doc["items"]),17)
        self.assertEqual(sum(x["status"]=="In verifica" for x in doc["items"]),7)
        self.assertEqual(sum(x["status"]=="Community" for x in doc["items"]),1)
        names={x["name"] for x in doc["items"]}
        self.assertTrue({x[0] for x in TASKS[:6]}.issubset(names))
        # Moses guide appends a spoiler description to the Sultan gift;
        # the SEO catalog must keep the actual car name as its own title.
        self.assertTrue(TASKS[6][0].startswith("Moses’ Sultan"))
        self.assertIn("Moses’ Sultan",names)
        self.assertIn("Canis Crawler",names)
        self.assertIn("Granforma Zorrusso",names)
        self.assertIn("Moses’ Sultan",names)
        self.assertIn("Invetero Coquette D10",names)
        self.assertIn("Nessuna associazione",doc["origin_lead"]["status"])

    def test_evidence_gate_fail_closed(self):
        original=load()
        for field,value in (
            ("slug","../../secrets"),
            ("source_url","http://malicious.example/photo.png"),
            ("status","Ufficiale"),
            ("steps",["Vai"]),
        ):
            bad=copy.deepcopy(original)
            bad["items"][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                validate(bad)
        bad=copy.deepcopy(original)
        bad["items"][0]["slug"]=bad["items"][1]["slug"]
        with self.assertRaises(ValueError):validate(bad)
        self.assertFalse(any("post di murciaconlimon" in x["note"].casefold() for x in ITEMS))

    def test_index_and_articles_use_no_fake_gameplay(self):
        doc=load()
        text=index_body(doc,BASE)
        self.assertEqual(text.count('class="vc-card"'),25)
        self.assertIn("data-vc-finder",text)
        self.assertIn("data-vc-todo",text)
        self.assertIn("non spawn garantiti",text.lower())
        self.assertNotIn("data-pin-lat",text)
        for car in doc["items"]:
            with self.subTest(car=car["slug"]):
                html=article_body(car,BASE,doc["items"])
                self.assertEqual(html.count("<h1>"),1)
                self.assertEqual(html.count("<li>"),len(car["steps"]))
                self.assertIn(car["source_url"],html.replace("&amp;","&"))
                self.assertIn(car["additional_source"],html.replace("&amp;","&"))
                self.assertIn("Controllo finale",html)
                self.assertIn(BASE+"salvare-auto/",html)
                self.assertNotIn("<img ",html)
                self.assertNotIn("<iframe",html)
                self.assertNotIn("data-gameplay-image",html)
                self.assertNotIn("data-pin-lat",html)
                if car["status"]==VERIFIED:
                    self.assertIsNotNone(social_text(car,BASE))
                    self.assertIn('https://x.com/intent/tweet?text=',html)
                else:
                    self.assertIsNone(social_text(car,BASE))
                    self.assertNotIn('https://x.com/intent/tweet?text=',html)
                    self.assertIn("Post X non disponibile",html)

    def test_generated_pages_sitemap_and_robots(self):
        directory=ROOT/PATH/"index.html"
        if not directory.exists():self.skipTest("Build artifact is created in CI")
        page=directory.read_text(encoding="utf-8")
        self.assertIn('rel="canonical" href="'+BASE+PATH+'"',page)
        self.assertIn('name="robots" content="index,follow"',page)
        self.assertEqual(page.count('class="vc-card"'),25)
        self.assertIn('vehicle-finder-v1.js?v=',page)
        self.assertIn('vehicle-finder-v1.css?v=',page)
        self.assertEqual(page.count('<h1'),1)
        sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
        self.assertIn(BASE+PATH,sitemap)
        verified=0
        pending=0
        for car in ITEMS:
            relative=PATH+car["slug"]+"/"
            article=ROOT/relative/"index.html"
            self.assertTrue(article.is_file(),relative)
            html=article.read_text(encoding="utf-8")
            self.assertIn('rel="canonical" href="'+BASE+relative+'"',html)
            self.assertEqual(html.count('<h1'),1,relative)
            if car["status"]==VERIFIED:
                verified+=1
                self.assertIn('name="robots" content="index,follow"',html)
                self.assertIn(BASE+relative,sitemap)
                self.assertIn('type="application/ld+json"',html)
            else:
                pending+=1
                self.assertIn('name="robots" content="noindex,follow"',html)
                self.assertNotIn(BASE+relative,sitemap)
                self.assertNotIn('https://x.com/intent/tweet?text=',html)
        self.assertEqual((verified,pending),(17,8))
        js=(ROOT/"assets/vehicle-finder-v1.js").read_text(encoding="utf-8")
        self.assertIn("localStorage",js)
        self.assertIn("botx-vehicle-finder-found-v1",js)
        self.assertNotIn("fetch(",js)
        self.assertNotIn("XMLHttpRequest",js)

if __name__=="__main__":
    unittest.main()
