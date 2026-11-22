"""Verify each visual guide's real image coverage before Pages deployment.

Five unique, relevant screenshots per guide is the editorial target, not a
license to fabricate maps or repeat images. A guide with fewer real images may
publish with a truthful warning, but never with broken URLs or remote hotlinks.
"""
from __future__ import annotations
from html.parser import HTMLParser
import json
import re
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
    # The 11-photo-target audit covers the existing guide catalog only.
    # Moses' six-job article is a separate optional reference, not a 12th role-based submission.
    guides=[p for p in (root/'guide-e-tutorial').glob('*/index.html')
            if p.parent.name!='veicoli-per-moses']
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
        screenshot_keys=set()
        promotional_keys=set()
        for a in tags.real:
            key=a['data-visual-image']
            kind=a.get('data-visual-kind')
            if kind not in ('screenshot','promotional'):
                broken.append({'page':page.relative_to(root).as_posix(),'image':key,'error':'unknown or missing visual provenance'})
            elif kind=='screenshot':
                screenshot_keys.add(key)
            else:
                promotional_keys.add(key)
            src=a.get('src','')
            url=urlsplit(src)
            rel=url.path.removeprefix('/gta-6/')
            path=(root/rel).resolve()
            allowed_prefix=('/gta-6/assets/approved/' if
                            a.get('data-approved-community-photo') else '/gta-6/assets/visual/')
            if (url.scheme!='https' or url.netloc!='xfederiko11.github.io'
                or not url.path.startswith(allowed_prefix)
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
        # Only positively mapped action images meet the five-photo goal;
        # a shop facade is helpful context, not proof of a cash exploit.
        action_keys=set(re.findall(r'data-visual-proof-image="([^"]+)"',article))
        if not action_keys.issubset(screenshot_keys):
            broken.append({'page':page.relative_to(root).as_posix(),
                           'error':'action-proof marker does not match displayed image'})
        missing=sorted({a.get('data-media-missing') for a in tags.missing if a.get('data-media-missing')})
        pages.append({'path':page.relative_to(root).as_posix(),
                      'unique_real_images':len(keys),'target':TARGET,
                      'real_step_screenshots':len(action_keys),
                      'promotional_images':len(promotional_keys),
                      'status':'target_met' if len(action_keys)>=TARGET else 'needs_more_verified_images',
                      'missing_sources':missing,'missing_count':len(missing)})
    if not pages: raise RuntimeError('No guide pages to check')
    report={'schema':'guide-media-quality-v1','target_unique_images':TARGET,
            'target_unique_gameplay_screenshots':TARGET,
            'guides_checked':len(pages),'ready':sum(p['status']=='target_met' for p in pages),
            'below_target':sum(p['status']!='target_met' for p in pages),
            'gameplay_screenshots_in_guide':sum(p['real_step_screenshots'] for p in pages),
            'promotional_images_in_guide':sum(p['promotional_images'] for p in pages),
            'broken_local_references':broken,'pages':pages,
            'editorial_policy':'Five DISTINCT action-specific gameplay screenshots are the target. An image of a place, a third-party source link, promotional art or a video does NOT prove the numbered action. Missing evidence remains editorial debt; do not invent screenshots, map pins or rewards.'}
    (root/'media-quality.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('GUIDE_MEDIA_AUDIT',json.dumps({k:report[k] for k in ('guides_checked','ready','below_target')}),
          'invalid_references='+str(len(broken)))
    if broken: raise RuntimeError('Broken or remote visual image paths: '+repr(broken[:5]))
    return report

if __name__=='__main__': audit()
