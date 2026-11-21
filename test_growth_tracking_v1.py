"""Offline tests: optional analytics do not create fake follower metrics or tracking."""
from __future__ import annotations
import unittest
from growth_tracking_v1 import normalize_id, enhance, classify, script_tag, annotate

ID = "94db1cb1-74f4-4a40-ad6c-962362670409"
PAGE = '''<!doctype html><html lang="it"><head><title>GTA VI Italia</title></head><body>
<a class="v-x-link" href="https://x.com/intent/follow?screen_name=xFederiko11">Segui</a>
<a href="https://x.com/intent/tweet?text=GTA&amp;url=https%3A%2F%2Fxfederiko11.github.io%2Fgta-6%2F">Condividi</a>
<a href="https://x.com/intent/tweet?in_reply_to=2123741902625218841">Rispondi</a>
<a href="https://x.com/xFederiko11/status/2123741902625218841">Post autentico</a>
<a href="https://x.com/xFederiko11">Profilo</a>
<a href="https://www.youtube.com/watch?v=tJbzMqJGH4k">Video su YouTube</a>
<a href="https://x.com.evil.example/intent/follow?screen_name=xFederiko11">Falso</a>
<a href="https://x.com/Other/status/2123741902625218841">Altri</a>
<a href="https://xfederiko11.github.io/gta-6/privacy/">Privacy</a>
</body></html>'''

