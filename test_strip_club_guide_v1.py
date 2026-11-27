import json
import re
import tempfile
import unittest
from pathlib import Path

import strip_club_guide_v1 as guide


class StripClubGuideTests(unittest.TestCase):
    def test_builds_indexable_article_without_static_or_preloaded_media(self):
        written = {}
        captured = {}

        def write(path, content):
            written[path] = content

        def layout(title, description, path, body, section, structured=None):
            captured["schema"] = structured
            return (
                '<html><head><meta name="twitter:card" content="summary_large_image">'
                '<meta property="og:image" content="assets/social-preview.png">'
                '<meta name="twitter:image" content="assets/social-preview.png"></head>'
                '<body>' + body + '</body></html>'
            )

        with tempfile.TemporaryDirectory() as folder:
            original_css, original_js = Path(guide.CSS_PATH), Path(guide.JS_PATH)
            self.assertTrue(original_css.is_file())
            self.assertTrue(original_js.is_file())
            path = guide.build(write, layout, lambda p="": "https://example.test/" + p, lambda rows: "")

        self.assertEqual(path, guide.PATH)
        page = written[guide.PATH + "index.html"]
        self.assertNotIn("<img", page)
        self.assertNotIn("<iframe", page)
        self.assertIn("assets/social-preview.png", page)
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', page)
        self.assertIn("NINE1NINE", page)
        self.assertIn("Jack of Hearts", page)
        self.assertIn("Delights Cabaret", page)
        self.assertIn(guide.MAPS["nine"], page)
        self.assertIn(guide.MAPS["jack"], page)
        self.assertIn(guide.MAPS["delights"], page)
        self.assertIn(guide.VIDEO_ID, page)
        self.assertIn("non una mappa ufficiale Rockstar", page)
        self.assertEqual(captured["schema"]["datePublished"], guide.PUBLISHED)
        self.assertEqual(captured["schema"]["@type"], "Article")
        script = Path(guide.JS_PATH).read_text(encoding="utf-8")
        self.assertIn("youtube-nocookie.com/embed/", script)
        self.assertIn("data-strip-video-load", script)
        self.assertIn("document.addEventListener", script)

    def test_disputed_access_and_prices_are_not_presented_as_facts(self):
        content = guide.body(lambda p="": "/" + p, lambda rows: "")
        self.assertIn("le fonti sono in disaccordo", content)
        self.assertIn("non lo presentiamo come verificato", content)
        self.assertIn("controlla il menu del locale", content.lower())
        self.assertIn(guide.SOURCES["pcgamer"], content)
        self.assertIn(guide.SOURCES["gtami"], content)
        self.assertIn(guide.SOURCES["everyeye"], content)

    def test_player_is_opt_in_and_map_data_is_attributed(self):
        content = guide.body(lambda p="": "/" + p, lambda rows: "")
        self.assertIn("data-strip-video-load", content)
        self.assertIn("Nessuna anteprima o connessione a YouTube prima del clic", content)
        self.assertIn("GTAAccess", content)
        self.assertIn("GTAMI è un progetto indipendente", content)
        self.assertNotRegex(content, r"<img\b|<iframe\b")
        self.assertEqual(len(re.findall(r'href="https://gtami.com/en/map/\?place=', content)), 6)


if __name__ == "__main__":
    unittest.main()
