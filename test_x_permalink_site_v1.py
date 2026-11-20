"""No-network site bridge tests: known X status links only."""
from __future__ import annotations
import json
import unittest
from io import BytesIO
from unittest.mock import patch
from community_social_sync_v1 import verified_permalinks,merge_post_snippets
from community_social_v1 import widget,home_rail
from pathlib import Path
from tempfile import TemporaryDirectory

ARTICLE="https://xfederiko11.github.io/gta-6/guide-e-tutorial/studiare-animali/"
LINK="https://x.com/xFederiko11/status/2123588882885186002"
class FakeResponse:
    def __init__(self,content):self.content=content
    def __enter__(self):return self
    def __exit__(self,*a):return False
    def read(self,n):return self.content[:n]
def response(post):
    return json.dumps({"schema":"verified-buffer-x-permalinks-v1",
                       "posts":[post]}).encode()
def item():
    return {"article_url":ARTICLE,"x_url":LINK,"buffer_id":"buf9876543210abcdef",
            "sent_at":"2026-11-20T09:44:00Z",
            "excerpt":"🦩 GTA VI | ANIMALI: 100% RAPIDO. Usa il binocolo.",
            "verified_by":"Buffer sent Post.externalLink on verified @xFederiko11 channel"}

class SocialBridgeTests(unittest.TestCase):
    def test_verified_exact_permalink_mapped(self):
        found=verified_permalinks(opener=lambda *args,**kw:FakeResponse(response(item())))
        self.assertEqual(found[0]["x_url"],LINK)
        self.assertEqual(found[0]["url"],ARTICLE)
        self.assertEqual(found[0]["buffer_status"],"sent")
        result=merge_post_snippets([],found)
        self.assertEqual(len(result),1)

    def test_reject_fake_metric_or_wrong_host_or_unverified_post(self):
        for change in (
            {"x_url":"https://x.com.fake.test/xFederiko11/status/2123588882885186002"},
            {"article_url":"https://attacker.test/gta-6/guide-e-tutorial/studiare-animali/"},
            {"verified_by":"self proclaimed"},
            {"x_url":None},
        ):
            result=verified_permalinks(opener=lambda *args,**kw:
                FakeResponse(response({**item(),**change})))
            self.assertEqual(result,[])

    def test_no_deletion_of_valid_ledger_excerpts_on_empty_bridge(self):
        older={"url":ARTICLE,"text":"Prima versione registrata da Buffer",
               "buffer_status":"sent","completed_utc":"2026-11-19T09:44:00Z"}
        self.assertEqual(merge_post_snippets([older],[]),[older])

    def test_widget_has_exact_source_and_reader_can_reply(self):
        found=verified_permalinks(opener=lambda *args,**kw:FakeResponse(response(item())))
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/"community.json"
            p.write_text(json.dumps({"schema":"community-social-v2",
                                     "x_posts":found,"x_metrics_available":False}))
            with patch("community_social_v1.INDEX",p):
                page=widget("guide-e-tutorial/studiare-animali/")
                self.assertIn("data-x-article-url",page)
                self.assertIn("in_reply_to=2123588882885186002",page)
                self.assertIn("data-x-primary-action",page)
                self.assertNotIn("new_comment_field",page)
                self.assertNotIn("github.com/xFederiko11/gta-6/issues/",page)
                self.assertIn("Rispondi al post",home_rail())

if __name__=="__main__":unittest.main()
