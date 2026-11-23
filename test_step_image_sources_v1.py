"""Step-photo references must stay source-linked and match actual tutorial actions."""
from __future__ import annotations
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest

from step_image_sources_v1 import load, render, validate

ROOT=Path('_site')

def guides():
    records=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
    records+=json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides']
    return records


class StepPhotoSourceTests(unittest.TestCase):
    def test_reviewed_refs_have_only_exact_source_articles(self):
        data=load()
        self.assertEqual(validate(data,guides()),17)
        self.assertEqual(set(data['guides']),{
            'registrare-auto-personale','scansionare-veicoli',
            'soldi-2500-three-sheets-liquor','soldi-facili-capitolo-1',
            'meditazione-capitolo-1','sportive-randy-posizioni'
        })
        for g in guides():
            for index in range(len(g['steps'])):
                fragment=render(data,g['id'],index)
                expected=data['guides'].get(g['id'],{}).get(str(index))
                self.assertEqual(bool(fragment),bool(expected),(g['id'],index))
                if expected:
                    self.assertIn('IMMAGINE SULLA FONTE · LINK ESTERNO',fragment)
                    self.assertIn('Guarda la schermata sul sito originale',fragment)
                    self.assertIn('il permesso di riutilizzo non è documentato',fragment)
                    self.assertNotIn('FOTO DEL PASSAGGIO · SITO ORIGINALE',fragment)
                    self.assertIn('target="_blank" rel="noopener noreferrer"',fragment)
                    self.assertIn(expected['source'],fragment)
                    self.assertNotIn('<img',fragment)
                    self.assertNotIn('<iframe',fragment)
                    self.assertNotIn('data-visual-image',fragment)

    def test_rejects_forged_photo_sources_and_wrong_indices(self):
        base=load()
        for bad in (
            'https://gta6data.com.evil.example/page/',
            'http://gta6data.com/foo/',
            'https://gta6data.com@evil.example/foo/',
            'https://gta6data.com/foo/?image=x',
            'https://gta6data.com/foo/#unverified',
            'https://images.pushsquare.com/foo.jpg',
        ):
            copy=deepcopy(base)
            copy['guides']['registrare-auto-personale']['0']['source']=bad
            with self.subTest(url=bad),self.assertRaises(ValueError):
                validate(copy,guides())
        invalid=deepcopy(base)
        invalid['guides']['registrare-auto-personale']['99']=invalid['guides']['registrare-auto-personale']['0']
        with self.assertRaises(ValueError):validate(invalid,guides())
        invalid=deepcopy(base)
        invalid['guides']['invented-guide']={'0':invalid['guides']['registrare-auto-personale']['0']}
        with self.assertRaises(ValueError):validate(invalid,guides())

    def test_public_steps_link_only_to_reviewed_photo_references(self):
        data=load()
        if not (ROOT/'salvare-auto/index.html').exists():
            self.skipTest('Site not generated yet')
        published=0
        for guide in guides():
            path=guide.get('canonical_path') or 'guide-e-tutorial/'+guide['id']+'/'
            text=(ROOT/path/'index.html').read_text(encoding='utf-8')
            procedure=text.split('<ol class="v-steps">',1)[1].split('</ol>',1)[0]
            expected=data['guides'].get(guide['id'],{})
            self.assertEqual(procedure.count('class="v-external-step-photo"'),len(expected),path)
            for index,ref in expected.items():
                self.assertIn('data-photo-source-guide="'+guide['id']+'"',procedure)
                self.assertIn('data-photo-source-step="'+str(int(index)+1)+'"',procedure)
                self.assertIn(ref['source'],procedure)
            published+=len(expected)
        self.assertEqual(published,17)


if __name__=='__main__':
    unittest.main()
