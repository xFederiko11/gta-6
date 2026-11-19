"""Offline checks for GitHub-source community radar and safe rendering."""
import unittest
from datetime import datetime, timezone
from community_watch import parse_issue, render, SOURCE_URL

NOW=datetime(2026,11,19,9,0,tzinfo=timezone.utc)

def example():
    return """<!-- gta6-community-editorial-queue-v1 -->
# GTA VI — coda editoriale indipendente
Scansione UTC: 2026-11-19T08:22:19+00:00
### 🔵 GUIDA INDIPENDENTE — GTA 6 Mission #8 - Hey Arnold! PS5 Walkthrough
Fonte: **GTA Series Videos** · Data fonte: 2026-11-19T02:00:30+00:00
 · [Apri originale](https://youtube.com/watch?v=12345678901)
Verifica: non confermata
### 🟠 RUMOR — GTA VI rumored property unlock
Fonte: **PowerPyx** · Data fonte: 2026-11-19T07:00:00+00:00
 · [Apri originale](https://powerpyx.com/story/)
### 🔵 GUIDA INDIPENDENTE — GTA VI download malware
Fonte: **Malicious** · Data fonte: 2026-11-19T07:00:00+00:00
 · [Apri originale](https://evil.example/malware)
"""

class CommunityWatchTests(unittest.TestCase):
    def test_dedicated_source_issue_and_statuses(self):
        records=parse_issue(example(),now=NOW)
        self.assertEqual(len(records["items"]),2)
        self.assertEqual(records["source_issue"],SOURCE_URL)
        self.assertEqual(records["items"][0]["label"],"🔵 GUIDA INDIPENDENTE")
        self.assertEqual(records["items"][1]["label"],"🟠 RUMOR")
        self.assertEqual(records["items"][0]["source"],"GTA Series Videos")

    def test_does_not_accept_unauthorized_urls(self):
        text=example().replace("https://youtube.com/watch?v=12345678901",
                               "https://example.com/click?to=youtube.com")
        obj=parse_issue(text,now=NOW)
        self.assertEqual(len(obj["items"]),1)
        self.assertEqual(obj["items"][0]["source"],"PowerPyx")

    def test_rejects_missing_marker_and_old_leads(self):
        with self.assertRaises(ValueError):
            parse_issue("No GitHub marker",now=NOW)
        late=datetime(2026,12,10,tzinfo=timezone.utc)
        self.assertEqual(parse_issue(example(),now=late)["items"],[])

    def test_html_escapes_untrusted_titles(self):
        body=example().replace("GTA 6 Mission #8 - Hey Arnold! PS5 Walkthrough",
                               "GTA 6 &lt;script&gt;alert(1)&lt;/script&gt; guide")
        result=parse_issue(body,now=NOW)
        self.assertIn("<script>",result["items"][0]["title"])
        # Page renderer re-escapes the string before using it in HTML.
        import community_watch
        original=community_watch.load
        community_watch.load=lambda:result
        try:
            out={}
            render(lambda p,s:out.setdefault(p,s),
                   lambda title,desc,path,body,section,structured=None:body,
                   lambda path="":"https://xfederiko11.github.io/gta-6/"+path,
                   lambda p:"")
            page=out["community/index.html"]
            self.assertNotIn("<script>",page)
            self.assertIn("&lt;script&gt;",page)
            self.assertIn("Titolo segnalato",page)
        finally:
            community_watch.load=original

if __name__=="__main__":
    unittest.main()
