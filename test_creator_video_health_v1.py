"""Offline tests: no internet required and no fake playback claims."""
import json
import unittest
from urllib.error import HTTPError, URLError
from creator_video_health_v1 import probe, ENDPOINT, MAX_BYTES

ITEM = {"key": "registrare-auto-personale", "video_id": "R0GdEkPZSvM"}
GOOD = {"type": "video", "provider_name": "YouTube", "title": "Test title",
        "author_name": "TGG", "html": '<iframe src="https://www.youtube.com/embed/R0GdEkPZSvM"></iframe>'}


def fake(meta, redirected=False):
    class Response:
        status = 200
        def __init__(self, url):
            self.url = url
        def geturl(self):
            return "https://example.org/" if redirected else self.url
        def read(self, cap):
            return json.dumps(meta).encode()[:cap]
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    def open_(request, timeout):
        assert request.full_url.startswith(ENDPOINT + "?")
        assert timeout <= 6
        return Response(request.full_url)
    return open_


class CreatorMetadataTests(unittest.TestCase):
    def test_official_metadata_only(self):
        self.assertEqual(probe(ITEM, fake(GOOD)), "metadata_confirmed")
    def test_wrong_creator_and_wrong_video(self):
        self.assertEqual(probe(ITEM, fake(dict(GOOD, author_name="Different channel"))), "creator_review_needed")
        self.assertEqual(probe(ITEM, fake(dict(GOOD, html=GOOD["html"].replace(ITEM["video_id"], "CJi2DWXxsoQ")))), "metadata_mismatch")
        self.assertEqual(probe(ITEM, fake(dict(GOOD, html=GOOD["html"].replace("www.youtube.com", "example.org")))), "metadata_mismatch")
    def test_no_redirect_malformed_or_oversized_metadata(self):
        self.assertEqual(probe(ITEM, fake(GOOD, True)), "metadata_unconfirmed")
        self.assertEqual(probe(ITEM, fake([])), "metadata_unconfirmed")
        self.assertEqual(probe(ITEM, fake(dict(GOOD, title="x"*MAX_BYTES))), "metadata_unconfirmed")
        self.assertEqual(probe(ITEM, fake(dict(GOOD, html="<p>not an embed</p>"))), "metadata_unconfirmed")
    def test_http_and_network_failure_are_not_playback_or_deletion_proof(self):
        for status in (401,403,404,410,451,429,503):
            def failed(req, timeout):
                raise HTTPError(req.full_url,status,"test",{},None)
            expected = "provider_restricted_or_unavailable" if status in (401,403,404,410,451) else "metadata_unconfirmed"
            self.assertEqual(probe(ITEM, failed), expected)
        def timeout(req, timeout):
            raise URLError("test")
        self.assertEqual(probe(ITEM, timeout), "metadata_unconfirmed")
    def test_unsafe_identifier_rejected_before_network(self):
        with self.assertRaises(ValueError):
            probe(dict(ITEM,video_id="not valid"), fake(GOOD))


if __name__ == "__main__":
    unittest.main()
