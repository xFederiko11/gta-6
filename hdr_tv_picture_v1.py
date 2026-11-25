"""Model-labelled HDR television reference image and sourced on-TV settings.

The illustration is authored locally, not a manufacturer photograph.  A TV
model must never inherit numeric values from a different family without
provenance; unknown values are explicitly marked as unverified.
"""
from __future__ import annotations

from functools import lru_cache
from html import escape
import json
from pathlib import Path


def _e(value):
    return escape(str(value), quote=True)


@lru_cache(maxsize=1)
def _profiles():
    document = json.loads(Path("data/hdr_tv_picture_v1.json").read_text(encoding="utf-8"))
    if document["schema"] != "gta-vi-hdr-tv-picture-v1":
        raise ValueError("Unsupported TV picture settings schema")
    return document["profiles"]



@lru_cache(maxsize=1)
def _photos():
    doc = json.loads(Path("data/hdr_tv_photo_sources_v1.json").read_text(encoding="utf-8"))
    if doc["schema"] != "gta-6-hdr-photos-v1":
        raise ValueError("Unexpected HDR photo source schema")
    return doc["families"]


def photo_info(family):
    """Editorial links to authentic product galleries, not copied photos."""
    return _photos()[family["slug"]]


def validate_photos(families):
    photo_map = _photos()
    if set(photo_map) != {f["slug"] for f in families}:
        raise ValueError("Every HDR family must have exactly one manufacturer photo gallery")
    hosts = {"LG": ("www.lg.com",), "Samsung": ("www.samsung.com",),
             "Sony": ("www.sony.it", "www.sony.de"),
             "Philips": ("www.philips.de", "www.philips.it"),
             "Panasonic": ("www.panasonic.com",)}
    from urllib.parse import urlparse
    for family in families:
        entry = photo_map[family["slug"]]
        if entry["reference_code"] not in {m["code"] for m in family["models"]}:
            raise ValueError("Photo does not match a model code: " + family["slug"])
        url = entry["photo_page_url"]
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in hosts[family["brand"]]:
            raise ValueError("Untrusted photo gallery source: " + family["slug"])
        if entry["rights"] != "link-only" or entry["photo_scope"] not in (
                "esatto", "variante-regionale", "famiglia"):
            raise ValueError("Photo license or scope not annotated: " + family["slug"])
        if entry["photo_scope"] == "esatto":
            code = entry["reference_code"].lower().replace("/", "_")
            if code not in url.lower().replace("/", "_"):
                raise ValueError("Exact model photo link must show the code: " + family["slug"])
        if entry["photo_scope"] == "variante-regionale" and not entry.get("pictured_region_code"):
            raise ValueError("Missing regional photo variant disclosure")
    return True


def validate(families):
    allowed = {family["slug"] for family in families}
    for slug, profile in _profiles().items():
        if slug not in allowed:
            raise ValueError("Unmatched HDR TV family: " + slug)
        family = next(f for f in families if f["slug"] == slug)
        if profile["reference_code"] not in {m["code"] for m in family["models"]}:
            raise ValueError("Unknown reference model for " + slug)
        if not profile["sources"] or not all(s.startswith("https://") for s in profile["sources"]):
            raise ValueError("Missing HTTPS source for " + slug)
        for row in profile["rows"]:
            if row["status"] not in {"Test HDR", "Verifica HDMI", "Solo riferimento SDR"}:
                raise ValueError("Unsupported television setting evidence label")
            if not row["name"] or not row["value"] or not row["source"]:
                raise ValueError("Setting without a value or evidence")
    return True


def render_reference(family, url):
    """Original TV illustration, visibly associated with the family and model."""
    reference = photo_info(family)
    code = reference["reference_code"]
    sample = next(m for m in family["models"] if m["code"] == code)
    manufacturer = reference["photo_page_url"]
    photo_scope = reference["photo_scope"]
    if photo_scope == "variante-regionale":
        photo_note = ("Le foto mostrano la variante regionale " +
                      reference["pictured_region_code"] +
                      ": non è lo stesso codice commerciale indicato qui.")
    elif photo_scope == "famiglia":
        photo_note = ("Le foto ufficiali mostrano la famiglia " +
                      family["series"] + ", non necessariamente il taglio selezionato.")
    else:
        photo_note = "Foto ufficiali del codice modello indicato."
    return (
        '<figure class="hdr-tv-reference" data-hdr-tv-reference="' + _e(family["slug"]) + '">'
        '<div class="hdr-tv-reference-visual">'
        '<img src="' + url("assets/hdr-tv-reference-v1.svg") + '" width="1000" height="600" '
        'loading="lazy" decoding="async" '
        'alt="Illustrazione originale di un televisore OLED; modello di riferimento: '
        + _e(family["brand"] + " " + family["series"] + ", " + code) + '">'
        '<span class="hdr-tv-reference-label">📺 Televisore selezionato</span>'
        '</div>'
        '<figcaption class="hdr-tv-reference-caption">'
        '<span class="hdr-tv-reference-brand">' + _e(family["brand"] + " · " + str(family["year"])) + '</span>'
        '<strong>' + _e(family["series"]) + '</strong>'
        '<span>Codice illustrato nella scheda: <b>' + _e(code) + '</b> · '
        + _e(sample["size"]) + '″</span>'
        '<small>Illustrazione originale (non è la foto della TV né uno screenshot '
        'di GTA VI). Per vedere il televisore reale usa la galleria del produttore.</small>'
        '<span class="hdr-tv-reference-photo-context">' + _e(photo_note) + '</span>'
        '<a class="hdr-tv-reference-source" href="' + _e(manufacturer) + '" '
        'target="_blank" rel="noopener noreferrer" '
        'data-hdr-photo-gallery="' + _e(family["slug"]) + '">'
        '📷 Apri le foto reali sul sito ' + _e(family["brand"]) + ' ↗</a>'
        '<small>Immagini ospitate e pubblicate dal produttore; nessuna fotografia '
        'di terzi viene copiata sul nostro sito.</small>'
        '</figcaption></figure>'
    )


