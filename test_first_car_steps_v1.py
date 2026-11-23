"""Offline and generated-page QA for first-car editorial pilot."""
from copy import deepcopy
from pathlib import Path
import json
import unittest

from first_car_steps_v1 import ACTIONS, CHECKS, render, validate
from visual_guide_content import enrich

ROOT=Path("_site")
CANON="https://xfederiko11.github.io/gta-6/salvare-auto/"

def guide():
    records=json.loads(Path("data/visual_guides.json").read_text(encoding="utf-8"))["guides"]
    return next(x for x in enrich(records) if x["id"]=="registrare-auto-personale")

class FirstCarPilotTests(unittest.TestCase):
    def test_exactly_seven_source_checked_player_steps(self):
        g=guide()
        self.assertTrue(validate(g))
        self.assertEqual(len(g["steps"]),7)
        self.assertEqual(len(g["step_headings"]),7)
        self.assertEqual(len(g["checks"]),7)
        self.assertEqual(len(ACTIONS),7)
        self.assertTrue(all(len(x)==3 for x in ACTIONS))
        self.assertEqual(len(CHECKS),7)
        self.assertIn("Watkins Auto Parts",g["steps"][0])
        self.assertIn("WAiNK",g["steps"][1])
        self.assertIn("Slim Jim",g["steps"][2])
        self.assertIn("senza tracker",g["steps"][3])
        self.assertIn("Respray",g["steps"][4])
        self.assertIn("Register",g["steps"][5])
        self.assertIn("Scooter Bros",g["steps"][6])
        self.assertIn("Daily Driver",g["benefit"])
        self.assertIn("prima registrazione",g["requirements"])
        for n in range(7):
            fragment=render(n)
            self.assertEqual(fragment.count('class="car-microstep"'),3,n)
            self.assertNotIn("<img",fragment)
            self.assertNotIn("<iframe",fragment)
        for n in (-1,7,99):
            with self.assertRaises(ValueError):
                render(n)

    def test_invalid_source_or_lost_guide_steps_fail_closed(self):
        broken=deepcopy(guide())
        broken["steps"].pop()
        with self.assertRaises(ValueError):
            validate(broken)
        broken=deepcopy(guide())
        broken["benefit"]="Garage subito senza missioni"
        with self.assertRaises(ValueError):
            validate(broken)

    def test_generated_article_matches_source_and_rights(self):
        path=ROOT/"salvare-auto"/"index.html"
        if not path.exists():
            self.skipTest("Build generated later in GitHub Actions")
        page=path.read_text(encoding="utf-8")
        self.assertIn('rel="canonical" href="'+CANON+'"',page)
        self.assertEqual(page.count('class="v-step"'),7)
        self.assertEqual(page.count('class="car-microsteps"'),7)
        self.assertEqual(page.count('class="car-microstep"'),21)
        self.assertIn("car-story-warning",page)
        self.assertIn("Scooter Bros si sblocca",page)
        self.assertIn("si sbloccano dopo Daily Driver",page)
        self.assertNotIn("Inizia dall’officina dove la storia ha sbloccato Register",page)
        self.assertIn("Watkins Auto Parts",page)
        self.assertIn("Guarda la schermata sul sito originale",page)
        self.assertEqual(page.count('data-photo-source-guide="registrare-auto-personale"'),7)
        self.assertNotIn('data-visual-proof-image="scooter-phone"',page)
        for n in range(1,8):
            step=page.split('id="passaggio-'+str(n)+'"',1)[1]
            if n<7:
                step=step.split('id="passaggio-'+str(n+1)+'"',1)[0]
            self.assertEqual(step.count('class="car-microsteps"'),1,n)
            self.assertEqual(step.count('class="car-microstep"'),3,n)
            self.assertIn('data-photo-source-step="'+str(n)+'"',step)
            self.assertIn("✓ Controllo",step)
        self.assertIn("data-step-external-evidence=\"map\"",page)
        self.assertIn("data-step-external-evidence=\"video\"",page)

if __name__=="__main__":
    unittest.main()
