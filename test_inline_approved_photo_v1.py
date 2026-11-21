"""Contract: genuine PS5 images appear at the exact approved step, with tiny source credit."""
import json
import unittest
from pathlib import Path
from photo_intake_v4 import validate_approved, render_approved_for_step, render_approved_for_guide

def fixtures():
    g=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
    g+=json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides']
    requests=json.loads(Path('data/visual_requests.json').read_text(encoding='utf-8'))['guides']
    return g,requests

class InlineApprovedPhotoTests(unittest.TestCase):
    def test_a_requested_photo_role_is_not_automatically_an_action_step(self):
        guides,requests=fixtures()
        registry=json.loads(Path('data/approved_screenshots_v4.json').read_text(encoding='utf-8'))
        self.assertTrue(validate_approved(registry,guides,requests))
        assert registry['photos']==[]
        # Without explicit editorial step mapping, a record must not pass review.
        fake={'schema':registry['schema'],'photos':[{
            'id':'manual-photo-001','guide_id':guides[0]['id'],'role':1,
            'platform':'PS5','rights':'explicit_nonexclusive_site_and_social',
            'author_confirmed':True,'approved_by':'xFederiko11',
            'human_reviewed':True,'published':True,'approved_on':'2026-11-21'
        }]}
        with self.assertRaisesRegex(ValueError,'numbered tutorial step'):
            validate_approved(fake,guides,requests)
        fake['photos'][0]['step_number']=len(guides[0]['steps'])+1
        with self.assertRaisesRegex(ValueError,'numbered tutorial step'):
            validate_approved(fake,guides,requests)

    def test_inline_photo_has_small_source_directly_below_it(self):
        guides,_=fixtures()
        guide=next(g for g in guides if g['id']=='registrare-auto-personale')
        photo={
            'id':'sample-verified-step','guide_id':guide['id'],
            'role':5,'step_number':2,'platform':'PS5',
            'file':'assets/approved/sample-verified-step.webp',
            'alt':'Schermata originale dell interfaccia del gioco',
            'caption':'Controllo tracker su un veicolo verificato',
            'credit':'Autore del gameplay',
            'source_post':'https://x.com/Autore/status/1234567890987654321'
        }
        example={'photos':[photo]}
        self.assertEqual(render_approved_for_step(guide,example,0),'')
        html=render_approved_for_step(guide,example,1)
        self.assertIn('data-visual-proof-image="community-sample-verified-step"',html)
        self.assertIn('data-visual-kind="screenshot"',html)
        self.assertIn('Fonte foto: Autore del gameplay',html)
        self.assertLess(html.index('<img'),html.index('<figcaption'))
        self.assertLess(html.index('<figcaption'),html.index('Fonte foto:'))
        self.assertIn(photo['source_post'],html)
        self.assertEqual(render_approved_for_guide(guide,example),'',
                         'No duplicate community gallery after the tutorial')

if __name__=='__main__':
    unittest.main()
