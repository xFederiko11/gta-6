"""Offline tests for explicit analytics activation and privacy boundaries."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch
import unittest

from build_site import analytics_scripts, layout


class AnalyticsTests(unittest.TestCase):
    def test_no_analytics_code_means_no_requesting_provider(self):
        with patch.dict(os.environ, {"GOATCOUNTER_CODE": ""}):
            self.assertEqual(analytics_scripts(), "")
            page=layout("Pagina test", "Descrizione", "privacy/", "<p>OK</p>")
            self.assertNotIn("data-analytics-endpoint",page)
            self.assertNotIn("gc.zgo.at",page)

    def test_only_a_valid_public_site_subdomain_activates(self):
        with patch.dict(os.environ, {"GOATCOUNTER_CODE": "gta6italia"}):
            html=analytics_scripts()
            self.assertIn('data-analytics-endpoint="https://gta6italia.goatcounter.com/count"',html)
            self.assertIn("assets/site-analytics.js",html)
            self.assertNotIn("gc.zgo.at/count.js",html)
            page=layout("Test", "Test", "privacy/", "<p>OK</p>")
            self.assertIn('data-analytics-endpoint="https://gta6italia.goatcounter.com/count"',page)
        for bad in ("https://attacker.example", "has.dot", "foo/bar",
                    "my\" onload=bad", "UPPERCASE", "-invalid", "invalid-",
                    "x"*65, "a b", "abc\nscript"):
            with self.subTest(site_code=bad), patch.dict(os.environ, {"GOATCOUNTER_CODE": bad}):
                with self.assertRaises(ValueError):
                    analytics_scripts()

    def test_script_respects_dnt_and_collects_only_categorized_clicks(self):
        script=Path("site/assets/site-analytics.js").read_text(encoding="utf-8")
        self.assertIn("navigator.globalPrivacyControl",script)
        self.assertIn("navigator.doNotTrack",script)
        self.assertIn('window.location.hostname !== "xfederiko11.github.io"',script)
        with patch.dict(os.environ, {"GOATCOUNTER_CODE": "gta6italia"}):
            self.assertIn("data-analytics-endpoint", analytics_scripts())
        self.assertIn('event: true',script)
        self.assertIn('no_session: true',script)
        self.assertIn("provider.dataset.goatcounter",script)
        self.assertIn("sitePath(",script)
        self.assertIn("location.pathname",script)
        self.assertNotIn("localStorage",script)
        self.assertNotIn("sessionStorage",script)
        self.assertNotIn("location.search",script)
        self.assertNotIn("document.cookie",script)
        self.assertNotIn("email",script)
        self.assertNotIn("JSON.stringify",script)
        self.assertIn("source-details",script)
        self.assertIn("recommended",script)

    def test_comparison_is_based_on_actual_page_and_click_events(self):
        script=Path("site/assets/site-analytics.js").read_text(encoding="utf-8")
        for interaction in ("copy-guide-steps", "copy-hdr-values",
                            "copy-cheat-sequence", "play-source-video",
                            "play-official-video"):
            self.assertIn(interaction,script)
        for destination in ("site-", "external-", "powerpyx", "gtabase",
                            "social-x", "playstation", "youtube"):
            self.assertIn(destination,script)


if __name__ == "__main__":
    unittest.main()
