import copy
from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from patch_observations_v1 import extract, fetch, load, SOURCE, OFFICIAL_ARTICLE, MAX_BYTES
from patch_archive_v1 import render_observations

NOW=datetime(2026,11,25,22,tzinfo=timezone.utc)
RECORD={"event_type":"official_patch_notes_available","game":"GTA VI","platform":"common",
        "region":"global","metric_kind":"availability","date_precision":"date","source_tier":"primary",
        "verification":"verified","source_url":OFFICIAL_ARTICLE,"version":None,"size_bytes":None,
        "occurred_at":"2026-11-23","first_observed_at":"2026-11-24T10:00:00Z",
        "last_observed_at":"2026-11-25T20:00:00Z","metadata":{"kind":"official_patch_note_metadata_v1",
        "platforms":["PS5","Xbox Series X|S"],"entry_count":7,"content_sha256":"a"*64},
        "notes":"Untrusted extra text never passed to renderer"}
def payload(records):
    return {"schema_version":1,"generated_at":"2026-11-25T21:00:00Z","records":records}

class FakeResponse(BytesIO):
    status=200
    def geturl(self):return SOURCE

class PatchObservationTests(unittest.TestCase):
    def test_valid_empty_ledger_never_invents_observation(self):
        result=extract(payload([{"event_type":"system_software_available","version":"26.07-14.23.00"}]),now=NOW)
        self.assertEqual(result["observations"],[])
        html=render_observations(result,[],lambda p:"https://xfederiko11.github.io/gta-6/"+p)
        self.assertIn("Nessuna osservazione automatica verificata",html)
        self.assertNotIn("data-patch-observation",html)
        self.assertNotIn("26.07",html)

    def test_metadata_only_and_existing_article_separate(self):
        new=copy.deepcopy(RECORD)
        new.update(occurred_at="2026-11-25",first_observed_at="2026-11-25T10:00:00Z")
        new["metadata"]["entry_count"]=3
        result=extract(payload([RECORD,new]),now=NOW)
        self.assertNotIn("Untrusted extra text",json.dumps(result))
        self.assertEqual([x["date"] for x in result["observations"]],["2026-11-25","2026-11-23"])
        html=render_observations(result,[{"date":"2026-11-23","fixes":[{}]*7}],lambda p:"https://xfederiko11.github.io/gta-6/"+p)
        self.assertEqual(html.count("data-patch-observation="),2)
        self.assertIn("Riepilogo italiano non ancora pubblicato",html)
        self.assertIn("patch/2026-11-23/",html)
        self.assertNotIn("patch/2026-11-25/",html)
        self.assertIn("non conferma automaticamente",html)
        self.assertIn(OFFICIAL_ARTICLE,html)

    def test_count_disagreement_and_revision_change_visible(self):
        rec=copy.deepcopy(RECORD)
        rec["metadata"].update(entry_count=8,content_sha256="b"*64)
        result=extract(payload([rec]),now=NOW)
        html=render_observations(result,[{"date":"2026-11-23","fixes":[{}]*7}],lambda p:p)
        self.assertIn("Numero di voci diverso",html)
        self.assertIn("b"*12,html)

    def test_invalid_or_duplicate_evidence_fails_closed(self):
        for key,bad in [("source_url","https://example.org/patch"),("verification","reported"),
                        ("platform","PS4"),("version","01.002.002"),("occurred_at","2026-11-26"),
                        ("last_observed_at","2026-11-26T00:00:00Z")]:
            rec=copy.deepcopy(RECORD);rec[key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):extract(payload([rec]),now=NOW)
        for value in (True,0,301):
            rec=copy.deepcopy(RECORD);rec["metadata"]["entry_count"]=value
            with self.assertRaises(ValueError):extract(payload([rec]),now=NOW)
        with self.assertRaises(ValueError):extract(payload([RECORD,RECORD]),now=NOW)

    def test_exact_read_only_endpoint_and_bounded_payload(self):
        def opener(req,timeout):
            self.assertEqual(req.full_url,SOURCE)
            self.assertEqual(timeout,12)
            self.assertIsNone(req.get_header("Authorization"))
            return FakeResponse(json.dumps(payload([RECORD])).encode())
        self.assertEqual(len(fetch(opener=opener,now=NOW)["observations"]),1)
        with self.assertRaises(ValueError):
            fetch(opener=lambda req,timeout:FakeResponse(b"x"*(MAX_BYTES+1)),now=NOW)
        class WrongURL(FakeResponse):
            def geturl(self):return "https://example.org/redirect"
        with self.assertRaises(ValueError):
            fetch(opener=lambda req,timeout:WrongURL(b"{}"),now=NOW)

    def test_missing_or_invalid_production_snapshot_does_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"patch.json"
            with patch.dict("os.environ",{"PATCH_LEDGER_REQUIRED":"true"}):
                with self.assertRaises(FileNotFoundError):load(file)
                file.write_text("{}")
                with self.assertRaises(ValueError):load(file)
            file.unlink()
            with patch.dict("os.environ",{"PATCH_LEDGER_REQUIRED":"false"}):
                self.assertEqual(load(file)["observations"],[])

if __name__=="__main__":
    unittest.main()
