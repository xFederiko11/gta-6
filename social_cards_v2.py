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
from html.parser import HTMLParser
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


def subject_for_path(relative):
    """Original, topical editorial pictograms, never simulated game UI."""
    if "scansionare-veicoli" in relative: return "scanner"
    if any(v in relative for v in ("veicoli/","salvare-auto","sportive-randy","veicoli-per-moses","viaggio-rapido-taxi","auto-speciali")): return "car"
    if "soldi" in relative: return "cash"
    if "studiare-animali" in relative: return "animal"
    if "meditazione" in relative: return "meditation"
    if "hdr" in relative: return "display"
    if relative.startswith("patch/"): return "checklist"
    if "100-percento" in relative or "sfide" in relative: return "checklist"
    if "collezionabili" in relative or "mappe" in relative: return "map"
    if relative.startswith("trofei/"): return "trophy"
    if "prima-persona" in relative or "poligoni" in relative: return "target"
    if "trucchi" in relative or relative.startswith("guide-e-tutorial/"): return "controller"
    return "editorial"


def draw_subject(draw,kind,accent):
    """Subject-specific cover artwork in the right-hand field of the card."""
    ink=(234,240,252)
    # Deliberately diagrammatic, with no borrowed screenshots or game marks.
    draw.rounded_rectangle((814,124,1158,488),radius=28,fill=(21,29,45),outline=(97,109,146),width=3)
    if kind in ("car","scanner"):
        draw.polygon([(849,349),(849,312),(879,285),(916,218),(1039,218),
                      (1091,282),(1123,310),(1123,349)],fill=(48,65,89))
        draw.line([(849,349),(849,312),(879,285),(916,218),(1039,218),
                   (1091,282),(1123,310),(1123,349),(849,349)],fill=ink,width=8,joint="curve")
        draw.line((887,282,1082,282),fill=accent,width=8)
        for x in (880,1062): draw.ellipse((x,326,x+49,375),fill=(21,29,45),outline=accent,width=8)
        if kind=="scanner":
            for x,y,dx,dy in ((842,183,1,1),(1130,183,-1,1),(842,407,1,-1),(1130,407,-1,-1)):
                draw.line([(x,y+42*dy),(x,y),(x+42*dx,y)],fill=accent,width=8)
    elif kind=="cash":
        for x,y in ((850,236),(863,256),(876,276)):
            draw.rounded_rectangle((x,y,x+242,y+118),radius=12,fill=(37,65,60),outline=accent,width=5)
        draw.ellipse((950,296,1035,380),outline=ink,width=5)
        draw.text((977,304),"$",font=_font(50),fill=ink)
    elif kind=="trophy":
        draw.line([(918,205),(918,295),(945,335),(986,349),(1027,335),(1054,295),(1054,205),(918,205)],fill=accent,width=10,joint="curve")
        draw.arc((872,215,965,317),0,180,fill=ink,width=8)
        draw.arc((1006,215,1099,317),0,180,fill=ink,width=8)
        draw.line((986,349,986,400),fill=accent,width=12)
        draw.rounded_rectangle((936,398,1036,423),radius=7,fill=ink)
    elif kind=="display":
        draw.rounded_rectangle((850,207,1122,362),radius=14,fill=(10,14,24),outline=accent,width=9)
        for x,color in ((874,(87,148,218)),(930,(195,114,200)),(986,(240,171,110)),(1042,(103,218,193))):
            draw.rectangle((x,232,x+55,337),fill=color)
        draw.line((986,363,986,394),fill=ink,width=8);draw.line((922,394,1050,394),fill=ink,width=8)
    elif kind=="animal":
        for x,y in ((892,227),(951,196),(1011,196),(1070,227)):
            draw.ellipse((x,y,x+49,y+70),fill=accent)
        draw.ellipse((928,287,1044,396),fill=ink)
    elif kind=="meditation":
        draw.ellipse((948,209,1023,284),outline=accent,width=9)
        draw.line([(986,289),(928,338),(873,354),(986,405),(1099,354),(1044,338),(986,289)],fill=ink,width=9,joint="curve")
        draw.arc((874,174,1098,398),210,330,fill=accent,width=4)
    elif kind=="checklist":
        for y in (225,297,369):
            draw.rounded_rectangle((866,y,908,y+42),radius=7,outline=accent,width=5)
            draw.line([(875,y+20),(884,y+30),(901,y+10)],fill=ink,width=6)
            draw.line((932,y+20,1105,y+20),fill=ink,width=6)
    elif kind=="map":
        draw.line([(858,234),(939,208),(1023,238),(1111,208),(1111,390),(1023,420),(939,390),(858,420),(858,234)],fill=ink,width=6,joint="curve")
        draw.line((939,208,939,390),fill=accent,width=5);draw.line((1023,238,1023,420),fill=accent,width=5)
        draw.ellipse((967,268,1043,344),outline=accent,width=9);draw.line((1005,344,1005,367),fill=accent,width=8)
    elif kind=="target":
        for rad in (112,70,28): draw.ellipse((986-rad,306-rad,986+rad,306+rad),outline=accent,width=7)
        draw.line((842,306,1130,306),fill=ink,width=4);draw.line((986,166,986,446),fill=ink,width=4)
    else:
        draw.rounded_rectangle((852,248,1120,363),radius=47,outline=accent,width=9)
        draw.line((908,270,908,339),fill=ink,width=15);draw.line((873,305,943,305),fill=ink,width=15)
        for x,y in ((1052,273),(1082,303),(1052,333),(1022,303)):
            draw.ellipse((x-10,y-10,x+10,y+10),fill=accent)


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
            "PATCH PS5 / XBOX" if relative.startswith("patch/") else
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
    if art is None:
        draw_subject(draw,subject_for_path(relative),accent)
    draw.text((1040,557),key[-6:].upper(),font=_font(23),fill=accent)
    return base


