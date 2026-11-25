"""Regression checks for the group-3 platinum page and per-step source links."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlsplit
import unittest
from copy import deepcopy

from platinum_roadmap_v1 import render, PHASES, ROADMAP_PATH
from guide_step_references_v1 import validate, render as step_render
from visual_guide_content import enrich

ROOT=Path("_site")


def fixtures():
    trophies=json.loads(Path("data/trofei.json").read_text(encoding="utf-8"))["trophies"]
    guides=json.loads(Path("data/guide.json").read_text(encoding="utf-8"))["guides"]
    guides+=json.loads(Path("data/visual_guides.json").read_text(encoding="utf-8"))["guides"]
    guides=enrich(guides)
    refs=json.loads(Path("data/guide_visual_refs.json").read_text(encoding="utf-8"))
    mapdata=json.loads(Path("data/guide_step_refs.json").read_text(encoding="utf-8"))
    return trophies,guides,refs,mapdata


class GroupThreeTests(unittest.TestCase):
    def test_roadmap_has_no_false_psn_synchronization_or_missable_certainty(self):
        trophies,*_=fixtures()
        html=render(trophies)
        self.assertEqual(len(PHASES),5)
        self.assertEqual(html.count('data-roadmap-check='),sum(len(x["tasks"]) for x in PHASES))
        self.assertEqual(len({phase["id"] for phase in PHASES}),5)
        self.assertIn("non leggono il tuo account PSN",html)
        self.assertIn("non ha ancora stabilito con certezza",html)
        self.assertIn("70 delle 80 sfide",html)
        self.assertIn("data-roadmap-trophy=\"28\"",html)
        self.assertIn("data-roadmap-trophy=\"17\"",html)
        self.assertIn("data-roadmap-trophy=\"14\"",html)
        self.assertIn('id="capitolo-uno"',html)
        self.assertIn('id="fonti-platino"',html)
        with self.assertRaises(ValueError):
            render(trophies[:-1])

    def test_all_step_links_reuse_sourced_existing_video_or_map(self):
        _,guides,refs,data=fixtures()
        self.assertTrue(validate(guides,data,refs))
        by={g["id"]:g for g in guides}
        self.assertIn("7:35",step_render(by["soldi-2500-three-sheets-liquor"],2,data,refs))
        self.assertIn("t=455s",step_render(by["soldi-2500-three-sheets-liquor"],2,data,refs))
        for n,stamp in ((0,285),(2,455)):
            money=step_render(by["soldi-2500-three-sheets-liquor"],n,data,refs)
            self.assertIn('data-step-video-id="1GtrjKhSwzM"',money)
            self.assertIn('data-step-video-seconds="'+str(stamp)+'"',money)
            self.assertNotIn("<iframe",money)
        self.assertEqual(step_render(by["soldi-2500-three-sheets-liquor"],1,data,refs),"")
        self.assertIn("gtabase.com/gta-6/map/",step_render(by["registrare-auto-personale"],0,data,refs))
        self.assertEqual(step_render(by["registrare-auto-personale"],3,data,refs),"")
        first=step_render(by["registrare-auto-personale"],1,data,refs)
        fifth=step_render(by["registrare-auto-personale"],4,data,refs)
        self.assertIn('data-step-video-id="R0GdEkPZSvM"',first)
        self.assertIn('data-step-video-seconds="266"',first)
        self.assertIn('data-step-video-seconds="675"',fifth)
        self.assertIn('data-step-video-open hidden',first)
        self.assertIn('rel="noopener noreferrer"',first)
        self.assertIn('video del passaggio',first)
        self.assertNotIn('<iframe',first)
        self.assertNotIn('data-step-video-open',step_render(by["prima-persona-glitch-ps5"],4,data,refs))

        for guide_id,steps in data["guides"].items():
            for n in steps:
                markup=step_render(by[guide_id],int(n),data,refs)
                self.assertIn("non screenshot",markup)
                self.assertNotIn("<img",markup)
                self.assertIn('rel="noopener noreferrer"',markup)
        altered=deepcopy(data)
        altered["guides"]["registrare-auto-personale"]["4"]["at"]=688
        with self.assertRaises(ValueError):
            validate(guides,altered,refs)

    def test_generated_page_and_guide_integration(self):
        if not (ROOT/"index.html").is_file():
            self.skipTest("Production build is not present yet")
        page=(ROOT/ROADMAP_PATH/"index.html").read_text(encoding="utf-8")
        self.assertIn("data-platinum-roadmap",page)
        self.assertIn("/assets/platinum-roadmap.js",page)
        self.assertIn("/assets/platinum-roadmap.css",page)
        self.assertIn('<link rel="canonical" href="https://xfederiko11.github.io/gta-6/'+ROADMAP_PATH+'"',page)
        index=(ROOT/"trofei/index.html").read_text(encoding="utf-8")
        self.assertIn(ROADMAP_PATH,index)
        _,guides,_,_=fixtures()
        glitch=next(g for g in guides if g["id"]=="prima-persona-glitch-ps5")
        media=(ROOT/glitch["canonical_path"]/"index.html").read_text(encoding="utf-8")
        self.assertIn("data-step-external-evidence=\"video\"",media)
        self.assertIn("Trophy Status Uncertain",media)
        money=next(g for g in guides if g["id"]=="soldi-2500-three-sheets-liquor")
        article=(ROOT/money["canonical_path"]/"index.html").read_text(encoding="utf-8")
        for n,stamp in ((1,285),(3,455)):
            step=article.split('id="passaggio-'+str(n)+'"',1)[1].split('id="passaggio-'+str(n+1)+'"',1)[0]
            self.assertIn('data-step-video-seconds="'+str(stamp)+'"',step)
        self.assertEqual(article.count('data-step-video-id="1GtrjKhSwzM"'),2)
        self.assertNotIn("<iframe",article)
        self.assertIn("step-video-opt-in-v1.js?v=",article)
        listing=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
        self.assertIn(ROADMAP_PATH,listing)

    def test_frontend_scripts_are_offline_and_syntax_accessible(self):
        script=Path("site/assets/platinum-roadmap.js").read_text(encoding="utf-8")
        for token in ("fetch(", "XMLHttpRequest","api.github.com","api.psn", "innerHTML","navigator.credentials"):
            self.assertNotIn(token,script)
        self.assertIn("gta6-italia:trophies:v1",script)
        self.assertIn("window.localStorage",script)


if __name__=="__main__": unittest.main()
