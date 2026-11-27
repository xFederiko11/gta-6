"""No-network verification of 69 consent-first GTA VI embedded map panels."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import unittest

from interactive_article_maps_v1 import (
    validate,article_paths,render,guide_points,trophy_points,collectible_points,
    as_json,SCHEMA,PRIMARY,SECONDARY
)
from visual_guide_content import enrich

BASE="https://xfederiko11.github.io/gta-6/"
ROOT=Path("_site")


def fixture():
    read=lambda p:json.loads(Path(p).read_text(encoding="utf-8"))
    guides=enrich(read("data/guide.json")["guides"]+read("data/visual_guides.json")["guides"])
    return (guides,read("data/trofei.json")["trophies"],
            read("data/guide_locations_v2.json"),read("data/collectible_routes_v4.json"),
            read("data/meditation_checklist_v1.json"))


class EmbedMapTests(unittest.TestCase):
    def test_11_guides_55_trophies_123_checkpoints_counted_without_fake_pins(self):
        guides,trophies,loc,points,med=fixture()
        report=validate(guides,trophies,loc,points)
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["guide_articles"],11)
        self.assertEqual(report["trophy_articles"],55)
        self.assertEqual(report["garage_guide_articles_with_map"],1)
        self.assertEqual(report["articles_with_map"],67)
        self.assertEqual(report["pages_with_interactive_map"],69)
        self.assertEqual(report["guide_location_descriptions"],18)
        self.assertEqual(report["collectible_descriptions"],123)
        self.assertEqual(report["exact_gameplay_coordinate_pairs_verified"],0)
        self.assertFalse(report["external_maps_loaded_automatically"])
        self.assertFalse(report["named_place_search_is_exact_pin"])
        self.assertEqual([x["embed"] for x in report["providers"]],[PRIMARY,SECONDARY])
        g,t=article_paths(guides,trophies)
        self.assertEqual(len(g),11)
        self.assertEqual(len(t),55)
        self.assertTrue(all(x.startswith("trofei/") for x in t))
        self.assertEqual(len(collectible_points(points)),12)
        shown=render("Tutti i checkpoint",collectible_points(points),id_suffix="collectibles")
        self.assertIn("Vice Map",shown)
        self.assertIn("GTA6.city",shown)
        self.assertIn("data-vim-load",shown)
        self.assertIn('data-vim-provider="vice"',shown)
        self.assertIn('data-vim-provider="city"',shown)
        self.assertIn('href="'+PRIMARY.replace("/embed/map","/map")+'"',shown)
        self.assertIn('role="status" aria-live="polite"',shown)
        self.assertNotIn("<iframe",shown)
        self.assertNotIn("lat=",shown)
        self.assertNotIn("data-vim-lat",shown)
        self.assertNotIn("iframe src=",shown)
        self.assertNotIn("onload=",shown)
        self.assertIn("non è un pin esatto verificato",shown)

    def test_no_fixed_location_and_spoiler_guides_are_labeled_truthfully(self):
        guides,trophies,loc,points,med=fixture()
        by={x["id"]:x for x in guides}
        meditation=guide_points(by["meditazione-capitolo-1"],loc,med)
        self.assertEqual(len(meditation),11)
        txt=render("Meditazioni",meditation,id_suffix="meditazione-capitolo-1")
        self.assertIn("Jason",txt)
        self.assertEqual(txt.count("data-vim-seek="),11)
        abstract=guide_points(by["prima-persona-glitch-ps5"],loc,med)
        text=render("Glitch visuale",abstract,id_suffix="glitch")
        self.assertIn("Non ha una posizione fissa",text)
        self.assertEqual(text.count("data-vim-seek="),0)
        self.assertIn("non certifica",text)
        t=render("Platino",trophy_points(1,{"group":"finale"},points),id_suffix="trofeo-1")
        self.assertIn("Nessun punto fisso verificato",t)
        with self.assertRaises(ValueError):
            render("Invalid",[{"name":"Fake","where":"...","precision":"exact"}],id_suffix="fake")
        with self.assertRaises(ValueError):
            render("Invalid",id_suffix="../malicious")

    def test_invalid_source_data_fails_closed(self):
        guides,trophies,loc,points,med=fixture()
        broken=deepcopy(loc)
        broken["guides"][guides[0]["id"]][0]["precision"]="exact"
        with self.assertRaises(ValueError):
            validate(guides,trophies,broken,points)
        broken=deepcopy(points)
        broken["points"][0]["id"]=broken["points"][1]["id"]
        with self.assertRaises(ValueError):
            validate(guides,trophies,loc,broken)
        broken=deepcopy(points)
        broken["points"].pop()
        with self.assertRaises(ValueError):
            validate(guides,trophies,loc,broken)

    def test_js_has_no_autoload_no_third_party_code_executed_without_click(self):
        js=Path("site/assets/interactive-map-v1.js").read_text(encoding="utf-8")
        self.assertIn('load.addEventListener("click"',js)
        self.assertIn('frame=document.createElement("iframe")',js)
        self.assertIn('frame.src=url',js)
        self.assertIn("https://vice-map.com/embed/map",js)
        self.assertIn("https://gta6.city/embed/map",js)
        self.assertIn("game-map-load-intent",js)
        self.assertIn("game-map-named-search-intent",js)
        self.assertNotIn("localStorage",js)
        self.assertNotIn("fetch(",js)
        self.assertNotIn("postMessage(",js)
        self.assertNotIn("window.PSN",js)
        self.assertNotIn("psn_api",js)
        self.assertNotIn("autoplay",js)

    def test_exported_public_build_contains_69_unique_interactive_map_panels(self):
        if not (ROOT/"index.html").exists():
            self.skipTest("Production site not built yet")
        guides,trophies,_,_,_=fixture()
        report=json.loads((ROOT/"map-rollout-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(json.loads(as_json(report)),report)
        self.assertEqual(report["pages_with_interactive_map"],69)
        g,t=article_paths(guides,trophies)
        for path in [*g,*t,"collezionabili/percorsi/","mappe-guide/","garage-gratuiti/southside-storage/"]:
            html=(ROOT/path/"index.html").read_text(encoding="utf-8")
            self.assertEqual(html.count("data-vi-map "),1,path)
            self.assertIn("interactive-map-v1.css?v=",html)
            self.assertIn("interactive-map-v1.js?v=",html)
            self.assertNotIn("<iframe src=",html)
            self.assertIn('href="https://vice-map.com/"',html)
            self.assertIn('data-vim-load',html)
            self.assertIn("mappa-interattiva",html)
        south=(ROOT/"garage-gratuiti/southside-storage/index.html").read_text(encoding="utf-8")
        self.assertEqual(south.count("data-vi-map "),1)
        self.assertEqual(south.count("data-southside-map-pin="),6)
        self.assertEqual(south.count('data-youtube-id="mu_VCQKeXvM"'),6)
        self.assertIn("interactive-map-v1.js?v=",south)
        collect=(ROOT/"collezionabili/percorsi/index.html").read_text(encoding="utf-8")
        self.assertEqual(collect.count('data-vim-map-search='),123)
        self.assertIn("Kenton",collect)
        self.assertIn("123 checkpoint",collect)
        guide=(ROOT/"guide-e-tutorial/soldi-facili-capitolo-1/index.html").read_text(encoding="utf-8")
        self.assertIn("Cerca nome nella mappa",guide)
        self.assertIn("data-vim-map-search",guide)
        spoiler=(ROOT/"guide-e-tutorial/meditazione-capitolo-1/index.html").read_text(encoding="utf-8")
        self.assertIn('class="v-map-spoiler"',spoiler)
        self.assertIn("Mostra la mappa interattiva",spoiler)
        self.assertNotIn("interactive-map-v1.js?v=",(ROOT/"index.html").read_text(encoding="utf-8"))
        self.assertTrue((ROOT/"assets/interactive-map-v1.js").is_file())
        self.assertTrue((ROOT/"assets/interactive-map-v1.css").is_file())
        self.assertIn(BASE+"mappe-guide/",(ROOT/"sitemap.xml").read_text(encoding="utf-8"))


if __name__=="__main__": unittest.main()
