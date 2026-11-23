"""Operational layout regressions: short guides, 6 Moses jobs, no fabricated photo."""
import json
from pathlib import Path
import unittest

from operational_brief_v1 import validate as validate_briefs
from moses_vehicle_jobs_v1 import validate as validate_moses, TASKS, PATH, SOURCE, GIFT, COMPLETION, MICROSTEPS, IGN_VIDEO_ID, IGN_TIMELINE

ROOT=Path("_site")


class OperationalGuidesV1Tests(unittest.TestCase):
    def test_compact_header_in_all_and_only_the_11_real_guides(self):
        a=json.loads(Path("data/guide.json").read_text(encoding="utf-8"))["guides"]
        b=json.loads(Path("data/visual_guides.json").read_text(encoding="utf-8"))["guides"]
        guides=a+b
        briefs=json.loads(Path("data/guide_operational_briefs_v1.json").read_text(encoding="utf-8"))
        self.assertTrue(validate_briefs(briefs,guides))
        for g in guides:
            path=g.get("canonical_path") or "guide-e-tutorial/"+g["id"]+"/"
            html=(ROOT/path/"index.html").read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertEqual(html.count('class="v-operation-brief"'),1)
                self.assertIn("operational-guide-v1.css?v=",html)
                self.assertEqual(html.count("<dt>"),3)
                self.assertEqual(html.count("<dd>"),3)
                self.assertLess(html.index('class="v-operation-brief"'),html.index('id="procedura"'))
                self.assertLess(html.index('class="v-operation-brief"'),html.index('id="passaggio-1"'))
                self.assertIn(briefs["guides"][g["id"]]["when"],html)
                self.assertIn(briefs["guides"][g["id"]]["goal"].replace("&","&amp;").replace("'","&#x27;"),html)
                self.assertEqual(html.count('class="v-step"'),len(g["steps"]))
                self.assertIn('class="v-guide-more"',html)
        for path in ("index.html","hdr-oled/index.html","trofei/index.html"):
            html=(ROOT/path).read_text(encoding="utf-8")
            self.assertNotIn('class="v-operation-brief"',html)

    def test_new_moses_page_has_6_distinct_deliveries_then_gift(self):
        self.assertTrue(validate_moses())
        page=(ROOT/PATH/"index.html").read_text(encoding="utf-8")
        self.assertIn("rel=\"canonical\"",page)
        self.assertEqual(page.count('class="v-step"'),7)
        self.assertIn('data-mo-default-all',page)
        self.assertIn('data-mo-show-all',page)
        self.assertIn('moses-visual-v1.css?v=',page)
        self.assertEqual(page.count('data-mo-real-gameplay='),6)
        self.assertEqual(page.count('data-mo-gift-ref="source-only"'),1)
        self.assertEqual(page.count('class="mo-video-screen"'),6)
        self.assertEqual(page.count("<iframe "),6)
        self.assertEqual(page.count('player ufficiale incorporato'),6)
        self.assertEqual(page.count("mo-photo-link"),6)
        self.assertIn('https://www.youtube-nocookie.com/embed/'+IGN_VIDEO_ID,page)
        for i,(seconds,label) in enumerate(IGN_TIMELINE,1):
            chapter=page.split('id="passaggio-'+str(i)+'"',1)[1].split('id="passaggio-'+str(i+1)+'"',1)[0]
            self.assertIn('data-mo-chapter-seconds="'+str(seconds)+'"',chapter)
            self.assertIn('start='+str(seconds),chapter)
            self.assertIn('minuto '+label,chapter)
            self.assertIn('Guarda anche le foto sulla guida PowerPyx',chapter)
            self.assertLess(chapter.index('<iframe '),chapter.index('Fonte video: IGN'))
        gift=page.split('id="passaggio-7"',1)[1].split('class="v-tutorial-finish"',1)[0]
        self.assertNotIn('<iframe',gift)
        self.assertIn('Non è disponibile qui un’immagine riutilizzabile',gift)
        self.assertEqual(page.count(SOURCE),7) # six photos + one source list
        self.assertEqual(page.count(GIFT),2)
        self.assertIn("Daily Driver",page)
        self.assertIn("2727",page)
        self.assertIn("ciascuna consegna conta",page)
        self.assertIn("100 attività facoltative",page)
        self.assertEqual(page.count('class="mo-jump-link"'),6)
        self.assertEqual(page.count('class="mo-microsteps"'),7)
        self.assertEqual(page.count('class="mo-instructions"'),7)
        self.assertEqual(page.count('<details class="mo-gift-reveal">'),1)
        self.assertIn('mo-story-warning',page)
        self.assertIn(COMPLETION,page)
        self.assertEqual(len(MICROSTEPS),7)
        self.assertEqual(sum(len(action) for action in MICROSTEPS),27)
        for n in range(1,7):
            self.assertIn('href="#passaggio-'+str(n)+'"',page)
        self.assertLess(page.index('class="mo-jump"'),page.index('id="procedura"'))
        self.assertLess(page.index('class="mo-microsteps"'),page.index('class="mo-video-screen"'))
        self.assertIn("operational-guide-v1.css?v=",page)
        self.assertIn("guide-flow-v1.js?v=",page)
        self.assertLess(page.index("Capitolo 2, dopo Daily Driver"),page.index('id="passaggio-1"'))
        self.assertEqual(page.split('<ol class="v-steps">',1)[1].split('</ol>',1)[0].count('<img'),0,
                         "do not pose stock or unlicensed photos as walkthrough proof inside steps")
        self.assertEqual(len(TASKS),7)
        self.assertIn("6 auto",page)
        self.assertIn("1.850 GTA$",page)
        self.assertIn("6.310 GTA$",page)
        self.assertIn("Moses’ Sultan",page)
        self.assertIn("guide-e-tutorial/veicoli-per-moses/",(ROOT/"sitemap.xml").read_text(encoding="utf-8"))
        garage=(ROOT/"salvare-auto/index.html").read_text(encoding="utf-8")
        self.assertIn(PATH,garage)
        self.assertIn("DOPO LA PRIMA AUTO",garage)

    def test_source_briefs_and_warning_truthfulness(self):
        briefs=json.loads(Path("data/guide_operational_briefs_v1.json").read_text(encoding="utf-8"))
        self.assertIn("trofei non verificati",briefs["guides"]["prima-persona-glitch-ps5"]["goal"])
        self.assertIn("Capitolo 1",briefs["guides"]["meditazione-capitolo-1"]["when"])
        page=(ROOT/PATH/"index.html").read_text(encoding="utf-8")
        self.assertIn("bonus condizioni",page)
        self.assertIn("facoltative",page)
        self.assertNotIn('data-visual-kind="promotional"',page)
        self.assertNotIn("ghp_",page)
        js=Path("site/assets/guide-flow-v1.js").read_text(encoding="utf-8")
        self.assertNotIn("fetch(",js)
        self.assertIn("[data-gf-next]",js)

if __name__=="__main__":
    unittest.main()
