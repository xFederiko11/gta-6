"""No-network tests for authentic GitHub community discussions and safe embeds."""
from __future__ import annotations
from datetime import datetime,timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from community_social_v1 import public_comment,path_from_issue,collect,widget,home_rail,REPO
from community_discovery_v2 import render
from community_social_sync_v1 import topics

class CommunitySocialTests(unittest.TestCase):
    def issue(self):
        return {"number":101,"body":"<!-- gta6-discussion-v1 path=salvare-auto/ -->",
                "html_url":"https://github.com/"+REPO+"/issues/101",
                "state":"open","labels":[{"name":"community-discussion"}],
                "title":"Salvare auto","comments":1,"reactions":{"+1":3}}
    def comment(self):
        return {"body":"Ho trovato un'altra posizione, ecco la procedura in gioco.",
                "user":{"login":"Giocatore88","type":"User"},
                "html_url":"https://github.com/"+REPO+"/issues/101#issuecomment-9918",
                "created_at":"2026-11-20T10:00:00Z"}

    def test_only_labelled_exact_first_party_issues(self):
        issue=self.issue()
        self.assertEqual(path_from_issue(issue),"salvare-auto/")
        for change in (
            {"html_url":"https://github.com/another/repo/issues/101"},
            {"body":"<script>injected</script>"},
            {"labels":[]},
            {"state":"closed"},
        ):
            self.assertIsNone(path_from_issue({**issue,**change}))

    def test_read_real_public_comments_without_claiming_x_metrics(self):
        def fake(path,token=""):
            if path.startswith("/issues?"):return [self.issue()]
            if path.startswith("/issues/101/comments"):return [self.comment()]
            raise AssertionError(path)
        result=collect(read=fake)
        self.assertEqual(result["issues"]["salvare-auto/"]["comment_count"],1)
        self.assertEqual(result["issues"]["salvare-auto/"]["likes"],3)
        self.assertFalse(result["x_metrics_available"])
        self.assertEqual(result["latest_comments"][0]["author"],"Giocatore88")
        comment=self.comment();comment["user"]["type"]="Bot"
        self.assertIsNone(public_comment(comment))

    def test_articles_have_real_comment_link_and_escape_untrusted_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"snapshot.json"
            path.write_text(json.dumps({"schema":"community-social-v1","issues":{"salvare-auto/":{
                "number":101,"url":"https://github.com/"+REPO+"/issues/101",
                "title":"Garage","comment_count":0,"likes":0}},
                "latest_comments":[{"author":"abc","body":"<script>alert(1)</script>",
                    "url":"https://github.com/"+REPO+"/issues/101#issuecomment-9918"}],
                "x_posts":[]}))
            with patch("community_social_v1.INDEX",path):
                html=widget("salvare-auto/")
                self.assertIn('data-discussion-issue="101"',html)
                self.assertIn('#new_comment_field',html)
                self.assertIn('serve un account GitHub',html)
                home=home_rail()
                self.assertNotIn('<script>alert(1)</script>',home)
                self.assertIn('&lt;script&gt;',home)
                self.assertIn("data-x-timeline-load",home)

    def test_targets_have_unique_paths(self):
        paths=[p for p,_ in topics()]
        self.assertGreaterEqual(len(paths),13)
        self.assertEqual(len(paths),len(set(paths)))
        self.assertIn("scoperte/",paths)
        self.assertIn("salvare-auto/",paths)

if __name__=="__main__":unittest.main()
