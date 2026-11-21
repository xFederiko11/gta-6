"""Regression tests for screenshot provenance, trophy solutions and the 100% tracker."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json
import unittest

from advanced_platinum_v3 import (validate as verify_advanced, render_100, render_hard,
                                  COLLECTIBLE_PATH, HARD_PATH)
from photo_provenance_v3 import (validate as verify_photos,render as render_photos,
                                 PATH as PHOTO_PATH)
from visual_guide_content import enrich

ROOT=Path("_site")
BASE="https://xfederiko11.github.io/gta-6/"

def sources():
    read=lambda file:json.loads(Path(file).read_text(encoding="utf-8"))
    trophies=read("data/trofei.json")["trophies"]
    records=read("data/guide.json")["guides"]+read("data/visual_guides.json")["guides"]
    guides=enrich(records)
    advanced=read("data/advanced_platinum_v3.json")
    photo=read("data/photo_provenance_review_v3.json")
    media=read("data/visual_media.json")["images"]
    return trophies,guides,advanced,photo,media

class AdvancedPlatinumTests(unittest.TestCase):
    def test_exactly_35_requirements_and_18_card_sets(self):
        trophies,_,data,_,_=sources()
        self.assertTrue(verify_advanced(data,trophies))
        self.assertEqual(len(data["requirements"]),35)
        self.assertEqual(len(data["cards"]),18)
        self.assertEqual(sum(x["total"] for x in data["cards"]),480)
        self.assertEqual(sum(x["total"] for x in sorted(data["cards"],key=lambda x:x["total"])[:15]),372)
        for target in (("Set di carte completi",15),("Medaglie Oro poligoni",42),
                       ("Meditazioni",15),("Acrobazie",300),("Modelli base veicoli WAiNK",200),
                       ("Animali studiati",100)):
            self.assertEqual(next(x["target"] for x in data["requirements"] if x["label"]==target[0]),target[1])
        markup=render_100(data,trophies)
        self.assertEqual(markup.count('data-ap-metric="'),35)
        self.assertEqual(markup.count('data-ap-card="'),18)
        self.assertIn("35 categorie",markup)
        self.assertIn("372 carte",markup)
        self.assertIn("Progressi",markup)
        self.assertNotIn("data-psn",markup)
        altered=deepcopy(data)
        altered["requirements"][0]["target"]=2
        with self.assertRaises(ValueError):verify_advanced(altered,trophies)
        altered=deepcopy(data)
        altered["cards"][0]["total"]=50
        with self.assertRaises(ValueError):verify_advanced(altered,trophies)

    def test_hard_trophies_still_distinguish_facts_and_uncertainty(self):
        trophies,_,data,_,_=sources()
        markup=render_hard(data,trophies)
        self.assertEqual(markup.count('data-hard-trophy="'),7)
        self.assertIn("Mile Zero Air Station",markup)
        self.assertIn("Starlet Motel",markup)
        self.assertIn("Gutterball Moreland 850",markup)
        self.assertIn("Forza",markup)
        self.assertIn('data-hard-status="incerto"',markup)
        self.assertIn("non li copiamo",markup)
        self.assertNotIn('<img ',markup)
        self.assertNotIn('<iframe',markup)
        for n in (38,46,47,48,49,50,30):
            self.assertIn('data-hard-trophy="'+str(n)+'"',markup)
        assert 49 in {x["trophy"] for x in data["hard"] if x["status"]=="incerto"}
        bad=deepcopy(data)
        next(x for x in bad["hard"] if x["trophy"]==49)["status"]="documentato"
        with self.assertRaises(ValueError):verify_advanced(bad,trophies)
        for n in (38,46,47,50):
            trophy=next(t for t in trophies if t["number"]==n)
            self.assertIsNotNone(trophy.get("tip_it"))

    def test_photo_provenance_is_not_a_licence_or_new_image(self):
        _,guides,_,photo,media=sources()
        self.assertTrue(verify_photos(photo,media,guides))
        self.assertEqual(len(photo["assets"]),10)
        self.assertEqual(len(photo["leads"]),8)
        html=render_photos(photo,media,guides,lambda key:None)
        self.assertEqual(html.count('data-provenance-key='),10)
        self.assertEqual(html.count('data-photo-source-lead='),8)
        self.assertIn('data-photo-review-ledger',html)
        self.assertIn("permesso specifico",html)
        self.assertIn("10 immagini",html)
        self.assertNotIn("<img",html)
        self.assertNotIn("srcset=",html)
        self.assertIn("Non sono stati importati screenshot aggiuntivi",html)
        enabled=render_photos(photo,media,guides,lambda key:BASE+"assets/visual/"+key+".webp")
        self.assertIn("10</strong><small>asset locali disponibili",enabled)
        fake=deepcopy(photo)
        fake["assets"][0]["reuse_permission"]="granted"
        with self.assertRaises(ValueError):verify_photos(fake,media,guides)
        fake=deepcopy(photo)
        fake["leads"][0]["copy_to_site"]=True
        with self.assertRaises(ValueError):verify_photos(fake,media,guides)

    def test_pages_exist_with_canonical_and_correct_asset_links(self):
        if not (ROOT/"index.html").is_file():self.skipTest("build not present")
        for path, marker in (
            (COLLECTIBLE_PATH,'data-advanced-platinum-100'),
            (HARD_PATH,'data-hard-trophy="49"'),
            (PHOTO_PATH,'data-photo-review-ledger')
        ):
            text=(ROOT/path/"index.html").read_text(encoding="utf-8")
            self.assertIn(marker,text)
            self.assertIn('<link rel="canonical" href="'+BASE+path+'"',text)
            self.assertIn('data-design-version="visual-v2-20261120"',text)
            self.assertNotIn("token=",text)
        hundred=(ROOT/COLLECTIBLE_PATH/"index.html").read_text(encoding="utf-8")
        self.assertEqual(hundred.count('data-ap-metric="'),35)
        self.assertEqual(hundred.count('data-ap-card="'),18)
        self.assertIn("/assets/advanced-platinum-v3.js?v=",hundred)
        self.assertIn("/assets/advanced-platinum-v3.css?v=",hundred)
        hard=(ROOT/HARD_PATH/"index.html").read_text(encoding="utf-8")
        self.assertIn("/assets/advanced-platinum-v3.css?v=",hard)
        self.assertNotIn("/assets/advanced-platinum-v3.js?v=",hard)
        photo=(ROOT/PHOTO_PATH/"index.html").read_text(encoding="utf-8")
        self.assertEqual(photo.count('data-provenance-key='),10)
        self.assertEqual(photo.count('data-photo-source-lead='),8)
        sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
        for path in (COLLECTIBLE_PATH,HARD_PATH,PHOTO_PATH):
            self.assertIn(BASE+path,sitemap)
        ledger=json.loads((ROOT/"photo-provenance-review.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger["new_images_rehosted"],0)
        self.assertEqual(ledger["permission_records_verified"],0)
        self.assertEqual(ledger["editorial_leads"],8)
        for asset in ("advanced-platinum-v3.css","advanced-platinum-v3.js"):
            self.assertTrue((ROOT/"assets"/asset).is_file())

    def test_js_local_only_and_without_remote_sync(self):
        js=Path("site/assets/advanced-platinum-v3.js").read_text(encoding="utf-8")
        self.assertIn("gta6-italia:100-completion:v3",js)
        self.assertIn("gta6-italia:card-sets:v3",js)
        self.assertIn("window.localStorage",js)
        for bad in ("fetch(","XMLHttpRequest","api.github.com","api.psn","innerHTML",
                    "navigator.credentials","https://","eval("):
            self.assertNotIn(bad,js)

if __name__=="__main__": unittest.main()
