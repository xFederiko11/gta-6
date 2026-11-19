"""Offline validation of generated GTA 6 Pages. No scraping or API calls."""
from __future__ import annotations
import json
import html
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

class PortalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.out=Path(cls.tmp.name)
        env=dict(os.environ,SITE_OUT=str(cls.out))
        proc=subprocess.run([sys.executable,"build_site.py"],env=env,capture_output=True,text=True)
        if proc.returncode:
            raise AssertionError(proc.stdout+"\n"+proc.stderr)
        cls.trophies=json.loads(Path("data/trofei.json").read_text(encoding="utf-8"))["trophies"]
        cls.guides=json.loads(Path("data/guide.json").read_text(encoding="utf-8"))["guides"]
        cls.hdr=json.loads(Path("data/hdr_oled.json").read_text(encoding="utf-8"))
        cls.cheats=json.loads(Path("data/trucchi.json").read_text(encoding="utf-8"))["cheats"]
        cls.sources=json.loads(Path("data/fonti_editoriali.json").read_text(encoding="utf-8"))["sources"]
        cls.community=json.loads(Path("data/community_feed.json").read_text(encoding="utf-8"))
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_content_counts_and_links(self):
        self.assertEqual(len(self.trophies),55)
        self.assertEqual(len(self.guides),6)
        self.assertEqual(len(self.hdr["families"]),21)
        self.assertEqual(sum(len(f["models"]) for f in self.hdr["families"]),92)
        self.assertEqual(len(self.cheats),17)
        self.assertEqual(len(self.sources),10)
        self.assertEqual(sum(x["independent_source_count"]==2 for x in self.cheats),9)
        self.assertEqual(sum(t["hidden"] for t in self.trophies),28)
        homepage=(self.out/"index.html").read_text(encoding="utf-8")
        self.assertIn("Trofei",homepage)
        self.assertIn("Guide e tutorial",homepage)
        self.assertIn("HDR OLED",homepage)
        self.assertIn("Trucchi PS5",homepage)
        self.assertIn("Scoperte GTA VI community",homepage)
        self.assertIn("https://xfederiko11.github.io/gta-6/hdr-oled/",homepage)
        self.assertIn("https://xfederiko11.github.io/gta-6/",homepage)
        self.assertNotIn("federiko-gta-playstation-bot",homepage)

    def test_every_trophy_seo_page_and_legacy_alias(self):
        for trophy in self.trophies:
            directory=self.out/"trofei"/trophy["slug"]
            html=(directory/"index.html").read_text(encoding="utf-8")
            self.assertIn(trophy["name_it"],html)
            self.assertIn("rel=\"canonical\"",html)
            self.assertIn("application/ld+json",html)
            self.assertIn("lang=\"it\"",html)
            self.assertIn("PowerPyx",html)
            self.assertIn("https://xfederiko11.github.io/gta-6/trofei/",html)
            legacy=(self.out/(trophy["id"]+".html")).read_text(encoding="utf-8")
            self.assertIn(trophy["slug"],legacy)

    def test_guides_each_have_original_source_and_italian_steps(self):
        for guide in self.guides:
            html=(self.out/"guide-e-tutorial"/guide["id"]/"index.html").read_text(encoding="utf-8")
            self.assertIn(guide["title"],html)
            self.assertIn(guide["source_url"].replace("&","&amp;"),html)
            procedural=re.search(r"<h2>🎯 Procedura passo passo</h2><ol>(.*?)</ol>",html,re.S)
            self.assertIsNotNone(procedural)
            self.assertEqual(procedural.group(1).count("<li>"),len(guide["steps"]))
            self.assertIn("Immagine promozionale",html)
            self.assertIn("guide-media-fallback",html)
            self.assertIn("onerror=",html)
            self.assertIn('data-guide-steps="'+guide["id"]+'"',html)
            self.assertIn("guide-steps-progress",html)
            self.assertIn("data-guide-copy",html)
            self.assertEqual(html.count("data-guide-step="),len(guide["steps"]))
            self.assertIn("guide-interactions.js",html)
            self.assertIn("Passaggi",html) if "Passaggi" in html else self.assertIn("Procedura",html)

    def test_guide_cards_have_photo_fallback_and_useful_recommendations(self):
        page=(self.out/"guide-e-tutorial"/"index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('class="card guide-index-card"'),len(self.guides))
        self.assertEqual(page.count('class="guide-tile-fallback"'),len(self.guides))
        self.assertEqual(page.count("guide-tile-media"),len(self.guides))
        self.assertIn("loading=\"lazy\"",page)
        for guide in self.guides:
            self.assertIn(guide["title"],page)
        related=(self.out/"guide-e-tutorial"/"studiare-animali"/"index.html").read_text(encoding="utf-8")
        self.assertIn("70-sfide-100-percento/",related)
        self.assertIn("scansionare-veicoli/",related)
        trophy=(self.out/"trofei"/"trofeo-17-cecchino"/"index.html").read_text(encoding="utf-8")
        self.assertIn("data-medal-tracker",trophy)
        self.assertIn("data-video-id=",trophy)

    def test_guide_steps_are_readable_without_javascript(self):
        for guide in self.guides:
            markup=(self.out/"guide-e-tutorial"/guide["id"]/"index.html").read_text(encoding="utf-8")
            self.assertIn("<h2>🎯 Procedura passo passo</h2><ol>",markup)
            self.assertIn('class="guide-step-text"',markup)
            self.assertIn('type="checkbox"',markup)
            self.assertIn("Solo su questo dispositivo",markup)
            self.assertIn("senza collegamento PSN",markup)
            self.assertIn("Copia passaggi",markup)
        script=(self.out/"assets"/"guide-interactions.js").read_text(encoding="utf-8")
        self.assertIn("window.localStorage",script)
        self.assertIn("navigator.clipboard.writeText",script)
        self.assertNotIn("fetch(",script)
        self.assertNotIn("PSN_API",script)

    def test_official_shooting_range_video_appears_only_when_relevant(self):
        shooting=(self.out/"guide-e-tutorial"/"poligoni-concentrazione"/"index.html").read_text(encoding="utf-8")
        self.assertIn("Guarda il poligono in azione",shooting)
        self.assertIn("riferimento visivo, non una guida",shooting)
        self.assertIn('data-video-id="tJbzMqJGH4k"',shooting)
        self.assertIn("trophy-experience.js",shooting)
        self.assertIn("guide-interactions.js",shooting)
        self.assertIn('onerror="this.remove()"',shooting)
        for guide in self.guides:
            if guide["id"]=="poligoni-concentrazione":
                continue
            markup=(self.out/"guide-e-tutorial"/guide["id"]/"index.html").read_text(encoding="utf-8")
            self.assertNotIn("trophy-experience.js",markup)
            self.assertNotIn("data-video-id=",markup)
        trophy=(self.out/"trofei"/"trofeo-17-cecchino"/"index.html").read_text(encoding="utf-8")
        self.assertIn("Guarda il poligono in azione",trophy)
        self.assertIn('onload="this.classList.add(\'media-loaded\')"',trophy)

    def test_related_cheat_cards_are_category_relevant(self):
        for cheat in self.cheats:
            page=(self.out/"trucchi"/cheat["slug"]/"index.html").read_text(encoding="utf-8")
            siblings=[x for x in self.cheats if x["category"]==cheat["category"]
                      and x["slug"]!=cheat["slug"]]
            for sibling in siblings[:3]:
                self.assertIn("trucchi/"+sibling["slug"]+"/",page)
            if not siblings:
                self.assertIn("Esplora tutte le sequenze documentate",page)
            self.assertIn("salvataggi",page.lower())
        script=(self.out/"assets"/"cheat-interactions.js").read_text(encoding="utf-8")
        self.assertIn("navigator.clipboard.writeText",script)
        self.assertNotIn("fetch(",script)
        self.assertNotIn("localStorage",script)

    def test_robots_and_sitemap(self):
        self.assertTrue((self.out/"robots.txt").exists())
        self.assertTrue((self.out/".nojekyll").exists())
        raw=(self.out/"sitemap.xml").read_text(encoding="utf-8")
        root=ET.fromstring(raw)
        locs=[x.text for x in root.iter() if x.tag.endswith("loc")]
        self.assertEqual(len(locs),7+27+6+1+len(self.hdr["families"])+1+len(self.cheats))
        self.assertEqual(len(locs),len(set(locs)))
        self.assertTrue(all(x.startswith("https://xfederiko11.github.io/gta-6/") for x in locs))
        self.assertTrue((self.out/"trofei"/"medaglie-oro"/"index.html").exists())
        self.assertIn("https://xfederiko11.github.io/gta-6/hdr-oled/",locs)

    def test_spoiler_indexing_before_launch_grace(self):
        # When executed after 21 November, all 55 pages become indexable.
        # The homepage keeps spoiler list collapsed in both cases.
        html=(self.out/"trofei"/"index.html").read_text(encoding="utf-8")
        self.assertIn("<details>",html)
        self.assertIn("28 trofei nascosti",html)

    def test_all_public_pages_show_real_update_views_and_x(self):
        pages=[self.out/"index.html",self.out/"trofei"/"index.html",
               self.out/"guide-e-tutorial"/"index.html",
               self.out/"trofei"/"medaglie-oro"/"index.html"]
        pages += [self.out/"trofei"/t["slug"]/"index.html" for t in self.trophies]
        pages += [self.out/"guide-e-tutorial"/g["id"]/"index.html" for g in self.guides]
        pages += [self.out/"hdr-oled"/"index.html"]
        pages += [self.out/"hdr-oled"/f["slug"]/"index.html" for f in self.hdr["families"]]
        pages += [self.out/"fonti"/"index.html"]
        pages += [self.out/"scoperte"/"index.html"]
        pages += [self.out/"privacy"/"index.html"]
        pages += [self.out/"trucchi"/"index.html"]
        pages += [self.out/"trucchi"/x["slug"]/"index.html" for x in self.cheats]
        self.assertEqual(len(pages),7+55+6+1+len(self.hdr["families"])+1+len(self.cheats))
        for page in pages:
            markup=page.read_text(encoding="utf-8")
            self.assertIn('class="page-meta"',markup,str(page))
            self.assertIn("Aggiornata il",markup,str(page))
            self.assertRegex(markup,r'<time datetime="20\d{2}-\d{2}-\d{2}">')
            self.assertIn('article:modified_time',markup,str(page))
            self.assertIn('"dateModified"',markup,str(page))
            self.assertIn("hitscounter.dev/api/hit?url=",markup,str(page))
            self.assertIn('<svg class="view-eye"',markup,str(page))
            self.assertIn('class="views-fallback" role="status"',markup,str(page))
            self.assertIn("Visualizzazioni · in aggiornamento",markup,str(page))
            self.assertIn('class="views-badge"',markup,str(page))
            self.assertIn('style="display:none" onload=',markup,str(page))
            self.assertIn("Conteggio non disponibile",markup,str(page))
            self.assertNotIn('<span class="view-eye"',markup,str(page))
            self.assertIn("Visualizzazioni",markup,str(page))
            self.assertIn('https://x.com/xFederiko11',markup,str(page))
            self.assertIn('rel="me noopener noreferrer"',markup,str(page))
            self.assertNotIn("12345 visite",markup)
        # Every URL counts its own visits, never a site-wide combined count.
        first=pages[0].read_text(encoding="utf-8")
        second=pages[1].read_text(encoding="utf-8")
        self.assertIn("https%3A%2F%2Fxfederiko11.github.io%2Fgta-6%2F",first)
        self.assertIn("https%3A%2F%2Fxfederiko11.github.io%2Fgta-6%2Ftrofei%2F",second)

    def test_homepage_social_preview_is_original_and_accessible(self):
        import struct
        image=self.out/"assets"/"social-preview.png"
        raw=image.read_bytes()
        self.assertTrue(raw.startswith(b"\\x89PNG\\r\\n\\x1a\\n"))
        self.assertEqual(struct.unpack("!II",raw[16:24]),(1200,630))
        self.assertGreater(len(raw),20000)
        homepage=(self.out/"index.html").read_text(encoding="utf-8")
        self.assertIn('property="og:image" content="https://xfederiko11.github.io/gta-6/assets/social-preview.png"',homepage)
        self.assertIn('name="twitter:image" content="https://xfederiko11.github.io/gta-6/assets/social-preview.png"',homepage)
        self.assertIn('property="og:image:width" content="1200"',homepage)
        self.assertIn('property="og:image:height" content="630"',homepage)
        self.assertIn('property="og:image:alt"',homepage)
        self.assertIn('name="twitter:card" content="summary_large_image"',homepage)
        source=Path("social_preview.py").read_text(encoding="utf-8")
        self.assertIn("No copied Rockstar art",source)
        self.assertNotIn("requests.",source)

    def test_privacy_and_no_signup_visit_counter(self):
        page=(self.out/"privacy"/"index.html").read_text(encoding="utf-8")
        self.assertIn("privacy e contatore visite",page.lower())
        self.assertIn("senza account analytics",page)
        self.assertIn("hitscounter.dev",page)
        self.assertIn("non i visitatori unici",page)
        self.assertIn('rel="canonical"',page)
        self.assertIn("https://xfederiko11.github.io/gta-6/privacy/",page)
        home=(self.out/"index.html").read_text(encoding="utf-8")
        self.assertIn("hitscounter.dev/api/hit?url=",home)
        self.assertIn("Privacy e visite</a>",home)
        for markup in (home,page):
            self.assertNotIn("goatcounter.com",markup.lower())
            self.assertNotIn("site-analytics.js",markup)
            self.assertNotIn("data-analytics-endpoint",markup)
        sitemap=(self.out/"sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("https://xfederiko11.github.io/gta-6/privacy/",sitemap)

    def test_freshness_date_source_is_not_deploy_clock_only(self):
        import site_info
        from unittest.mock import patch, Mock
        from datetime import datetime, timezone
        site_info.last_modified_at.cache_clear()
        stamp="2026-11-17T08:31:00+00:00"
        with patch("site_info.subprocess.run",return_value=Mock(returncode=0,stdout=stamp)):
            actual=site_info.last_modified_at("trofei/trofeo-14-una-lunga-strada/")
            self.assertEqual(actual,datetime(2026,11,17,8,31,tzinfo=timezone.utc))
        site_info.last_modified_at.cache_clear()
        with self.assertRaises(ValueError):
            site_info.view_badge_url("https://example.com/elsewhere")
        with self.assertRaises(ValueError):
            site_info.view_badge_url("https://xfederiko11.github.io/gta-6.evil.net/")

    def test_hdr_oled_family_pages_models_and_search(self):
        root=self.out/"hdr-oled"/"index.html"
        self.assertTrue(root.exists())
        index=root.read_text(encoding="utf-8")
        self.assertIn('id="hdr-ricerca"',index)
        self.assertIn("data-hdr-search=",index)
        self.assertIn("data-hdr-brand=",index)
        self.assertIn('data-hdr-brand-filter="all"',index)
        self.assertEqual(index.count('data-hdr-brand-filter='),6)
        self.assertIn("Nessun modello trovato",index)
        self.assertIn("Max Brightness",index)
        self.assertIn("Paper White",index)
        self.assertIn("1100",index)
        self.assertIn("600",index)
        self.assertIn("valori di partenza osservati nel gioco",index)
        self.assertIn("OLED55C44LA",index)
        self.assertIn("OLED65C47LA",index)
        self.assertIn("QE77S90DAEXZT",index)
        self.assertIn("Game HDR",index)
        self.assertIn("HGiG",index)
        self.assertIn("application/ld+json",index)
        self.assertIn("92",index)
        self.assertIn('href="#trova-tv"',index)
        self.assertIn('href="#valori-gioco"',index)
        self.assertIn('class="hdr-art"',index)
        self.assertIn('class="hdr-copy-panel"',index)
        self.assertIn('data-hdr-copy="600 · 50 · 50"',index)
        self.assertIn("assets/hdr-interactions.js",index)
        for family in self.hdr["families"]:
            path=self.out/"hdr-oled"/family["slug"]/"index.html"
            self.assertTrue(path.exists(),family["slug"])
            page=path.read_text(encoding="utf-8")
            self.assertIn('rel="canonical"',page)
            self.assertIn("Regola HDR",page)
            self.assertIn("https://www.playstation.com/it-it/support/hardware/ps5-enable-adjust-hdr/",page)
            self.assertIn("Fonti per modello e impostazioni",page)
            self.assertIn("GTA VI",page)
            self.assertIn('class="hdr-art"',page)
            self.assertIn('id="valori-hdr"',page)
            self.assertIn('id="modelli-tv"',page)
            self.assertIn('data-hdr-copy=',page)
            self.assertIn("Copia i tre valori",page)
            self.assertIn("assets/hdr-interactions.js",page)
            self.assertIn('href="#valori-hdr"',page)
            self.assertIn('href="#modelli-tv"',page)
            related=[x for x in self.hdr["families"] if
                     x["brand"]==family["brand"] and x["slug"]!=family["slug"]][:3]
            if related:
                self.assertIn("Confronta altri OLED",page)
                self.assertIn("discovery-rail",page)
                for other in related:
                    self.assertIn("/hdr-oled/"+other["slug"]+"/",page)
            for model in family["models"]:
                self.assertIn(model["code"],index)
                self.assertIn(model["code"],page)
                self.assertIn(str(model["size"])+"″",page)
            for source in family["sources"]:
                self.assertIn(source.replace("&","&amp;"),page)
            if family["brand"] == "LG":
                self.assertIn("Compensazione mappatura toni",page)
        c4=(self.out/"hdr-oled"/"lg-oled-c4"/"index.html").read_text(encoding="utf-8")
        c2=(self.out/"hdr-oled"/"lg-oled-c2"/"index.html").read_text(encoding="utf-8")
        g5=(self.out/"hdr-oled"/"lg-oled-g5"/"index.html").read_text(encoding="utf-8")
        self.assertIn("1100",c4)
        self.assertIn('data-hdr-copy="1100 · 0 · 50"',c4)
        self.assertIn("Testimonianza community",c4)
        self.assertIn("800",c2)
        self.assertIn("non misurata",c4)
        self.assertIn("NON preset personalizzato",g5)
        self.assertIn('data-hdr-copy="600 · 50 · 50"',g5)
        self.assertIn("Brightness Booster",c4)
        self.assertIn("OLED55C43LA",c4)
        self.assertIn("Compensazione mappatura toni",c4)
        self.assertNotIn("1000 nit calibrati per GTA 6",index)


    def test_cheat_pages_have_genuine_dpad_sequences_and_trophy_warning(self):
        hub=(self.out/"trucchi"/"index.html").read_text(encoding="utf-8")
        self.assertIn("Trucchi GTA 6",hub)
        self.assertIn("DualSense",hub)
        self.assertIn("250.000",hub)
        self.assertIn("9 sequenze coincidono",hub)
        self.assertIn("https://xfederiko11.github.io/gta-6/fonti/",hub)
        self.assertIn("data-cheat-search=",hub)
        self.assertIn("aria-pressed=",hub)
        self.assertIn("Disabilita",hub) if "Disabilita" in hub else self.assertIn("disabilita",hub)
        self.assertIn('aria-label="Croce direzionale',hub)
        self.assertIn('class="ps5-dpad',hub)
        self.assertNotIn("R1, R1, Cerchio, R2",hub)
        for cheat in self.cheats:
            page=(self.out/"trucchi"/cheat["slug"]/"index.html").read_text(encoding="utf-8")
            self.assertIn(cheat["title"],page)
            self.assertIn(html.escape(cheat["unlock"],quote=True),page)
            self.assertIn("trofei",page.lower())
            self.assertIn("salvataggi",page.lower())
            self.assertIn('application/ld+json',page)
            self.assertIn('rel="canonical"',page)
            self.assertEqual(page.count('class="ps5-dpad'),len(cheat["sequence"])+1)
            self.assertIn('class="cheat-code-panel" id="codice"',page)
            self.assertIn('data-copy-sequence="↑ · L1 + R1 ·',page)
            self.assertIn('data-cheat-feedback',page)
            self.assertIn("cheat-interactions.js",page)
            self.assertIn("Scopri i trucchi correlati",page)
            self.assertIn('id="fonti-codice"',page)
            self.assertIn('href="#codice"',page)
            for source in cheat["sources"]:
                self.assertIn(source.replace("&","&amp;"),page)


    def test_editorial_source_provenance_seo_and_conflicting_cheat_requirements(self):
        page=(self.out/"fonti"/"index.html").read_text(encoding="utf-8")
        self.assertIn("PowerPyx",page)
        self.assertIn("GTAForums",page)
        self.assertIn("GTA Series Videos",page)
        self.assertIn("GTABase",page)
        self.assertIn("GTA Wiki",page)
        self.assertIn("Rockstar Newswire",page)
        self.assertIn("non",page.lower())
        self.assertIn('rel="canonical"',page)
        self.assertIn('application/ld+json',page)
        self.assertIn("https://xfederiko11.github.io/gta-6/fonti/",page)
        cheat=(self.out/"trucchi"/"munizioni-massime"/"index.html").read_text(encoding="utf-8")
        self.assertIn("PowerPyx indica 25",cheat)
        self.assertIn("PC Gamer indica 20",cheat)
        corroborated=(self.out/"trucchi"/"soldi-250000"/"index.html").read_text(encoding="utf-8")
        self.assertIn("PowerPyx e PC Gamer",corroborated)
        single=(self.out/"trucchi"/"munizioni-massime"/"index.html").read_text(encoding="utf-8")
        self.assertIn("non abbiamo un secondo controllo",single)


    def test_autonomous_community_index_is_transparent_and_seo_safe(self):
        page=(self.out/"scoperte"/"index.html").read_text(encoding="utf-8")
        self.assertIn("scoperte della community",page)
        self.assertIn("Non sono notizie confermate",page)
        self.assertIn('id="community-search"',page)
        self.assertIn('data-community-filter-source="all"',page)
        self.assertIn('data-community-filter-status="all"',page)
        self.assertIn("community-interactions.js",page)
        self.assertIn('data-community-grid',page)
        self.assertIn("CONTINUA LA RICERCA",page)
        self.assertIn("0 affermazioni verificate dal solo feed",page)
        self.assertNotIn("gtabase.com.evil.example",page)
        self.assertIn("Rumor",page)
        self.assertIn('rel="canonical"',page)
        self.assertIn('application/ld+json',page)
        self.assertIn("https://xfederiko11.github.io/gta-6/scoperte/",page)
        if self.community.get("generated_utc"):
            self.assertIn("Ultima scansione delle fonti",page)
            from community_page import validate
            items=validate(self.community)
            self.assertEqual(page.count('class="community-card"'),len(items))
            for item in items:
                self.assertIn(html.escape(item["title"],quote=True),page)
                self.assertIn(html.escape(item["url"],quote=True),page)
                self.assertIn(html.escape(item["source"],quote=True),page)
                self.assertIn(html.escape(item["status"],quote=True),page)
            script=(self.out/"assets"/"community-interactions.js").read_text(encoding="utf-8")
            self.assertIn("www.youtube-nocookie.com/embed/",script)
            self.assertNotIn("fetch(",script)
        else:
            self.assertIn("Prima scansione pubblica non ancora disponibile",page)

    def test_trophy_pages_offer_actionable_visual_mobile_experience(self):
        from trophy_experience import RANGES
        self.assertEqual(len(RANGES),2)
        self.assertEqual(sum(len(levels) for _,_,courses in RANGES
                             for _,levels in courses),42)
        self.assertEqual([sum(len(levels) for _,levels in courses)
                          for _,_,courses in RANGES],[18,24])
        for trophy in self.trophies:
            page=(self.out/"trofei"/trophy["slug"]/"index.html").read_text(encoding="utf-8")
            self.assertIn('class="trophy-hero"',page)
            self.assertIn('class="trophy-art"',page)
            self.assertIn('class="discovery-rail"',page)
            self.assertIn('class="source-details"',page)
            self.assertIn('data-trophy-done=',page)
            self.assertIn("assets/trophy-experience.js",page)
            self.assertIn('rel="canonical"',page)
            self.assertIn("application/ld+json",page)
            self.assertIn("Fonte",page) if "Fonte" in page else self.assertIn("Fonti",page)
            self.assertNotIn('id="requisito" id="requisito"',page)
        cec=(self.out/"trofei"/"trofeo-17-cecchino"/"index.html").read_text(encoding="utf-8")
        self.assertIn("Griffin Shooting Range",cec)
        self.assertIn("Rodgers Ranch",cec)
        self.assertIn("Waiver Pass",cec)
        self.assertIn("18",cec)
        self.assertIn("24",cec)
        self.assertIn("42",cec)
        self.assertEqual(cec.count('type="checkbox"'),42)
        self.assertEqual(cec.count('class="medal-course"'),12)
        self.assertEqual(cec.count('class="medal-group"'),2)
        self.assertIn('data-video-id="tJbzMqJGH4k"',cec)
        self.assertIn('data-video-start="1112"',cec)
        self.assertIn("non una guida a tutte le medaglie",cec)
        self.assertIn("https://www.powerpyx.com/gta-6-all-shooting-range-gold-medal-challenges/",cec)
        other=(self.out/"trofei"/"trofeo-14-una-lunga-strada"/"index.html").read_text(encoding="utf-8")
        self.assertNotIn('data-video-id="tJbzMqJGH4k"',other)
        self.assertNotIn('data-medal-tracker',other)
        self.assertEqual(other.count('id="requisito"'),1)

    def test_guide_pages_have_faster_reading_and_relevant_discovery(self):
        for g in self.guides:
            page=(self.out/"guide-e-tutorial"/g["id"]/"index.html").read_text(encoding="utf-8")
            self.assertIn('class="guide-hero"',page)
            self.assertIn('class="guide-answer"',page)
            self.assertIn('class="figure guide-photo"',page)
            self.assertIn('id="passaggi"',page)
            self.assertIn('id="fonte-guida"',page)
            self.assertIn('class="discovery-rail"',page)
            self.assertLess(page.index('class="figure guide-photo"'),
                            page.index('id="passaggi"'))
            self.assertIn(g["source_url"].replace("&","&amp;"),page)

    def test_interactions_need_user_gesture_and_have_local_only_state(self):
        js=(self.out/"assets"/"trophy-experience.js").read_text(encoding="utf-8")
        self.assertIn("localStorage",js)
        self.assertIn("data-medal-reset",js)
        self.assertIn("data-medal-count",js)
        self.assertIn("data-trophy-done",js)
        self.assertIn('data-video-id',js)
        self.assertIn('addEventListener("click"',js)
        self.assertIn("youtube-nocookie.com/embed/",js)
        self.assertIn("id !== \"tJbzMqJGH4k\"",js)
        self.assertIn("replaceChildren(iframe)",js)
        self.assertNotIn("api.buffer.com",js)
        self.assertNotIn("fetch(",js)
        css=(self.out/"assets"/"style.css").read_text(encoding="utf-8")
        self.assertIn(".medal-chip",css)
        self.assertIn(".video-consent",css)
        self.assertIn(".discovery-rail",css)
        self.assertIn("flex-wrap:nowrap",css)
        self.assertIn(".trophy-hero",css)

    def test_personal_55_trophy_index_progress_is_private_and_consistent(self):
        page=(self.out/"trofei"/"index.html").read_text(encoding="utf-8")
        self.assertIn("data-trophy-index-progress",page)
        self.assertIn("data-trophy-total",page)
        self.assertIn("0 / 55 trofei segnati",page)
        self.assertIn("Non legge il tuo account PSN",page)
        self.assertIn("assets/trophy-experience.js",page)
        self.assertEqual(page.count('data-trophy-number="'),55)
        script=(self.out/"assets"/"trophy-experience.js").read_text(encoding="utf-8")
        self.assertIn("data-trophy-index-progress",script)
        self.assertIn("TROPHY_KEY",script)
        self.assertIn('addEventListener("pageshow", render)',script)
        self.assertIn('addEventListener("storage", render)',script)
        self.assertNotIn("api.psnprofiles.com",script)
        css=(self.out/"assets"/"style.css").read_text(encoding="utf-8")
        self.assertIn(".trophy-index-progress",css)
        self.assertIn('.index-item[data-completed="true"]',css)

    def test_no_external_paid_dependencies(self):
        self.assertFalse((self.out/"node_modules").exists())
        self.assertEqual(len(list((self.out/"trofei").glob("trofeo-*/index.html"))),55)
        self.assertEqual(len(list((self.out/"guide-e-tutorial").glob("*/index.html"))),6)

if __name__=="__main__":
    unittest.main()
