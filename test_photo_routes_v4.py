"""Regression: seven sourced regional routes + consent-first PS5 intake, no fake uploads."""
from __future__ import annotations
import json
import unittest
from copy import deepcopy
from pathlib import Path

from collectible_routes_v4 import validate_routes,render as render_routes,PATH as ROUTE_PATH
from photo_intake_v4 import validate_approved,render as render_intake,PATH as INTAKE_PATH,approved_count,render_approved_for_guide
from visual_guide_content import enrich
from photo_request_hub_v1 import screenshot_count

ROOT=Path("_site")
BASE="https://xfederiko11.github.io/gta-6/"


def data():
    load=lambda path:json.loads(Path(path).read_text(encoding="utf-8"))
    routes=load("data/collectible_routes_v4.json")
    registry=load("data/approved_screenshots_v4.json")
    requests=load("data/visual_requests.json")["guides"]
    guides=enrich(load("data/guide.json")["guides"]+load("data/visual_guides.json")["guides"])
    media=load("data/visual_media.json")["images"]
    extras=load("data/guide_extras.json")["guides"]
    return routes,registry,guides,requests,media,extras


class RegionalRouteTests(unittest.TestCase):
    def test_jack_collection_is_complete_and_menu_numbers_are_not_route_order(self):
        routes,*_=data()
        jack=[p for p in routes["points"] if p.get("card_set")=="jack-of-hearts"]
        self.assertEqual(len(jack),36)
        self.assertEqual({p["card_number"] for p in jack},set(range(1,37)))
        self.assertEqual({p["source_order"] for p in jack},set(range(1,37)))
        old=next(p for p in jack if p["id"]=="pt-12")
        self.assertEqual((old["card_number"],old["source_order"]),(3,11))
        for field in ("card_number","source_order"):
            invalid=deepcopy(routes)
            invalid["points"][-1][field]=invalid["points"][-2][field]
            with self.assertRaises(ValueError):validate_routes(invalid)
        invalid=deepcopy(routes);invalid["points"][-1]["card_number"]=True
        with self.assertRaises(ValueError):validate_routes(invalid)
        html=render_routes(routes)
        self.assertEqual(html.count('data-cr-set="jack-of-hearts"'),36)
        self.assertIn('data-cr-jack aria-pressed="false" hidden',html)
        self.assertIn('Card 3 nel menu',html)

    def test_exactly_157_sourced_waypoints_and_caveats(self):
        routes,*_=data()
        self.assertTrue(validate_routes(routes))
        points=routes["points"]
        self.assertEqual(len(points),157)
        self.assertEqual(len(routes["regions"]),7)
        self.assertEqual(sum(p["type"]=="cards" for p in points),57)
        self.assertEqual(sum(p["type"]=="playlist" for p in points),5)
        self.assertEqual(sum(p["type"]=="waink" for p in points),38)
        self.assertEqual(sum(p["type"]=="underwater" for p in points),6)
        self.assertEqual(sum(p["type"]=="stunt" for p in points),24)
        self.assertEqual(sum(p["type"]=="vehicles" for p in points),3)
        self.assertEqual(sum(p["type"]=="reading" for p in points),2)
        self.assertEqual(sum(p["type"]=="magazines" for p in points),20)
        self.assertEqual(sum(p["type"]=="kenton" for p in points),2)
        self.assertEqual(sum(p.get("location_limited") is True for p in points),9)
        self.assertIn("Christmas House",render_routes(routes))
        self.assertEqual(len([p for p in points if p.get("missable")]),2)
        self.assertEqual(routes["underwater"]["required"],33)
        self.assertEqual(routes["underwater"]["known_in_atlas"],6)
        markup=render_routes(routes)
        self.assertEqual(markup.count('data-cr-step='),157)
        self.assertEqual(markup.count('data-cr-done='),157)
        self.assertEqual(markup.count('data-cr-region='),7)
        self.assertEqual(markup.count('data-cr-filter='),10)
        self.assertIn('id="cr-kelly"',markup)
        self.assertIn("Vicki",markup)
        self.assertIn("Victor Maravilla",markup)
        self.assertIn("Capitolo 2",markup)
        self.assertIn("6/33",markup)
        self.assertIn("30 su 34",markup)
        self.assertIn("Belpoint Strait",markup)
        self.assertIn("Bobcat Dive Site",markup)
        self.assertEqual(markup.count('data-cr-photo-intent='),157)
        self.assertEqual(markup.count('class="cr-limited-copy"'),9)
        self.assertIn('data-cr-follow',markup)
        self.assertIn('target="_blank" rel="noopener noreferrer"',markup)
        self.assertEqual(len({p["id"] for p in points}),157)
        for p in points:
            self.assertIn('id="cr-'+p["id"]+'"',markup)
        for p in points:
            if p["type"]=="kenton":self.assertIs(p["counts_underwater"],False)

        self.assertIn("mancano",markup)
        self.assertIn("Fonte originale e immagini",markup)
        self.assertNotIn("<img",markup)
        self.assertNotIn("<iframe",markup)
        self.assertNotIn("data-map-lat=",markup)
        self.assertNotIn("duration_minutes",markup)
        original=deepcopy(routes)
        original["points"][0]["lat"]=39.0
        with self.assertRaises(ValueError):validate_routes(original)
        original=deepcopy(routes)
        original["points"][25]["missable"]=False
        with self.assertRaises(ValueError):validate_routes(original)
        original=deepcopy(routes)
        original["sources"]["playlist"]="https://attacker.example/fake-map"
        with self.assertRaises(ValueError):validate_routes(original)
        original=deepcopy(routes)
        original["underwater"]["known_in_atlas"]=33
        with self.assertRaises(ValueError):validate_routes(original)
        original=deepcopy(routes)
        original["points"][101]["location_note"]="This is forever missable"
        with self.assertRaises(ValueError):validate_routes(original)
        original=deepcopy(routes)
        original["points"][121]["counts_underwater"]=True
        with self.assertRaises(ValueError):validate_routes(original)


    def test_stunt_recommendations_do_not_fake_300_map_pins(self):
        routes,*_=data()
        s=routes["stunts"]
        self.assertEqual(s["total"],397)
        self.assertEqual(s["needed"],300)
        self.assertEqual(sum(x[1] for x in s["jump_by_region"]),130)
        text=render_routes(routes)
        self.assertIn("300 su 397",text)
        self.assertIn("non presentiamo 300",text)
        self.assertIn("All sources remain WIP",routes["notes"])


