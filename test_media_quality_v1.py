"""Media quality checks: complete paths, no hotlinks and honest five-image goals."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from media_quality_v1 import audit, TARGET

class MediaQualityTests(unittest.TestCase):
    def test_production_local_only_and_five_image_target_report(self):
        r=audit()
        self.assertEqual(r['target_unique_images'],5)
        self.assertGreaterEqual(r['guides_checked'],10)
        self.assertEqual(r['broken_local_references'],[])
        self.assertTrue(all(p['unique_real_images']>=0 for p in r['pages']))
        self.assertEqual(r['ready']+r['below_target'],r['guides_checked'])

    def test_remote_hotlink_fails_before_publication(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            page=root/'guide-e-tutorial'/'example'/'index.html'
            page.parent.mkdir(parents=True)
            page.write_text('<article class="v-guide-main"><img data-visual-image="broken" alt="demo" src="https://other.example/image.jpg"></article><aside></aside>',encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError,'Broken or remote'):
                audit(root)

    def test_missing_placeholder_is_allowed_but_does_not_count_as_photo(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            page=root/'guide-e-tutorial'/'example'/'index.html'
            page.parent.mkdir(parents=True)
            page.write_text('<article class="v-guide-main"><div data-media-missing="lost" role="img" aria-label="Non disponibile"></div></article><aside></aside>',encoding='utf-8')
            report=audit(root)
            self.assertEqual(report['ready'],0)
            self.assertEqual(report['below_target'],1)
            self.assertEqual(report['pages'][0]['missing_sources'],['lost'])

if __name__=='__main__':unittest.main()
