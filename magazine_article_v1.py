"""Reader-first article enhancements; use only the built public catalog.

Never rewrite H1, canonical, cover, editorial text, dates or steps. Secret
trophies keep their original spoiler gating. No new media or runtime service.
"""
from datetime import date
from html import escape, unescape
from pathlib import Path
import json,re
from article_chronology_v1 import BASE,CATALOG,category_path

MAIN='<main class="wrap" id="contenuto">'
COVER='data-article-cover="shared-social"'
MARKER='data-magazine-article="v1"'
STEP_LIST='<ol class="v-steps">'
PATH=re.compile(r"(?:[a-z0-9-]+/)+")
IMAGE=re.compile(r"assets/(?:archive-thumbs/[a-f0-9]{16}\.webp|social-cards/[a-f0-9]{16}\.jpg)")

def esc(value):
    return escape(str(value),quote=True)

def load_catalog(root=Path("_site")):
    obj=json.loads((root/CATALOG).read_text(encoding="utf-8"))
    assert obj["schema"]=="gta6-public-archive-v2"
    rows=obj["items"]
    from article_tags_v1 import validate_item_tags
    assert all(validate_item_tags(r) for r in rows)
    result={r["path"]:r for r in rows}
    assert len(result)==len(rows)
    return result

def applicable(page,item):
    return bool(item and not item["secret"] and COVER in page and MAIN in page)

def _tag_ids(item):
    return {tag.get("id") for tag in item.get("tags",[]) if isinstance(tag,dict) and tag.get("id")}

def suggestions(item,catalog,limit=3):
    # Shared explicit tags can connect related guides across categories.
    # Glitches remain separate from legitimate routes.
    group=item["group"];tags=_tag_ids(item)
    peers=[]
    for value in catalog.values():
        if value["secret"] or value["path"]==item["path"]:
            continue
        if (group=="glitch") != (value["group"]=="glitch"):
            continue
        shared=len(tags&_tag_ids(value))
        if value["group"]==group or shared:
            peers.append((value,shared))
    peers.sort(key=lambda pair:(-pair[1],pair[0]["group"]!=group,pair[0]["sub"]!=item["sub"],pair[0].get("published") or "",pair[0]["title"].casefold()))
    return [value for value,_ in peers[:limit]]

def attr(track,event,target):
    if not track:return ""
    return (' data-umami-event="'+esc(event)+'" data-umami-event-placement="magazine-article"'
            ' data-umami-event-destination="'+esc(target)+'"')

def href(path):
    if not PATH.fullmatch(path):raise ValueError("Invalid public magazine path")
    return BASE+path

def article_bar(item,track):
    group=item["group"];sub=item["sub"]
    parent=category_path(group);child=category_path(group,sub)
    stamp=item["published"]
    date_html=('Pubblicato il <time datetime="'+esc(stamp)+'">'+date.fromisoformat(stamp).strftime("%d/%m/%Y")+'</time>') if stamp else "Data di pubblicazione non documentata"
    bar=('<div class="ma-article-bar" '+MARKER+' data-color="'+esc(item["color"])+'">'
            '<nav aria-label="Categoria dell’articolo"><a href="'+href(parent)+'"'+attr(track,"category-open",parent)+'>'+esc(item["group_label"])+'</a>'
            '<span aria-hidden="true">/</span><a href="'+href(child)+'"'+attr(track,"category-open",child)+'>'+esc(item["sub_label"])+'</a></nav>'
            '<div class="ma-byline"><span>GTA 6 Italia</span><span>'+date_html+'</span><span>'+esc(item["badge"])+'</span></div></div>')
    tags=item.get("tags",[])
    tag_nav=('<nav class="ma-tags" aria-label="Argomenti">'+''.join(
        '<a class="ma-tag" href="'+href(tag["path"])+'"'+attr(track,"article-tag-open",tag["id"])+'>'+esc(tag["label"])+'</a>'
        for tag in tags if isinstance(tag,dict) and tag.get("path") and tag.get("label"))+'</nav>' if tags else "")
    return bar+tag_nav
def step_index(page):
    if page.count(STEP_LIST)!=1:return page
    start=page.index(STEP_LIST)
    # Use the exact rendered headings, after existing visible spoiler notice.
    # Some steps contain nested numbered instructions (e.g. Moses).
    # Limit matching to the tutorial section, not the first closing ol.
    stop=page.index("</section>",start) if "</section>" in page[start:] else len(page)
    steps=page[start:stop]
    # Match every main step, including when it contains nested lists.
    if len(re.findall(r'<li class="v-step" id="passaggio-[0-9]+">',steps))!=len(re.findall(r'<li class="v-step" id="passaggio-[0-9]+">',page)):
        steps=page[start:]
    headings=re.findall(r'<li class="v-step" id="(passaggio-[0-9]+)">.*?<h3>(.*?)</h3>',steps,re.S)
    if not headings:return page
    assert [x[0] for x in headings]==["passaggio-"+str(i) for i in range(1,len(headings)+1)]
    links="".join('<a href="#'+ident+'"><span class="ma-step-number">'+str(i).zfill(2)+'</span><span>'+esc(unescape(re.sub(r"<[^>]+>","",label)))+'</span></a>'
                  for i,(ident,label) in enumerate(headings,1))
    nav=('<nav class="ma-step-index" data-magazine-steps aria-label="Indice dei passaggi"><details><summary><strong>Vai al passaggio</strong><span>'+str(len(headings))+' passaggi</span></summary><div>'+links+'</div></details></nav>')
    return page[:start]+nav+page[start:]

