"""Offline regression coverage for guide-source provenance validation."""
import json
from pathlib import Path
import unittest
from guide_source_validation import validate_guide_source


class GuideSourceTests(unittest.TestCase):
    def test_approved_sources(self):
        for url in (
            'https://www.powerpyx.com/gta-6-guide/',
            'https://powerpyx.com/gta-6-guide/',
            'https://insider-gaming.com/gta-6-early-game-locations-make-money/',
            'https://www.insider-gaming.com/example/',
        ):
            with self.subTest(url=url):
                self.assertTrue(validate_guide_source(url))

    def test_rejects_unapproved_or_ambiguous_urls(self):
        for value in (
            None, '', 3, 'http://www.powerpyx.com/a/',
            'https://www.powerpyx.com.evil.example/a/',
            'https://insider-gaming.com.evil.example/a/',
            'https://www.powerpyx.com@evil.example/a/',
            'https://user:secret@www.powerpyx.com/a/',
            'https://www.powerpyx.com:444/a/',
            'https://www.powerpyx.com:invalid/a/',
            'https://www.powerpyx.com/',
            'https://www.powerpyx.com/a/#fragment',
            'https://www.powerpyx.com/a/\n',
            ' https://www.powerpyx.com/a/',
            'https://www.powerpyx.com\\@evil.example/a/',
        ):
            with self.subTest(value=value):
                self.assertFalse(validate_guide_source(value))

    def test_current_guide_sources_and_money_guides(self):
        guides = json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
        for guide in guides:
            with self.subTest(guide=guide['id']):
                self.assertTrue(validate_guide_source(guide['source_url']))
        identifiers = {guide['id'] for guide in guides}
        self.assertIn('soldi-facili-capitolo-1', identifiers)
        self.assertIn('soldi-2500-three-sheets-liquor', identifiers)


if __name__ == '__main__':
    unittest.main()