def artwork_for_page(relative, artworks):
    """Only generic project homepage may use illustrative Rockstar photography.

    Tutorials, trophy pages, HDR guides and location articles get their own
    original text-first branded cards. A random character/scene cannot be
    confused for the exact gameplay action illustrated by that article.
    """
    if not artworks or relative != '':
        return None
    return artworks[0]


class _ApprovedImages(HTMLParser):
    """Read only actual step images in the final article, never source links."""
    def __init__(self):
        super().__init__()
        self.images={}
    def handle_starttag(self,tag,attrs):
        if tag!="img":
            return
        attributes=dict(attrs)
        key=attributes.get("data-approved-community-photo")
        if key:
            if key in self.images:
                raise ValueError("Duplicate approved photo in canonical page")
            self.images[key]=attributes.get("src")


def approved_preview(html,registry,root=None):
    """Select the explicitly cleared local photo that is actually on this page.

    The site build independently validates the full registry (owner, consent,
    step mapping, SHA and media). Recheck the social-specific flags and bytes
    on the built site, not a source URL, stock image or third-party thumbnail.
    """
    root=ROOT if root is None else Path(root)
    if registry.get("schema")!="gta6-approved-screenshots-v4":
        raise ValueError("Unexpected approved screenshot registry")
    parser=_ApprovedImages()
    parser.feed(html)
    selected=[]
    for row in registry["photos"]:
        if row.get("social_preview") is not True or row["id"] not in parser.images:
            continue
        if (row.get("rights")!="explicit_nonexclusive_site_and_social" or
            row.get("author_confirmed") is not True or row.get("human_reviewed") is not True or
            row.get("approved_by")!="xFederiko11" or row.get("published") is not True or
            row.get("gameplay_only") is not True or row.get("no_real_people") is not True):
            raise ValueError("Social screenshot is not approved for gameplay reuse")
        file="assets/approved/"+row["id"]+".webp"
        if (not re.fullmatch(r"[a-z0-9-]{6,55}",row["id"]) or
            row.get("file")!=file or parser.images[row["id"]]!=BASE+file):
            raise ValueError("Social preview must be the actual approved local image")
        path=root/file
        if not path.resolve().is_relative_to((root/"assets/approved").resolve()):
            raise ValueError("Unsafe approved photo path")
        raw=path.read_bytes()
        if (not 1500<=len(raw)<=4_000_000 or raw[:4]!=b"RIFF" or raw[8:12]!=b"WEBP" or
            hashlib.sha256(raw).hexdigest()!=row["source_sha256"]):
            raise ValueError("Published screenshot bytes do not match approval")
        with Image.open(BytesIO(raw)) as opened:
            opened.load()
            if opened.format!="WEBP" or opened.width<480 or opened.height<270:
                raise ValueError("Approved image too small or not WebP")
            photo=opened.convert("RGB")
        selected.append((row,photo))
    if len(selected)>1:
        raise ValueError("Multiple selected social previews on a canonical page")
    return selected[0] if selected else None


