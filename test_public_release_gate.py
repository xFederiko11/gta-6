"""Publishing-contract regressions: source-side editorial reports never reach Pages."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from public_release_gate import BASE, apply, verify


def page(text="Hello"):
    return '<!doctype html><html lang="it"><head><title>Guide</title></head><body>' + text + '</body></html>'


def fixture(root: Path):
    (root / "index.html").write_text(page('<a href="' + BASE + 'salvare-auto/">Guida</a>'), encoding="utf-8")
    (root / "salvare-auto").mkdir(parents=True)
    (root / "salvare-auto/index.html").write_text(page(
        '<ol class="v-steps"><li class="v-step"><figure><img data-visual-kind="screenshot" src="/gta-6/assets/real.webp"></figure>'
        '<p class="v-step-photo-gap" data-step-photo-status="missing">Segnaposto fotografico</p></li></ol>'
        '<aside id="contributi-foto" data-visual-request-id="registrare-auto-personale">'
        '<p class="v-visual-coverage" data-visual-screenshot-count="0">0/5 screenshot</p>'
        '<details><summary>55 richieste editoriali</summary></details></aside>'),
        encoding="utf-8")
    (root / "crescita-x").mkdir()
    (root / "crescita-x/index.html").write_text(page("Staff dashboard"), encoding="utf-8")
    (root / "screenshot-ps5/verifica").mkdir(parents=True)
    (root / "screenshot-ps5/verifica/index.html").write_text(page("Editorial ledger"), encoding="utf-8")
    (root / "growth-evidence-v1.json").write_text('{"internal": true}', encoding="utf-8")
    (root / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        '<url><loc>' + BASE + '</loc></url>'
        '<url><loc>' + BASE + 'salvare-auto/</loc></url>'
        '<url><loc>' + BASE + 'crescita-x/</loc></url>'
        '<url><loc>' + BASE + 'screenshot-ps5/verifica/</loc></url>'
        '</urlset>', encoding="utf-8")


class PublicReleaseGateTests(unittest.TestCase):
    def test_removes_operations_preserves_real_tutorial_screenshots(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            report = apply(root)
            self.assertIn("crescita-x/", report["removed_artifacts"])
            self.assertFalse((root / "crescita-x").exists())
            self.assertFalse((root / "screenshot-ps5/verifica").exists())
            self.assertFalse((root / "growth-evidence-v1.json").exists())
            html = (root / "salvare-auto/index.html").read_text(encoding="utf-8")
            self.assertIn('data-visual-kind="screenshot"', html)
            self.assertIn('id="contributi-foto"', html)
            self.assertIn('screenshot-ps5/invia/?guida=registrare-auto-personale', html)
            self.assertNotIn("0/5 screenshot", html)
            self.assertNotIn("Segnaposto fotografico", html)
            self.assertNotIn("55 richieste editoriali", html)
            sitemap = (root / "sitemap.xml").read_text(encoding="utf-8")
            self.assertIn(BASE + 'salvare-auto/', sitemap)
            self.assertNotIn(BASE + 'crescita-x/', sitemap)
            verify(root)
            self.assertEqual(apply(root)["updated_reader_pages"], 0)

    def test_rejects_leaked_operational_url_and_credential(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            apply(root)
            home = root / "index.html"
            home.write_text(page('<a href="' + BASE + 'crescita-x/">Interno</a>'), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "internal material"):
                verify(root)
            home.write_text(page('ghp_' + 'X' * 40), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Credential-like"):
                verify(root)

    def test_rejects_missing_public_home(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "Missing public homepage"):
                verify(Path(tmp))


if __name__ == "__main__":
    unittest.main()