def related_card(item,track):
    path=item["path"];image=item["image"]
    if image and IMAGE.fullmatch(image):
        media='<img src="'+esc(BASE+image)+'" width="480" height="252" loading="lazy" decoding="async" alt=""><small class="ma-card-credit">'+esc(item["credit"])+'</small>'
    else:
        media=""
    return ('<a class="ma-related-card" data-related-article="'+esc(path)+'" href="'+href(path)+'"'+attr(track,"related-guide-open",path)+'>'+
            ('<span class="ma-card-media">'+media+'</span>' if media else '')+'<span class="ma-card-copy"><small>'+esc(item["sub_label"])+'</small>'
            '<strong>'+esc(item["title"])+'</strong><span>'+esc(item["summary"])+'</span><span class="ma-read">Leggi →</span></span></a>')

def related_panel(item,catalog,track):
    group=item["group"];path=category_path(group)
    cards=suggestions(item,catalog)
    return ('<section class="ma-related" data-magazine-related data-color="'+esc(item["color"])+'" aria-label="Articoli correlati per argomento">'
            '<div class="ma-related-head"><div><span>CONTINUA A ESPLORARE</span><h2>'+esc(item["group_label"])+'</h2></div>'
            '<a href="'+href(path)+'"'+attr(track,"category-open",path)+'>Tutta la categoria →</a></div>'+
            ('<div class="ma-related-grid">'+''.join(related_card(v,track) for v in cards)+'</div>' if cards else '<p>Apri la categoria per trovare gli articoli e gli aggiornamenti dedicati.</p>')+'</section>')

def enhance(page,path,catalog,track=False):
    item=catalog.get(path)
    if not applicable(page,item) or MARKER in page:return page
    start=page.index(MAIN)+len(MAIN)
    stop=page.index("</main>",start)
    inner=page[start:stop]
    assert len(re.findall(r"<h1(?:\s|>)",inner,re.I))==1,path
    inner=re.sub(r"<h1(?:\s|>)",lambda m:article_bar(item,track)+m.group(0),inner,count=1,flags=re.I)
    inner=step_index(inner)
    inner+=related_panel(item,catalog,track)
    return page[:start]+inner+page[stop:]

def verify(root=Path("_site")):
    catalog=load_catalog(root);count=steps=0
    for path,item in catalog.items():
        page=(root/path/"index.html").read_text(encoding="utf-8")
        if item["secret"]:
            assert MARKER not in page and 'data-magazine-related' not in page,path
            continue
        if COVER not in page:continue
        assert page.count(MARKER)==1 and page.count("data-magazine-related")==1,path
        assert re.search(r"</h1\s*><figure class=\"article-cover\"",page,re.I),path
        if item["published"]:assert 'datetime="'+item["published"]+'"' in page,path
        tag_nav=re.search(r'<nav class="ma-tags".*?</nav>',page,re.S)
        if item.get("tags"):
            assert tag_nav and all(href(tag["path"]) in tag_nav.group(0) for tag in item["tags"]),path
        actual=re.findall(r'data-related-article="([^"]+)"',page)
        expected=[v["path"] for v in suggestions(item,catalog)]
        assert actual==expected,path
        assert all(not catalog[p]["secret"] and
                   (catalog[p]["group"]==item["group"] or bool(_tag_ids(item)&_tag_ids(catalog[p]))) and
                   ((item["group"]=="glitch")== (catalog[p]["group"]=="glitch"))
                   for p in actual),path
        if STEP_LIST in page:
            assert page.count("data-magazine-steps")==1,path
            assert page.index("data-magazine-steps")<page.index(STEP_LIST),path
            ids=re.findall(r'<li class="v-step" id="(passaggio-[0-9]+)">',page)
            index=re.search(r'<nav class="ma-step-index".*?</nav>',page,re.S).group(0)
            assert re.findall(r'href="#(passaggio-[0-9]+)"',index)==ids,path
            steps+=1
        count+=1
    assert count>=100 and steps>=11,(count,steps)
    print("MAGAZINE_ARTICLES_STATIC_OK",count,"article layouts;",steps,"step indexes")
