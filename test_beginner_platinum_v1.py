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
                if t["number"]==23:
                    self.assertEqual(page.count('data-kenton-step='),10)
                    self.assertLess(page.index('data-kenton-tutorial'),page.index('class="tg-verify"'))
                    self.assertIn("5 set di Kenton su 7",page)
                    self.assertIn("non concordano",page)
                    self.assertIn("gta-6-maritime-dispute-stop-by-kentons-shop-walkthrough/",page)
                    self.assertIn("gta-6-underwater-discoveries-locations-and-kentons-treasures",page)
                    body=page.split('data-kenton-tutorial',1)[1].split('class="tg-verify"',1)[0]
                    self.assertNotIn('<img',body)
                    self.assertNotIn('<iframe',body)
                elif t["number"]==29:
                    self.assertEqual(page.count('data-bret-step='),7)
                    self.assertLess(page.index('data-bret-tutorial'),page.index('class="tg-verify"'))
                    self.assertIn("non confermano quale singolo animale",page)
                    self.assertIn("gta-6-veteran-hunted-meet-bret-walkthrough/",page)
                    self.assertIn("gta-6-brets-hunting-target-deck-locations",page)
                    self.assertIn("gta-6-all-brets-target-decks-locations-brets-hunts/",page)
                    self.assertEqual(page.count('data-bret-deck='),6)
                    self.assertIn('id="bret-target-decks"><summary>',page)
                    self.assertNotIn("quindicesimo è ancora in aggiornamento",page)
                    self.assertIn("tutti i 15 Target Decks",page)
                    self.assertIn('data-bret-deck="15"',page)
                    self.assertIn("Unique White Fox",page)
                    self.assertIn("Emerald Springs",page)
                    self.assertIn("Bret’s Rebel",page)
                    self.assertIn("Good o Pristine",page)
                    self.assertIn("Belpoint Island",page)
                    self.assertIn("nord di Belville",page)
                    self.assertIn("guide-e-tutorial/studiare-animali/",page)
                    body=page.split('data-bret-tutorial',1)[1].split('class="tg-verify"',1)[0]
                    self.assertNotIn('<img',body)
                    self.assertNotIn('<iframe',body)
                elif t.get("tip_it"):
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

    def test_linear_collectibles_use_same_real_items_and_places_map_afterward(self):
        page=(ROOT/"collezionabili/percorsi/index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('data-cr-step='),157)
        self.assertEqual(page.count('data-cr-done='),157)
        self.assertNotIn('data-cr-wizard',page)
        self.assertIn('data-article-cover="shared-social"',page)
        self.assertIn('class="cr-priority-links"',page)
        for ident in ('pt-102','pt-26','pt-66','pt-108','pt-111'):
            self.assertIn('href="#cr-'+ident+'"',page)
            self.assertIn('id="cr-'+ident+'"',page)
        self.assertIn('data-cr-deadline="1"',page)
        self.assertEqual(page.count('data-cr-deadline="1"'),5)
        self.assertEqual(page.count('data-cr-deadline="2"'),4)
        self.assertEqual(page.count('data-cr-deadline="3"'),2)
        self.assertEqual(page.count('data-cr-deadline="99"'),146)
        self.assertNotIn('collectible-beginner-v1.js?v=',page)
        self.assertIn('collectible-beginner-v1.css?v=',page)
        self.assertLess(page.index('class="cr-hero"'),page.index('data-cr-step="pt-01"'))
        self.assertLess(page.index('class="cr-priority-links"'),page.index('data-cr-step="pt-01"'))
        self.assertLess(page.index('data-cr-step="pt-01"'),page.index('class="cr-map-extra"'))
        self.assertIn('NON indica 157 pin esatti',page)
        self.assertIn("gta-6-all-under-the-bridges-locations/",page)
        self.assertIn("gta-6-all-no-flusher-tag-utility-markings-locations/",page)
        self.assertIn("Sottoponti: come registrarli",page)
        self.assertIn("No Flusher Tags",page)
        self.assertIn('id="radio-segrete"',page)
        self.assertIn("how-to-unlock-secret-radio-stations-in-gta-6",page)
        for ident in ("pt-01","pt-02","pt-03","pt-07","pt-09"):
            self.assertIn('href="#cr-'+ident+'"',page)
        self.assertIn('data-cr-filter="all"',page)
        self.assertIn('data-cr-query',page)
        self.assertIn('data-cr-bar',page)

    def test_no_js_original_content_and_no_network_shenanigans(self):
        for name in ("collectible-beginner-v1.js","collectible-beginner-v1.css","trophy-simple-v1.css"):
            self.assertTrue((ROOT/"assets"/name).is_file(),name)
        js=Path("site/assets/collectible-beginner-v1.js").read_text(encoding="utf-8")
        self.assertNotIn("slot.appendChild(step)",js)
        self.assertNotIn("anchor.replaceWith(active)",js)
        self.assertNotIn('found.addEventListener("click"',js)
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
