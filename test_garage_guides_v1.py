"""Check source-only garage content and canonical production output."""
import unittest
from pathlib import Path
from garage_guides_v1 import PATH,SOUTH,DOMESTIC,STORY,VANESSA,BUY,pages,SOUTH_MEDIA,MEDIA_REGISTRY
BASE="https://xfederiko11.github.io/gta-6/"
ROOT=Path("_site")
class GarageGuidesTests(unittest.TestCase):
    def test_source_only_and_distinct_unlocks(self):
        result={path:body for path,_,_,body,_ in pages(BASE)}
        self.assertEqual(len(result),8)
        from garage_guides_v1 import STORY_ROWS
        for ident,*_ in STORY_ROWS:
            self.assertIn('https://www.gtabase.com/gta-6/properties/',result[STORY+ident+'/'])
        self.assertEqual(result[PATH].count('data-garage-entry'),7)
        self.assertEqual(result[SOUTH].count('data-garage-step='),8)
        self.assertEqual(result[SOUTH].count('data-southside-map-pin='),6)
        self.assertEqual(result[SOUTH].count('data-youtube-id="mu_VCQKeXvM"'),6)
        self.assertEqual(result[SOUTH].count('class="v-video-reference" open'),6)
        self.assertIn('data-youtube-start="294"',result[SOUTH])
        self.assertIn('data-youtube-start="255"',result[SOUTH])
        self.assertIn('data-youtube-start="323"',result[SOUTH])
        self.assertIn("Capitolo minimo",result[SOUTH])
        self.assertIn("non concordano",result[SOUTH])
        self.assertEqual(MEDIA_REGISTRY["schema"],"gta6-editorial-media-rights-v1")
        self.assertEqual(SOUTH_MEDIA["southside-powerpyx-video"]["rights_status"],"youtube_platform_embed_only")
        self.assertEqual(sum(x["kind"]=="community_map_location_link" for x in MEDIA_REGISTRY["items"]),6)
        self.assertEqual(result[DOMESTIC].count('data-garage-step='),7)
        self.assertEqual(result[STORY].count('data-story-garage='),4)
        self.assertIn("1010",result[SOUTH])
        self.assertIn("11.600",result[DOMESTIC])
        self.assertIn("27.150",result[DOMESTIC])
        self.assertIn("Supply &amp; Demand",result[DOMESTIC])
        self.assertIn("25.000 GTA$",result[DOMESTIC])
        self.assertIn("Little Boxes",result[DOMESTIC])
        self.assertIn("non garantito per tutte le progressioni",result[DOMESTIC])
        self.assertIn("proprietà non confermata",result[PATH])
        self.assertIn(BASE+VANESSA,result[PATH])
        self.assertIn(BASE+BUY,result[PATH])
        self.assertIn("The Cartel Heist",result[PATH])
        for body in result.values():
            self.assertEqual(body.count("<h1>"),1)
            self.assertNotIn("<img",body)
            self.assertNotIn("<iframe",body)
            self.assertNotIn("data-pin-lat",body)
    def test_codes_preserve_digits_and_work_without_javascript(self):
        from garage_codes_v1 import CODES, code_field
        result={path:body for path,_,_,body,_ in pages(BASE)}
        self.assertIn('value="1010"',result[SOUTH])
        self.assertIn('value="92665"',result[PATH])
        self.assertEqual(CODES["invetero-spiderweb-coquette"],"092319")
        field=code_field("092319","Party House")
        self.assertIn('readonly',field)
        self.assertIn('value="092319"',field)
        self.assertIn('data-vc-copy-code hidden',field)
        self.assertIn('role="status"',field)
        with self.assertRaises(ValueError):code_field("invalid","Garage")
    def test_generated_pages_canonical_and_discoverable(self):
        self.assertTrue((ROOT/"sitemap.xml").exists())
        sitemap=(ROOT/"sitemap.xml").read_text()
        for path,_,_,_,kind in pages(BASE):
            html=(ROOT/path/"index.html").read_text()
            self.assertIn(BASE+path,sitemap)
            self.assertIn('rel="canonical" href="'+BASE+path+'"',html)
            self.assertEqual(html.count('<h1'),1)
            self.assertIn('vehicle-finder-v1.css?v=',html)
            self.assertIn('data-sunset-layout="right-blog"',html)
            if kind=="Article":
                self.assertIn('data-article-cover="shared-social"',html)
        for path,code in ((VANESSA,"92665"),("veicoli/declasse-applesauce-bobcat/","360782"),("veicoli/invetero-spiderweb-coquette/","092319")):
            self.assertIn('value="'+code+'"',(ROOT/path/"index.html").read_text())
        for path in ("salvare-auto/","guide-e-tutorial/","auto-speciali/","veicoli/",VANESSA,BUY):
            self.assertIn(BASE+PATH,(ROOT/path/"index.html").read_text())
if __name__=="__main__":unittest.main()
