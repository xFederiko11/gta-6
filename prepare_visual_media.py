"""Legacy visual-media references are link-only pending documented reuse rights.

This path must not fetch, hotlink, or restore old provider images. Independently
reviewed community assets and the frozen Rockstar archive use separate paths.
"""
import json
from pathlib import Path
import re


def prepare(entries, dest=Path('site/assets/visual'),
            manifest=Path('.visual-media/manifest.json')):
    # Validate all manifest rows before modifying any generated files.
    for key, entry in entries.items():
        if not re.fullmatch(r'[a-z0-9-]+', key):
            raise ValueError('Unsafe image manifest key')
        if entry.get('kind') not in {'screenshot', 'promotional'}:
            raise ValueError('Unknown legacy image kind')

    for key in entries:
        for width in (480, 960):
            (dest / f'{key}-{width}.webp').unlink(missing_ok=True)
        print('MEDIA_SOURCE_LINK_ONLY', key)

    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text('{}\n', encoding='utf-8')
    print('RESPONSIVE_MEDIA_READY', 0, 'of', len(entries))


if __name__ == '__main__':
    entries = json.loads(Path('data/visual_media.json').read_text(
        encoding='utf-8'))['images']
    prepare(entries)
