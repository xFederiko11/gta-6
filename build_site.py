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
import hashlib
import json
import os
import re
import shutil
import xml.etree.ElementTree as ET
from site_info import SOCIAL_URL, SOCIAL_HANDLE, iso_modified, page_meta
from hdr_catalog import render as render_hdr_pages
from cheats_catalog import render as render_cheat_pages
from sources_page import render as render_sources_page
from community_page import render as render_community_page
from related_research import for_guide as new_related_research, for_catalog as new_catalog_research
from trophy_experience import ornament, related_trophies, shootist_content, SHOOTING_SOURCE, video_panel
from social_preview import render as render_social_preview
from guide_source_validation import validate_guide_source

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
    card=img or url("assets/social-preview.png")
    out.extend([f'<meta property="og:image" content="{e(card)}">',
                f'<meta name="twitter:image" content="{e(card)}">'])
    if not img:
        out.extend(['<meta property="og:image:width" content="1200">',
                    '<meta property="og:image:height" content="630">',
                    '<meta property="og:image:alt" content="GTA 6 Italia: trofei, guide e HDR OLED per PS5">'])
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
         ("HDR OLED","hdr-oled/",section=="hdr"),("Trucchi PS5","trucchi/",section=="cheats"),
         ("Scoperte","scoperte/",section=="community")]
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
       f'<div><a href="{url("trofei/")}">Trofei</a> · <a href="{url("guide-e-tutorial/")}">Guide e tutorial</a> · <a href="{url("hdr-oled/")}">HDR OLED</a> · <a href="{url("trucchi/")}">Trucchi PS5</a> · <a href="{url("fonti/")}">Fonti e metodo</a> · <a href="{url("scoperte/")}">Scoperte community</a>'
       f'<p class="footer-social"><a href="{SOCIAL_URL}" rel="me noopener noreferrer" target="_blank">𝕏 Aggiornamenti su {SOCIAL_HANDLE} ↗</a></p>'
       f'<p class="footer-privacy"><a href="{url("privacy/")}">Privacy e visite</a></p></div>'
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
    icon={"Collezionabili":"🔎","Platino":"🏆","Trofei":"🥇","Movimento":"🚕"}.get(g["tag"],"🎮")
    return (f'<article class="card guide-index-card"><a class="card-link guide-index-link" '
        f'href="{url(guide_path(g))}">'
        '<span class="guide-tile-media" aria-hidden="true">'
        f'<span class="guide-tile-fallback"><b>{icon}</b><small>GTA VI · PS5</small></span>'
        f'<img src="{e(g["image"])}" loading="lazy" decoding="async" width="640" height="360" '
        'alt="" onload="this.classList.add(\'media-loaded\')" '
        'onerror="this.remove()"></span>'
        f'<span class="card-label">🎮 {e(g["tag"])}</span>'
        f'<h3>{e(g["title"])}</h3><p>{e(g["summary"])}</p>'
        f'<span class="end">{len(g["steps"])} passaggi · Apri la guida ↗</span></a></article>')

