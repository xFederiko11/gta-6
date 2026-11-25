"""Prepare the existing official promotional assets, not publisher screenshots.
Legacy editorial screenshot URLs are source references only: an attribution
or a correct step match does not establish redistribution permission.
Community photos still use the separate existing approved-screenshots ledger.
"""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from PIL import Image,ImageOps

HOSTS={'www.rockstargames.com'}
LIMIT=6_000_000
Image.MAX_IMAGE_PIXELS=25_000_000
DEST=Path('site/assets/visual')
DEST.mkdir(parents=True,exist_ok=True)

def allowed(url):
    p=urlsplit(url)
    return p.scheme=='https' and p.hostname in HOSTS and not p.username and not p.password and p.port in (None,443)

def prepare(pair):
    key,entry=pair
    if not re.fullmatch(r'[a-z0-9-]+',key):
        raise ValueError('Unsafe image manifest key')
    if entry.get('kind') == 'screenshot':
        # Purge only our generated derivatives, not the reference or rights ledger.
        for width in (480,960):
            (DEST/f'{key}-{width}.webp').unlink(missing_ok=True)
        print('MEDIA_SOURCE_LINK_ONLY',key)
        return key,None
    if entry.get('kind') != 'promotional' or not allowed(entry['url']):
        raise ValueError('Unsafe promotional image manifest')
    try:
        request=Request(entry['url'],headers={'User-Agent':'GTA6Italia/visual-guide-image-build'})
        with urlopen(request,timeout=18) as response:
            if not allowed(response.url): raise ValueError('Unexpected image redirect')
            if not response.headers.get_content_type().startswith('image/'): raise ValueError('Non-image response')
            data=response.read(LIMIT+1)
        if len(data)>LIMIT: raise ValueError('Oversized media')
        with Image.open(BytesIO(data)) as original:
            original.load()
            image=ImageOps.exif_transpose(original).convert('RGB')
            if min(image.size)<250: raise ValueError('Image too small for a visual tutorial')
            record={}
            for width in (480,960):
                resized=image.copy()
                resized.thumbnail((width,round(width*image.height/image.width)),Image.Resampling.LANCZOS)
                target=DEST/f'{key}-{width}.webp'
                resized.save(target,'WEBP',quality=84,method=5)
                record[str(width)]='assets/visual/'+target.name
            record['source']=entry['source']
            record['credit']=entry['credit']
            record['width']=image.width
            record['height']=image.height
            print('MEDIA_READY',key)
            return key,record
    except Exception as error:
        print('MEDIA_ORIGINAL_FALLBACK',key,type(error).__name__)
        return key,None

if __name__=='__main__':
    entries=json.loads(Path('data/visual_media.json').read_text(encoding='utf-8'))['images']
    with ThreadPoolExecutor(max_workers=4) as pool:
        result=dict((key,value) for key,value in pool.map(prepare,entries.items()) if value)
    path=Path('.visual-media/manifest.json'); path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('RESPONSIVE_MEDIA_READY',len(result),'of',len(entries))
