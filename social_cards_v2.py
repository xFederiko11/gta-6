"""Distinct, attributable social previews for every canonical GTA VI Italia page.

Build-time only: one JPEG per page (1200x630), optionally using official
Rockstar artwork from the exact user-supplied ZIP. This is PROMOTIONAL ART,
never a screenshot proving gameplay, trophy conditions or locations.
Always falls back to original graphics if download is unavailable.
No automatic claim of a commercial-use license. No original ZIP in Git.
"""
from __future__ import annotations
from datetime import datetime, timezone
from html import unescape, escape
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
import hashlib
import json
import os
import re
import time
import zipfile

from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

ROOT=Path("_site")
BASE="https://xfederiko11.github.io/gta-6/"
ARCHIVE="https://media-rockstargames-com.akamaized.net/VI/downloads/artwork_wallpapers/GTAVI_Artwork_Wallpapers.zip"
OFFICIAL_PAGE="https://www.rockstargames.com/VI/media"
COPYRIGHT_PAGE="https://support.rockstargames.com/articles/7bNaeoMFTV0iUDGhStTXvz/policy-on-posting-copyrighted-rockstar-games-material"
WIDTH,HEIGHT=1200,630
MAX_ZIP=240_000_000
MAX_IMAGE=20_000_000
MAX_ARTWORKS=35
# Individually linked Rockstar image variants visible on the official artwork page.
# Used only if the complete user-provided ZIP exceeds the archive limit.
DIRECT_ARTWORKS=(
    ("Jason and Lucia Robbery", "https://www.rockstargames.com/VI/_next/static/media/Jason_and_Lucia_Robbery_landscape.09c8a~do21h4p.jpg?akim=1&imdensity=1&imwidth=3840"),
    ("Jason and Lucia Motel", "https://www.rockstargames.com/VI/_next/static/media/Jason_and_Lucia_Motel_landscape.08edvuwtm-20v.jpg?akim=1&imdensity=1&imwidth=3840"),
    ("Cal Hampton", "https://www.rockstargames.com/VI/_next/static/media/Cal_Hampton_landscape.17k7bnt3myg.2.jpg?akim=1&imdensity=1&imwidth=3840"),
    ("Boobie Ike", "https://www.rockstargames.com/VI/_next/static/media/Boobie_Ike_landscape.0ldnbn87k-8mq.jpg?akim=1&imdensity=1&imwidth=3840"),
    ("Vice City Postcard", "https://www.rockstargames.com/VI/_next/static/media/Vice_City_Postcard_landscape.0v2njmlk2n-qm.jpg?akim=1&imdensity=1&imwidth=3840"),
    ("Leonida Keys Postcard", "https://www.rockstargames.com/VI/_next/static/media/Leonida_Keys_Postcard_landscape.05oezf2h--~ed.jpg?akim=1&imdensity=1&imwidth=3840"),
    ("Port Gellhorn Postcard", "https://www.rockstargames.com/VI/_next/static/media/Port_Gellhorn_Postcard_landscape.176c2o75nmcr8.jpg?akim=1&imdensity=1&imwidth=3840"),
    ("Ambrosia Postcard", "https://www.rockstargames.com/VI/_next/static/media/Ambrosia_Postcard_landscape.0gd~9a41ia-rt.jpg?akim=1&imdensity=1&imwidth=3840"),
    ("Grassrivers Postcard", "https://www.rockstargames.com/VI/_next/static/media/Grassrivers_Postcard_landscape.15-10i39nhex2.jpg?akim=1&imdensity=1&imwidth=3840"),
    ("Mount Kalaga National Park Postcard", "https://www.rockstargames.com/VI/_next/static/media/Mount_Kalaga_National_Park_Postcard_landscape.0c1cb4ocq16n3.jpg?akim=1&imdensity=1&imwidth=3840"),
)
Image.MAX_IMAGE_PIXELS=45_000_000
PALETTES=("#fa9ec5","#85e3d4","#c6acff","#ffc8a1","#8ac6ff","#f5b2f6")


def cover_key(path):
    """Contract shared with bot; input is canonical relative path, including /."""
    if not isinstance(path,str) or path.startswith("/") or "\\" in path or ".." in path.split("/"):
        raise ValueError("Unsafe canonical path")
    if path and (not path.endswith("/") or not re.fullmatch(r"(?:[a-z0-9-]+/)+",path)):
        raise ValueError("Unsafe canonical path")
    return hashlib.sha256(path.encode("utf-8")).hexdigest()[:16]


