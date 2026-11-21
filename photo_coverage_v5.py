"""Editorial GTA VI screenshot workboard: 55 precise roles, zero invented rights.

This is a factual backlog, not a stock-photo gallery or a file uploader.
Only photo_intake_v4's separate human rights + WebP integrity gate can
approve and publish user-captured gameplay. Bookmarks on the user device
are not proof of trofeo or X/PSN syncing.
"""
from __future__ import annotations
from collections import Counter
from html import escape
from urllib.parse import urlencode
import json
import re

BASE="https://xfederiko11.github.io/gta-6/"
PATH="screenshot-ps5/priorita/"
SCHEMA="gta6-photo-coverage-v5"
HIGH_GUIDES={"meditazione-capitolo-1","prima-persona-glitch-ps5",
             "poligoni-concentrazione","soldi-facili-capitolo-1"}
MEDIUM_GUIDES={"70-sfide-100-percento","soldi-2500-three-sheets-liquor",
               "registrare-auto-personale","scansionare-veicoli"}
PRIORITIES=("alta","media","normale")


def e(v):return escape(str(v),quote=True)


def audit(guides,requests,registry,provenance):
    ids={x["id"] for x in guides}
    if len(ids)!=11 or len(guides)!=11 or ids!=set(requests):
        raise ValueError("Exactly 11 real guides and role lists required")
    if not isinstance(registry.get("photos"),list) or not isinstance(provenance.get("assets"),list):
        raise ValueError("Invalid photo registries")
    if len(provenance["assets"])!=10:
        raise ValueError("Unreviewed published screenshot inventory count")
    from photo_intake_v4 import validate_approved
    validate_approved(registry,guides,requests)
    approved={(x["guide_id"],x["role"]):x for x in registry["photos"]}
    tasks=[]
    for g in sorted(guides,key=lambda g:g["safe_title"].casefold()):
        gid=g["id"]
        if not re.fullmatch(r"[a-z0-9-]+",gid):raise ValueError("Unsafe guide id")
        path=g["canonical_path"]
        if not re.fullmatch(r"(?:[a-z0-9-]+/)+",path):raise ValueError("Unsafe canonical guide path")
        roles=requests[gid]
        if len(roles)!=5 or len(set(roles))!=5:raise ValueError("Five individual roles required")
        for idx,description in enumerate(roles,1):
            if not isinstance(description,str) or not 12<=len(description)<=220:
                raise ValueError("Unsafe screenshot description")
            status="approvato" if (gid,idx) in approved else "da documentare"
            priority=("alta" if gid in HIGH_GUIDES or gid in MEDIUM_GUIDES and idx<=2
                      else "media" if gid in MEDIUM_GUIDES or idx<=2
                      else "normale")
            tasks.append({
                "id":gid+"-"+str(idx),"guide_id":gid,"guide_title":g["safe_title"],
                "role":idx,"description":description,"priority":priority,
                "status":status,"source_type":"original_ps5_capture",
                "screenshot_verified":status=="approvato",
                "rights_verified":status=="approvato",
                "guide_url":BASE+path,
                "submission_url":BASE+"screenshot-ps5/invia/?"+urlencode({"guida":gid,"passo":idx}),
            })
    if len(tasks)!=55 or len({x["id"] for x in tasks})!=55:
        raise ValueError("55 unique photo requests required")
    return {"schema":SCHEMA,"scope":"11 guides x 5 requested photo roles",
            "tasks":tasks,"total_requests":len(tasks),
            "approved_new_community_screenshots":len(approved),
            "unapproved_roles":sum(x["status"]=="da documentare" for x in tasks),
            "existing_attributed_editorial_screenshots":len(provenance["assets"]),
            "existing_editorial_reuse_permissions_verified":sum(
                x.get("reuse_permission")=="documented_and_approved" for x in provenance["assets"]),
            "note":"Requests are editorial role examples, not 55 missing existing photos. Existing source-attributed images are counted separately. No camera upload, automatic approval, automated X posting, or PSN sync.",
            "human_review_required":True,
            "automatic_social_posting":False}


