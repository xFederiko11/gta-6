"""Deterministic internal-link crawler tests, no external web requests."""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape
import unittest

from internal_link_graph_v1 import BASE, analyze, file_for, normalized_page_link, sitemap_urls


def fixture(root: Path):
    page_paths = ["", "trofei/", "guide-e-tutorial/", "guide-e-tutorial/meditazione-capitolo-1/", "unlinked/"]
    urls = [BASE + p for p in page_paths]
    xml = '<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(
        "<url><loc>" + escape(url) + "</loc></url>" for url in urls
    ) + "</urlset>"
    (root/"sitemap.xml").write_text(xml,encoding="utf-8")
    contents = {
        "": '<a href="/gta-6/trofei/">trofei</a><a href="guide-e-tutorial/">guide</a>',
        "trofei/": '<a href="../guide-e-tutorial/">guide</a>',
        "guide-e-tutorial/": '<a href="meditazione-capitolo-1/">meditazione</a>',
        "guide-e-tutorial/meditazione-capitolo-1/": '<a href="/gta-6/trofei/spoiler-temporaneo/">noindex intentional</a>',
        "unlinked/": "<p>Unlinked but in sitemap</p>",
    }
    for path, html in contents.items():
        f=root/path/"index.html"
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text("<!doctype html><html><body>"+html+"</body></html>",encoding="utf-8")


class InternalLinkGraphTests(unittest.TestCase):
    def test_normalizes_links_only_inside_our_project_and_never_uses_external_sites(self):
        page=BASE+"guide-e-tutorial/"
        self.assertEqual(normalized_page_link("../trofei/?query=1#foo",page), BASE+"trofei/")
        self.assertEqual(normalized_page_link("/gta-6/hdr-oled/",page), BASE+"hdr-oled/")
        self.assertEqual(normalized_page_link(BASE+"trofei/",page), BASE+"trofei/")
        for value in (
            "https://github.com/xFederiko11/gta-6/",
            "https://evil.example/gta-6/trofei/",
            "https://xfederiko11.github.io/other-repository/",
            "https://xfederiko11.github.io.evil.example/gta-6/",
            "javascript:alert(1)",
            "http://xfederiko11.github.io/gta-6/trofei/",
            "https://user@xfederiko11.github.io/gta-6/trofei/",
            "",
            "x" * 2050,
        ):
            with self.subTest(value=value):
                self.assertIsNone(normalized_page_link(value,page))

    def test_bfs_finds_orphans_and_does_not_mislabel_noindex_as_broken(self):
        with TemporaryDirectory() as folder:
            root=Path(folder);fixture(root)
            result=analyze(root)
            self.assertEqual(result["pages"],5)
            self.assertEqual(result["reachable"],4)
            self.assertEqual(result["not_linked_from_home"],1)
            self.assertEqual(result["orphan_sample"],[BASE+"unlinked/"])
            self.assertEqual(result["primary_hubs_clicks"][BASE+"trofei/"],1)
            self.assertEqual(result["primary_hubs_clicks"][BASE+"guide-e-tutorial/"],1)
            self.assertEqual(result["distance_distribution"],{0:1,1:2,2:1})
            self.assertEqual(result["html_links_outside_sitemap"],1)
            self.assertEqual(result["outside_sitemap_sample"][0]["target"], BASE+"trofei/spoiler-temporaneo/")

    def test_duplicate_sitemap_or_missing_html_fails_explicitly(self):
        with TemporaryDirectory() as folder:
            root=Path(folder);fixture(root)
            (root/"trofei/index.html").unlink()
            with self.assertRaisesRegex(ValueError,"Missing HTML"):
                analyze(root)
            fixture(root)
            xml=(root/"sitemap.xml").read_text(encoding="utf-8")
            xml=xml.replace("</urlset>",'<url><loc>'+BASE+'</loc></url></urlset>')
            (root/"sitemap.xml").write_text(xml,encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"repeated"):
                sitemap_urls(root)

    def test_real_production_hubs_are_reachable_without_javascript(self):
        root=Path("_site")
        if not (root/"sitemap.xml").exists():
            self.skipTest("Site must be built before production link analysis")
        result=analyze(root)
        self.assertGreater(result["pages"],80)
        self.assertGreater(result["links"],result["pages"])
        for site,dist in result["primary_hubs_clicks"].items():
            self.assertIsNotNone(dist,site)
            self.assertLessEqual(dist,2,site)
        self.assertLessEqual(result["reachable"],result["pages"])


if __name__=="__main__":
    unittest.main()
