"""OLED HDR guides for PS5 / PS5 Pro. Source-driven; no invented GTA VI nits."""
from __future__ import annotations

from collections import Counter
from html import escape as _esc
import json
from pathlib import Path


def e(value):
    return _esc(str(value), quote=True)


def _badge_models(family):
    return " · ".join(f'<span class="hdr-code">{e(m["code"])} <small>{m["size"]}″</small></span>'
                     for m in family["models"])


def _source_links(family, ps5_source):
    links = [ps5_source] + family["sources"]
    unique = list(dict.fromkeys(links))
    return "<ol>" + "".join(
        f'<li><a href="{e(address)}" target="_blank" rel="noopener noreferrer">'
        f'{e(address.split("/")[2])} · fonte {index + 1}</a></li>'
        for index, address in enumerate(unique)) + "</ol>"


def render(write, layout, schema_article, url, crumbs):
    """Write searchable group index and one detail page per panel family.

    SEO titles contain a family name; model codes and diagonal values are
    readable text on the page. Grouping avoids doorway pages with identical
    settings for every size.
    """
    catalog = json.loads(Path("data/hdr_oled.json").read_text(encoding="utf-8"))
    families = catalog["families"]
    assert len({f["slug"] for f in families}) == len(families)
    assert len({m["code"] for f in families for m in f["models"]}) == sum(
        len(f["models"]) for f in families)
    total = sum(len(f["models"]) for f in families)
    index_path = "hdr-oled/"
    groups = Counter(f["brand"] for f in families)

    intro = (crumbs([("HDR OLED", index_path)])
        + '<section class="page-intro"><span class="eyebrow">📺 GTA VI · PS5 e PS5 Pro</span>'
        + '<h1>GTA 6 HDR OLED: <span class="highlight">trova la tua TV</span></h1>'
        + '<p class="lead">Impostazioni HDR per GTA VI su PS5 e PS5 Pro: '
        + 'LG, Samsung, Sony, Philips e Panasonic. Cerca il codice completo del televisore, '
        + 'la diagonale in pollici o la serie. Menu verificabili e calibrazione prudente, '
        + 'senza valori universali inventati.</p>'
        + f'<div class="statline"><span>📺 <b>{total}</b> codici TV</span>'
        + f'<span><b>{len(families)}</b> famiglie di impostazioni</span>'
        + f'<span><b>{len(groups)}</b> produttori</span></div></section>'
        + '<div class="info">🧪 <strong>Trasparenza:</strong> le opzioni PS5 sono documentate da Sony, '
        + 'mentre i controlli dei TV derivano dalle fonti dei produttori. '
        + 'Non pubblichiamo presunti valori numerici «migliori per GTA VI» '
        + 'senza misure ripetibili e dettagli di patch/firmware.</div>')

    steps = "<ol class=\"hdr-steps\">" + "".join(
        "<li>" + e(step) + "</li>" for step in catalog["ps5_steps"]) + "</ol>"
    form = ('<label for="hdr-ricerca" class="micro">Trova la tua TV: codice, '
            'brand, serie o pollici</label><br>'
            '<input id="hdr-ricerca" type="search" class="search" '
            'placeholder="Es. OLED65C54LA, S95F, 77, Sony" autocomplete="off">'
            '<p class="count" id="hdr-risultati" aria-live="polite"></p>')
    blocks = []
    for family in families:
        path = index_path + family["slug"] + "/"
        terms = " ".join([family["brand"], family["series"], family["group"]]
                         + [m["code"] + " " + str(m["size"]) for m in family["models"]])
        blocks.append(
            f'<article class="hdr-family" data-hdr-search="{e(terms.casefold())}">'
            f'<div class="hdr-family-head"><div><span class="card-label">{e(family["brand"])} · {e(family["year"])}</span>'
            f'<h3><a href="{url(path)}">{e(family["series"])} ↗</a></h3>'
            f'<p>{e(family["summary"])}</p></div><span class="hdr-family-count">{len(family["models"])} tagli</span></div>'
            f'<div class="hdr-models">{_badge_models(family)}</div>'
            f'<a class="hdr-family-link" href="{url(path)}">Apri configurazione e istruzioni →</a>'
            "</article>"
        )
    script = r"""<script>
(function(){
 const input=document.getElementById("hdr-ricerca");
 const cards=Array.from(document.querySelectorAll("[data-hdr-search]"));
 const counter=document.getElementById("hdr-risultati");
 if(!input || !counter)return;
 function render(){
   const q=input.value.trim().toLocaleLowerCase("it-IT");
   let count=0;
   cards.forEach(card=>{
     const match=!q || card.dataset.hdrSearch.includes(q);
     card.hidden=!match;
     if(match)count++;
   });
   counter.textContent=count+" famiglie compatibili visualizzate";
 }
 input.addEventListener("input",render);
 render();
})();
</script>"""
    title = "GTA 6 HDR OLED PS5 Pro: impostazioni per LG, Samsung, Sony e altre TV"
    desc = (f"Guida HDR GTA VI PS5 e PS5 Pro: cerca tra {total} codici OLED in "
            "8 famiglie LG, Samsung, Sony, Philips e Panasonic. HGiG, Game HDR e calibrazione.")
    page = (intro + '<section class="section"><h2>Trova il modello OLED esatto</h2>' + form
            + '<div class="hdr-list">' + "".join(blocks) + "</div>" + script + "</section>"
            + '<section class="section"><span class="eyebrow">🎮 Consoles</span>'
            + '<h2>Configurazione HDR di base su PS5 e PS5 Pro</h2>' + steps
            + f'<p class="source">Procedura PlayStation: <a href="{e(catalog["ps5_source"])}" '
            'target="_blank" rel="noopener noreferrer">supporto ufficiale Sony (HDR PS5)</a>.</p>'
            + '</section><section class="section"><h2>Domande frequenti</h2>'
            + '<div class="hdr-faq"><h3>Esiste un valore unico di luminosità HDR per ogni OLED?</h3>'
            + '<p>No. Dimensione, pannello, firmware, tone mapping e luce ambiente possono '
            + 'modificare la resa. Per questo non consigliamo numeri di click o nit universali.</p>'
            + '<h3>Con PS5 è meglio HGiG o Dynamic Tone Mapping?</h3>'
            + '<p>HGiG, quando supportato, è un punto di partenza ragionevole per una calibrazione '
            + 'coerente. Il mapping dinamico può piacere di più in una stanza luminosa, '
            + 'ma altera intenzionalmente la resa rispetto alla calibrazione di base.</p>'
            + '<h3>Devo usare Dolby Vision Gaming su PS5?</h3>'
            + '<p>Questa guida calibra il segnale HDR compatibile con PS5. '
            + 'Non dare per scontato che un menu Dolby Vision del TV significhi '
            + 'Dolby Vision Gaming disponibile sulla console.</p></div></section>')
    structured = {"@context": "https://schema.org", "@type": "CollectionPage",
        "name": title, "description": desc, "inLanguage": "it-IT",
        "url": url(index_path), "numberOfItems": len(families),
        "mainEntity": {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i+1,
             "name": f["brand"]+" "+f["series"], "url":url(index_path+f["slug"]+"/")}
            for i,f in enumerate(families)]}}
    write("hdr-oled/index.html", layout(title, desc, index_path, page,
                                      "hdr", structured=structured))
    paths = [index_path]
    for family in families:
        path = index_path + family["slug"] + "/"
        paths.append(path)
        model_rows = "".join(
            '<tr><td><strong>'+e(m["code"])+'</strong></td><td>'+str(m["size"])
            +'″</td><td>'+e(family["series"])+'</td></tr>' for m in family["models"]
        )
        model_list = ', '.join(m["code"] for m in family["models"])
        tv_steps = "<ol class=\"hdr-steps\">" + "".join(
            "<li>"+e(step)+"</li>" for step in family["settings"]) + "</ol>"
        detail = (
            crumbs([("HDR OLED", index_path), (family["series"], path)])
            + f'<section class="page-intro"><span class="eyebrow">📺 {e(family["brand"])}'
            f' · {e(family["year"])} · PS5 / PS5 Pro</span>'
            f'<h1>GTA 6 HDR su {e(family["series"])}: '
            '<span class="highlight">impostazioni OLED</span></h1>'
            f'<p class="lead">{e(family["summary"])}</p>'
            f'<div class="statline"><span>📺 <b>{len(family["models"])}</b> modelli</span>'
            f'<span>{e(family["group"])}</span><span>🎮 PS5 + PS5 Pro</span></div></section>'
            '<div class="article-grid"><article class="prose">'
            '<h2>Modelli e diagonali compatibili con questa procedura</h2>'
            '<div class="hdr-table-scroll"><table class="hdr-table"><thead><tr>'
            '<th>Codice modello TV</th><th>Pollici</th><th>Famiglia</th>'
            '</tr></thead><tbody>'+model_rows+'</tbody></table></div>'
            '<p class="micro">Una procedura comune non implica luminosità massima identica '
            'per tutte le dimensioni dello schermo.</p>'
            '<h2>1. Configura il televisore</h2>'+tv_steps
            + '<h2>2. Configura PS5 / PS5 Pro</h2>'+steps
            + f'<div class="info warn">⚠️ <strong>Attenzione:</strong> {e(family["caution"])}</div>'
            '<h2>3. Verifica la resa in GTA VI</h2>'
            '<p>Confronta un cielo luminoso, riflessi sulle carrozzerie e una scena '
            'notturna. Se il gioco propone regolazioni HDR proprie, controlla '
            'soprattutto luci bruciate e ombre troppo chiuse. Non attribuire al gioco '
            'parametri o scale non verificati nella versione installata.</p>'
            '<h2>Fonti per modello e impostazioni</h2>'+_source_links(family,catalog["ps5_source"])
            + '<p class="source">Contenuto editoriale indipendente, non affiliato a '
            'Rockstar Games o ai produttori. Non è una misurazione strumentale '
            'di GTA VI su ogni codice TV.</p></article>'
            '<aside class="sidebox"><h3>Ricerca rapida</h3>'
            f'<a href="{url(index_path)}">← Tutti i TV OLED</a>'
            f'<a href="{url("guide-e-tutorial/")}">⚡ Altre guide</a>'
            f'<a href="{url("trofei/")}">🏆 Trofei e platino</a>'
            f'<p class="micro">Codici trattati:<br>{e(model_list)}</p></aside></div>'
        )
        dtitle = f"GTA 6 HDR {family['brand']} {family['series']}: PS5 Pro, modelli e settaggi"
        ddesc = f"Impostazioni HDR GTA VI su {family['brand']} {family['series']} per PS5/PS5 Pro. " \
                + f"Codici TV: {model_list}. HGiG, Game Mode e calibrazione."
        write(path + "index.html", layout(dtitle, ddesc[:310], path, detail,
                                         "hdr", structured=schema_article(dtitle, ddesc, url(path))))
    return paths