class ConsentPhotoTests(unittest.TestCase):
    def test_empty_registry_requires_no_new_received_photos(self):
        _,registry,guides,requests,media,extras=data()
        self.assertTrue(validate_approved(registry,guides,requests))
        self.assertEqual(registry["photos"],[])
        self.assertEqual(approved_count(registry,guides[0]["id"]),0)
        self.assertEqual(render_approved_for_guide(guides[0],registry),"")
        html=render_intake(guides,requests,registry)
        self.assertEqual(html.count('data-guide-link='),11)
        self.assertEqual(html.count('data-photo-guide='),55)
        self.assertIn('data-photo-intake',html)
        self.assertIn('data-pi-owner',html)
        self.assertIn('data-pi-rights',html)
        self.assertIn('data-pi-public',html)
        self.assertIn('data-pi-submit disabled',html)
        self.assertIn('data-pi-fallback',html)
        self.assertIn("Non è un upload dal sito",html)
        self.assertIn("0</strong> nuove foto",html)
        self.assertNotIn('<input type="file"',html)
        self.assertNotIn("data-auto-post",html)
        self.assertNotIn("https://api.github.com/",html)
        self.assertEqual(screenshot_count(guides[0],media,extras,lambda _:None,registry["photos"]),0)
        fake=deepcopy(registry)
        fake["photos"]=[{"id":"made-up-proof","guide_id":guides[0]["id"],"role":1,"platform":"PS5",
                         "rights":"none","author_confirmed":True,"published":True,
                         "human_reviewed":True,"approved_by":"xFederiko11","approved_on":"2026-11-21"}]
        with self.assertRaises(ValueError):validate_approved(fake,guides,requests)
        fake=deepcopy(registry)
        fake["photos"]=[{"id":"unsafe-webp","guide_id":guides[0]["id"],"role":1,"platform":"PS5",
                         "rights":"explicit_nonexclusive_site_and_social",
                         "author_confirmed":True,"published":True,
                         "human_reviewed":False,"approved_by":"bot","approved_on":"2026-11-21"}]
        with self.assertRaises(ValueError):validate_approved(fake,guides,requests)

    def test_creator_frame_requires_visual_review_and_exact_original_source(self):
        _,registry,guides,requests,_,_=data()
        from photo_intake_v4 import render_approved_for_step
        fake=deepcopy(registry)
        row={"id":"creator-test","guide_id":guides[0]["id"],"role":1,
             "step_number":1,"platform":"PS5","rights":"explicit_nonexclusive_site_and_social",
             "author_confirmed":True,"human_reviewed":True,"approved_by":"xFederiko11",
             "published":True,"gameplay_only":True,"no_real_people":True,
             "social_preview":True,"capture_kind":"creator_supplied_video_frame",
             "creator_supplied_file":True,"source_video_id":"R0GdEkPZSvM",
             "source_second":266,"file":"assets/approved/creator-test.webp",
             "source_post":"https://x.com/example/status/123456789",
             "consent_evidence":"https://x.com/example/status/123456789",
             "credit":"Test creator","alt":"Test image only","caption":"Test image only",
             "approved_on":"2026-11-25","source_sha256":"a"*64}
        fake["photos"]=[row]
        for key in ("gameplay_only","no_real_people","creator_supplied_file"):
            row[key]=False
            with self.assertRaises(ValueError):validate_approved(fake,guides,requests)
            row[key]=True
        row["source_second"]=-1
        with self.assertRaises(ValueError):validate_approved(fake,guides,requests)
        row["source_second"]=266
        # Even a plausible record cannot pass without the actual approved file.
        with self.assertRaises(ValueError):validate_approved(fake,guides,requests)
        markup=render_approved_for_step(guides[0],fake,0)
        self.assertIn("FOTOGRAMMA AUTORIZZATO",markup)
        self.assertIn("watch?v=R0GdEkPZSvM&amp;t=266s",markup)
        self.assertIn("4:26",markup)

    def test_scripts_do_not_read_psn_or_claim_to_upload(self):
        for asset in ("site/assets/photo-intake-v4.js","site/assets/collectible-routes-v4.js"):
            text=Path(asset).read_text(encoding="utf-8")
            for bad in ("fetch(","XMLHttpRequest","api.github.com","api.psn","FormData(",
                        "innerHTML","eval(","location.href"):
                self.assertNotIn(bad,text)
        intake=Path("site/assets/photo-intake-v4.js").read_text(encoding="utf-8")
        self.assertIn("window.open",intake)
        self.assertIn(".content.querySelectorAll(\"option\")",intake)
        self.assertIn("rights.checked",intake)
        self.assertIn("text().length<=280",intake)
        routes=Path("site/assets/collectible-routes-v4.js").read_text(encoding="utf-8")
        self.assertIn("gta6-italia:collectible-routes:v4",routes)
        self.assertIn("window.localStorage",routes)

    def test_published_pages_and_sitemap(self):
        if not (ROOT/"index.html").is_file():
            self.skipTest("Production site is not generated")
        route=(ROOT/ROUTE_PATH/"index.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="canonical" href="'+BASE+ROUTE_PATH+'"',route)
        self.assertEqual(route.count('data-cr-step='),157)
        self.assertEqual(route.count('data-cr-region='),7)
        self.assertIn('/assets/collectible-routes-v4.js?v=',route)
        self.assertIn('/assets/collectible-routes-v4.css?v=',route)
        intake=(ROOT/INTAKE_PATH/"index.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="canonical" href="'+BASE+INTAKE_PATH+'"',intake)
        self.assertEqual(intake.count('data-photo-guide='),55)
        self.assertIn("data-pi-rights",intake)
        self.assertIn("/assets/photo-intake-v4.js?v=",intake)
        self.assertIn("/assets/photo-intake-v4.css?v=",intake)
        self.assertIn("data-pi-fallback",intake)
        self.assertNotIn('type="file"',intake)
        sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
        for path in (ROUTE_PATH,INTAKE_PATH):self.assertIn(BASE+path,sitemap)
        for asset in ("collectible-routes-v4.js","collectible-routes-v4.css",
                      "photo-intake-v4.js","photo-intake-v4.css"):
            self.assertTrue((ROOT/"assets"/asset).is_file())
        audit=json.loads((ROOT/"photo-intake-audit.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["approved_new_community_photos"],0)
        self.assertEqual(audit["guide_role_examples"],55)
        self.assertFalse(audit["automatic_publication"])
        main=(ROOT/"screenshot-ps5/index.html").read_text(encoding="utf-8")
        self.assertIn(INTAKE_PATH,main)
        map_hub=(ROOT/"mappe-guide/index.html").read_text(encoding="utf-8")
        self.assertIn(ROUTE_PATH,map_hub)


if __name__=="__main__":unittest.main()
