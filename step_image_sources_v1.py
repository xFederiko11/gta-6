"""Reviewed off-site photographs indexed by exact GTA VI tutorial step.

This module NEVER downloads, embeds or republishes third-party images.
It only offers contextual links to publisher pages with a descriptive section,
and forbids unrelated or unreviewed photography inside numbered instructions.
"""
from __future__ import annotations

from html import escape
from urllib.parse import urlsplit
from pathlib import Path
import json
import re

PATH=Path('data/step_image_sources_v1.json')
ALLOWED={
    'gta6data.com',
    'www.gta6data.com',
    'insider-gaming.com',
    'www.insider-gaming.com',
    'www.pushsquare.com',
    'pushsquare.com',
}
SCHEMA='gta6-step-image-sources-v1'


def load():
    return json.loads(PATH.read_text(encoding='utf-8'))


def validate(data, guides):
    if data.get('schema') != SCHEMA or not isinstance(data.get('guides'),dict):
        raise ValueError('Invalid tutorial image-source schema')
    if not re.fullmatch(r'20\d\d-\d\d-\d\d',str(data.get('reviewed',''))):
        raise ValueError('Tutorial image-source review date missing')
    by_id={g['id']:g for g in guides}
    if len(by_id)!=len(guides):
        raise ValueError('Duplicate guide id')
    count=0
    for guide_id,steps in data['guides'].items():
        if guide_id not in by_id or not isinstance(steps,dict):
            raise ValueError('Unknown guide with photographic references')
        for index,item in steps.items():
            if not re.fullmatch(r'0|[1-9][0-9]*',str(index)):
                raise ValueError('Invalid photographed step number')
            if int(index)>=len(by_id[guide_id]['steps']):
                raise ValueError('Photographic reference is beyond the guide')
            if not isinstance(item,dict) or set(item)!={'source','label','section','scope'}:
                raise ValueError('Invalid source photograph metadata')
            link=urlsplit(item['source'])
            if (link.scheme!='https' or link.hostname not in ALLOWED
                or link.username or link.password or link.port
                or not re.fullmatch(r'/(?:[a-z0-9-]+/)*[a-z0-9-]+/?',link.path)
                or link.query or link.fragment):
                raise ValueError('Untrusted source image link')
            for key in ('label','section','scope'):
                value=item[key]
                if not isinstance(value,str) or not 10<=len(value)<=180 or '<' in value or '>' in value:
                    raise ValueError('Missing actionable source photo description')
            count+=1
    return count


def render(data, guide_id, index):
    ref=data['guides'].get(guide_id,{}).get(str(index))
    if not ref:
        return ''
    label=escape(ref['label'])
    source=escape(ref['source'],quote=True)
    section=escape(ref['section'])
    scope=escape(ref['scope'])
    return (
        '<div class="v-external-step-photo" data-photo-source-guide="'+escape(guide_id,quote=True)
        +'" data-photo-source-step="'+str(index+1)+'">'
        '<div class="v-external-step-photo-title"><span aria-hidden="true">📷</span>'
        '<strong>FOTO DEL PASSAGGIO · SITO ORIGINALE</strong></div>'
        '<p>'+label+'</p>'
        '<a href="'+source+'" target="_blank" rel="noopener noreferrer">'
        'Apri la fonte con le foto ↗</a>'
        '<small>Cerca la sezione: <b>'+section+'</b>. '+scope
        +'. La foto non è ospitata da GTA VI Italia.</small></div>'
    )
