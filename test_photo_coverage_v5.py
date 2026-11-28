"""Offline end-to-end photo priorities: 60 real role references, explicit rights."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import json
import unittest

from photo_coverage_v5 import audit,render,json_report,SCHEMA,PATH
from visual_guide_content import enrich

ROOT=Path("_site")
BASE="https://xfederiko11.github.io/gta-6/"


def fixture():
    load=lambda name:json.loads(Path(name).read_text(encoding="utf-8"))
    guides=enrich(load("data/guide.json")["guides"]+load("data/visual_guides.json")["guides"])
    requests=load("data/visual_requests.json")["guides"]
    approved=load("data/approved_screenshots_v4.json")
    provenance=load("data/photo_provenance_review_v3.json")
    return guides,requests,approved,provenance


class PhotoWorkboardTests(unittest.TestCase):
    def test_all_real_roles_are_unique_and_not_auto_approved(self):
        report=audit(*fixture())
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["total_requests"],60)
        self.assertEqual(report["approved_new_community_screenshots"],0)
        self.assertEqual(report["existing_attributed_editorial_screenshots"],10)
        self.assertEqual(report["existing_editorial_reuse_permissions_verified"],0)
        self.assertEqual(report["unapproved_roles"],60)
        self.assertFalse(report["automatic_social_posting"])
        self.assertEqual(len({r["id"] for r in report["tasks"]}),60)
        self.assertEqual({r["role"] for r in report["tasks"]},{1,2,3,4,5})
        self.assertEqual(len({r["guide_id"] for r in report["tasks"]}),12)
        self.assertGreaterEqual(sum(r["priority"]=="alta" for r in report["tasks"]),15)
        for row in report["tasks"]:
            parts=urlsplit(row["submission_url"])
            self.assertEqual((parts.scheme,parts.hostname,parts.path),
                             ("https","xfederiko11.github.io","/gta-6/screenshot-ps5/invia/"))
            qs=parse_qs(parts.query)
            self.assertEqual(qs["guida"],[row["guide_id"]])
            self.assertEqual(qs["passo"],[str(row["role"])])
            self.assertFalse(row["screenshot_verified"])
            self.assertFalse(row["rights_verified"])
            self.assertEqual(row["source_type"],"original_ps5_capture")
        html=render(report)
        self.assertEqual(html.count('data-pc-task='),60)
        self.assertEqual(html.count('data-pc-guide='),12)
        self.assertIn("non 60 immagini certamente assenti",html)
        self.assertNotIn('<input type="file"',html)
        self.assertNotIn('<img',html)
        self.assertIn('data-pc-filter',html)

    def test_missing_or_invented_rights_cannot_inflate_coverage(self):
        guides,requests,approved,provenance=fixture()
        bad=deepcopy(requests);bad[guides[0]["id"]]=["Falso"]
        with self.assertRaises(ValueError):audit(guides,bad,approved,provenance)
        copied=deepcopy(approved)
        copied["photos"].append({"id":"fake-screenshot","guide_id":guides[0]["id"],"role":1,
                                  "rights":"none","source_post":"https://x.com/u/status/123456789"})
        with self.assertRaises(ValueError):audit(guides,requests,copied,provenance)
        forged=deepcopy(provenance);forged["assets"]=[]
        with self.assertRaises(ValueError):audit(guides,requests,approved,forged)

    def test_public_board_and_json_have_matching_counts(self):
        page=ROOT/PATH/"index.html"
        report=ROOT/"photo-backlog-v5.json"
        if not page.exists():
            self.skipTest("Production site not generated yet")
        source=page.read_text(encoding="utf-8")
        self.assertEqual(source.count('data-pc-task='),60)
        self.assertIn('rel="canonical" href="'+BASE+PATH+'"',source)
        self.assertIn("photo-coverage-v5.css?v=",source)
        self.assertIn("photo-coverage-v5.js?v=",source)
        obj=json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(obj["total_requests"],60)
        self.assertIn(BASE+PATH,(ROOT/"sitemap.xml").read_text(encoding="utf-8"))
        self.assertEqual(json.loads(json_report(obj))["unapproved_roles"],60)
        intake=(ROOT/"screenshot-ps5/invia/index.html").read_text(encoding="utf-8")
        self.assertEqual(intake.count('data-photo-guide='),60)
        js=Path("site/assets/photo-intake-v4.js").read_text(encoding="utf-8")
        self.assertIn('params.get("guida")',js)
        self.assertIn('params.get("passo")',js)
        self.assertNotIn("rights.checked=true",js)
        self.assertNotIn("owner.checked=true",js)


if __name__=="__main__": unittest.main()
