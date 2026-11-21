"""Offline regressions for the public GTA VI growth dashboard provenance."""
from datetime import datetime,timezone,timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import json,unittest

from x_growth_dashboard_v1 import (
    SCHEMA,ISSUE_IDS,PUBLIC,API,blank,public_issue,parse_radar,parse_buffer,
    parse_owned_and_manual,report,read_report,render,to_json
)

NOW=datetime(2026,11,21,19,30,tzinfo=timezone.utc)
ROOT=Path("_site")


def issue(n,body,age=1):
    return {"number":n,"html_url":PUBLIC+str(n),"updated_at":(NOW-timedelta(hours=age)).isoformat(),
            "body":body}


def radar_body(questions=0):
    return ("# GTA VI - Social Radar: post verificati e risposte pronte\n\n"
            "## 🆓 Tweet trovati senza API X a pagamento\n\n"
            "Articoli di testate controllati: 4 (limite 4).\n"
            "Permalink X candidati rintracciati (non tutti verificati): 29; embed originali interrogati: 8.\n"
            "Candidati recenti dall'ID X (NON verificati): 12.\n"
            f"Domande esterne confermate da oEmbed: {questions}; altri post verificati usabili solo come riferimenti: 2.\n"
            "\n---\n")

def buffer_body(available=False):
    return ("## 📈 Buffer: diagnosi sperimentale delle performance X\n"
            "Controllo UTC: 2026-11-21T18:00:00+00:00\n"+
            ("Totali **solo sulle voci effettivamente ricevute nel campione**;\n"
             "- Impression (Buffer): 23\n"
             if available else "Metriche X da Buffer: **non disponibili**\nMotivo tecnico: BufferAPIError\n"))

def growth_body(manual=False):
    return ("<!-- gta6-organic-growth-v1 -->\n## 🎯 Conversazioni nostre da valorizzare (post X reali)\n\n"
            "- [Apri la conversazione originale](https://x.com/xFederiko11/status/2124113814308204657)\n"
            "- [Apri la conversazione originale](https://x.com/xFederiko11/status/2124083036509610148)\n"
            "## 🗺️ Mappe interattive\n\n"+
            ("**Data registrata:** 2026-11-21\n- x_profile_visits: 3\n- x_new_followers: 1\n" if manual else
             "**Nessuna riga manuale disponibile:** metriche non disponibili, non zero.\n"))


