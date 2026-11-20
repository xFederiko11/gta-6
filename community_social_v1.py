"""X-first, optionally YouTube, community participation for static GTA VI pages.

No GitHub account required by the site. A visitor writes on the real X
conversation (or a vetted YouTube video), not in a fake local comment form.
Buffer delivery receipts are not X comment or like metrics.
"""
from __future__ import annotations
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlencode, urlsplit

BASE="https://xfederiko11.github.io/gta-6/"
PROFILE="https://x.com/xFederiko11"
INDEX=Path("data/community_social.json")
VERSION="community-social-v2"

def load(path=None):
    path=Path(path or INDEX)
    if not path.exists():
        return {"schema":VERSION,"x_posts":[],"x_metrics_available":False}
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") not in (VERSION,"community-social-v1"):
        raise ValueError("Unsupported community feed")
    return data

def verified_x_url(value):
    """Permalinks from Buffer's verified externalLink only; never guess post IDs."""
    if not isinstance(value,str) or any(ord(c)<33 for c in value):return None
    try:u=urlsplit(value)
    except ValueError:return None
    if u.scheme!="https" or u.hostname not in {"x.com","www.x.com","twitter.com","www.twitter.com"}:
        return None
    if u.username or u.password or u.port not in (None,443) or u.query or u.fragment:
        return None
    match=re.fullmatch(r"/xFederiko11/status/([0-9]{8,25})/?",u.path,re.I)
    return "https://x.com/xFederiko11/status/"+match.group(1) if match else None

def relevant_youtube(page):
    """Offer YouTube comments only when the actual article embeds a real video."""
    candidates=(
      r'https://www\\.youtube-nocookie\\.com/embed/([A-Za-z0-9_-]{11})',
      r'https://www\\.youtube\\.com/embed/([A-Za-z0-9_-]{11})',
      r'https://www\\.youtube\\.com/watch\\?v=([A-Za-z0-9_-]{11})(?:&amp;|&|")',
    )
    for pattern in candidates:
        hit=re.search(pattern,page)
        if hit:return "https://www.youtube.com/watch?v="+hit.group(1)
    return None

def post_for(path):
    expected=BASE+path
    for post in load().get("x_posts",[]):
        if post.get("url","").rstrip("/") == expected.rstrip("/") and post.get("buffer_status")=="sent":
            return post
    return None

def suggested_tweet(path):
    """Tweet compose opens at X; posting always requires a visitor action."""
    if not re.fullmatch(r"(?:[a-z0-9-]+/)+",path):
        raise ValueError("Invalid first-party article path")
    text="@xFederiko11 Ho una domanda o scoperta su questa guida GTA VI: "+BASE+path
    return "https://x.com/intent/tweet?"+urlencode({"text":text})

def xpost_for(path):
    item=post_for(path)
    if not item:return ""
    text=str(item.get("text") or "").strip()[:440]
    if not text:return ""
    link=verified_x_url(item.get("x_url"))
    second=(
       '<a href="'+escape(link,quote=True)+'" target="_blank" rel="noopener noreferrer">Apri il post originale su X ↗</a>'
       if link else
       '<p class="micro">Il collegamento diretto al post X non è ancora disponibile nei dati Buffer.</p>'
    )
    return ('<section class="social-x-excerpt" aria-label="Post inviato su X">'
            '<span class="eyebrow">𝕏 POST SU X</span><h2>Ne abbiamo parlato su X</h2>'
            '<blockquote>'+escape(text)+'</blockquote>'+second+'</section>')

