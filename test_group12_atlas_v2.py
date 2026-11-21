"""Regression: every trophy and guide has sourced, spoiler-aware, truthful data."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import re
import unittest

from platinum_atlas_v2 import render as render_trophies, validate as validate_trophies, UNCERTAIN
from guide_location_atlas_v2 import (render_hub, render_guide, validate as validate_places, HUB_PATH)
from visual_guide_content import enrich

ROOT=Path("_site")
BASE="https://xfederiko11.github.io/gta-6/"


def fixtures():
    read=lambda p:json.loads(Path(p).read_text(encoding="utf-8"))
    trophies=read("data/trofei.json")["trophies"]
    routes=read("data/platinum_trophy_routes_v2.json")
    guides=read("data/guide.json")["guides"]+read("data/visual_guides.json")["guides"]
    guides=enrich(guides)
    loc=read("data/guide_locations_v2.json")
    med=read("data/meditation_checklist_v1.json")
    media=read("data/visual_media.json")["images"]
    extras=read("data/guide_extras.json")["guides"]
    return trophies,routes,guides,loc,med,media,extras


class Group12AtlasTests(unittest.TestCase):
    def test_every_trophy_has_individual_instruction_and_proof(self):
        trophies,routes,*_=fixtures()
        self.assertTrue(validate_trophies(trophies,routes))
        self.assertEqual(len(routes["records"]),55)
        self.assertEqual({x["number"] for x in routes["records"]},set(range(1,56)))
        self.assertEqual(sum(x["hidden"] for x in trophies),28)
        markup=render_trophies(trophies,routes)
        self.assertEqual(markup.count('data-atlas-card '),55)
        self.assertEqual(markup.count('data-atlas-trophy='),55)
        self.assertEqual(markup.count('data-atlas-spoiler'),28)
        self.assertIn('data-atlas-filter="all"',markup)
        self.assertIn('data-atlas-search',markup)
        self.assertIn("55 trofei",markup)
        self.assertIn("non sono prove di gioco dirette",markup)
        for num in UNCERTAIN:
            self.assertTrue(routes["records"][num-1].get("warning"))
        for record in routes["records"]:
            t=trophies[record["number"]-1]
            self.assertIn(BASE+"trofei/"+t["slug"]+"/",markup)
        changed=deepcopy(routes)
        changed["records"].pop()
        with self.assertRaises(ValueError):validate_trophies(trophies,changed)
        changed=deepcopy(routes)
        changed["records"][27]["guide"]="https://evil.example/attack"
        with self.assertRaises(ValueError):validate_trophies(trophies,changed)

    def test_every_guide_has_sourced_places_and_no_fake_pins(self):
        _,_,guides,loc,med,media,extras=fixtures()
        self.assertTrue(validate_places(guides,loc,med))
        total=sum(len(v) for v in loc["guides"].values())
        self.assertEqual(len(loc["guides"]),11)
        self.assertEqual(total,18)
        self.assertEqual(sum(x["kind"]=="map-category" for v in loc["guides"].values() for x in v),4)
        by={g["id"]:g for g in guides}
        intro=render_guide(by["meditazione-capitolo-1"],loc,med)
        self.assertEqual(intro.count('class="g-loc-number"'),10)
        self.assertIn("Jason’s House",intro)
        self.assertIn("Mount Kalaga",intro)
        self.assertIn('class="g-loc-spoiler"',intro)
        self.assertIn("non sono pin geolocalizzati",intro)
        money=render_guide(by["soldi-facili-capitolo-1"],loc,med)
        self.assertIn("Manatee Motel",money)
        self.assertIn("Nessun pin",money)
        hub=render_hub(guides,loc,media,extras,lambda key:None)
        self.assertEqual(hub.count('data-location-guide='),11)
        self.assertIn(BASE+"screenshot-ps5/",hub)
        self.assertNotIn("lat=",hub)
        self.assertNotIn("<iframe",hub)
        self.assertNotIn("<img ",hub)
        # Source-only location photographs must NOT be presented as verified
        # action screenshots in the maps section.
        demo=render_hub(guides,loc,media,extras,
                        lambda key:BASE+"assets/visual/"+key+".webp"
                        if key in ("liquor-store","shirley-house","taxi-phone","save-car","scooter-phone") else None)
        self.assertIn('data-map-guide-screenshot="scooter-phone"',demo)
        self.assertNotIn('data-map-guide-screenshot="liquor-store"',demo)
        self.assertNotIn('data-map-guide-screenshot="taxi-phone"',demo)
        self.assertIn('class="g-map-preview"',demo)
        self.assertNotIn("rockstargames.com/VI/_next",demo)
        malformed=deepcopy(loc)
        malformed["guides"]["registrare-auto-personale"][0]["url"]="https://attacker.example/map"
        with self.assertRaises(ValueError):validate_places(guides,malformed,med)

    def test_static_page_links_and_assets_after_build(self):
        if not (ROOT/"index.html").is_file():
            self.skipTest("Production site not built")
        roadmap=(ROOT/"trofei/roadmap-platino/index.html").read_text(encoding="utf-8")
        self.assertIn('id="guida-55-trofei"',roadmap)
        self.assertEqual(roadmap.count('data-atlas-card '),55)
        self.assertIn('assets/platinum-atlas-v2.js?v=',roadmap)
        self.assertIn('assets/platinum-atlas-v2.css?v=',roadmap)
        self.assertIn('data-trophy-atlas',roadmap)
        self.assertIn('data-atlas-trophy="28"',roadmap)
        hub=(ROOT/HUB_PATH/"index.html").read_text(encoding="utf-8")
        self.assertEqual(hub.count("data-location-guide="),11)
        self.assertIn('<link rel="canonical" href="'+BASE+HUB_PATH+'"',hub)
        self.assertNotIn("fake-map",hub)
        meditation=(ROOT/"guide-e-tutorial/meditazione-capitolo-1/index.html").read_text(encoding="utf-8")
        self.assertIn('id="luoghi-mappe"',meditation)
        self.assertIn("10 punti di orientamento",meditation)
        self.assertIn("Mount Kalaga",meditation)
        index=(ROOT/"trofei/index.html").read_text(encoding="utf-8")
        self.assertIn("guida-55-trofei",index)
        sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
        self.assertIn(BASE+HUB_PATH,sitemap)
        for asset in ("platinum-atlas-v2.js","platinum-atlas-v2.css"):
            self.assertTrue((ROOT/"assets"/asset).is_file())

    def test_scripts_are_local_only_and_no_credentials(self):
        script=Path("site/assets/platinum-atlas-v2.js").read_text(encoding="utf-8")
        for bad in ("fetch(","XMLHttpRequest","https://","window.open","innerHTML","location.href","api.psn","api.github"):
            self.assertNotIn(bad,script)
        self.assertIn('gta6-italia:trophies:v1',script)
        self.assertIn('data-atlas-filter',script)
        self.assertIn('gta6-italia:trophy-progress-changed',script)
        original=Path("site/assets/platinum-roadmap.js").read_text(encoding="utf-8")
        self.assertIn('gta6-italia:trophy-progress-changed',original)


if __name__=="__main__": unittest.main()
