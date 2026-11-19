"""Ensure source updates are relevant, attributed and not misrepresented as verified."""
import unittest

from related_research import for_guide, for_catalog, candidates


def item(title, source="PowerPyx", status="🔵 GUIDA INDIPENDENTE", url="https://www.powerpyx.com/gta-6-guide"):
    return {"title":title, "source":source, "status":status,
            "url":url, "published_utc":"2026-11-19T08:00:00+00:00",
            "verified":False}

def feed(items):
    return {"schema":"gta6-community-feed-v1",
            "generated_utc":"2026-11-19T08:10:00+00:00","items":items}


class RelatedResearchTests(unittest.TestCase):
    def test_exact_guide_match_does_not_rewrite_claims(self):
        report=feed([
            item("GTA VI scan vehicle database WAiNK"),
            item("GTA VI shooting range concentration guide",
                 url="https://www.powerpyx.com/gta-6-shooting-range/"),
            item("GTA 6 money rumor",status="🟠 RUMOR",
                 url="https://www.powerpyx.com/gta6-rumor/"),
        ])
        vehicle=for_guide("scansionare-veicoli",report)
        self.assertIn("WAiNK",vehicle)
        self.assertNotIn("shooting range",vehicle)
        self.assertNotIn("money rumor",vehicle)
        self.assertIn("In verifica:",vehicle)
        self.assertIn("non modificano le istruzioni",vehicle.lower())
        self.assertEqual(for_guide("studiare-animali",report),"")
        self.assertEqual(for_guide("unknown-id",report),"")
        self.assertIn("shooting range",for_guide("poligoni-concentrazione",report))

    def test_unverified_gtabase_leads_display_with_distinct_yellow_label(self):
        report=feed([
            item("GTA 6 cheat codes confirmed?",status="🟠 RUMOR"),
            item("GTA VI cars and vehicles database",source="GTABase",
                 status="🟡 SEGNALAZIONE",url="https://www.gtabase.com/news/gta-6-cars"),
            item("GTA 6 mission walkthrough",source="GTA Series Videos",
                 url="https://www.youtube.com/watch?v=ABCDE12345"),
        ])
        self.assertEqual(len(candidates(report)),2)
        html=for_catalog(report)
        self.assertIn("GTA Series Videos",html)
        self.assertIn("GTABase",html)
        self.assertIn("🟡 SEGNALAZIONE",html)
        self.assertNotIn("GTABase",for_guide("scansionare-veicoli",report))
        self.assertNotIn("confirmed",html)
        self.assertIn("🔵 GUIDA INDIPENDENTE",html)

    def test_independent_gta_wiki_edits_are_unverified_metadata(self):
        wiki=item("Grand Theft Auto VI: new vehicles wiki page changes",
                  source="GTA Wiki (independent)",status="🟡 SEGNALAZIONE",
                  url="https://gta.wiki/wiki/Grand_Theft_Auto_VI")
        data=feed([wiki])
        rows=candidates(data)
        self.assertEqual(len(rows),1)
        html=for_catalog(data)
        self.assertIn("GTA Wiki (independent)",html)
        self.assertIn("🟡 SEGNALAZIONE",html)
        self.assertIn("In verifica:",html)
        self.assertNotIn("Rockstar conferma",html)
        self.assertNotIn("GTA Wiki (independent)",
                         for_guide("scansionare-veicoli",data))
        bad=feed([item("GTA VI vehicle changes",source="GTA Wiki (independent)",
                       status="🟡 SEGNALAZIONE",
                       url="https://gta.wiki.evil.example/wiki/GTA_VI")])
        with self.assertRaises(ValueError):
            candidates(bad)

    def test_escapes_untrusted_headlines_and_urls(self):
        report=feed([item('GTA VI WAiNK scan vehicle database <script>alert(1)</script>')])
        html=for_guide("scansionare-veicoli",report)
        self.assertIn("&lt;script&gt;",html)
        self.assertNotIn("<script>",html)
        bad=feed([item("GTA VI vehicle database",url="https://evil.example/")])
        with self.assertRaises(ValueError):for_guide("scansionare-veicoli",bad)

if __name__=="__main__":
    unittest.main()