def _generic_rows(family):
    """Never manufacture numeric values for unmeasured panels."""
    brand = family["brand"]
    if brand == "LG":
        names = (("Modalità immagine HDR", "Game Optimizer"),
                 ("Tone Mapping HDR", "HGiG, se disponibile"))
    elif brand == "Samsung":
        names = (("Modalità immagine HDR", "Modalità gioco"),
                 ("Game HDR", "Attivo, se disponibile"))
    elif brand == "Sony":
        names = (("Modalità immagine HDR", "Gioco"),
                 ("Auto HDR Tone Mapping", "Automatico, se supportato con PS5"))
    elif brand == "Philips":
        names = (("Modalità immagine HDR", "Gioco"),
                 ("Tone Mapping HDR", "HGiG, se disponibile"))
    else:
        names = (("Modalità immagine HDR", "True Game / Gioco, se disponibile"),
                 ("Tone Mapping HDR", "Da verificare sul firmware"))
    rows = [{"name": name, "value": val, "status": "Menu TV",
             "source": "Voce documentata nella procedura del produttore; verificarne la disponibilità"}
            for name, val in names]
    for name in ("Luminosità pixel OLED", "Contrasto", "Temperatura colore",
                 "Nitidezza", "Colore / Color Depth"):
        rows.append({"name": name, "value": "Non verificato",
                     "status": "Da verificare", "source": "Nessuna misura numerica HDR affidabile per questa famiglia"})
    return rows


def render_settings(family):
    """Second HDR table: settings ON THE TV, separate from the three game sliders."""
    profile = _profiles().get(family["slug"])
    rows = profile["rows"] if profile else _generic_rows(family)
    bits = []
    for row in rows:
        status = row["status"]
        badge_class = ("hdr-tv-status-verified" if status in {"Test HDR", "Verifica HDMI"}
                       else "hdr-tv-status-warning" if status == "Solo riferimento SDR"
                       else "hdr-tv-status-unknown")
        bits.append(
            '<tr><th scope="row">' + _e(row["name"]) + '</th>'
            '<td><strong>' + _e(row["value"]) + '</strong></td>'
            '<td><span class="hdr-tv-status ' + badge_class + '">' + _e(status) + '</span>'
            '<small>' + _e(row["source"]) + '</small></td></tr>'
        )
    table = (
        '<section class="hdr-tv-settings" aria-label="Impostazioni immagine del televisore">'
        '<p class="hdr-tv-settings-intro">Questa è la <strong>tabella dei menu della TV</strong>; '
        'non contiene Max Brightness, Black Levels o Paper White, che si impostano nel gioco.</p>'
        '<div class="hdr-tv-table-scroll"><table class="hdr-tv-settings-table"><thead><tr>'
        '<th scope="col">Impostazione sulla TV</th><th scope="col">Valore</th>'
        '<th scope="col">Verifica / fonte</th></tr></thead><tbody>'
        + "".join(bits) + '</tbody></table></div>'
    )
    if profile:
        table += (
            '<p class="hdr-tv-confirmed">✔ Le prime sette righe descrivono il setup HDR '
            'di laboratorio RTINGS su <strong>' + _e(profile["tested_hardware"]) +
            '</strong>; non sono misure di GTA VI né una calibrazione personalizzata. '
            'La voce HDMI viene verificata separatamente.</p>'
            + '<ul class="hdr-tv-notes">' + "".join('<li>' + _e(n) + '</li>'
                                                    for n in profile["notes"]) + '</ul>'
            + '<p class="source">Fonti specifiche per valori TV: '
            + ' · '.join('<a href="' + _e(s) + '" target="_blank" rel="noopener noreferrer">'
                       + _e(("RTINGS: test HDR" if i == 0 else
                              "RTINGS: menu TV" if i == 1 else "LG: supporto HGiG"))
                       + '</a>' for i, s in enumerate(profile["sources"])) + '.</p>'
        )
    else:
        table += (
            '<p class="hdr-tv-unverified">⚠️ Per questo modello sono documentati i menu '
            'principali, <strong>non una tabella numerica HDR certificata</strong>. '
            'Non copiare luminosità, contrasto o temperatura colore da una serie differente. '
            'I valori non verificati restano esplicitamente tali.</p>'
        )
    return table + '</section>'
