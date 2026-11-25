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
    profile = _profiles().get(family["slug"], {})
    code = profile.get("reference_code") or family["models"][0]["code"]
    sample = next(m for m in family["models"] if m["code"] == code)
    matching = next((s for s in family["sources"]
                     if code.casefold() in s.casefold()
                     and not s.lower().split("?")[0].endswith(".pdf")), None)
    manufacturer = matching or next((s for s in family["sources"]
                                     if s.startswith("https://")
                                     and not s.lower().split("?")[0].endswith(".pdf")),
                                    family["sources"][0])
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
        '<small>Illustrazione grafica originale, non foto del modello né screenshot di GTA VI. '
        'Usa il codice sulla targhetta della tua TV per identificare la variante.</small>'
        '<a class="hdr-tv-reference-source" href="' + _e(manufacturer) + '" '
        'target="_blank" rel="noopener noreferrer">'
        + ('Apri le fotografie ufficiali della TV ↗' if family["slug"] == "lg-oled-c4"
           else 'Apri la scheda o fonte del produttore ↗') + '</a>'
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
