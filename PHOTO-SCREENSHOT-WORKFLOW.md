# Screenshot workflow — BOT X

The intake remains manual and consent-gated. The WebP preflight is read-only and reports technical facts; a passing result is **not** permission to publish.

1. **Acquire:** keep the creator's original capture. Tie it to one guide and one numbered gameplay step; don't download frames or images from third-party pages.
2. **Verify source and rights:** inspect the original public post and explicit non-exclusive reuse consent. Record both URLs and credit. A public post or checkbox alone is not approval.
3. **Select and crop:** choose the frame that proves the exact action. Crop only a derivative, keep relevant game UI/context visible, and retain the untouched original. Reject private messages, account IDs, facecam, or real people.
4. **Prepare:** export an opaque, static WebP between 1.5 KB and 4 MB. Keep at least 540 px on the short edge; avoid enlarging a small capture. Strip EXIF, XMP, and ICC metadata. Compress only as far as needed to fit the budget while keeping game text readable.
5. **Run the binary preflight:** `python3 photo_webp_audit_v1.py path/to/candidate.webp`. This checks the RIFF/WebP structure, dimensions, byte budget, animation, and metadata chunks, then prints a non-approval review checklist.
6. **Review accessibility and layout:** write concise alt text that describes the visible interface/action, not the filename. Render the target guide at 390 px and 1440 px; check that the screenshot is legible, uncropped by the layout, and credited directly below it.
7. **Publish only after review:** add the image and provenance record through the existing maintainer workflow. Mark source, gameplay/step match, framing, alt text, mobile and desktop review explicitly. Build validation rechecks the binary and hash; the public site must not ingest candidate files.

No screenshot, rights claim, crop decision, or visual approval is inferred by the preflight.
