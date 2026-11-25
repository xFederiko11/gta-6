"""Regression contracts for opt-in creator showcase and source ethics."""
from __future__ import annotations
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

from creator_video_hub_v1 import BASE, PATH, load, records, render, CURATED, KINDS

ROOT = Path("_site")


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append((tag,dict(attrs)))


class CreatorVideoHubTests(unittest.TestCase):
    def test_curation_links_to_four_distinct_source_videos(self):
        items=records(load())
        self.assertEqual(len(items),4)
        self.assertEqual(len({x["video_id"] for x in items}),4)
        self.assertEqual({x["category"] for x in items},set(KINDS))
        self.assertEqual({x["creator"] for x in items},
                         {"TGG","IGN","oneboyler (procedura attribuita a Kackalack dalla community)"})
        self.assertEqual({x["key"] for x in items},{x[0] for x in CURATED})
        for item in items:
            self.assertTrue(item["source"].startswith("https://"))
            self.assertTrue((ROOT/item["guide_path"]/"index.html").is_file())
            self.assertTrue(item["chapters"])
            self.assertTrue(1<=len(item["chapters"])<=8)
        moses=next(x for x in items if x["key"]=="moses-ign")
        self.assertEqual([c["at"] for c in moses["chapters"]], [101,191,293,346,428,520])
        self.assertIn("NON compare",moses["detail"])
        self.assertTrue(moses["spoiler"])
        self.assertTrue(next(x for x in items if x["key"]=="prima-persona-glitch-ps5")["category"]=="extra")

    def test_untrusted_or_duplicate_reference_is_not_published(self):
        data=load()
        bad=deepcopy(data)
        bad["guides"]["registrare-auto-personale"]["youtube_id"] = "invalid"
        with self.assertRaises(ValueError):records(bad)
        bad=deepcopy(data)
        bad["guides"]["registrare-auto-personale"]["youtube_id"]=bad["guides"]["soldi-facili-capitolo-1"]["youtube_id"]
        with self.assertRaises(ValueError):records(bad)
        bad=deepcopy(data)
        bad["guides"]["prima-persona-glitch-ps5"]["spoiler"]=None
        with self.assertRaises(ValueError):records(bad)
        bad=deepcopy(data)
        bad["guides"]["registrare-auto-personale"]["chapters"][0]["at"]=-30
        with self.assertRaises(ValueError):records(bad)

    def test_render_has_provider_fallback_but_no_preloaded_embed(self):
        html=render(records(load()))
        self.assertEqual(html.count('class="cv-card"'),4)
        self.assertEqual(html.count('class="cv-chapter"'),11)
        self.assertEqual(html.count('class="cv-load"'),4)
        self.assertEqual(html.count('data-cv-slot'),4)
        self.assertNotIn("<iframe",html)
        self.assertNotIn('i.ytimg.com',html)
        self.assertNotIn('youtube-nocookie.com/embed',html)
        self.assertNotIn('widgets.js',html)
        self.assertIn('non una partnership',html)
        self.assertIn('non sono verificati indipendentemente',html)
        self.assertIn('non una prova che il nostro team abbia ripetuto',html)
        self.assertIn('Video originale su YouTube',html)
        tags=Tags();tags.feed(html)
        self.assertEqual(sum(t=="h1" for t,a in tags.tags),1)
        self.assertEqual(len([a for t,a in tags.tags if t=="a" and "youtube.com/watch" in a.get("href","")]),4)
        for item in records(load()):
            self.assertIn(BASE+item["guide_path"],html)

    def test_final_html_has_canonical_jsonld_sitemap_dark_and_no_hidden_network(self):
        page=ROOT/PATH/"index.html"
        self.assertTrue(page.is_file())
        html=page.read_text(encoding="utf-8")
        self.assertIn('<link rel="canonical" href="'+BASE+PATH+'"',html)
        self.assertIn('creator-video-hub-v1.css?v=',html)
        self.assertIn('creator-video-hub-v1.js?v=',html)
        self.assertIn('"CollectionPage"',html)
        self.assertIn('"numberOfItems":4',html)
        self.assertEqual(html.count('class="cv-card"'),4)
        self.assertNotIn('<iframe',html)
        self.assertNotIn('data-x-timeline-load',html)
        self.assertIn('reader-theme-boot',html)
        self.assertIn(BASE+PATH,(ROOT/"sitemap.xml").read_text(encoding="utf-8"))
        self.assertIn('video-tutorial/',(ROOT/"index.html").read_text(encoding="utf-8"))
        self.assertIn('video-tutorial/',(ROOT/"guide-e-tutorial/index.html").read_text(encoding="utf-8"))
        script=Path("site/assets/creator-video-hub-v1.js").read_text(encoding="utf-8")
        self.assertIn("youtube-nocookie.com/embed/",script)
        self.assertIn('frame.src = ',script)
        self.assertNotIn("fetch(",script)
        self.assertNotIn("localStorage",script)
        self.assertNotIn("document.cookie",script)
        self.assertNotIn("widgets.js",script)

if __name__=="__main__":
    unittest.main()