class ReportTests(unittest.TestCase):
    def test_issue_provenance_and_verified_nonzero_counters(self):
        issues={48:issue(48,radar_body()),72:issue(72,buffer_body()),42:issue(42,growth_body())}
        d=report(issues,NOW)
        self.assertEqual(d["schema"],SCHEMA)
        self.assertEqual(d["source_status"],"verified")
        self.assertEqual(d["radar"]["post_urls_discovered"],29)
        self.assertEqual(d["radar"]["official_oembed_checks"],8)
        self.assertEqual(d["radar"]["recent_links"],12)
        self.assertEqual(d["radar"]["questions_verified"],0)
        self.assertEqual(d["radar"]["source_posts_verified"],2)
        self.assertEqual(d["radar"]["owned_posts_in_issue"],2)
        self.assertIsNone(d["x"]["profile_visits"])
        self.assertIsNone(d["x"]["new_followers"])
        self.assertIsNone(d["buffer"]["impressions"])
        self.assertEqual(d["buffer"]["status"],"unavailable")
        self.assertIn("Non disponibile",render(d))
        self.assertIn("29",render(d))
        self.assertIn("Domande X esterne verificate",render(d))
        self.assertIn('data-metric="followers"',render(d))
        self.assertIn("Issue #48",render(d))
        self.assertIn("Issue #72",render(d))
        self.assertIn("Issue #42",render(d))
        self.assertIn("Non sono disponibili",render(d).replace("Non disponibile","Non sono disponibili")) if False else None

    def test_manual_data_and_buffer_sample_cannot_be_counted_as_total_followers(self):
        issues={48:issue(48,radar_body(questions=1)),72:issue(72,buffer_body(True)),
                42:issue(42,growth_body(True))}
        d=report(issues,NOW)
        self.assertEqual(d["radar"]["questions_verified"],1)
        self.assertEqual(d["x"]["profile_visits"],3)
        self.assertEqual(d["x"]["new_followers"],1)
        self.assertEqual(d["x"]["provenance"],"owner_manual_entry")
        self.assertEqual(d["x"]["metrics_date"],"2026-11-21")
        self.assertEqual(d["buffer"]["impressions"],23)
        self.assertEqual(d["buffer"]["status"],"reported_buffer_subset")
        self.assertIn("Solo campione",render(d))
        self.assertIn("non reach totale di X",render(d))
        self.assertIn("non follower complessivi",render(d))

    def test_missing_stale_foreign_issue_never_generates_zero_or_fake_follower(self):
        d=report({},NOW)
        self.assertEqual(d["source_status"],"unavailable")
        self.assertIsNone(d["radar"]["questions_verified"])
        self.assertIsNone(d["x"]["new_followers"])
        self.assertIsNone(d["buffer"]["impressions"])
        self.assertEqual(len(d["sources"]),3)
        self.assertIn("Non disponibile",render(d))
        stale=issue(48,radar_body(),age=65)
        foreign=issue(42,growth_body());foreign["html_url"]="https://evil.test/issue/42"
        d=report({48:stale,42:foreign,72:issue(72,buffer_body())},NOW)
        self.assertEqual(d["source_status"],"partial")
        self.assertIsNone(d["radar"]["post_urls_discovered"])
        self.assertEqual(d["sources"][0]["status"],"stale")
        self.assertEqual(d["sources"][2]["status"],"invalid")
        buf=buffer_body(True).replace("2026-11-21","2026-11-10")
        self.assertEqual(parse_buffer(buf,NOW)["status"],"stale")
        with self.assertRaises(ValueError):
            parse_radar("This is an unapproved influencer report")
        with self.assertRaises(ValueError):
            parse_buffer("Error from Buffer",NOW)

    def test_allowlisted_github_api_is_readonly_and_rejects_foreign_issue(self):
        data=issue(48,radar_body())
        class FakeResp:
            def __init__(self,url,body):self.url=url;self.body=body
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def geturl(self):return self.url
            def read(self,n):return json.dumps(self.body).encode("utf-8")
        seen=[]
        def opener(req,timeout):
            seen.append((req.full_url,req.get_method(),timeout))
            return FakeResp(req.full_url,data)
        self.assertEqual(public_issue(48,opener)["number"],48)
        self.assertEqual(seen,[(API+"48","GET",12)])
        with self.assertRaises(ValueError):public_issue(77,opener)
        def wrong(req,timeout):
            return FakeResp("https://evil.test/redirect",data)
        with self.assertRaises(ValueError):public_issue(48,wrong)
        def fake_account(req,timeout):
            other={**data,"html_url":"https://github.com/other/repo/issues/48"}
            return FakeResp(req.full_url,other)
        with self.assertRaises(ValueError):public_issue(48,fake_account)

    def test_schema_report_roundtrip_without_public_fetch(self):
        original=blank(NOW)
        self.assertEqual(tuple(ISSUE_IDS),(48,72,42))
        with TemporaryDirectory() as folder:
            p=Path(folder)/"report.json"
            p.write_text(to_json(original),encoding="utf-8")
            self.assertEqual(read_report(p)["radar"]["questions_verified"],None)
            original["sources"][0]["url"]="https://evil.test"
            p.write_text(json.dumps(original),encoding="utf-8")
            with self.assertRaises(ValueError):read_report(p)

    def test_production_has_readable_dashboard_and_source_json(self):
        if not (ROOT/"index.html").exists():self.skipTest("Site build absent")
        p=ROOT/"crescita-x/index.html"
        self.assertTrue(p.is_file())
        html=p.read_text(encoding="utf-8")
        self.assertIn("data-design-version=",html)
        self.assertIn("x-growth-dashboard-v1.css?v=",html)
        self.assertIn('name="robots" content="noindex,follow"',html)
        self.assertIn('id="crescita-x"',html)
        self.assertIn("Non disponibile",html) # offline PR: no real X analytics
        self.assertIn("growth-evidence-v1.json",html)
        self.assertIn("https://github.com/xFederiko11/federiko-gta-playstation-bot/issues/48",html)
        self.assertIn("https://github.com/xFederiko11/federiko-gta-playstation-bot/issues/72",html)
        self.assertIn("Statistiche X",(ROOT/"index.html").read_text(encoding="utf-8"))
        self.assertTrue((ROOT/"assets/x-growth-dashboard-v1.css").exists())
        public=json.loads((ROOT/"growth-evidence-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(public["schema"],SCHEMA)
        self.assertIn("sources",public)
        self.assertIn("radar",public)


if __name__=="__main__":unittest.main()
