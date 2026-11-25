"""Offline tests: 21 linked manufacturer photo galleries + verified HDR Game tables."""
from __future__ import annotations
import json
from pathlib import Path
import unittest
from hdr_tv_picture_v1 import (validate, validate_photos, photo_info,
                               render_reference, render_settings)

BASE = "https://xfederiko11.github.io/gta-6/"
def url(path):
    return BASE + path


class HDRTVPictureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(Path("data/hdr_oled.json").read_text(encoding="utf-8"))
        cls.profiles = json.loads(Path("data/hdr_tv_picture_v1.json").read_text(encoding="utf-8"))
        cls.photos = json.loads(Path("data/hdr_tv_photo_sources_v1.json").read_text(encoding="utf-8"))

    def get(self, slug):
        return next(f for f in self.data["families"] if f["slug"] == slug)

    def test_catalog_integrity_and_no_invented_family(self):
        self.assertTrue(validate(self.data["families"]))
        self.assertTrue(validate_photos(self.data["families"]))
        self.assertEqual(len(self.data["families"]),21)
        self.assertEqual(sum(len(f["models"]) for f in self.data["families"]),92)
        self.assertEqual(len(self.photos["families"]),21)
        self.assertEqual(len(self.profiles["profiles"]),19)
        self.assertEqual(set(self.data["families"][i]["slug"] for i in range(len(self.data["families"]))) - set(self.profiles["profiles"]), {"philips-oled811", "philips-oled850"})
        self.assertEqual(self.profiles["profiles"]["lg-oled-c4"]["reference_code"],
                         "OLED55C44LA")

    def test_each_family_has_original_graphic_and_one_manufacturer_photo_link(self):
        artwork=Path("site/assets/hdr-tv-reference-v1.svg").read_text(encoding="utf-8")
        self.assertTrue(artwork.startswith("<svg"))
        self.assertNotIn("<script", artwork)
        for family in self.data["families"]:
            with self.subTest(family=family["slug"]):
                markup=render_reference(family,url)
                self.assertIn('class="hdr-tv-reference"',markup)
                self.assertIn('src="' + BASE + 'assets/hdr-tv-reference-v1.svg"', markup)
                self.assertIn(family["series"], markup)
                self.assertIn(family["brand"], markup)
                self.assertIn('data-hdr-photo-gallery="'+family["slug"]+'"', markup)
                self.assertIn("foto reali",markup)
                self.assertIn("Illustrazione originale",markup)
                self.assertIn("non",markup)
                self.assertIn('target="_blank" rel="noopener noreferrer"',markup)
                self.assertIn(photo_info(family)["photo_page_url"].replace("&","&amp;"),markup)
                self.assertIn(photo_info(family)["reference_code"],markup)

    def test_region_caveat_prevents_image_model_mismatch(self):
        for slug in ("samsung-s90f","samsung-s95f","samsung-s95d","sony-a80l"):
            with self.subTest(slug=slug):
                markup=render_reference(self.get(slug),url)
                entry=self.photos["families"][slug]
                self.assertIn("variante regionale",markup)
                self.assertIn(entry["pictured_region_code"],markup)
                self.assertNotEqual(entry["reference_code"],entry["pictured_region_code"])
        for slug in ("sony-bravia-8-ii","sony-bravia-8"):
            self.assertIn("non necessariamente il taglio",render_reference(self.get(slug),url))

    def test_c4_settings_keep_sources_and_sdr_warning(self):
        html=render_settings(self.get("lg-oled-c4"))
        self.assertIn("Luminosità pixel OLED",html)
        self.assertIn("<strong>100</strong>",html)
        self.assertIn("Alto (High)",html)
        self.assertIn("HGiG",html)
        self.assertIn("https://www.rtings.com/tv/reviews/lg/c4-oled",html)
        self.assertEqual(html.count("hdr-tv-status-verified"),8)
        self.assertEqual(html.count("hdr-tv-status-warning"),3)
        self.assertIn("Solo riferimento SDR",html)
        self.assertIn("42 e 48 pollici",html)
        self.assertIn("NON test HDR gioco",html)
        self.assertNotIn("Max Brightness</th>",html)
        self.assertNotIn("Paper White</th>",html)

    def test_provenance_and_model_specific_values(self):
        for slug,profile in self.profiles["profiles"].items():
            with self.subTest(slug=slug):
                markup=render_settings(self.get(slug))
                self.assertIn('class="hdr-tv-settings-table"',markup)
                self.assertIn("RTINGS",markup)
                self.assertIn("impostazioni HDR Game documentate",markup)
                self.assertIn(profile["tested_hardware"],markup.replace("&amp;","&"))
                self.assertEqual(markup.count("hdr-tv-status-verified"),
                                 sum(x["status"] in ("Test HDR","Verifica HDMI") for x in profile["rows"]))
                for row in profile["rows"]:
                    self.assertIn(row["name"],markup)
                    self.assertIn(row["value"],markup)
                self.assertIn("non una calibrazione GTA VI",markup)

    def test_unknown_families_fail_closed_without_numeric_preset(self):
        for family in self.data["families"]:
            if family["slug"] in self.profiles["profiles"]:continue
            with self.subTest(family=family["slug"]):
                html=render_settings(family)
                self.assertIn("Non verificato",html)
                self.assertIn("Da verificare",html)
                self.assertIn("Nessuna misura numerica HDR affidabile",html)
                self.assertNotIn("Test HDR",html)
                self.assertEqual(html.count('<tr><th scope="row">'),7)

    def test_photo_references_and_profiles_reject_unknown_panels(self):
        without_c4=[f for f in self.data["families"] if f["slug"]!="lg-oled-c4"]
        with self.assertRaises(ValueError):validate(without_c4)
        with self.assertRaises(ValueError):validate_photos(without_c4)


if __name__ == "__main__":
    unittest.main()
