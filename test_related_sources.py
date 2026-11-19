"""No-network tests for source-linked GTA VI guide updates without changing guide claims."""
import unittest

from community_page import validate
from related_sources import matching, box, PATTERNS

STAMP="2026-11-19T09:15:00+00:00"

def item(title,source="GTABase",url="https://www.gtabase.com/gta-6/news/vehicles"):
    return {"title":title,"source":source,"url":url,
            "tier":"database","status":"🟡 SEGNALAZIONE",
            "published_utc":STAMP,"verified":False}


class RelatedSourcesTests(unittest.TestCase):
    def test_gtabase_is_allowed_only_as_unverified_research(self):
        data={"schema":"gta6-community-feed-v1","generated_utc":STAMP,
              "items":[item("GTA 6: How to scan vehicles in WAiNK")]}
        result=validate(data)
        self.assertEqual(len(result),1)
        self.assertFalse(result[0]["verified"])
        data["items"][0]["verified"]=True
        with self.assertRaises(ValueError):
            validate(data)

    def test_only_relevant_guide_links_are_inserted(self):
        all_items=[
            item("GTA 6: Scan vehicle database in WAiNK"),
            item("GTA VI: How to use Paradise Taxi for fast travel",
                 source="PowerPyx",url="https://www.powerpyx.com/gta-6-taxi/"),
            item("GTA VI chapter 9 walkthrough",
                 source="GTA Series Videos",url="https://youtube.com/watch?v=ABCDEFGHIJK"),
        ]
        scan=matching("scansionare-veicoli",all_items)
        self.assertEqual(len(scan),1)
        self.assertIn("WAiNK",scan[0]["title"])
        html=box("scansionare-veicoli",all_items)
        self.assertIn("NUOVA FONTE",html)
        self.assertIn("Non abbiamo ancora verificato",html)
        self.assertIn("www.gtabase.com",html)
        self.assertNotIn("Paradise Taxi",html)
        self.assertEqual(html.count("<li>"),0)
        self.assertNotIn("trophy safe",html.lower())
        self.assertIn("Paradise Taxi",box("viaggio-rapido-taxi",all_items))
        self.assertEqual(box("meditazione-capitolo-1",all_items),"")
        self.assertEqual(set(PATTERNS),{
            "scansionare-veicoli","studiare-animali","70-sfide-100-percento",
            "meditazione-capitolo-1","viaggio-rapido-taxi","poligoni-concentrazione"})

    def test_external_headlines_are_html_escaped(self):
        feed=[item("GTA 6 WAiNK scan <script>alert('bad')</script>")]
        html=box("scansionare-veicoli",feed)
        self.assertNotIn("<script>",html)
        self.assertIn("&lt;script&gt;",html)
        self.assertIn('rel="noopener noreferrer"',html)

if __name__=="__main__":
    unittest.main()
