"""Offline checks for model-labelled TV artwork and evidence-based on-TV HDR values."""
from __future__ import annotations
import json
from pathlib import Path
import unittest
from hdr_tv_picture_v1 import validate, render_reference, render_settings

BASE = "https://xfederiko11.github.io/gta-6/"
def url(path):
    return BASE + path

class HDRTVPictureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(Path("data/hdr_oled.json").read_text(encoding="utf-8"))
        cls.profiles = json.loads(Path("data/hdr_tv_picture_v1.json").read_text(encoding="utf-8"))

    def get(self, slug):
        return next(f for f in self.data["families"] if f["slug"] == slug)

    def test_catalog_reference_integrity(self):
        self.assertTrue(validate(self.data["families"]))
        self.assertEqual(len(self.data["families"]), 21)
        self.assertEqual(sum(len(f["models"]) for f in self.data["families"]), 92)
        self.assertEqual(set(self.profiles["profiles"]), {"lg-oled-c4"})
        self.assertEqual(self.profiles["profiles"]["lg-oled-c4"]["reference_code"], "OLED65C44LA")

    def test_each_model_has_identifiable_local_illustration_and_manufacturer_link(self):
        original = Path("site/assets/hdr-tv-reference-v1.svg").read_text(encoding="utf-8")
        self.assertTrue(original.startswith("<svg"))
        self.assertNotIn("<script", original)
        self.assertIn("non", original.lower())
        for family in self.data["families"]:
            with self.subTest(family=family["slug"]):
                markup = render_reference(family, url)
                self.assertIn('class="hdr-tv-reference"', markup)
                self.assertIn('src="' + BASE + 'assets/hdr-tv-reference-v1.svg"', markup)
                self.assertIn(family["series"], markup)
                self.assertIn(family["brand"], markup)
                self.assertIn(family["year"].__str__(), markup)
                self.assertIn('target="_blank" rel="noopener noreferrer"', markup)
                self.assertIn("non foto", markup)
                self.assertIn("fotografie ufficiali", markup)

    def test_numeric_values_c4_only_with_hdr_evidence_separate_from_sdr(self):
        c4 = render_settings(self.get("lg-oled-c4"))
        self.assertIn('class="hdr-tv-settings-table"', c4)
        self.assertIn("Luminosità pixel OLED", c4)
        self.assertIn("<strong>100</strong>", c4)
        self.assertIn("Contrasto", c4)
        self.assertIn("Alto (High)", c4)
        self.assertIn("HGiG", c4)
        self.assertIn("https://www.rtings.com/tv/reviews/lg/c4-oled", c4)
        self.assertEqual(c4.count("hdr-tv-status-verified"), 8)
        self.assertEqual(c4.count("hdr-tv-status-warning"), 3)
        self.assertIn("Solo riferimento SDR", c4)
        self.assertIn("42 e 48 pollici", c4)
        self.assertIn("NON test HDR gioco", c4)
        self.assertNotIn("Max Brightness</th>", c4)
        self.assertNotIn("Black Levels</th>", c4)
        self.assertNotIn("Paper White</th>", c4)

    def test_other_families_do_not_inherit_c4_brightness(self):
        for family in self.data["families"]:
            if family["slug"] == "lg-oled-c4":
                continue
            with self.subTest(family=family["slug"]):
                html = render_settings(family)
                self.assertIn("Non verificato", html)
                self.assertIn("Da verificare", html)
                self.assertIn("Nessuna misura numerica HDR affidabile", html)
                self.assertNotIn("Test HDR", html)
                self.assertNotIn("Solo riferimento SDR", html)
                self.assertEqual(html.count('<tr>'), 7)

    def test_json_profiles_cannot_silently_reference_unknown_panel(self):
        altered = list(self.data["families"])
        altered = [f for f in altered if f["slug"] != "lg-oled-c4"]
        with self.assertRaises(ValueError):
            validate(altered)

if __name__ == "__main__":
    unittest.main()
