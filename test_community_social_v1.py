"""No-network regression tests: social comments require only X or YouTube."""
from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote
from community_social_v1 import widget,home_rail,verified_x_url,suggested_tweet,relevant_youtube,xpost_for,share_intent,FOLLOW_INTENT

class SocialParticipationTests(unittest.TestCase):
    def test_verified_publication_time(self):
        from community_social_v1 import post_time_html
        from sunset_blog_v1 import sidebar
        item={"x_url":"https://x.com/xFederiko11/status/2123588882885186002","text":"Test post","source":"Buffer sent Post.externalLink on verified X channel","buffer_status":"sent","completed_utc":"2026-11-26T12:44:40.575000Z"}
        self.assertIn("26/11/2026 · 13:44",post_time_html(item))
        self.assertIn("11/07/2026 · 00:30",post_time_html({**item,"completed_utc":"2026-07-10T22:30:00Z"}))
        for change in ({"source":"ledger"},{"buffer_status":"queued"},{"completed_utc":"2026-11-26T12:44:00"}):
            self.assertEqual(post_time_html({**item,**change}),"")
        with patch("sunset_blog_v1.load",return_value={"x_posts":[item]}):
            self.assertIn("26/11/2026 · 13:44",sidebar())

    def test_url_validation(self):
        good="https://twitter.com/xFederiko11/status/2123588882885186002"
        self.assertEqual(verified_x_url(good),"https://x.com/xFederiko11/status/2123588882885186002")
        for bad in ("https://twitter.com/Other/status/2123588882885186002",
                    "https://x.com.evil.example/xFederiko11/status/2123588882885186002",
                    "http://x.com/xFederiko11/status/2123588882885186002",
                    "https://x.com/xFederiko11/status/2123588882885186002?evil=1",None):
            self.assertIsNone(verified_x_url(bad))

    def test_no_github_login_or_fake_comment_form(self):
        html=widget("salvare-auto/")
        self.assertIn("x.com/intent/tweet?",html)
        self.assertTrue("Scrivi a Federiko su X" in html or
                        "Rispondi al post su X" in html)
        self.assertNotIn("github.com",html.lower())
        self.assertNotIn("GitHub Issues",html)
        self.assertIn("salvare-auto%2F",html)
        self.assertIn("x.com/intent/tweet",suggested_tweet("scoperte/"))
        self.assertIn('x.com/intent/follow?screen_name=xFederiko11',html)
        self.assertIn('Condividi la guida su X',html)
        self.assertIn('url=https%3A%2F%2Fxfederiko11.github.io%2Fgta-6%2Fscoperte%2F',
                      share_intent("scoperte/"))
        with self.assertRaises(ValueError):share_intent("../other")
        with self.assertRaises(ValueError):suggested_tweet("../secret")

    def test_known_x_post_reply_target(self):
        with tempfile.TemporaryDirectory() as temp:
            f=Path(temp)/"state.json"
            f.write_text(json.dumps({"schema":"community-social-v2","x_posts":[{
                "url":"https://xfederiko11.github.io/gta-6/salvare-auto/",
                "text":"Questo è il nostro post originale.",
                "buffer_status":"sent","x_url":"https://x.com/xFederiko11/status/2123588882885186002"}]}))
            with patch("community_social_v1.INDEX",f):
                out=widget("salvare-auto/")
                self.assertIn("in_reply_to=2123588882885186002",out)
                self.assertIn("Rispondi al post su X",out)
                self.assertNotIn("github.com",out)
                self.assertIn("Questo è il nostro post originale",xpost_for("salvare-auto/"))
                self.assertIn("Post recenti e conversazioni",home_rail())

    def test_youtube_only_when_real_video_found(self):
        video='<iframe src="https://www.youtube-nocookie.com/embed/ABCDEFGHIJK?start=13"></iframe>'
        self.assertEqual(relevant_youtube(video),"https://www.youtube.com/watch?v=ABCDEFGHIJK")
        self.assertIn("Commenta il video su YouTube",widget("scoperte/",youtube_url=video))
        self.assertNotIn("Commenta il video su YouTube",widget("trofei/"))
        self.assertIsNone(relevant_youtube('<p>No embedded videos</p>'))

if __name__=="__main__":unittest.main()
