"""Synthetic fixtures only. No live analytics traffic or data."""
from datetime import date
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from import_umami_popular_v1 import canonical_path, convert, write_snapshot
from magazine_popular_v1 import validate

TODAY=date(2026,11,28)
START=date(2026,11,21)
END=date(2026,11,27)
CATALOG={f"guide/{c}/":{"secret":False} for c in "abcdef"}
CATALOG["trofei/secret/"]={"secret":True}

class UmamiAggregateTests(unittest.TestCase):
    def convert(self,text,start=START,end=END):
        return convert(text,start,end,TODAY,CATALOG)
    def test_only_top_five_public_articles_written(self):
        csv="path,pageviews\n/gta-6/,999\n/gta-6/guide/a/,8\nhttps://xfederiko11.github.io/gta-6/guide/b,12\n"
        csv+="guide/c/index.html,3\nguide/d/,2\nguide/e/,1\nguide/f/,20\ntrofei/secret/,888\narticoli/,777\n"
        result=self.convert(csv)
        self.assertEqual([(r["path"],r["pageviews"]) for r in result["items"]],
                         [("guide/f/",20),("guide/b/",12),("guide/a/",8),("guide/c/",3),("guide/d/",2)])
        self.assertEqual(validate(result,TODAY,CATALOG)[2][0],("guide/f/",20))
        with TemporaryDirectory() as tmp:
            out=Path(tmp)/"data/popular_articles_v1.json"
            write_snapshot(result,out)
            text=out.read_text()
            self.assertNotIn("trofei/secret",text)
            self.assertNotIn("999",text)
            self.assertEqual(json.loads(text),result)
    def test_canonical_paths(self):
        for p in ("/gta-6/guide/a","guide/a/","https://xfederiko11.github.io/gta-6/guide/a/index.html"):
            self.assertEqual(canonical_path(p),"guide/a/")
    def test_reject_raw_extra_columns_private_parameters_or_duplicates(self):
        for data in (
            "path,pageviews,session_id\nguide/a/,1,PRIVATE\n",
            "path,pageviews\n/gta-6/guide/a/?email=private,1\n",
            "path,pageviews\nhttps://example.com/gta-6/guide/a/,1\n",
            "path,pageviews\n/gta-6/guide/a,1\nguide/a/,2\n",
            "path,pageviews\nguide/a/,-1\n",
            "path,pageviews\nguide/a/,1.5\n",
            "path,pageviews\nguide/a/,NaN\n",
            "path,pageviews\nguide/a/,0\n",
            "path,pageviews\ntrofei/secret/,9\n",
        ):
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.convert(data)
    def test_stale_or_future_dates(self):
        data="path,pageviews\nguide/a/,5\n"
        with self.assertRaises(ValueError):
            self.convert(data,start=date(2026,11,1),end=date(2026,11,10))
        with self.assertRaises(ValueError):
            self.convert(data,end=date(2026,11,29))
