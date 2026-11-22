"""11 compact guide headers: when, where and concrete result.

Editorial navigation only: never rewrite source mission steps or suppress
missable/trophy/save warnings; no image sources or outside embeds here.
"""
from html import escape

SCHEMA="gta6-operational-guide-briefs-v1"


def validate(data,guides):
    by={g["id"]:g for g in guides}
    if data.get("schema")!=SCHEMA or len(by)!=11 or set(data.get("guides",{}))!=set(by):
        raise ValueError("Operational briefs must cover exactly the 11 real guides")
    for ident,row in data["guides"].items():
        if set(row)!={"when","where","goal"}:
            raise ValueError("Only three compact, checked fields per guide")
        for key,value in row.items():
            if (not isinstance(value,str) or not 8<=len(value)<=160
                or any(x in value for x in "<>\n\r")):
                raise ValueError("Unclear/unsafe operational summary: "+ident+"."+key)
    if "trofei non verificati" not in data["guides"]["prima-persona-glitch-ps5"]["goal"]:
        raise ValueError("The trophy warning must never be hidden")
    if "Capitolo 1" not in data["guides"]["meditazione-capitolo-1"]["when"]:
        raise ValueError("The missable first meditation must remain visible")
    if "Girl’s Trip" not in data["guides"]["registrare-auto-personale"]["when"]:
        raise ValueError("First registration must not be confused with Moses' later vehicle jobs")
    return True


def render(data,guide):
    row=data["guides"][guide["id"]]
    out=['<section class="v-operation-brief" aria-label="Prima di iniziare">',
         '<h2>Prima di iniziare</h2><dl>']
    for key,title in (("when","Quando"),("where","Dove"),("goal","Obiettivo")):
        out.append('<div><dt>'+title+'</dt><dd>'+escape(row[key],quote=True)+'</dd></div>')
    out.append('</dl></section>')
    return "".join(out)