class GrowthTrackingTests(unittest.TestCase):
    def test_disabled_means_no_script_no_tracking_and_no_mutations(self):
        self.assertIsNone(normalize_id(""))
        self.assertEqual(script_tag(None), "")
        self.assertEqual(enhance(PAGE, ""), PAGE)
        self.assertNotIn("data-umami-event", enhance(PAGE, None))
    def test_only_canonical_nonzero_uuid(self):
        self.assertEqual(normalize_id(ID.upper()), ID)
        for raw in ("x", "<script>", ID+"-evil", "00000000-0000-0000-0000-000000000000",
                    "javascript:alert(1)", "94db1cb1-74f4-4a40-ad6c-962362670409\n"):
            with self.subTest(value=raw):
                with self.assertRaises(ValueError):
                    normalize_id(raw)
    def test_opted_in_tracks_native_own_ctas_not_fake_conversions(self):
        result = enhance(PAGE, ID)
        self.assertIn('data-website-id="'+ID+'"', result)
        self.assertIn('data-do-not-track="true"', result)
        self.assertIn('data-domains="xfederiko11.github.io"', result)
        self.assertIn('data-exclude-search="true"', result)
        self.assertEqual(result.count('data-umami-event="x-follow-intent"'), 1)
        self.assertEqual(result.count('data-umami-event="x-share-intent"'), 1)
        self.assertEqual(result.count('data-umami-event="x-reply-intent"'), 1)
        self.assertEqual(result.count('data-umami-event="x-post-open"'), 1)
        self.assertEqual(result.count('data-umami-event="x-profile-open"'), 1)
        self.assertEqual(result.count('data-umami-event="youtube-video-open"'), 1)
        self.assertEqual(result.count("data-umami-event="), 6)
        self.assertNotIn("new_followers", result)
        self.assertNotIn("gtag(", result)
        self.assertNotIn("GoogleAnalyticsObject", result)
        self.assertEqual(enhance(result, ID), result)
        self.assertEqual(annotate(annotate(PAGE)),annotate(PAGE))
    def test_screenshot_compose_is_measured_as_intent_not_photo_delivery(self):
        from urllib.parse import urlencode
        draft=("@xFederiko11 Screenshot PS5 GTA VI: la schermata del comando"
               "\nhttps://xfederiko11.github.io/gta-6/guide-e-tutorial/"
               " #GTA6Italia")
        target="https://x.com/intent/tweet?"+urlencode({"text":draft})
        anchor='<a data-visual-request-photo="2" href="'+target+'">Proponi foto</a>'
        generic='<a data-visual-send-x href="'+target+'">Richiesta generale</a>'
        self.assertEqual(classify(anchor),'x-screenshot-intent')
        self.assertEqual(classify(generic),'x-screenshot-intent')
        self.assertIn('data-umami-event="x-screenshot-intent"',annotate(anchor))
        self.assertEqual(classify('<a data-visual-request-photo="2" href="https://x.com/intent/tweet?text=spam">Proponi foto</a>'),None)
        self.assertEqual(classify('<a data-visual-request-photo="2" href="https://evil.test/intent/tweet?'+target.split("?",1)[1]+'">Proponi foto</a>'),None)
        tagged=enhance('<html><head></head><body>'+anchor+'</body></html>',ID)
        self.assertNotIn('photo-submitted',tagged)
        self.assertNotIn('license-granted',tagged)
        self.assertEqual(tagged.count('data-umami-event="x-screenshot-intent"'),1)

    def test_unofficial_map_provider_and_follow_intents_are_not_conversions(self):
        src = ('<a data-vim-full href="https://vice-map.com/map">Vice Map</a>'
               '<a data-vim-full href="https://gta6.city/">GTA6.city</a>'
               '<a data-vim-follow href="https://x.com/intent/follow?screen_name=xFederiko11">Segui</a>'
               '<a data-vim-full href="https://vice-map.com.evil.test/map">Falso</a>')
        annotated=annotate(src)
        self.assertEqual(annotated.count('data-umami-event="game-map-external-open"'),2)
        self.assertEqual(annotated.count('data-umami-event="game-map-follow-intent"'),1)
        self.assertNotIn("followers-acquired",annotated)
        self.assertIn('https://vice-map.com.evil.test/map',annotated)
        self.assertNotIn('data-umami-event="game-map-loaded"',annotated)

    def test_never_track_untrusted_hosts(self):
        for link in (
          'https://x.com.evil.test/intent/follow?screen_name=xFederiko11',
          'https://x.com/intent/follow?screen_name=Other',
          'http://x.com/intent/follow?screen_name=xFederiko11',
          'https://x.com@host.example/intent/follow?screen_name=xFederiko11',
          'https://www.youtube.com/watch?v=invalid',
          'https://x.com/Other/status/2123741902625218841',
          'https://x.com/xFederiko11?utm=1',
          'https://x.com/xFederiko11/status/2123741902625218841#hidden',
        ):
            self.assertIsNone(classify('<a href="'+link+'">test</a>'), link)
    def test_real_owner_umami_id_is_public_not_secret_and_event_names_are_honest(self):
        owner_id='ec3592c0-e9f7-4e13-8c29-f9c7d59aa8fd'
        page=PAGE.replace('</body>','<button type="button" data-load-youtube>Riproduci</button></body>')
        result=enhance(page,owner_id)
        self.assertEqual(result.count('data-website-id="'+owner_id+'"'),1)
        self.assertEqual(result.count('id="growth-analytics-v1"'),1)
        self.assertEqual(result.count('data-umami-event="youtube-player-open"'),1)
        self.assertIn('data-umami-event="x-follow-intent"',result)
        self.assertEqual(enhance(result,owner_id),result)
        self.assertEqual(enhance(page,None),page)
        self.assertNotIn('data-umami-event="youtube-player-open"',enhance(page,None))
        self.assertNotIn('followers-acquired',result)
        self.assertNotIn('video-watched',result)

    def test_workflow_tracks_only_production_builds(self):
        from pathlib import Path
        workflow=Path('.github/workflows/deploy-site.yml').read_text(encoding='utf-8')
        self.assertIn("UMAMI_WEBSITE_ID: ${{ github.event_name != 'pull_request' && 'ec3592c0-e9f7-4e13-8c29-f9c7d59aa8fd' || '' }}",workflow)
        self.assertIn('PUBLIC_GTA6_UMAMI_TAG_OK',workflow)
        self.assertNotIn("UMAMI_WEBSITE_ID: ${{ vars.UMAMI_WEBSITE_ID }}",workflow)

    def test_missing_head_fails_closed_only_when_configured(self):
        self.assertEqual(enhance("<body>ok</body>", ""), "<body>ok</body>")
        with self.assertRaises(ValueError):
            enhance("<body>ok</body>", ID)

if __name__ == "__main__":
    unittest.main()