def render(report):
    if report.get("schema")!=SCHEMA or len(report.get("tasks",[]))!=55:
        raise ValueError("Invalid photo workboard report")
    groups={}
    for row in report["tasks"]:
        if row["priority"] not in PRIORITIES:
            raise ValueError("Unrecognized priority")
        groups.setdefault(row["guide_id"],[]).append(row)
    body=[
        '<section class="pc-root" data-photo-coverage>',
        '<header class="pc-hero"><span class="eyebrow">📷 GTA VI ITALIA · PS5 / PS5 PRO</span>',
        '<h1>Screenshot autentici: cosa fotografare nelle 11 guide</h1>',
        '<p>Trova un passaggio che puoi documentare con una schermata tua,',
        ' apri il modulo X con guida e numero già selezionati e allega tu',
        ' la foto. Nessun accesso GitHub, nessuna foto pubblicata automaticamente.</p>',
        '<div class="pc-stats">',
        '<div><strong>55</strong><small>ruoli fotografici richiesti</small></div>',
        '<div><strong>'+str(report["approved_new_community_screenshots"])+'</strong><small>nuovi screenshot approvati</small></div>',
        '<div><strong>'+str(report["existing_attributed_editorial_screenshots"])+'</strong><small>foto attribuite già catalogate</small></div>',
        '<div><strong>'+str(report["existing_editorial_reuse_permissions_verified"])+'</strong><small>permessi riuso documentati</small></div>',
        '</div><p class="pc-legend"><strong>Importante:</strong> le 55 richieste sono esempi di',
        ' schermate utili, non 55 immagini certamente assenti. Le foto già',
        ' attribuite non diventano autorizzate solo perché il loro link funziona.',
        ' I contenuti promozionali Rockstar non dimostrano missioni o trofei.</p>',
        '<a class="v-button secondary" href="'+BASE+'screenshot-ps5/verifica/">Inventario fonti e diritti →</a> ',
        '<a class="v-button secondary" href="'+BASE+'collezionabili/percorsi/">Percorsi collezionabili →</a> ',
        '<a class="v-button secondary" href="https://x.com/intent/follow?screen_name=xFederiko11" target="_blank" rel="noopener noreferrer" data-pc-follow>𝕏 Segui per i nuovi tutorial ↗</a>',
        '</header>',
        '<div class="pc-filters"><label for="pc-priority">Mostra priorità</label>',
        '<select id="pc-priority" data-pc-filter><option value="all">Tutte le richieste</option>',
        '<option value="alta">Alta</option><option value="media">Media</option>',
        '<option value="normale">Normale</option></select>',
        '<p data-pc-shown role="status" aria-live="polite">55 richieste visibili</p></div>',
    ]
    for gid,rows in groups.items():
        body.extend([
            '<section class="pc-guide" data-pc-guide="'+e(gid)+'">',
            '<h2>'+e(rows[0]["guide_title"])+'</h2>',
            '<p><a href="'+e(rows[0]["guide_url"])+'">Leggi questa guida →</a></p>',
            '<ol class="pc-tasks">'
        ])
        for row in rows:
            body.extend([
                '<li class="pc-task" data-pc-task="'+e(row["id"])+'" data-pc-priority="'+e(row["priority"])+'">',
                '<div class="pc-task-copy"><small>PASSO '+str(row["role"])+'/5 · PRIORITÀ '+e(row["priority"].upper())+'</small>',
                '<strong>'+e(row["description"])+'</strong>',
                '<span>Stato: '+e(row["status"])+
                (' · foto e diritti verificati' if row["rights_verified"] else ' · foto originale ancora da approvare')+'</span></div>',
                '<a href="'+e(row["submission_url"])+'" class="pc-send">Prepara foto X ↗</a>',
                '</li>'
            ])
        body.extend(['</ol></section>'])
    body.extend([
        '<aside class="pc-rules"><h2>Prima di proporre una foto</h2>',
        '<p>Per PS5 usa il pulsante Crea; non includere username PSN, chat, informazioni',
        ' private o screenshot di altri autori. Verifica tu stesso patch e contesto,',
        ' segnala spoiler e allega manualmente la foto su X. Il post pubblico e una',
        ' dichiarazione non bastano da soli per concedere automaticamente diritti:',
        ' la redazione deve esaminare il materiale e il consenso specifico.</p>',
        '<p>Una foto di artwork ufficiale può accompagnare un articolo, ma non',
        ' sostituire una schermata reale di un passaggio di gioco.</p></aside></section>'
    ])
    return ''.join(body)


def json_report(report):
    if report.get("schema")!=SCHEMA or report.get("total_requests")!=55:
        raise ValueError("Cannot export invalid photo role register")
    return json.dumps(report,ensure_ascii=False,indent=2)+"\n"
