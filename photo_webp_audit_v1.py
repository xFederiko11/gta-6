"""Read-only preflight for privacy-safe, legible GTA VI screenshot WebPs.

This checks the binary container only. It never verifies authorship, rights,
gameplay context, crop quality, or accessibility meaning, and never approves
or publishes a photo. Those remain explicit human review gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


MIN_BYTES = 1_500
MAX_BYTES = 4_000_000
MIN_EDGE = 540
MAX_EDGE = 8_192
MAX_PIXELS = 33_554_432
FORBIDDEN_CHUNKS = {b"EXIF", b"XMP ", b"ICCP", b"ANIM", b"ANMF"}


class WebPReviewError(ValueError):
    """The candidate WebP failed a technical or privacy check."""


def _chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    if len(data) < 20 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise WebPReviewError("Not a complete WebP RIFF container")
    if int.from_bytes(data[4:8], "little") != len(data) - 8:
        raise WebPReviewError("RIFF length does not match file length")

    result = []
    offset = 12
    while offset < len(data):
        if len(data) - offset < 8:
            raise WebPReviewError("Truncated WebP chunk header")
        name = data[offset:offset + 4]
        size = int.from_bytes(data[offset + 4:offset + 8], "little")
        start = offset + 8
        end = start + size
        padded_end = end + (size & 1)
        if end > len(data) or padded_end > len(data):
            raise WebPReviewError("Truncated WebP chunk data")
        if size & 1 and data[end] != 0:
            raise WebPReviewError("Invalid WebP chunk padding")
        result.append((name, data[start:end]))
        offset = padded_end
    if offset != len(data) or not result:
        raise WebPReviewError("Invalid WebP chunk layout")
    return result


def _vp8_dimensions(payload: bytes) -> tuple[int, int]:
    if len(payload) < 10 or payload[0] & 1 or payload[3:6] != b"\x9d\x01\x2a":
        raise WebPReviewError("Invalid VP8 key-frame header")
    width = int.from_bytes(payload[6:8], "little") & 0x3FFF
    height = int.from_bytes(payload[8:10], "little") & 0x3FFF
    return width, height


def _vp8l_dimensions(payload: bytes) -> tuple[int, int]:
    if len(payload) < 5 or payload[0] != 0x2F:
        raise WebPReviewError("Invalid VP8L lossless header")
    bits = int.from_bytes(payload[1:5], "little")
    if bits >> 29:
        raise WebPReviewError("Unsupported VP8L bitstream version")
    return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1


def inspect_webp_bytes(data: bytes) -> dict:
    """Return verified technical facts, or reject metadata/unsafe dimensions."""
    if not MIN_BYTES <= len(data) <= MAX_BYTES:
        raise WebPReviewError(f"WebP must be between {MIN_BYTES} bytes and {MAX_BYTES} bytes")
    chunks = _chunks(data)
    names = [name for name, _ in chunks]
    forbidden = sorted(name.decode("ascii", "replace") for name in names if name in FORBIDDEN_CHUNKS)
    if forbidden:
        raise WebPReviewError("Remove metadata/animation chunks: " + ", ".join(forbidden))
    if any(name not in {b"VP8X", b"VP8 ", b"VP8L"} for name in names):
        raise WebPReviewError("Unsupported WebP chunk; use a static opaque screenshot")
    if names.count(b"VP8X") > 1 or names.count(b"VP8 ") + names.count(b"VP8L") != 1:
        raise WebPReviewError("Expected one static WebP image payload")
    if b"VP8X" in names and names[0] != b"VP8X":
        raise WebPReviewError("VP8X must be the first chunk")

    payloads = dict(chunks)
    image_name = b"VP8 " if b"VP8 " in payloads else b"VP8L"
    image_size = _vp8_dimensions(payloads[image_name]) if image_name == b"VP8 " else _vp8l_dimensions(payloads[image_name])
    if b"VP8X" in payloads:
        header = payloads[b"VP8X"]
        if len(header) != 10 or header[0] != 0 or header[1:4] != b"\0\0\0":
            raise WebPReviewError("Extended WebP must be opaque, static, and metadata-free")
        width = int.from_bytes(header[4:7], "little") + 1
        height = int.from_bytes(header[7:10], "little") + 1
        if (width, height) != image_size:
            raise WebPReviewError("WebP canvas and encoded image dimensions differ")
    else:
        width, height = image_size

    if min(width, height) < MIN_EDGE:
        raise WebPReviewError(f"Both orientations need at least {MIN_EDGE}px on the short edge")
    if max(width, height) > MAX_EDGE or width * height > MAX_PIXELS:
        raise WebPReviewError("WebP dimensions exceed the safe image-processing limit")

    return {
        "format": "WebP",
        "width": width,
        "height": height,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "metadata_free": True,
        "static_opaque_image": True,
        "technical_preflight": "pass",
        "publication_ready": False,
        "human_review_required": [
            "verify source and explicit reuse permission",
            "match the screenshot to one exact gameplay step",
            "review composition and any crop without hiding evidence",
            "review concise, contextual alt text",
            "inspect the rendered page at 390px and 1440px",
            "confirm no real people, facecam, private messages, or account IDs",
        ],
    }


def inspect_webp(path: Path) -> dict:
    return inspect_webp_bytes(Path(path).read_bytes())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("webp", type=Path, help="Prepared WebP candidate; the file is read only")
    args = parser.parse_args(argv)
    try:
        report = inspect_webp(args.webp)
    except (OSError, WebPReviewError) as error:
        print(f"PHOTO_WEBP_REJECTED: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
