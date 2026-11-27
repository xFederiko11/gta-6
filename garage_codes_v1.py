"""Reviewed in-game keypad codes. Strings preserve leading zeroes."""
from html import escape
import re

CODES = {
    "pfister-vanessas-growler": "92665",
    "declasse-applesauce-bobcat": "360782",
    "invetero-spiderweb-coquette": "092319",
}

def code_field(code, label):
    if not re.fullmatch(r"[0-9]{4,6}", code):
        raise ValueError("Expected reviewed numeric keypad code")
    label = escape(label, quote=True)
    return (
        '<div class="vc-code" data-vc-code><label>' + label +
        '<input type="text" readonly inputmode="numeric" autocomplete="off" '
        'spellcheck="false" data-vc-code-value value="' + code + '"></label>'
        '<button type="button" data-vc-copy-code hidden aria-label="Copia ' + label +
        '">Copia</button><small role="status" aria-live="polite" data-vc-code-status>'
        'Seleziona il codice per copiarlo.</small></div>'
    )
