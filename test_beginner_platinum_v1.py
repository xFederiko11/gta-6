"""Every trophy has one obvious true objective; collectible guidance cannot forge locations or progress."""
from __future__ import annotations
from pathlib import Path
from html import escape
import json
import unittest

ROOT=Path("_site")

class BeginnerPlatinumTests(unittest.TestCase):
    def test_all_fifty_five_trophies_start_with_one_unambiguous_objective(self):
        trophies=json.loads(Path("data/trofei.json").read_text(encoding="utf-8"))["trophies"]
        self.assertEqual(len(trophies),55)
        for t in trophies:
            with self.subTest(number=t["number"],name=t["name_it"]):
                page=(ROOT/"trofei"/t["slug"]/"index.html").read_text(encoding="utf-8")
                self.assertEqual(page.count('data-trophy-beginner'),1)
                self.assertEqual(page.count('id="requisito"'),1)
                self.assertEqual(page.count('class="tg-goal"'),1)
                self.assertIn('trophy-simple-v1.css?v=',page)
                self.assertIn(escape(t["requirement_it"],quote=True),page)
                self.assertIn("▶ QUESTA È LA GUIDA",page)
                self.assertIn("COME CAPIRE SE HAI FINITO",page)
                self.assertEqual(page.count('data-trophy-done="'+str(t["number"])+'"'),1)
                self.assertIn("Solo in questo browser. Non modifica i trofei PSN.",page)
                self.assertLess(page.index('class="tg-goal"'),page.index('data-trophy-done='))
                self.assertLess(page.index('data-trophy-done='),page.index('class="source-details"'))
                self.assertIn('class="tg-extra"',page)
                self.assertIn('class="tg-extra tg-related"',page)
                if t.get("tip_it"):
                    self.assertIn(escape(t["tip_it"],quote=True),page)
                    self.assertIn("CONSIGLIO DOCUMENTATO",page)
                else:
                    self.assertIn("Nessun passaggio extra confermato",page)

    def test_cecchino_checklist_is_still_complete_but_optional_to_expand(self):
        page=(ROOT/"trofei/trofeo-17-cecchino/index.html").read_text(encoding="utf-8")
        self.assertIn('<details class="tg-deep" id="dettagli-cecchino">',page)
        self.assertIn("APRI LA CHECKLIST DELLE 42 MEDAGLIE",page)
        self.assertEqual(page.count('data-medal-id='),42)
        self.assertEqual(page.count('class="medal-course"'),12)
        self.assertEqual(page.count('class="medal-group"'),2)
        self.assertIn('data-medal-tracker',page)
        self.assertIn('trophy-experience.js',page)

    def test_collectible_wizard_uses_same_real_items_and_places_map_afterward(self):
        page=(ROOT/"collezionabili/percorsi/index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('data-cr-step='),123)
        self.assertEqual(page.count('data-cr-done='),123)
        self.assertEqual(page.count('data-cr-wizard hidden'),1)
        self.assertIn('data-cr-wizard-found',page)
        self.assertIn('data-cr-wizard-skip',page)
        self.assertIn('data-cr-wizard-back',page)
        self.assertIn('data-cr-wizard-toggle',page)
        self.assertIn('data-cr-deadline="1"',page)
        self.assertEqual(page.count('data-cr-deadline="1"'),5)
        self.assertEqual(page.count('data-cr-deadline="2"'),4)
        self.assertEqual(page.count('data-cr-deadline="3"'),2)
        self.assertEqual(page.count('data-cr-deadline="99"'),112)
        self.assertIn('collectible-beginner-v1.js?v=',page)
        self.assertIn('collectible-beginner-v1.css?v=',page)
        self.assertLess(page.index('data-cr-wizard hidden'),page.index('class="cr-hero"'))
        self.assertLess(page.index('data-cr-wizard hidden'),page.index('data-cr-step="pt-01"'))
        self.assertLess(page.index('data-cr-step="pt-01"'),page.index('class="cr-map-extra"'))
        self.assertIn('NON indica 123 pin esatti',page)
        self.assertIn('data-cr-filter="all"',page)
        self.assertIn('data-cr-query',page)
        self.assertIn('data-cr-bar',page)

    def test_no_js_original_content_and_no_network_shenanigans(self):
        for name in ("collectible-beginner-v1.js","collectible-beginner-v1.css","trophy-simple-v1.css"):
            self.assertTrue((ROOT/"assets"/name).is_file(),name)
        js=Path("site/assets/collectible-beginner-v1.js").read_text(encoding="utf-8")
        self.assertIn("slot.appendChild(step)",js)
        self.assertIn("anchor.replaceWith(active)",js)
        self.assertIn('window.addEventListener("hashchange"',js)
        self.assertIn('found.addEventListener("click"',js)
        self.assertNotIn("fetch(",js)
        self.assertNotIn("api.psn",js.lower())
        self.assertNotIn("<img",js)
        html=(ROOT/"collezionabili/percorsi/index.html").read_text(encoding="utf-8")
        self.assertNotIn('class="cr-step" hidden',html)
        self.assertNotIn('hidden class="cr-step"',html)
        for path in ("index.html","trofei/index.html","hdr-oled/index.html"):
            page=(ROOT/path).read_text(encoding="utf-8")
            self.assertNotIn('trophy-simple-v1.css?v=',page)
            self.assertNotIn('collectible-beginner-v1.js?v=',page)

if __name__ == "__main__":
    unittest.main()
