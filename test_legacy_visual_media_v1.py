"""The legacy manifest never constitutes a photo reuse authorization."""
import json
from pathlib import Path
import tempfile
import unittest

from prepare_visual_media import prepare


class LegacyVisualMediaTests(unittest.TestCase):
    def test_link_only_purges_known_derivatives_and_stale_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dest = root / 'visual'
            dest.mkdir()
            manifest = root / 'cache' / 'manifest.json'
            manifest.parent.mkdir()
            manifest.write_text('{"promo":{"960":"old.webp"}}')
            entries = {'promo': {'kind': 'promotional', 'url': 'https://example.invalid/p.jpg'},
                       'screen': {'kind': 'screenshot', 'url': 'https://example.invalid/s.jpg'}}
            for key in entries:
                for width in (480, 960):
                    (dest / f'{key}-{width}.webp').write_bytes(b'old')
            untouched = dest / 'independent-960.webp'
            untouched.write_bytes(b'independent')
            prepare(entries, dest, manifest)
            self.assertEqual(json.loads(manifest.read_text()), {})
            self.assertEqual(list(dest.iterdir()), [untouched])
            self.assertEqual(untouched.read_bytes(), b'independent')
            prepare(entries, dest, manifest)
            self.assertEqual(json.loads(manifest.read_text()), {})

    def test_invalid_manifest_does_not_modify_existing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / 'safe-480.webp'
            file.write_bytes(b'old')
            for invalid in ({'../escape': {'kind': 'promotional'}},
                            {'bad': {'kind': 'unknown'}}):
                entries = {'safe': {'kind': 'screenshot'}, **invalid}
                with self.assertRaises(ValueError):
                    prepare(entries, root, root / 'manifest.json')
                self.assertEqual(file.read_bytes(), b'old')
                self.assertFalse((root / 'manifest.json').exists())

    def test_renderer_cannot_resolve_legacy_media(self):
        import build_visual_site as reader
        for key in reader.MEDIA:
            self.assertIsNone(reader.media_src(key))
            self.assertIsNone(reader.media_src(key, 480))


if __name__ == '__main__':
    unittest.main()
