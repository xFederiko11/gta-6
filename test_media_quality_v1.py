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

    def test_promotional_images_never_satisfy_five_gameplay_screenshots(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            page=root/'guide-e-tutorial'/'example'/'index.html'
            page.parent.mkdir(parents=True)
            media=root/'assets'/'visual'
            media.mkdir(parents=True)
            imgs=[]
            for n in range(6):
                filename=f'proof-{n}-960.webp'
                (media/filename).write_bytes(b'local-screenshot-fixture')
                kind='screenshot' if n<4 else 'promotional'
                marker=('data-visual-proof-image="proof-'+str(n)+'" ' if n<4 else '')
                imgs.append('<img '+marker+'data-visual-image="proof-'+str(n)+
                            '" data-visual-kind="'+kind+
                            '" alt="Riferimento" src="https://xfederiko11.github.io/gta-6/assets/visual/'+filename+'">')
            page.write_text('<article class="v-guide-main">'+''.join(imgs)+'</article><aside></aside>',
                            encoding='utf-8')
            report=audit(root)
            self.assertEqual(report['ready'],0)
            self.assertEqual(report['below_target'],1)
            row=report['pages'][0]
            self.assertEqual(row['unique_real_images'],6)
            self.assertEqual(row['real_step_screenshots'],4)
            self.assertEqual(row['promotional_images'],2)
            self.assertEqual(report['target_unique_gameplay_screenshots'],5)
            self.assertEqual(report['gameplay_screenshots_in_guide'],4)
            self.assertEqual(report['promotional_images_in_guide'],2)
            updated=page.read_text(encoding='utf-8').replace(
                'data-visual-kind="promotional"','data-visual-kind="screenshot"',1)
            updated=updated.replace('data-visual-image="proof-4"',
                                    'data-visual-proof-image="proof-4" data-visual-image="proof-4"')
            page.write_text(updated,encoding='utf-8')
            improved=audit(root)
            self.assertEqual(improved['ready'],1)
            self.assertEqual(improved['pages'][0]['real_step_screenshots'],5)

    def test_unclassified_photo_fails_source_provenance_audit(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            media=root/'assets'/'visual'
            media.mkdir(parents=True)
            (media/'photo-960.webp').write_bytes(b'test')
            page=root/'guide-e-tutorial'/'example'/'index.html'
            page.parent.mkdir(parents=True)
            page.write_text('<article class="v-guide-main">'
                            '<img data-visual-image="photo" alt="test" '
                            'src="https://xfederiko11.github.io/gta-6/assets/visual/photo-960.webp">'
                            '</article><aside></aside>',encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError,'visual provenance'):
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