def trophy_card(t):
    desc=t["requirement_it"] if not t["hidden"] else "Trofeo nascosto: attenzione agli spoiler."
    return f'<article class="index-item" data-trophy-number="{t["number"]}" data-tier="{e(t["tier"].lower())}" data-search="{e((t["name_it"]+" "+desc).lower())}"><span class="card-label {e(t["tier"].lower())}">{e(t["tier"])}</span><h3><a href="{url(trophy_path(t))}">{e(t["name_it"])}</a></h3><p>{e(desc)}</p></article>'

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
    hdr_data=json.loads((DATA/"hdr_oled.json").read_text(encoding="utf-8"))
    hdr_total=sum(len(f["models"]) for f in hdr_data["families"])
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
    {category_card("HDR OLED per PS5 Pro","Valori HDR direttamente in GTA VI: Max Brightness, Black Levels, Paper White e profili OLED verificabili.","hdr-oled/",f"{hdr_total} MODELLI TV","📺")}
    {category_card("Trucchi GTA VI PS5","Codici post-storia con sequenze D-pad illustrate, effetti e avvisi sui trofei.","trucchi/","DUALSENSE","🎮")}
    {category_card("Scoperte GTA VI community","Nuove guide, segnalazioni e rumor con fonte e stato di verifica chiaramente indicati.","scoperte/","FONTI IN VERIFICA","🔎")}
    </div></section>'''
    guides_cards="".join(guide_card(g) for g in guides[:6])
    guides_section=f'''<section class="section"><div class="section-head"><div><span class="eyebrow">⚡ Tips & tricks</span><h2>Guide rapide che fanno risparmiare tempo</h2><p>Le istruzioni subito, gli approfondimenti quando servono.</p></div><a href="{url("guide-e-tutorial/")}">Tutte le guide ↗</a></div><div class="grid">{guides_cards}</div></section>'''
    call=f'''<section class="section feature"><div><span class="eyebrow">🏆 Obiettivo platino</span><h2>Un percorso, tutti i trofei.</h2>
    <p class="lead">Trofei mancabili, requisiti e sfide: una base consultabile prima di prendere decisioni irreversibili nella storia.</p>
    <a class="button secondary" href="{url("trofei/")}">Apri l'elenco trofei →</a></div><div class="decor" aria-hidden="true"></div></section>'''
    hdr_feature=f'''<section class="section hdr-promo"><div><span class="eyebrow">📺 Nuova guida OLED</span>
    <h2>GTA VI: quali valori HDR inserire nel gioco?</h2>
    <p>LG OLED C3/C4/C5/C6, B4 e G4/G5/G6, Samsung S90D/S90F/S90H e S95D/S95F/S95H, Sony BRAVIA, Philips e Panasonic:
    impostazioni raggruppate per famiglia, codici commerciali e dimensioni verificate.</p>
    <a class="button secondary" href="{url("hdr-oled/")}">Trova i valori HDR nel gioco →</a></div>
    <div class="hdr-promo-orb" aria-hidden="true">HDR<span>OLED</span></div></section>'''
    return hero+sections+hdr_feature+guides_section+call

def trophy_index(trophies):
    shown=[t for t in trophies if not t["hidden"]]
    hidden=[t for t in trophies if t["hidden"]]
    counts=Counter(t["tier"] for t in trophies)
    lead=crumbs([("Trofei","trofei/")])+f'''<div class="page-intro"><span class="eyebrow">🏆 Trofei PlayStation 5</span><h1>Tutti i 55 trofei<br><span class="highlight">GTA VI in italiano</span></h1>
    <p class="lead">Requisiti e consigli per il platino, con accesso diretto a ogni scheda. Attenzione: anche le schede dei trofei nascosti possono contenere spoiler.</p>
    <div class="statline"><span>💎 {counts["Platino"]} Platino</span><span>🥇 {counts["Oro"]} Oro</span><span>🥈 {counts["Argento"]} Argento</span><span>🥉 {counts["Bronzo"]} Bronzo</span></div>
    </div><div class="info warn">⚠️ Una meditazione iniziale potrebbe essere mancabile. Prima di proseguire conserva un salvataggio manuale e consulta <a href="{url("guide-e-tutorial/meditazione-capitolo-1/")}">questa guida</a>.</div>
    <p><a href="{url("trofei/medaglie-oro/")}">🥇 Trofei Oro e medaglie Oro: guida ai requisiti →</a></p><p><a class="button secondary" href="{url("trofei/roadmap-platino/")}">🗺️ Roadmap Platino GTA 6: cinque fasi e checklist →</a></p><p><a href="{url("trofei/roadmap-platino/")}#guida-55-trofei">🏆 Apri le 55 schede operative con ricerca e filtri →</a> · <a href="{url("mappe-guide/")}">⌖ Mappa dei luoghi verificati →</a></p><p><a href="{url("trofei/100-percento/")}">📋 Checklist 100% con 35 categorie e 18 set carte →</a> · <a href="{url("trofei/trofei-difficili/")}">🔎 Rhino, UFO e trofei difficili →</a></p><p><a href="{url("collezionabili/percorsi/")}">⌖ 41 checkpoint con percorsi per regione (dati parziali) →</a></p>'''
    cards=list_search()+'<h2>Trofei visibili</h2><div class="index-list">'+"".join(trophy_card(t) for t in shown)+'</div>'
    secrets='<div class="v-spoiler-warning" role="note">⚠️ <strong>Attenzione spoiler:</strong> i trofei nascosti possono rivelare eventi della storia.</div><h2>Trofei nascosti</h2><div class="index-list">'+"".join(trophy_card(t) for t in hidden)+'</div>'
    sources=f'<div class="source">Fonti: <a href="{e(TROPHY_SOURCE)}" rel="noopener noreferrer">PowerPyx – Trophy Roadmap</a> e <a href="{e(LIST_SOURCE)}" rel="noopener noreferrer">elenco italiano</a>. Le indicazioni possono cambiare con le patch.</div>'
    progress=('<section class="trophy-index-progress" data-trophy-index-progress>'
              '<div><span class="eyebrow">IL TUO PERCORSO</span>'
              '<strong data-trophy-total aria-live="polite">0 / 55 trofei segnati</strong>'
              '<p>Segna i trofei nelle rispettive schede: il riepilogo si aggiorna qui. '
              'Non legge il tuo account PSN.</p></div>'
              '<progress max="55" value="0" data-trophy-index-bar '
              'aria-label="Trofei segnati manualmente"></progress></section>')
    return lead+progress+cards+secrets+sources+f'<script src="{url("assets/trophy-experience.js")}" defer></script>'

