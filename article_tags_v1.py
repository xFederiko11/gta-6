"""Curated, canonical article tags and static tag archives.

Tags are assigned only from existing article metadata and explicit text signals.
Archives are user-facing across categories; thin or duplicate collections are noindex.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET

TAG_DEFINITIONS = {
    "gta-vi": {"label": "GTA VI", "intro": "GTA 6 e GTA VI sono nomi equivalenti. Il tag viene normalizzato e non crea un archivio generico duplicato.", "aliases": ("GTA 6", "GTA6", "Grand Theft Auto VI")},
    "capitolo-1": {"label": "Capitolo 1", "intro": "Guide che citano esplicitamente il Capitolo 1. Il tag non prova da solo prerequisiti o disponibilità minima.", "aliases": ("Cap. 1", "Chapter 1", "Chapter One")},
    "garage-gratuiti": {"label": "Garage gratuiti", "intro": "Guide sui garage gratuiti e sui relativi sblocchi documentati.", "aliases": ("garage gratis", "free garages")},
    "auto-e-veicoli": {"label": "Auto e veicoli", "intro": "Guide dedicate ai veicoli, alla registrazione, alla ricerca e alla vendita.", "aliases": ("auto", "macchine", "automobili", "cars")},
    "codici-ps5": {"label": "Codici PS5", "intro": "Codici e trucchi PS5, separati dalle guide legittime e dai glitch.", "aliases": ("trucchi", "cheat", "cheat codes")},
    "auto-rare": {"label": "Auto rare", "intro": "Guide che identificano esplicitamente auto rare o difficili da trovare.", "aliases": ("auto rara", "rare cars")},
    "veicoli-speciali": {"label": "Veicoli speciali", "intro": "Veicoli descritti esplicitamente come speciali nelle rispettive guide.", "aliases": ("veicolo speciale", "special vehicles")},
    "1010-murales": {"label": "1010 Murals", "intro": "Guide ai cinque murales collegati al registro 1010 Murals e al garage Southside Storage.", "aliases": ("murales 1010", "southside storage")},
    "waink": {"label": "WAiNK", "intro": "Guide che citano lo scanner WAiNK, le scansioni e i relativi obiettivi.", "aliases": ("wa ink", "wa-in-k")},
    "randy": {"label": "Randy", "intro": "Guide e richieste associate a Randy, senza dedurre ricompense o disponibilità non documentate.", "aliases": ("randy",)},
    "moses": {"label": "Moses", "intro": "Guide e richieste associate a Moses, con requisiti e fonti descritti nelle singole pagine.", "aliases": ("moses",)},
    "vice-city": {"label": "Vice City", "intro": "Articoli che citano esplicitamente Vice City.", "aliases": ("vice city",)},
    "port-gellhorn": {"label": "Port Gellhorn", "intro": "Articoli che citano esplicitamente Port Gellhorn.", "aliases": ("port gellhorn",)},
    "collezionabili": {"label": "Collezionabili", "intro": "Checklist e percorsi per gli oggetti collezionabili descritti nelle guide.", "aliases": ("collectibles", "oggetti da collezione")},
    "mancabili": {"label": "Contenuti mancabili", "intro": "Contenuti indicati esplicitamente come mancabili o non recuperabili in seguito.", "aliases": ("mancabile", "missable")},
    "trofei": {"label": "Trofei", "intro": "Guide ai trofei e alle attività collegate al completamento.", "aliases": ("trofeo", "trophy", "trophies")},
    "trofei-bronzo": {"label": "Trofei Bronzo", "intro": "Guide il cui contenuto identifica esplicitamente il grado Bronzo.", "aliases": ("trofeo bronzo", "bronze trophy")},
    "platino": {"label": "Platino", "intro": "Guide che citano esplicitamente il Platino o la roadmap del completamento.", "aliases": ("platinum", "platino ps5")},
    "glitch": {"label": "Glitch", "intro": "Anomalie ed exploit separati dalle strategie legittime.", "aliases": ("glitches", "exploit")},
    "denaro": {"label": "Denaro", "intro": "Guide su denaro e bottini. Le procedure restano distinte dai glitch.", "aliases": ("soldi", "money", "gta$")},
    "ps5-pro": {"label": "PS5 Pro", "intro": "Impostazioni o guide che nominano esplicitamente PS5 Pro.", "aliases": ("playstation 5 pro",)},
    "hdr": {"label": "HDR", "intro": "Profili e consigli HDR con i limiti di verifica indicati nella guida.", "aliases": ("high dynamic range",)},
    "oled": {"label": "OLED", "intro": "Schede che riguardano display OLED.", "aliases": ("tv oled",)},
    "meditazioni": {"label": "Meditazioni", "intro": "Guide alle meditazioni e alla relativa checklist.", "aliases": ("meditazione",)},
    "missioni": {"label": "Missioni", "intro": "Guide che appartengono alle missioni o citano esplicitamente una procedura di missione.", "aliases": ("missione", "missions")},
    "cento-percento": {"label": "Completamento 100%", "intro": "Checklist e guide che citano esplicitamente il completamento al 100%.", "aliases": ("100%", "100 percento", "completamento al 100%")},
}

def _words(value: object) -> str:
    value = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii").casefold()
    value = re.sub(r"\bgta\s*6\b|\bgta\s+vi\b|grand theft auto\s+(?:6|vi)\b", "gta vi", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()

_ALIAS_TO_ID = {}
for _tag_id, _definition in TAG_DEFINITIONS.items():
    for _alias in (_tag_id.replace("-", " "), _definition["label"], *_definition["aliases"]):
        _key = _words(_alias)
        if _key in _ALIAS_TO_ID and _ALIAS_TO_ID[_key] != _tag_id:
            raise ValueError("Ambiguous tag alias: " + _key)
        _ALIAS_TO_ID[_key] = _tag_id

def canonical_tag_id(value: object) -> str | None:
    """Resolve a label, slug, or alias to one canonical tag ID."""
    return _ALIAS_TO_ID.get(_words(value))

def tag_path(tag_id: str) -> str:
    if tag_id not in TAG_DEFINITIONS:
        raise ValueError("Unknown article tag")
    return "articoli/tag/" + tag_id + "/"

def chapter_order(item: dict) -> int | None:
    """Return only an explicitly named chapter; never infer unlock order."""
    text = _words(" ".join(str(item.get(k, "")) for k in ("path", "title")))
    match = re.search(r"\b(?:capitolo|chapter)\s+([1-9][0-9]?)\b", text)
    return int(match.group(1)) if match else None

def tag_ids_for(item: dict) -> list[str]:
    if item.get("secret"):
        return []
    path = str(item.get("path", ""))
    group = str(item.get("group", ""))
    sub = str(item.get("sub", ""))
    category = str(item.get("category", ""))
    text = _words(" ".join(str(item.get(k, "")) for k in ("path", "title", "category", "group", "sub", "summary", "badge")))
    if group == "glitch" or category.casefold() == "glitch":
        return ["glitch"]
    if group == "trucchi" or category.casefold() == "trucchi":
        return ["codici-ps5"]
    found = []
    def add(tag_id: str) -> None:
        if tag_id not in found:
            found.append(tag_id)
    chapter = chapter_order(item)
    if chapter == 1:
        add("capitolo-1")
    if group == "veicoli" or (group == "soldi" and sub == "vendita"):
        add("auto-e-veicoli")
    if path == "garage-gratuiti/southside-storage/" or "1010 murals" in text:
        add("1010-murales")
    if (group == "veicoli" and sub == "garage") or path.startswith("garage-gratuiti/"):
        add("garage-gratuiti")
    if "wa ink" in text or "waink" in text:
        add("waink")
    if re.search(r"\brandy\b", text):
        add("randy")
    if re.search(r"\bmoses\b", text):
        add("moses")
    if "vice city" in text:
        add("vice-city")
    if "port gellhorn" in text:
        add("port-gellhorn")
    if (group == "platino" and sub == "collezionabili") or path.startswith("collezionabili/"):
        add("collezionabili")
    if group == "soldi" or "gta$" in str(item.get("title", "")).casefold():
        add("denaro")
    if group == "platino" and (sub in ("trofei", "roadmap", "sfide") or "trofeo" in text):
        add("trofei")
    if group == "platino" and ("platino" in text or sub == "roadmap"):
        add("platino")
    if (group == "platino" and sub == "meditazione") or "meditaz" in text:
        add("meditazioni")
    if group == "hdr" or category.casefold() == "hdr oled":
        add("hdr")
        add("oled")
    if "ps5 pro" in text:
        add("ps5-pro")
    if "auto rare" in text or "auto rara" in text:
        add("auto-rare")
    if "veicoli speciali" in text or "veicolo speciale" in text:
        add("veicoli-speciali")
    if "mancabile" in text or "mancabili" in text or "missable" in text:
        add("mancabili")
    if re.search(r"\b100\s+percento\b", text) or "100-percento" in path or "completamento al 100" in text:
        add("cento-percento")
    if group == "guide" and (sub == "missioni" or "missione" in text or "missioni" in text):
        add("missioni")
    if "bronzo" in text or "bronze trophy" in text:
        add("trofei-bronzo")
    return found[:8]

def enrich_item(item: dict) -> dict:
    result = dict(item)
    ids = tag_ids_for(result)
    result["tags"] = [{"id": tag_id, "label": TAG_DEFINITIONS[tag_id]["label"], "path": tag_path(tag_id), "aliases": list(TAG_DEFINITIONS[tag_id]["aliases"])} for tag_id in ids]
    result["chapter_order"] = chapter_order(result)
    return result

def validate_item_tags(item: dict) -> bool:
    tags = item.get("tags", [])
    if not isinstance(tags, list) or len(tags) > 8:
        return False
    ids = []
    for tag in tags:
        if not isinstance(tag, dict) or tag.get("id") not in TAG_DEFINITIONS:
            return False
        if tag.get("path") != tag_path(tag["id"]) or tag.get("label") != TAG_DEFINITIONS[tag["id"]]["label"]:
            return False
        if tag.get("aliases") != list(TAG_DEFINITIONS[tag["id"]]["aliases"]):
            return False
        ids.append(tag["id"])
    if len(ids) != len(set(ids)) or (item.get("secret") and tags):
        return False
    if not item.get("secret") and item.get("group") in ("glitch","trucchi"):
        if ids != (["glitch"] if item["group"]=="glitch" else ["codici-ps5"]):
            return False
    order = item.get("chapter_order")
    return order is None or (isinstance(order, int) and 1 <= order <= 99)

def _card(item: dict, url, card_fn=None) -> str:
    if card_fn is None:
        from article_chronology_v1 import card as card_fn
    html_card = card_fn(item, url)
    marker = '<a class="ed-home-card chronology-card"'
    if marker not in html_card:
        raise ValueError("Chronology card contract changed")
    attrs = (' data-tag-archive-card data-published="' + escape(str(item.get("published") or ""), quote=True) +
             '" data-story-order="' + escape(str(item.get("chapter_order") or ""), quote=True) + '"')
    return html_card.replace(marker, marker + attrs, 1)

def _render_controls(items: list[dict]) -> str:
    groups = {}
    for item in items:
        groups[item["group"]] = item["group_label"]
    options = '<option value="">Tutte le categorie</option>' + "".join(
        '<option value="' + escape(group, quote=True) + '">' + escape(label) + '</option>'
        for group, label in sorted(groups.items(), key=lambda pair: pair[1].casefold()))
    return ('<div class="ma-tag-controls" data-tag-archive-controls hidden>'
            '<label>Categoria<select data-tag-category>' + options + '</select></label>'
            '<label>Ordina per<select data-tag-sort>'
            '<option value="recent">Data più recente</option>'
            '<option value="story">Progressione con capitolo documentato</option>'
            '<option value="title">Titolo A–Z</option></select></label></div>'
            '<p class="ma-tag-count" role="status" aria-live="polite" data-tag-count hidden></p>')

def build_archives(items: list[dict], root: Path = Path("_site"), *, layout_fn=None, url_fn=None, crumbs_fn=None, card_fn=None) -> list[str]:
    """Write crawlable tag archives, retaining navigation for thin collections."""
    root = Path(root)
    if layout_fn is None or url_fn is None or crumbs_fn is None:
        import build_visual_site as visual
        from reader_experience import transform
        url_fn = url_fn or visual.url
        crumbs_fn = crumbs_fn or visual.legacy.crumbs
        if layout_fn is None:
            # Archives are built after the original reader transform. Reuse
            # the exact reader asset digest and production analytics setting,
            # without copying unrelated page markup or sending telemetry.
            release = json.loads((root / "design-version.json").read_text(encoding="utf-8"))
            version = release["reader_asset_version"]
            archive = (root / "articoli/index.html").read_text(encoding="utf-8")
            site_id = re.search(r'<script id="growth-analytics-v1"[^>]*\bdata-website-id="([^"]+)"', archive)
            if 'id="growth-analytics-v1"' in archive and not site_id:
                raise ValueError("Cannot determine existing analytics configuration")
            def layout_fn(*args, **kwargs):
                return transform(visual.layout(*args, **kwargs), version=version,
                                 umami_website_id=site_id.group(1) if site_id else None)
    public = [item for item in items if not item.get("secret") and item.get("path")]
    category_sets = set()
    groups = {}
    for item in public:
        groups.setdefault((item.get("group", ""), item.get("sub", "")), set()).add(item["path"])
        groups.setdefault((item.get("group", ""), ""), set()).add(item["path"])
    category_sets.update(frozenset(value) for value in groups.values())
    tag_items = {}
    for item in public:
        for tag in item.get("tags", []):
            if tag.get("id") in TAG_DEFINITIONS:
                tag_items.setdefault(tag["id"], {})[item["path"]] = item
    sitemap = root / "sitemap.xml"
    if not sitemap.is_file():
        raise FileNotFoundError("Built sitemap is required before tag archives")
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    tree = ET.parse(sitemap)
    sitemap_root = tree.getroot()
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    for node in list(sitemap_root):
        loc = node.find(ns + "loc")
        if loc is not None and loc.text and "/articoli/tag/" in loc.text:
            sitemap_root.remove(node)
    indexable_paths = []
    seen_sets = set()
    # A real, crawlable directory for the breadcrumb and global navigation.
    directory_path = "articoli/tag/"
    directory_body = (crumbs_fn([("Articoli", "articoli/"), ("Tag", directory_path)]) +
                      '<section class="ed-intro archive-intro"><h1>Argomenti GTA VI</h1>'
                      '<p>Esplora i tag editoriali: un articolo può appartenere a più argomenti.</p></section>'+
                      '<nav class="ma-tags ma-tag-directory" data-tag-directory aria-label="Tutti gli argomenti">'+
                      "".join('<a class="ma-tag" href="'+escape(url_fn(tag_path(tag_id)),quote=True)+'">'+
                              escape(definition["label"])+' <small>'+str(len(tag_items[tag_id]))+'</small></a>'
                              for tag_id,definition in TAG_DEFINITIONS.items() if tag_id in tag_items)+
                      '</nav>')
    directory = root / directory_path / "index.html"
    directory.parent.mkdir(parents=True,exist_ok=True)
    directory.write_text(layout_fn("Argomenti GTA VI: tag delle guide","Tutti i tag editoriali delle guide GTA VI.",
                         directory_path,directory_body,"articles",robots="noindex,follow",
                         structured={"@context":"https://schema.org","@type":"CollectionPage",
                                     "name":"Argomenti GTA VI","url":url_fn(directory_path),"inLanguage":"it-IT"}),
                         encoding="utf-8")
    for tag_id, definition in TAG_DEFINITIONS.items():
        selected_map = tag_items.get(tag_id, {})
        if not selected_map:
            continue
        selected = sorted(selected_map.values(), key=lambda row: (row.get("published") or "", row.get("title", "").casefold()), reverse=True)
        selected_paths = frozenset(item["path"] for item in selected)
        duplicate = selected_paths in category_sets or selected_paths in seen_sets
        seen_sets.add(selected_paths)
        indexable = len(selected) >= 3 and not duplicate
        path = tag_path(tag_id)
        title = "Tag " + definition["label"] + " GTA VI: guide e articoli"
        description = definition["intro"]
        crumbs = crumbs_fn([("Articoli", "articoli/"), ("Tag", "articoli/tag/"), (definition["label"], path)])
        body = (crumbs + '<section class="ed-intro archive-intro"><span class="archive-kicker">ARGOMENTI GTA VI</span>'
                '<h1>' + escape(title) + '</h1><p>' + escape(description) + '</p>'
                '<p class="ma-tag-total">' + str(len(selected)) + (' articoli' if len(selected) != 1 else ' articolo') + '</p></section>')
        body += _render_controls(selected)
        body += '<section class="ed-home" data-tag-archive data-tag-id="' + escape(tag_id, quote=True) + '"><div class="archive-grid" data-tag-grid>'
        body += "".join(_card(item, url_fn, card_fn) for item in selected)
        body += '</div><nav class="archive-pagination" data-tag-pager hidden aria-label="Pagine degli articoli"></nav></section>'
        js_path = Path("site/assets/article-tags-v1.js")
        digest = hashlib.sha256(js_path.read_bytes()).hexdigest()[:12] if js_path.is_file() else "v1"
        body += '<script src="' + escape(url_fn("assets/article-tags-v1.js") + "?v=" + digest, quote=True) + '" defer></script>'
        schema = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title,
                  "description": description, "url": url_fn(path), "inLanguage": "it-IT",
                  "numberOfItems": len(selected),
                  "mainEntity": {"@type": "ItemList", "numberOfItems": len(selected),
                                 "itemListElement": [{"@type": "ListItem", "position": index, "url": url_fn(item["path"])}
                                                     for index, item in enumerate(selected, 1)]}}
        page = layout_fn(title, description, path, body, "articles",
                         robots="index,follow" if indexable else "noindex,follow", structured=schema)
        target = root / path / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")
        if indexable:
            node = ET.SubElement(sitemap_root, ns + "url")
            ET.SubElement(node, ns + "loc").text = url_fn(path)
            indexable_paths.append(path)
    tree.write(sitemap, encoding="utf-8", xml_declaration=True)
    print("MAGAZINE_TAG_ARCHIVES_BUILT", len(tag_items), "tags;", len(indexable_paths), "indexable")
    return indexable_paths
