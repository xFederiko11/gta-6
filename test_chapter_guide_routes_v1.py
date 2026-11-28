"""Guard against turning disputed unlocks into chapter guarantees."""
from pathlib import Path
import unittest

from chapter_guide_routes_v1 import CHAPTER_ROUTES, UNCERTAIN_ROUTES, render
from garage_guides_v1 import STORY, STORY_ROWS

BASE = "https://xfederiko11.github.io/gta-6/"


class ChapterGuideRoutesTests(unittest.TestCase):
    def test_story_garages_use_their_documented_chapter_and_mission(self):
        chapters = {chapter: rows for chapter, rows in CHAPTER_ROUTES}
        for ident, _, chapter, mission, _, _ in STORY_ROWS:
            matches = [row for row in chapters[int(chapter)] if row[0] == STORY + ident + "/"]
            self.assertEqual(len(matches), 1)
            self.assertIn(mission, matches[0][2])

    def test_uncertain_final_rewards_are_not_assigned_an_unlock_chapter(self):
        known = {path for _, rows in CHAPTER_ROUTES for path, _, _ in rows}
        uncertain = {path for path, _, _ in UNCERTAIN_ROUTES}
        self.assertFalse(known & uncertain)
        self.assertIn("garage-gratuiti/southside-storage/", uncertain)
        self.assertIn("garage-gratuiti/domestic-timbers/", uncertain)
        self.assertIn("guide-e-tutorial/vendere-veicoli/", uncertain)
        self.assertIn("Dale Mamba", render(lambda path: BASE + path))

    def test_published_directory_has_one_closed_native_group_per_chapter(self):
        page = Path("_site/guide-e-tutorial/index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('id="guide-per-capitolo"'), 1)
        for chapter in (1, 2, 3, 4, 5, "uncertain"):
            self.assertIn('data-guide-chapter="' + str(chapter) + '"><summary>', page)
        paths = [path for _, rows in CHAPTER_ROUTES for path, _, _ in rows]
        paths += [path for path, _, _ in UNCERTAIN_ROUTES]
        self.assertEqual(len(paths), len(set(paths)))
        for path in paths:
            self.assertTrue((Path("_site") / path / "index.html").is_file(), path)
            self.assertIn('href="' + BASE + path + '"', page)
        self.assertNotIn('data-guide-chapter="3" open', page)


if __name__ == "__main__":
    unittest.main()
