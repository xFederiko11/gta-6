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

    def test_published_pages_have_distinct_public_og_and_real_jpegs(self):
        audit=c.ROOT/"social-cards-audit.json"
        if not audit.exists():
            self.skipTest("Generate the production _site before running public-card audit")
        obj=json.loads(audit.read_text(encoding="utf-8"))
        self.assertEqual(obj["schema"],"gta6-social-cards-v2")
        self.assertGreaterEqual(obj["pages"],65)
        self.assertEqual(obj["unique_images"],obj["pages"])
        # Article thumbnails must be topical text cards, not random promotional scenes.
        self.assertTrue(all(row['artwork'] is None for row in obj['entries'] if row['path']))
        self.assertLessEqual(obj['artwork_backed_cards'],1)
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
            self.assertIn('content="'+record["image"]+'"',source)
        self.assertTrue((c.ROOT/"trofei/roadmap-platino/index.html").exists())
        self.assertTrue((c.ROOT/"collezionabili/percorsi/index.html").exists())


if __name__=="__main__":unittest.main()
