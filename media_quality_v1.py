"""Verify each visual guide's real image coverage before Pages deployment.

Five unique, relevant screenshots per guide is the editorial target, not a
license to fabricate maps or repeat images. A guide with fewer real images may
publish with a truthful warning, but never with broken URLs or remote hotlinks.
"""
from __future__ import annotations
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path('_site')
BASE='https://xfederiko11.github.io/gta-6/'
TARGET=5

class MediaTags(HTMLParser):
    def __init__(self):
        super().__init__(); self.real=[];self.missing=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='img' and 'data-visual-image' in a:
            self.real.append(a)
        if 'data-media-missing' in a:
            self.missing.append(a)

def audit(root=ROOT):
    pages=[]
    broken=[]
    guides=list((root/'guide-e-tutorial').glob('*/index.html'))
    save=root/'salvare-auto/index.html'
    if save.is_file(): guides.append(save)
    for page in sorted(guides):
        text=page.read_text(encoding='utf-8')
        # Read only article content, not related-guide cards or site navigation.
        marker='<article class="v-guide-main">'
        if marker not in text: continue
        article=text.split(marker,1)[1].split('</article><aside',1)[0]
        tags=MediaTags();tags.feed(article)
        keys=set()
        for a in tags.real:
            key=a['data-visual-image']
            src=a.get('src','')
            url=urlsplit(src)
            rel=url.path.removeprefix('/gta-6/')
            path=(root/rel).resolve()
            if (url.scheme!='https' or url.netloc!='xfederiko11.github.io'
                or not url.path.startswith('/gta-6/assets/visual/')
                or not path.is_relative_to(root.resolve()) or not path.is_file()):
                broken.append({'page':page.relative_to(root).as_posix(),'image':key,'src':src})
            for entry in a.get('srcset','').split(','):
                ref=entry.strip().split(' ')[0]
                if ref:
                    part=urlsplit(ref)
                    local=(root/part.path.removeprefix('/gta-6/')).resolve()
                    if not local.is_relative_to(root.resolve()) or not local.is_file():
                        broken.append({'page':page.relative_to(root).as_posix(),'image':key,'src':ref})
            if not a.get('alt'):
                broken.append({'page':page.relative_to(root).as_posix(),'image':key,'error':'alt missing'})
            keys.add(key)
        missing=sorted({a.get('data-media-missing') for a in tags.missing if a.get('data-media-missing')})
        pages.append({'path':page.relative_to(root).as_posix(),
                      'unique_real_images':len(keys),'target':TARGET,
                      'status':'target_met' if len(keys)>=TARGET else 'needs_more_verified_images',
                      'missing_sources':missing,'missing_count':len(missing)})
    if not pages: raise RuntimeError('No guide pages to check')
    report={'schema':'guide-media-quality-v1','target_unique_images':TARGET,
            'guides_checked':len(pages),'ready':sum(p['status']=='target_met' for p in pages),
            'below_target':sum(p['status']!='target_met' for p in pages),
            'broken_local_references':broken,'pages':pages,
            'editorial_policy':'Aim for five distinct, relevant, attributed images per guide (position, approach, action, result, confirmation). Never pad with duplicates or fabricated map locations. A missing source gets a working source link.'}
    (root/'media-quality.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('GUIDE_MEDIA_AUDIT',json.dumps({k:report[k] for k in ('guides_checked','ready','below_target')}),
          'invalid_references='+str(len(broken)))
    if broken: raise RuntimeError('Broken or remote visual image paths: '+repr(broken[:5]))
    return report

if __name__=='__main__': audit()
