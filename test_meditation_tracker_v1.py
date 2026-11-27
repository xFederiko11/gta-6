"""Offline regression tests for the trophy-safe 10-site / 18-session meditation tracker."""
from __future__ import annotations
import copy
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest

from meditation_tracker_v1 import validated, render, FILE


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag,dict(attrs)))


class MeditationChecklistTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(FILE.read_text(encoding="utf-8"))

    def test_exact_ten_locations_and_eighteen_distinct_sessions(self):
        obj=validated(self.data)
        self.assertEqual(len(obj["spots"]),10)
        modes=[mode for spot in obj["spots"] for mode in spot["modes"]]
        self.assertEqual(len(modes),18)
        self.assertEqual(modes.count("jason"),8)
        self.assertEqual(modes.count("lucia"),8)
        self.assertEqual(modes.count("one"),1)
        self.assertEqual(modes.count("final"),1)
        self.assertEqual(obj["target_100"],15)

    def test_produced_checkboxes_have_stable_ids_and_no_tracked_server_requests(self):
        page=render(self.data)
        t=Tags();t.feed(page)
        checks=[a for tag,a in t.tags if tag=="input" and "data-meditation-check" in a]
        self.assertEqual(len(checks),18)
        self.assertEqual(len(set(x["id"] for x in checks)),18)
        self.assertEqual(len(set(x["data-meditation-check"] for x in checks)),18)
        self.assertEqual(sum(a["data-meditation-check"].endswith(":final") for a in checks),1)
        self.assertIn('id="meditazione-luogo-jasons-house"',page)
        self.assertIn('id="meditazione-luogo-ascent-mountain"',page)
        self.assertIn('data-meditation-target="15"',page)
        self.assertIn('PRIMA OCCASIONE · CAPITOLO 1',page)
        self.assertIn('10 luoghi, 18 meditazioni',page)
        self.assertIn('Learn to Meditate Together',page)
        self.assertIn('Port Gellhorn',page)
        self.assertIn('https://www.gtabase.com/gta-6/map/?feature=meditation',page)
        self.assertIn('non è una sessione aggiuntiva',page)
        self.assertIn('entrambi i personaggi',page)
        self.assertIn('Lezione iniziale o alternativa',page)
        self.assertEqual(page.count('data-meditation-video-link'),10)
        self.assertIn('WZ9EM_i_W38&amp;t=377s',page)
        self.assertIn('Maka91Productions',page)
        self.assertIn('www.powerpyx.com/gta-6-all-meditation-spot-locations/',page)
        self.assertIn('www.pushsquare.com/guides/gta-6-meditation-locations',page)
        self.assertNotIn('trackEvent(',page)
        self.assertNotIn('new followers',page)
        self.assertNotIn('<iframe',page)
        self.assertNotIn('<script',page)
        self.assertNotIn('checked=',page)

    def test_invalid_schema_or_mismatched_location_count_fails_closed(self):
        mutants=[]
        wrong=copy.deepcopy(self.data);wrong["schema"]="unknown";mutants.append(wrong)
        wrong=copy.deepcopy(self.data);wrong["total_meditations"]=17;mutants.append(wrong)
        wrong=copy.deepcopy(self.data);wrong["spots"].pop();mutants.append(wrong)
        wrong=copy.deepcopy(self.data);wrong["spots"][1]["modes"]=["jason"];mutants.append(wrong)
        wrong=copy.deepcopy(self.data);wrong["spots"][1]["id"]=wrong["spots"][0]["id"];mutants.append(wrong)
        wrong=copy.deepcopy(self.data);wrong["spots"][0]["phase"]="later";mutants.append(wrong)
        wrong=copy.deepcopy(self.data);wrong["spots"][9]["phase"]="none";mutants.append(wrong)
        wrong=copy.deepcopy(self.data);wrong["source"]="https://example.com/";mutants.append(wrong)
        wrong=copy.deepcopy(self.data);wrong["map_source"]="https://example.com/";mutants.append(wrong)
        for data in mutants:
            with self.subTest(mutation=data.get("schema")):
                with self.assertRaises(ValueError):
                    validated(data)

    def test_escaped_editorial_data_never_adds_markup(self):
        altered=copy.deepcopy(self.data)
        altered["spots"][1]["name"]='<img src=x onerror="alert(1)">'
        html=render(altered)
        self.assertNotIn('<img src=x onerror=',html)
        self.assertIn('&lt;img src=x',html)


if __name__=="__main__":
    unittest.main()
