import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from article_tags_v1 import build_archives, canonical_tag_id, chapter_order, enrich_item, tag_ids_for, validate_item_tags

BASE = "https://example.test/"

def item(path, title, group="guide", sub="missioni", category="Guide", **extra):
    row = {
        "path": path, "title": title, "category": category, "group": group, "sub": sub,
        "group_label": group.title(), "sub_label": sub.title(), "color": "cyan",
        "published": "2026-11-27", "badge": "Guida", "summary": "",
        "secret": False, "image": "", "credit": "",
    }
    row.update(extra)
    return enrich_item(row)

class ArticleTagsTests(unittest.TestCase):
    def test_brand_and_chapter_aliases_resolve_to_one_canonical_id(self):
        self.assertEqual(canonical_tag_id("GTA 6"), "gta-vi")
        self.assertEqual(canonical_tag_id("GTA6"), "gta-vi")
        self.assertEqual(canonical_tag_id("Grand Theft Auto VI"), "gta-vi")
        self.assertEqual(canonical_tag_id("Capitolo 1"), "capitolo-1")
        self.assertEqual(canonical_tag_id("Chapter One"), "capitolo-1")

    def test_only_explicit_article_evidence_assigns_tags_or_story_order(self):
        southside = item("garage-gratuiti/southside-storage/", "Southside Storage: 1010 Murals", "veicoli", "garage", "Garage")
        self.assertEqual(set(tag_ids_for(southside)), {"1010-murales", "garage-gratuiti"})
        self.assertIsNone(chapter_order(southside))
        later = item("guide-e-tutorial/wyman-capitolo-1/", "Capitolo 1: Randy a Vice City")
        self.assertEqual(chapter_order(later), 1)
        self.assertTrue({"capitolo-1", "randy", "vice-city", "missioni"}.issubset(tag_ids_for(later)))
        self.assertLessEqual(len(tag_ids_for(later)), 8)

    def test_secret_articles_receive_no_public_tags(self):
        secret = item("trofei/trofeo-segreto-1/", "Trofeo segreto n. 1", "platino", "trofei", "Trofei", secret=True)
        self.assertEqual(tag_ids_for(secret), [])
        self.assertTrue(validate_item_tags(enrich_item(secret)))

    def test_summary_does_not_infer_unlock_chapter(self):
        row = item("guide-e-tutorial/garage/", "Garage: requisiti", summary="Disponibile dopo il Capitolo 3")
        self.assertIsNone(chapter_order(row))

    def test_archive_indexing_threshold_duplicates_sitemap_and_filters(self):
        rows = [
            item("guide-e-tutorial/randy-one/", "Randy: primo veicolo", "veicoli", "posizioni", "Veicoli"),
            item("guide-e-tutorial/randy-two/", "Randy: seconda richiesta", "guide", "missioni", "Guide"),
            item("articoli/randy-three/", "Randy: guida aggiornata", "news", "patch", "News"),
            item("trofei/trofeo-segreto-1/", "Trofeo segreto n. 1", "platino", "trofei", "Trofei", secret=True),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
            sitemap = ET.Element("{"+ns+"}urlset")
            ET.SubElement(sitemap, "{"+ns+"}url")
            ET.ElementTree(sitemap).write(root / "sitemap.xml", encoding="utf-8", xml_declaration=True)
            def card(row, url):
                return '<a class="ed-home-card chronology-card" href="'+url(row["path"])+'"><strong class="archive-title">'+row["title"]+'</strong></a>'
            def layout(title, desc, path, body, section, robots="index,follow", structured=None):
                return '<html><head><meta name="robots" content="'+robots+'"></head><body>'+body+'</body></html>'
            def url(path):
                return BASE+path
            def crumbs(parts):
                return '<nav>'+''.join(label for label, _ in parts)+'</nav>'
            indexed = build_archives(rows, root, layout_fn=layout, url_fn=url, crumbs_fn=crumbs, card_fn=card)
            self.assertEqual(indexed, ["articoli/tag/randy/"])
            html = (root/"articoli/tag/randy/index.html").read_text(encoding="utf-8")
            self.assertIn("3 articoli", html)
            self.assertIn("data-tag-category", html)
            self.assertIn("data-tag-sort", html)
            self.assertNotIn("Trofeo segreto", html)
            sitemap_text = (root/"sitemap.xml").read_text(encoding="utf-8")
            self.assertIn(url("articoli/tag/randy/"), sitemap_text)
            self.assertNotIn("articoli/tag/gta-vi/", sitemap_text)

if __name__ == "__main__":
    unittest.main()
