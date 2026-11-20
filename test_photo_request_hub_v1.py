"""Build-time proof that the photo request hub is truthful, safe and linked."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import json
import unittest

from photo_request_hub_v1 import render, screenshot_count, x_photo_intent, BASE
from visual_guide_content import enrich

TARGET = 5
ROOT = Path("_site")

def load_data():
    guides = json.loads(Path("data/guide.json").read_text(encoding="utf-8"))["guides"]
    guides += json.loads(Path("data/visual_guides.json").read_text(encoding="utf-8"))["guides"]
    guides = enrich(guides)
    requests = json.loads(Path("data/visual_requests.json").read_text(encoding="utf-8"))["guides"]
    media = json.loads(Path("data/visual_media.json").read_text(encoding="utf-8"))["images"]
    extras = json.loads(Path("data/guide_extras.json").read_text(encoding="utf-8"))["guides"]
    return guides, requests, media, extras


class CommunityPhotoHubTests(unittest.TestCase):
    def test_request_text_is_safe_length_limited_and_preserves_exact_guide(self):
        url = BASE + "salvare-auto/"
        link = x_photo_intent("Schermata del menu Register",url)
        parsed=urlsplit(link)
        self.assertEqual((parsed.scheme,parsed.hostname,parsed.path),
                         ("https","x.com","/intent/tweet"))
        text=parse_qs(parsed.query)["text"][0]
        self.assertIn("@xFederiko11",text)
        self.assertIn("#GTA6Italia",text)
        self.assertIn(url,text)
        self.assertLessEqual(len(text),280)
        for bad in (
            "http://xfederiko11.github.io/gta-6/salvare-auto/",
            "https://xfederiko11.github.io.evil.net/gta-6/salvare-auto/",
            "https://xfederiko11.github.io/gta-6.evil.test/",
            "https://xfederiko11.github.io/gta-6/../",
            "https://xfederiko11.github.io/gta-6/%2e%2e/",
            "https://xfederiko11.github.io/gta-6/salvare-auto/?utm_source=x",
            "https://xfederiko11.github.io/gta-6/salvare-auto/#spoilers",
            "https://www.powerpyx.com/gta-6/",
        ):
            with self.subTest(url=bad):
                with self.assertRaises(ValueError):
                    x_photo_intent("Menu del veicolo",bad)
        for role in ("x", "X"*180, "<script>"*25):
            with self.subTest(role=role):
                with self.assertRaises(ValueError):
                    x_photo_intent(role,url)

    def test_all_guides_have_real_editorial_roles_and_honest_counts(self):
        guides, requests, media, extras=load_data()
        available={"save-car","register-car","scooter-phone","scooter-menu","liquor-store","shirley-house","taxi-phone","taxi-ride"}
        body,report=render(guides,requests,media,extras,lambda key:key if key in available else None)
        self.assertEqual(report["schema"],"gta6-community-photo-requests-v1")
        self.assertEqual(report["guides"],len(guides))
        self.assertEqual(len(guides),11)
        self.assertEqual(report["photo_role_examples"],len(guides)*5)
        self.assertEqual(len(report["entries"]),11)
        self.assertEqual(body.count('data-photo-guide='),11)
        self.assertEqual(body.count('data-visual-request-photo='),55)
        self.assertEqual(body.count('<details class="v-photo-hub-details">'),11)
        self.assertNotIn("<iframe",body)
        self.assertNotIn('type="file"',body)
        self.assertNotIn("github.com/xFederiko11/gta-6/issues/",body)
        self.assertNotIn("followers-acquired",body)
        self.assertIn("non significa",body)
        self.assertIn("il consenso esplicito",body)
        for record in report["entries"]:
            g=next(g for g in guides if g["id"]==record["id"])
            n=screenshot_count(g,media,extras,lambda key:key if key in available else None)
            self.assertEqual(record["screenshot_count"],n)
            self.assertEqual(record["photo_prompts"],5)
            self.assertEqual(record["ready"],n>=5)
        # Promotional asset cannot improve a single game's screenshot score.
        for entry in media.values():
            self.assertIn(entry["kind"],("screenshot","promotional"))
        all_available=set(media)
        body2,r2=render(guides,requests,media,extras,
                        lambda key:key if key in all_available else None)
        self.assertEqual(r2["photo_role_examples"],55)
        self.assertGreaterEqual(r2["gameplay_screenshots_counted_across_guides"],
                                report["gameplay_screenshots_counted_across_guides"])
        self.assertNotIn('data-visual-kind="promotional"',body2)

    def test_bad_manifests_fail_before_publication(self):
        guides, requests, media, extras=load_data()
        with self.assertRaises(ValueError):
            render(guides[:-1],requests,media,extras,lambda _:None)
        corrupted=dict(requests); corrupted[guides[0]["id"]]=["Only one role"]
        with self.assertRaises(ValueError):
            render(guides,corrupted,media,extras,lambda _:None)

    def test_built_public_hub_is_discoverable_and_audit_matches_real_media(self):
        import xml.etree.ElementTree as ET
        from test_visual_site import parse
        hub=ROOT/"screenshot-ps5"/"index.html"
        html,tags=parse(hub)
        self.assertEqual(sum(tag=="h1" for tag,_ in tags.tags),1)
        self.assertIn('<link rel="canonical" href="'+BASE+'screenshot-ps5/"',html)
        self.assertIn('class="v-photo-hub-stats"',html)
        self.assertEqual(html.count('data-photo-guide='),11)
        self.assertEqual(html.count('data-visual-request-photo='),55)
        self.assertIn("Prepara su X",html)
        self.assertIn("Non",html)
        self.assertIn("permesso",html)
        self.assertNotIn("<iframe",html)
        self.assertNotIn('input type="file"',html)
        self.assertNotIn("l'immagine inviata",html)
        sitemap=ET.parse(ROOT/"sitemap.xml").getroot()
        urls=[node.text for node in sitemap.iter() if node.tag.endswith("loc")]
        self.assertIn(BASE+"screenshot-ps5/",urls)
        for path in ("index.html","salvare-auto/index.html","guide-e-tutorial/soldi-facili-capitolo-1/index.html"):
            self.assertIn(BASE+"screenshot-ps5/",(ROOT/path).read_text(encoding="utf-8"))
        audit=json.loads((ROOT/"photo-requests.json").read_text(encoding="utf-8"))
        media_report=json.loads((ROOT/"media-quality.json").read_text(encoding="utf-8"))
        self.assertEqual(media_report["guides_checked"],audit["guides"])
        self.assertEqual(audit["guides_at_target"],media_report["ready"])
        self.assertEqual(audit["photo_role_examples"],55)
        by_path={r["path"]:r for r in media_report["pages"]}
        for entry in audit["entries"]:
            key=entry["path"]+"index.html"
            self.assertEqual(entry["screenshot_count"],by_path[key]["real_step_screenshots"])
        # Analytics is present only when the actual build opted into it.
        if 'id="growth-analytics-v1"' in html:
            self.assertEqual(html.count('data-umami-event="x-screenshot-intent"'),55)
        else:
            self.assertNotIn('data-umami-event=',html)


if __name__=="__main__":
    unittest.main()