def render_screenshot_card(title,relative,row,photo,*,label="GUIDA DI GIOCO"):
    """Show the full real game image without a destructive crop or overlay."""
    key=cover_key(relative)
    accent=PALETTES[int(key[:3],16)%len(PALETTES)]
    card=Image.new("RGB",(WIDTH,HEIGHT),(16,19,29))
    draw=ImageDraw.Draw(card)
    draw.text((32,36),"GTA VI / ITALIA",font=_font(30),fill=accent)
    draw.text((32,91),label,font=_font(19),fill=(190,202,221))
    cleaned=re.sub(r"\s*[-|•]\s*GTA\s*6\s*Italia.*$","",title,flags=re.I).strip()
    font=_font(38 if len(cleaned)<55 else 32)
    for i,line in enumerate(_wrap(cleaned,draw,font,340,6)):
        draw.text((32,151+i*49),line,font=font,fill=(247,247,252))
    image=ImageOps.contain(photo,(778,466),method=Image.Resampling.LANCZOS)
    card.paste(image,(400+(778-image.width)//2,45+(466-image.height)//2))
    credit="Fonte: "+row["credit"]
    if row.get("capture_kind")=="creator_supplied_video_frame":
        seconds=row["source_second"]
        credit+=" · "+str(seconds//60)+":"+str(seconds%60).zfill(2)
    for i,line in enumerate(_wrap(credit,draw,_font(19,False),778,2)):
        draw.text((400,520+i*24),line,font=_font(19,False),fill=(211,220,233))
    draw.line((32,579,1168,579),fill=(90,99,126),width=2)
    draw.text((32,594),"XFEDERIKO11.GITHUB.IO/GTA-6",font=_font(17),fill=(190,202,221))
    draw.text((1064,594),key[-6:].upper(),font=_font(20),fill=accent)
    return card


def is_article(html,relative):
    """Cover actual articles, not landing pages, indexes or admin utilities."""
    if not relative:
        return False
    if 'id="procedura" class="v-tutorial"' in html:
        return True
    if re.search(r'"@type"\s*:\s*"(?:Article|NewsArticle|BlogPosting|HowTo|TechArticle)"',html):
        return True
    return (relative in {"hdr-oled/","trucchi/","trofei/roadmap-platino/",
                         "trofei/100-percento/","trofei/trofei-difficili/",
                         "collezionabili/percorsi/"} or
            bool(re.fullmatch(r"(?:veicoli|hdr-oled|articoli|news|guide-e-tutorial)/[^/]+/",relative)))


def insert_article_cover(html,relative,link,alt,credit,source_url=None):
    """Use exactly the same bytes and URL as OG and Twitter, after the H1."""
    if not is_article(html,relative):
        return html,False
    if 'data-article-cover=' in html:
        raise ValueError("Duplicate article cover: "+relative)
    # The earlier cinematic banner is decorative and was inserted before H1.
    # Remove only that known figure on article pages, not source/step images.
    html=re.sub(r'<figure class="ci-section-cover">.*?</figure>',"",html,flags=re.S)
    if len(re.findall(r"</h1\s*>",html,re.I))!=1:
        raise ValueError("Article must have exactly one H1: "+relative)
    caption=escape(credit)
    if source_url:
        if not source_url.startswith("https://"):
            raise ValueError("Unsafe cover source")
        caption+=' · <a href="'+escape(source_url,quote=True)+'" target="_blank" rel="noopener noreferrer">Fonte ↗</a>'
    figure=('<figure class="article-cover" data-article-cover="shared-social">'
            '<img src="'+escape(link,quote=True)+'" alt="'+alt+'" width="1200" height="630" '
            'loading="eager" decoding="async" fetchpriority="high">'
            '<figcaption>'+caption+'</figcaption></figure>')
    html=re.sub(r"</h1\s*>",lambda m:m.group(0)+figure,html,count=1,flags=re.I)
    style=(Path("site/assets/article-cover-v1.css")).read_bytes()
    version=hashlib.sha256(style).hexdigest()[:12]
    html=html.replace("</head>",'<link rel="stylesheet" href="'+BASE+'assets/article-cover-v1.css?v='+version+'"></head>',1)
    return html,True


# Explicit editorial matches reviewed against the official Rockstar gallery.
# Promotional context only: never proof of a menu, a mission or a spawn.
GUIDE_PHOTOS = {
    "salvare-auto/": (
        "ULTIMATE_EDITION_RIDEOUT_CUSTOMS_03.jpg",
        "Auto gialla in officina Rideout Customs (materiale Ultimate Edition)"),
    "guide-e-tutorial/scansionare-veicoli/": (
        "Jason_Duval_01.jpg",
        "Jason accanto a una motocicletta verde"),
    "guide-e-tutorial/studiare-animali/": (
        "Leonida_Keys_02.jpg",
        "Iguana verde sulla strada delle Leonida Keys"),
}


def publish():
    if not ROOT.is_dir():
        raise RuntimeError("No generated Pages site to process")
    # No new remote promotional artwork without specific reuse evidence.
    # Existing local editorial archive is legacy material, not a reuse grant.
    enabled=False
    artworks,source_status=fetch_artworks(enabled)
    direct_status='not_needed' if artworks else 'not_enabled'
    if enabled and not artworks:
        artworks,direct_status=fetch_direct_official_artworks(enabled=True)
    path=ROOT/"assets/social-cards"
    path.mkdir(parents=True,exist_ok=True)
    entries=[];digest=set()
    registry=json.loads(Path("data/approved_screenshots_v4.json").read_text(encoding="utf-8"))
    from editorial_articles import load as load_editorial, LIBRARY
    _,editorial,editorial_images=load_editorial()
    selected={item['path']:editorial_images[item['hero']] for item in editorial}
    from cinematic_site import HERO
    selected['']=editorial_images[HERO]
    selected.update({route:editorial_images[name] for route,(name,_) in GUIDE_PHOTOS.items()})
    for page in sorted(ROOT.rglob("index.html")):
        parsed=_parse_page(page)
        if parsed is None:continue
        html,relative,title=parsed
        # Use the actual reader-facing headline, without SEO suffixes, on
        # article artwork. Keep document title, metadata and canonical unchanged.
        headline=title
        if is_article(html,relative):
            h1=re.search(r'<h1\b[^>]*>(.*?)</h1\s*>',html,re.I|re.S)
            if h1:
                headline=" ".join(unescape(re.sub(r'<[^>]+>'," ",h1.group(1))).split()) or title
        key=cover_key(relative)
        art=artwork_for_page(relative,artworks)
        if relative in selected:
            row=selected[relative]
            with Image.open(LIBRARY/row['file']) as original:
                art={'name':row['title'],'image':original.convert('RGB')}
        preview=approved_preview(html,registry)
        if preview:
            row,screenshot=preview
            art=None
            photo=render_screenshot_card(headline,relative,row,screenshot)
        elif art and (relative in GUIDE_PHOTOS or relative=="articoli/gta-vi-ultimate-edition-auto-garage/"):
            photo=render_screenshot_card(headline,relative,
                                         {"credit":"Rockstar Games · promozionale"},art["image"],
                                         label="IMMAGINE PROMOZIONALE")
        else:
            photo=render_card(headline,relative,art["image"] if art else None)
        cover_kind=("approved_gameplay" if preview else "official_game_photo" if art else "original_illustration")
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
        if preview:
            alt_text="Screenshot di gameplay autorizzato: "+preview[0]["alt"]+" · Fonte: "+preview[0]["credit"]
            credit="Screenshot autorizzato · "+preview[0]["credit"]
        elif art:
            if relative in GUIDE_PHOTOS:
                alt_text="Immagine promozionale Rockstar Games: "+GUIDE_PHOTOS[relative][1]+". Non mostra la procedura."
                credit="Immagine promozionale · Rockstar Games · non mostra la procedura"
            else:
                alt_text="Immagine promozionale ufficiale Rockstar Games; copertina editoriale GTA VI Italia."
                credit="Immagine promozionale · Rockstar Games"
        else:
            alt_text="Copertina illustrata originale GTA VI Italia: "+headline+". Non screenshot di gameplay."
            credit="Copertina illustrata · GTA VI Italia"
        attr=escape(alt_text,quote=True)
        source_url=(("https://www.youtube.com/watch?v="+preview[0]["source_video_id"]+
                     "&t="+str(preview[0]["source_second"])+"s") if preview and
                     preview[0].get("capture_kind")=="creator_supplied_video_frame" else
                    (preview[0].get("source_post") if preview else OFFICIAL_PAGE if art else None))
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
        html=html.replace('</head>',new+f'<meta name="gta6:cover-kind" content="{cover_kind}"><meta name="gta6:cover-sha256" content="{binary_hash}"></head>',1)
        html,has_cover=insert_article_cover(html,relative,link,attr,credit,source_url)
        page.write_text(html,encoding="utf-8")
        entries.append({"path":relative,"image":link,"sha256":binary_hash,"artwork":art["name"] if art else None,
                        "approved_screenshot":preview[0]["id"] if preview else None,
                        "screenshot_credit":preview[0]["credit"] if preview else None,
                        "article_cover":has_cover,"cover_kind":cover_kind,"cover_subject":subject_for_path(relative) if not art and not preview else None})
    if len(entries)<65:
        raise RuntimeError("Too few canonical pages to validate social cards")
    if len({x["image"] for x in entries})!=len(entries):
        raise ValueError("Shared image URL detected")
    report={"schema":"gta6-social-cards-v2","generated_utc":datetime.now(timezone.utc).isoformat(),
            "pages":len(entries),"unique_images":len(digest),"artwork_source":ARCHIVE,
            "official_media_page":OFFICIAL_PAGE,"rights_policy":COPYRIGHT_PAGE,
            "official_zip_status":source_status,"official_direct_status":direct_status,"artworks_loaded":len(artworks),
            "artwork_backed_cards":sum(bool(x["artwork"]) for x in entries),
            "approved_screenshot_backed_cards":sum(bool(x["approved_screenshot"]) for x in entries),
            "article_covers":sum(bool(x["article_cover"]) for x in entries),
            "description":"Artwork is illustrative, not trophy/mission evidence. Commercial licensing not asserted.",
            "entries":entries}
    (ROOT/"social-cards-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("GTA6_SOCIAL_CARDS",len(entries),"unique",len(digest),"artworks",len(artworks),"source",source_status,"direct",direct_status)
    return report


if __name__=="__main__":
    publish()
