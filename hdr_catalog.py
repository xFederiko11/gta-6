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


def _hdr_values(preset):
    return ('<div class="game-hdr-values">'
        + ''.join('<div><b>'+e(preset[key])+'</b><span>'+e(label)+'</span></div>'
                  for key, label in [
                      ("max_brightness", "Max Brightness"),
                      ("black_levels", "Black Levels"),
                      ("paper_white", "Paper White")])
        + '</div>')


def render(write, layout, schema_article, url, crumbs):
    """Write searchable group index and one detail page per panel family.

    SEO titles contain a family name; model codes and diagonal values are
    readable text on the page. Grouping avoids doorway pages with identical
    settings for every size.
    """
    catalog = json.loads(Path("data/hdr_oled.json").read_text(encoding="utf-8"))
    families = catalog["families"]
    game_hdr = catalog["game_hdr"]
    reports = game_hdr["reports"]
    defaults = game_hdr["default"]
    assert set(reports).issubset({f["slug"] for f in families})
    assert len({f["slug"] for f in families}) == len(families)
    assert len({m["code"] for f in families for m in f["models"]}) == sum(
        len(f["models"]) for f in families)
    total = sum(len(f["models"]) for f in families)
    index_path = "hdr-oled/"
    groups = Counter(f["brand"] for f in families)

    intro = (crumbs([("HDR OLED", index_path)])
        + '<section class="page-intro"><span class="eyebrow">📺 GTA VI · PS5 e PS5 Pro</span>'
        + '<h1>GTA 6: <span class="highlight">valori HDR nel gioco per ogni OLED</span></h1>'
        + '<p class="lead">Impostazioni HDR per GTA VI su PS5 e PS5 Pro: '
        + 'LG, Samsung, Sony, Philips e Panasonic. Cerca il codice completo del televisore, '
        + 'la diagonale in pollici o la serie. Menu verificabili e calibrazione prudente, '
        + 'senza valori universali inventati.</p>'
        + f'<div class="statline"><span>📺 <b>{total}</b> codici TV</span>'
        + f'<span><b>{len(families)}</b> famiglie di impostazioni</span>'
        + f'<span><b>{len(groups)}</b> produttori</span></div></section>'
        + '<div class="guide-hero-actions"><a class="button" href="#trova-tv">🔎 Trova la tua TV</a>'
        '<a class="button secondary" href="#valori-gioco">🎮 Valori nel gioco</a></div>'
        + '<div class="info">🧪 <strong>Come leggere i numeri:</strong> i valori di GTA VI '
        + 'pubblicati dalla community sono prove individuali, non misure certificate. '
        + 'Per le altre TV mostriamo i valori iniziali del gioco, da calibrare, senza '
        + 'spacciarli per preset ottimizzati.</div>')

    steps = "<ol class=\"hdr-steps\">" + "".join(
        "<li>" + e(step) + "</li>" for step in catalog["ps5_steps"]) + "</ol>"
    filters = ('<div class="filters" role="group" aria-label="Filtra per produttore">'
        + f'<button type="button" data-hdr-brand-filter="all" aria-pressed="true">Tutti · {total}</button>'
        + ''.join(
            f'<button type="button" data-hdr-brand-filter="{e(brand.casefold())}" aria-pressed="false">'
            f'{e(brand)} · {sum(len(f["models"]) for f in families if f["brand"] == brand)}</button>'
            for brand in sorted(groups)
        ) + '</div>')
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
            f'<article class="hdr-family" data-hdr-brand="{e(family["brand"].casefold())}" data-hdr-search="{e(terms.casefold())}">'
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
 const brandButtons=Array.from(document.querySelectorAll("[data-hdr-brand-filter]"));
 let brand="all";
 if(!input || !counter)return;
 function render(){
   const q=input.value.trim().toLocaleLowerCase("it-IT");
   let count=0;
   cards.forEach(card=>{
     const match=(!q || card.dataset.hdrSearch.includes(q)) &&
       (brand==="all" || card.dataset.hdrBrand===brand);
     card.hidden=!match;
     if(match)count++;
   });
   counter.textContent=count ? count+" famiglie compatibili visualizzate" :
       "Nessun modello trovato: controlla il codice o seleziona Tutti.";
 }
 input.addEventListener("input",render);
 brandButtons.forEach(btn=>btn.addEventListener("click",()=>{
   brand=btn.dataset.hdrBrandFilter;
   brandButtons.forEach(b=>b.setAttribute("aria-pressed",String(b===btn)));
   render();
 }));
 render();
})();
</script>"""
    report_cards = []
    for family in families:
        preset = reports.get(family["slug"])
        if not preset:
            continue
        address = url(index_path + family["slug"] + "/")
        report_cards.append(
            '<article class="hdr-family">'
            f'<span class="card-label">{e(family["brand"])} · {e(family["series"])}</span>'
            + _hdr_values(preset)
            + f'<p>⚠️ {e(preset["note"])}</p>'
            + f'<a class="hdr-family-link" href="{address}">Valori e calibrazione nel gioco →</a>'
            + '</article>')
    in_game_index = (
        '<section class="section" id="valori-gioco"><span class="eyebrow">🎮 GTA VI · MENU HDR</span>'
        '<h2>Max Brightness, Black Levels e Paper White</h2>'
        '<p>Apri GTA VI → Pausa (Options) → Impostazioni → Schermo (Display) → '
        'Calibrazione HDR (HDR Calibration). Con R1 cambia immagine di prova e con '
        'Triangolo nascondi l’interfaccia, secondo le schermate di lancio PS5.</p>'
        + '<div class="hdr-list">' + ''.join(report_cards) + '</div>'
        + f'<p class="source">Testimonianze community del 18 novembre 2026: '
        f'<a href="{e(game_hdr["source_community"])}" target="_blank" rel="noopener noreferrer">Reddit OLED Gaming</a>. '
        'Nessuna delle tre configurazioni è una calibrazione strumentale certificata.</p>'
        + '<h3>E se la tua TV non compare tra i preset numerici?</h3>'
        + _hdr_values(defaults)
        + '<p>600 / 50 / 50 sono i valori di partenza osservati nel gioco, '
        'non una raccomandazione calibrata per tutti gli OLED. Imposta il massimo '
        'seguendo il logo che scompare; controlla che i neri non perdano dettaglio '
        'e regola Paper White per una luminosità confortevole dell’interfaccia. '
        'Evita di copiare i valori di una TV con pannello e luminosità differenti.</p>'
        + f'<p class="micro">Menu e valori iniziali: <a href="{e(game_hdr["source_menu"])}" '
        'target="_blank" rel="noopener noreferrer">schermate PS5 del 19 novembre</a>.</p>'
        + '</section>')
    title = "GTA 6 HDR: Max Brightness, Black Levels e Paper White per TV OLED"
    desc = (f"Valori HDR GTA VI nel gioco (Max Brightness, Black Levels, Paper White) per {total} codici OLED in "
            f"{len(families)} famiglie LG, Samsung, Sony, Philips e Panasonic. HGiG, Game HDR e calibrazione.")
    page = (intro + in_game_index + '<section class="section" id="trova-tv"><h2>Trova il modello OLED esatto</h2>' + form
            + filters + '<div class="hdr-list">' + "".join(blocks) + "</div>" + script + "</section>"
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
        preset = reports.get(family["slug"])
        shown = preset or defaults
        status = ("⚠️ Testimonianza community singola del 18/11/2026, non misurata."
                  if preset else "⚠️ Valori iniziali GTA VI; NON preset personalizzato per questa TV.")
        game_note = e(preset["note"]) if preset else (
            "Per questo modello non abbiamo ancora una misura HDR GTA VI verificata. "
            "Usa la calibrazione a logo e verifica nero, alte luci e Paper White.")
        game_panel = (
            '<h2 id="valori-hdr">1. GTA VI: impostazioni da inserire nel gioco</h2>'
            '<p>Su PS5/PS5 Pro: premi Options → Impostazioni → Schermo (Display) → '
            'Calibrazione HDR (HDR Calibration). Premi R1 per cambiare il test, '
            'Triangolo per nascondere le voci.</p>'
            + _hdr_values(shown)
            + f'<p class="micro">{status}</p><p>{game_note}</p>'
            + f'<p class="source">Fonte: <a href="{e(game_hdr["source_community"] if preset else game_hdr["source_menu"])}" '
            'target="_blank" rel="noopener noreferrer">valori e menu di GTA VI</a>.</p>')
        related_families=[other for other in families if other["slug"]!=family["slug"] and other["brand"]==family["brand"]][:3]
        related_cards="".join(
            f'<a class="discovery-card" href="{url(index_path+other["slug"]+"/")}">'
            f'<span class="discovery-label">📺 {e(other["brand"])} · {e(other["year"])}</span>'
            f'<strong>{e(other["series"])}</strong><span>{len(other["models"])} codici · Apri impostazioni →</span></a>'
            for other in related_families)
        detail = (
            crumbs([("HDR OLED", index_path), (family["series"], path)])
            + f'<section class="page-intro"><span class="eyebrow">📺 {e(family["brand"])}'
            f' · {e(family["year"])} · PS5 / PS5 Pro</span>'
            f'<h1>GTA 6 HDR su {e(family["series"])}: '
            '<span class="highlight">impostazioni OLED</span></h1>'
            f'<p class="lead">{e(family["summary"])}</p>'
            f'<div class="statline"><span>📺 <b>{len(family["models"])}</b> modelli</span>'
            f'<span>{e(family["group"])}</span><span>🎮 PS5 + PS5 Pro</span></div>'
            '<div class="guide-hero-actions"><a class="button" href="#valori-hdr">🎮 Valori GTA VI</a>'
            '<a class="button secondary" href="#modelli-tv">📺 Codici compatibili</a></div></section>'
            '<div class="article-grid"><article class="prose">'
            + game_panel
            + '<h2 id="modelli-tv">Modelli e diagonali compatibili con questa procedura</h2>'
            '<div class="hdr-table-scroll"><table class="hdr-table"><thead><tr>'
            '<th>Codice modello TV</th><th>Pollici</th><th>Famiglia</th>'
            '</tr></thead><tbody>'+model_rows+'</tbody></table></div>'
            '<p class="micro">Una procedura comune non implica luminosità massima identica '
            'per tutte le dimensioni dello schermo.</p>'
            '<h2>2. Configura il televisore</h2>'+tv_steps
            + '<h2>3. Configura PS5 / PS5 Pro</h2>'+steps
            + f'<div class="info warn">⚠️ <strong>Attenzione:</strong> {e(family["caution"])}</div>'
            '<h2>4. Verifica la resa in GTA VI</h2>'
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
            + ('<section class="section discover-more"><div class="section-head"><div>'
               '<span class="eyebrow">STESSO PRODUTTORE · ALTRE FAMIGLIE</span>'
               '<h2>Confronta altri OLED</h2></div></div>'
               '<div class="discovery-rail">'+related_cards+'</div></section>'
               if related_cards else '')
        )
        dtitle = f"GTA 6 HDR {family['brand']} {family['series']}: valori Max Brightness e Paper White"
        ddesc = f"Valori HDR dentro GTA VI per {family['brand']} {family['series']} su PS5/PS5 Pro. " \
                + f"Codici TV: {model_list}. HGiG, Game Mode e calibrazione."
        write(path + "index.html", layout(dtitle, ddesc[:310], path, detail,
                                         "hdr", structured=schema_article(dtitle, ddesc, url(path))))
    return paths
