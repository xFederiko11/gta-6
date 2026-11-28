"""Source matching and opt-in behavior for original card video moments."""
import copy
import json
from pathlib import Path
import unittest
from collectible_video_refs_v1 import load,validate,render


class CardVideoTests(unittest.TestCase):
    def test_identity_and_source_chapters_are_required(self):
        data=load()
        routes=json.loads(Path('data/collectible_routes_v4.json').read_text())
        by={x['id']:x for x in routes['points']}
        for ident,seconds in (('pt-12',577),('pt-32',1183)):
            html=render(by[ident])
            self.assertIn('data-step-video-seconds="'+str(seconds)+'"',html)
            self.assertIn('GTA Series Videos',html)
            self.assertIn('&amp;t='+str(seconds)+'s',html)
            self.assertIn('data-step-video-open hidden',html)
            self.assertIn('non abbiamo verificato la riproduzione',html)
            self.assertNotIn('<img',html)
            self.assertNotIn('<iframe',html)
            bad=copy.deepcopy(by[ident]);bad['name']='Carta diversa'
            with self.assertRaises(ValueError):render(bad)
        self.assertEqual(render(by['pt-11']),'')
        broken=copy.deepcopy(data);broken['moments']['pt-12']['at']=578
        with self.assertRaises(ValueError):validate(broken)
        broken=copy.deepcopy(data);broken['source_url']='https://example.org/'
        with self.assertRaises(ValueError):validate(broken)

    def test_built_atlas_has_only_two_reviewed_players_and_source_fallback(self):
        from site_info import sources_for
        self.assertIn('data/collectible_video_refs_v1.json',sources_for('collezionabili/percorsi/'))
        page=Path('_site/collezionabili/percorsi/index.html')
        if not page.exists():self.skipTest('Build not yet available')
        html=page.read_text()
        self.assertEqual(html.count('data-collectible-video="'),2)
        self.assertIn('step-video-opt-in-v1.js?v=',html)
        self.assertIn('step-video-opt-in-v1.css?v=',html)
        self.assertNotIn('youtube-nocookie.com/embed/LTbw8B0DQHA',html)
        self.assertIn('https://www.youtube.com/watch?v=LTbw8B0DQHA&amp;t=577s',html)
        self.assertIn('https://www.youtube.com/watch?v=LTbw8B0DQHA&amp;t=1183s',html)


if __name__=='__main__':unittest.main()
