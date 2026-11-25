"""Verified WAiNK mechanics from PowerPyx/GTABase, not copied infographics."""
import json
from pathlib import Path
import unittest
from visual_guide_content import enrich

ROOT=Path("_site")
GUIDE_ID="scansionare-veicoli"
PATH=ROOT/"guide-e-tutorial"/GUIDE_ID/"index.html"

def load():
    data=json.loads(Path("data/guide.json").read_text(encoding="utf-8"))
    return next(x for x in enrich(data["guides"]) if x["id"]==GUIDE_ID)

class WainkVerifiedGuide(unittest.TestCase):
    def test_story_and_collection_distinctions(self):
        g=load()
        self.assertEqual(len(g["steps"]),5)
        self.assertEqual(len(g["checks"]),5)
        self.assertEqual(len(g["step_headings"]),5)
        self.assertIn("↑",g["steps"][0])
        self.assertIn("R1",g["steps"][2])
        self.assertIn("No Tracker",g["steps"][3])
        self.assertIn("Standard",g["steps"][3])
        self.assertIn("Advanced",g["steps"][3])
        self.assertIn("200 dei 277",g["benefit"])
        self.assertIn("100 WAiNK Locations",g["benefit"])
        self.assertIn("280",g["benefit"])
        self.assertIn("Key Cloner",g["caution"])
        self.assertIn("Capitolo 3",g["caution"])
        self.assertEqual(len(g["extra_sources"]),4)
        self.assertFalse(g["spoiler"])

    def test_generated_page_avoids_misleading_photography(self):
        if not PATH.exists():
            self.skipTest("CI generates article")
        html=PATH.read_text(encoding="utf-8")
        self.assertIn('rel="canonical" href="https://xfederiko11.github.io/gta-6/guide-e-tutorial/scansionare-veicoli/"',html)
        self.assertEqual(html.count('class="v-step"'),5)
        self.assertEqual(html.count('class="v-check"'),5)
        self.assertIn("waink-tracker-warning",html)
        self.assertLess(html.index("waink-tracker-warning"),html.index('id="passaggio-1"'))
        self.assertIn("100 WAiNK Locations",html)
        self.assertIn("200 dei 277",html)
        self.assertIn("Verifica PowerPyx",html)
        self.assertNotIn('data-visual-proof-image=',html)
        self.assertNotIn('data-visual-location-image=',html)
        self.assertIn('data-photo-source-guide="scansionare-veicoli"',html)
        self.assertNotIn("immagine ricreata",html.lower())
        self.assertEqual(html.count('data-step-video-id="R0GdEkPZSvM"'),1)
        self.assertEqual(html.count('data-step-video-id="0RBe_fz67gs"'),1)
        self.assertLess(html.index('class="waink-video-intro"'),html.index('class="v-operation-brief"'))
        self.assertNotIn('class="v-guide-prep"',html)
        self.assertEqual(html.count('data-waink-diagram='),5)
        for n in range(1,6):
            section=html.split('id="passaggio-'+str(n)+'"',1)[1].split('</li>',1)[0]
            self.assertIn('data-waink-diagram="'+str(n)+'"',section)
            self.assertIn('assets/waink-guide/step-'+str(n)+'.svg',section)
            self.assertIn('non screenshot',section)
            self.assertIn('loading="eager"',section)
            self.assertNotIn('loading="lazy"',section.split('data-waink-diagram=',1)[1].split('</figure>',1)[0])
            self.assertTrue((ROOT/'assets/waink-guide'/('step-'+str(n)+'.svg')).is_file())
        self.assertIn("Schermate reali WAiNK",html)
        step=html.split('id="passaggio-4"',1)[1].split('id="passaggio-5"',1)[0]
        self.assertIn('data-step-video-seconds="266"',step)
        self.assertIn("non una prova dei comandi DualSense",step)
        self.assertNotIn("<iframe",html)
        self.assertIn("step-video-opt-in-v1.js?v=",html)

if __name__=="__main__":
    unittest.main()
