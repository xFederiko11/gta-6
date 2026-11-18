#!/usr/bin/env python3
"""Static Italian GTA VI portal: homepage, 55 trophies, guides, SEO metadata.
Public GitHub Pages only. No API keys, scraping, database or paid features.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import html
import json
import os
import re
import shutil
import xml.etree.ElementTree as ET
from site_info import SOCIAL_URL, SOCIAL_HANDLE, iso_modified, page_meta
from hdr_catalog import render as render_hdr_pages

BASE = "https://xfederiko11.github.io/gta-6"
OUT = Path(os.getenv("SITE_OUT", "_site"))
DATA = Path("data")
SITE = Path("site")
TODAY = datetime.now(timezone.utc)
TROPHY_SOURCE = "https://www.powerpyx.com/gta-6-grand-theft-auto-vi-trophy-guide-roadmap/"
LIST_SOURCE = "https://www.planetgta6.com/it/trofei-gta-6/"

def e(x): return html.escape(str(x if x is not None else ""), quote=True)
def write(path, body):
    p = OUT/path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
def url(path=""):
    return BASE + "/" + path
def clean(s):
    return re.sub(r"[^a-z0-9-]+", "-", str(s).lower()).strip("-")
def trophy_path(t):
    return "trofei/" + t["slug"] + "/"
def guide_path(g):
    return "guide-e-tutorial/" + g["id"] + "/"
def news_meta(title, desc, canonical, img=None, kind="website", robots="index,follow", structured=None, modified=None):
    payload = json.dumps(structured, ensure_ascii=False, separators=(",",":")).replace("</","<\\/") if structured else None
    out = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f'<title>{e(title)}</title>',
        f'<meta name="description" content="{e(desc)}">',
        f'<meta name="robots" content="{e(robots)}">',
        f'<link rel="canonical" href="{e(canonical)}">',
        '<meta name="theme-color" content="#080b16">',
        '<meta property="og:locale" content="it_IT">',
        f'<meta property="og:type" content="{e(kind)}">',
        '<meta property="og:site_name" content="GTA 6 Italia · Guide e trofei">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:url" content="{e(canonical)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:site" content="{SOCIAL_HANDLE}">',
        f'<link rel="me" href="{SOCIAL_URL}">',
        f'<meta name="twitter:title" content="{e(title)}">',
        f'<link rel="stylesheet" href="{url("assets/style.css")}">'
    ]
    if modified:
        out.append(f'<meta property="article:modified_time" content="{e(modified)}">')
    if img:
        out.extend([f'<meta property="og:image" content="{e(img)}">',
                    f'<meta name="twitter:image" content="{e(img)}">'])
    if payload:
        out.append('<script type="application/ld+json">' + payload + '</script>')
    return "\n".join(out)

def schema_article(title, desc, canonical, image=None):
    v={"@context":"https://schema.org","@type":"Article",
       "headline":title,"description":desc,"inLanguage":"it-IT","url":canonical,
       "mainEntityOfPage":canonical,
       "isPartOf":{"@type":"WebSite","name":"GTA 6 Italia","url":url()}}
    path=canonical.removeprefix(BASE + "/")
    v["dateModified"]=iso_modified(path)
    v["author"]={"@type":"Organization","name":"GTA 6 Italia","url":url()}
    if image: v["image"] = image
    return v

def layout(title, desc, path, body, section=None, image=None, robots="index,follow", structured=None):
    canonical=url(path)
    nav=[("Home","",section=="home"),("Trofei","trofei/",section=="trofei"),
         ("Guide e tutorial","guide-e-tutorial/",section=="guide"),
         ("HDR OLED","hdr-oled/",section=="hdr")]
    links="".join(f'<a href="{url(p)}"'+(' aria-current="page"' if selected else '')+f'>{e(n)}</a>' for n,p,selected in nav)
    modified=iso_modified(path)
    if structured:
        structured=dict(structured)
        structured["dateModified"]=modified
    meta=news_meta(title,desc,canonical,image,robots=robots,structured=structured,modified=modified)
    info=page_meta(canonical,path)
    return (f'<!doctype html><html lang="it"><head>{meta}</head><body>'
       '<a class="skip" href="#contenuto">Vai al contenuto</a>'
       '<header class="site-header"><div class="wrap header-inner">'
       f'<a class="brand" href="{url()}"><strong>GTA 6</strong> / ITALIA</a>'
       f'<nav class="mainnav" aria-label="Navigazione principale">{links}'
       f'<a class="nav-cta" href="{SOCIAL_URL}" target="_blank" rel="me noopener noreferrer" aria-label="Segui GTA 6 Italia su X">𝕏 Seguici</a></nav>'
       '</div></header><main class="wrap" id="contenuto">'+info+body+'</main>'
       '<footer class="footer"><div class="wrap footer-grid"><div>'
       '<strong>GTA 6 Italia</strong><p>Guide indipendenti in italiano per PS5 e PS5 Pro. '
       'Contenuti da verificare rispetto alle patch: non affiliato a Rockstar, Sony o PowerPyx.</p></div>'
       f'<div><a href="{url("trofei/")}">Trofei</a> · <a href="{url("guide-e-tutorial/")}">Guide e tutorial</a> · <a href="{url("hdr-oled/")}">HDR OLED</a>'
       f'<p class="footer-social"><a href="{SOCIAL_URL}" rel="me noopener noreferrer" target="_blank">𝕏 Aggiornamenti su {SOCIAL_HANDLE} ↗</a></p></div>'
       '</div></footer></body></html>')

def crumbs(parts):
    b=[f'<a href="{url()}">GTA 6 Italia</a>']
    for label, href in parts[:-1]: b.append(f'<a href="{url(href)}">{e(label)}</a>')
    b.append(e(parts[-1][0]))
    return '<nav class="breadcrumbs" aria-label="Percorso">'+' <span aria-hidden="true">/</span> '.join(b)+'</nav>'

def category_card(title, desc, href, tag, icon):
    return (f'<article class="card"><span class="card-label">{e(icon)} {e(tag)}</span>'
        f'<h3><a class="card-link" href="{url(href)}">{e(title)}</a></h3>'
        f'<p>{e(desc)}</p><div class="end">Esplora</div></article>')

def guide_card(g):
    return category_card(g["title"],g["summary"],guide_path(g),g["tag"],"🎮")

def trophy_card(t):
    desc=t["requirement_it"] if not t["hidden"] else "Trofeo nascosto: attenzione agli spoiler."
    return f'<article class="index-item" data-tier="{e(t["tier"].lower())}" data-search="{e((t["name_it"]+" "+desc).lower())}"><span class="card-label {e(t["tier"].lower())}">{e(t["tier"])}</span><h3><a href="{url(trophy_path(t))}">{e(t["name_it"])}</a></h3><p>{e(desc)}</p></article>'

def list_search():
    return '''
<label for="trofei-cerca" class="micro">Cerca un trofeo per nome o requisito</label>
<div><input class="search" type="search" id="trofei-cerca" placeholder="Es. Oro, collezionabili, 100%…"></div>
<div class="filters" aria-label="Filtra per rarità">
<button type="button" aria-pressed="true" data-filter="tutti">Tutti</button>
<button type="button" aria-pressed="false" data-filter="platino">💎 Platino</button>
<button type="button" aria-pressed="false" data-filter="oro">🥇 Oro</button>
<button type="button" aria-pressed="false" data-filter="argento">🥈 Argento</button>
<button type="button" aria-pressed="false" data-filter="bronzo">🥉 Bronzo</button>
</div>
<p id="results-count" class="count" role="status" aria-live="polite"></p>
<script>
(function(){
 const input=document.getElementById("trofei-cerca");
 const buttons=Array.from(document.querySelectorAll("[data-filter]"));
 const cards=Array.from(document.querySelectorAll("[data-tier]"));
 let tier="tutti";
 function render(){
  const q=input.value.toLocaleLowerCase("it-IT").trim();
  let visible=0;
  cards.forEach(card=>{
   const okay=(tier==="tutti"||card.dataset.tier===tier) && (!q||card.dataset.search.includes(q));
   card.hidden=!okay;
   if(okay) visible++;
  });
  document.getElementById("results-count").textContent=visible+" trofei visualizzati";
 }
 input.addEventListener("input",render);
 buttons.forEach(btn=>btn.addEventListener("click",()=>{
  tier=btn.dataset.filter;
  buttons.forEach(b=>b.setAttribute("aria-pressed",String(b===btn)));
  render();
 }));
 render();
})();
</script>'''

def site_home(trophies, guides):
    hero = f'''<section class="hero">
    <span class="eyebrow">🎮 Il punto di riferimento in italiano</span>
    <h1>Tutto GTA 6.<br><span class="highlight">Zero tempo perso.</span></h1>
    <p class="lead">Trofei PS5, platino, guide pratiche e strategie per Grand Theft Auto VI.
    Risposte utili, percorsi chiari e fonti consultabili: dal consiglio rapido alla guida completa.</p>
    <div class="actions">
      <a class="button" href="{url("guide-e-tutorial/")}">🎮 Esplora le guide</a>
      <a class="button secondary" href="{url("trofei/")}">🏆 Tutti i trofei</a>
      <a class="button secondary" href="{SOCIAL_URL}" target="_blank" rel="me noopener noreferrer">𝕏 Novità live su X</a>
    </div>
    <div class="statline"><span><b>55</b> trofei PS5</span><span><b>{len(guides)}</b> guide pratiche</span><span>🇮🇹 Contenuti in italiano</span></div>
    </section>'''
    sections=f'''<section class="section"><div class="section-head"><div><span class="eyebrow">📚 Le sezioni</span>
    <h2>Da dove vuoi cominciare?</h2></div></div><div class="grid">
    {category_card("Trofei e platino","Elenco completo dei 55 trofei in italiano, requisiti Oro, consigli e spoiler protetti.","trofei/","55 TROFEI","🏆")}
    {category_card("Guide e tutorial","Tutorial rapidi, combinazioni dei pulsanti, collezionabili, strategie e approfondimenti.","guide-e-tutorial/","PASSO PASSO","⚡")}
    {category_card("HDR OLED per PS5 Pro","Seleziona marca, codice TV e diagonale per regolare HDR, HGiG e Game Mode senza preset inventati.","hdr-oled/","27 MODELLI TV","📺")}
    </div></section>'''
    guides_cards="".join(guide_card(g) for g in guides[:6])
    guides_section=f'''<section class="section"><div class="section-head"><div><span class="eyebrow">⚡ Tips & tricks</span><h2>Guide rapide che fanno risparmiare tempo</h2><p>Le istruzioni subito, gli approfondimenti quando servono.</p></div><a href="{url("guide-e-tutorial/")}">Tutte le guide ↗</a></div><div class="grid">{guides_cards}</div></section>'''
    call=f'''<section class="section feature"><div><span class="eyebrow">🏆 Obiettivo platino</span><h2>Un percorso, tutti i trofei.</h2>
    <p class="lead">Trofei mancabili, requisiti e sfide: una base consultabile prima di prendere decisioni irreversibili nella storia.</p>
    <a class="button secondary" href="{url("trofei/")}">Apri l'elenco trofei →</a></div><div class="decor" aria-hidden="true"></div></section>'''
    hdr_feature=f'''<section class="section hdr-promo"><div><span class="eyebrow">📺 Nuova guida OLED</span>
    <h2>HDR di GTA VI, su misura per la tua TV.</h2>
    <p>LG OLED C5 e G5, Samsung S90F e S95F, Sony BRAVIA, Philips e Panasonic:
    impostazioni raggruppate per famiglia, codici commerciali e dimensioni verificate.</p>
    <a class="button secondary" href="{url("hdr-oled/")}">Trova il tuo modello OLED →</a></div>
    <div class="hdr-promo-orb" aria-hidden="true">HDR<span>OLED</span></div></section>'''
    return hero+sections+hdr_feature+guides_section+call

def trophy_index(trophies):
    shown=[t for t in trophies if not t["hidden"]]
    hidden=[t for t in trophies if t["hidden"]]
    counts=Counter(t["tier"] for t in trophies)
    lead=crumbs([("Trofei","trofei/")])+f'''<div class="page-intro"><span class="eyebrow">🏆 Trofei PlayStation 5</span><h1>Tutti i 55 trofei<br><span class="highlight">GTA VI in italiano</span></h1>
    <p class="lead">Requisiti e consigli per il platino, con accesso diretto a ogni scheda. I trofei nascosti sono protetti dagli spoiler nella lista principale.</p>
    <div class="statline"><span>💎 {counts["Platino"]} Platino</span><span>🥇 {counts["Oro"]} Oro</span><span>🥈 {counts["Argento"]} Argento</span><span>🥉 {counts["Bronzo"]} Bronzo</span></div>
    </div><div class="info warn">⚠️ Una meditazione iniziale potrebbe essere mancabile. Prima di proseguire conserva un salvataggio manuale e consulta <a href="{url("guide-e-tutorial/meditazione-capitolo-1/")}">questa guida</a>.</div>
    <p><a href="{url("trofei/medaglie-oro/")}">🥇 Trofei Oro e medaglie Oro: guida ai requisiti →</a></p>'''
    cards=list_search()+'<h2>Trofei visibili</h2><div class="index-list">'+"".join(trophy_card(t) for t in shown)+'</div>'
    secrets='<details><summary>⚠️ Mostra i 28 trofei nascosti (spoiler)</summary><div class="index-list">'+"".join(trophy_card(t) for t in hidden)+'</div></details>'
    sources=f'<div class="source">Fonti: <a href="{e(TROPHY_SOURCE)}" rel="noopener noreferrer">PowerPyx – Trophy Roadmap</a> e <a href="{e(LIST_SOURCE)}" rel="noopener noreferrer">elenco italiano</a>. Le indicazioni possono cambiare con le patch.</div>'
    return lead+cards+secrets+sources

def trophy_detail(t, guides):
    path=trophy_path(t)
    intro=crumbs([("Trofei","trofei/"),(t["name_it"],path)])
    medal={"Oro":"🥇","Argento":"🥈","Bronzo":"🥉","Platino":"💎"}[t["tier"]]
    disclosure='<p class="info warn">⚠️ Questo trofeo è nascosto e può anticipare eventi della storia.</p>' if t["hidden"] else ""
    tips=f'<h2>💡 Consiglio per il platino</h2><p>{e(t["tip_it"])}</p>' if t.get("tip_it") else ""
    matched=[g for g in guides if g.get("related_trophy")==t["number"]]
    related="".join(f'<a href="{url(guide_path(g))}">🎮 {e(g["title"])} ↗</a>' for g in matched)
    body=f'''{intro}<div class="page-intro"><span class="eyebrow">{medal} Trofeo {e(t["tier"])} · PS5</span>
    <h1>{e(t["name_it"])}</h1><p class="lead">{e(t["requirement_it"])}</p></div>
    <div class="article-grid"><article class="prose">{disclosure}<h2>🎯 Come si ottiene</h2><p>{e(t["requirement_it"])}</p>
    {tips}<div class="info">🛡️ <strong>Platinum-safe:</strong> questa pagina descrive il requisito; non certifica eventuali glitch. Prima di usare exploit controlla patch, stato dei trofei e salvataggi.</div>
    <div class="source">Fonte: <a href="{e(t["source_url"])}" rel="noopener noreferrer">PowerPyx – GTA VI Trophy Roadmap</a>.
    Elenco dei nomi in italiano: <a href="{e(LIST_SOURCE)}" rel="noopener noreferrer">lista trofei PS5</a>.
    I requisiti possono cambiare con gli aggiornamenti del gioco.</div></article>
    <aside class="sidebox"><h3>Continua a esplorare</h3><a href="{url("trofei/")}">← Tutti i 55 trofei</a>
    <a href="{url("trofei/medaglie-oro/")}">🥇 Requisiti Oro</a>{related}
    <a href="{url("guide-e-tutorial/")}">Guide e tutorial →</a></aside></div>'''
    title=f'{t["name_it"]} — Trofeo {t["tier"]} GTA VI PS5 | Guida italiana'
    desc=f'Come sbloccare {t["name_it"]} in GTA 6 su PS5. Requisito: {t["requirement_it"]}'
    # No site-wide plagiarism or false screenshot-specific claims.
    robots=("noindex,follow" if t["hidden"] and TODAY<datetime(2026,11,21,tzinfo=timezone.utc) else "index,follow")
    write(Path(path)/"index.html", layout(title,desc,path,body,"trofei",robots=robots,structured=schema_article(title,desc,url(path))))
    return robots

def medal_page():
    path="trofei/medaglie-oro/"
    body=crumbs([("Trofei","trofei/"),("Medaglie Oro",path)])+f'''<section class="page-intro"><span class="eyebrow">🥇 Percorso platino</span><h1>Trofei Oro e medaglie Oro<br><span class="highlight">senza confusione</span></h1>
    <p class="lead">In GTA VI, i trofei di grado Oro sono distinti dalle medaglie Oro assegnate nelle attività.</p></section>
    <div class="prose"><h2>🏆 Due trofei di grado Oro</h2>
    <p><a href="{url("trofei/trofeo-07-devi-sapere-quando-scendere/")}">Devi sapere quando scendere</a>: completa la missione finale della storia. Contiene spoiler.</p>
    <p><a href="{url("trofei/trofeo-14-una-lunga-strada/")}">Una lunga strada</a>: raggiungi il completamento al 100% della checklist.</p>
    <h2>🎯 Medaglie nelle attività</h2><p>Secondo la roadmap PowerPyx non sono previste medaglie Oro per le missioni della storia.</p>
    <p>Per il trofeo Argento <a href="{url("trofei/trofeo-17-cecchino/")}">Cecchino</a> servono tutte le 42 medaglie Oro delle sfide dei poligoni di tiro.</p>
    <p>Per la checklist del 100% PowerPyx segnala anche 10 medaglie Oro sulle 13 sfide di gara.</p>
    <p class="source">Fonti: <a href="{TROPHY_SOURCE}">PowerPyx Trophy Guide</a> e <a href="https://www.powerpyx.com/gta-6-100-completion-checklist-guide/">100% Completion Checklist</a>.</p></div>'''
    title="GTA 6: trofei Oro, medaglie Oro e requisiti del platino PS5"
    desc="GTA VI: due trofei Oro PS5, 42 medaglie nei poligoni, 10 sfide gara e requisiti del 100%. Guida italiana."
    write(Path(path)/"index.html",layout(title,desc,path,body,"trofei",structured=schema_article(title,desc,url(path))))

def guide_index(guides):
    body=crumbs([("Guide e tutorial","guide-e-tutorial/")])+f'''<section class="page-intro"><span class="eyebrow">⚡ Consigli pratici per PS5</span>
    <h1>Guide e tutorial <span class="highlight">GTA 6</span></h1>
    <p class="lead">Come fare subito, senza articoli inutilmente lunghi. Pulsanti, procedure, vantaggi e fonti per approfondire.</p></section>
    <div class="info">📘 Tutti i tutorial sono in italiano, riprendono fonti indicate nella pagina e specificano i limiti di verifica. Nuove guide verranno aggiunte qui senza modificare l'indirizzo della sezione.</div>
    <section class="section"><div class="grid">{"".join(guide_card(g) for g in guides)}</div></section>'''
    title="GTA 6 Guide e Tutorial PS5: trucchi, collezionabili e 100%"
    desc="Guide GTA VI in italiano: tutorial rapidi per PS5, pulsanti, trofei, 100%, viaggio rapido, attività e strategie."
    write("guide-e-tutorial/index.html",layout(title,desc,"guide-e-tutorial/",body,"guide",structured={
      "@context":"https://schema.org","@type":"CollectionPage","name":title,
      "inLanguage":"it-IT","url":url("guide-e-tutorial/"),"numberOfItems":len(guides)}))

def guide_detail(g, tro):
    path=guide_path(g)
    num=g.get("related_trophy")
    related=next((t for t in tro if t["number"]==num),None)
    intro=crumbs([("Guide e tutorial","guide-e-tutorial/"),(g["title"],path)])
    steps="".join("<li>"+e(s)+"</li>" for s in g["steps"])
    related_html=(f'<a href="{url(trophy_path(related))}">🏆 Trofeo collegato: {e(related["name_it"])}</a>' if related else "")
    photo=f'''<figure class="figure"><img class="media" loading="lazy" src="{e(g["image"])}" alt="Screenshot promozionale ufficiale GTA VI, solo illustrativo">
    <figcaption>Immagine promozionale © Rockstar Games: non rappresenta la schermata della procedura. I diritti restano ai rispettivi titolari.</figcaption></figure>'''
    body=f'''{intro}<section class="page-intro"><span class="eyebrow">🎮 {e(g["tag"])} · Guida PS5</span>
    <h1>{e(g["title"])}</h1><p class="lead">{e(g["summary"])}</p></section>
    <div class="article-grid"><article class="prose">
    <div class="info">⚡ <strong>Risposta rapida:</strong> {e(g["benefit"])}</div>
    <h2>🎯 Procedura passo passo</h2><ol>{steps}</ol>
    <h2>✅ Risultato utile</h2><p>{e(g["benefit"])}</p>
    <div class="info warn">⚠️ {e(g["caution"])}</div>
    {photo}
    <div class="source">Approfondimento originale: <a href="{e(g["source_url"])}" rel="noopener noreferrer">PowerPyx — guida consultata</a>.
    I passaggi sono una sintesi editoriale in italiano e non riproducono l'articolo integrale.</div></article>
    <aside class="sidebox"><h3>Altri contenuti</h3><a href="{url("guide-e-tutorial/")}">← Tutte le guide</a>
    {related_html}<a href="{url("trofei/")}">🏆 Elenco trofei PS5</a></aside></div>'''
    title=g["title"]+" | Guida GTA VI PS5 in italiano"
    desc=g["summary"]+" Passaggi, comandi PS5 e fonte della guida."
    write(Path(path)/"index.html",layout(title,desc,path,body,"guide",image=g.get("image"),structured=schema_article(title,desc,url(path),g.get("image"))))

def redirect(path,dest):
    # Legacy local URLs only, old host will continue until cutover is validated.
    target=url(dest)
    page=(f'<!doctype html><html lang="it"><head><meta charset="utf-8">'
          f'<meta name="robots" content="noindex,follow">'
          f'<link rel="canonical" href="{e(target)}">'
          f'<meta http-equiv="refresh" content="0; url={e(target)}">'
          f'<title>Reindirizzamento GTA VI</title></head>'
          f'<body><p>Nuova guida: <a href="{e(target)}">{e(target)}</a></p></body></html>')
    write(path,page)

def main():
    trophies=json.loads((DATA/"trofei.json").read_text(encoding="utf-8"))["trophies"]
    guides=json.loads((DATA/"guide.json").read_text(encoding="utf-8"))["guides"]
    assert len(trophies)==55 and len({t["slug"] for t in trophies})==55
    assert len(guides)>=6 and len({g["id"] for g in guides})==len(guides)
    assert Counter(t["tier"] for t in trophies)==Counter({"Platino":1,"Oro":2,"Argento":6,"Bronzo":46})
    assert sum(t["hidden"] for t in trophies)==28
    assert all(g["source_url"].startswith("https://www.powerpyx.com/") for g in guides)
    OUT.mkdir(parents=True,exist_ok=True)
    shutil.copytree(SITE/"assets",OUT/"assets",dirs_exist_ok=True)
    write(".nojekyll","")
    home_title="GTA 6 Italia: guide, tutorial e trofei PS5 | Grand Theft Auto VI"
    home_desc="GTA 6 in italiano: guide, tutorial, trofei PS5, platino, collezionabili, trucchi e consigli rapidi per Grand Theft Auto VI."
    home_struct={"@context":"https://schema.org","@type":"WebSite","name":"GTA 6 Italia",
                 "url":url(),"inLanguage":"it-IT"}
    write("index.html",layout(home_title,home_desc,"",site_home(trophies,guides),"home",structured=home_struct))
    title="GTA 6 Trofei PS5: elenco completo dei 55 requisiti in italiano"
    desc="Tutti i 55 trofei GTA VI su PS5: Platino, 2 Oro, 6 Argento, 46 Bronzo, trofei nascosti e guida ai requisiti."
    write("trofei/index.html",layout(title,desc,"trofei/",trophy_index(trophies),"trofei",
          structured={"@context":"https://schema.org","@type":"CollectionPage",
                     "name":title,"url":url("trofei/"),"inLanguage":"it-IT","numberOfItems":55}))
    guide_index(guides)
    medal_page()
    hdr_paths=render_hdr_pages(write,layout,schema_article,url,crumbs)
    xml_urls=["","trofei/","guide-e-tutorial/","trofei/medaglie-oro/"] + hdr_paths
    for t in trophies:
        state=trophy_detail(t,guides)
        if state=="index,follow":xml_urls.append(trophy_path(t))
        redirect(t["id"]+".html",trophy_path(t))
    for g in guides:
        guide_detail(g,trophies)
        xml_urls.append(guide_path(g))
    redirect("guida-medaglie-oro.html","trofei/medaglie-oro/")
    write("robots.txt","User-agent: *\nAllow: /\nSitemap: "+url("sitemap.xml")+"\n")
    sitemap=ET.Element("urlset",xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for path in xml_urls:
        record=ET.SubElement(sitemap,"url")
        ET.SubElement(record,"loc").text=url(path)
    write("sitemap.xml",ET.tostring(sitemap,encoding="unicode",xml_declaration=True))
    print("BUILT GTA6 PORTAL:",len(trophies),"trofei,",len(guides),"guide,",len(hdr_paths),"HDR paths,",len(xml_urls),"indexable urls")
if __name__=="__main__":main()
