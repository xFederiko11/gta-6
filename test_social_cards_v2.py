"""Offline contracts and generated-site verification for unique GTA VI social cards."""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import re
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image
import social_cards_v2 as c


class SocialCardTests(unittest.TestCase):
    def test_keys_are_unique_stable_and_safe(self):
        paths=["","trofei/","trofei/trofeo-14-qualcosa/","collezionabili/percorsi/",
               "screenshot-ps5/invia/","guide-e-tutorial/viaggio-rapido-taxi/"]
        ids=[c.cover_key(p) for p in paths]
        self.assertEqual(len(set(ids)),len(ids))
        self.assertEqual(ids,[c.cover_key(p) for p in paths])
        for bad in ("/absolute/","../evil/","guide//a/","guide/../a/","guide/query?bad","\\network"):
            with self.assertRaises(ValueError):
                c.cover_key(bad)

    def test_cards_are_1200_630_distinct_and_not_fake_screenshots(self):
        items=["trofei/trofeo-01/","trofei/trofeo-02/",
               "guide-e-tutorial/scansionare-veicoli/","hdr-oled/"]
        binaries=[]
        for item in items:
            image=c.render_card("Guida GTA VI "+item,item)
            self.assertEqual(image.size,(1200,630))
            data=BytesIO();image.save(data,format="JPEG",quality=83)
            binaries.append(hashlib.sha256(data.getvalue()).hexdigest())
        self.assertEqual(len(binaries),len(set(binaries)))

    def test_no_random_rockstar_photo_on_specific_article_social_cards(self):
        images=[{'image':Image.new('RGB',(1400,800)), 'name':'official art'}]
        self.assertIs(c.artwork_for_page('',images),images[0])
        for page in ('salvare-auto/','guide-e-tutorial/',
                     'guide-e-tutorial/soldi-facili-capitolo-1/',
                     'guide-e-tutorial/meditazione-capitolo-1/',
                     'guide-e-tutorial/glitch-prima-persona-ps5/',
                     'trofei/trofeo-17-cecchino/','hdr-oled/',
                     'mappe-guide/','scoperte/'):
            self.assertIsNone(c.artwork_for_page(page,images),page)
        self.assertIsNone(c.artwork_for_page('',[]))

    def test_only_approved_actual_gameplay_photo_becomes_social_preview(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            path=root/"assets/approved/demo-photo.webp"
            path.parent.mkdir(parents=True)
            # Synthetic fixture exists only in a temporary test directory.
            from random import Random
            rng=Random(71)
            image=Image.frombytes("RGB",(640,360),rng.randbytes(640*360*3))
            image.save(path,"WEBP",quality=80)
            row={"id":"demo-photo","file":"assets/approved/demo-photo.webp",
                 "rights":"explicit_nonexclusive_site_and_social","published":True,
                 "author_confirmed":True,"human_reviewed":True,"approved_by":"xFederiko11",
                 "gameplay_only":True,"no_real_people":True,"social_preview":True,
                 "credit":"Test fixture","alt":"Test fixture only",
                 "source_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
            registry={"schema":"gta6-approved-screenshots-v4","photos":[row]}
            html='<img src="'+c.BASE+row["file"]+'" data-approved-community-photo="demo-photo">'
            self.assertIsNone(c.approved_preview("<p>No screenshot</p>",registry,root))
            row["social_preview"]=False
            self.assertIsNone(c.approved_preview(html,registry,root))
            row["social_preview"]=True
            for flag in ("gameplay_only","no_real_people","human_reviewed","author_confirmed","published"):
                row[flag]=False
                with self.assertRaises(ValueError):
                    c.approved_preview(html,registry,root)
                row[flag]=True
            self.assertRaises(ValueError,c.approved_preview,html.replace(c.BASE,"https://example.org/"),registry,root)
            selected,photo=c.approved_preview(html,registry,root)
            card=c.render_screenshot_card("Test screenshot","salvare-auto/",selected,photo)
            self.assertEqual(card.size,(1200,630))
            # Full image retained at its original aspect ratio.
            self.assertEqual(photo.size,(640,360))
            path.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                c.approved_preview(html,registry,root)

    def test_zip_parses_only_landscape_images_and_deduplicates(self):
        with TemporaryDirectory() as temp:
            image=Image.new("RGB",(1400,800),(42,65,81))
            data=BytesIO();image.save(data,"JPEG");valid=data.getvalue()
            payload=BytesIO()
            with zipfile.ZipFile(payload,"w") as z:
                z.writestr("GTAVI_Landscape_1.jpg",valid)
                z.writestr("different_name_same_visual.jpg",valid)
                z.writestr("../unsafe/image.jpg",valid)
                z.writestr("readme.txt","Rockstar Games")
            class Fake:
                headers={"Content-Length":str(len(payload.getvalue()))}
                def __enter__(self): return self
                def __exit__(self,*args):pass
                def geturl(self):return c.ARCHIVE
                def read(self,n=-1):
                    return self.stream.read(n)
                def __init__(self):self.stream=BytesIO(payload.getvalue())
            rows,status=c.fetch_artworks(True,opener=lambda req,timeout:Fake())
            self.assertEqual(status,"ok")
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["name"],"GTAVI_Landscape_1.jpg")
            self.assertEqual(rows[0]["image"].mode,"RGB")

    def test_direct_official_artworks_are_bounded_and_not_rehosted_untrusted(self):
        self.assertEqual(len(c.DIRECT_ARTWORKS),10)
        self.assertEqual(len(set(url for name,url in c.DIRECT_ARTWORKS)),10)
        im=Image.new("RGB",(1600,900),(83,43,109))
        img=BytesIO();im.save(img,"JPEG",quality=90)
        raw=img.getvalue()
        class Fake:
            headers={"Content-Length":str(len(raw)),"Content-Type":"image/jpeg"}
            def __init__(self,url):self.target=url;self.stream=BytesIO(raw)
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def geturl(self):return self.target
            def read(self,n=-1):return self.stream.read(n)
        def opener(request,timeout):
            self.assertLessEqual(timeout,10)
            return Fake(request.full_url)
        rows,status=c.fetch_direct_official_artworks(True,opener=opener)
        self.assertEqual(len(rows),1)  # perceptually duplicate images are dropped
        self.assertTrue(status.startswith("direct_ok_"))
        self.assertIn("Official artwork:",rows[0]["name"])
        disabled,reason=c.fetch_direct_official_artworks(False,opener=opener)
        self.assertEqual((disabled,reason),([],"direct_disabled"))

    def test_zip_is_optional_and_fallback_is_predictable(self):
        rows,status=c.fetch_artworks(False)
        self.assertEqual(rows,[])
        self.assertEqual(status,"disabled_on_preview")
        page1=c.render_card("GTA VI - MAPPE","collezionabili/percorsi/")
        page2=c.render_card("GTA VI - MAPPE","collezionabili/percorsi/")
        self.assertEqual(page1.tobytes(),page2.tobytes())

    def test_cover_scope_and_topic_are_explicit(self):
        self.assertTrue(c.is_article('<script type="application/ld+json">{"@type":"Article"}</script>',"news/demo/"))
        self.assertFalse(c.is_article('{"@type":"CollectionPage"}',"guide-e-tutorial/"))
        self.assertFalse(c.is_article('{"@type":"WebSite"}',""))
        self.assertEqual(c.subject_for_path("guide-e-tutorial/scansionare-veicoli/"),"scanner")
        self.assertEqual(c.subject_for_path("guide-e-tutorial/strip-club-gta-6/"),"map")
        self.assertEqual(c.subject_for_path("guide-e-tutorial/soldi-facili-capitolo-1/"),"cash")
        self.assertEqual(c.subject_for_path("hdr-oled/lg-oled-c4/"),"display")

    def test_published_pages_have_distinct_public_og_and_real_jpegs(self):
        audit=c.ROOT/"social-cards-audit.json"
        if not audit.exists():
            self.skipTest("Generate the production _site before running public-card audit")
        obj=json.loads(audit.read_text(encoding="utf-8"))
        self.assertEqual(obj["schema"],"gta6-social-cards-v2")
        self.assertGreaterEqual(obj["pages"],65)
        self.assertEqual(obj["unique_images"],obj["pages"])
        # Only explicit editorial selections may illustrate a specific article.
        from editorial_articles import load
        _, articles, images = load()
        selected={article['path']:images[article['hero']]['title'] for article in articles}
        selected.update({route:images[name]['title'] for route,(name,_) in c.GUIDE_PHOTOS.items()})
        for row in obj['entries']:
            if row['path'] in selected:
                if not row['approved_screenshot']:
                    self.assertEqual(row['artwork'],selected[row['path']])
            elif row['path']:
                self.assertIsNone(row['artwork'])
        self.assertLessEqual(obj['artwork_backed_cards'],1+len(selected))
        self.assertEqual(obj['approved_screenshot_backed_cards'],
                         sum(bool(row['approved_screenshot']) for row in obj['entries']))
        urls=set()
        for record in obj["entries"]:
            name=c.cover_key(record["path"])
            self.assertEqual(record["image"],c.BASE+"assets/social-cards/"+name+".jpg")
            self.assertNotIn(record["image"],urls)
            urls.add(record["image"])
            image=c.ROOT/"assets/social-cards"/(name+".jpg")
            self.assertTrue(image.is_file())
            self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(),record["sha256"])
            with Image.open(image) as opened:self.assertEqual(opened.size,(1200,630))
            page=c.ROOT/(record["path"]+"index.html")
            source=page.read_text(encoding="utf-8")
            self.assertEqual(source.count('<meta property="og:image" content="'),1)
            self.assertEqual(source.count('<meta name="twitter:image" content="'),1)
            expected_kind = ('approved_gameplay' if record['approved_screenshot'] else
                             'official_game_photo' if record['artwork'] else 'original_illustration')
            self.assertEqual(record['cover_kind'],expected_kind)
            self.assertIn(f'<meta name="gta6:cover-kind" content="{expected_kind}">',source)
            self.assertEqual(source.count('<meta name="gta6:cover-sha256" content="'),1)
            self.assertIn('<meta name="gta6:cover-sha256" content="'+record["sha256"]+'">',source)
            if record['path'] in c.GUIDE_PHOTOS and not record['approved_screenshot']:
                self.assertIn('Non mostra la procedura.',source)
            self.assertIn('content="'+record["image"]+'"',source)
            self.assertEqual(record["article_cover"],c.is_article(source,record["path"]))
            if record["article_cover"]:
                self.assertEqual(source.count('data-article-cover="shared-social"'),1)
                self.assertNotIn('class="ci-section-cover"',source)
                cover=source.split('data-article-cover="shared-social"',1)[1].split('</figure>',1)[0]
                self.assertIn('src="'+record["image"]+'"',cover)
                self.assertIn('loading="eager"',cover)
                self.assertIn('article-cover-v1.css?v=',source)
                self.assertLess(source.index('</h1>'),source.index('data-article-cover="shared-social"'))
                self.assertIn('<figcaption>',cover)
            else:
                self.assertNotIn('data-article-cover=',source)
        self.assertEqual(obj['article_covers'],sum(row['article_cover'] for row in obj['entries']))
        self.assertGreaterEqual(obj['article_covers'],67) # 55 trophies + 12 tutorial articles
        self.assertTrue((c.ROOT/"trofei/roadmap-platino/index.html").exists())
        self.assertTrue((c.ROOT/"collezionabili/percorsi/index.html").exists())


if __name__=="__main__":unittest.main()