def trophy_seo_title(t):
    """Keep the complete PS5 trophy name while respecting concise SERP titles.

    The name (including spoiler-related wording) is never truncated; the
    suffix is shortened instead. The full requirement remains on the page.
    """
    name=t["name_it"].strip()
    choices=(
        f'{name} | Trofeo {t["tier"]} GTA 6 PS5',
        f'{name} | Trofeo GTA 6 PS5',
        f'{name} | GTA 6 PS5',
        f'{name} | GTA 6',
    )
    title=next((item for item in choices if len(item)<=60),choices[-1])
    if len(title)<=43:
        for suffix in (" | Guida italiana"," | Guida"):
            if len(title)+len(suffix)<=60:
                return title+suffix
    return title


def trophy_detail(t, guides, trophies):
    path=trophy_path(t)
    intro=crumbs([("Trofei","trofei/"),(t["name_it"],path)])
    medal={"Oro":"🥇","Argento":"🥈","Bronzo":"🥉","Platino":"💎"}[t["tier"]]
    is_shootist=t["number"]==17
    disclosure='<p class="info warn">⚠️ Questa scheda contiene dettagli di un trofeo nascosto.</p>' if t["hidden"] else ""
    fact=(f'<div class="trophy-hero-facts"><span><b>42</b> medaglie Oro</span>'
          '<span><b>12</b> percorsi</span><span><b>2</b> poligoni</span></div>'
          if is_shootist else f'<div class="trophy-hero-facts"><span>🏆 {e(t["tier"])}</span><span>🎮 PS5 / PS5 Pro</span></div>')
    hero=(f'''{intro}<section class="trophy-hero" aria-label="Scheda trofeo">
    <div class="trophy-hero-copy"><span class="eyebrow">{medal} TROFEO {e(t["tier"]).upper()} · GTA VI PS5</span>
    <h1>{e(t["name_it"])}</h1>
    <p class="trophy-hero-requirement">{e(t["requirement_it"])}</p>
    {fact}
    <div class="trophy-actions"><a class="button" href="#requisito">
    ▶ INIZIA IL TUTORIAL</a>
    <a class="button secondary" href="{url("trofei/")}">← Tutti i trofei</a></div></div>
    <div class="trophy-art-wrap">{ornament(t["tier"])}</div></section>''')
    finished=(f'<div class="trophy-done-wrap"><button type="button" data-trophy-done="{t["number"]}" '
              f'class="trophy-done-button" aria-pressed="false">○ Segna trofeo ottenuto</button>'
              '<span class="micro" data-trophy-status>Solo in questo browser. Non modifica i trofei PSN.</span></div>')
    # No speculative tasks: each trophy has exactly one sourced requirement.
    task=(
        '<section class="quick-route trophy-guide-flow" id="requisito" data-trophy-beginner>'
        '<span class="tg-start">▶ QUESTA È LA GUIDA · INIZIA QUI</span>'
        '<p class="tg-step-label">UN SOLO OBIETTIVO</p>'
        '<h2>Cosa devi fare</h2>'
        '<p class="tg-goal">'+e(t["requirement_it"])+'</p>'
    )
    if t.get("tip_it"):
        task+=('<div class="tg-guidance"><strong>COME FARLO · CONSIGLIO DOCUMENTATO</strong>'
               '<p>'+e(t["tip_it"])+'</p></div>')
    else:
        task+=('<p class="tg-guidance tg-no-guess"><strong>Nessun passaggio extra confermato.</strong> '
               'Segui esattamente il requisito sopra; non aggiungiamo azioni inventate.</p>')
    task+=(
        '<div class="tg-verify"><strong>COME CAPIRE SE HAI FINITO</strong>'
        '<p>Controlla che il trofeo risulti sbloccato nell’elenco Trofei della PS5. '
        'Solo quando lo vedi ottenuto, segnalo qui sotto.</p></div>'
        '<div class="tg-finish">'+finished+'</div>'
        '</section>'
    )
    if is_shootist:
        guidance=(task+
            '<details class="tg-deep" id="dettagli-cecchino">'
            '<summary>🥇 APRI LA CHECKLIST DELLE 42 MEDAGLIE →</summary>'
            '<div class="tg-deep-content">'+shootist_content()+'</div></details>')
    else:
        guidance=task
    related_guides=[g for g in guides if g.get("related_trophy")==t["number"]]
    guides_html="".join(
        f'<a class="guide-related-link" href="{url(guide_path(g))}">🎮 {e(g["title"])} ↗</a>'
        for g in related_guides
    )
    sources=(f'<details class="source-details"><summary>🔎 Fonti e note di verifica</summary>'
             f'<p><a href="{e(t["source_url"])}" target="_blank" rel="noopener noreferrer">'
             'PowerPyx — GTA VI Trophy Roadmap ↗</a>. '
             f'<a href="{e(LIST_SOURCE)}" target="_blank" rel="noopener noreferrer">'
             'Elenco italiano dei trofei PS5 ↗</a>.</p>'
             + (f'<p><a href="{e(SHOOTING_SOURCE)}" target="_blank" rel="noopener noreferrer">'
                'PowerPyx — guida completa alle 42 medaglie Oro ↗</a></p>'
                if is_shootist else '')
             + '<p>Le istruzioni sono sintesi originali del sito. '
             'La presenza di fonti non garantisce che un exploit mantenga attivi i trofei.</p></details>')
    article=(
        '<div class="article-grid trophy-article">'
        '<article class="prose trophy-prose">'
        +disclosure+guidance
        +'<div class="trophy-safety"><strong>🛡️ Platino prima di tutto</strong>'
        '<p>Questa scheda spiega il requisito del gioco, non certifica glitch o duplicazioni. '
        'Non usare trucchi che disabilitano trofei e salvataggi durante la run del platino.</p></div>'
        + sources
        + '</article>'
        '<details class="tg-extra"><summary>Altre guide utili (facoltative)</summary>'
        '<aside class="sidebox trophy-sidebar"><h3>Scopri altre guide</h3>'
        f'<a href="{url("trofei/")}">🏆 Elenco completo dei 55 trofei</a>'
        f'<a href="{url("trofei/roadmap-platino/")}">🗺️ Roadmap Platino in cinque fasi</a>'
        f'<a href="{url("trofei/roadmap-platino/")}#guida-55-trofei">🏆 Tutte le 55 strategie trofei</a>'
        f'<a href="{url("trofei/medaglie-oro/")}">🥇 Medaglie Oro e 100%</a>'
        +guides_html
        +f'<a href="{url("guide-e-tutorial/")}">⚡ Guide pratiche PS5 →</a>'
        + '</aside></details></div>'
    )
    body=hero+article+(
        '<details class="tg-extra tg-related"><summary>Altri trofei (facoltativo)</summary>'
        +related_trophies(t,trophies,url)+'</details>')
    body+=f'<script src="{url("assets/trophy-experience.js")}" defer></script>'
    title=trophy_seo_title(t)
    desc=f'Come sbloccare {t["name_it"]} in GTA 6 su PS5. Requisito: {t["requirement_it"]}'
    robots=("noindex,follow" if t["hidden"] and TODAY<datetime(2026,11,21,tzinfo=timezone.utc) else "index,follow")
    write(Path(path)/"index.html",layout(title,desc,path,body,"trofei",robots=robots,structured=schema_article(title,desc,url(path))))
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
    <section class="section"><div class="grid">{"".join(guide_card(g) for g in guides)}</div></section>''' + new_catalog_research()
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
    step_revision=hashlib.sha256("\n".join(g["steps"]).encode("utf-8")).hexdigest()[:12]
    steps="".join(
        f'<li><label class="guide-step-option"><input type="checkbox" data-guide-step="{n}" '
        f'aria-label="Passaggio {n} completato">'
        f'<span class="guide-step-number" aria-hidden="true">{n:02d}</span>'
        f'<span class="guide-step-text">{e(step)}</span></label></li>'
        for n,step in enumerate(g["steps"],1))
    related_html=(f'<a href="{url(trophy_path(related))}">🏆 Trofeo collegato: {e(related["name_it"])}</a>' if related else "")
    # Editorial images are linked to existing official promotional material, not copied from PowerPyx.
    photo=f'''<figure class="figure guide-photo"><div class="guide-media-wrap">
    <div class="guide-media-fallback" role="img" aria-label="Immagine illustrativa non disponibile">
    <span aria-hidden="true">🎮</span><strong>GTA VI · Guida PS5</strong>
    <small>Immagine promozionale non disponibile</small></div>
    <img class="media" loading="lazy" decoding="async" src="{e(g["image"])}"
    alt="Immagine promozionale ufficiale GTA VI, solo illustrativa"
    onload="this.classList.add('media-loaded')"
    onerror="this.remove();this.parentElement.classList.add('media-unavailable')"></div>
    <figcaption>Immagine promozionale di Rockstar Games, illustrativa e non specifica della procedura. Diritti dei rispettivi titolari.</figcaption></figure>'''
    theme=g["tag"]
    guide_source = "Insider Gaming" if "insider-gaming.com" in g["source_url"] else "PowerPyx"
    spoiler_guard = g["tag"] == "Soldi"
    intro_block=f'''{intro}<section class="guide-hero"><span class="eyebrow">🎮 {e(theme)} · GTA VI PS5 / PS5 Pro</span>
    <h1>{e(g["title"])}</h1><p class="lead">{e(g["summary"])}</p>
    <div class="guide-hero-facts"><span>🧭 {len(g["steps"])} passaggi</span>
    <span>🎮 PS5 / PS5 Pro</span><span>🔎 Fonte: {e(guide_source)}</span></div>
    <div class="guide-hero-actions"><a class="button" href="#passaggi">↓ Vai ai passaggi</a>
    <a class="button secondary" href="#fonte-guida">↗ Fonti</a></div></section>'''
    # Prefer related trophy and topic; never silently fill the rail with unrelated items.
    other_guides=[item for item in json.loads((DATA/"guide.json").read_text(encoding="utf-8"))["guides"]
                  if item["id"]!=g["id"]]
    other_guides.sort(key=lambda item: (
        -(num is not None and item.get("related_trophy")==num),
        -(item["tag"]==g["tag"]),
        item["title"].casefold()))
    suggestions=other_guides[:3]
    cards="".join(
        f'<a class="discovery-card" href="{url(guide_path(item))}">'
        f'<span class="discovery-label">🎮 {e(item["tag"])}</span>'
        f'<strong>{e(item["title"])}</strong><span>Apri la guida →</span></a>'
        for item in suggestions
    )
    body=(
        intro_block+'<div class="article-grid guide-article">'
        + '<article class="prose guide-prose">'
        + '<div class="guide-answer"><span class="eyebrow">⚡ RISPOSTA RAPIDA</span>'
        + f'<p>{e(g["benefit"])}</p></div>'
        +photo
        + ('<p class="v-spoiler-warning" role="note">⚠️ <strong>Attenzione spoiler:</strong> qui trovi luoghi, passaggi e possibili eventi della storia.</p>' if spoiler_guard else '')
        + f'<section id="passaggi" class="guide-steps" data-guide-steps="{e(g["id"])}" data-guide-version="{step_revision}">'
        + f'<div class="guide-steps-header"><span class="eyebrow">CHECKLIST PERSONALE</span>'
        + f'<span class="guide-steps-count" data-guide-count aria-live="polite">0 / {len(g["steps"])}</span></div>'
        + f'<h2>🎯 Procedura passo passo</h2><ol>{steps}</ol>'
        + f'<progress class="guide-steps-progress" max="{len(g["steps"])}" value="0" '
        + f'aria-label="Avanzamento personale dei passaggi"></progress>'
        + '<div class="guide-steps-footer"><span data-guide-feedback role="status" aria-live="polite">'
        + 'Spunta i passaggi mentre giochi. Solo su questo dispositivo, senza collegamento PSN.</span>'
        + '<button class="guide-copy" type="button" data-guide-copy>📋 Copia passaggi</button></div></section>'
        + f'<div class="guide-caution"><strong>⚠️ Da verificare prima di procedere</strong><p>{e(g["caution"])}</p></div>'
        + (video_panel() if g["id"]=="poligoni-concentrazione" else "")
        +new_related_research(g["id"])
        +f'<details class="source-details" id="fonte-guida"><summary>🔎 Fonti e note editoriali</summary>'
        + f'<p>Approfondimento originale: <a href="{e(g["source_url"])}" target="_blank" '
        + f'rel="noopener noreferrer">{e(guide_source)} — guida consultata ↗</a>.</p>'
        + '<p>Le istruzioni sono una sintesi originale in italiano e non riproducono l’articolo integrale. '
        + 'La foto è illustrativa: non rappresenta il passaggio descritto.</p></details>'
        + '</article><aside class="sidebox guide-sidebar"><h3>Continua a giocare</h3>'
        + f'<a href="{url("guide-e-tutorial/")}">← Tutte le guide</a>'
        +related_html
        +f'<a href="{url("trofei/")}">🏆 Elenco trofei PS5</a>'
        + f'<a href="{url("scoperte/")}">🔎 Novità dalla community</a>'
        + '</aside></div>'
        + '<section class="section discover-more"><div class="section-head"><div>'
        + '<span class="eyebrow">ALTRI CONSIGLI UTILI</span><h2>La prossima guida</h2>'
        + '</div></div><div class="discovery-rail">'+cards+'</div></section>'
        + f'<script src="{url("assets/guide-interactions.js")}" defer></script>'
        + (f'<script src="{url("assets/trophy-experience.js")}" defer></script>'
           if g["id"]=="poligoni-concentrazione" else "")
    )
    title=g["title"]+" | Guida GTA VI PS5 in italiano"
    desc=g["summary"]+" Passaggi, comandi PS5 e fonte della guida."
    write(Path(path)/"index.html",layout(title,desc,path,body,"guide",image=g.get("image"),structured=schema_article(title,desc,url(path),g.get("image"))))

def privacy_page():
    body=(
        crumbs([("Privacy e contatore visite","privacy/")])
        + '<section class="page-intro"><span class="eyebrow">🔐 TRASPARENZA</span>'
        '<h1>Privacy e <span class="highlight">visite</span></h1>'
        '<p class="lead">Un contatore pubblico semplice, senza account analytics.</p></section>'
        '<section class="section prose"><h2>Come funziona il contatore</h2>'
        '<p>Ogni pagina mostra un badge di hitscounter.dev. Il numero rappresenta '
        'le richieste conteggiate dal servizio per quella pagina, non i visitatori '
        'unici, le sessioni, le persone o i follower. Ricaricamenti, protezioni '
        'del browser e richieste automatiche possono influenzare il totale.</p>'
        '<p>Non è richiesta alcuna iscrizione da parte dei lettori o del gestore. '
        'Il badge è un servizio esterno: il suo server può ricevere informazioni '
        'tecniche associate alla richiesta. Non utilizziamo GoatCounter né '
        'altri strumenti aggiuntivi di analytics o profilazione.</p>'
        '<h2>Video, link e progressi</h2><p>Il player YouTube si carica '
        'solo su richiesta. I link verso X e altri siti aprono servizi indipendenti. '
        'Le checklist salvano i progressi soltanto nel browser locale '
        'e non li inviano a noi o al PlayStation Network.</p>'
        '<p>Questo sito statico non dispone di statistiche su visitatori unici, '
        'provenienza o conversioni: non presentiamo stime come dati reali.</p></section>'
    )
    from growth_tracking_v1 import normalize_id
    if normalize_id(os.getenv("UMAMI_WEBSITE_ID", "")):
        # Only disclose enabled collection if the build actually loads Umami.
        body = body.replace(
            "Un contatore pubblico semplice, senza account analytics.",
            "Statistiche aggregate e contatore pubblico: cosa misuriamo davvero.")
        body = body.replace(
            "Non utilizziamo GoatCounter né altri strumenti aggiuntivi di analytics o profilazione.",
            "Non utilizziamo GoatCounter. Umami Cloud è attivo per contare visite "
            "aggregate e clic sui collegamenti X/YouTube, senza account obbligatori "
            "o cookie impostati dal nostro codice. Il gestore di Umami può ricevere "
            "dati tecnici delle richieste; il tracciamento rispetta il segnale "
            "Do Not Track quando disponibile. Il servizio è di un soggetto terzo: "
            "consulta anche la sua informativa sulla privacy.")
        body = body.replace(
            "Questo sito statico non dispone di statistiche su visitatori unici, "
            "provenienza o conversioni: non presentiamo stime come dati reali.",
            "Umami misura statistiche aggregate per pagina e gli eventi "
            "x-follow-intent, x-share-intent, x-reply-intent, x-post-open, "
            "x-screenshot-intent (soltanto apertura della bozza su X, NON invio "
            "o licenza dell’immagine) e youtube-player-open "
            "(apertura del player, non visione completa). "
            "Un clic per seguire il profilo NON prova che un follower sia stato "
            "acquisito. Non registriamo identità PSN o account X, non "
            "colleghiamo visitatori individuali ai follower e non inventiamo "
            "dati di conversione finale. Il blocco degli strumenti di analisi "
            "nel browser può ridurre i conteggi.")
        body = body.replace(
            "Il player YouTube si carica solo su richiesta.",
            "Il player YouTube si carica solo su richiesta.")
    title="GTA 6 Italia: privacy e contatore visite"
    desc=("Statistiche aggregate Umami e contatore pagine: informazioni sulla privacy."
          if normalize_id(os.getenv("UMAMI_WEBSITE_ID", "")) else
          "Come funziona il contatore pubblico di visualizzazioni del sito GTA 6 Italia, senza account analytics.")
    write("privacy/index.html",layout(title,desc,"privacy/",body,structured={
        "@context":"https://schema.org","@type":"WebPage","name":title,
        "url":url("privacy/"),"inLanguage":"it-IT"}))


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
    if not all(validate_guide_source(g.get("source_url")) for g in guides):
        raise ValueError("Unapproved or malformed guide source URL")
    OUT.mkdir(parents=True,exist_ok=True)
    shutil.copytree(SITE/"assets",OUT/"assets",dirs_exist_ok=True)
    render_social_preview(OUT/"assets"/"social-preview.png")
    write(".nojekyll","")
    home_title="GTA 6 Italia: guide, tutorial e trofei PS5 | Grand Theft Auto VI"
    home_desc="GTA 6 in italiano: guide, tutorial, trofei PS5, platino, collezionabili, trucchi e consigli rapidi per Grand Theft Auto VI."
    home_struct={"@context":"https://schema.org","@type":"WebSite","name":"GTA 6 Italia",
                 "url":url(),"inLanguage":"it-IT"}
    write("index.html",layout(home_title,home_desc,"",site_home(trophies,guides),"home",structured=home_struct))
    title="Trofei GTA 6 PS5: 55 requisiti e guida al platino"
    desc="Tutti i 55 trofei GTA VI su PS5: Platino, 2 Oro, 6 Argento, 46 Bronzo, trofei nascosti e guida ai requisiti."
    write("trofei/index.html",layout(title,desc,"trofei/",trophy_index(trophies),"trofei",
          structured={"@context":"https://schema.org","@type":"CollectionPage",
                     "name":title,"url":url("trofei/"),"inLanguage":"it-IT","numberOfItems":55}))
    guide_index(guides)
    medal_page()
    hdr_paths=render_hdr_pages(write,layout,schema_article,url,crumbs)
    cheat_paths=render_cheat_pages(write,layout,schema_article,url,crumbs)
    sources_path=render_sources_page(write,layout,url,crumbs)
    community_path=render_community_page(write,layout,url,crumbs)
    privacy_page()
    xml_urls=["","trofei/","guide-e-tutorial/","trofei/medaglie-oro/",sources_path,community_path,"privacy/"] + hdr_paths + cheat_paths
    for t in trophies:
        state=trophy_detail(t,guides,trophies)
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
