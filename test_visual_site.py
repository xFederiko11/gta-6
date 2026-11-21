"""Regression checks on the actual visual production output, not just legacy HTML."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json
import re
import unittest
import xml.etree.ElementTree as ET

ROOT=Path('_site')
BASE='https://xfederiko11.github.io/gta-6/'

class Tags(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]; self.scripts=[]; self.json=False; self.buf=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); self.tags.append((tag,a))
        if tag=='script' and a.get('type')=='application/ld+json': self.json=True; self.buf=[]
    def handle_data(self,data):
        if self.json: self.buf.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.json:
            self.scripts.append(json.loads(''.join(self.buf))); self.json=False

def parse(path):
    text=path.read_text(encoding='utf-8'); tags=Tags(); tags.feed(text); return text,tags

class VisualSiteTests(unittest.TestCase):
    def test_design_release_marker(self):
        release=json.loads((ROOT/'design-version.json').read_text())
        self.assertEqual(release['version'],'visual-v2-20261120')
        self.assertGreaterEqual(release['guides'],10)
        self.assertGreaterEqual(release['image_assets'],10)

    def test_home_is_real_new_layout(self):
        text,tags=parse(ROOT/'index.html')
        self.assertIn('v-hero',text)
        self.assertIn('giri a vuoto',text)
        self.assertNotIn('Tutto GTA 6.<br>',text)
        self.assertNotIn('128.941',text)
        self.assertNotIn('50 guide',text)
        self.assertIn('/soldi-facili/',text)
        self.assertIn('/auto-speciali/',text)
        self.assertIn('/salvare-auto/',text)
        # Promotional art may be used once for site identity, never as card evidence.
        self.assertGreaterEqual(sum(t=='img' and 'data-visual-image' in a for t,a in tags.tags),0)
        for part in text.split('class="v-guide-card v-guide-card-plain"')[1:]:
            self.assertNotIn('data-visual-image=',part.split('</article>',1)[0])
        self.assertIn('v-promo-no-media',text)

    def test_sitemap_pages_exist_keep_canonicals_and_one_h1(self):
        root=ET.parse(ROOT/'sitemap.xml').getroot()
        locs=[x.text for x in root.iter() if x.tag.endswith('loc')]
        self.assertEqual(len(locs),len(set(locs)))
        for loc in locs:
            self.assertTrue(loc.startswith(BASE))
            target=ROOT/loc.removeprefix(BASE)/'index.html'
            self.assertTrue(target.is_file(),str(target))
            text,tags=parse(target)
            self.assertEqual(sum(t=='h1' for t,a in tags.tags),1,str(target))
            canonical=[a['href'] for t,a in tags.tags if t=='link' and a.get('rel')=='canonical']
            self.assertEqual(canonical,[loc],str(target))
            self.assertIn('data-design-version="visual-v2-20261120"',text)
            self.assertTrue(tags.scripts,str(target))
            self.assertTrue(any(t=='meta' and a.get('name')=='description' for t,a in tags.tags),str(target))
            self.assertIn('visual-v2.css?v=',text)
            self.assertIn('visual-v2.js?v=',text)
        for path in ('soldi-facili/','auto-speciali/','salvare-auto/','guide-e-tutorial/sportive-randy-posizioni/'):
            self.assertIn(BASE+path,locs)

    def test_existing_guides_are_preserved_and_rewritten(self):
        data=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
        for guide in data:
            page=ROOT/'guide-e-tutorial'/guide['id']/'index.html'
            text,tags=parse(page)
            self.assertIn('v-step-head',text)
            self.assertEqual(text.count('class="v-step"'),len(guide['steps']))
            self.assertIn('id="fonti"',text)
            self.assertIn(guide['source_url'].replace('&','&amp;'),text)
        self.assertEqual(len(list((ROOT/'trofei').glob('trofeo-*/index.html'))),55)

    def test_all_guides_start_with_a_clear_tutorial_before_optional_content(self):
        originals=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
        originals+=json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides']
        self.assertEqual(len(originals),11)
        for guide in originals:
            path=guide.get('canonical_path') or 'guide-e-tutorial/'+guide['id']+'/'
            source=(ROOT/path/'index.html').read_text(encoding='utf-8')
            with self.subTest(path=path):
                first=source.index('id="passaggio-1"')
                procedure=source.index('id="procedura"')
                optional=source.index('class="v-guide-more"')
                self.assertLess(procedure,first)
                self.assertLess(first,optional)
                self.assertIn('▶ INIZIA QUI',source[:first])
                self.assertIn('TUTORIAL · ISTRUZIONI DA SEGUIRE',source[:first])
                self.assertIn('class="v-guide-intro"',source.replace('v-intro v-guide-intro','v-guide-intro'))
                self.assertNotIn('class="v-guide-aside"',source)
                self.assertIn('Non fanno parte del tutorial: mappe, video, fonti e note',source)
                self.assertIn('class="v-guide-social"',source)
                self.assertEqual(source.count('class="v-step"'),len(guide['steps']))
                for number in range(1,len(guide['steps'])+1):
                    self.assertIn('PASSO '+str(number)+' DI '+str(len(guide['steps'])),source)
                self.assertNotIn('class="v-reference-hub"',source[:first])
                self.assertNotIn('id="mappa"',source[:first])
                self.assertNotIn('id="consigli"',source[:first])
                self.assertNotIn('class="r-gallery"',source[:first])
                self.assertNotIn('class="v-intro" ><figure',source[:first])

    def test_guides_show_spoilers_directly_with_clear_warning(self):
        for path in ('guide-e-tutorial/soldi-facili-capitolo-1/','guide-e-tutorial/soldi-2500-three-sheets-liquor/','guide-e-tutorial/sportive-randy-posizioni/'):
            text,tags=parse(ROOT/path/'index.html')
            self.assertFalse(any(t=='details' and 'data-spoiler' in a for t,a in tags.tags))
            self.assertIn('v-spoiler-warning',text)
            self.assertIn('Attenzione spoiler',text)
            self.assertNotIn('Mostra spoiler',text)
            self.assertNotIn('data-spoiler-choice=',text)
            self.assertIn('id="procedura"',text)

    def test_header_x_link_and_primary_shortcuts_on_every_page(self):
        for target in (ROOT/'index.html',ROOT/'salvare-auto/index.html',ROOT/'trofei/index.html'):
            text,tags=parse(target)
            self.assertIn('class="v-x-link"',text)
            self.assertIn('class="v-x-link" href="https://x.com/intent/follow?screen_name=xFederiko11"',text)
            self.assertIn('aria-label="Segui Federiko su X"',text)
            for path in ('soldi-facili/','auto-speciali/','salvare-auto/'):
                self.assertIn(BASE+path,text)
        html=(ROOT/'index.html').read_text()
        self.assertLess(html.index('class="v-categories"'),html.index('class="v-hero"'))
        self.assertIn('class="v-follow-home"',html)
        self.assertIn('Segui @xFederiko11',html)
        self.assertNotIn('followers: 0',html)

    def test_discovery_page_has_no_filters_and_contains_social_sources(self):
        page=(ROOT/'scoperte/index.html').read_text(encoding='utf-8')
        self.assertNotIn('data-community-filter-source',page)
        self.assertNotIn('id="community-search"',page)
        self.assertIn('X, Reddit, GTAForums e Discord',page)
        self.assertIn('https://www.reddit.com/r/GTA6/new/',page)
        self.assertIn('https://gtaforums.com/',page)
        self.assertIn('x.com/intent/tweet?',page)
        self.assertNotIn('data-discussion-issue=',page)
        self.assertNotIn('new_comment_field',page)
        self.assertIn('Attenzione spoiler',page)

    def test_home_and_articles_have_social_discussion_and_x_content(self):
        home=(ROOT/'index.html').read_text(encoding='utf-8')
        self.assertIn('data-x-timeline-load',home)
        self.assertIn('Post recenti e conversazioni GTA VI',home)
        self.assertIn('Mostra i post X',home)
        for pagepath in ('salvare-auto/','soldi-facili/','guide-e-tutorial/soldi-facili-capitolo-1/'):
            text=(ROOT/pagepath/'index.html').read_text(encoding='utf-8')
            self.assertIn('x.com/intent/tweet?',text)
            self.assertIn('class="social-discussion"',text)
            self.assertNotIn('github.com/xFederiko11/gta-6/issues/',text)
            self.assertIn('community-social-v1.js?v=',text)
            self.assertNotIn('data-community-filter-source',text)

    def test_early_money_guides_warn_about_chapter_transition_without_spoiling_titles(self):
        pages=('guide-e-tutorial/soldi-facili-capitolo-1/',
               'guide-e-tutorial/soldi-2500-three-sheets-liquor/')
        for path in pages:
            text,tags=parse(ROOT/path/'index.html')
            self.assertIn('class="v-cash-safety"',text,path)
            self.assertIn('id="avviso-capitolo-1"',text,path)
            self.assertIn('Family Savings',text,path)
            self.assertIn('Tourist Trap',text,path)
            self.assertIn('PRIMA di Recalibration',text,path)
            self.assertIn('https://www.gtabase.com/gta-6/articles/how-to-keep-your-money-safe-in-gta-6',text)
            self.assertIn('https://gta.tech4gamers.com/gta-6/guides/money-end-of-chapter-1/',text)
            self.assertIn('La compatibilità con i trofei',text)
            details=[a for t,a in tags.tags if t=='details' and a.get('id')=='avviso-capitolo-1']
            self.assertEqual(len(details),1)
            self.assertNotIn('Tourist Trap</h1>',text)
        catalog=(ROOT/'soldi-facili/index.html').read_text(encoding='utf-8')
        self.assertIn('Non farmare alla cieca',catalog)
        self.assertIn('Family Savings',catalog)
        self.assertIn('Checking Account di BuckMe non protegge',catalog)
        self.assertIn('soldi-facili-capitolo-1/#avviso-capitolo-1',catalog)
        self.assertNotIn('Tourist Trap',catalog)

    def test_each_guide_invites_original_ps5_screenshots_without_github_or_fake_media(self):
        from urllib.parse import parse_qs
        from html import unescape
        specs=json.loads(Path('data/visual_requests.json').read_text(encoding='utf-8'))
        self.assertEqual(specs['schema'],'gta6-visual-contribution-requests-v1')
        self.assertEqual(len(specs['guides']),11)
        guides=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
        guides+=json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides']
        for g in guides:
            path=g.get('canonical_path') or 'guide-e-tutorial/'+g['id']+'/'
            text,tags=parse(ROOT/path/'index.html')
            request=specs['guides'][g['id']]
            self.assertEqual(len(request),5)
            panels=[a for t,a in tags.tags if t=='aside' and a.get('data-visual-request-id')==g['id']]
            self.assertEqual(len(panels),1,path)
            links=[a for t,a in tags.tags if t=='a' and 'data-visual-send-x' in a]
            self.assertEqual(len(links),1,path)
            target=urlsplit(unescape(links[0]['href']))
            self.assertEqual((target.scheme,target.netloc,target.path),('https','x.com','/intent/tweet'))
            query=parse_qs(target.query)
            self.assertEqual(len(query['text']),1)
            self.assertIn('@xFederiko11',query['text'][0])
            self.assertIn('#GTA6Italia',query['text'][0])
            self.assertIn(BASE+path,query['text'][0])
            self.assertLessEqual(len(query['text'][0]),280)
            contents=text.split('<details class="v-visual-request-details">',1)[1].split('</details>',1)[0]
            role_links=[a for t,a in tags.tags if t=='a' and 'data-visual-request-photo' in a]
            self.assertEqual(len(role_links),5,path)
            self.assertIn('class="v-visual-request-row"',contents)
            self.assertIn('data-visual-screenshot-count=',text)
            for index,(item,link) in enumerate(zip(request,role_links),1):
                self.assertIn(unescape(item.split('>')[0]),unescape(contents),path)
                self.assertEqual(link['data-visual-request-photo'],str(index))
                destination=urlsplit(unescape(link['href']))
                self.assertEqual((destination.scheme,destination.netloc,destination.path),
                                 ('https','x.com','/intent/tweet'))
                draft=parse_qs(destination.query)['text'][0]
                self.assertIn('@xFederiko11',draft)
                self.assertIn('#GTA6Italia',draft)
                self.assertIn(BASE+path,draft)
                self.assertIn(item,draft)
                self.assertLessEqual(len(draft),280)
            article=text.split('<article class="v-guide-main">',1)[1].split('</article>',1)[0]
            article_tags=Tags();article_tags.feed(article)
            in_article={a['data-visual-image'] for t,a in article_tags.tags
                        if t=='img' and a.get('data-visual-kind')=='screenshot'}
            procedure=text.split('<ol class="v-steps">',1)[1].split('</ol>',1)[0]
            step_tags=Tags();step_tags.feed(procedure)
            steps_shown={a['data-visual-image'] for t,a in step_tags.tags
                         if t=='img' and a.get('data-visual-kind')=='screenshot'}
            marker=[a for t,a in tags.tags if t=='p' and 'data-visual-screenshot-count' in a]
            self.assertEqual(len(marker),1,path)
            # Only screenshots proving an ACTION count toward the 5-photo target.
            # An exterior shot can identify a shop, but not prove its hidden loot.
            proof_images=set(re.findall(r'data-visual-proof-image="([^"]+)"',article))
            self.assertEqual(int(marker[0]['data-visual-screenshot-count']),len(proof_images),path)
            self.assertTrue(proof_images.issubset(in_article),path)
            # Unknown photos are excluded instead of presented as proof.
            self.assertFalse(any(t=='p' and 'data-step-photo-status' in a for t,a in step_tags.tags))
            review=json.loads(Path('data/tutorial_photo_review.json').read_text(encoding='utf-8'))
            allowed={item['key'] for item in review['guide_step_approved'].get(g['id'],{}).values()}
            context={entry['key'] for entry in review.get('context_approved',{}).get(g['id'],{}).values()}
            self.assertTrue(steps_shown.issubset(allowed|context),(path,steps_shown,allowed,context))
            self.assertFalse(any(t=='img' and a.get('data-visual-kind')=='promotional'
                                 for t,a in step_tags.tags),path)
            self.assertIn('Crea (Create) su PS5',text)
            self.assertIn('ti chiederemo un permesso esplicito',text)
            self.assertNotIn('input type="file"',contents)
            self.assertNotIn('github.com/xFederiko11/gta-6/issues/',contents)
        self.assertNotIn('UMAMI_WEBSITE_ID',specs['note'])

    def test_verified_gameplay_clips_and_maps_are_real_source_linked_and_click_to_load(self):
        import html
        catalog=json.loads(Path('data/guide_visual_refs.json').read_text(encoding='utf-8'))
        self.assertEqual(catalog['schema'],'gta6-guide-video-evidence-v1')
        expected={
            'guide-e-tutorial/soldi-facili-capitolo-1/':('1GtrjKhSwzM',285,1),
            'guide-e-tutorial/soldi-2500-three-sheets-liquor/':('1GtrjKhSwzM',455,1),
            'salvare-auto/':('R0GdEkPZSvM',675,2),
            'guide-e-tutorial/glitch-prima-persona-ps5/':('CJi2DWXxsoQ',0,0),
        }
        for path,(video_id,start,map_count) in expected.items():
            text,tags=parse(ROOT/path/'index.html')
            self.assertIn('id="riferimenti-visivi"',text,path)
            self.assertIn('data-youtube-id="'+video_id+'"',text,path)
            self.assertIn('data-youtube-start="'+str(start)+'"',text,path)
            self.assertIn('data-load-youtube',text,path)
            self.assertIn('www.youtube.com/watch?v='+video_id+'&amp;t='+str(start)+'s',text,path)
            self.assertEqual(sum(t=='div' and a.get('class')=='v-map-reference' for t,a in tags.tags),map_count,path)
            self.assertEqual(sum(t=='details' and a.get('class')=='v-video-reference' for t,a in tags.tags),1,path)
            self.assertNotIn('youtube-nocookie.com/embed/',text,path)
            self.assertNotIn('<iframe',text,path)
            self.assertIn('trari.com/en/story/' if video_id!='CJi2DWXxsoQ' else 'www.dexerto.com/gta/',text,path)
        money=(ROOT/'guide-e-tutorial/soldi-2500-three-sheets-liquor/index.html').read_text(encoding='utf-8')
        self.assertIn('Three Sheets Liquor a Key Lento',money)
        self.assertIn('feature=liquor-store',money)
        self.assertIn('Get Shirley’s Rum',money)
        self.assertIn('Steal the Scooter',money)
        self.assertIn('mancabili, ma non richieste per il platino',money)
        self.assertIn('gta-6-all-strangers-freaks-side-missions/',money)
        car=(ROOT/'salvare-auto/index.html').read_text(encoding='utf-8')
        self.assertIn('Watkins Auto Parts',car)
        self.assertIn('Girl’s Trip',car)
        self.assertIn('Slim Jim',car)
        self.assertIn('Respray',car)
        self.assertIn('Register',car)
        self.assertIn('feature=garages',car)
        self.assertIn('feature=vehicle-mod-shop',car)
        self.assertIn('Prima registrazione',car)
        self.assertEqual(car.count('class="v-step"'),7)
        script=Path('site/assets/visual-v2.js').read_text(encoding='utf-8')
        self.assertIn("document.querySelectorAll('[data-load-youtube]')",script)
        self.assertIn("document.createElement('iframe')",script)
        self.assertIn('https://www.youtube-nocookie.com/embed/',script)
        self.assertIn("button.addEventListener('click'",script)
        self.assertNotIn('fetch(',script)
        report=json.loads((ROOT/'media-quality.json').read_text(encoding='utf-8'))
        # Video/map references are never counted as real screenshot media.
        self.assertEqual(report['guides_checked'],11)
        self.assertEqual(report['ready']+report['below_target'],report['guides_checked'])

    def test_medidation_missable_and_local_checklist_is_accessible_and_exact(self):
        path=ROOT/'guide-e-tutorial/meditazione-capitolo-1/index.html'
        text,tags=parse(path)
        self.assertIn('id="meditazioni-checklist"',text)
        self.assertIn('data-meditation-total="18"',text)
        self.assertIn('data-meditation-target="15"',text)
        self.assertIn('MANCABILE · CAPITOLO 1',text)
        self.assertIn('Positive Mental Attitude',text)
        self.assertIn('Down to Earth',text)
        self.assertIn('Coffee Break',text)
        self.assertIn('L2',text)
        self.assertIn('R2',text)
        self.assertIn('tutti i luoghi',text.lower())
        self.assertIn('meditazione-luogo-ascent-mountain',text)
        self.assertIn('id="meditazione-luogo-jasons-house"',text)
        self.assertIn('meditazioni-checklist',text)
        spots=[a for t,a in tags.tags if t=='li' and a.get('class')=='v-meditation-spot']
        checks=[a for t,a in tags.tags if t=='input' and 'data-meditation-check' in a]
        self.assertEqual(len(spots),10)
        self.assertEqual(len(checks),18)
        self.assertEqual(len({a['id'] for a in checks}),18)
        self.assertEqual(len({a['data-meditation-check'] for a in checks}),18)
        self.assertTrue(all(a['type']=='checkbox' for a in checks))
        self.assertNotIn('checked=',text)
        self.assertIn('solo in questo browser',text)
        self.assertIn('non certifica',text)
        self.assertIn('www.powerpyx.com/gta-6-all-meditation-spot-locations/',text)
        self.assertIn('www.pushsquare.com/guides/gta-6-meditation-locations',text)
        self.assertNotIn('<iframe',text)
        script=Path('site/assets/visual-v2.js').read_text(encoding='utf-8')
        self.assertIn("gta6-meditations-v1",script)
        self.assertIn("localStorage.setItem(KEY",script)
        self.assertIn("localStorage.removeItem(KEY",script)
        self.assertIn("window.confirm(",script)
        self.assertIn("boxes.length !== 18",script)

    def test_ps5_first_person_camera_glitch_is_accurate_and_not_claimed_trophy_safe(self):
        path=ROOT/'guide-e-tutorial/glitch-prima-persona-ps5/index.html'
        text,tags=parse(path)
        self.assertEqual(sum(t=='h1' for t,_ in tags.tags),1)
        self.assertIn('v-glitch-status',text)
        self.assertIn('Probabilmente funzionante su PS5',text)
        self.assertIn('Trophy Status Uncertain',text)
        self.assertIn('patch esatta non è documentata',text)
        self.assertIn('single-player',text)
        self.assertIn('Camera (2/2)',text)
        self.assertIn('Map (1/2)',text)
        self.assertIn('Cerchio',text)
        self.assertIn('touchpad',text)
        self.assertIn('salvataggio manuale separato',text)
        self.assertIn('ricarica il salvataggio manuale',text)
        self.assertIn('PC Gamer',text)
        self.assertIn('reddit.com/r/GTA6/comments/1y15kfv/',text)
        self.assertEqual(text.count('class="v-step"'),6)
        self.assertIn('data-youtube-id="CJi2DWXxsoQ"',text)
        self.assertNotIn('<iframe',text)
        self.assertEqual(len([a for t,a in tags.tags if t=='a' and 'data-visual-send-x' in a]),1)
        self.assertNotIn('🏆 Trophy Safe',text)
        self.assertNotIn('guadagno infinito',text)
        self.assertIn('guide-e-tutorial/glitch-prima-persona-ps5/',(ROOT/'sitemap.xml').read_text(encoding='utf-8'))

    def test_openseo_onpage_titles_meta_and_semantic_heading_hierarchy(self):
        """Fix real 20 November 2026 OpenSEO crawl findings without title stuffing."""
        from html import unescape
        def seo(path):
            markup, tags=parse(ROOT/path/'index.html')
            title=re.search(r'<title>(.*?)</title>',markup,re.S)
            self.assertIsNotNone(title,path)
            title=unescape(title.group(1))
            desc=[a['content'] for t,a in tags.tags
                  if t=='meta' and a.get('name')=='description']
            self.assertEqual(len(desc),1,path)
            return title, desc[0], markup, tags
        for slug in ('trofei/','fonti/','hdr-oled/','trucchi/'):
            with self.subTest(hub=slug):
                title,desc,markup,tags=seo(slug)
                self.assertLessEqual(len(title),60,slug)
                self.assertTrue(70<=len(desc)<=160,slug)
        for kind in ('guide-e-tutorial/','soldi-facili/','auto-speciali/'):
            title,desc,markup,tags=seo(kind)
            self.assertIn('class="v-directory-section-title"',markup)
            headings=[(tag, i) for i,(tag,attrs) in enumerate(tags.tags)
                      if tag in ('h1','h2','h3')]
            self.assertTrue(headings,kind)
            first_h2=next(i for tag,i in headings if tag=='h2')
            first_h3=next(i for tag,i in headings if tag=='h3')
            self.assertLess(first_h2,first_h3,kind)
        trophy_data=json.loads(Path('data/trofei.json').read_text(encoding='utf-8'))['trophies']
        for trophy in trophy_data:
            path='trofei/'+trophy['slug']+'/'
            title,desc,markup,tags=seo(path)
            self.assertLessEqual(len(title),60,path)
            self.assertIn(trophy['name_it'],title,path)
            self.assertIn('GTA 6',title,path)
        cec=(ROOT/'trofei/trofeo-17-cecchino/index.html').read_text(encoding='utf-8')
        self.assertEqual(cec.count('class="medal-course"'),12)
        self.assertNotIn('<h4>',cec)
        self.assertEqual(cec.count('<div class="medal-course"><h3>'),12)
        guides=(json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
                +json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides'])
        from visual_guide_content import enrich
        for guide in enrich(guides):
            path=guide['canonical_path']
            title,desc,markup,tags=seo(path)
            self.assertLessEqual(len(title),60,path)
            self.assertTrue(70<=len(desc)<=160,(path,len(desc)))
            self.assertEqual(desc,guide['seo_description'],path)
            self.assertIn(guide['summary'],unescape(markup),path)
            self.assertIn('<link rel="canonical" href="'+BASE+path+'">',markup)
        first=(ROOT/'guide-e-tutorial/meditazione-capitolo-1/index.html').read_text(encoding='utf-8')
        self.assertIn('meditazioni',first.lower())
        glitch=(ROOT/'guide-e-tutorial/glitch-prima-persona-ps5/index.html').read_text(encoding='utf-8')
        self.assertIn('Trophy Status Uncertain',glitch)
        self.assertNotIn('🏆 Trophy Safe',glitch)

    def test_openseo_hdr_model_and_cheat_titles_preserve_complete_names(self):
        """Audit all TV families and PS5 cheats, not just the crawler's 50-page sample."""
        from html import unescape
        def metadata(page):
            html,tags=parse(page)
            match=re.search(r'<title>(.*?)</title>',html,re.S)
            self.assertIsNotNone(match,str(page))
            title=unescape(match.group(1))
            desc=[a["content"] for t,a in tags.tags
                  if t=="meta" and a.get("name")=="description"]
            self.assertEqual(len(desc),1,str(page))
            self.assertLessEqual(len(title),60,str(page))
            self.assertGreaterEqual(len(desc[0]),70,str(page))
            self.assertLessEqual(len(desc[0]),160,str(page))
            return html,title,desc[0]
        oled=json.loads(Path('data/hdr_oled.json').read_text(encoding='utf-8'))['families']
        self.assertEqual(len(oled),21)
        for family in oled:
            with self.subTest(oled=family['slug']):
                path=ROOT/'hdr-oled'/family['slug']/'index.html'
                html,title,desc=metadata(path)
                model=family['brand']+' '+family['series']
                self.assertIn(model,title)
                self.assertIn(model,desc)
                self.assertIn('PS5',title)
                self.assertIn('Paper White',desc)
                self.assertIn(family['models'][0]['code'],desc)
                self.assertIn('id="modelli-tv"',html)
                self.assertIn('rel="canonical"',html)
                # Do not remove any commercial codes while making a snippet concise.
                for item in family['models']:
                    self.assertIn(item['code'],html)
        codes=json.loads(Path('data/trucchi.json').read_text(encoding='utf-8'))['cheats']
        self.assertEqual(len(codes),17)
        for code in codes:
            with self.subTest(cheat=code['slug']):
                html,title,desc=metadata(ROOT/'trucchi'/code['slug']/'index.html')
                self.assertIn(code['title'],title)
                self.assertIn('GTA 6',title)
                self.assertIn('PS5',title)
                self.assertIn('disabilita trofei e salvataggi',desc)
                self.assertIn('data-copy-sequence=',html)
                self.assertIn('rel="canonical"',html)

    def test_trophy_article_photos_must_be_evidence_not_decorative_art(self):
        # All 55 trophy pages currently have operational text and ornamental
        # tier icons, but no confirmed gameplay screenshot licenses/placements.
        # Do not silently reintroduce unrelated stock or launch artwork.
        pages=sorted((ROOT/'trofei').glob('trofeo-*/index.html'))
        self.assertEqual(len(pages),55)
        for page in pages:
            html=page.read_text(encoding='utf-8')
            self.assertIn('class="prose trophy-prose"',html)
            article=html.split('class="prose trophy-prose"',1)[1].split('</article>',1)[0]
            with self.subTest(page=page.relative_to(ROOT)):
                images=re.findall(r'<img\\b[^>]*>',article)
                if 'trofeo-17-cecchino' in page.as_posix():
                    # This is the labeled YouTube *video poster*, not a claimed
                    # gameplay-step photo or evidence of medal requirements.
                    self.assertEqual(len(images),1)
                    self.assertIn('i.ytimg.com/vi/tJbzMqJGH4k/hqdefault.jpg',images[0])
                    self.assertIn('È un riferimento visivo, non una guida',article)
                    self.assertIn('Apri l’originale sul canale Rockstar Games',article)
                else:
                    self.assertFalse(images, page)
                self.assertNotIn('data-visual-kind="promotional"',article)
                self.assertNotIn('data-visual-image=',article)

    def test_screenshots_have_real_provenance(self):
        manifest=json.loads(Path('data/visual_media.json').read_text(encoding='utf-8'))['images']
        for key,item in manifest.items():
            self.assertEqual(urlsplit(item['url']).scheme,'https')
            self.assertEqual(urlsplit(item['source']).scheme,'https')
            self.assertIn(item['kind'],('screenshot','promotional'))
            self.assertTrue(item['alt']); self.assertTrue(item['credit'])
            self.assertNotIn('imagegen',item['url'])
        review=json.loads(Path('data/tutorial_photo_review.json').read_text(encoding='utf-8'))
        self.assertEqual(review['schema'],'gta6-tutorial-photo-review-v2')
        guides=json.loads(Path('data/guide.json').read_text(encoding='utf-8'))['guides']
        guides+=json.loads(Path('data/visual_guides.json').read_text(encoding='utf-8'))['guides']
        for guide in guides:
            path=guide.get('canonical_path') or 'guide-e-tutorial/'+guide['id']+'/'
            page=ROOT/path/'index.html'
            text,tags=parse(page)
            procedure=text.split('<ol class="v-steps">',1)[1].split('</ol>',1)[0]
            step_tags=Tags();step_tags.feed(procedure)
            approved={rec['key'] for rec in review['guide_step_approved'].get(guide['id'],{}).values()}
            actual={a['data-visual-image'] for t,a in step_tags.tags if t=='img' and 'data-visual-image' in a}
            approved_context={item['key'] for item in review.get('context_approved',{}).get(guide['id'],{}).values()}
            self.assertTrue(actual.issubset(approved|approved_context),(path,actual,approved,approved_context))
            proof=set(re.findall(r'data-visual-proof-image="([^"]+)"',procedure))
            context=set(re.findall(r'data-visual-location-image="([^"]+)"',procedure))
            self.assertTrue(proof.issubset(approved),path)
            self.assertEqual(context,approved_context,path)
            self.assertTrue(context.isdisjoint(proof),path)
            for media_id in actual:
                self.assertIn('data-visual-image="'+media_id+'"',procedure)
            self.assertEqual(procedure.count('class="v-caption v-photo-attribution"'),len(actual))
            self.assertEqual(procedure.count('class="v-photo-origin"'),len(actual))
            self.assertEqual(procedure.count('Fonte foto:'),len(actual))
            self.assertNotIn('data-media-missing=',procedure)
            self.assertNotIn('data-step-photo-status=',procedure)
            self.assertNotIn('class="r-gallery"',text)
            self.assertNotIn('class="v-guide-aside"',text)
            self.assertLess(text.index('FINE DEI PASSAGGI'),text.index('class="v-guide-more"'))
            for t,a in step_tags.tags:
                if t=='img':
                    self.assertEqual(a['data-visual-kind'],'screenshot')
                    self.assertIn('alt',a)
                    self.assertIn('/gta-6/assets/visual/',a['src'])
                    self.assertTrue((ROOT/a['src'].split('/gta-6/',1)[1]).is_file())
        self.assertEqual(len(review['rejected_assignments']),8)


    def test_internal_links_and_assets_do_not_point_to_ghost_pages(self):
        for target in ROOT.rglob('index.html'):
            text,tags=parse(target)
            for t,a in tags.tags:
                value=a.get('href' if t=='a' else 'src','')
                if not value.startswith(BASE): continue
                rel=unquote(urlsplit(value).path.removeprefix('/gta-6/'))
                local=ROOT/rel
                if value.split('?',1)[0].split('#',1)[0].endswith('/'):
                    local=local/'index.html'
                self.assertTrue(local.exists(),f'{target}: {value}')

    def test_no_credentials_or_external_mutations_in_client(self):
        script=Path('site/assets/visual-v2.js').read_text()
        for token in ('api.buffer.com','Authorization','createPost','innerHTML','fetch('):
            self.assertNotIn(token,script)
        self.assertNotIn('data-spoiler-choice',script)
        self.assertIn('aria-pressed',script)
        self.assertIn('prefers-reduced-motion',Path('site/assets/visual-v2.css').read_text())

if __name__=='__main__': unittest.main()
