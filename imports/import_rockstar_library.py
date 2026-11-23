"""Import exactly the 189 owner-supplied images from matching official archives."""
from pathlib import Path, PurePosixPath
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO
from PIL import Image
import hashlib, json, shutil

source=Path('site/assets/rockstar/gta-vi/manifest.json')
manifest=json.loads(source.read_text(encoding='utf-8'))
dest=Path('portal/site/assets/rockstar/gta-vi')
dest.mkdir(parents=True,exist_ok=True)
selected={'Vice_City_03.jpg','Leonida_Keys_01.jpg','Grassrivers_03.jpg','Port_Gellhorn_01.jpg','Ambrosia_01.jpg','Mount_Kalaga_National_Park_03.jpg'}
verified=[]
for archive in manifest['archives']:
    name=archive['file_name']
    url='https://media-rockstargames-com.akamaized.net/VI/downloads/screenshots/'+name
    print('Downloading official archive',name,flush=True)
    with urlopen(url,timeout=90) as response:
        payload=response.read(240_000_001)
    if len(payload)>240_000_000: raise ValueError('Archive too large')
    expected=[r for r in manifest['assets'] if r['original_archive']==name]
    with ZipFile(BytesIO(payload)) as z:
        actual={i.filename for i in z.infolist() if not i.is_dir()}
        if actual != {r['original_entry'] for r in expected}: raise ValueError('Archive entry mismatch')
        for row in expected:
            raw=z.read(row['original_entry'])
            if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:
                raise ValueError('Original differs from owner-supplied image: '+row['original_entry'])
            rel=PurePosixPath(row['file'])
            if rel.is_absolute() or '..' in rel.parts: raise ValueError('Unsafe path')
            target=dest/row['file']
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists() and target.read_bytes()!=raw: raise ValueError('Existing original differs')
            target.write_bytes(raw)
            with Image.open(BytesIO(raw)) as image:
                image.load()
                if image.size!=(3840,2160): raise ValueError('Unexpected dimensions')
                for width,path in row['variants'].items():
                    w=int(width)
                    photo=image.convert('RGB');photo.thumbnail((w,w*9//16))
                    out=dest/path;out.parent.mkdir(parents=True,exist_ok=True)
                    photo.save(out,'WEBP',quality=76 if w==480 else 85,method=4)
            verified.append(row['file'])
    print('Verified originals',len(expected),flush=True)
if len(verified)!=189 or len(set(verified))!=189: raise ValueError('Incomplete library')
shutil.copy2(source,dest/'manifest.json')
receipt={'schema':'gta6-rockstar-import-receipt-v1','verified_originals':len(verified),
         'bytes':sum(r['bytes'] for r in manifest['assets']),'verification':'Every original SHA-256 matches the owner-supplied archive manifest',
         'source_urls':['https://media-rockstargames-com.akamaized.net/VI/downloads/screenshots/'+a['file_name'] for a in manifest['archives']]}
(dest/'import-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('ROCKSTAR_IMPORT_VERIFIED',len(verified),flush=True)