def _font(size,bold=True):
    family=("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    for name in ("/usr/share/fonts/truetype/dejavu/"+family, family):
        try: return ImageFont.truetype(name,size)
        except (OSError,ValueError): pass
    return ImageFont.load_default()


def _parse_page(path):
    html=path.read_text(encoding="utf-8")
    title=re.search(r"<title>(.*?)</title>",html,re.I|re.S)
    canonical=re.search(r'<link rel="canonical" href="([^"]+)"',html,re.I)
    if not title or not canonical:
        return None
    link=unescape(canonical.group(1))
    if not link.startswith(BASE):
        return None
    relative=link[len(BASE):]
    if relative != (path.relative_to(ROOT).as_posix()).removesuffix("index.html"):
        raise ValueError("Canonical mismatch: "+str(path))
    cover_key(relative)
    value=unescape(re.sub(r"<[^>]+>"," ",title.group(1))).strip()
    return html,relative,value


def _wrap(text, draw, font, max_width, max_lines=3):
    text=" ".join(text.split())
    words=text.split()
    lines=[]
    current=""
    for word in words:
        trial=(current+" "+word).strip()
        if draw.textbbox((0,0),trial,font=font)[2] > max_width and current:
            lines.append(current);current=word
        else: current=trial
        if len(lines)==max_lines-1 and current:
            rest=" ".join(words[words.index(word)+1:])
            if rest:current=current+" "+rest
            break
    if current:lines.append(current)
    lines=lines[:max_lines]
    for i,line in enumerate(lines):
        if draw.textbbox((0,0),line,font=font)[2]>max_width:
            while len(line)>4 and draw.textbbox((0,0),line+"…",font=font)[2]>max_width:
                line=line[:-1]
            lines[i]=line.rstrip()+"…"
    return lines


def dhash(image):
    image=ImageOps.grayscale(image).resize((9,8))
    values=list(image.getdata())
    bits=0
    for y in range(8):
        for x in range(8):
            bits=(bits<<1)|(values[y*9+x]>values[y*9+x+1])
    return bits


def fetch_artworks(enabled=False,opener=urlopen):
    """Bounded read of the exact official ZIP; never extract ZIP entry paths."""
    if not enabled:return [],"disabled_on_preview"
    request=Request(ARCHIVE,headers={"User-Agent":"GTA6-Italia-Artwork/1.0","Accept":"application/zip"})
    try:
        with opener(request,timeout=20) as response:
            if response.geturl().split("?")[0]!=ARCHIVE:
                return [],"unexpected_redirect"
            length=response.headers.get("Content-Length","")
            if length.isdigit() and int(length)>MAX_ZIP:
                return [],"archive_over_size_limit"
            raw=bytearray();start=time.monotonic()
            while True:
                block=response.read(1024*1024)
                if not block: break
                raw.extend(block)
                if len(raw)>MAX_ZIP or time.monotonic()-start>85:
                    return [],"size_or_time_limit"
        archive=zipfile.ZipFile(BytesIO(raw))
        rows=[];hashes=[]
        entries=sorted((i for i in archive.infolist() if not i.is_dir()),key=lambda x:x.filename)
        for item in entries:
            if len(rows)>=MAX_ARTWORKS:break
            name=item.filename.replace("\\","/")
            if (item.file_size>MAX_IMAGE or item.file_size<2000 or
                not name.lower().endswith((".jpg",".jpeg",".png",".webp")) or
                name.startswith("/") or ".." in name.split("/")):continue
            try:
                with archive.open(item) as stream:
                    binary=stream.read(MAX_IMAGE+1)
                if len(binary)>MAX_IMAGE:continue
                with Image.open(BytesIO(binary)) as opened:
                    opened.load()
                    if opened.width<1000 or opened.height<560 or opened.width/opened.height<1.25:
                        continue
                    art=opened.convert("RGB")
                    art.thumbnail((1500,1000))
                    signature=dhash(art)
                    if any((signature ^ other).bit_count()<=7 for other in hashes):continue
                    hashes.append(signature)
                    rows.append({"image":art,"name":name,"hash":hashlib.sha256(binary).hexdigest()})
            except (OSError,ValueError,UnidentifiedImageError,Image.DecompressionBombError,RuntimeError):
                continue
        return rows,("ok" if rows else "no_usable_landscape_artworks")
    except (OSError,ValueError,TimeoutError,zipfile.BadZipFile,EOFError,Exception) as exc:
        # No re-hosting or hosting by a third party. The original graphics
        # fallback still gives each canonical URL its own unique OG image.
        return [],"source_unavailable_"+type(exc).__name__


def fetch_direct_official_artworks(enabled=False, opener=urlopen):
    """Download a capped subset of actual artwork variants linked by Rockstar.

    Never scrape third-party wallpaper mirrors, redirect to CDN unknown hosts
    or treat these as game screenshots. Official ZIP is still preferred.
    """
    if not enabled:
        return [], "direct_disabled"
    entries=[];signatures=[];errors=0
    for name,url in DIRECT_ARTWORKS:
        if not url.startswith("https://www.rockstargames.com/VI/_next/static/media/"):
            raise ValueError("Official artwork list was modified unsafely")
        try:
            req=Request(url,headers={"User-Agent":"GTA6Italia-OfficialArtwork/1.0",
                                     "Accept":"image/jpeg"})
            with opener(req,timeout=10) as response:
                if response.geturl()!=url:
                    errors+=1
                    continue
                if response.headers.get("Content-Type","").split(";")[0].lower() not in ("image/jpeg","image/jpg"):
                    errors+=1
                    continue
                size=response.headers.get("Content-Length","")
                if size.isdigit() and int(size)>9_000_000:
                    errors+=1
                    continue
                raw=response.read(9_000_001)
            if len(raw)>9_000_000 or not raw.startswith(b"\xff\xd8\xff"):
                errors+=1
                continue
            with Image.open(BytesIO(raw)) as opened:
                opened.load()
                if opened.width<1000 or opened.height<560 or opened.width/opened.height<1.25:
                    errors+=1
                    continue
                art=opened.convert("RGB")
                art.thumbnail((1500,1000))
            sig=dhash(art)
            if any((sig^existing).bit_count()<=7 for existing in signatures):
                continue
            signatures.append(sig)
            entries.append({"image":art,"name":"Official artwork: "+name,
                            "hash":hashlib.sha256(raw).hexdigest()})
        except (OSError,ValueError,UnidentifiedImageError,Image.DecompressionBombError,
                TimeoutError,RuntimeError) as exc:
            errors+=1
            continue
    return entries, ("direct_ok" if entries else "direct_sources_unavailable") + "_errors_"+str(errors)


def render_card(title,relative, art=None):
    key=cover_key(relative)
    accent=PALETTES[int(key[:3],16)%len(PALETTES)]
    base=Image.new("RGB",(WIDTH,HEIGHT),(16,19,29))
    draw=ImageDraw.Draw(base)
    if art is not None:
        try:
            photo=ImageOps.fit(art,(675,HEIGHT),method=Image.Resampling.LANCZOS,centering=(0.5,0.48))
            base.paste(photo,(WIDTH-675,0))
        except (OSError,ValueError):
            art=None
    if art is None:
        # Original editorial vector-like background (not Rockstar art).
        draw.polygon([(520,0),(1200,0),(1200,510),(760,620)],fill=(35+int(key[2:4],16)//12,30,66))
        draw.ellipse((730,-210,1350,410),outline=accent,width=14)
        draw.ellipse((840,-70,1250,340),outline=(103,191,200),width=5)
        draw.rectangle((790,405,1200,420),fill=(100,102,154))
        draw.line((950,110,950,555),fill=(87,140,171),width=4)
        for k in range(5):
            x=570+((int(key[k*2:k*2+2],16)*3)%480)
            y=55+((int(key[k+1:k+3],16)*2)%470)
            draw.ellipse((x,y,x+15,y+15),fill=accent)
    # Dark panel makes words readable over a high-detail official photo.
    draw.rounded_rectangle((34,42,785,585),radius=22,fill=(15,17,29),outline=(68,64,88),width=3)
    draw.rectangle((34,42,44,585),fill=accent)
    draw.text((78,75),"GTA VI  /  ITALIA",font=_font(33),fill=accent)
    suffix=("TROFEI / PLATINO" if relative.startswith("trofei/") else
            "GUIDE PS5" if relative.startswith("guide-e-tutorial/") else
            "MAPPE & COLLEZIONABILI" if "collezionabili" in relative else
            "PS5 / PS5 PRO")
    draw.text((80,150),suffix,font=_font(20),fill=(190,202,221))
    cleaned=re.sub(r"\s*[\-|•]\s*GTA\s*6\s*Italia.*$","",title,flags=re.I).strip() or "Guide e strategie GTA VI"
    # The page title is displayed on every unique card rather than a reusable logo.
    fontsize=53 if len(cleaned)<67 else 42
    font=_font(fontsize)
    lines=_wrap(cleaned,draw,font,655,4)
    for idx,line in enumerate(lines):
        draw.text((78,213+idx*(fontsize+10)),line,font=font,fill=(247,247,252))
    draw.line((78,521,735,521),fill=(90,99,126),width=2)
    draw.text((80,537),"XFEDERIKO11.GITHUB.IO/GTA-6",font=_font(18),fill=(190,202,221))
    draw.text((1040,557),key[-6:].upper(),font=_font(23),fill=accent)
    return base


def publish():
    if not ROOT.is_dir():
        raise RuntimeError("No generated Pages site to process")
    enabled=os.environ.get("GTA6_FETCH_ROCKSTAR_ART","false").lower()=="true"
    artworks,source_status=fetch_artworks(enabled)
    direct_status='not_needed' if artworks else 'not_enabled'
    if enabled and not artworks:
        artworks,direct_status=fetch_direct_official_artworks(enabled=True)
    path=ROOT/"assets/social-cards"
    path.mkdir(parents=True,exist_ok=True)
    entries=[];digest=set()
    for page in sorted(ROOT.rglob("index.html")):
        parsed=_parse_page(page)
        if parsed is None:continue
        html,relative,title=parsed
        key=cover_key(relative)
        art=artworks[int(key,16)%len(artworks)] if artworks else None
        photo=render_card(title,relative,art["image"] if art else None)
        dest=path/(key+".jpg")
        photo.save(dest,"JPEG",quality=83,optimize=True,progressive=True,subsampling=0)
        data=dest.read_bytes()
        if not 8_000<=len(data)<=1_600_000 or not data.startswith(b"\xff\xd8\xff"):
            raise ValueError("Generated social card is not a valid lightweight JPEG")
        binary_hash=hashlib.sha256(data).hexdigest()
        if binary_hash in digest:
            raise ValueError("Two canonical pages rendered same social image")
        digest.add(binary_hash)
        link=BASE+"assets/social-cards/"+key+".jpg"
        attr=escape("Artwork promozionale Rockstar Games; copertina editoriale GTA VI Italia, non screenshot di gameplay." if art else
                    "Copertina grafica originale GTA VI Italia; non screenshot di gameplay.",quote=True)
        # Always replace generic previews AND source-image previews so X link
        # shares have one dedicated, reliably sized card for each URL.
        for tag,kind in ((r'<meta property="og:image" content="[^"]*">','og'),
                         (r'<meta name="twitter:image" content="[^"]*">','twitter')):
            replacement=(f'<meta property="og:image" content="{link}">' if kind=="og" else
                         f'<meta name="twitter:image" content="{link}">')
            html,count=re.subn(tag,lambda _m:replacement,html,count=1)
            if count!=1:raise ValueError("Missing OG card meta in "+relative)
        html=re.sub(r'<meta property="og:image:(?:width|height|alt|type)" content="[^"]*">\s*',"",html)
        new=(f'<meta property="og:image:width" content="1200">'
             f'<meta property="og:image:height" content="630">'
             f'<meta property="og:image:type" content="image/jpeg">'
             f'<meta property="og:image:alt" content="{attr}">'
             f'<meta name="twitter:image:alt" content="{attr}">')
        html=html.replace('</head>',new+'</head>',1)
        page.write_text(html,encoding="utf-8")
        entries.append({"path":relative,"image":link,"sha256":binary_hash,"artwork":art["name"] if art else None})
    if len(entries)<65:
        raise RuntimeError("Too few canonical pages to validate social cards")
    if len({x["image"] for x in entries})!=len(entries):
        raise ValueError("Shared image URL detected")
    report={"schema":"gta6-social-cards-v2","generated_utc":datetime.now(timezone.utc).isoformat(),
            "pages":len(entries),"unique_images":len(digest),"artwork_source":ARCHIVE,
            "official_media_page":OFFICIAL_PAGE,"rights_policy":COPYRIGHT_PAGE,
            "official_zip_status":source_status,"official_direct_status":direct_status,"artworks_loaded":len(artworks),
            "artwork_backed_cards":sum(bool(x["artwork"]) for x in entries),
            "description":"Artwork is illustrative, not trophy/mission evidence. Commercial licensing not asserted.",
            "entries":entries}
    (ROOT/"social-cards-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("GTA6_SOCIAL_CARDS",len(entries),"unique",len(digest),"artworks",len(artworks),"source",source_status,"direct",direct_status)
    return report


if __name__=="__main__":
    publish()
