import unittest,hashlib,json
from pathlib import Path
from editorial_feed_v1 import BASE,SCHEMA,validate,verify_page,valid_summary

class FeedTests(unittest.TestCase):
    def test_exact_photo_and_public_summary(self):
        path="articoli/example/";url=BASE+path
        image=BASE+"assets/social-cards/"+hashlib.sha256(path.encode()).hexdigest()[:16]+".jpg"
        jpeg=bytes.fromhex("ffd8ff")+b"x"*8500+bytes.fromhex("ffd9")
        digest=hashlib.sha256(jpeg).hexdigest()
        row={"url":url,"title":"GTA VI: articolo di prova","summary":"Una sintesi originale in italiano con una fotografia pertinente.","published":"2026-11-26","image":image,"sha256":digest,"kind":"official_game_photo"}
        html=f'<link rel="canonical" href="{url}"><meta name="gta6:share-summary" content="{row["summary"]}"><meta name="gta6:cover-kind" content="{row["kind"]}"><meta name="gta6:cover-sha256" content="{digest}"><meta property="og:image" content="{image}"><meta name="twitter:image" content="{image}">'
        validate({"schema":SCHEMA,"items":[row]});verify_page(row,html,jpeg)
        for bad in (dict(row,url="https://evil.test/articoli/example/"),dict(row,kind="original_illustration"),dict(row,summary="@someone prova")):
            with self.assertRaises(ValueError):validate({"schema":SCHEMA,"items":[bad]})
        with self.assertRaises(ValueError):verify_page(row,html,jpeg+b"x")
        with self.assertRaises(ValueError):verify_page(row,html.replace(row["summary"],"Old"),jpeg)
        with self.assertRaises(ValueError):validate({"schema":SCHEMA,"items":[row,row]})
        self.assertFalse(valid_summary("https://example.org/"+ "a"*40))

if __name__=="__main__":unittest.main()
