"""Source-attributed GTA VI cheat hub; accessible PS5 D-pad visual sequences."""
from __future__ import annotations

from collections import Counter
from html import escape
import json
from pathlib import Path

ARROWS = {"↑": ("Su", "up"), "↓": ("Giù", "down"), "←": ("Sinistra", "left"), "→": ("Destra", "right")}
BASE = "trucchi/"


def e(value):
    return escape(str(value), quote=True)


def keycap(token):
    name, direction = ARROWS[token]
    return f'<kbd class="ps5-dpad dir-{direction}" aria-label="Croce direzionale {name}" title="{name}">{token}</kbd>'


def sequence_view(tokens, *, include_preamble=False):
    buttons = "".join(keycap(token) for token in tokens)
    if include_preamble:
        return ('<div class="cheat-sequence"><span class="sequence-preamble">'
                '<kbd class="ps5-dpad dir-up" aria-label="Croce su per aprire il telefono">↑</kbd>'
                '<span class="sequence-note">Telefono</span><span class="sequence-divider">›</span>'
                '<kbd class="ps5-trigger">L1</kbd><span>+</span><kbd class="ps5-trigger">R1</kbd>'
                '<span class="sequence-divider">›</span></span><span class="sequence-buttons">'
                + buttons + '</span></div>')
    return '<div class="cheat-sequence"><span class="sequence-buttons">' + buttons + '</span></div>'


