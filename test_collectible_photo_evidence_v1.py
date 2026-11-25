"""PS5 photo proof: eleven critical collectibles, zero invented image licenses."""
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlsplit
import json
import unittest

from collectible_photo_evidence_v1 import validate, render

ROOT = Path("_site")
BASE = "https://xfederiko11.github.io/gta-6/"
REQ = {"pt-102","pt-103","pt-104","pt-105","pt-106","pt-26","pt-66",
       "pt-108","pt-109","pt-111","pt-112"}


def fixture():
    routes = json.loads(Path("data/collectible_routes_v4.json").read_text(encoding="utf-8"))
    photos = json.loads(Path("data/collectible_photo_evidence_v1.json").read_text(encoding="utf-8"))
    return routes,photos


class CollectiblePhotoProofTests(unittest.TestCase):
    def test_all_and_only_critical_points_have_editorial_source_links(self):
        routes,photos = fixture()
        self.assertTrue(validate(photos,routes))
        self.assertEqual(len(routes["points"]),123)
        self.assertEqual({x["checkpoint_id"] for x in photos["requests"]},REQ)
        self.assertEqual(photos["approved_photos"],[])
        for item in routes["points"]:
            markup = render(item,photos,routes)
            if item["id"] in REQ:
                with self.subTest(item=item["id"]):
                    self.assertIn('data-cr-photo-state="source-only"',markup)
                    self.assertIn(routes["sources"][item["source"]],markup)
                    self.assertIn("Fonte:",markup)
                    self.assertIn("foto non copiata",markup)
                    self.assertNotIn("<img",markup)
            else:
                self.assertEqual(markup,"")

    def test_an_unlicensed_picture_cannot_be_sneaked_into_the_site(self):
        routes,photos = fixture()
        fake=deepcopy(photos)
        fake["approved_photos"]=[{
            "checkpoint_id":"pt-26","file":"assets/approved/collectible-pt-26.webp",
            "platform":"PS5","human_reviewed":False,"author_confirmed":False,
            "rights":"none","published":False,"source_post":"https://x.com/bot/status/12345678",
            "consent_evidence":"https://x.com/bot/status/12345678",
        }]
        with self.assertRaisesRegex(ValueError,"human rights review"):
            validate(fake,routes)
        rogue=deepcopy(photos)
        rogue["requests"][0]["approved"]=True
        with self.assertRaisesRegex(ValueError,"self-certify"):
            validate(rogue,routes)
        missing=deepcopy(photos)
        missing["requests"].pop()
        with self.assertRaises(ValueError):
            validate(missing,routes)
        altered=deepcopy(photos)
        altered["requests"][0]["checkpoint_id"]="pt-99"
        with self.assertRaises(ValueError):
            validate(altered,routes)

    def test_generated_page_shows_steps_and_photo_source_in_correct_order(self):
        page=(ROOT/"collezionabili/percorsi/index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('data-cr-photo-state="source-only"'),11)
        self.assertEqual(page.count('data-cr-photo-state="approved"'),0)
        self.assertEqual(page.count('data-cr-photo-checkpoint='),11)
        self.assertEqual(page.count('class="cr-instruction-where"'),123)
        self.assertEqual(page.count('class="cr-instruction-do"'),123)
        self.assertIn("collectible-photo-v1.css?v=",page)
        self.assertIn("Apri le immagini e la posizione sulla fonte originale",page)
        self.assertNotIn("TROVATO → PROSSIMO",page)
        self.assertNotIn("Salta questo",page)
        self.assertNotIn('data-cr-wizard',page)
        self.assertEqual(page.count('data-cr-done='),123)
        self.assertIn('data-article-cover="shared-social"',page)
        self.assertNotIn("photo-backlog-v5.json",page)
        for ident in REQ:
            with self.subTest(id=ident):
                section = page.split('id="cr-'+ident+'"',1)[1].split("</li>",1)[0]
                self.assertIn('data-cr-photo-checkpoint="'+ident+'"',section)
                self.assertLess(section.index("1 · VAI QUI"),
                                section.index("2 · FAI QUESTO"))
                self.assertLess(section.index("2 · FAI QUESTO"),
                                section.index('data-cr-photo-checkpoint='))
                self.assertLess(section.index('data-cr-photo-checkpoint='),
                                section.index('class="cr-step-extra"'))
        self.assertEqual(page.count('data-cr-step='),123)

    def test_no_internal_photo_registry_is_shipped_to_public_pages(self):
        # The hard release gate strips these documents on deployed Pages,
        # while retaining them inside the repository for editorial QA.
        from public_release_gate import PRIVATE_PREFIXES,PRIVATE_FILES
        self.assertIn("screenshot-ps5/verifica/",PRIVATE_PREFIXES)
        self.assertIn("screenshot-ps5/priorita/",PRIVATE_PREFIXES)
        self.assertIn("photo-backlog-v5.json",PRIVATE_FILES)
        self.assertIn("photo-provenance-review.json",PRIVATE_FILES)


if __name__ == "__main__":
    unittest.main()
