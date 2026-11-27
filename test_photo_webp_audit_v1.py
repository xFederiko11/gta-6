"""Offline regression checks for the read-only screenshot WebP preflight."""
import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from photo_webp_audit_v1 import WebPReviewError, inspect_webp_bytes


def _chunk(name: bytes, payload: bytes) -> bytes:
    return name + len(payload).to_bytes(4, "little") + payload + (b"\0" if len(payload) & 1 else b"")


def _webp(width=1920, height=1080, metadata=(), flags=0, lossless=False):
    if lossless:
        bits = (width - 1) | ((height - 1) << 14)
        image_name = b"VP8L"
        frame = b"\x2f" + bits.to_bytes(4, "little") + b"x" * 1800
    else:
        image_name = b"VP8 "
        frame = b"\0\0\0\x9d\x01\x2a" + width.to_bytes(2, "little") + height.to_bytes(2, "little") + b"x" * 1800
    chunks = []
    if flags or metadata:
        ext = bytes([flags]) + b"\0\0\0" + (width - 1).to_bytes(3, "little") + (height - 1).to_bytes(3, "little")
        chunks.append(_chunk(b"VP8X", ext))
    chunks.extend(_chunk(name, b"metadata") for name in metadata)
    chunks.append(_chunk(image_name, frame))
    body = b"WEBP" + b"".join(chunks)
    return b"RIFF" + len(body).to_bytes(4, "little") + body


class WebPPreflightTests(unittest.TestCase):
    def test_valid_webp_reports_technical_facts_but_never_approves(self):
        report = inspect_webp_bytes(_webp())
        self.assertEqual((report["width"], report["height"]), (1920, 1080))
        self.assertTrue(report["metadata_free"])
        self.assertEqual(report["technical_preflight"], "pass")
        self.assertFalse(report["publication_ready"])
        self.assertIn("inspect the rendered page at 390px and 1440px", report["human_review_required"])

    def test_exif_xmp_and_icc_chunks_are_rejected(self):
        for name in (b"EXIF", b"XMP ", b"ICCP"):
            with self.subTest(chunk=name), self.assertRaisesRegex(WebPReviewError, "metadata/animation"):
                inspect_webp_bytes(_webp(metadata=(name,)))

    def test_extended_webp_metadata_flags_are_rejected_even_without_chunks(self):
        with self.assertRaisesRegex(WebPReviewError, "opaque, static, and metadata-free"):
            inspect_webp_bytes(_webp(flags=0x08))

    def test_lossless_webp_is_rejected_when_opacity_cannot_be_proven(self):
        with self.assertRaisesRegex(WebPReviewError, "cannot be proven opaque"):
            inspect_webp_bytes(_webp(1280, 720, lossless=True))

    def test_low_resolution_and_oversized_dimensions_are_rejected(self):
        with self.assertRaisesRegex(WebPReviewError, "short edge"):
            inspect_webp_bytes(_webp(960, 480))
        with self.assertRaisesRegex(WebPReviewError, "safe image-processing limit"):
            inspect_webp_bytes(_webp(8192, 8192))

    def test_invalid_container_lengths_and_animation_are_rejected(self):
        image = _webp()
        with self.assertRaisesRegex(WebPReviewError, "RIFF length"):
            inspect_webp_bytes(image[:-1])
        with self.assertRaisesRegex(WebPReviewError, "metadata/animation"):
            inspect_webp_bytes(_webp(metadata=(b"ANIM",)))

    def test_approval_gate_rechecks_webp_and_visual_review_flags(self):
        import photo_intake_v4
        from visual_guide_content import enrich

        guides = json.loads(Path("data/guide.json").read_text(encoding="utf-8"))["guides"]
        guides += json.loads(Path("data/visual_guides.json").read_text(encoding="utf-8"))["guides"]
        guides = enrich(guides)
        requests = json.loads(Path("data/visual_requests.json").read_text(encoding="utf-8"))["guides"]
        clean = _webp()
        record = {
            "id": "review-proof-01", "guide_id": guides[0]["id"], "role": 1,
            "step_number": 1, "platform": "PS5",
            "rights": "explicit_nonexclusive_site_and_social", "author_confirmed": True,
            "approved_by": "xFederiko11", "human_reviewed": True,
            "gameplay_only": True, "no_real_people": True, "social_preview": False,
            "published": True, "approved_on": "2026-11-21",
            "source_post": "https://x.com/creator/status/123456789012",
            "consent_evidence": "https://x.com/creator/status/123456789013",
            "credit": "@creator", "alt": "Menu WAiNK aperto sul veicolo selezionato.",
            "caption": "Schermata del controllo WAiNK.",
            "source_sha256": hashlib.sha256(clean).hexdigest(),
            "file": "assets/approved/review-proof-01.webp",
            "framing_reviewed": True, "alt_reviewed": True,
            "mobile_reviewed": True, "desktop_reviewed": True,
        }
        original_cwd = Path.cwd()
        with TemporaryDirectory() as temp:
            os.chdir(temp)
            try:
                image_path = Path("site/assets/approved/review-proof-01.webp")
                image_path.parent.mkdir(parents=True)
                image_path.write_bytes(clean)
                registry = {"schema": "gta6-approved-screenshots-v4", "photos": [record]}
                with patch.object(photo_intake_v4, "IMAGE_DIR", Path("site/assets/approved")):
                    self.assertTrue(photo_intake_v4.validate_approved(registry, guides, requests))

                    image_path.write_bytes(_webp(metadata=(b"EXIF",)))
                    record["source_sha256"] = hashlib.sha256(image_path.read_bytes()).hexdigest()
                    with self.assertRaisesRegex(ValueError, "metadata"):
                        photo_intake_v4.validate_approved(registry, guides, requests)

                    image_path.write_bytes(clean)
                    record["desktop_reviewed"] = False
                    with self.assertRaisesRegex(ValueError, "framing, alt-text, mobile and desktop"):
                        photo_intake_v4.validate_approved(registry, guides, requests)
            finally:
                os.chdir(original_cwd)


    def test_workflow_doc_matches_lossy_vp8_preflight(self):
        text = Path("PHOTO-SCREENSHOT-WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("lossy VP8", text)
        self.assertIn("VP8L", text)
        self.assertIn("alpha hint cannot prove opacity", text)


if __name__ == "__main__":
    unittest.main()