def widget(path, *, title="Partecipa alla discussione", youtube_url=None):
    if not re.fullmatch(r"(?:[a-z0-9-]+/)+",path):
        raise ValueError("Unsupported article URL")
    item=post_for(path)
    url=verified_x_url(item.get("x_url")) if item else None
    if url:
        number=url.rsplit("/",1)[-1]
        target="https://x.com/intent/tweet?"+urlencode({"in_reply_to":number})
        label="💬 Rispondi al post su X"
        description="La conversazione si svolge sul post X originale. Puoi leggere le risposte e partecipare con il tuo account X."
    else:
        target=suggested_tweet(path)
        label="💬 Scrivi a Federiko su X"
        description=("Non c'è ancora un post X collegato con permalink verificato. "
                     "Il pulsante apre una bozza con @xFederiko11 e il link alla guida: "
                     "pubblichi tu, soltanto se lo desideri.")
    youtube=""
    verified_video=relevant_youtube(youtube_url or "") if youtube_url else None
    if verified_video:
        youtube=(
            '<a class="v-button secondary" href="'+escape(verified_video,quote=True)+'" '
            'target="_blank" rel="noopener noreferrer">▶ Commenta il video su YouTube</a>'
            '<p class="social-disclosure">Il video può essere di un creator esterno: i commenti '
            'rimangono sul relativo canale YouTube.</p>')
    return (
      '<section class="social-discussion" id="commenti" aria-label="Partecipa su X o YouTube">'
      '<div class="social-discussion-head"><div><span class="eyebrow">LA COMMUNITY PARTECIPA</span>'
      '<h2>'+escape(title)+'</h2>'
      '<p>Domande, posizioni, suggerimenti ed eventuali correzioni: scegli il social che usi già.</p>'
      '</div><span class="social-count">𝕏 Community</span></div>'
      '<div class="social-discussion-cta"><a class="v-button" href="'+escape(target,quote=True)+'" '
      'target="_blank" rel="noopener noreferrer">'+label+'</a>'
      '<a class="v-button secondary" href="'+PROFILE+'" target="_blank" '
      'rel="me noopener noreferrer">𝕏 Vai al profilo</a>'+youtube+'</div>'
      '<p class="social-disclosure">'+escape(description)+' '
      'Non servono GitHub né nuove registrazioni al sito. Le risposte sono pubblicate '
      'e moderate dalle rispettive piattaforme.</p></section>')

def home_rail():
    items=[x for x in load().get("x_posts",[]) if x.get("buffer_status")=="sent"][:4]
    parts=['<section class="social-home-rail" aria-label="Attività e discussioni GTA VI">'
           '<div class="v-section-head"><div><span class="v-kicker">𝕏 PARLIAMONE</span>'
           '<h2>Post recenti e conversazioni GTA VI</h2>'
           '<p>Guide dal nostro account X. Rispondi sul social che usi, senza account GitHub.</p>'
           '</div><a href="'+PROFILE+'" target="_blank" rel="me noopener noreferrer">Segui Federiko su X ↗</a></div>'
           '<div class="social-home-grid">']
    for post in items:
        link=verified_x_url(post.get("x_url"))
        parts.append('<article class="social-comment-card"><span>𝕏 @xFederiko11</span>'
                     '<p>'+escape(str(post.get("text") or "")[:220])+'</p>'
                     +(('<a href="'+escape(link,quote=True)+'" target="_blank" '
                       'rel="noopener noreferrer">Rispondi al post ↗</a>') if link
                       else '<span class="micro">Registrato come inviato da Buffer</span>')
                     +'</article>')
    if not items:
        parts.append('<p class="social-empty">Gli estratti dei post non sono disponibili adesso. '
                     'Apri il profilo X per le conversazioni aggiornate.</p>')
    parts.append('</div><div class="social-home-x"><div>'
                 '<strong>𝕏 Vedi gli ultimi post e le risposte su X</strong>'
                 '<p>Il feed X si carica solo su richiesta. I contatori dei commenti '
                 'e dei like non vengono inventati.</p></div>'
                 '<button type="button" class="v-button secondary" data-x-timeline-load>'
                 'Mostra i post X</button>'
                 '<a class="v-button" href="'+PROFILE+'" rel="me noopener noreferrer" '
                 'target="_blank">Commenta su X ↗</a>'
                 '<div data-x-timeline-slot aria-live="polite"></div></div></section>')
    return "".join(parts)