def render(write, layout, schema_article, url, crumbs):
    data=json.loads(Path("data/trucchi.json").read_text(encoding="utf-8"))
    cheats=data["cheats"]
    assert all(cheat["sequence"] and all(x in ARROWS for x in cheat["sequence"]) for cheat in cheats)
    assert len({x["slug"] for x in cheats})==len(cheats)
    groups=Counter(x["category"] for x in cheats)
    comparison=data["research_summary"]
    assert sum(x["independent_source_count"] == 2 for x in cheats) == comparison["independently_matched"]
    intro=(
        crumbs([("Trucchi PS5",BASE)])
        + '<section class="page-intro"><span class="eyebrow">🎮 GTA VI · PS5 / PS5 Pro</span>'
        + '<h1>Trucchi GTA 6: <span class="highlight">codici e pulsanti DualSense</span></h1>'
        + '<p class="lead">Sequenze direzionali dei trucchi GTA VI, con icone dei tasti PlayStation, '
        + 'effetti, requisiti e fonti. Non sono le combinazioni di GTA V.</p>'
        + f'<div class="statline"><span><b>{len(cheats)}</b> sequenze pubblicate</span>'
        + f'<span><b>{data["total_reported"]}</b> effetti segnalati</span>'
        + '<span>🎮 PS5 e PS5 Pro</span></div></section>')
    warning=(
        '<div class="info warn"><strong>🏆 Attenzione ai trofei e al platino:</strong> '
        'completare prima la storia e la sfida richiesta. Usare trucchi disabilita '
        'salvataggi e trofei durante la sessione. Prima di provarli, crea un salvataggio '
        'manuale separato; torna al tuo salvataggio pulito per il platino. '
        'Le sequenze sono riportate da fonti esterne, non testate personalmente da questo sito.</div>')
    how=(
        '<section class="section"><h2>Come inserire i codici PS5</h2>'
        '<ol class="hdr-steps"><li>Completa la storia: la scheda Progressi → Trucchi '
        'diventa disponibile soltanto dopo il finale. Sblocca la sfida del trucco scelto.</li>'
        '<li>Nel gioco libero premi la croce direzionale SU (↑) per aprire il telefono.</li>'
        '<li>Tieni premuto L1 e premi R1, poi inserisci le frecce indicate in sequenza. '
        'I simboli rappresentano i quattro pulsanti della croce direzionale, non gli analogici.</li>'
        '<li>Se un trucco non si attiva, verifica che sia sbloccato e ripeti dall’inizio. '
        'Non usare i trucchi nella partita con cui vuoi ottenere trofei o salvare progressi.</li>'
        '</ol></section>')
    rows=[]
    for x in cheats:
        terms=" ".join((x["title"],x["category"],x["effect"],x["unlock"])).lower()
        rows.append(
            f'<article class="cheat-card" data-cheat-search="{e(terms)}" data-cheat-category="{e(x["category"])}">'
            f'<span class="card-label">{e(x["category"])} · PS5</span>'
            f'<h3><a href="{url(BASE+x["slug"]+"/")}">{e(x["title"])}</a></h3>'
            f'<p>{e(x["effect"])}</p>'
            +sequence_view(x["sequence"])
            +f'<p class="micro">Sblocco: {e(x["unlock"])}</p>'
            +f'<p class="micro">{e(x["status"])}</p>'
            +f'<a class="hdr-family-link" href="{url(BASE+x["slug"]+"/")}">Procedura e fonte →</a></article>')
    category_options=''.join(
        f'<button type="button" data-cheat-category-filter="{e(k)}" aria-pressed="false">{e(k)} · {n}</button>'
        for k,n in sorted(groups.items()))
    script=r"""<script>
(function(){
const search=document.getElementById("cheat-search");
const result=document.getElementById("cheat-results");
const cards=[...document.querySelectorAll("[data-cheat-search]")];
const filters=[...document.querySelectorAll("[data-cheat-category-filter]")];
if(!search||!result)return;
let category="all";
function paint(){
 const q=search.value.trim().toLocaleLowerCase("it-IT");
 let visible=0;
 for(const card of cards){
  const ok=(!q||card.dataset.cheatSearch.includes(q))&&(category==="all"||category===card.dataset.cheatCategory);
  card.hidden=!ok;if(ok)visible++;
 }
 result.textContent=visible+" trucchi con sequenza visualizzati";
}
search.addEventListener("input",paint);
for(const btn of filters)btn.addEventListener("click",()=>{
 category=btn.dataset.cheatCategoryFilter;
 for(const b of filters)b.setAttribute("aria-pressed",String(b===btn));
 paint();
});
paint();
})();
</script>"""
    finder=(
        '<section class="section"><h2>Trova un trucco GTA VI</h2>'
        '<label for="cheat-search" class="micro">Cerca soldi, armi, veicoli, effetti o requisiti</label>'
        '<div><input class="search" type="search" id="cheat-search" placeholder="Es. 250.000, munizioni, meteo" autocomplete="off"></div>'
        '<div class="filters" role="group" aria-label="Filtra trucchi per categoria">'
        '<button type="button" data-cheat-category-filter="all" aria-pressed="true">Tutti</button>'
        +category_options+'</div>'
        '<p id="cheat-results" role="status" aria-live="polite" class="count"></p>'
        '<div class="cheat-grid">'+"".join(rows)+'</div>'+script+'</section>')
    links=(
        '<section class="section"><h2>Fonti e attendibilità</h2>'
        '<p>I codici disponibili sono quelli pubblicati dai siti consultati al 19 novembre 2026. '
        'Il numero di sequenze rese pubbliche può crescere; non inventiamo codici mancanti. '
        'Rockstar non ha fornito un elenco ufficiale completo in queste fonti. '
        +str(comparison["independently_matched"])+ ' sequenze coincidono tra PowerPyx e PC Gamer; '
        +str(comparison["single_origin"])+ ' al momento hanno un solo riscontro indipendente.</p>'
        '<p><a href="'+e(data["sources"]["powerpyx"])+'" rel="noopener noreferrer" target="_blank">PowerPyx — tutti i trucchi GTA VI</a>'
        ' · <a href="'+e(data["sources"]["pcgamer"])+'" rel="noopener noreferrer" target="_blank">PC Gamer — verifiche post-storia</a>'
        ' · <a href="'+e(data["sources"]["gtadb"])+'" rel="noopener noreferrer" target="_blank">GTADB — riepilogo terzo</a>.</p>'
        f'<p><a href="{url("fonti/")}">Come verifichiamo le fonti GTA VI e le notizie →</a></p></section>')
    title="Trucchi GTA 6 PS5: codici DualSense, soldi e veicoli"
    desc=f"Tutti i trucchi GTA 6 per PS5 e PS5 Pro: {len(cheats)} sequenze con icone dei tasti DualSense, sblocco, soldi, armi, veicoli e attenzione ai trofei."
    structured={"@context":"https://schema.org","@type":"CollectionPage",
        "name":title,"description":desc,"url":url(BASE),"inLanguage":"it-IT",
        "mainEntity":{"@type":"ItemList","itemListElement":[
            {"@type":"ListItem","position":i+1,"name":x["title"],"url":url(BASE+x["slug"]+"/")}
            for i,x in enumerate(cheats)]}}
    write(BASE+"index.html",layout(title,desc,BASE,intro+warning+how+finder+links,"cheats",structured=structured))
    paths=[BASE]
    for x in cheats:
        p=BASE+x["slug"]+"/"
        # Preserve the full cheat name and PS5 intent; instructions and the
        # trophy-breaking warning remain in the visible article, not its title.
        title=f"GTA 6 trucco {x['title']}: codice PS5"
        if len(title)>60:
            raise ValueError("Cheat search title exceeds 60 characters: "+x["slug"])
        desc=f"GTA VI PS5: trucco {x['title']}, sequenza croce direzionale, come sbloccarlo ed effetto. Attenzione: disabilita trofei e salvataggi."
        steps=(
            '<ol class="hdr-steps"><li>Completa la storia di GTA VI.</li>'
            f'<li>Verifica il requisito del trucco: {e(x["unlock"])}.</li>'
            '<li>In esplorazione libera premi ↑ per aprire il telefono. Tieni L1 e premi R1.</li>'
            '<li>Inserisci tutti i pulsanti della sequenza qui sotto nell’ordine indicato.</li>'
            '<li>Se il codice fallisce, verifica che risulti sbloccato in Progressi → Trucchi e ricomincia.</li></ol>')
        related=[item for item in cheats if item["category"]==x["category"] and item["slug"]!=x["slug"]][:3]
        related_cards="".join(
            f'<a class="discovery-card" href="{url(BASE+item["slug"]+"/")}">'
            f'<span class="discovery-label">🎮 {e(item["category"])}</span>'
            f'<strong>{e(item["title"])}</strong><span>Visualizza la sequenza →</span></a>'
            for item in related)
        if not related_cards:
            related_cards=(f'<a class="discovery-card" href="{url(BASE)}">'
                '<span class="discovery-label">🎮 CATALOGO PS5</span>'
                '<strong>Esplora tutte le sequenze documentate</strong>'
                '<span>Vai ai trucchi →</span></a>')
        copy_value="↑ · L1 + R1 · "+" ".join(x["sequence"])
        source_links="".join(
            '<li><a href="'+e(link)+'" target="_blank" rel="noopener noreferrer">'
            +e(link.split("/")[2])+' — fonte esterna</a></li>'
            for link in x["sources"])
        detail=(
            crumbs([("Trucchi PS5",BASE),(x["title"],p)])
            +f'<section class="page-intro"><span class="eyebrow">🎮 GTA VI · {e(x["category"])} · PS5</span>'
            f'<h1>{e(x["title"])}: <span class="highlight">codice e sequenza</span></h1>'
            f'<p class="lead">{e(x["effect"])}. Procedura per DualSense, PS5 e PS5 Pro.</p>'
            '<div class="guide-hero-actions">'
            '<a class="button" href="#codice">🎮 Vai alla sequenza</a>'
            '<a class="button secondary" href="#fonti-codice">🔎 Controlla le fonti</a>'
            '</div></section>'
            +warning
            +'<div class="article-grid"><article class="prose">'
            +'<section class="cheat-code-panel" id="codice">'
            +'<span class="eyebrow">DUALSENSE · SEQUENZA DIREZIONALE</span>'
            +'<h2>Codice completo sul controller PS5</h2>'
            +sequence_view(x["sequence"],include_preamble=True)
            +'<p class="micro">Prima ↑ per il telefono, poi L1 + R1 e infine soltanto le frecce evidenziate.</p>'
            +f'<div class="cheat-panel-footer"><button type="button" class="guide-copy" '
            f'data-copy-sequence="{e(copy_value)}">📋 Copia la sequenza</button>'
            '<span data-cheat-feedback role="status" aria-live="polite">Usa i pulsanti PS5 direttamente nel gioco, non incollare testo.</span></div></section>'
            +'<h2>Come attivare questo trucco, passo passo</h2>'+steps
            +f'<h2>Risultato e requisito</h2><p>{e(x["effect"])}</p>'
            +f'<p><strong>Requisito:</strong> {e(x["unlock"])}</p>'
            +f'<p><strong>Stato verifica:</strong> {e(x["status"])}.</p>'
            +f'<p><strong>Confronto delle fonti:</strong> {e(x["source_note"])}</p>'
            + (f'<div class="info warn">{e(x["unlock_note"])}</div>' if x.get("unlock_note") else "")
            +'<h2 id="fonti-codice">Fonti del codice</h2><ol>'+source_links+'</ol>'
            +'</article><aside class="sidebox"><h3>Altre guide</h3>'
            +f'<a href="{url(BASE)}">← Tutti i trucchi</a>'
            +f'<a href="{url("trofei/")}">🏆 Percorso platino</a>'
            +f'<a href="{url("guide-e-tutorial/")}">⚡ Guide PS5</a>'
            +f'<a href="{url("fonti/")}">🔎 Metodo e fonti</a>'
            +'</aside></div>'
            +'<section class="section discover-more"><div class="section-head"><div>'
            '<span class="eyebrow">ALTRE SEQUENZE DOCUMENTATE</span><h2>Scopri i trucchi correlati</h2>'
            '</div></div><div class="discovery-rail">'+related_cards+'</div></section>'
            +f'<script src="{url("assets/cheat-interactions.js")}" defer></script>')
        write(p+"index.html",layout(title,desc,p,detail,"cheats",structured=schema_article(title,desc,url(p))))
        paths.append(p)
    return paths
